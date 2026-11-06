#!/usr/bin/env python3
"""智慧芽专利著录查询；使用公共调用、响应缓存和会话输出。"""

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/zhihuiya/bibliography"
SLUG = "linkfox-zhihuiya-bibliography"


def _request_with_status(api_path, params):
    """保留 HTTP 状态与错误正文，供著录查询的认证和业务判断使用。"""
    headers = {
        "Authorization": call_api.get_api_key(),
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        **{name: os.environ.get(name, "")
           for name in ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME")},
    }
    request = call_api.Request(
        call_api.get_api_url(api_path),
        data=json.dumps(params).encode("utf-8"), headers=headers, method="POST",
    )
    try:
        with call_api.urlopen(request, timeout=150) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
    except call_api.HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
    except call_api.URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}
    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        result = {"error": f"HTTP {status}: 响应不是有效 JSON", "details": body}
    if not isinstance(result, dict):
        result = {"_response_body": result}
    result["_http_status"] = status
    return result


def _prepare_output():
    """在付费请求前检查当前目录的输出路径和可写性。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt":
        tmp = Path("/tmp").resolve()
        if cwd == tmp or tmp in cwd.parents:
            raise OSError("禁止将响应写入 /tmp，请切换到可写的项目目录")
    root = (cwd / "linkfox").resolve()
    if not root.is_relative_to(cwd):
        raise OSError("响应根目录必须位于当前工作目录内")
    ts = time.time()
    date_dir = root / time.strftime("%Y-%m-%d", time.localtime(ts))
    session_dir = (date_dir / call_api._session_id(ts)).resolve()
    if session_dir == date_dir or not session_dir.is_relative_to(date_dir):
        raise OSError("SESSION_ID 必须指向当前目录下当日会话目录，不能使用越界路径")
    root.mkdir(parents=True, exist_ok=True)
    # 会话根目录固定到当前项目，避免自动回退。
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session = call_api._ensure_session(ts)
    data_dir = Path(session) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def main(argv=None):
    parser = argparse.ArgumentParser(description="通过专利 ID 或公开公告号查询智慧芽著录信息")
    parser.add_argument("parameters", help="JSON 参数字符串")
    parser.add_argument("--inline", action="store_true", help="完整打印响应并保存")
    parser.add_argument("--no-cache", action="store_true", help="不读取或写入响应缓存")
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        parser.print_usage(file=sys.stderr)
        return 1
    args = parser.parse_args(argv)
    try:
        json.loads(args.parameters)
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式无效：{exc}", file=sys.stderr)
        return 1
    try:
        _prepare_output()
    except (OSError, ValueError) as exc:
        print(f"无法准备当前目录的响应文件：{exc}", file=sys.stderr)
        return 1
    options = [args.parameters]
    if args.inline:
        options.append("--inline")
    if args.no_cache:
        options.append("--no-cache")
    # 使用公共调用器的缓存键、TTL 和旁路选项，不设置第二层缓存。
    original_request = call_api.call_api
    try:
        call_api.call_api = _request_with_status
        call_api.run(API_PATH, SLUG, options)
    finally:
        call_api.call_api = original_request
    return 0


if __name__ == "__main__":
    sys.exit(main())
