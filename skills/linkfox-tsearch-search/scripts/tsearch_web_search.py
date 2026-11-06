#!/usr/bin/env python3
"""网页搜索与在线信息检索。

用法：python tsearch_web_search.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；不超过 8000 个 UTF-8 字节时全量输出，否则输出摘要。
默认使用 24 小时本地缓存；--inline 强制全量输出，--no-cache 禁用缓存。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api as api

API_PATH = "/tsearch/search"
SLUG = "linkfox-tsearch-search"


def _prepare_output():
    """请求前确认输出可写，只选择已配置工作区或当前目录。"""
    workspace = (os.environ.get("ACPX_WORKSPACES") or "").strip().split(os.pathsep)[0].strip()
    candidates = ([Path(workspace) / "linkfox"] if workspace else []) + [Path.cwd() / "linkfox"]
    last_error = None
    for candidate in candidates:
        root = candidate.resolve()
        # 输出根目录优先选择工作区，其次为当前目录，不回退到用户或临时目录。
        if root.as_posix() == "/tmp" or root.as_posix().startswith("/tmp/"):
            last_error = OSError("完整响应禁止保存到 /tmp")
            continue
        try:
            root.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=root):
                pass
        except OSError as exc:
            last_error = exc
            continue
        api._SESSION_CACHE["_root"] = str(root)
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        # 检查实际响应文件名的长度，避免 Windows 在请求后才报路径过长。
        probe = data_dir / f"{SLUG}-{time.time_ns() // 1000}.json"
        with probe.open("x", encoding="utf-8"):
            pass
        probe.unlink()
        return
    raise OSError(f"工作区和当前目录均无法保存完整响应：{last_error}")


def main():
    argv = sys.argv[1:]
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 无参数或 JSON 无效时，由公共调用器输出 CLI 提示，不创建会话目录。
    if not params:
        return api.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(params[0])
    except json.JSONDecodeError:
        return api.run(API_PATH, SLUG, argv=argv)

    previous_root = api._SESSION_CACHE.get("_root")
    try:
        _prepare_output()
        # 缓存路径、TTL 和 --no-cache 行为统一由公共调用器管理。
        api.run(API_PATH, SLUG, argv=argv)
    except OSError as exc:
        print(f"无法保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
