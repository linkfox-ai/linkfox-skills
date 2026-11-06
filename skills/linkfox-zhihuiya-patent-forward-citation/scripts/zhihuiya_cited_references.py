#!/usr/bin/env python3
"""智慧芽专利引用查询；支持 JSON 参数、--inline、--no-cache 命令行。

公共调用器提供 24 小时缓存、认证、摘要与会话落盘。
业务入口负责当前目录检查，不另建缓存或 HTTP transport。
"""

import os
from pathlib import Path
import sys
import tempfile
import time
from urllib.error import HTTPError

import call_api


API_PATH = "/zhihuiya/patentForwardCitation"
SLUG = "linkfox-zhihuiya-patent-forward-citation"


def _call_preserving_http_status(original_call, api_path, params):
    """复用公共传输，保留其 JSON 错误分支会丢失的 HTTP 状态。"""
    original_open = call_api.urlopen
    http_status = None

    def capture_status(*args, **kwargs):
        nonlocal http_status
        try:
            return original_open(*args, **kwargs)
        except HTTPError as exc:
            http_status = exc.code
            raise

    call_api.urlopen = capture_status
    try:
        result = original_call(api_path, params)
    finally:
        call_api.urlopen = original_open
    if http_status is not None:
        if not isinstance(result, dict):
            result = {"_response": result}
        result["_http_status"] = http_status
    return result


def _current_root():
    """请求前确认当前工作目录可保存数据，禁止回退到其他目录。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("本技能禁止将会话数据写入 /tmp，请更换工作目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def main(argv=None):
    try:
        root = _current_root()
    except OSError as exc:
        print(f"当前目录无法保存会话数据：{exc}", file=sys.stderr)
        raise SystemExit(1)

    # 使用公共调用器的进程内路径缓存固定本次调用的目录。
    # 这是输出目录选择，响应缓存仍由 call_api.run 单独管理。
    previous = call_api._SESSION_CACHE.get("_root")
    call_api._SESSION_CACHE["_root"] = root
    original_call = call_api.call_api
    try:
        # 根目录可写不代表已有会话的 data 目录可写；先检查真正落盘位置，
        # 避免请求已计费后才发现目录被文件占用或没有写权限。
        try:
            _, session_dir = call_api._ensure_session(time.time())
            data_dir = Path(session_dir) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
        except OSError as exc:
            print(f"当前会话目录无法保存数据：{exc}", file=sys.stderr)
            raise SystemExit(1)
        call_api.call_api = lambda api_path, params: _call_preserving_http_status(
            original_call, api_path, params
        )
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api.call_api = original_call
        if previous is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous


if __name__ == "__main__":
    main()
