"""AIGC 业务兼容层；LinkFox HTTP、落盘和唯一响应缓存由 call_api 提供。"""
import io
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from xml.etree import ElementTree

import call_api

SLUG = "linkfox-aigc-video-translate"


def normal_errcode(value):
    """沿用公共响应规则，明确排除 0 和布尔值。"""
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
    """网关正常后仍检查业务 code 字段；不能把 code 当成 errcode。"""
    return (
        not isinstance(result, dict)
        or bool(result.get("error"))
        or not normal_errcode(result.get("errcode"))
        or result.get("code") not in (None, 0, 200, "0", "200")
    )


def decode_response(body, headers=None):
    """解析 JSON/XML 响应和实际计费头，不发网络请求。"""
    try:
        result = json.loads(body)
    except (ValueError, TypeError):
        try:
            root = ElementTree.fromstring(body)
            if root.tag.rsplit("}", 1)[-1] != "ToolErrorResponse":
                raise ValueError("不是网关错误 XML")
            fields = {child.tag.rsplit("}", 1)[-1]: child.text or "" for child in root}
            code = fields.get("errcode")
            try:
                code = int(code)
            except (TypeError, ValueError):
                pass
            result = {"errcode": code, "errmsg": fields.get("errmsg", "")}
        except (ElementTree.ParseError, ValueError):
            result = {"error": "网关响应格式异常", "details": body}
    if not isinstance(result, dict):
        result = {"error": "网关响应不是 JSON 对象"}
    if headers is not None:
        for header, field in (("X-Cost-Token", "costToken"), ("X-Cost-Credit", "costCredit")):
            value = headers.get(header)
            if value is not None:
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    pass
                result[field] = value
    return result


class _Response:
    """仅将公共调用器已取得的响应规范化；请求由 call_api 的传输函数发起。"""
    def __init__(self, response):
        self.response = response
        self.status = response.status

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    def read(self):
        body = self.response.read().decode("utf-8", errors="replace")
        return json.dumps(decode_response(body, self.response.headers), ensure_ascii=False).encode("utf-8")


def run_entry(api_path, operation, argv=None, force_no_cache=False):
    """通过 call_api.run 执行 AIGC 调用，退出时还原钩子。"""
    from material_runtime import check_output_directory

    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or "--help" in argv or "-h" in argv:
        print(f"用法：{Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        if not argv:
            raise SystemExit(1)
        return
    # 先移除选项再读取 JSON，支持选项位于位置参数之前。
    parameters = [arg for arg in argv if arg not in {"--inline", "--no-cache"}]
    if not parameters:
        raise SystemExit("请提供 JSON 参数")
    try:
        params = json.loads(parameters[0])
    except ValueError as error:
        raise SystemExit(f"JSON 参数格式错误：{error}")
    if not isinstance(params, dict):
        raise SystemExit("参数必须是 JSON 对象")
    check_output_directory()
    # 在调用之前检查认证，尤其避免先下载用户素材。
    call_api.get_api_key()
    call_api._SESSION_CACHE["_root"] = str((Path.cwd() / "linkfox").resolve())
    if force_no_cache and "--no-cache" not in argv:
        argv.append("--no-cache")

    names = ("urlopen", "call_api", "_cache_path", "_load_cache", "_is_cacheable", "_resolve_output_path")
    original = {name: getattr(call_api, name) for name in names}

    def adapt_urlopen(*args, **kwargs):
        try:
            return _Response(original["urlopen"](*args, **kwargs))
        except HTTPError as error:
            raw = error.read().decode("utf-8", errors="replace") if error.fp else ""
            payload = decode_response(raw, error.headers)
            # call_api 负责 HTTP 状态和错误处理；这里只转换错误体。
            normalized = io.BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            raise HTTPError(error.url, error.code, error.reason, error.headers, normalized) from error

    def checked_call(path, parameters):
        status, result = original["call_api"](path, parameters)
        if not isinstance(result, dict):
            result = {"error": "网关响应不是 JSON 对象"}
        if status is None or not 200 <= status < 300:
            result.setdefault("error", f"HTTP {status}" if status is not None else "网络连接失败")
            result["_transportHttpStatus"] = status
        elif api_error(result):
            result["_transportHttpStatus"] = status
        return status, result

    def cache_path(slug, parameters):
        # 创建缓存使用技能标识，操作响应的文件名使用各自标识。
        return original["_cache_path"](SLUG if operation == "videoTranslation" else slug, parameters)

    def load_cache(path):
        try:
            if time.time() - os.path.getmtime(path) > call_api.CACHE_TTL_SEC:
                return None
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return None
            if raw.get("_cache_version") == 1:
                status, payload = raw.get("http_status"), raw.get("body")
                if type(status) is not int or not 200 <= status < 300:
                    return None
            else:
                payload = raw  # 缓存可直接存响应对象；只复用已接受的任务编号。
            if api_error(payload) or not payload.get("taskId"):
                return None
            payload["_cache"] = {"hit": True}
            return payload
        except (OSError, ValueError):
            return None

    def cacheable(status, payload):
        return (type(status) is int and 200 <= status < 300
                and not api_error(payload) and bool(payload.get("taskId")))

    call_api.urlopen = adapt_urlopen
    call_api.call_api = checked_call
    call_api._cache_path = cache_path
    call_api._load_cache = load_cache
    call_api._is_cacheable = cacheable
    # 响应文件使用微秒命名，避免快速轮询覆盖。
    call_api._resolve_output_path = lambda slug, stamp: call_api.resolve_data_path(slug, time.time())
    try:
        call_api.run(api_path, SLUG + "-" + operation, argv)
    finally:
        for name, value in original.items():
            setattr(call_api, name, value)
