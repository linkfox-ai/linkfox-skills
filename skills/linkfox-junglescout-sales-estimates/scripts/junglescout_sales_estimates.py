#!/usr/bin/env python3
"""Jungle Scout ASIN 销售估算，使用公共调用器请求、缓存和保存响应。

用法：
  python junglescout_sales_estimates.py '<JSON 参数>' [--inline] [--no-cache]

提供 24 小时缓存、完整响应落盘和 8 KB 输出阈值。
--inline 强制完整打印；--no-cache 禁止读取和写入响应缓存。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/tool-jungle-scout/sales-estimates/query"
SLUG = "linkfox-junglescout-sales-estimates"


def _prepare_output_root():
    """请求前确认当前目录可保存响应，禁止公共调用器回退到其他目录。"""
    cwd = Path.cwd().resolve()
    tmp = Path("/tmp").resolve()
    if cwd == tmp or tmp in cwd.parents:
        raise OSError("禁止在 /tmp 下保存响应，请切换到项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 无参数或非法 JSON 由公共调用器输出 CLI 错误。
    if not params:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(params[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv=argv)

    previous_root = call_api._SESSION_CACHE.get("_root")
    try:
        try:
            call_api._SESSION_CACHE["_root"] = _prepare_output_root()
            _, session_dir = call_api._ensure_session(time.time())
            data_dir = os.path.join(session_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            # 在发起付费请求前检查最终数据目录，而非只检查根目录。
            with tempfile.TemporaryFile(dir=data_dir):
                pass
        except OSError as exc:
            print(f"当前目录无法保存响应：{exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        return call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
