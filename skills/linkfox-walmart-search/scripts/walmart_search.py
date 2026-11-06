#!/usr/bin/env python3
"""Walmart 商品搜索：复用公共调用器的一层缓存与输出流程。

用法：python walmart_search.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；不超过 8 KB 时全量输出，否则打印摘要。
"""

import os
import sys
import tempfile
import time

import call_api
from call_api import run


API_PATH = "/walmart/search"
SLUG = "linkfox-walmart-search"


def _cwd_root():
    """使用 cwd 下的落盘目录，禁止回退到家目录或临时目录。"""
    root = os.path.join(os.getcwd(), "linkfox")
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def main():
    argv = sys.argv[1:]
    original_root = call_api._linkfox_root
    try:
        call_api._linkfox_root = _cwd_root
        if any(arg not in ("--inline", "--no-cache") for arg in argv):
            # 根目录可写不代表会话目录可写；先验证完整落盘位置，
            # 避免请求消耗算力后才发现 data 路径被文件占用或无写权限。
            _, session_dir = call_api._ensure_session(time.time())
            data_dir = os.path.join(session_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
        run(API_PATH, SLUG, argv=argv)
    except OSError as exc:
        print(f"当前工作目录无法保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        call_api._linkfox_root = original_root


if __name__ == "__main__":
    main()
