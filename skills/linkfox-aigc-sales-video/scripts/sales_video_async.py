#!/usr/bin/env python3
"""创建带货口播视频；支持 JSON、--inline、--no-cache 命令行与单层缓存。"""
from _linkfox_runtime import (
    run_entry, get_api_key, _ensure_session, _update_meta, resolve_data_path,
)

API_PATH = "/aigc/salesVideo"
SLUG = "linkfox-aigc-sales-video"


def main(argv=None):
    import sys
    from model_catalog import list_models, parse_model_args
    args = sys.argv[1:] if argv is None else argv
    try:
        listing, inline, allowed = parse_model_args(args)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2) from error
    if listing:
        list_models("video", 73, SLUG, resolve_data_path, inline, allowed)
        return 0

    return run_entry(API_PATH, "sales-video", argv)


if __name__ == "__main__":
    main()
