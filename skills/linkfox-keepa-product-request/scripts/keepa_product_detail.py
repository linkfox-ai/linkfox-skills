#!/usr/bin/env python3
"""Keepa 商品详情：通过公共调用器执行请求、缓存和响应输出。

用法：python keepa_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
默认复用 24 小时本地缓存；--no-cache 同时禁用读取和写入。
"""

import json
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/keepa/productRequest"
SLUG = "linkfox-keepa-product-request"


def _prepare_output():
    """响应保存在 cwd 下，在任何请求前验证目录可写性。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 为本业务绑定 cwd，避免家目录或临时目录兜底。
    call_api._SESSION_CACHE["_root"] = str(root.resolve())
    sid = call_api._session_id(time.time())
    session = root / time.strftime("%Y-%m-%d") / sid
    if not session.resolve().is_relative_to(root.resolve()):
        raise ValueError("SESSION_ID 必须使会话目录保持在当前工作目录的 linkfox 内")
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法：keepa_product_detail.py '<JSON 参数>' [--inline] [--no-cache]")
        return
    params_argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if params_argv:
        try:
            params = json.loads(params_argv[0])
        except json.JSONDecodeError:
            # 使用公共调用器的 JSON 错误提示与退出码。
            return call_api.run(API_PATH, SLUG, argv=argv)
        if not isinstance(params, dict):
            print("JSON 参数必须是对象", file=sys.stderr)
            raise SystemExit(1)
        try:
            _prepare_output()
        except (OSError, ValueError) as exc:
            print(f"当前目录无法保存响应：{exc}", file=sys.stderr)
            raise SystemExit(1)
    # 仅使用公共调用器的一层缓存，其缓存键、目录和 TTL 按接口参考约定。
    call_api.run(API_PATH, SLUG, argv=argv)


if __name__ == "__main__":
    main()
