#!/usr/bin/env python3
"""通过 Base64 上传素材；支持 JSON、--inline、--no-cache CLI。"""
from _aigc_api import run_entry, get_api_key, get_api_base, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/uploadByBase64"
SLUG = "linkfox-aigc-image-edit"


def main():
    return run_entry(API_PATH)


if __name__ == "__main__":
    main()
