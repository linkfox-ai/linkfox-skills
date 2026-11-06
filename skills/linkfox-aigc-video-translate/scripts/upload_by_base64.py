#!/usr/bin/env python3
"""上传 Base64 素材；始终禁用响应缓存。"""
import call_api
from call_api import get_api_key, resolve_data_path, _ensure_session, _update_meta
from _aigc_runtime import run_entry

API_PATH = "/aigc/uploadByBase64"
SLUG = "linkfox-aigc-video-translate"


def main(argv=None):
    return run_entry(API_PATH, "uploadByBase64", argv, force_no_cache=True)


if __name__ == "__main__":
    main()
