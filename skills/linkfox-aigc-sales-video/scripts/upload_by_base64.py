#!/usr/bin/env python3
"""Base64 素材上传；支持 JSON、--inline、--no-cache 命令行与单层缓存。"""
from _linkfox_runtime import (
    run_entry, get_api_key, _ensure_session, _update_meta, resolve_data_path,
)

API_PATH = "/aigc/uploadByBase64"
SLUG = "linkfox-aigc-sales-video"


def main(argv=None):
    return run_entry(API_PATH, "upload", argv)


if __name__ == "__main__":
    main()
