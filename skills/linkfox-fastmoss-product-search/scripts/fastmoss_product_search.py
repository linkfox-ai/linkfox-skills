#!/usr/bin/env python3
"""FastMoss TikTok 商品搜索：使用公共传输和单层响应缓存。

用法：python fastmoss_product_search.py '<JSON 参数>' [--inline] [--no-cache]
"""

import json
import secrets
import sys
import time
from pathlib import Path

import call_api


API_PATH = "/fastmoss/productSearch"
SLUG = "linkfox-fastmoss-product-search"


def _prepare_output():
    """请求前验证当前目录可写，并禁止公共调用器回退到其他目录。"""
    root = Path.cwd() / "linkfox"
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(time.time())
    # 缓存文件写入失败会被忽略；命中缓存或 --no-cache 不写入缓存文件。
    # 公共调用器仍会确保缓存目录存在。
    directory = Path(session_dir) / "data"
    directory.mkdir(parents=True, exist_ok=True)
    probe = directory / (".write_probe-" + secrets.token_hex(6))
    try:
        with probe.open("x", encoding="utf-8"):
            pass
    finally:
        if probe.exists():
            probe.unlink()


def main():
    argv = sys.argv[1:]
    # 无参或非法 JSON 保留公共 CLI 的退出码和错误输出，且不产生请求。
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if positional:
        try:
            json.loads(positional[0])
        except json.JSONDecodeError:
            pass
        else:
            try:
                _prepare_output()
            except OSError as error:
                print(f"当前目录无法保存响应：{error}", file=sys.stderr)
                raise SystemExit(1)
    # 响应缓存的键、路径与 TTL 统一由公共调用器维护。
    call_api.run(API_PATH, SLUG, argv=argv)


if __name__ == "__main__":
    main()
