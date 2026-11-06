#!/usr/bin/env python3
"""Keepa 亚马逊商品搜索；接受 JSON 参数，支持 --inline 和 --no-cache 选项。

使用公共调用器的一层 24 小时缓存，并在请求前检查响应保存目录。
"""

import json
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/keepa/productSearch"
SLUG = "linkfox-keepa-product-search"


def _prepare_output_root():
    """请求前检查实际会话数据目录，不使用公共调用器的回退路径。"""
    cwd = Path.cwd().resolve()
    if cwd.as_posix() == "/tmp" or cwd.as_posix().startswith("/tmp/"):
        raise OSError("完整响应禁止保存到 /tmp，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = str(root)
    # 只检查根目录不足以保证落盘：会话目录或 data 可能被文件占用或只读。
    # 使用公共调用器的会话规则，提前准备元数据并检查最终数据目录。
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass
    return str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # 缺少参数或 JSON 无效时由公共 CLI 输出错误提示，不执行请求或建目录。
    params_argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if params_argv:
        try:
            json.loads(params_argv[0])
        except json.JSONDecodeError:
            pass
        else:
            try:
                _prepare_output_root()
            except OSError as exc:
                print(f"当前目录无法保存完整响应：{exc}", file=sys.stderr)
                raise SystemExit(1)
    call_api.run(API_PATH, SLUG, argv=argv)


if __name__ == "__main__":
    main()
