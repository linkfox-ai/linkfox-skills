"""处理 AIGC 的 24h 缓存、XML 错误、费用头和 cwd 落盘。

HTTP 请求与响应输出由 call_api.run 执行；这里不创建网络请求。
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from xml.etree import ElementTree

import call_api as core
from material_runtime import check_output_directory

SLUG = "linkfox-aigc-image-to-video"
CACHE_TTL_SEC = 24 * 60 * 60
get_api_key = core.get_api_key
_update_meta = core._update_meta


def _cwd_root():
    check_output_directory()
    return str((Path.cwd() / "linkfox").resolve())


@contextlib.contextmanager
def _override(**attributes):
    previous = {key: getattr(core, key) for key in attributes}
    try:
        for key, value in attributes.items():
            setattr(core, key, value)
        yield
    finally:
        for key, value in previous.items():
            setattr(core, key, value)


def _ensure_session(stamp):
    with _override(_linkfox_root=_cwd_root):
        return core._ensure_session(stamp)


def resolve_data_path(slug, stamp, ext="json"):
    _, session = _ensure_session(stamp)
    folder = Path(session) / "data"
    folder.mkdir(exist_ok=True)
    tick = time.time_ns()
    output = folder / f"{slug}-{tick}.{ext}"
    # Windows 时钟粒度可能使连续响应取得同一时间，不能覆盖之前的原始数据。
    while output.exists():
        tick += 1
        output = folder / f"{slug}-{tick}.{ext}"
    core._update_meta(session, skill=slug, kind="data", file_rel=str(output.relative_to(session)), ts=stamp)
    return str(output)


def _cache_path(params):
    # 使用请求参数键和 24h TTL；关闭公共脚本缓存，仅使用业务层缓存。
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    key = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    folder = Path.cwd() / "linkfox" / ".cache" / SLUG
    folder.mkdir(parents=True, exist_ok=True)
    return folder / (SLUG + "-" + key + ".json")


def _load_cache(path):
    try:
        if time.time() - path.stat().st_mtime > CACHE_TTL_SEC:
            return None
        raw = path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            # 已存在响应不能因格式异常变成缓存未命中，避免重新创建收费任务。
            payload = {"error": "缓存响应必须是 JSON 对象", "details": raw}
        if not isinstance(payload.get("_cache"), dict):
            payload["_cache"] = {}
        payload["_cache"]["hit"] = True
        return payload
    except (OSError, ValueError, TypeError):
        return None


def _save_cache(path, payload):
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def _normalize(body, headers, status=None, reason=None):
    """在公共 transport 解析前规范化 JSON/XML 与响应头费用。"""
    text = body.decode("utf-8")
    try:
        result = json.loads(text)
    except ValueError:
        result = None
        try:
            root = ElementTree.fromstring(text)
            if root.tag.rsplit("}", 1)[-1] == "ToolErrorResponse":
                fields = {child.tag.rsplit("}", 1)[-1]: child.text or "" for child in root}
                code = fields.get("errcode")
                try:
                    code = int(code)
                except (ValueError, TypeError):
                    pass
                result = {"errcode": code, "errmsg": fields.get("errmsg", "")}
        except ElementTree.ParseError:
            pass
        if result is None:
            label = f"HTTP {status}" if status is not None else "Invalid gateway response format"
            if reason:
                label += ": " + str(reason)
            result = {"error": label}
            if text:
                result["details"] = text
    if not isinstance(result, dict):
        result = {"error": "网关响应必须是 JSON 对象", "details": text}
    if headers is not None:
        for header, field in (("X-Cost-Token", "costToken"), ("X-Cost-Credit", "costCredit")):
            value = headers.get(header)
            if value is not None:
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    pass
                result[field] = value
    return json.dumps(result, ensure_ascii=False).encode("utf-8")


class _Response:
    def __init__(self, response):
        self.response = response

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    @property
    def status(self):
        return self.response.status

    def read(self):
        return _normalize(self.response.read(), self.response.headers)


def run(api_path, operation, argv=None, *, force_no_cache=False):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or "--help" in argv or "-h" in argv:
        print(f"用法：{Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        if not argv:
            raise SystemExit(1)
        return
    filtered = [item for item in argv if item not in {"--inline", "--no-cache"}]
    if len(filtered) != 1:
        raise SystemExit("请传入一个 JSON 参数对象")
    try:
        params = json.loads(filtered[0])
    except ValueError:
        raise SystemExit("JSON 参数格式无效")
    if not isinstance(params, dict):
        raise SystemExit("参数必须是 JSON 对象")
    check_output_directory()
    cache_enabled = not force_no_cache and "--no-cache" not in argv
    cache_path = _cache_path(params) if cache_enabled else None
    original_call = core.call_api
    original_open = core.urlopen

    def compatible_open(request, **kwargs):
        # Request、鉴权、环境头、超时由公共 transport 构造；只适配响应。
        try:
            return _Response(original_open(request, **kwargs))
        except HTTPError as error:
            raw = error.read() if error.fp else b""
            normalized = _normalize(raw, error.headers, error.code, error.reason)
            raise HTTPError(error.url, error.code, error.reason, error.headers, io.BytesIO(normalized)) from error

    def cached_call(path, payload):
        cached = _load_cache(cache_path) if cache_enabled else None
        if cached is not None:
            return cached.get("transportHttpStatus") if isinstance(cached, dict) else None, cached
        status, result = original_call(path, payload)
        if isinstance(result, dict):
            result["transportHttpStatus"] = status
        if cache_enabled:
            _save_cache(cache_path, result)
        return status, result

    # 始终关闭公共缓存，业务层仅使用一层响应缓存。
    with _override(call_api=cached_call, urlopen=compatible_open, _linkfox_root=_cwd_root,
                   _cache_path=lambda slug, payload: str(_cache_path(payload)),
                   _resolve_output_path=resolve_data_path):
        core.run(api_path, SLUG + "-" + operation, argv=argv + ["--no-cache"])
