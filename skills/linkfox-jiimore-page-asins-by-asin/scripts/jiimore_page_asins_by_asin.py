#!/usr/bin/env python3
"""极目同细分市场竞品查询。

用法：python jiimore_page_asins_by_asin.py '<JSON 参数>' [--inline] [--no-cache]
24 小时缓存和输出策略由公共调用器统一执行。
"""

import os
import sys
import tempfile
import time

import call_api


API_PATH = "/jiimore/pageAsinsByAsin"
SLUG = "linkfox-jiimore-page-asins-by-asin"


def _prepare_output_root():
    """将输出限定在当前工作目录，禁止公共调用器回退到其他目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    try:
        os.makedirs(root, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"当前工作目录不可写，无法保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    call_api._SESSION_CACHE["_root"] = root


def _resolve_unique_output_path(slug, ts):
    """以微秒时间戳独占创建文件，保留同秒调用的每份完整响应。"""
    stamp = max(int(ts * 1_000_000), time.time_ns() // 1000)
    while True:
        path = call_api.resolve_data_path(slug, stamp / 1_000_000)
        try:
            with open(path, "x", encoding="utf-8"):
                pass
            return path
        except FileExistsError:
            stamp += 1


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        _prepare_output_root()
    original_resolver = call_api._resolve_output_path
    call_api._resolve_output_path = _resolve_unique_output_path
    try:
        call_api.run(API_PATH, SLUG, argv=args)
    finally:
        call_api._resolve_output_path = original_resolver


if __name__ == "__main__":
    main()
