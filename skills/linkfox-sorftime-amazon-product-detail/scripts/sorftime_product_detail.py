#!/usr/bin/env python3
"""Sorftime 亚马逊商品详情与趋势查询。

用法：python sorftime_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
公共调用器提供 24 小时缓存、会话落盘和摘要输出；不叠加第二层缓存。
"""

import os
import sys
import tempfile

import call_api


API_PATH = "/sorftime/amazon/productDetail"
SLUG = "linkfox-sorftime-amazon-product-detail"


def _prepare_output_root():
    """响应保存在当前目录，请求前确认可写，不回退到临时目录。"""
    cwd = os.path.realpath(os.getcwd())
    if os.name != "nt" and (cwd == "/tmp" or cwd.startswith("/tmp/")):
        raise OSError("禁止在 /tmp 下保存本技能响应，请切换到项目工作目录")
    root = os.path.join(cwd, "linkfox")
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    # 只固定公共调用器的输出根目录，不改变其认证、HTTP 或缓存实现。
    call_api._SESSION_CACHE["_root"] = root


def main():
    try:
        _prepare_output_root()
    except OSError as exc:
        print(f"当前目录不可用于保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    call_api.run(API_PATH, SLUG)


if __name__ == "__main__":
    main()
