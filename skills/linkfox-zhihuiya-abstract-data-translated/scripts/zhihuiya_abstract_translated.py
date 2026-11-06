#!/usr/bin/env python3
"""智慧芽专利标题与摘要翻译；使用公共调用器及 24 小时缓存。"""

import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/zhihuiya/abstractDataTranslated"
SLUG = "linkfox-zhihuiya-abstract-data-translated"


def _prepare_output_root():
    """在请求前确认实际会话目录可写，并固定当前目录落盘。"""
    root = (Path.cwd() / "linkfox").resolve()
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
        ts = time.time()
        date_root = root / time.strftime("%Y-%m-%d", time.localtime(ts))
        session_path = (date_root / call_api._session_id(ts)).resolve()
        if session_path == date_root.resolve() or not session_path.is_relative_to(date_root.resolve()):
            raise OSError("SESSION_ID 必须指向当日数据目录内的会话子目录")
        call_api._SESSION_CACHE["_root"] = os.fspath(root)
        _, session_dir = call_api._ensure_session(ts)
        data_dir = Path(session_dir) / "data"
        if not data_dir.resolve().is_relative_to(session_path):
            raise OSError("会话 data 目录必须位于当前会话内")
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
    except OSError as exc:
        print(f"当前目录不可写，无法保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args in (["--help"], ["-h"]):
        print("用法：python zhihuiya_abstract_translated.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认使用 24 小时缓存并保存完整响应；--inline 全量打印，--no-cache 禁用缓存。")
        return
    _prepare_output_root()
    call_api.run(API_PATH, SLUG, argv=args)


if __name__ == "__main__":
    main()
