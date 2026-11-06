#!/usr/bin/env python3
"""亚马逊关键词商业洞察报告入口。

用法：python amazon_opportunity_report.py '<JSON 参数>' [--inline] [--no-cache]
提供 24 小时响应缓存及完整响应落盘，全部请求交由 call_api.run 执行。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/amazon/opportunity/reportByKeyword"
SLUG = "linkfox-amazon-opportunity-report-by-keyword"
USAGE = "python amazon_opportunity_report.py '<JSON 参数>' [--inline] [--no-cache]"


def _unique_output_path(slug, timestamp):
    """以微秒时间戳独占预留文件，避免公共流程的整秒时间戳覆盖已有响应。"""
    stamp = max(int(timestamp * 1_000_000), int(time.time() * 1_000_000))
    while True:
        path = call_api.resolve_data_path(slug, stamp / 1_000_000)
        try:
            with open(path, "x", encoding="utf-8"):
                pass
            return path
        except FileExistsError:
            stamp += 1


def _windows_cache_path(path):
    """保留缓存的物理位置，在 Windows 文件操作中支持超过 MAX_PATH 的缓存路径。"""
    if os.name != "nt":
        return path
    absolute = os.path.abspath(path)
    if absolute.startswith(("\\\\?\\", "\\\\.\\")):
        return absolute
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute[2:]
    return "\\\\?\\" + absolute


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print(USAGE)
        print("--inline 全量打印；--no-cache 禁用默认的 24 小时响应缓存。")
        return

    # 先让公共调用器处理无参数与 JSON 格式错误，避免无效 CLI 创建会话文件。
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(positional[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv=argv)

    # 响应只写当前目录且不可回退；业务封装固定根目录。
    previous_root = call_api._SESSION_CACHE.get("_root")
    previous_output_path = call_api._resolve_output_path
    previous_cache_path = call_api._cache_path
    try:
        root = (Path.cwd() / "linkfox").resolve()
        if os.name != "nt" and (root == Path("/tmp") or Path("/tmp") in root.parents):
            raise OSError("按本技能约定，禁止将响应写入 /tmp")
        call_api._SESSION_CACHE["_root"] = str(root)
        try:
            _, session_dir = call_api._ensure_session(time.time())
            data_dir = Path(session_dir) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
        except OSError as exc:
            print(f"当前工作目录无法保存完整响应：{exc}", file=sys.stderr)
            raise SystemExit(1) from exc

        # 唯一响应缓存沿用公共调用器的相同键、路径和 TTL；透传 --no-cache。
        call_api._resolve_output_path = _unique_output_path
        call_api._cache_path = lambda slug, params: _windows_cache_path(previous_cache_path(slug, params))
        return call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._resolve_output_path = previous_output_path
        call_api._cache_path = previous_cache_path
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
