#!/usr/bin/env python3
"""taskQuery 业务入口；参数与运行约定见 references。"""
from _video_runtime import run, get_api_key, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/taskQuery"
SLUG = "linkfox-aigc-video-edit"

def main():
    return run(API_PATH, SLUG + "-taskQuery", force_no_cache=True)

if __name__ == "__main__":
    main()
