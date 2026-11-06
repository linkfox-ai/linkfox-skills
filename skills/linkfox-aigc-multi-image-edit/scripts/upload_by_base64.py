#!/usr/bin/env python3
"""素材 Base64 上传；接受 JSON CLI 参数，通过公共调用器执行。"""
from _aigc_runtime import run_entry, get_api_key, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/uploadByBase64"
SLUG = "linkfox-aigc-multi-image-edit"


def main():
    return run_entry(API_PATH, force_no_cache=False)


if __name__ == "__main__":
    main()
