#!/usr/bin/env python3
"""查询异步任务且始终绕过缓存；支持 JSON、--inline、--no-cache CLI。"""
from _aigc_api import run_entry, get_api_key, get_api_base, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/taskQuery"
SLUG = "linkfox-aigc-image-edit"


def main():
    return run_entry(API_PATH)


if __name__ == "__main__":
    main()
