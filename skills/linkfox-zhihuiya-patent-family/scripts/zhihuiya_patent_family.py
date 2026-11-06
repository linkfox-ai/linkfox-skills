#!/usr/bin/env python3
"""智慧芽专利家族查询：支持 CLI、单层 24 小时缓存和会话输出。

用法：python zhihuiya_patent_family.py '<JSON 参数>' [--inline] [--no-cache]
HTTP、缓存和打印均委托给随技能分发的 call_api.run。
"""

import sys
import tempfile
import time
from pathlib import Path

import call_api as api

API_PATH = "/zhihuiya/patentFamily"
SLUG = "linkfox-zhihuiya-patent-family"


def _call_with_http_status(call, api_path, params):
    """复用公共请求处理，并保留本次实际收到的 HTTP 状态。"""
    status = None
    previous_urlopen = api.urlopen

    def capture_status(*args, **kwargs):
        nonlocal status
        try:
            response = previous_urlopen(*args, **kwargs)
        except api.HTTPError as error:
            status = error.code
            raise
        status = response.status
        return response

    api.urlopen = capture_status
    try:
        result = call(api_path, params)
    finally:
        api.urlopen = previous_urlopen
    if isinstance(result, dict) and status is not None:
        result["_http_status"] = status
    return result


def main():
    # 数据保存在 cwd，禁止公共调用器回退其他目录。
    root = Path.cwd() / "linkfox"
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    previous_call_api = api.call_api
    api._SESSION_CACHE["_root"] = str(root)
    try:
        # 请求前检查实际会话数据目录，避免根目录可写、data 不可写时先扣费。
        # 公共 run 使用整秒时间；这里预先以微秒生成本次唯一输出路径。
        output_path = api.resolve_data_path(SLUG, time.time())
        with tempfile.TemporaryFile(dir=Path(output_path).parent):
            pass
        api._resolve_output_path = lambda _slug, _ts: output_path
        api.call_api = lambda path, params: _call_with_http_status(previous_call_api, path, params)
        # 使用公共调用器的缓存位置、键和 TTL，不叠加缓存。
        api.run(API_PATH, SLUG, argv=sys.argv[1:])
    finally:
        api.call_api = previous_call_api
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
