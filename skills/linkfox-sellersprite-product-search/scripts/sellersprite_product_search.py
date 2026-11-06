#!/usr/bin/env python3
"""卖家精灵商品搜索：提供 CLI、24 小时缓存与当前目录落盘。

用法：python sellersprite_product_search.py '<JSON 参数>' [--inline] [--no-cache]
接口请求、唯一一层响应缓存及摘要统一由 call_api.run 完成。
业务封装校验输出目录、分配唯一文件名，并保留本次请求的 HTTP 状态。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/sellersprite/productSearch"
SLUG = "linkfox-sellersprite-product-search"


def _prepare_output_root():
    """请求前核对当前目录可写，阻止通用调用器回退到其他目录。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("业务数据禁止写入 /tmp，请从可写的项目目录运行")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 只固定输出根目录；缓存继续由公共调用器在 cwd/linkfox/.cache 下管理。
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def _resolve_unique_output_path(slug, ts):
    """按会话登记输出文件，原子占位以避免同一秒的响应相互覆盖。"""
    _, session_dir = call_api._ensure_session(ts)
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    stamp = int(ts * 1_000_000)
    while True:
        out_path = data_dir / f"{slug}-{stamp}.json"
        try:
            with out_path.open("x", encoding="utf-8"):
                pass
        except FileExistsError:
            stamp += 1
        else:
            break
    call_api._update_meta(
        session_dir, skill=slug, kind="data",
        file_rel=os.path.relpath(out_path, session_dir), ts=ts,
    )
    return str(out_path)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 无参数及无效 JSON 的错误输出和退出码由公共 CLI 处理。
    if positional:
        try:
            json.loads(positional[0])
        except json.JSONDecodeError:
            pass
        else:
            try:
                _prepare_output_root()
            except OSError as exc:
                print(f"当前目录不可写或无法保存业务数据：{exc}", file=sys.stderr)
                raise SystemExit(1) from exc
    # 保留传输状态，避免 JSON 错误响应丢失 HTTP 401/402 等判据。
    original_request = call_api.call_api
    original_urlopen = call_api.urlopen

    def request_with_status(api_path, params):
        status = None

        def urlopen_with_status(*args, **kwargs):
            nonlocal status
            try:
                response = original_urlopen(*args, **kwargs)
            except call_api.HTTPError as exc:
                status = exc.code
                raise
            status = response.status
            return response

        try:
            call_api.urlopen = urlopen_with_status
            result = original_request(api_path, params)
        finally:
            call_api.urlopen = original_urlopen
        if isinstance(result, dict) and status is not None:
            result["_http_status"] = status
        return result

    # 仅在本次调用期间替换业务钩子，结束后恢复公共调用器。
    original_resolver = call_api._resolve_output_path
    try:
        call_api._resolve_output_path = _resolve_unique_output_path
        call_api.call_api = request_with_status
        return call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._resolve_output_path = original_resolver
        call_api.call_api = original_request


if __name__ == "__main__":
    main()
