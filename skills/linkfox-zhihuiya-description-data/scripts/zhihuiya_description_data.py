#!/usr/bin/env python3
"""智慧芽专利说明书查询。

用法：
  python zhihuiya_description_data.py '<JSON 参数>' [--inline] [--no-cache]

使用公共调用器的 24 小时缓存、完整响应落盘和摘要输出。
业务入口固定当前工作目录，目录不可写时在请求前报错。
"""

import os
import sys
import tempfile

import call_api


API_PATH = "/zhihuiya/descriptionData"
SLUG = "linkfox-zhihuiya-description-data"


def _prepare_output_root():
    """遵守当前目录落盘约定，禁止公共调用器回退到其他目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    try:
        os.makedirs(root, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"当前工作目录不可写，无法保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    # 仅固定落盘根目录；响应缓存仍完全由公共调用器管理。
    call_api._SESSION_CACHE["_root"] = root


def _reserve_output_path(slug, ts):
    """独占创建输出文件，同秒多次运行也保留每份完整响应。"""
    while True:
        path = call_api.resolve_data_path(slug, ts)
        try:
            with open(path, "x", encoding="utf-8"):
                pass
            return path
        except FileExistsError:
            ts += 0.000001


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if any(arg not in ("--inline", "--no-cache") for arg in args):
        _prepare_output_root()
    previous_resolver = call_api._resolve_output_path
    call_api._resolve_output_path = _reserve_output_path
    try:
        return call_api.run(API_PATH, SLUG, argv=args)
    finally:
        call_api._resolve_output_path = previous_resolver


if __name__ == "__main__":
    main()
