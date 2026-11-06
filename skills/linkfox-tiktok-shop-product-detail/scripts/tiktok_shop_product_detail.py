#!/usr/bin/env python3
"""TikTok Shop 商品详情 CLI；复用公共调用、24 小时缓存与响应输出。

用法：python tiktok_shop_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终保存在当前工作目录；不回退其他目录。
"""

import json
import os
from pathlib import Path
import secrets
import sys
import time

import call_api


API_PATH = "/tiktok/shop/product/detail"
SLUG = "linkfox-tiktok-shop-product-detail"


def _prepare_output():
    """在请求前验证当前工作目录可写，并约束公共调用器的输出根目录。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("禁止在 /tmp 下保存商品详情，请切换到可写的项目目录")
    sid = (os.environ.get("SESSION_ID") or "").strip()
    if sid and (sid in (".", "..") or any(c in sid for c in ("/", "\\", ":"))):
        raise ValueError("SESSION_ID 必须是单个目录名，不能包含路径分隔符或盘符")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    if root.resolve() != cwd / "linkfox":
        raise OSError("linkfox 输出目录不能通过符号链接指向其他目录")
    call_api._SESSION_CACHE["_root"] = str(root)
    ts = time.time()
    # 先检查待用路径，再让公共调用器创建会话、索引和元数据。
    # 已有日期或会话目录可能是符号链接 / Windows junction。
    session_dir = root / time.strftime("%Y-%m-%d", time.localtime(ts)) / call_api._session_id(ts)
    data_dir = session_dir / "data"
    if root not in data_dir.resolve().parents:
        raise OSError("会话输出路径超出当前工作目录的 linkfox 目录")
    call_api._ensure_session(ts)
    data_dir.mkdir(parents=True, exist_ok=True)
    # 与真实响应文件名等长，也能在请求前发现 Windows 路径长度限制。
    probe = data_dir / (SLUG + "-" + secrets.token_hex(8) + ".json")
    created = False
    try:
        with probe.open("x", encoding="utf-8") as handle:
            created = True
            handle.write("")
    finally:
        if created:
            probe.unlink()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--help"] or argv == ["-h"]:
        print("用法：tiktok_shop_product_detail.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认复用 24 小时本地缓存；--inline 全量输出；--no-cache 跳过缓存读写。")
        return 0
    params_argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if len(params_argv) != 1:
        print("用法：tiktok_shop_product_detail.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        return 1
    try:
        if not isinstance(json.loads(params_argv[0]), dict):
            raise ValueError("JSON 参数必须为对象")
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"参数格式错误：{exc}", file=sys.stderr)
        return 1
    previous_root = call_api._SESSION_CACHE.get("_root")
    try:
        _prepare_output()
        # 仅由公共调用器维护 24 小时本地缓存，按参数缓存键读写响应文件。
        call_api.run(API_PATH, SLUG, argv=argv)
    except (OSError, ValueError) as exc:
        print(f"商品详情执行失败：{exc}", file=sys.stderr)
        return 1
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
