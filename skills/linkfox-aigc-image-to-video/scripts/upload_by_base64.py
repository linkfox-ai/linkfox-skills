#!/usr/bin/env python3
"""Base64 上传低层入口；优先使用 upload_file.py 在进程内编码。"""
from _aigc_common import run, get_api_key

API_PATH = "/aigc/uploadByBase64"
SLUG = "linkfox-aigc-image-to-video"


def main():
    run(API_PATH, "upload")


if __name__ == "__main__":
    main()
