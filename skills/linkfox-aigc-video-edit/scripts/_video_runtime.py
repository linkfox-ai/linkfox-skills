"""视频编辑业务适配：复用公共调用器，支持本地缓存及响应兼容。"""
import io
import json
import hashlib
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from xml.etree import ElementTree
from unittest.mock import patch
import call_api as public_api

SLUG = "linkfox-aigc-video-edit"
CACHE_TTL_SEC = 24 * 60 * 60
get_api_key = public_api.get_api_key

def check_output_directory():
    configured = (os.environ.get("ACPX_WORKSPACES") or "").split(os.pathsep)[0].strip()
    if configured and Path(configured).resolve() != Path.cwd().resolve():
        raise RuntimeError("请取消 ACPX_WORKSPACES，并从可写任务目录运行")
    output = Path.cwd() / "linkfox"
    output.mkdir(exist_ok=True)
    probe = output / (".write-probe-" + str(time.time_ns()))
    try:
        probe.write_bytes(b"")
    finally:
        probe.unlink(missing_ok=True)
    public_api._SESSION_CACHE["_root"] = str(output.resolve())

def _ensure_session(ts):
    check_output_directory()
    return public_api._ensure_session(ts)

def resolve_data_path(slug, ts, ext="json"):
    check_output_directory()
    return public_api.resolve_data_path(slug, ts, ext)

_update_meta = public_api._update_meta

def _decode_gateway_response(body, http_status=None, reason=None):
    """解析 JSON，并标准化网关 ToolErrorResponse XML。"""
    if body:
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            try:
                root = ElementTree.fromstring(body)
                if root.tag.rsplit("}", 1)[-1] == "ToolErrorResponse":
                    fields = {
                        child.tag.rsplit("}", 1)[-1]: (child.text or "")
                        for child in root
                    }
                    code = fields.get("errcode")
                    if code is not None:
                        try:
                            code = int(code)
                        except ValueError:
                            pass
                    return {"errcode": code, "errmsg": fields.get("errmsg", "")}
            except ElementTree.ParseError:
                pass

    if http_status is not None:
        label = f"HTTP {http_status}"
        if reason:
            label += f": {reason}"
        result = {"error": label}
    else:
        result = {"error": "Invalid gateway response format"}
    if body:
        result["details"] = body
    return result


def _attach_gateway_cost_headers(result, headers):
    """将网关费用响应头合并到标准化响应。"""
    if not isinstance(result, dict) or headers is None:
        return result
    for header, field in (
        ("X-Cost-Token", "costToken"),
        ("X-Cost-Credit", "costCredit"),
    ):
        value = headers.get(header)
        if value is None:
            continue
        try:
            value = int(value)
        except (TypeError, ValueError):
            pass
        # 响应头为本次请求的权威费用值。
        result[field] = value
    return result


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            return None
        if not isinstance(payload.get("_cache", {}), dict):
            return None
        payload.setdefault("_cache", {})["hit"] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass



def _normal_body(raw, status, reason, headers):
    result = _decode_gateway_response(raw.decode("utf-8"), status, reason)
    if not isinstance(result, dict):
        result = {"error": "网关响应必须为 JSON 对象", "details": result}
    result = _attach_gateway_cost_headers(result, headers)
    result["transportHttpStatus"] = status
    return json.dumps(result, ensure_ascii=False).encode("utf-8")

class _Response:
    """仅转换公共调用器收到的响应流，不构造或提交请求。"""
    def __init__(self, response):
        self.response = response
        self.status = response.status

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    def read(self):
        return _normal_body(self.response.read(), self.status,
                            getattr(self.response, "reason", None), self.response.headers)

def run(api_path, slug, argv=None, *, force_no_cache=False):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or "--help" in argv or "-h" in argv:
        print(f"用法: {Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        if argv:
            return
        raise SystemExit(1)
    raw = [arg for arg in argv if arg not in {"--inline", "--no-cache"}]
    try:
        params = json.loads(raw[0])
    except (IndexError, json.JSONDecodeError) as error:
        raise SystemExit(f"JSON 参数无效: {error}")
    if not isinstance(params, dict):
        raise SystemExit("参数必须为 JSON 对象")
    check_output_directory()
    use_cache = not force_no_cache and "--no-cache" not in argv
    cache_path = _cache_path(params)
    cached = _load_cache(cache_path) if use_cache else None
    original_open = public_api.urlopen
    original_call = public_api.call_api

    def adapted_open(*args, **kwargs):
        # 请求仍由公共调用器构造并发送，本层只装饰其响应。
        try:
            return _Response(original_open(*args, **kwargs))
        except HTTPError as error:
            body = _normal_body(error.read() if error.fp else b"", error.code,
                                error.reason, error.headers)
            raise HTTPError(error.url, error.code, error.reason, error.headers, io.BytesIO(body)) from error

    def dispatch(path, body):
        if cached is not None:
            return cached.get("transportHttpStatus", 200), cached
        status, result = original_call(path, body)
        if isinstance(result, dict):
            result.setdefault("transportHttpStatus", status)
        if use_cache:
            _save_cache(cache_path, result)
        return status, result

    def output_path(out_slug, ts):
        return resolve_data_path(out_slug, time.time())

    # 业务适配层提供唯一一层缓存；公共 run 始终禁用自己的缓存。上下文退出后恢复被替换的方法。
    with patch.object(public_api, "urlopen", adapted_open), \
         patch.object(public_api, "call_api", dispatch), \
         patch.object(public_api, "_cache_path", lambda *args: cache_path), \
         patch.object(public_api, "_resolve_output_path", output_path):
        return public_api.run(api_path, slug, argv=[*argv, "--no-cache"])
