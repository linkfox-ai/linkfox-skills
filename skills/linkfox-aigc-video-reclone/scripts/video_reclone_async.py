#!/usr/bin/env python3
"""创建商品视频复刻任务，保留 JSON、--inline、--no-cache 命令行入口。"""
from _aigc_runtime import run_entry, get_api_key, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/videoReclone"
SLUG = "linkfox-aigc-video-reclone"


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
        list_models("video", 89, SLUG, resolve_data_path, inline, allowed)
        return 0

    run_entry(API_PATH)


if __name__ == "__main__":
    main()
