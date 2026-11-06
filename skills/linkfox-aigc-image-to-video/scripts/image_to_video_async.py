#!/usr/bin/env python3
"""创建图转视频任务；保留 JSON/--inline/--no-cache CLI 与 24h 缓存。"""
from _aigc_common import run, get_api_key
from call_api import resolve_data_path

API_PATH = "/aigc/imageToVideo"
SLUG = "linkfox-aigc-image-to-video"


def main():
    import sys
    from model_catalog import list_models, parse_model_args
    args = sys.argv[1:]
    try:
        listing, inline, allowed = parse_model_args(args)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2) from error
    if listing:
        list_models("video", 30, SLUG, resolve_data_path, inline, allowed)
        return 0

    run(API_PATH, "image-to-video")


if __name__ == "__main__":
    main()
