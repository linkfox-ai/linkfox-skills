#!/usr/bin/env python3
"""MPSTATS Ozon 商品搜索：JSON CLI、单层缓存及会话输出。

用法：mpstats_ozon_product_search.py '<JSON 参数>' [--inline] [--no-cache]
请求、24 小时缓存和输出由 call_api.py 统一执行。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api as _runner

API_PATH = "/mpstats/ozon/productSearch"
SLUG = "linkfox-mpstats-ozon-product-search"


def _call_with_http_status(call, api_path, params):
    """保留 HTTP 异常状态；正文解析与请求行为仍由公共调用器负责。"""
    previous_open = _runner.urlopen
    status = None

    def open_with_status(*args, **kwargs):
        nonlocal status
        try:
            return previous_open(*args, **kwargs)
        except _runner.HTTPError as exc:
            status = exc.code
            raise

    _runner.urlopen = open_with_status
    try:
        result = call(api_path, params)
    finally:
        _runner.urlopen = previous_open
    if status is not None and isinstance(result, dict):
        result["_http_status"] = status
    return result


def _prepare_output():
    """按文档约定锁定当前目录，请求前检查可写性，不回退其他目录。"""
    root = Path.cwd().resolve() / "linkfox"
    if os.name != "nt" and Path("/tmp") in root.parents:
        raise OSError("当前目录位于 /tmp，请切换到可写项目目录后运行")
    root.mkdir(parents=True, exist_ok=True)
    # 仅在目标目录内探测权限，不使用系统临时目录。
    with tempfile.TemporaryFile(dir=root):
        pass
    _runner._SESSION_CACHE["_root"] = str(root)
    _, session_dir = _runner._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(exist_ok=True)
    # 用实际响应文件的完整名称探测，避免目录可写但长路径等限制导致
    # 请求已收费后才发现无法保存。只删除本次以 x 模式新建的探测文件。
    probe_path = data_dir / f"{SLUG}-{int(time.time() * 1_000_000)}.json"
    with probe_path.open("x", encoding="utf-8"):
        pass
    probe_path.unlink()


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--help" in args or "-h" in args:
        print("用法：mpstats_ozon_product_search.py '<JSON 参数>' [--inline] [--no-cache]")
        return 0
    # 参数错误交给公共 CLI，避免产生无效任务文件。
    values = [a for a in args if a not in ("--inline", "--no-cache")]
    if not values:
        return _runner.run(API_PATH, SLUG, args)
    try:
        json.loads(values[0])
    except json.JSONDecodeError:
        return _runner.run(API_PATH, SLUG, args)
    previous_root = _runner._SESSION_CACHE.get("_root")
    previous_output = _runner._resolve_output_path
    previous_call = _runner.call_api
    try:
        _prepare_output()
        # 使用完整精度时间，防止同秒调用覆盖已保存响应。
        _runner._resolve_output_path = lambda slug, ts: _runner.resolve_data_path(slug, time.time())
        _runner.call_api = lambda path, params: _call_with_http_status(previous_call, path, params)
        return _runner.run(API_PATH, SLUG, args)
    except OSError as exc:
        print(f"无法写入当前目录的会话数据：{exc}", file=sys.stderr)
        return 1
    finally:
        _runner.call_api = previous_call
        _runner._resolve_output_path = previous_output
        if previous_root is None:
            _runner._SESSION_CACHE.pop("_root", None)
        else:
            _runner._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    sys.exit(main())
