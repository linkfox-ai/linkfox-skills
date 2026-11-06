#!/usr/bin/env python3
"""WallySmarter Walmart 商品详情入口。

用法：python wallysmarter_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
默认保留 24 小时缓存；完整响应始终落盘，小响应全量输出，大响应摘要输出。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.error import HTTPError, URLError

import call_api

API_PATH = "/wallysmarter/productDetail"
SLUG = "linkfox-wallysmarter-product-detail"


def _call_with_http_status(api_path, params):
    """保留传输状态，避免 JSON 错误体掩盖 HTTP 401/402 等失败。"""
    request = call_api.Request(
        call_api.get_api_url(api_path),
        data=json.dumps(params).encode("utf-8"),
        headers={
            "Authorization": call_api.get_api_key(),
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/2.0",
            **{name: os.environ.get(name, "") for name in
               ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME")},
        },
        method="POST",
    )
    try:
        with call_api.urlopen(request, timeout=150) as response:
            result = json.loads(response.read().decode("utf-8"))
            status = response.status
    except HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8") if exc.fp else ""
        try:
            result = json.loads(body)
        except ValueError:
            result = {"error": f"HTTP {status}: {exc.reason}", "details": body}
        if not isinstance(result, dict):
            result = {"error": f"HTTP {status}: {exc.reason}", "details": result}
    except URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}
    if isinstance(result, dict):
        result["_http_status"] = status
    return result


def _prepare_output_root():
    """在当前目录准备响应落盘位置，禁止静默回退到家目录或 /tmp。"""
    cwd = Path.cwd().resolve()
    forbidden = Path("/tmp").resolve()
    if cwd == forbidden or forbidden in cwd.parents:
        raise OSError("禁止在 /tmp 中保存响应，请在可写的项目目录运行")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return os.fspath(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # 无参数时复用公共调用器的 CLI 错误，不提前创建输出目录。
    if not [arg for arg in argv if arg not in ("--inline", "--no-cache")]:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        root = _prepare_output_root()
    except OSError as exc:
        print(f"无法在当前目录保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    previous_root = call_api._SESSION_CACHE.get("_root")
    previous_call = call_api.call_api
    call_api._SESSION_CACHE["_root"] = root
    call_api.call_api = _call_with_http_status
    try:
        return call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api.call_api = previous_call
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
