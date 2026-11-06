"""AIGC 兼容封装：公共调用器负责请求，支持 XML、费用头和单层业务缓存。"""
import io
import json
import hashlib
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from xml.etree import ElementTree
import call_api as api

SLUG = "linkfox-aigc-video-reclone"
CACHE_TTL_SEC = 24 * 60 * 60
get_api_key = api.get_api_key
_ensure_session = api._ensure_session
_update_meta = api._update_meta
resolve_data_path = api.resolve_data_path

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
    """在标准化响应中保留网关费用头。"""
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
        # 本次请求以网关费用头为准。
        result[field] = value
    return result


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params, api_path=None):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    if api_path == "/aigc/uploadByBase64":
        path = os.path.join(path, "uploadByBase64")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path, api_path=None):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            return None
        metadata = payload.get("_cache")
        metadata = metadata if isinstance(metadata, dict) else {}
        cached_path = metadata.get("apiPath")
        if cached_path is not None and cached_path != api_path:
            return None
        # 缓存未保存接口标识时，只复用可以明确识别归属的成功响应。
        if cached_path is None and api_path is not None:
            expected = "taskId" if api_path == "/aigc/videoReclone" else "viewUrl"
            opposite = "viewUrl" if expected == "taskId" else "taskId"
            if not payload.get(expected) or opposite in payload:
                return None
        payload["_cache"] = {**metadata, "hit": True}
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


class _Response(io.BytesIO):
    def __init__(self, payload, status, headers):
        super().__init__(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        self.status = status
        self.headers = headers


def run_entry(api_path, argv=None):
    """保留业务缓存，始终关闭公共调用器的响应缓存，避免重复缓存。"""
    from material_runtime import check_output_directory
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv == ["--help"]:
        print(f"用法：{Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        if not argv:
            raise SystemExit(1)
        return
    raw = [arg for arg in argv if arg not in {"--inline", "--no-cache"}]
    if len(raw) != 1:
        raise SystemExit("请提供一个 JSON 参数对象")
    try:
        params = json.loads(raw[0])
    except json.JSONDecodeError as error:
        raise SystemExit(f"JSON 参数无效：{error}")
    if not isinstance(params, dict):
        raise SystemExit("参数必须是 JSON 对象")
    check_output_directory()
    use_cache = "--no-cache" not in argv and api_path != "/aigc/taskQuery"
    cache_path = _cache_path(params, api_path) if use_cache else None
    original_transport, original_open = api.call_api, api.urlopen
    original_output = api._resolve_output_path
    original_cache_path = api._cache_path
    previous_root = api._SESSION_CACHE.get("_root")

    def normalize_response(request, timeout):
        # 请求由公共 call_api 构造并发起；本层只适配已有响应格式。
        try:
            response = original_open(request, timeout=timeout)
        except HTTPError as error:
            with error:
                body = error.read().decode("utf-8", errors="replace") if error.fp else ""
                payload = _decode_gateway_response(body, error.code, error.reason)
                payload = _attach_gateway_cost_headers(payload, error.headers)
                return _Response(payload, error.code, error.headers)
        with response:
            body = response.read().decode("utf-8", errors="replace")
            payload = _decode_gateway_response(body)
            payload = _attach_gateway_cost_headers(payload, response.headers)
            return _Response(payload, response.status, response.headers)

    def with_business_cache(path, payload):
        result = _load_cache(cache_path, path) if use_cache else None
        if result is None and use_cache and path == "/aigc/uploadByBase64":
            result = _load_cache(_cache_path(payload), path)
            if result is not None:
                # 将旧上传缓存迁入隔离目录，不再依赖可能被创建覆盖的旧位置。
                migrated = {**result, "_cache": {"apiPath": path}}
                _save_cache(cache_path, migrated)
        if result is not None:
            return result.get("transportHttpStatus", 200), result
        status, result = original_transport(path, payload)
        if not isinstance(result, dict):
            result = {"error": "网关响应不是 JSON 对象", "details": result}
        result["transportHttpStatus"] = status
        if use_cache:
            result["_cache"] = {"apiPath": path}
            _save_cache(cache_path, result)
        return status, result

    api.urlopen = normalize_response
    api.call_api = with_business_cache
    # run 会解析缓存路径；命中提示指向实际业务缓存文件。
    api._cache_path = lambda _slug, payload: cache_path or _cache_path(payload, api_path)
    api._SESSION_CACHE["_root"] = str(Path.cwd() / "linkfox")
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time_ns() / 1e9)
    options = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if "--inline" in argv:
        options.append("--inline")
    try:
        api.run(api_path, SLUG + "-" + api_path.rsplit("/", 1)[-1], argv=options)
    finally:
        api.urlopen, api.call_api = original_open, original_transport
        api._resolve_output_path = original_output
        api._cache_path = original_cache_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
