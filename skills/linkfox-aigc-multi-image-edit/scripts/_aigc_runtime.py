"""业务兼容层：管理 24 小时缓存，通过公共 run 完成网关调用和响应落盘。"""
import io
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from xml.etree import ElementTree

import call_api as api
from material_runtime import check_output_directory

SLUG = "linkfox-aigc-multi-image-edit"
CACHE_TTL_SEC = 24 * 60 * 60
get_api_key = api.get_api_key
_update_meta = api._update_meta


def _cwd_storage(operation, *args):
    """媒体及清单使用公共存储，且与业务响应一样禁止目录回退。"""
    check_output_directory()
    previous = api._SESSION_CACHE.get("_root")
    api._SESSION_CACHE["_root"] = str((Path.cwd() / "linkfox").resolve())
    try:
        return operation(*args)
    finally:
        if previous is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous


def _ensure_session(stamp):
    return _cwd_storage(api._ensure_session, stamp)


def resolve_data_path(slug, stamp, ext="json"):
    return _cwd_storage(api.resolve_data_path, slug, stamp, ext)


def _decode(body, http_status=None, reason=None):
    """解析 JSON / ToolErrorResponse XML 并提供非 JSON 错误诊断。"""
    if body:
        try:
            return json.loads(body)
        except (ValueError, TypeError):
            try:
                root = ElementTree.fromstring(body)
                if root.tag.rsplit("}", 1)[-1] == "ToolErrorResponse":
                    fields = {child.tag.rsplit("}", 1)[-1]: child.text or "" for child in root}
                    code = fields.get("errcode")
                    try:
                        code = int(code)
                    except (ValueError, TypeError):
                        pass
                    return {"errcode": code, "errmsg": fields.get("errmsg", "")}
            except ElementTree.ParseError:
                pass
    label = f"HTTP {http_status}" if http_status is not None else "Invalid gateway response format"
    if reason and http_status is not None:
        label += f": {reason}"
    result = {"error": label}
    if body:
        result["details"] = body
    return result


class _ResponseView:
    """只适配响应读取；实际请求始终由公共 call_api 的 transport 发出。"""
    def __init__(self, response, captured):
        self.response = response
        self.status = response.status
        captured.update(response.headers)

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    def read(self):
        body = self.response.read().decode("utf-8")
        return json.dumps(_decode(body), ensure_ascii=False).encode("utf-8")


def _load_cache(path):
    """支持无版本号缓存文件；有效期为 24 小时。"""
    if not path.is_file() or time.time() - path.stat().st_mtime > CACHE_TTL_SEC:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            # 缓存也可能保存非对象响应；保留诊断，避免崩溃或重新创建收费任务。
            payload = {"error": "缓存响应不是 JSON 对象", "details": payload}
        marker = payload.get("_cache")
        payload["_cache"] = {**(marker if isinstance(marker, dict) else {}), "hit": True}
        return payload
    except (OSError, ValueError):
        return None


def run_entry(api_path, argv=None, *, force_no_cache=False):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--help" in argv or "-h" in argv:
        print(f"用法：{Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        return
    values = [value for value in argv if value not in {"--inline", "--no-cache"}]
    if len(values) != 1:
        raise SystemExit("需要一个 JSON 对象参数；可附加 --inline / --no-cache")
    try:
        params = json.loads(values[0])
    except ValueError as error:
        raise SystemExit(f"JSON 参数格式错误：{error}")
    if not isinstance(params, dict):
        raise SystemExit("参数必须是 JSON 对象")
    check_output_directory()
    root = str((Path.cwd() / "linkfox").resolve())
    use_cache = not force_no_cache and "--no-cache" not in argv
    cache_path = Path(api._cache_path(SLUG, params))
    transport, opener = api.call_api, api.urlopen
    old_root = api._SESSION_CACHE.get("_root")
    old_output = api._resolve_output_path
    old_summary = api.summarize

    def summarize_with_credit(result):
        old_summary(result)
        if isinstance(result, dict) and "costCredit" in result:
            print("  costCredit: " + str(result["costCredit"]))

    def compatible_transport(path, payload):
        cached = _load_cache(cache_path) if use_cache else None
        if cached is not None:
            return cached.get("transportHttpStatus", 200), cached
        captured = {}

        def observe_response(*args, **kwargs):
            try:
                return _ResponseView(opener(*args, **kwargs), captured)
            except HTTPError as error:
                if error.headers is not None:
                    captured.update(error.headers)
                raw = error.read().decode("utf-8") if error.fp else ""
                normalized = io.BytesIO(json.dumps(_decode(raw, error.code, error.reason), ensure_ascii=False).encode("utf-8"))
                # HTTPError 会缓存 read 委托，不能仅替换 fp，否则公共 transport 读到旧的空流。
                error.close()
                raise HTTPError(error.url, error.code, error.reason, error.headers, normalized) from error

        api.urlopen = observe_response
        try:
            status, result = transport(path, payload)
        finally:
            api.urlopen = opener
        if not isinstance(result, dict):
            result = {"error": "网关响应不是 JSON 对象", "details": result}
        # 响应头为本次请求费用的权威值；不以创建响应的 0 覆盖终态查询。
        lowered = {key.lower(): value for key, value in captured.items()}
        for header, field in (("x-cost-token", "costToken"), ("x-cost-credit", "costCredit")):
            if header in lowered:
                value = lowered[header]
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass
                result[field] = value
        result["transportHttpStatus"] = status
        if use_cache:
            try:
                cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            except OSError:
                pass
        return status, result

    api.call_api = compatible_transport
    api._SESSION_CACHE["_root"] = root
    # 公共 runner 使用秒时间戳；业务封装保留快速连续响应，避免覆盖任务编号。
    api._resolve_output_path = lambda slug, stamp: api.resolve_data_path(slug, time.time())
    api.summarize = summarize_with_credit
    try:
        forwarded = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in argv:
            forwarded.append("--inline")
        api.run(api_path, SLUG, argv=forwarded)
    finally:
        api.call_api, api.urlopen = transport, opener
        api._resolve_output_path = old_output
        api.summarize = old_summary
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
