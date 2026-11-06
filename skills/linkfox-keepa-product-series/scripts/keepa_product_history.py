#!/usr/bin/env python3
"""Keepa 商品历史查询：JSON 参数透传、24 小时缓存和当前目录输出。"""

import json
import sys
import tempfile
import time
from pathlib import Path

import call_api


API_PATH = "/keepa/productSeries"
SLUG = "linkfox-keepa-product-series"


def _cwd_linkfox_root():
    """业务输出仅写当前目录；失败时不使用公共调用器的回退位置。"""
    cwd = Path.cwd().resolve()
    if cwd.as_posix() == "/tmp" or cwd.as_posix().startswith("/tmp/"):
        raise PermissionError("禁止将本技能数据写入 /tmp，请切换工作目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


def _prepare_output():
    """先检查实际数据目录可写，再发起可能收费的请求。"""
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    # 探针覆盖实际输出文件名长度，Windows 长路径不可用时也应在请求前停止。
    with tempfile.TemporaryFile(
        dir=data_dir, prefix=f"{SLUG}-{int(time.time()) * 1_000_000}-",
        suffix=".json", mode="w", encoding="utf-8",
    ) as probe:
        probe.write("目录写入检查")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法: keepa_product_history.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认使用 24 小时缓存；--inline 完整打印；--no-cache 绕过缓存读写。")
        return 0

    # 参数校验留给公共入口；无参数或 JSON 非法时不创建输出目录。
    params_argv = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not params_argv:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(params_argv[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv=argv)

    # 业务封装限定输出根目录；缓存、认证、HTTP 和输出由公共入口完成。
    original_root = call_api._linkfox_root
    call_api._linkfox_root = _cwd_linkfox_root
    try:
        _prepare_output()
        return call_api.run(API_PATH, SLUG, argv=argv)
    except OSError as exc:
        print(f"当前工作目录无法保存响应: {exc}", file=sys.stderr)
        return 1
    finally:
        call_api._linkfox_root = original_root


if __name__ == "__main__":
    sys.exit(main())
