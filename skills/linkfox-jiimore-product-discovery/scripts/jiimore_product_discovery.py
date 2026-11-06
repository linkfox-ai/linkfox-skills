#!/usr/bin/env python3
"""极目商品发掘：复用公共调用器的认证、缓存、会话记录和输出。

用法：python jiimore_product_discovery.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；8 KB 以内完整输出，大响应显示摘要。
"""

import os
from pathlib import Path
import sys
import tempfile

import call_api


API_PATH = "/jiimore/productDiscovery"
SLUG = "linkfox-jiimore-product-discovery"


def _prepare_output_root():
    """业务结果必须留在当前工作目录，不采用公共调用器的目录回退。"""
    cwd = Path.cwd().resolve()
    if cwd.as_posix() == "/tmp" or cwd.as_posix().startswith("/tmp/"):
        raise OSError("业务结果禁止写入 /tmp，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 请求前验证实际写权限；唯一探测文件关闭后自动删除。
    with tempfile.TemporaryFile(dir=root):
        pass
    return os.fspath(root)


def main():
    argv = sys.argv[1:]
    # 无参数或无效 JSON 交由公共调用器输出 CLI 报错，不提前建目录。
    data_args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not data_args:
        return call_api.run(API_PATH, SLUG, argv=argv)
    import json
    try:
        json.loads(data_args[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        root = _prepare_output_root()
    except OSError as exc:
        print(f"无法在当前目录保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    previous = call_api._SESSION_CACHE.get("_root")
    call_api._SESSION_CACHE["_root"] = root
    try:
        # 根目录可写不代表现有会话目录可写；在收费请求前检查实际落盘位置。
        try:
            _, session_dir = call_api._ensure_session(call_api.time.time())
            data_dir = Path(session_dir) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
        except OSError as exc:
            print(f"无法在当前会话目录保存响应：{exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        # 仅使用公共调用器的一层缓存，按参数键、固定路径和 24 小时 TTL 复用。
        return call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        if previous is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous


if __name__ == "__main__":
    main()
