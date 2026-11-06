#!/usr/bin/env python3
"""友鹰 Shopee 商品选品。

用法：python youying_shopee_search.py '<JSON 参数>' [--inline] [--no-cache]
公共调用器提供 24 小时缓存、完整落盘、8 KB 阈值及三条摘要样本。
"""

import os
from pathlib import Path
import sys
import tempfile
from urllib.error import HTTPError

import call_api


API_PATH = "/youying/shopee/getProductInfos"
SLUG = "linkfox-youying-shopee-get-product-infos"


def _prepare_storage():
    """在请求前检查 cwd 落盘条件，不回退到其他目录。"""
    sid = (os.environ.get("SESSION_ID") or "").strip()
    if sid in (".", "..") or any(char in sid for char in ("/", "\\", ":")):
        raise ValueError("SESSION_ID 必须是单个目录名")
    root = (Path.cwd() / "linkfox").resolve()
    if os.name != "nt" and (root == Path("/tmp") or Path("/tmp") in root.parents):
        raise ValueError("响应文件禁止写入 /tmp，请切换工作目录")
    root.mkdir(parents=True, exist_ok=True)
    # 只覆盖公共调用器的目录选择缓存，不修改其源码，也不增加响应缓存。
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session = call_api._ensure_session(call_api.time.time())
    data_dir = Path(session) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def _resolve_output_path(slug, ts):
    """独占分配文件名，避免公共流程的秒级时间戳覆盖已有响应。"""
    _, session = call_api._ensure_session(ts)
    data_dir = Path(session) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    stamp = int(ts * 1_000_000)
    while True:
        out = data_dir / f"{slug}-{stamp}.json"
        try:
            with out.open("x", encoding="utf-8"):
                pass
            break
        except FileExistsError:
            stamp += 1
    call_api._update_meta(
        session, skill=slug, kind="data", file_rel=str(out.relative_to(session)), ts=ts
    )
    return str(out)


def _call_with_http_status(transport, api_path, params):
    """保留本次请求的实际 HTTP 状态，正文仍由公共调用器解析。"""
    original_urlopen = call_api.urlopen
    http_status = None

    def observe_status(*args, **kwargs):
        nonlocal http_status
        try:
            response = original_urlopen(*args, **kwargs)
        except HTTPError as exc:
            http_status = exc.code
            raise
        http_status = response.getcode()
        return response

    call_api.urlopen = observe_status
    try:
        result = transport(api_path, params)
    finally:
        call_api.urlopen = original_urlopen
    if isinstance(result, dict) and http_status is not None:
        result["_http_status"] = http_status
    return result


def _cache_path(slug, params):
    """沿用公共缓存位置与键，在 Windows 使用可支持长文件名的绝对路径。"""
    folder = str(Path.cwd() / "linkfox" / ".cache" / slug)
    if os.name == "nt" and not folder.startswith("\\\\?\\"):
        folder = "\\\\?\\UNC\\" + folder[2:] if folder.startswith("\\\\") else "\\\\?\\" + folder
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{slug}-{call_api._cache_key(params)}.json")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        _prepare_storage()
    except (OSError, ValueError) as exc:
        print(f"当前目录无法保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    # 仅在本次 CLI 流程中替换输出路径分配，HTTP 与响应缓存仍由 run 负责。
    original = call_api._resolve_output_path
    original_transport = call_api.call_api
    original_cache_path = call_api._cache_path
    call_api._resolve_output_path = _resolve_output_path
    call_api.call_api = lambda path, params: _call_with_http_status(original_transport, path, params)
    call_api._cache_path = _cache_path
    try:
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._resolve_output_path = original
        call_api.call_api = original_transport
        call_api._cache_path = original_cache_path


if __name__ == "__main__":
    main()
