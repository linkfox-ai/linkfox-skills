#!/usr/bin/env python3
"""Walmart 产品分析：响应解析、缓存和命令行调用。

用法：python sorftime_walmart_product_analysis.py '<JSON 参数>' [--inline] [--no-cache]
完整响应保存在当前工作目录的 linkfox/<日期>/<会话>/data/；不回退临时目录。
默认使用 24 小时缓存及 8000 字节摘要阈值。
"""

import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from urllib.error import HTTPError
from xml.etree import ElementTree

import call_api as api

API_PATH = "/sorftime/walmart/productAnalysis"
SLUG = "linkfox-sorftime-walmart-product-analysis"
CACHE_TTL_SEC = 24 * 60 * 60

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

def _decode_gateway_response(body, http_status=None, reason=None):
    """解析 JSON 并兼容网关 ToolErrorResponse XML。"""
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
    """将网关计费响应头补入规范化 JSON。"""
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
        # 网关计费响应头是本次请求的权威扣费值。
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
        if isinstance(payload, dict):
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


class _CompatibleResponse:
    """只适配公共 transport 已取得的响应，不创建请求或另发 HTTP。"""

    def __init__(self, response):
        self.response = response

    def __getattr__(self, name):
        return getattr(self.response, name)

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    def read(self):
        raw = self.response.read().decode("utf-8")
        payload = _decode_gateway_response(raw)
        payload = _attach_gateway_cost_headers(payload, self.response.headers)
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not args:
        print("用法：sorftime_walmart_product_analysis.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        raise SystemExit(1)

    # 在任何收费请求前验证当前目录可写，不使用公共调用器的回退目录。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    transport = api.call_api
    opener = api.urlopen
    old_cache_path = api._cache_path
    old_output_path = api._resolve_output_path
    old_summarize = api.summarize
    old_root = api._SESSION_CACHE.get("_root")

    def compatible_open(request, **kwargs):
        # 请求构造、认证、超时与发送均由公共调用器 call_api.py 负责。
        try:
            return _CompatibleResponse(opener(request, **kwargs))
        except HTTPError as exc:
            raw = exc.read().decode("utf-8") if exc.fp else ""
            payload = _decode_gateway_response(raw, exc.code, exc.reason)
            payload = _attach_gateway_cost_headers(payload, exc.headers)
            raise HTTPError(exc.url, exc.code, exc.reason, exc.headers,
                            io.BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8"))) from exc

    def legacy_cached_call(api_path, request_params):
        path = _cache_path(request_params)
        result = _load_cache(path) if use_cache else None
        if result is not None:
            # 命中缓存不产生本次 HTTP 状态；旧缓存的原始状态未知，不补造成功值或重发请求。
            return None, result
        status, result = transport(api_path, request_params)
        if isinstance(result, dict):
            # 公共输出器仅保存响应体；在业务层保留实际 HTTP 状态供错误分流。
            # 缓存命中时保留原请求状态，不为没有状态的旧缓存补造成功值。
            result["_http_status"] = status
        if use_cache:
            _save_cache(path, result)
        return status, result

    def summarize_with_billing(result):
        # 大响应仍需展示本次操作、上游消耗及响应头中的实际扣费。
        # 命中缓存时这些字段来自原请求，不代表本次新增扣费。
        if isinstance(result, dict):
            for field in ("_http_status", "operation", "requestConsumed", "costCredit"):
                if field in result:
                    print(f"  {field}: {result[field]}")
        old_summarize(result)

    api.urlopen = compatible_open
    api.call_api = legacy_cached_call
    api.summarize = summarize_with_billing
    # run 始终 --no-cache；统一使用本技能缓存目录，不创建第二套缓存文件或格式。
    api._cache_path = lambda _slug, request_params: _cache_path(request_params)
    api._SESSION_CACHE["_root"] = str(root)
    # 保留每次调用的独立数据文件，避免同一秒内覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        forwarded = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            forwarded.append("--inline")
        api.run(API_PATH, SLUG, argv=forwarded)
    finally:
        api.urlopen = opener
        api.call_api = transport
        api._cache_path = old_cache_path
        api._resolve_output_path = old_output_path
        api.summarize = old_summarize
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root


if __name__ == "__main__":
    main()
