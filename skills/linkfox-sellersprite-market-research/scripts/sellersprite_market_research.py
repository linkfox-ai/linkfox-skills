#!/usr/bin/env python3
"""卖家精灵类目市场调研。

用法：python sellersprite_market_research.py '<JSON 参数>' [--inline] [--no-cache]
使用公共调用器的 24 小时缓存、会话登记和大小响应输出策略。
"""

import json
import os
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import call_api


API_PATH = "/sellersprite/market/research"
SLUG = "linkfox-sellersprite-market-research"


def _call_market_api(api_path, params):
    """保留 HTTP 状态，避免 JSON 错误体被误作正常市场结果。"""
    headers = {
        "Authorization": call_api.get_api_key(),
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        **{name: os.environ.get(name, "")
           for name in ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME")},
    }
    request = Request(call_api.get_api_url(api_path),
                      data=json.dumps(params).encode("utf-8"),
                      headers=headers, method="POST")
    failure = None
    try:
        with urlopen(request, timeout=150) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        failure = f"HTTP {status}: {exc.reason}"
    except URLError as exc:
        return {"error": f"Connection failed: {exc.reason}", "_http_status": None}

    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        result = {"error": failure or f"HTTP {status}: 响应不是有效 JSON", "details": body}
    if not isinstance(result, dict):
        result = {"error": failure or f"HTTP {status}: 响应不是 JSON 对象", "details": body}
    if failure:
        result.setdefault("error", failure)
    result["_http_status"] = status
    return result


def _prepare_output_root():
    """将响应保存到当前目录；不可写时在发出请求前报错。"""
    cwd = os.path.realpath(os.getcwd())
    if cwd == "/tmp" or cwd.startswith("/tmp/"):
        raise OSError("禁止将响应写入 /tmp；请在可写的项目目录运行。")
    root = os.path.join(cwd, "linkfox")
    os.makedirs(root, exist_ok=True)
    # 显式指定目录，不使用系统临时目录，也不另建缓存。
    with tempfile.TemporaryFile(dir=root):
        pass
    call_api._SESSION_CACHE["_root"] = os.path.abspath(root)


def main(argv=None):
    _prepare_output_root()
    transport = call_api.call_api
    call_api.call_api = _call_market_api
    try:
        return call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api.call_api = transport


if __name__ == "__main__":
    main()
