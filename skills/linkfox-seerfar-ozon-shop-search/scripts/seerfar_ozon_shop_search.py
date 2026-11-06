#!/usr/bin/env python3
"""Seerfar Ozon 店铺商品搜索；复用公共调用器的传输、缓存与输出。

用法：python seerfar_ozon_shop_search.py '<JSON 参数>' [--inline] [--no-cache]
默认使用 24 小时缓存，完整响应保存到当前工作目录。
"""

import json
from pathlib import Path
import secrets
import sys
import time

import call_api


API_PATH = "/seerfar/ozon/shopSearch"
SLUG = "linkfox-seerfar-ozon-shop-search"


def _prepare_output():
    """在请求前验证当前目录可写，覆盖公共调用器的目录回退。"""
    cwd = Path.cwd().resolve()
    if cwd == Path("/tmp") or Path("/tmp") in cwd.parents:
        raise OSError("禁止将响应写入 /tmp，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    # 使用与实际响应文件等长的名称，提前发现 Windows 完整路径过长等问题。
    # 探测文件只在会话数据目录内创建，不使用系统临时目录。
    timestamp_width = len(str(int(time.time()) * 1_000_000))
    token = secrets.token_hex((timestamp_width + 1) // 2)[:timestamp_width]
    probe = data_dir / f"{SLUG}-{token}.json"
    with probe.open("x", encoding="utf-8"):
        pass
    probe.unlink()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--help"] or argv == ["-h"]:
        print("用法：python seerfar_ozon_shop_search.py '<JSON 参数>' [--inline] [--no-cache]")
        return 0
    params_argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 缺参或无效 JSON 仍由公共 CLI 报错，且不提前创建输出目录。
    if not params_argv:
        call_api.run(API_PATH, SLUG, argv)
        return 0
    try:
        json.loads(params_argv[0])
    except json.JSONDecodeError:
        call_api.run(API_PATH, SLUG, argv)
        return 0
    try:
        _prepare_output()
    except OSError as exc:
        print(f"当前工作目录无法保存响应：{exc}", file=sys.stderr)
        return 1
    # 使用公共调用器的一层缓存，不叠加第二层业务缓存。
    call_api.run(API_PATH, SLUG, argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
