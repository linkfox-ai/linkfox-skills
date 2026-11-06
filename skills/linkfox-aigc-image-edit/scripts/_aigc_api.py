"""AIGC 业务调用：单层缓存、XML 错误、费用头；HTTP 统一委托 call_api.run。"""
import io
import json
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch
from urllib.error import HTTPError
from xml.etree import ElementTree

import call_api as _api

SLUG = "linkfox-aigc-image-edit"
CACHE_TTL_SEC = 24 * 60 * 60
get_api_key = _api.get_api_key
get_api_base = _api.get_api_base
_update_meta = _api._update_meta


def _prepare_storage():
    # 业务层检查输出目录可写，将响应固定保存在 cwd。
    from material_runtime import check_output_directory
    check_output_directory()
    _api._SESSION_CACHE["_root"] = str((Path.cwd() / "linkfox").resolve())


def _ensure_session(ts):
    _prepare_storage()
    return _api._ensure_session(ts)


def resolve_data_path(slug, ts, ext="json"):
    _prepare_storage()
    return _api.resolve_data_path(slug, ts, ext)


def _valid_code(value):
    if value is None:
        return True
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return True
        if len(value) != 3 or not value.isascii() or not value.isdigit():
            return False
        value = int(value)
    return type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0


def api_error(result):
    if not isinstance(result, dict) or result.get("error"):
        return True
    if "transportHttpStatus" in result:
        status = result["transportHttpStatus"]
        if type(status) is not int or not 200 <= status < 300:
            return True
    if not _valid_code(result.get("errcode")):
        return True
    # 兼容额外 code 字段；errcode=0/false 则始终不成功。
    code = result.get("code")
    return code not in (None, 0, "0") and not _valid_code(code)


def _normalize(raw, status, headers, reason=None):
    text = raw.decode("utf-8", errors="replace")
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
            result = {"error": f"HTTP {status}" + (f": {reason}" if reason else ""), "details": text}
    if not isinstance(result, dict):
        result = {"error": "网关响应必须是 JSON 对象", "details": text}
    result["transportHttpStatus"] = status
    for header, field in (("X-Cost-Token", "costToken"), ("X-Cost-Credit", "costCredit")):
        value = headers.get(header) if headers is not None else None
        if value is not None:
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass
            result[field] = value
    return json.dumps(result, ensure_ascii=False).encode("utf-8")


class _Response(io.BytesIO):
    def __init__(self, raw, status, headers):
        super().__init__(raw)
        self.status = status
        self.headers = headers


def _cache_path(params):
    # 创建、查询和上传入口共用缓存目录及参数散列。
    return Path(_api._cache_path(SLUG, params))


def _load_cache(path):
    try:
        if time.time() - path.stat().st_mtime > CACHE_TTL_SEC:
            return None
        result = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(result, dict):
            return None
        metadata = result.get("_cache")
        if not isinstance(metadata, dict):
            metadata = {}
            result["_cache"] = metadata
        metadata["hit"] = True
        return result
    except (OSError, ValueError, TypeError):
        return None


def _save_cache(path, result):
    try:
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def run_entry(api_path, argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv == ["--help"]:
        print(f"用法: {Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        if not argv:
            raise SystemExit(1)
        return
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv and api_path != "/aigc/taskQuery"
    values = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    try:
        if len(values) != 1:
            raise ValueError("需要一个 JSON 参数对象")
        params = json.loads(values[0])
        if not isinstance(params, dict):
            raise ValueError("参数必须为 JSON 对象")
    except ValueError as error:
        raise SystemExit(f"参数格式错误: {error}")
    _prepare_storage()
    cache_path = _cache_path(params)
    cached = _load_cache(cache_path) if use_cache else None
    original_transport = _api.call_api
    original_open = _api.urlopen
    original_summarize = _api.summarize

    def normalize_response(request, timeout):
        # 仅装饰模板的响应读取；请求构造、凭证、超时与发送均由模板负责。
        try:
            response = original_open(request, timeout=timeout)
        except HTTPError as error:
            try:
                raw = error.read() if error.fp else b""
            finally:
                error.close()
            normalized = _normalize(raw, error.code, error.headers, error.reason)
            raise HTTPError(error.url, error.code, error.reason, error.headers, io.BytesIO(normalized)) from None
        with response:
            return _Response(_normalize(response.read(), response.status, response.headers),
                             response.status, response.headers)

    def dispatch(path, payload):
        if cached is not None:
            return cached.get("transportHttpStatus", 200), cached
        status, result = original_transport(path, payload)
        if isinstance(result, dict):
            result["transportHttpStatus"] = status
            if use_cache:
                _save_cache(cache_path, result)
        return status, result

    def summarize(result):
        original_summarize(result)
        if isinstance(result, dict) and isinstance(result.get("costCredit"), (int, float, str)):
            print(f"  costCredit: {result['costCredit']}")

    # 通用模板缓存始终关闭，只使用一层业务缓存。
    options = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        options.append("--inline")
    with patch.object(_api, "urlopen", normalize_response), \
            patch.object(_api, "call_api", dispatch), \
            patch.object(_api, "summarize", summarize), \
            patch.object(_api, "_resolve_output_path", lambda slug, ts: resolve_data_path(
                slug + "-" + api_path.rsplit("/", 1)[-1], time.time())):
        _api.run(api_path, SLUG, argv=options)
