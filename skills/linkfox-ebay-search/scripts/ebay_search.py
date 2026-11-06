#!/usr/bin/env python3
"""eBay 商品搜索；公共调用器提供唯一的 HTTP、24 小时缓存及输出流程。

用法：python ebay_search.py '<JSON 参数>' [--inline] [--no-cache]
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api as _runner


API_PATH = "/ebay/search"
SLUG = "linkfox-ebay-search"


def main(argv=None):
    """复用公共流程，仅在当前工作目录落盘。"""
    args = list(sys.argv[1:] if argv is None else argv)
    # 无参数或错误 JSON 交由公共调用器输出 CLI 错误，不预建会话。
    positional = [a for a in args if a not in ("--inline", "--no-cache")]
    if not positional:
        return _runner.run(API_PATH, SLUG, argv=args)
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError:
        return _runner.run(API_PATH, SLUG, argv=args)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        raise SystemExit(1)

    cwd = Path.cwd()
    if os.name != "nt" and cwd.is_relative_to(Path("/tmp")):
        raise OSError("禁止将会话数据写入 /tmp，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 请求前确认可写，不允许公共调用器回退到家目录或临时目录。
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_root = _runner._SESSION_CACHE.get("_root")
    _runner._SESSION_CACHE["_root"] = str(root)
    try:
        # 根目录可写不代表日期、会话及 data 目录可写；全部检查后再请求。
        _, session_dir = _runner._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        return _runner.run(API_PATH, SLUG, argv=args)
    finally:
        if previous_root is None:
            _runner._SESSION_CACHE.pop("_root", None)
        else:
            _runner._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
