#!/usr/bin/env python3
"""EchoTik TikTok 视频排行，复用公共调用器的传输、缓存和输出。

用法：
  python echotik_list_video_rank.py '<JSON 参数>' [--inline] [--no-cache]

使用参数缓存键、24 小时有效期和会话文件；当前目录不可写时在请求前报错。
"""

import os
import secrets
import sys

import call_api


API_PATH = "/echotik/listVideoRank"
SLUG = "linkfox-echotik-list-video-rank"


def _prepare_output_root():
    """将完整响应保存到当前目录，阻止公共调用器回退其他目录。"""
    cwd = os.getcwd()
    if cwd == "/tmp" or cwd.startswith("/tmp/"):
        raise OSError("原始数据禁止写入 /tmp，请切换到项目工作目录后重试")
    root = os.path.abspath(os.path.join(cwd, "linkfox"))
    ts = call_api.time.time()
    date = call_api.time.strftime("%Y-%m-%d", call_api.time.localtime(ts))
    data_dir = os.path.join(root, date, call_api._session_id(ts), "data")
    os.makedirs(data_dir, exist_ok=True)
    # 与真实响应文件同长度的文件名，同时检查 Windows 完整路径长度。
    probe_path = os.path.join(data_dir, f"{SLUG}-{secrets.token_hex(8)}.json")
    probe = open(probe_path, "x", encoding="utf-8")
    try:
        probe.write("linkfox-output-check")
        probe.flush()
    finally:
        # Windows 需先关闭文件句柄才能删除。
        probe.close()
        os.remove(probe_path)
    call_api._SESSION_CACHE["_root"] = root


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        _prepare_output_root()
    except OSError as exc:
        print(f"当前工作目录无法保存 LinkFox 数据：{exc}", file=sys.stderr)
        return 1
    call_api.run(API_PATH, SLUG, argv=argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
