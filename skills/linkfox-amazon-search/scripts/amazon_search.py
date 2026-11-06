#!/usr/bin/env python3
"""亚马逊前台搜索 CLI，提供 24 小时缓存与完整落盘输出。

用法：python amazon_search.py '<JSON 参数>' [--inline] [--no-cache]
LinkFox 请求、缓存和输出统一委托给 call_api.run。
"""

from contextlib import contextmanager
import json
import os
import sys
import tempfile
import time
from urllib.error import HTTPError

import call_api


API_PATH = "/amazon/search"
SLUG = "linkfox-amazon-search"


def _prepare_output():
    """在请求前落实当前目录可写、禁止家目录或临时目录回退的约定。"""
    cwd = os.path.realpath(os.getcwd())
    if cwd == "/tmp" or cwd.startswith("/tmp/"):
        raise OSError("请在项目目录运行，禁止将响应保存在 /tmp")
    root = os.path.join(cwd, "linkfox")
    os.makedirs(root, exist_ok=True)
    call_api._SESSION_CACHE["_root"] = root
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def _unique_output_path(slug, ts):
    """独占预留输出文件，避免同秒查询或并行 CLI 覆盖完整响应。"""
    _, session_dir = call_api._ensure_session(ts)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    stamp = int(ts * 1_000_000)
    while True:
        out = os.path.join(data_dir, f"{slug}-{stamp}.json")
        try:
            with open(out, "x", encoding="utf-8"):
                pass
        except FileExistsError:
            stamp += 1
        else:
            break
    call_api._update_meta(
        session_dir, skill=slug, kind="data",
        file_rel=os.path.relpath(out, session_dir), ts=ts,
    )
    return out


@contextmanager
def _preserve_http_errors():
    """公共调用器保留原 JSON；业务层额外保留 HTTP 失败状态以免误判空结果。"""
    opener = call_api.urlopen
    transport = call_api.call_api
    observed = {}

    def observe(*args, **kwargs):
        try:
            return opener(*args, **kwargs)
        except HTTPError as exc:
            observed.update(status=exc.code, reason=str(exc.reason))
            raise

    def request(path, params):
        observed.clear()
        result = transport(path, params)
        if "status" not in observed:
            return result
        failure = dict(result) if isinstance(result, dict) else {"details": result}
        failure["transportHttpStatus"] = observed["status"]
        failure["error"] = failure.get("error") or failure.get("errmsg") or failure.get("msg") or f"HTTP {observed['status']}: {observed['reason']}"
        return failure

    call_api.urlopen = observe
    call_api.call_api = request
    try:
        yield
    finally:
        call_api.urlopen = opener
        call_api.call_api = transport


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 无参数或 JSON 格式错误由公共入口输出 CLI 错误。
    if positional:
        try:
            json.loads(positional[0])
        except json.JSONDecodeError:
            pass
        else:
            try:
                _prepare_output()
            except OSError as exc:
                print(f"当前工作目录无法保存完整响应: {exc}", file=sys.stderr)
                raise SystemExit(1)
    # 在本次 CLI 调用期间使用独占文件命名策略。
    resolver = call_api._resolve_output_path
    call_api._resolve_output_path = _unique_output_path
    try:
        with _preserve_http_errors():
            call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._resolve_output_path = resolver


if __name__ == "__main__":
    main()
