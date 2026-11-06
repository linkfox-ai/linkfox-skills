#!/usr/bin/env python3
"""EchoTik TikTok Shop 新品排行。

用法：python echotik_list_new_product_rank.py '<JSON 参数>' [--inline] [--no-cache]
默认复用 24 小时本地缓存；完整响应始终落盘，大响应输出摘要。
"""

import os
from pathlib import Path
import sys
import tempfile

import call_api


API_PATH = "/echotik/listNewProductRank"
SLUG = "linkfox-echotik-list-new-product-rank"


def _prepare_output_root():
    """将响应保存在当前目录，禁止回退到家目录或 /tmp。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("当前工作目录位于 /tmp，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    # 在业务入口预先固定已验证的工作目录。
    call_api._SESSION_CACHE["_root"] = str(root)


def main(argv=None):
    try:
        _prepare_output_root()
    except OSError as exc:
        print(f"当前工作目录无法保存响应：{exc}", file=sys.stderr)
        return 1
    # 使用唯一缓存层，支持 --no-cache / --inline 选项。
    call_api.run(API_PATH, SLUG, argv=argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
