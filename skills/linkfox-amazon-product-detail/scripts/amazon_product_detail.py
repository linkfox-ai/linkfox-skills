#!/usr/bin/env python3
"""亚马逊商品详情查询：使用公共缓存、输出与认证，固定在当前目录保存数据。

用法：python amazon_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
"""

import json
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/amazon/product/detail"
SLUG = "linkfox-amazon-product-detail"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv == ["--help"] or argv == ["-h"]:
        print("用法：amazon_product_detail.py '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stdout if argv else sys.stderr)
        return 0 if argv else 1

    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    try:
        if len(positional) != 1:
            raise ValueError("需要一个 JSON 参数对象")
        params = json.loads(positional[0])
        if not isinstance(params, dict):
            raise ValueError("JSON 参数必须是对象")
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"参数格式无效：{exc}", file=sys.stderr)
        return 1

    try:
        cwd = Path.cwd().resolve()
        if sys.platform != "win32" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
            raise OSError("禁止在 /tmp 保存响应，请切换到项目目录")
        root = cwd / "linkfox"
        root.mkdir(parents=True, exist_ok=True)
        # 显式指定 dir；仅在当前目录内探测，不使用系统临时目录。
        with tempfile.TemporaryFile(dir=root):
            pass
        call_api._SESSION_CACHE["_root"] = str(root.resolve())
        # 根目录可写不代表日期、会话与 data 目录可写；在收费请求前完成检查。
        _, session_dir = call_api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        call_api.run(API_PATH, SLUG, argv)
    except OSError as exc:
        print(f"无法在当前目录保存响应：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
