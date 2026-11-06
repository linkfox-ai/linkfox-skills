#!/usr/bin/env python3
"""店雷达 1688 商品搜索。

用法：python dld_product_search.py '<JSON 参数>' [--inline] [--no-cache]
调用 /dld/productSearch，使用 24 小时缓存并保存完整响应；
由公共调用器统一处理认证、HTTP、缓存和输出，不叠加第二层缓存。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/dld/productSearch"
SLUG = "linkfox-dld-product-search"


def _prepare_output():
    """在请求前检查落盘目录，不使用公共调用器的目录回退。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("禁止在 /tmp 下保存本技能响应，请切换到可写的工作目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 固定本次调用的根目录，同时沿用公共调用器的会话元数据与索引。
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 无参和无效 JSON 的 CLI 提示由公共调用器产生。
    if not params:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(params[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv=argv)

    previous_root = call_api._SESSION_CACHE.get("_root")
    try:
        _prepare_output()
        return call_api.run(API_PATH, SLUG, argv=argv)
    except OSError as exc:
        print(f"无法在当前目录保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
