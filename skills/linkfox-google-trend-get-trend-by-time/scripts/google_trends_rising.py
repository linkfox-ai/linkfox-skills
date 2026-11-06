#!/usr/bin/env python3
"""Google Trends 时下流行查询：使用公共调用、缓存及输出流程。

用法：python google_trends_rising.py '<JSON 参数>' [--inline] [--no-cache]
"""

import json
import os
from pathlib import Path
import sys
import tempfile

import call_api

API_PATH = "/googleTrend/getTrendByTime"
SLUG = "linkfox-google-trend-get-trend-by-time"


def _prepare_output_root():
    """仅在当前目录落盘，写入失败时在请求前停止。"""
    root = Path.cwd().resolve() / "linkfox"
    if os.name != "nt" and Path("/tmp") in root.parents:
        raise OSError("禁止将响应写入 /tmp，请切换到可写的项目目录")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # 参数格式错误交给公共 CLI 处理，不在错误输入下创建输出目录。
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional:
        return call_api.run(API_PATH, SLUG, argv)
    try:
        json.loads(positional[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv)
    try:
        root = _prepare_output_root()
    except OSError as exc:
        print(f"当前目录不可写：{exc}", file=sys.stderr)
        raise SystemExit(1)
    previous_root = call_api._SESSION_CACHE.get("_root")
    call_api._SESSION_CACHE["_root"] = root
    try:
        # 缓存由公共调用器管理，使用统一的键算法和路径，无第二层缓存。
        return call_api.run(API_PATH, SLUG, argv)
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
