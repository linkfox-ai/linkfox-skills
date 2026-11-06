#!/usr/bin/env python3
"""1688商品热销榜单CLI：提供24小时缓存、会话落盘和大小响应输出策略。"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/dld/productBillboard"
SLUG = "linkfox-dld-product-billboard"


def main(argv=None):
    """业务入口只固定本技能的输出目录，缓存与请求均由公共调用器处理。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not params:
        return call_api.run(API_PATH, SLUG, argv)
    try:
        json.loads(params[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv)

    # 输出目录固定在当前工作目录，不回退到家目录或临时目录。
    root = Path.cwd() / "linkfox"
    # 本次调用期间固定会话根目录，不影响响应缓存算法。
    previous = call_api._SESSION_CACHE.get("_root")
    call_api._SESSION_CACHE["_root"] = os.fspath(root)
    try:
        try:
            # 检查实际会话的 data 目录，避免根目录可写而嵌套目录被占用时先付费。
            _, session_dir = call_api._ensure_session(time.time())
            data_dir = Path(session_dir) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
        except OSError as exc:
            print(f"当前目录不可写，未请求接口：{exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        return call_api.run(API_PATH, SLUG, argv)
    finally:
        if previous is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous


if __name__ == "__main__":
    main()
