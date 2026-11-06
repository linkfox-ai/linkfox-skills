#!/usr/bin/env python3
"""查询异步创作任务，始终禁用响应缓存，支持 JSON、--inline、--no-cache 命令行入口。"""
from _aigc_runtime import run_entry, get_api_key, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/taskQuery"
SLUG = "linkfox-aigc-video-reclone"


def main():
    run_entry(API_PATH)


if __name__ == "__main__":
    main()
