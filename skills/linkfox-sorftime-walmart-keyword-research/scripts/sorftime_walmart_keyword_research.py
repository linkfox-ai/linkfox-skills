#!/usr/bin/env python3
"""Walmart 关键词研究业务封装：提供 CLI、24 小时缓存、XML 解析与计费头处理。"""
import hashlib
import io
import json
import os
import sys
import time
from contextlib import contextmanager
from urllib.error import HTTPError
from xml.etree import ElementTree
from unittest.mock import patch

import call_api as api_runner

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

API_PATH = "/sorftime/walmart/keywordResearch"
SLUG = "linkfox-sorftime-walmart-keyword-research"
CACHE_TTL_SEC = 24 * 60 * 60
UNCACHEABLE_OPERATIONS = frozenset({"favoriteAdd", "favoriteChange", "favoriteList"})

def _decode_gateway_response(body, http_status=None, reason=None):
    """解析 JSON 响应，并统一网关 ToolErrorResponse XML 的格式。"""
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
    """将网关计费头保留到标准化后的 JSON 响应。"""
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



class _Response:
    """将公共传输层返回的响应转换为其可读取的 JSON，保留状态与计费头。"""
    def __init__(self, body, status, headers, reason=None):
        result = _decode_gateway_response(body, status if status and status >= 300 else None, reason)
        if isinstance(result, dict):
            # 公共 run 不输出传输状态，需在业务结果中保留供认证与错误判断。
            result["_http_status"] = status
        self.status = status
        self.headers = headers
        self.body = json.dumps(_attach_gateway_cost_headers(result, headers), ensure_ascii=False).encode("utf-8")

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


@contextmanager
def _normalize_responses():
    """仅包装公共调用器的接收结果，不自行构造请求、重试或增加网络调用。"""
    public_open = api_runner.urlopen

    def receive(*args, **kwargs):
        try:
            with public_open(*args, **kwargs) as response:
                return _Response(response.read().decode("utf-8"), response.status, response.headers)
        except HTTPError as error:
            try:
                body = error.read().decode("utf-8") if error.fp else ""
                normalized = _Response(body, error.code, error.headers, error.reason)
            finally:
                error.close()
            # 公共调用器继续处理 HTTPError，保留原始 HTTP 状态。
            raise HTTPError(error.url, error.code, error.reason, error.headers, io.BytesIO(normalized.read())) from error

    with patch.object(api_runner, "urlopen", receive):
        yield


def _cwd_root():
    """当前目录不可写即报错，不回退到家目录或临时目录。"""
    root = os.path.join(os.getcwd(), "linkfox")
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, f".keyword-write-probe-{os.getpid()}")
    with open(probe, "w", encoding="utf-8") as stream:
        stream.write("")
    os.remove(probe)
    return root


@contextmanager
def _response_output():
    """请求前预留可写文件，避免付费后才发现无法落盘，以及同秒覆盖。"""
    root = _cwd_root()
    with patch.object(api_runner, "_linkfox_root", lambda: root):
        _, session_dir = api_runner._ensure_session(time.time())
        data_dir = os.path.join(session_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        # 使用纳秒时间戳，并以排他创建确保不会覆盖已有完整响应。
        out_path = os.path.join(data_dir, f"{SLUG}-{time.time_ns()}.json")
        with open(out_path, "x", encoding="utf-8"):
            pass
        try:
            # 公共调用器沿用已检查的路径，完整响应仍由 run 写入。
            with patch.object(api_runner, "_resolve_output_path", lambda slug, ts: out_path):
                yield
            if os.path.getsize(out_path) == 0:
                raise OSError(f"完整响应未保存：{out_path}")
            api_runner._update_meta(
                session_dir, skill=SLUG, kind="data",
                file_rel=os.path.relpath(out_path, session_dir), ts=time.time(),
            )
        finally:
            # 认证失败或落盘失败时不留下空文件；不触碰已有响应。
            if os.path.isfile(out_path) and os.path.getsize(out_path) == 0:
                os.remove(out_path)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or "--help" in argv or "-h" in argv:
        print("用法：sorftime_walmart_keyword_research.py '<JSON 参数>' [--inline] [--no-cache]")
        print("只读研究默认使用 24 小时缓存；收藏新增、变更、列表始终不缓存。")
        return 0 if argv else 1
    args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    try:
        params = json.loads(args[0])
        if not isinstance(params, dict):
            raise ValueError("参数必须为 JSON 对象")
    except (IndexError, ValueError) as error:
        print(f"参数格式无效：{error}", file=sys.stderr)
        return 1

    use_cache = "--no-cache" not in argv and params.get("operation") not in UNCACHEABLE_OPERATIONS
    public_call = api_runner.call_api

    def cached_call(api_path, payload):
        path = _cache_path(payload) if use_cache else None
        cached = _load_cache(path) if use_cache else None
        if cached is not None:
            # 缓存中的状态属于原请求；旧缓存未记录时不补造 HTTP 200。
            return cached.get("_http_status") if isinstance(cached, dict) else None, cached
        status, result = public_call(api_path, payload)
        if use_cache:
            _save_cache(path, result)
        return status, result

    try:
        with _response_output(), _normalize_responses(), patch.object(api_runner, "call_api", cached_call):
            api_runner.run(API_PATH, SLUG, argv=argv + ["--no-cache"])
    except OSError as error:
        print(f"当前目录无法保存响应：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
