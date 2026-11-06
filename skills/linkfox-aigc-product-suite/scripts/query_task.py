#!/usr/bin/env python3
"""查询任务结果，始终禁用缓存；支持 JSON CLI 和会话输出。"""
from _aigc_runtime import (
    SLUG, _ensure_session, _update_meta, get_api_key, resolve_data_path, run_entry,
)

API_PATH = "/aigc/taskQuery"


def main():
    return run_entry(API_PATH)


if __name__ == "__main__":
    main()
