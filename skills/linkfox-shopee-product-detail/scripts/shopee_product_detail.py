#!/usr/bin/env python3
"""Shopee 单商品详情 CLI；保留 HTTP 状态，复用公共缓存及输出流程。

用法：python shopee_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
"""
import json
import os
import sys
import tempfile
import time

import call_api

API_PATH = "/shopee/product/detail"
SLUG = "linkfox-shopee-product-detail"


def _with_http_status(payload, status):
    """保留响应正文，并单独记录本次请求的实际 HTTP 状态。"""
    result = dict(payload) if isinstance(payload, dict) else {"_response_body": payload}
    result["_http_status"] = status
    return result


def _request(api_path, params):
    """商品查询保留 HTTP 状态；缓存与落盘仍由公共调用器维护。"""
    headers = {
        "Authorization": call_api.get_api_key(),
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        **{name: os.environ.get(name, "")
           for name in ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME")},
    }
    request = call_api.Request(
        call_api.get_api_url(api_path),
        data=json.dumps(params).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with call_api.urlopen(request, timeout=150) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return _with_http_status(payload, response.getcode())
    except call_api.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        try:
            payload = json.loads(body) if body else {"error": f"HTTP {exc.code}: {exc.reason}"}
        except json.JSONDecodeError:
            payload = {"error": f"HTTP {exc.code}: {exc.reason}", "details": body}
        return _with_http_status(payload, exc.code)
    except call_api.URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}


def _working_root():
    """在当前目录保存输出；请求前确认可写，不向外回退。"""
    root = os.path.join(os.getcwd(), "linkfox")
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def _prepare_output():
    """在可能计费的请求前检查实际会话输出位置，不只检查根目录。"""
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass
    # 公共调用器保存响应时还会更新已有元数据；提前检查写权限。
    with open(os.path.join(session_dir, "_meta.json"), "r+", encoding="utf-8"):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法：python shopee_product_detail.py '<JSON 参数>' [--inline] [--no-cache]")
        print("JSON 参数：productUrl，完整要求见 references/api.md。")
        print("默认复用 24 小时本地缓存；--no-cache 跳过读写，--inline 强制全量输出。")
        return
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional:
        call_api.run(API_PATH, SLUG, argv=argv)
        return
    # 先解析参数；语法错误不应创建缓存或会话目录。
    try:
        json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
    try:
        root = _working_root()
    except OSError as exc:
        print(f"当前工作目录不可写，已停止查询：{exc}", file=sys.stderr)
        raise SystemExit(1)
    # 为本业务入口限定落盘根目录。
    previous_root = call_api._SESSION_CACHE.get("_root")
    previous_request = call_api.call_api
    call_api._SESSION_CACHE["_root"] = root
    call_api.call_api = _request
    try:
        try:
            _prepare_output()
        except OSError as exc:
            print(f"当前会话输出位置不可写，已停止查询：{exc}", file=sys.stderr)
            raise SystemExit(1)
        # 由公共调用器维护唯一一层缓存。
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api.call_api = previous_request
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
