#!/usr/bin/env python3
"""FastMoss TikTok 热销商品排行。

用法：
  python fastmoss_product_rank_top_selling.py '<JSON 参数>' [--inline] [--no-cache]

通过公共调用器提供单层 24 小时缓存、完整落盘和 8 KB 摘要输出。
在请求前检查当前工作目录可写，禁止写入 /tmp，不回退到其他位置。
"""

import os
import sys
import tempfile

import call_api


API_PATH = "/fastmoss/productRankTopSelling"
SLUG = "linkfox-fastmoss-product-rank-top-selling"


def _prepare_output_root():
    """将公共调用器的会话输出固定到可写的当前工作目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    if os.name == "posix":
        # 解析符号链接，兼容 /tmp 在部分系统上指向 /private/tmp 的情况。
        tmp_root = os.path.realpath("/tmp")
        real_root = os.path.realpath(root)
        if os.path.commonpath((tmp_root, real_root)) == tmp_root:
            raise OSError("禁止写入 /tmp，请切换到项目目录后重试")
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = root


def main():
    try:
        _prepare_output_root()
    except OSError as exc:
        print(f"当前工作目录不能保存响应：{exc}", file=sys.stderr)
        sys.exit(1)
    # 由 run 提供单层缓存。
    call_api.run(API_PATH, SLUG)


if __name__ == "__main__":
    main()
