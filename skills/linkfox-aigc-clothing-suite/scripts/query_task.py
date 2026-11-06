#!/usr/bin/env python3
"""查询生成任务，保留 JSON、--inline 与 --no-cache 命令行。"""
import sys
import call_api as common
from _aigc_runtime import request, run_entry

API_PATH = "/aigc/taskQuery"
SLUG = "linkfox-aigc-clothing-suite"
get_api_key = common.get_api_key
get_api_base = common.get_api_base
_ensure_session = common._ensure_session
_update_meta = common._update_meta
resolve_data_path = common.resolve_data_path


def main():
    return run_entry(API_PATH, SLUG)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
