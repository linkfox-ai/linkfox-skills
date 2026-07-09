#!/usr/bin/env python3
"""
Temu Signed File Download - LinkFox Skill
Downloads Temu signed resource files via /temu/fileDownload.

Usage:
  python temu_file_download.py '{
    "site": "us",
    "managementType": "semi-managed",
    "accessToken": "your_temu_access_token",
    "url": "https://example.com/signed-file-url"
  }'
"""

import json
import sys

from _temu_common import (
    emit_result,
    lf_inline_flag,
    FILE_DOWNLOAD_URL,
    call_temu_api,
    load_json_arg,
    require_text,
    resolve_access_token,
    validate_management_type,
    validate_site,
)

def build_request(params: dict) -> dict:
    site = validate_site(require_text(params, "site"))
    management_type = validate_management_type(
        require_text(params, "managementType")
    )
    access_token = resolve_access_token(params)
    url = require_text(params, "url")
    return {
        "site": site,
        "managementType": management_type,
        "accessToken": access_token,
        "url": url,
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: temu_file_download.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: temu_file_download.py \'{"site":"us","managementType":"semi-managed",'
            '"accessToken":"TOKEN","url":"https://example.com/signed-file-url"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    params = load_json_arg(sys.argv)
    body = build_request(params)
    result = call_temu_api(FILE_DOWNLOAD_URL, body, timeout=120, linkfox_params=params)
    emit_result(result, inline=lf_inline_flag())

if __name__ == "__main__":
    main()
