#!/usr/bin/env python3
"""查询 TikTok 商品关联视频，复用公共调用、24 小时缓存和输出逻辑。

用法：python echotik_list_product_video.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终保存；不超过 8000 字节时全量输出，否则展示摘要。
"""

import os
import sys
import tempfile
import time

import call_api


API_PATH = "/echotik/listProductVideo"
SLUG = "linkfox-echotik-product-video"


def _prepare_output_root():
    """请求前检查实际会话数据目录，不回退到家目录或临时目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    # 只固定落盘根目录；响应缓存的键和路径由公共调用器管理。
    call_api._SESSION_CACHE["_root"] = root
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--help" in args or "-h" in args:
        print("用法：echotik_list_product_video.py '<JSON 参数>' [--inline] [--no-cache]")
        return
    try:
        _prepare_output_root()
    except OSError as exc:
        print(f"当前工作目录无法保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    call_api.run(API_PATH, SLUG, argv=args)


if __name__ == "__main__":
    main()
