#!/usr/bin/env python3
"""Jungle Scout 产品数据库查询，支持 JSON 位置参数、缓存和会话输出。

用法：python junglescout_product_database.py '<JSON 参数>' [--inline] [--no-cache]
默认使用 24 小时缓存；缓存键、缓存位置、8 KB 摘要和完整响应落盘
由公共调用器统一实现，业务入口直接使用公共调用器的缓存与 HTTP transport。
"""

import json
import sys
import tempfile
from pathlib import Path

import call_api

API_PATH = "/tool-jungle-scout/product-database/query"
SLUG = "linkfox-junglescout-product-database"


def _probe_directory(path):
    path.mkdir(parents=True, exist_ok=True)
    # 使用唯一文件名，避免覆盖用户已有的 .write_probe。
    with tempfile.NamedTemporaryFile(dir=path, prefix=".write_probe-", mode="w", encoding="utf-8"):
        pass


def _prepare_output():
    """在请求前检查实际会话目录，禁止回退到 cwd 之外。"""
    root = (Path.cwd() / "linkfox").resolve()
    if root.as_posix() == "/tmp/linkfox" or "/tmp/" in root.as_posix():
        raise OSError("响应禁止写入 /tmp，请切换到可写的项目目录。")
    if not root.is_relative_to(Path.cwd().resolve()):
        raise OSError("linkfox 目录必须位于当前工作目录内。")
    ts = int(call_api.time.time())
    date = call_api.time.strftime("%Y-%m-%d", call_api.time.localtime(ts))
    session = (root / date / call_api._session_id(ts)).resolve()
    data = (session / "data").resolve()
    if not session.is_relative_to(root) or not data.is_relative_to(root):
        raise OSError("会话输出目录必须位于当前工作目录的 linkfox 内。")
    _probe_directory(root)
    call_api._SESSION_CACHE["_root"] = str(root)
    # 根目录可写不代表既有会话目录可写；提前检查数据与元数据目录。
    _probe_directory(session)
    _probe_directory(data)
    call_api._ensure_session(ts)
    with open(session / "_meta.json", "r+", encoding="utf-8"):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if params:
        try:
            json.loads(params[0])
        except json.JSONDecodeError:
            pass  # 保留公共调用器的 CLI 错误信息，无效参数不创建输出目录。
        else:
            try:
                _prepare_output()
            except OSError as exc:
                print(f"无法准备当前目录的响应输出：{exc}", file=sys.stderr)
                raise SystemExit(1)
    # 由公共调用器统一处理缓存与请求。
    call_api.run(API_PATH, SLUG, argv)


if __name__ == "__main__":
    main()
