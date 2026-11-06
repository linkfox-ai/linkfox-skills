#!/usr/bin/env python3
"""创建单图智能修图任务；支持 JSON、--inline、--no-cache CLI。"""
from _aigc_api import run_entry, get_api_key, get_api_base, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/imageEdit"
SLUG = "linkfox-aigc-image-edit"


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
        list_models("image", 61, SLUG, resolve_data_path, inline, allowed)
        return 0

    return run_entry(API_PATH)


if __name__ == "__main__":
    main()
