#!/usr/bin/env python3
"""Walmart 类目研究：提供业务缓存、XML 解码和费用字段，委托公共调用器发送请求。

用法：python sorftime_walmart_category_market.py '<JSON 参数>' [--inline] [--no-cache]
完整响应保存在当前目录的 linkfox 会话目录；大于 8000 字节默认只展示摘要。
"""

import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from contextlib import contextmanager
from urllib.error import HTTPError
from xml.etree import ElementTree
from unittest.mock import patch

import call_api as api

API_PATH = "/sorftime/walmart/categoryMarket"
SLUG = "linkfox-sorftime-walmart-category-market"
CACHE_TTL_SEC = 24 * 60 * 60

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _decode_gateway_response(body, http_status=None, reason=None):
    """保留 JSON 原值；将含命名空间的 ToolErrorResponse XML 转为 JSON。"""
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
    label = f"HTTP {http_status}" if http_status is not None else "Invalid gateway response format"
    if http_status is not None and reason:
        label += f": {reason}"
    result = {"error": label}
    if body:
        result["details"] = body
    return result


def _attach_gateway_cost_headers(result, headers):
    """费用头是本次请求的权威值，覆盖同名响应体字段，保留 0。"""
    if not isinstance(result, dict) or headers is None:
        return result
    for header, field in (("X-Cost-Token", "costToken"), ("X-Cost-Credit", "costCredit")):
        value = headers.get(header)
        if value is None:
            continue
        try:
            value = int(value)
        except (TypeError, ValueError):
            pass
        result[field] = value
    return result


def _normalized_body(body, headers, http_status=None, reason=None):
    result = _decode_gateway_response(body.decode("utf-8"), http_status, reason)
    return json.dumps(_attach_gateway_cost_headers(result, headers), ensure_ascii=False).encode("utf-8")


class _GatewayResponse:
    """仅适配公共 transport 已取得的响应，不构造或发送 HTTP 请求。"""

    def __init__(self, response):
        self.response = response
        self.status = response.status

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    def read(self):
        return _normalized_body(self.response.read(), self.response.headers)


@contextmanager
def _adapt_gateway_response():
    """为公共调用器适配响应解码；实际发送使用其 transport。"""
    transport_open = api.urlopen

    def adapted_open(request, timeout):
        try:
            return _GatewayResponse(transport_open(request, timeout=timeout))
        except HTTPError as error:
            try:
                body = error.read() if error.fp else b""
                normalized = _normalized_body(body, error.headers, error.code, error.reason)
            finally:
                error.close()
            raise HTTPError(error.url, error.code, error.reason, error.headers, io.BytesIO(normalized)) from error

    with patch.object(api, "urlopen", adapted_open):
        yield


def _call_with_status(params):
    with _adapt_gateway_response():
        status, result = api.call_api(API_PATH, params)
    return _retain_http_status(status, result)


def _retain_http_status(status, result):
    """本地诊断保留实际 HTTP 状态；连接失败为 None，不改写网关业务码。"""
    if isinstance(result, dict):
        result["_http_status"] = status
    return status, result


def call_api(params):
    """调用接口并返回响应体。"""
    return _call_with_status(params)[1]


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    path = Path.cwd() / "linkfox" / ".cache" / SLUG
    path.mkdir(parents=True, exist_ok=True)
    return str(path / f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path) or time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as stream:
            payload = json.load(stream)
        if isinstance(payload, dict):
            payload.setdefault("_cache", {})["hit"] = True
            # 旧缓存没有 HTTP 状态证据，保持未知，不能推断为成功。
            payload.setdefault("_http_status", None)
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
    except OSError:
        pass


def summarize(result):
    api.summarize(result)
    if isinstance(result, dict):
        for field in ("_http_status", "operation", "requestConsumed", "costCredit"):
            if field in result:
                print(f"  {field}: {result[field]}")


def _writable_root():
    """在收费请求前检查 cwd 可写，按技能约定禁止向 /tmp 或其他目录回退。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("本技能禁止写入 /tmp，请在可写的项目目录运行。")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv == ["--help"]:
        print("用法：sorftime_walmart_category_market.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        return 0 if argv else 1
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not args:
        print("缺少 JSON 参数", file=sys.stderr)
        return 1
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as error:
        print(f"参数 JSON 格式错误：{error}", file=sys.stderr)
        return 1
    try:
        root = _writable_root()
        cache_path = _cache_path(params)
        # 预先创建会话输出路径，权限问题必须在生产请求之前暴露。
        with patch.object(api, "_linkfox_root", lambda: root):
            output_path = api.resolve_data_path(SLUG, time.time())
        with open(output_path, "w", encoding="utf-8"):
            pass
    except OSError as error:
        print(f"当前工作目录不可写：{error}", file=sys.stderr)
        return 1

    transport = api.call_api
    original_summarize = api.summarize

    def request_or_cache(api_path, request_params):
        result = _load_cache(cache_path) if use_cache else None
        if result is not None:
            return result.get("_http_status") if isinstance(result, dict) else None, result
        with _adapt_gateway_response():
            status, result = transport(api_path, request_params)
        status, result = _retain_http_status(status, result)
        if use_cache:
            _save_cache(cache_path, result)
        return status, result

    def show_summary(result):
        original_summarize(result)
        if isinstance(result, dict):
            for field in ("_http_status", "operation", "requestConsumed", "costCredit"):
                if field in result:
                    print(f"  {field}: {result[field]}")

    # 只使用业务缓存。run 负责输出和落盘，其第二层缓存始终关闭。
    run_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        run_argv.append("--inline")
    with patch.object(api, "call_api", request_or_cache), \
         patch.object(api, "_resolve_output_path", lambda slug, ts: output_path), \
         patch.object(api, "summarize", show_summary):
        api.run(API_PATH, SLUG, argv=run_argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
