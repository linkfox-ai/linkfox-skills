#!/usr/bin/env python3
"""EchoTik TikTok 视频搜索。

用法：python echotik_list_video.py '<JSON 参数>' [--inline] [--no-cache]
使用公共调用器提供 24 小时缓存、完整响应落盘和大小响应输出策略。
"""

import os
import sys
import tempfile
import time
import call_api

API_PATH = "/echotik/listVideo"
SLUG = "linkfox-echotik-list-video"


def main(argv=None):
    # 数据落在当前目录，不允许公共调用器回退到其他目录。
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    try:
        os.makedirs(root, exist_ok=True)
        # 使用独占临时文件探测写权限，避免覆盖同名的既有文件。
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"当前工作目录不可写：{exc}", file=sys.stderr)
        raise SystemExit(1)
    previous_root = call_api._SESSION_CACHE.get("_root")
    previous_output_path = call_api._resolve_output_path
    call_api._SESSION_CACHE["_root"] = root
    # 使用微秒级文件名，避免连续响应互相覆盖。
    call_api._resolve_output_path = lambda slug, _ts: call_api.resolve_data_path(slug, time.time())
    try:
        # 缓存由公共调用器 run 统一管理。
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._resolve_output_path = previous_output_path
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
