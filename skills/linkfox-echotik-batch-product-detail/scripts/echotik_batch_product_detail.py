#!/usr/bin/env python3
"""批量查询 TikTok 商品详情，复用公共调用器的认证、缓存和输出。

用法：echotik_batch_product_detail.py '<JSON 参数>' [--inline] [--no-cache]
"""

import os
import sys
import time
from pathlib import Path

import call_api

API_PATH = "/echotik/batchProductDetail"
SLUG = "linkfox-echotik-batch-product-detail"


def main(argv=None):
    """执行 CLI 查询，使用单层 24 小时缓存并向当前目录落盘。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    # 公共调用器可回退到家目录或临时目录；本技能仅向当前目录落盘。
    root = Path.cwd() / "linkfox"
    previous_root = call_api._SESSION_CACHE.get("_root")
    try:
        if Path("/tmp").resolve() in root.resolve().parents:
            raise OSError("本技能禁止将响应保存到 /tmp，请切换工作目录")
        root.mkdir(parents=True, exist_ok=True)
        call_api._SESSION_CACHE["_root"] = str(root)
        # 根目录可写不代表会话目录可写；先验证实际输出目录，避免请求后才失败。
        _, session_dir = call_api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / (".write_probe_" + os.urandom(6).hex())
        with probe.open("x", encoding="utf-8"):
            pass
        probe.unlink()
        # 缓存键、路径和有效期由公共调用器管理，仅使用一层缓存。
        call_api.run(API_PATH, SLUG, argv=argv)
    except OSError as exc:
        print(f"当前工作目录不可用于保存响应：{exc}", file=sys.stderr)
        return 1
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root
    return 0


if __name__ == "__main__":
    sys.exit(main())
