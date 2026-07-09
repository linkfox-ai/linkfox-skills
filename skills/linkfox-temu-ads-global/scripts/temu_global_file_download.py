#!/usr/bin/env python3
"""US site signed file download via /temu/fileDownload."""

import json
import sys

from _temu_common import load_json_arg
from _temu_global_common import DEFAULT_SITE, global_file_download_call
from _temu_global_common import emit_result, lf_inline_flag

def main():
    if len(sys.argv) < 2:
        print(
            'Usage: temu_global_file_download.py \'{"accessToken":"...","url":"https://..."}\'',
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    result = global_file_download_call(params)
    emit_result(result, inline=lf_inline_flag())

if __name__ == "__main__":
    main()
