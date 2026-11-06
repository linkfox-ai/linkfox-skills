#!/usr/bin/env python3
"""获取智慧芽专利 PDF 链接，提供 CLI、缓存和会话数据输出。

用法：python zhihuiya_pdf_data.py '<JSON 参数>' [--inline] [--no-cache]
请求、唯一一层 24 小时缓存、摘要和 UTF-8 完整响应落盘均使用公共调用器。
业务封装提供本地帮助、输入检查、写入预检及 JSON 响应请求头。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api as transport
from call_api import run


API_PATH = "/zhihuiya/pdfData"
SLUG = "linkfox-zhihuiya-pdf-data"
USAGE = "用法：zhihuiya_pdf_data.py '<JSON 参数>' [--inline] [--no-cache]"


def _cwd_root():
    """在当前目录保存；不使用公共调用器的目录回退。"""
    root = Path(os.getcwd()) / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print(USAGE)
        print("默认复用 24 小时缓存；--no-cache 禁用读写，--inline 强制全量输出。")
        return

    values = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not values:
        print(USAGE, file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(values[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须是对象。", file=sys.stderr)
        raise SystemExit(1)

    original_root = transport._linkfox_root
    original_request = transport.Request
    original_call = transport.call_api

    def call_with_http_status(api_path, request_params):
        # 公共调用器解析 JSON 错误体时不保留 HTTP 状态，在业务层附加。
        original_open = transport.urlopen
        http_status = None

        def open_with_status(*args, **kwargs):
            nonlocal http_status
            try:
                response = original_open(*args, **kwargs)
            except transport.HTTPError as exc:
                http_status = exc.code
                raise
            http_status = response.status
            return response

        transport.urlopen = open_with_status
        try:
            result = original_call(api_path, request_params)
        finally:
            transport.urlopen = original_open
        if isinstance(result, dict) and http_status is not None:
            result["_http_status"] = http_status
        return result

    def request_with_accept(*args, **kwargs):
        # 显式要求 JSON 响应；HTTP 由公共调用器执行。
        request = original_request(*args, **kwargs)
        request.add_header("Accept", "application/json")
        return request

    transport._linkfox_root = _cwd_root
    transport.Request = request_with_accept
    transport.call_api = call_with_http_status
    try:
        # 请求前验证最终数据目录可写，避免收费后才发现不能保存响应。
        _, session_dir = transport._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        # 缓存目录、参数键、TTL 和 --no-cache 行为由公共调用器管理。
        # 此处不维护第二层缓存，LinkFox HTTP 也由公共调用器执行。
        run(API_PATH, SLUG, argv=argv)
    except OSError as exc:
        print(f"当前工作目录无法保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        transport._linkfox_root = original_root
        transport.Request = original_request
        transport.call_api = original_call


if __name__ == "__main__":
    main()
