#!/usr/bin/env python3
"""EU 加签文件下载，默认 site=eu。"""

import sys

from _temu_eu_common import DEFAULT_SITE, eu_file_download_call
from _temu_common import load_json_arg
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
