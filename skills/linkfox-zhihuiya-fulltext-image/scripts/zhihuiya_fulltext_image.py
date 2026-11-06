#!/usr/bin/env python3
"""智慧芽专利全文附图查询。

用法：python zhihuiya_fulltext_image.py '<JSON 参数>' [--inline] [--no-cache]
公共调用器按请求参数生成缓存键，在工作目录下缓存响应，有效期为 24 小时，不另设业务缓存。
完整响应保存在当前工作目录；--inline 强制全量输出。
"""

import json
import os
from pathlib import Path
import sys
import time

import call_api


API_PATH = "/zhihuiya/fulltextImage"
SLUG = "linkfox-zhihuiya-fulltext-image"


def _prepare_output():
    """在当前工作目录保存响应，不回退到家目录或临时目录。"""
    cwd = Path.cwd().resolve()
    tmp = Path("/tmp").resolve()
    if cwd == tmp or tmp in cwd.parents:
        raise OSError("本技能禁止在 /tmp 下保存响应，请切换到任务工作目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 固定公共调用器本次输出根目录，避免其 ACPX/家目录/临时目录回退。
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    probe = data_dir / (".write_probe-" + os.urandom(6).hex())
    try:
        with probe.open("x", encoding="utf-8"):
            pass
    finally:
        if probe.exists():
            probe.unlink()


def _resolve_unique_output_path(slug, _ts):
    """避免公共调用器按秒取整导致同一会话的完整响应相互覆盖。"""
    timestamp_us = time.time_ns() // 1000
    while True:
        path = call_api.resolve_data_path(slug, timestamp_us / 1_000_000)
        try:
            with open(path, "x", encoding="utf-8"):
                pass
            return path
        except FileExistsError:
            timestamp_us += 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法：zhihuiya_fulltext_image.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认复用 24 小时本地缓存；--no-cache 禁用缓存；--inline 全量输出。")
        return 0
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional:
        print("用法：zhihuiya_fulltext_image.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        return 1
    try:
        json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式无效：{exc}", file=sys.stderr)
        return 1
    try:
        _prepare_output()
    except OSError as exc:
        print(f"当前工作目录不可用于保存响应：{exc}", file=sys.stderr)
        return 1
    # 使用公共调用器提供的唯一一层缓存。
    original_resolver = call_api._resolve_output_path
    try:
        call_api._resolve_output_path = _resolve_unique_output_path
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._resolve_output_path = original_resolver
    return 0


if __name__ == "__main__":
    sys.exit(main())
