#!/usr/bin/env python3
"""查询参考 ASIN 的细分市场，复用公共调用、单层缓存与会话输出。

用法：python jiimore_get_niche_info_by_asin.py '<JSON 参数>' [--inline] [--no-cache]
"""

import json
import os
import sys
import tempfile
import time

import call_api


API_PATH = "/jiimore/getNicheInfoByAsin"
SLUG = "linkfox-jiimore-get-niche-info-by-asin"


def _prepare_output():
    """检查当前目录的响应落盘路径，失败时在请求前报错。"""
    cwd = os.path.abspath(os.getcwd())
    if cwd == "/tmp" or cwd.startswith("/tmp/"):
        raise OSError("响应禁止保存到 /tmp，请切换到可写的工作目录")
    root = os.path.join(cwd, "linkfox")
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    # 固定公共调用器的输出根目录，避免只读目录时回退到其他位置。
    call_api._SESSION_CACHE["_root"] = root
    # 根目录可写不代表已有的会话数据目录可写，必须在付费请求前验证。
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = [a for a in argv if a not in ("--inline", "--no-cache")]
    # 无参数或 JSON 错误交回公共 CLI 报错，避免无效输入创建目录。
    if args:
        try:
            json.loads(args[0])
        except json.JSONDecodeError:
            pass
        else:
            try:
                _prepare_output()
            except OSError as exc:
                print(f"当前工作目录不可写或不适合保存响应：{exc}", file=sys.stderr)
                raise SystemExit(1)
    call_api.run(API_PATH, SLUG, argv=argv)


if __name__ == "__main__":
    main()
