#!/usr/bin/env python3
"""智慧芽专利摘要附图：命令行查询、24 小时缓存和会话输出。

用法：python zhihuiya_abstract_image.py '<JSON 参数>' [--inline] [--no-cache]
LinkFox 请求、唯一一层响应缓存及输出均由 call_api.run 执行。
响应落盘到当前目录，不可写即报错；高精度时间戳避免同秒响应覆盖。
"""

import json
from pathlib import Path
import secrets
import sys
import tempfile
import time
from urllib.error import HTTPError

import call_api


API_PATH = "/zhihuiya/abstractImage"
SLUG = "linkfox-zhihuiya-abstract-image"


def _call_with_http_status(request_call, api_path, params):
    """保留实际传输状态，避免 JSON 错误体掩盖认证或计费失败。"""
    original_urlopen = call_api.urlopen
    http_status = None

    def capture_status(*args, **kwargs):
        nonlocal http_status
        try:
            response = original_urlopen(*args, **kwargs)
        except HTTPError as exc:
            http_status = exc.code
            raise
        http_status = response.status
        return response

    call_api.urlopen = capture_status
    try:
        result = request_call(api_path, params)
    finally:
        call_api.urlopen = original_urlopen
    if isinstance(result, dict) and http_status is not None:
        result["_http_status"] = http_status
    return result


def _check_writable(directory):
    directory.mkdir(parents=True, exist_ok=True)
    probe = directory / (".write_probe-" + secrets.token_hex(6))
    try:
        with probe.open("x", encoding="utf-8") as stream:
            stream.write("")
    finally:
        if probe.exists():
            probe.unlink()


def _prepare_root():
    """请求前检查目标目录，禁止临时目录和公共调用器的目录回退。"""
    cwd = Path.cwd().resolve()
    temp_roots = (Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve())
    if any(cwd == root or root in cwd.parents for root in temp_roots):
        raise OSError("禁止在临时目录运行，请切换到可写的项目目录")
    root = cwd / "linkfox"
    _check_writable(root)
    return str(root)


def _prepare_session():
    """实际会话数据、元数据及索引都可写后，才能发起收费请求。"""
    root, session = call_api._ensure_session(time.time())
    _check_writable(Path(session) / "data")
    with (Path(session) / "_meta.json").open("r+", encoding="utf-8"):
        pass
    with (Path(root) / "index.jsonl").open("a", encoding="utf-8"):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法：zhihuiya_abstract_image.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认复用 24 小时缓存；--inline 全量输出；--no-cache 跳过缓存读写。")
        return 0

    # 无参数或 JSON 错误沿用公共 CLI 的退出与提示，不触发网络请求。
    positional = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not positional:
        return call_api.run(API_PATH, SLUG, argv)
    try:
        json.loads(positional[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv)

    try:
        root = _prepare_root()
    except OSError as exc:
        print(f"当前目录不可用于保存响应：{exc}", file=sys.stderr)
        return 1

    # 在运行时指定当前工作目录作为输出根目录。
    original_root = call_api._linkfox_root
    original_output_path = call_api._resolve_output_path
    original_call = call_api.call_api
    original_summarize = call_api.summarize
    call_api._linkfox_root = lambda: root
    call_api.call_api = lambda path, params: _call_with_http_status(original_call, path, params)

    def summarize_with_status(result):
        if isinstance(result, dict) and "_http_status" in result:
            print(f"HTTP status (recorded): {result['_http_status']}")
        original_summarize(result)

    call_api.summarize = summarize_with_status
    # 公共 run 传入整秒时间；输出路径使用当前高精度时间。
    call_api._resolve_output_path = lambda slug, _ts: original_output_path(
        slug, time.time_ns() / 1_000_000_000
    )
    try:
        _prepare_session()
        return call_api.run(API_PATH, SLUG, argv)
    except OSError as exc:
        print(f"当前目录不可用于保存响应：{exc}", file=sys.stderr)
        return 1
    finally:
        call_api._linkfox_root = original_root
        call_api._resolve_output_path = original_output_path
        call_api.call_api = original_call
        call_api.summarize = original_summarize


if __name__ == "__main__":
    sys.exit(main())
