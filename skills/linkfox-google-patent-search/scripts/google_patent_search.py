#!/usr/bin/env python3
"""Google Patents 检索入口，使用公共调用器管理的单层 24 小时缓存。

用法：python google_patent_search.py '<JSON 参数>' [--inline] [--no-cache]
完整响应落盘，小响应全量打印，大响应输出摘要；业务入口不回退输出目录。
"""

import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/googlePatent/search"
SLUG = "linkfox-google-patent-search"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    # run 负责全部缓存、传输、响应落盘和摘要；这里只预检输出目录。
    # 无参数及 JSON 格式错误由 run 输出 CLI 提示。
    argv = sys.argv[1:]
    params = [value for value in argv if value not in ("--inline", "--no-cache")]
    if params:
        cwd = Path.cwd().resolve()
        if cwd == Path("/tmp").resolve() or Path("/tmp").resolve() in cwd.parents:
            print("当前目录位于 /tmp，请切换到可写的项目目录。", file=sys.stderr)
            raise SystemExit(1)
        root = cwd / "linkfox"
        try:
            root.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=root):
                pass
            call_api._SESSION_CACHE["_root"] = os.fspath(root)
            # 根目录可写并不代表已有会话的 data 目录和元数据可写。
            # 在请求前检查实际保存位置，复用公共调用器的会话标识与路径。
            _, session_dir = call_api._ensure_session(time.time())
            data_dir = Path(session_dir) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
            with (Path(session_dir) / "_meta.json").open("r+", encoding="utf-8"):
                pass
        except OSError as exc:
            print(f"当前目录不可写，无法保存响应：{exc}", file=sys.stderr)
            raise SystemExit(1)

    call_api.run(API_PATH, SLUG, argv=argv)


if __name__ == "__main__":
    main()
