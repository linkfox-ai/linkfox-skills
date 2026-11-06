#!/usr/bin/env python3
"""EchoTik TikTok 店铺搜索。

用法：python echotik_list_seller.py '<JSON 参数>' [--inline] [--no-cache]
默认复用24小时本地缓存；完整响应始终落盘，小结果全量打印、大结果摘要。
"""

import json
from pathlib import Path
import sys
import tempfile
import time

import call_api

API_PATH = "/echotik/listSeller"
SLUG = "linkfox-echotik-list-seller"


def _prepare_output_root():
    """在请求前检查当前目录能否落盘，不回退到临时目录。"""
    cwd = Path.cwd().resolve()
    if cwd.as_posix() == "/tmp" or cwd.as_posix().startswith("/tmp/"):
        raise OSError("禁止将本技能响应写入 /tmp，请在项目目录运行")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    # 固定本次运行的输出根目录，使用公共调用器的单层响应缓存。
    call_api._SESSION_CACHE["_root"] = str(root)
    # 根目录可写不代表最终会话目录可写；先检查实际保存位置，避免请求后才失败。
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    params = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 缺少参数或 JSON 格式错误时使用公共 CLI 的错误提示，不创建输出文件。
    if params:
        try:
            json.loads(params[0])
        except json.JSONDecodeError:
            pass
        else:
            try:
                _prepare_output_root()
            except OSError as exc:
                print(f"当前目录无法保存响应：{exc}", file=sys.stderr)
                raise SystemExit(1) from exc
    call_api.run(API_PATH, SLUG, argv=argv)


if __name__ == "__main__":
    main()
