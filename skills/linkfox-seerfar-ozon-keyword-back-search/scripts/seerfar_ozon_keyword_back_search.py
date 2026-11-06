#!/usr/bin/env python3
"""Seerfar Ozon 关键词反查。

用法：python seerfar_ozon_keyword_back_search.py '<JSON 参数>' [--inline] [--no-cache]
通过公共调用器提供 24 小时缓存、会话落盘及大小响应输出。
"""

import json
import os
from urllib.error import HTTPError, URLError

import call_api as common


API_PATH = "/seerfar/ozon/keywordBackSearch"
SLUG = "linkfox-seerfar-ozon-keyword-back-search"


def _decode_response(raw, status, reason=""):
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"error": f"HTTP {status}: {reason or '响应不是有效 JSON'}", "details": raw}
    if not isinstance(result, dict):
        result = {"error": "响应体不是 JSON 对象", "details": result}
    result["_http_status"] = status
    return result


def _call_api(api_path, params):
    """保留传输状态和原始业务字段，不重试或改写业务错误码。"""
    headers = {
        "Authorization": common.get_api_key(),
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
    }
    for name in ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME"):
        headers[name] = os.environ.get(name, "")
    request = common.Request(
        common.get_api_url(api_path),
        data=json.dumps(params).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with common.urlopen(request, timeout=150) as response:
            return _decode_response(response.read().decode("utf-8", errors="replace"), response.status)
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return _decode_response(raw, exc.code, str(exc.reason))
    except URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}


def main(argv=None):
    # 只替换本次运行的传输入口，复用公共缓存、落盘和输出逻辑。
    original = common.call_api
    common.call_api = _call_api
    try:
        common.run(API_PATH, SLUG, argv)
    finally:
        common.call_api = original


if __name__ == "__main__":
    main()
