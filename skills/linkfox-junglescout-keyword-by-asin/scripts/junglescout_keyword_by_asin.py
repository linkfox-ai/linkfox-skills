#!/usr/bin/env python3
"""Jungle Scout ASIN 关键词反查入口；使用公共调用器的一层缓存和输出策略。"""

import json
import os
import sys
import tempfile
from pathlib import Path

import call_api as api_client


API_PATH = "/tool-jungle-scout/keywords/by-asin"
SLUG = "linkfox-junglescout-keyword-by-asin"


def _prepare_output():
    """请求前确认当前目录可写，固定落盘根目录，禁止回退到其他目录。"""
    cwd = Path.cwd().resolve()
    # 公共调用器会接受任何 cwd；本技能明确禁止在临时目录落盘。
    # 在创建会话目录或发起收费请求之前检查，亦覆盖指向临时目录的链接。
    temp_roots = (Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve())
    if any(cwd == path or path in cwd.parents for path in temp_roots):
        raise OSError("工作目录位于临时目录，请切换到可持久保存数据的项目目录")
    root = str(cwd / "linkfox")
    api_client._SESSION_CACHE["_root"] = root
    _, session_dir = api_client._ensure_session(api_client.time.time())
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=data_dir, prefix=".write_probe-", delete=True):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--help" in argv or "-h" in argv:
        print("用法: junglescout_keyword_by_asin.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认使用 24 小时缓存；--no-cache 禁止缓存读写；--inline 完整打印并保存。")
        return 0
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 由公共入口处理无参数或无效 JSON，输出 CLI 错误与退出状态。
    if not positional:
        return api_client.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(positional[0])
    except json.JSONDecodeError:
        return api_client.run(API_PATH, SLUG, argv=argv)
    try:
        _prepare_output()
    except OSError as exc:
        print(f"当前工作目录不可用于保存数据，未请求接口: {exc}", file=sys.stderr)
        return 1
    # 缓存由公共入口统一处理，仅使用一层缓存。
    return api_client.run(API_PATH, SLUG, argv=argv)


if __name__ == "__main__":
    sys.exit(main())
