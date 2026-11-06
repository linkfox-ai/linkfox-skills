#!/usr/bin/env python3
"""查询已有任务，每次获取当前状态，不读取或写入响应缓存。"""
from _aigc_common import run, get_api_key, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/taskQuery"
SLUG = "linkfox-aigc-image-to-video"


def main():
    run(API_PATH, "task-query", force_no_cache=True)


if __name__ == "__main__":
    main()
