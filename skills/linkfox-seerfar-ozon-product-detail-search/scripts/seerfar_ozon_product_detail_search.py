#!/usr/bin/env python3
"""Seerfar Ozon 商品详情查询。

用法：python seerfar_ozon_product_detail_search.py '<JSON 参数>' [--inline] [--no-cache]
复用公共调用器的单层 24 小时缓存、认证、会话落盘与输出策略。
"""

from contextlib import contextmanager
import os
from pathlib import Path
import sys
import tempfile

import call_api


API_PATH = "/seerfar/ozon/productDetailSearch"
SLUG = "linkfox-seerfar-ozon-product-detail-search"


@contextmanager
def _working_directory():
    """Windows 使用扩展路径，避免深层项目中的缓存和响应文件保存失败。"""
    original = os.getcwd()
    changed = os.name == "nt" and not original.startswith("\\\\?\\")
    if changed:
        extended = ("\\\\?\\UNC\\" + original[2:] if original.startswith("\\\\")
                    else "\\\\?\\" + original)
        os.chdir(extended)
    try:
        yield
    finally:
        if changed:
            os.chdir(original)


def _prepare_output_root():
    """仅在当前目录落盘，不回退至其他目录。"""
    root = Path.cwd().resolve() / "linkfox"
    # 从已解析路径的根构造 /tmp，兼容 Windows 扩展路径和 UNC 根。
    tmp_root = Path(root.anchor) / "tmp"
    if tmp_root in (root, *root.parents):
        raise OSError("禁止在 /tmp 下保存响应，请切换到可写的项目目录")
    root.mkdir(parents=True, exist_ok=True)
    # 使用唯一探针，避免多个进程互相删除固定文件名的探针。
    with tempfile.TemporaryFile(dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = os.fspath(root)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    with _working_directory():
        # 无参数及 JSON 解析错误沿用公共 CLI 的提示和退出行为。
        if args and not all(arg in ("--inline", "--no-cache") for arg in args):
            try:
                _prepare_output_root()
            except OSError as exc:
                print(f"当前目录无法保存响应：{exc}", file=sys.stderr)
                raise SystemExit(1)
        call_api.run(API_PATH, SLUG, args)


if __name__ == "__main__":
    main()
