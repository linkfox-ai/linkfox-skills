"""商品套图适配：复用公共执行器，处理 XML、费用头和单层缓存。"""
import io
import json
import os
from pathlib import Path
import sys
import time
from contextlib import ExitStack
from unittest.mock import patch
from urllib.error import HTTPError
from xml.etree import ElementTree

import call_api as shared

SLUG = "linkfox-aigc-product-suite"
CACHE_TTL_SEC = 24 * 60 * 60


def strict_root():
    """请求前验证任务目录，禁止共享模板静默回退到其他目录。"""
    from material_runtime import check_output_directory
    check_output_directory()
    return str((Path.cwd() / "linkfox").resolve())


def resolve_data_path(slug, ts, ext="json"):
    with patch.object(shared, "_linkfox_root", strict_root):
        # 使用当前时钟的小数部分，避免连续查询在同一秒覆盖历史响应。
        return shared.resolve_data_path(slug, time.time(), ext)


def _ensure_session(ts):
    with patch.object(shared, "_linkfox_root", strict_root):
        return shared._ensure_session(ts)


_update_meta = shared._update_meta
get_api_key = shared.get_api_key


def _cache_path(params):
    # 按参数散列访问缓存目录中的已有文件，使用单层缓存。
    return shared._cache_path(SLUG, params)


def _load_cache(path):
    if not os.path.isfile(path) or time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as source:
            payload = json.load(source)
        if not isinstance(payload, dict):
            return None
        if not isinstance(payload.get("_cache"), dict):
            payload["_cache"] = {}
        payload["_cache"]["hit"] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as output:
            json.dump(payload, output, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _decode(body, headers, http_status=None, reason=None):
    """解析网关 XML 错误和实际费用响应头，交给公共 HTTP 层读取 JSON。"""
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeError):
        try:
            root = ElementTree.fromstring(body)
            if root.tag.rsplit("}", 1)[-1] != "ToolErrorResponse":
                raise ValueError("不是网关标准错误")
            fields = {node.tag.rsplit("}", 1)[-1]: node.text or "" for node in root}
            code = fields.get("errcode")
            try:
                code = int(code)
            except (TypeError, ValueError):
                pass
            payload = {"errcode": code, "errmsg": fields.get("errmsg", "")}
        except (ElementTree.ParseError, ValueError):
            label = f"HTTP {http_status}: {reason}" if http_status is not None else "网关响应格式无效"
            payload = {"error": label}
            if body:
                payload["details"] = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else body
    if not isinstance(payload, dict):
        payload = {"error": "网关响应不是 JSON 对象", "details": payload}
    for header, field in (("X-Cost-Token", "costToken"), ("X-Cost-Credit", "costCredit")):
        value = headers.get(header) if headers is not None else None
        if value is not None:
            try:
                value = int(value)
            except (TypeError, ValueError):
                pass
            payload[field] = value
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class _Response:
    """仅规范化公共传输已取得的响应，不创建独立 HTTP 请求。"""
    def __init__(self, response):
        self.response = response
        self.status = response.status

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    def read(self):
        return _decode(self.response.read(), self.response.headers)


def is_error(payload):
    """按外层 HTTP 与 errcode 基础规则判断，再识别接口的 error/code。"""
    status = payload.get("transportHttpStatus", 200)
    if status is None or not 200 <= status < 300 or payload.get("error"):
        return True
    code = payload.get("errcode")
    if code is not None and not (isinstance(code, str) and not code.strip()):
        if isinstance(code, bool):
            return True
        if isinstance(code, str):
            code = code.strip()
            if len(code) != 3 or not code.isascii() or not code.isdigit():
                return True
            code = int(code)
        if type(code) not in (int, float) or not 200 <= code < 300 or code % 1:
            return True
    # code 是接口额外的业务失败标志，不替代 errcode / HTTP 规则。
    return payload.get("code") not in (None, 0, 200, "0", "200")


def run_entry(api_path, argv=None):
    """提供 JSON CLI 和单层缓存；所有 LinkFox HTTP 请求由公共执行器完成。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    parameters = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not parameters or "--help" in argv or "-h" in argv:
        print(f"用法: {Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        if "--help" not in argv and "-h" not in argv:
            raise SystemExit(1)
        return
    try:
        params = json.loads(parameters[0])
    except json.JSONDecodeError as error:
        raise SystemExit(f"JSON 参数格式错误：{error}")
    if not isinstance(params, dict):
        raise SystemExit("参数必须为 JSON 对象")
    strict_root()
    get_api_key()
    # 在可能扣费前验证完整输出路径，含 Windows 路径长度；不能仅探测根目录。
    reserved_output = resolve_data_path(SLUG, time.time())
    with open(reserved_output, "x", encoding="utf-8"):
        pass
    os.remove(reserved_output)
    use_cache = "--no-cache" not in argv and api_path != "/aigc/taskQuery"
    old_cache = _cache_path(params) if use_cache else None
    cached = _load_cache(old_cache) if use_cache else None
    transport = shared.urlopen
    http_call = shared.call_api

    def normalize_response(*args, **kwargs):
        # Request、URL、请求头、超时和网络发送仍由公共 call_api.py 负责。
        try:
            return _Response(transport(*args, **kwargs))
        except HTTPError as error:
            body = error.read() if error.fp else b""
            # HTTPError.read 绑定原 file；只替换 fp 无效，需建立规范化异常。
            normalized = io.BytesIO(_decode(body, error.headers, error.code, error.reason))
            raise HTTPError(error.url, error.code, error.reason, error.headers, normalized) from error

    def business_call(path, payload):
        if cached is not None:
            return cached.get("transportHttpStatus", 200), cached
        status, result = http_call(path, payload)
        result["transportHttpStatus"] = status
        if status is not None and not 200 <= status < 300:
            result.setdefault("error", f"HTTP {status}")
        if use_cache:
            _save_cache(old_cache, result)
        return status, result

    def output_path(slug, ts):
        return reserved_output

    summarize = shared.summarize

    def summarize_with_cost(result):
        summarize(result)
        if isinstance(result, dict) and "costCredit" in result:
            print(f"  costCredit: {result['costCredit']}")

    with ExitStack() as stack:
        stack.enter_context(patch.object(shared, "urlopen", normalize_response))
        stack.enter_context(patch.object(shared, "call_api", business_call))
        stack.enter_context(patch.object(shared, "_linkfox_root", strict_root))
        stack.enter_context(patch.object(shared, "_resolve_output_path", output_path))
        stack.enter_context(patch.object(shared, "summarize", summarize_with_cost))
        # 响应缓存由业务层负责，公共执行器不得再缓存一次。
        shared.run(api_path, SLUG, argv + ["--no-cache"])
    if not Path(reserved_output).is_file():
        raise RuntimeError("完整响应未能保存；保留已接受的 taskId，不重新创建任务")
