#!/usr/bin/env python3
"""解析 TikTok 视频下载地址，使用命令行参数、24 小时缓存和会话输出。

用法：python echotik_get_video_download_url.py '<JSON 参数>' [--inline] [--no-cache]
"""

import json
import os
from pathlib import Path
import sys
import tempfile

import call_api

API_PATH = "/echotik/getVideoDownloadUrl"
SLUG = "linkfox-echotik-get-video-download-url"


def _prepare_output_root():
    """业务入口坚持 cwd 落盘，在请求前检查，禁止公共调用器回退目录。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("禁止将响应写入 /tmp，请切换到项目工作目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # 先校验 JSON，再检查落盘目录。
    # 缺少参数或格式错误时由公共调用器报告，不创建目录或遮蔽参数错误。
    params_argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    valid_json = False
    if params_argv:
        try:
            json.loads(params_argv[0])
            valid_json = True
        except json.JSONDecodeError:
            pass
    if valid_json:
        try:
            _prepare_output_root()
        except OSError as exc:
            print(f"当前目录不可写：{exc}", file=sys.stderr)
            raise SystemExit(1)
    # 缓存由公共调用器单独管理，默认 24 小时，不建立业务缓存层。
    call_api.run(API_PATH, SLUG, argv=argv)


if __name__ == "__main__":
    main()
