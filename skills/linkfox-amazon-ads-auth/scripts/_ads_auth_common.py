"""Ads 授权业务兼容层；HTTP 仅由 call_api.py 执行。"""

from contextlib import contextmanager, nullcontext, redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from xml.etree import ElementTree

import call_api as api

SLUG = "linkfox-amazon-ads-auth"


def is_success(http_status, result):
    """授权接口兼容旧版的 0 和 "0" 成功码。"""
    if http_status is None or not 200 <= http_status < 300 or not isinstance(result, dict):
        return False
    code = result.get("errcode")
    if (code is None or type(code) is int and code == 0
            or isinstance(code, str) and code.strip() in ("", "0")):
        return not result.get("error")
    if isinstance(code, str):
        code = code.strip()
        if not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and not result.get("error")


def _normalize_xml(raw):
    """兼容解绑入口的 ToolErrorResponse XML。"""
    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError:
        return raw
    if root.tag.rsplit("}", 1)[-1] != "ToolErrorResponse":
        return raw
    fields = {child.tag.rsplit("}", 1)[-1]: child.text or "" for child in root}
    code = fields.get("errcode")
    try:
        code = int(code)
    except (TypeError, ValueError):
        pass
    return json.dumps({"errcode": code, "errmsg": fields.get("errmsg", "")},
                      ensure_ascii=False).encode("utf-8")


class _Response:
    def __init__(self, response, evidence):
        self.response = response
        self.status = response.status
        self.evidence = evidence

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    def read(self):
        raw = self.response.read()
        self.evidence["raw_body"] = raw
        return _normalize_xml(raw)


def request(path, params, *, persist=False, inline=False):
    """运行公共 CLI；自动模式只在内存捕获输出，不落盘或复制 OAuth URL。

    每个脚本进程串行调用；临时兼容钩子总在 finally 中恢复。
    """
    root = Path.cwd() / "linkfox"
    if persist:
        # 请求前验证当前目录；不使用公共调用器的 HOME/临时目录回退。
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass

    names = ("call_api", "urlopen", "_cache_path", "_resolve_output_path", "open")
    missing = object()
    previous = {name: getattr(api, name, missing) for name in names}
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    old_root = api._SESSION_CACHE.get("_root", missing)
    received = {}
    billing_headers = {}

    def capture_response(*args, **kwargs):
        try:
            response = previous["urlopen"](*args, **kwargs)
            received["http_status"] = response.status
            billing_headers.update(response.headers or {})
            return _Response(response, received)
        except api.HTTPError as exc:
            received["http_status"] = exc.code
            billing_headers.update(exc.headers or {})
            raw = exc.read()
            received["raw_body"] = raw
            exc.close()
            # HTTPError.read 可能缓存旧流的方法；新建同类错误以确保公共层读取归一化内容。
            raise api.HTTPError(exc.url, exc.code, exc.reason, exc.headers,
                                io.BytesIO(_normalize_xml(raw))) from None

    def transport(api_path, request_params):
        try:
            status, result = previous["call_api"](api_path, request_params)
        except (ValueError, UnicodeError) as exc:
            status = received.get("http_status")
            raw = received.get("raw_body", b"")
            result = {"error": f"网关响应格式错误：{exc}",
                      "details": raw.decode("utf-8", errors="replace")}
        if not isinstance(result, dict):
            result = {"error": "网关响应必须为 JSON 对象", "details": result}
        for header, field in (("X-Cost-Token", "costToken"), ("X-Cost-Credit", "costCredit")):
            value = next((v for k, v in billing_headers.items() if k.lower() == header.lower()), None)
            if value is not None:
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    pass
                result[field] = value
        if not is_success(status, result):
            result.setdefault("error", result.get("errmsg") or f"HTTP {status}：请求未正常完成")
            result["transportHttpStatus"] = status
        received["result"] = result
        return status, result

    @contextmanager
    def output_file(*args, **kwargs):
        try:
            with open(*args, **kwargs) as handle:
                yield handle
        except OSError as exc:
            received["save_error"] = str(exc)
            raise

    try:
        if not old_gateway:
            os.environ["LINKFOX_TOOL_GATEWAY"] = (
                os.environ.get("AMAZON_ADS_BASE_URL") or api.get_api_base())
        api.call_api = transport
        api.urlopen = capture_response
        # 业务请求不使用响应缓存；同时避免 run 无条件创建空缓存目录。
        api._cache_path = lambda *_args: ""
        if persist:
            api._SESSION_CACHE["_root"] = str(root)
            api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
            api.open = output_file
        else:
            api._resolve_output_path = lambda *_args: "<仅内存>"
            api.open = lambda *_args, **_kwargs: io.StringIO()
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            argv.append("--inline")
        try:
            with nullcontext() if persist else redirect_stdout(io.StringIO()):
                api.run(path, SLUG, argv=argv)
        except OSError as exc:
            if "result" not in received:
                raise
            received["save_error"] = str(exc)
            print(json.dumps(received["result"], ensure_ascii=False), file=sys.stdout)
        if received.get("save_error"):
            # 请求可能已完成；保存失败只能报告，绝不能重新发送写操作。
            received["result"]["error"] = "请求已完成，但保存响应失败：" + received["save_error"]
            print(received["result"]["error"], file=sys.stderr)
        return received["result"]
    finally:
        for name, value in previous.items():
            if value is missing:
                if hasattr(api, name):
                    delattr(api, name)
            else:
                setattr(api, name, value)
        if old_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_gateway
        if old_root is missing:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root


def cli_params(argv, *, required=False):
    """保留位置 JSON 与 --inline/--no-cache；空参数用于读取快照。"""
    args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if len(args) > 1 or required and not args:
        raise ValueError("用法：'<JSON 参数>' [--inline] [--no-cache]")
    params = json.loads(args[0]) if args else {}
    if not isinstance(params, dict):
        raise ValueError("参数必须为 JSON 对象")
    return params
