#!/usr/bin/env python3
"""查询已有任务；始终禁用响应缓存。"""
import call_api
from call_api import get_api_key, resolve_data_path, _ensure_session, _update_meta
from _aigc_runtime import run_entry

API_PATH = "/aigc/taskQuery"
SLUG = "linkfox-aigc-video-translate"


def main(argv=None):
    return run_entry(API_PATH, "taskQuery", argv, force_no_cache=True)


if __name__ == "__main__":
    main()
