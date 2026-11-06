#!/usr/bin/env python3
"""Jungle Scout 关键词历史搜索量：提供 JSON CLI、缓存和输出流程。

用法：python junglescout_keyword_history.py '<JSON 参数>' [--inline] [--no-cache]
公共调用器负责 24 小时缓存与会话落盘，不叠加业务缓存。
"""

import json
from pathlib import Path
import sys
import tempfile
import time

import call_api

API_PATH = "/tool-jungle-scout/keywords/historical-search-volume"
SLUG = "linkfox-junglescout-keyword-history"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 参数错误仍交给公共调用器处理，不提前创建输出目录。
    if not positional:
        return call_api.run(API_PATH, SLUG, argv)
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv)

    previous_root = call_api._SESSION_CACHE.get("_root")
    try:
        root = (Path.cwd() / "linkfox").resolve()
        if root.is_relative_to(Path("/tmp").resolve()):
            raise OSError("本技能禁止将响应保存到 /tmp")
        # 仅为本次调用固定输出根目录，防止公共调用器回退到其他目录。
        call_api._SESSION_CACHE["_root"] = str(root)
        _, session_dir = call_api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        # 使用与响应文件等长的名字，避免 Windows 长路径在收费请求后才失败。
        with tempfile.TemporaryFile(prefix=f"{SLUG}-00000000", suffix=".json", dir=data_dir):
            pass
        if "--no-cache" not in argv:
            cache_path = call_api._cache_path(SLUG, params)
            if call_api._load_cache(cache_path) is None:
                with tempfile.TemporaryFile(prefix=f"{SLUG}-00000000", suffix=".json", dir=Path(cache_path).parent):
                    pass
    except OSError as exc:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root
        print(f"当前目录无法保存完整响应或缓存：{exc}", file=sys.stderr)
        raise SystemExit(1)

    try:
        return call_api.run(API_PATH, SLUG, argv)
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
