#!/usr/bin/env python3
"""欧洲站加签文件下载 via /temu/fileDownload (default site=eu)."""

import json
import sys

from _temu_common import load_json_arg
from _temu_eu_common import DEFAULT_SITE, eu_file_download_call

def main():
    if len(sys.argv) < 2:
        print(
            'Usage: temu_eu_file_download.py \'{"accessToken":"...","url":"https://..."}\'',
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    eu_file_download_call(params, display=True)

if __name__ == "__main__":
    main()
