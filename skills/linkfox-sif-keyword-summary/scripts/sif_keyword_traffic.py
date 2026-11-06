#!/usr/bin/env python3
"""SIF 关键词流量来源分析，支持命令行调用、单层缓存与会话输出。

用法：python sif_keyword_traffic.py '<JSON 参数>' [--inline] [--no-cache]
公共调用器使用按参数计算的缓存键和 24 小时有效期，不另设业务缓存。
"""

import sys
import tempfile
import time
from pathlib import Path

import call_api as api


API_PATH = "/sif/keywordSummary"
SLUG = "linkfox-sif-keyword-summary"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # 必须先检查当前目录，不允许公共调用器回退到家目录或临时目录。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    previous_request = api.Request
    previous_urlopen = api.urlopen
    previous_call_api = api.call_api
    previous_summarize = api.summarize
    http_status = None

    def request_with_accept(*args, **kwargs):
        request = previous_request(*args, **kwargs)
        request.add_header("Accept", "application/json")
        return request

    def urlopen_with_status(*args, **kwargs):
        nonlocal http_status
        try:
            response = previous_urlopen(*args, **kwargs)
        except api.HTTPError as exc:
            http_status = exc.code
            raise
        http_status = response.getcode()
        return response

    def call_with_status(api_path, params):
        nonlocal http_status
        http_status = None
        result = previous_call_api(api_path, params)
        if isinstance(result, dict) and http_status is not None:
            result["_http_status"] = http_status
        return result

    def summarize_with_status(result):
        if isinstance(result, dict) and "_http_status" in result:
            print(f"  _http_status: {result['_http_status']}")
        previous_summarize(result)

    api._SESSION_CACHE["_root"] = str(root)
    # 公共调用器默认使用整秒；业务入口使用微秒时间戳，避免同秒覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    api.Request = request_with_accept
    api.urlopen = urlopen_with_status
    api.call_api = call_with_status
    api.summarize = summarize_with_status
    try:
        api.run(API_PATH, SLUG, argv=argv)
    finally:
        api.summarize = previous_summarize
        api.call_api = previous_call_api
        api.urlopen = previous_urlopen
        api.Request = previous_request
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
