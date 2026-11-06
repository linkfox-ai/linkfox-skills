#!/usr/bin/env python3
"""上传 Base64 素材，保留 JSON、--inline、--no-cache 命令行入口。"""
from _aigc_runtime import run_entry, get_api_key, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/uploadByBase64"
SLUG = "linkfox-aigc-video-reclone"


def main():
    run_entry(API_PATH)


if __name__ == "__main__":
    main()
