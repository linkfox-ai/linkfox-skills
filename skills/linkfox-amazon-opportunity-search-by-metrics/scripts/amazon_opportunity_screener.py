#!/usr/bin/env python3
"""亚马逊商业指标反向选品：命令行调用、缓存和当前目录落盘。

用法：python amazon_opportunity_screener.py '<JSON 参数>' [--inline] [--no-cache]
使用公共调用器的一层 24 小时缓存，缓存路径和键由 _cache_path 定义。
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import call_api as api


API_PATH = "/amazon/opportunity/searchByMetrics"
SLUG = "linkfox-amazon-opportunity-search-by-metrics"


def _filesystem_path(path):
    """Windows 使用扩展长度路径，同一目录下的缓存和响应不受 MAX_PATH 影响。"""
    value = str(path)
    if os.name == "nt" and not value.startswith("\\\\?\\"):
        value = ("\\\\?\\UNC\\" + value[2:] if value.startswith("\\\\")
                 else "\\\\?\\" + value)
    return Path(value)


def _cache_path(root, slug, params):
    """为公共调用器提供文件路径，使用其缓存键和单层缓存。"""
    directory = root / ".cache" / slug
    directory.mkdir(parents=True, exist_ok=True)
    return str(directory / f"{slug}-{api._cache_key(params)}.json")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional:
        print("用法：amazon_opportunity_screener.py '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式无效：{exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        raise SystemExit(1)

    # 当前目录不可写即报错，禁止使用公共调用器的目录回退。
    cwd = Path.cwd().resolve()
    # Windows 上 /tmp 不带盘符，须先解析为当前盘符下的绝对路径再比较。
    tmp_root = Path("/tmp").resolve()
    if cwd == tmp_root or tmp_root in cwd.parents:
        raise OSError("本技能禁止在 /tmp 中保存响应，请切换到可写的项目目录")
    root = _filesystem_path(cwd / "linkfox")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    previous_cache_path = api._cache_path
    api._SESSION_CACHE["_root"] = str(root)
    api._cache_path = lambda slug, params: _cache_path(root, slug, params)
    # 连续执行即使处于同一秒，也分别保存完整响应。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        # 使用公共调用器的单层缓存，路径和键由上述适配器提供，TTL 为 24 小时。
        api.run(API_PATH, SLUG, argv=argv)
    finally:
        api._resolve_output_path = previous_output_path
        api._cache_path = previous_cache_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
