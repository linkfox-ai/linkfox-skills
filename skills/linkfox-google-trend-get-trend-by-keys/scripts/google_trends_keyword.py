#!/usr/bin/env python3
"""Google Trends 关键词趋势查询，提供 CLI、缓存和响应输出。

用法：python google_trends_keyword.py '<JSON 参数>' [--inline] [--no-cache]
默认使用 24 小时缓存；完整响应始终落盘，小结果全量输出，大结果展示摘要。
"""

import json
from pathlib import Path
import sys
import tempfile
import time

import call_api as api


API_PATH = "/googleTrend/getTrendByKeys"
SLUG = "linkfox-google-trend-get-trend-by-keys"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return
    if not argv:
        return api.run(API_PATH, SLUG, argv=argv)

    # 公共调用器可回退目录；本技能要求当前目录可写，且应在收费请求前检查。
    cwd = Path.cwd().resolve()
    tmp_root = Path("/tmp").resolve()
    if cwd == tmp_root or tmp_root in cwd.parents:
        print("禁止将响应保存在 /tmp，请切换到可写的项目目录。", file=sys.stderr)
        raise SystemExit(1)
    root = cwd / "linkfox"
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"当前工作目录不可写，无法保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    api._SESSION_CACHE["_root"] = str(root)
    output_path = None

    def resolve_output_path(slug, _ts):
        nonlocal output_path
        # 同秒多次执行也分别保存响应，避免覆盖已保存的数据。
        output_path = api.resolve_data_path(slug, time.time())
        return output_path

    api._resolve_output_path = resolve_output_path
    try:
        # 使用公共调用器的缓存键、目录和 TTL，不另设一层缓存。
        result = api.run(API_PATH, SLUG, argv=argv)
        # 公共调用器会记录但吞掉保存错误；本技能要求落盘失败时明确退出。
        if output_path is not None:
            with open(output_path, encoding="utf-8") as saved:
                json.load(saved)
        return result
    except (OSError, json.JSONDecodeError) as exc:
        print(f"无法完整保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
