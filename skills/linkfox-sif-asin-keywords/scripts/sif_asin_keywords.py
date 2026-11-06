#!/usr/bin/env python3
"""SIF ASIN 流量关键词查询。

用法：python sif_asin_keywords.py '<JSON 参数>' [--inline] [--no-cache]
复用公共调用器的请求、24 小时缓存、会话落盘和输出策略。
"""

import os
from pathlib import Path
import sys
import tempfile

import call_api


API_PATH = "/sif/asinKeywords"
SLUG = "linkfox-sif-asin-keywords"


def _prepare_output_root():
    """仅写当前工作目录，不回退到其他目录。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("禁止将会话数据写入 /tmp，请使用可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print(__doc__)
        return
    if argv:
        try:
            _prepare_output_root()
        except OSError as exc:
            print(f"当前工作目录不可用于保存响应：{exc}", file=sys.stderr)
            raise SystemExit(1)
    call_api.run(API_PATH, SLUG, argv)


if __name__ == "__main__":
    main()
