#!/usr/bin/env python3
"""US site signed file download via /temu/fileDownload."""

import json
import sys

from _temu_common import load_json_arg, emit_result, lf_inline_flag
from _temu_us_common import DEFAULT_SITE, us_file_download_call

def main():
    if len(sys.argv) < 2:
        print(
            'Usage: temu_us_file_download.py \'{"accessToken":"...","url":"https://..."}\'',
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    result = us_file_download_call(params)
    inline = lf_inline_flag()
    emit_result(result, inline)

if __name__ == "__main__":
    main()
