#!/usr/bin/env python3
"""MPSTATS Ozon 类目商品查询。

用法：
  python mpstats_ozon_category_products.py '<JSON 参数>' [--inline] [--no-cache]

完整响应始终落盘；不超过 8 KB 时全量输出，否则输出摘要。
默认保留 24 小时本地缓存；--no-cache 禁用本次缓存读写。
"""

from pathlib import Path
import sys
import tempfile
import time

import call_api as api


API_PATH = "/mpstats/ozon/categoryProducts"
SLUG = "linkfox-mpstats-ozon-category-products"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not [arg for arg in argv if arg not in ("--inline", "--no-cache")]:
        return api.run(API_PATH, SLUG, argv=argv)

    # 数据保存在当前工作目录；请求前验证可写，禁止自动回退。
    root = Path.cwd() / "linkfox"
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"无法写入当前工作目录 {root}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    api._SESSION_CACHE["_root"] = str(root)
    # 公共调用器使用整秒时间；以高精度时间避免同秒调用覆盖完整响应。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        return api.run(API_PATH, SLUG, argv=argv)
    finally:
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
