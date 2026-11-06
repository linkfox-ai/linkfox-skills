#!/usr/bin/env python3
"""1688 商品详情查询。

用法：python alibaba1688_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
通过公共 run 执行 24 小时缓存、会话落盘和大小响应输出策略。
在请求前检查当前目录的数据保存位置，禁止回退到其他目录。
"""

import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/alibaba1688/productDetail"
SLUG = "linkfox-1688-product-detail"


def _prepare_output_root():
    """检查当前目录可写，并固定公共调用器的数据保存位置。"""
    root = (Path.cwd() / "linkfox").resolve()
    temporary_roots = [Path(tempfile.gettempdir()).resolve()]
    if os.name != "nt":
        temporary_roots.append(Path("/tmp").resolve())
    if any(root.is_relative_to(base) for base in temporary_roots):
        raise OSError("禁止将商品详情保存到临时目录，请切换到可写的项目目录")
    root.mkdir(parents=True, exist_ok=True)
    # 公共调用器允许自动回退；仅在本业务入口固定到已检查的当前目录。
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    previous_root = call_api._SESSION_CACHE.get("_root")
    try:
        if any(arg not in ("--inline", "--no-cache") for arg in argv):
            try:
                _prepare_output_root()
            except OSError as exc:
                print(f"无法在当前目录保存完整响应：{exc}", file=sys.stderr)
                raise SystemExit(1)
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
