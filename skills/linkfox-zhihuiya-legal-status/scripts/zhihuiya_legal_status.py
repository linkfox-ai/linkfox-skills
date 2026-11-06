#!/usr/bin/env python3
"""智慧芽专利法律状态查询。

用法：python zhihuiya_legal_status.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；不超过 8 KB 时完整输出，否则输出摘要。
默认保留 24 小时本地缓存；--no-cache 跳过缓存，--inline 强制完整输出。
"""

import json
import os
from pathlib import Path
import secrets
import sys

import call_api


API_PATH = "/zhihuiya/legalStatus"
SLUG = "linkfox-zhihuiya-legal-status"


def _query_with_http_status(api_path, params):
    """保留 HTTP 诊断信息，供业务响应判定及认证/算力恢复使用。"""
    request = call_api.Request(
        call_api.get_api_url(api_path),
        data=json.dumps(params).encode("utf-8"),
        headers={
            "Authorization": call_api.get_api_key(),
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/2.0",
            **{name: os.environ.get(name, "") for name in
               ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME")},
        },
        method="POST",
    )
    try:
        with call_api.urlopen(request, timeout=150) as response:
            status = response.status
            payload = json.loads(response.read().decode("utf-8"))
    except call_api.HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8") if exc.fp else ""
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {"details": body}
        if not isinstance(payload, dict):
            payload = {"_response": payload}
        payload["_http_error"] = f"HTTP {status}: {exc.reason}"
    except call_api.URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}
    if isinstance(payload, dict):
        payload["_http_status"] = status
    return payload


def _check_writable(directory):
    probe = directory / (".legal_status_probe_" + secrets.token_hex(6))
    try:
        with probe.open("x", encoding="utf-8"):
            pass
    finally:
        if probe.exists():
            probe.unlink()


def _prepare_output_root():
    """请求前检查完整落盘目录，查询数据仅写入当前工作目录。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("当前工作目录位于 /tmp，禁止在此保存查询数据")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    _check_writable(root)
    # 只约束当前调用的落盘根目录，不修改公共资源或添加第二层缓存。
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(int(call_api.time.time()))
    session = Path(session_dir)
    data_dir = session / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    # 根目录可写不代表已有会话目录、元数据和 data 目录也可写。
    with (session / "_meta.json").open("r+", encoding="utf-8"):
        pass
    _check_writable(data_dir)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--help"]:
        print("用法：python zhihuiya_legal_status.py '<JSON 参数>' [--inline] [--no-cache]")
        print("--inline 完整打印；--no-cache 跳过默认的 24 小时缓存。")
        return
    if args:
        try:
            _prepare_output_root()
        except OSError as exc:
            print(f"无法在当前工作目录保存查询数据：{exc}", file=sys.stderr)
            raise SystemExit(1)
    original_transport = call_api.call_api
    call_api.call_api = _query_with_http_status
    try:
        call_api.run(API_PATH, SLUG, argv=args)
    finally:
        call_api.call_api = original_transport


if __name__ == "__main__":
    main()
