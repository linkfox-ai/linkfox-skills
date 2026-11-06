#!/usr/bin/env python3
"""智慧芽专利被引查询。

用法：python zhihuiya_cited_by.py '<JSON 参数>' [--inline] [--no-cache]
默认使用 24 小时缓存，完整响应始终以 UTF-8 保存。
"""

import json
import os
import sys
import tempfile
import time

import call_api


API_PATH = "/zhihuiya/patentCited"
SLUG = "linkfox-zhihuiya-patent-cited"


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    # 保留通用 CLI 对缺少参数和无效 JSON 的诊断；此时不产生目录或请求。
    if not [arg for arg in args if arg not in ("--inline", "--no-cache")]:
        return call_api.run(API_PATH, SLUG, args)
    try:
        json.loads(next(arg for arg in args if arg not in ("--inline", "--no-cache")))
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, args)

    # 当前目录不可写时报错；业务封装阻止公共调用器回退到其他目录。
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    try:
        os.makedirs(root, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
        call_api._SESSION_CACHE["_root"] = root
        _, session_dir = call_api._ensure_session(time.time())
        data_dir = os.path.join(session_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
    except OSError as exc:
        print(f"当前工作目录不可写，无法保存响应：{exc}", file=sys.stderr)
        return 1

    # 设置 JSON 响应协商；HTTP、缓存和输出由公共调用器负责。
    request_factory = call_api.Request
    api_caller = call_api.call_api

    def json_request(*request_args, **request_kwargs):
        request = request_factory(*request_args, **request_kwargs)
        request.add_header("Accept", "application/json")
        return request

    def call_with_status(api_path, params):
        # 公共调用器解析 HTTPError 后仅返回响应体，在业务层保留实际状态。
        opener = call_api.urlopen
        status = None

        def tracked_open(*open_args, **open_kwargs):
            nonlocal status
            try:
                response = opener(*open_args, **open_kwargs)
            except call_api.HTTPError as exc:
                status = exc.code
                raise
            status = response.getcode()
            return response

        call_api.urlopen = tracked_open
        try:
            result = api_caller(api_path, params)
        finally:
            call_api.urlopen = opener
        if isinstance(result, dict) and status is not None:
            result["_http_status"] = status
        return result

    call_api.Request = json_request
    call_api.call_api = call_with_status
    try:
        call_api.run(API_PATH, SLUG, args)
    finally:
        call_api.Request = request_factory
        call_api.call_api = api_caller
    return 0


if __name__ == "__main__":
    sys.exit(main())
