#!/usr/bin/env python3
"""极目亚马逊细分市场评论查询。

用法：python jiimore_get_niche_review.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；默认使用 24 小时缓存，不叠加第二层缓存。
"""

from pathlib import Path
import sys
import tempfile
import time

import call_api as _common


API_PATH = "/jiimore/getNicheReviewFromKeyword"
SLUG = "linkfox-jiimore-get-niche-review-from-keyword"


def _prepare_output_root():
    """请求前验证当前目录可写；业务数据不使用公共调用器的回退目录。"""
    cwd = Path.cwd().resolve()
    forbidden = Path("/tmp").resolve()
    if cwd == forbidden or forbidden in cwd.parents:
        raise OSError("禁止将业务数据写入 /tmp，请切换到可写的工作目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 防止已有 linkfox 符号链接把输出带到当前目录外。
    if root.resolve() != root:
        raise OSError("linkfox 必须是当前工作目录内的真实目录")
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法：jiimore_get_niche_review.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认缓存 24 小时；--inline 全量输出；--no-cache 关闭缓存读写。")
        return 0

    # 无参数时由公共调用器输出 CLI 用法，不触发目录创建或网络请求。
    if not [arg for arg in argv if arg not in ("--inline", "--no-cache")]:
        return _common.run(API_PATH, SLUG, argv=argv)

    try:
        root = _prepare_output_root()
    except OSError as exc:
        print(f"当前工作目录不可用于保存响应：{exc}", file=sys.stderr)
        return 1

    previous_root = _common._SESSION_CACHE.get("_root")
    original_request = _common.Request
    original_output_path = _common._resolve_output_path

    def output_path(slug, _ts):
        # 公共流程把时间截断到秒；保留微秒以免连续查询覆盖完整响应。
        return original_output_path(slug, time.time())

    def json_request(*args, **kwargs):
        # 业务入口携带 Accept；HTTP transport 由公共调用器实现。
        request = original_request(*args, **kwargs)
        request.add_header("Accept", "application/json")
        return request

    _common._SESSION_CACHE["_root"] = root
    _common.Request = json_request
    _common._resolve_output_path = output_path
    try:
        # 公共调用器管理缓存键、TTL、缓存命中标记、会话元信息和摘要流程。
        # 默认开启缓存，可通过 --no-cache 关闭缓存读写。
        _common.run(API_PATH, SLUG, argv=argv)
    finally:
        _common._resolve_output_path = original_output_path
        _common.Request = original_request
        if previous_root is None:
            _common._SESSION_CACHE.pop("_root", None)
        else:
            _common._SESSION_CACHE["_root"] = previous_root
    return 0


if __name__ == "__main__":
    sys.exit(main())
