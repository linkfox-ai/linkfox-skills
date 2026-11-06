#!/usr/bin/env python3
"""Base64 素材上传；支持 JSON CLI 和会话输出。"""
from _aigc_runtime import (
    SLUG, _ensure_session, _update_meta, get_api_key, resolve_data_path, run_entry,
)

API_PATH = "/aigc/uploadByBase64"


def main():
    return run_entry(API_PATH)


if __name__ == "__main__":
    main()
