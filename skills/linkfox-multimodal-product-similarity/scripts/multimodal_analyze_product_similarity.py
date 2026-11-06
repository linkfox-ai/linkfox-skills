#!/usr/bin/env python3
"""商品主图相似度分析：提供 CLI、缓存和会话输出。

用法：python multimodal_analyze_product_similarity.py '<JSON 参数>' [--inline] [--no-cache]
--inline 强制全量输出；--no-cache 禁用默认 24 小时缓存。
请求、缓存、UTF-8 响应保存和摘要统一交给公共调用器。
"""

import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/multimodal/analyzeProductSimilarity"
SLUG = "linkfox-multimodal-product-similarity"


def _prepare_output_root():
    """请求前检查实际会话落盘位置，避免收费后才发现目录不可写。"""
    cwd = Path.cwd().resolve()
    if os.name == "posix" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("禁止在 /tmp 中保存响应，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(mode="w", encoding="utf-8", dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(mode="w", encoding="utf-8", dir=data_dir):
        pass
    # 公共调用器保存响应时会更新现有元数据，也须在请求前确认可写。
    with open(Path(session_dir) / "_meta.json", "r+", encoding="utf-8"):
        pass


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--help" in args or "-h" in args:
        print("用法：python multimodal_analyze_product_similarity.py '<JSON 参数>' [--inline] [--no-cache]")
        print("--inline 强制全量输出；--no-cache 禁用 24 小时响应缓存。")
        return 0
    if args:
        try:
            _prepare_output_root()
        except OSError as exc:
            print(f"当前目录无法保存响应：{exc}", file=sys.stderr)
            return 1
    # 公共调用器按 slug 和参数哈希管理缓存，使用单层缓存。
    call_api.run(API_PATH, SLUG, argv=args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
