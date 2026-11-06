#!/usr/bin/env python3
"""智慧芽检索式专利检索；复用公共请求、24 小时缓存及输出流程。

用法：
  python zhihuiya_query_search_patent.py '<JSON 参数>' [--inline] [--no-cache]

缓存文件路径与参数哈希由公共调用器维护；完整响应只保存至当前目录的 linkfox/。
"""

import json
import os
import sys
import tempfile

import call_api as _runner


API_PATH = "/zhihuiya/querySearchPatent"
SLUG = "linkfox-zhihuiya-retrieval-patent-search"


def _cwd_linkfox_root():
    """只允许在当前目录落盘，不采用公共调用器的其他目录回退。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    # 仅在目标目录创建临时探针，不创建系统临时目录文件。
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    positional = [a for a in args if a not in ("--inline", "--no-cache")]
    if not positional:
        print(
            "用法：zhihuiya_query_search_patent.py '<JSON 参数>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        raise SystemExit(1)
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 无效：{exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象，未发送请求", file=sys.stderr)
        raise SystemExit(1)

    # 缓存算法、文件位置及 CLI 由公共调用器维护，仅使用一层缓存。
    # 同步 CLI 期间临时约束输出根目录，结束后恢复，避免影响同进程其他调用。
    previous_root = _runner._linkfox_root
    try:
        _runner._linkfox_root = _cwd_linkfox_root
        try:
            # 根目录可写不代表会话及 data 子目录可写；收费请求前检查实际保存目录。
            _, session_dir = _runner._ensure_session(_runner.time.time())
            data_dir = os.path.join(session_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
        except OSError as exc:
            print(f"当前工作目录的响应保存路径不可写，未发送请求：{exc}", file=sys.stderr)
            raise SystemExit(1)
        return _runner.run(API_PATH, SLUG, argv=args)
    finally:
        _runner._linkfox_root = previous_root


if __name__ == "__main__":
    main()
