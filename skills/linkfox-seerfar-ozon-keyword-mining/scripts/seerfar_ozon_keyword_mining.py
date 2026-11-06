#!/usr/bin/env python3
"""Seerfar Ozon 关键词挖掘。

用法：python seerfar_ozon_keyword_mining.py '<JSON 参数>' [--inline] [--no-cache]
使用 24 小时单层响应缓存，由公共调用器执行缓存、落盘和输出。
"""

import os
from pathlib import Path
import tempfile

import call_api as api


API_PATH = "/seerfar/ozon/keywordMining"
SLUG = "linkfox-seerfar-ozon-keyword-mining"


def _call_with_http_status(call, api_path, params):
    """沿用公共请求逻辑，补存传输层状态，避免 JSON 错误体丢失状态码。"""
    status = None
    previous_urlopen = api.urlopen

    def record_status(*args, **kwargs):
        nonlocal status
        try:
            response = previous_urlopen(*args, **kwargs)
        except api.HTTPError as exc:
            status = exc.code
            raise
        status = response.status
        return response

    api.urlopen = record_status
    try:
        result = call(api_path, params)
    finally:
        api.urlopen = previous_urlopen
    if isinstance(result, dict) and status is not None:
        result["_http_status"] = status
    return result


def main():
    # 响应落盘到 cwd；禁止公共调用器回退到家目录或临时目录。
    root = Path.cwd() / "linkfox"
    if os.name != "nt" and Path("/tmp") in root.resolve().parents:
        raise OSError("请在可写的项目目录运行，禁止将响应写入 /tmp")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_root = api._SESSION_CACHE.get("_root")
    previous_call = api.call_api
    api._SESSION_CACHE["_root"] = str(root)
    api.call_api = lambda path, params: _call_with_http_status(previous_call, path, params)
    try:
        # 公共调用器负责单层响应缓存，此处不另行读写缓存。
        api.run(API_PATH, SLUG)
    finally:
        api.call_api = previous_call
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
