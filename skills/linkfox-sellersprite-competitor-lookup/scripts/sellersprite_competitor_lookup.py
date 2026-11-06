#!/usr/bin/env python3
"""卖家精灵竞品查询：支持 JSON CLI、24 小时缓存和会话数据输出。

用法：
  python sellersprite_competitor_lookup.py '<JSON 参数>' [--inline] [--no-cache]

公共调用器统一管理缓存目录、参数键与有效期，不建立第二层缓存。
"""

import json
import os
from pathlib import Path
import sys
import tempfile

import call_api as _runner


API_PATH = "/sellersprite/competitor-lookup"
SLUG = "linkfox-sellersprite-competitor-lookup"


def main():
    argv = sys.argv[1:]
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 无参数和 JSON 语法错误继续使用公共 CLI 的错误处理，不产生目录。
    if not positional:
        return _runner.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(positional[0])
    except json.JSONDecodeError:
        return _runner.run(API_PATH, SLUG, argv=argv)

    # 响应保存在当前目录，不向 /tmp 或家目录回退。
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        print("当前工作目录位于 /tmp，请切换到项目目录后再运行。", file=sys.stderr)
        raise SystemExit(1)
    root = cwd / "linkfox"
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"当前目录无法保存响应，请切换到可写目录：{exc}", file=sys.stderr)
        raise SystemExit(1)

    # 公共调用器不设置 Accept；业务封装设置 JSON 响应协商。
    # 请求仍由 call_api.run 统一发送，不另建 HTTP transport 或缓存。
    original_request = _runner.Request

    def json_request(*args, **kwargs):
        request = original_request(*args, **kwargs)
        request.add_header("Accept", "application/json")
        return request

    previous_root = _runner._SESSION_CACHE.get("_root")
    _runner._SESSION_CACHE["_root"] = str(root)
    _runner.Request = json_request
    try:
        return _runner.run(API_PATH, SLUG, argv=argv)
    finally:
        _runner.Request = original_request
        if previous_root is None:
            _runner._SESSION_CACHE.pop("_root", None)
        else:
            _runner._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
