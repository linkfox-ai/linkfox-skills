#!/usr/bin/env python3
"""卖家精灵流量词反查 CLI。

用法：
  python sellersprite_traffic_keyword.py '<JSON 参数>' [--inline] [--no-cache]

尝试保存完整响应；不超过 8000 字节时全量输出，否则输出摘要。
--inline 强制完整输出，--no-cache 禁用默认的 24 小时本地缓存。
公共调用器提供缓存、目录选择、认证兼容和会话落盘功能。
"""

import json
import os
from urllib.error import HTTPError, URLError

import call_api as shared


API_PATH = "/sellersprite/traffic/keyword"
SLUG = "linkfox-sellersprite-traffic-keyword"


def call_api(api_path, params):
    """保留本次 HTTP 状态与响应体，供认证、用量和业务错误判断。"""
    headers = {
        "Authorization": shared.get_api_key(),
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        **{name: os.environ.get(name, "")
           for name in ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME")},
    }
    request = shared.Request(
        shared.get_api_url(api_path),
        data=json.dumps(params).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with shared.urlopen(request, timeout=150) as response:
            status = response.status
            body = response.read().decode("utf-8")
            reason = response.reason
    except HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8") if exc.fp else ""
        reason = str(exc.reason)
    except URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {"error": f"HTTP {status}: {reason}" if status >= 400
                   else "Response is not valid JSON", "details": body}
    if not isinstance(payload, dict):
        payload = {"_response_body": payload}
    payload["_http_status"] = status
    return payload


def summarize(result):
    if isinstance(result, dict) and "_http_status" in result:
        print(f"HTTP status: {result['_http_status']}")
    _summarize(result)


_summarize = shared.summarize


def main():
    original_call = shared.call_api
    original_summary = shared.summarize
    shared.call_api = call_api
    shared.summarize = summarize
    try:
        shared.run(API_PATH, SLUG)
    finally:
        shared.call_api = original_call
        shared.summarize = original_summary


if __name__ == "__main__":
    main()
