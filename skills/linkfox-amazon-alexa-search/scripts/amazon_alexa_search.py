#!/usr/bin/env python3
"""亚马逊 Alexa 购物助手。

用法：python amazon_alexa_search.py '<JSON 参数>' [--inline] [--no-cache]
通过公共调用器完成请求、24 小时缓存、完整响应落盘及摘要输出。
"""

import json
import os
import sys
import tempfile
import time

import call_api

API_PATH = "/amazon/alexaSearch"
SLUG = "linkfox-amazon-alexa-search"


def _prepare_output_root():
    """检查当前目录可写，禁止回退至家目录或临时目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    # 指定会话根目录，响应缓存由公共调用器维护。
    call_api._SESSION_CACHE["_root"] = root


def _resolve_output_path(slug, _ts):
    """使用微秒时间并避开已有文件，保留同一秒内的每份响应。"""
    ts = time.time()
    path = call_api.resolve_data_path(slug, ts)
    while os.path.exists(path):
        ts += 0.000001
        path = call_api.resolve_data_path(slug, ts)
    return path


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = [a for a in argv if a not in ("--inline", "--no-cache")]
    # 缺少参数或 JSON 错误由公共调用器输出 CLI 错误。
    if args:
        try:
            json.loads(args[0])
        except json.JSONDecodeError:
            pass
        else:
            try:
                _prepare_output_root()
            except OSError as exc:
                print(f"当前目录不可写，无法保存完整响应：{exc}", file=sys.stderr)
                raise SystemExit(1)
    # 本次调用使用避免覆盖的文件命名，缓存和传输由公共调用器维护。
    original_resolver = call_api._resolve_output_path
    try:
        call_api._resolve_output_path = _resolve_output_path
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._resolve_output_path = original_resolver


if __name__ == "__main__":
    main()
