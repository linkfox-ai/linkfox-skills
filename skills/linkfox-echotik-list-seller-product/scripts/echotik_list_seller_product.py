#!/usr/bin/env python3
"""EchoTik TikTok 店铺商品列表；完整响应保存到当前目录，使用单层缓存。

用法：python echotik_list_seller_product.py '<JSON 参数>' [--inline] [--no-cache]
传输、24 小时缓存、会话元数据及大小响应输出均复用公共调用器。
"""

import os
from pathlib import Path
import sys
import tempfile

import call_api


API_PATH = "/echotik/listSellerProduct"
SLUG = "linkfox-echotik-list-seller-product"


def _cwd_linkfox_root():
    """检查当前目录可写，禁止公共调用器回退到其他目录。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("禁止将本技能数据写入 /tmp，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(mode="w", encoding="utf-8", dir=root) as probe:
        probe.write("")
    return str(root)


def main():
    try:
        # 请求前检查；缓存目录也由公共调用器限定在当前目录。
        _cwd_linkfox_root()
    except OSError as exc:
        print(f"当前目录无法保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    original_root = call_api._linkfox_root
    try:
        call_api._linkfox_root = _cwd_linkfox_root
        call_api.run(API_PATH, SLUG)
    finally:
        call_api._linkfox_root = original_root


if __name__ == "__main__":
    main()
