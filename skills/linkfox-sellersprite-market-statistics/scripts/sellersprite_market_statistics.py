#!/usr/bin/env python3
"""卖家精灵类目市场统计命令行入口。

用法：python sellersprite_market_statistics.py '<JSON 参数>' [--inline] [--no-cache]
公共调用器提供单层 24 小时缓存、会话落盘和摘要输出。
"""

from pathlib import Path
import json
import os
import tempfile
import time

import call_api


API_PATH = "/sellersprite/market/statistics"
SLUG = "linkfox-sellersprite-market-statistics"


def _call_api_with_status(api_path, params):
    """保留 HTTP 状态，供认证、算力引导及响应码判断使用。"""
    headers = {
        "Authorization": call_api.get_api_key(),
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        **{name: os.environ.get(name, "")
           for name in ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME")},
    }
    request = call_api.Request(
        call_api.get_api_url(api_path),
        data=json.dumps(params).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        response = call_api.urlopen(request, timeout=150)
    except call_api.HTTPError as error:
        response = error
    except call_api.URLError as error:
        return {"error": f"Connection failed: {error.reason}"}

    with response:
        status = response.code
        reason = getattr(response, "reason", "")
        body = response.read().decode("utf-8")
    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        result = {"error": f"HTTP {status}: {reason}; 响应不是有效 JSON", "details": body}
    if not isinstance(result, dict):
        result = {"_response_body": result}
    result["_http_status"] = status
    return result


def main(argv=None):
    # 响应只保存到当前工作目录下，不回退家目录或临时目录。
    cwd = Path.cwd().resolve()
    if cwd == Path("/tmp").resolve() or Path("/tmp").resolve() in cwd.parents:
        raise OSError("原始响应禁止保存到 /tmp，请切换到可写的项目目录")
    call_api._SESSION_CACHE["_root"] = str(cwd / "linkfox")
    # 在可能扣费的请求前确认本次会话的数据目录可写。
    # 公共调用器的保存发生在请求之后，入口负责提前兑现落盘约束。
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass
    original_call = call_api.call_api
    call_api.call_api = _call_api_with_status
    try:
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api.call_api = original_call


if __name__ == "__main__":
    main()
