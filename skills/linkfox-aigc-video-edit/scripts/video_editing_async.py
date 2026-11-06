#!/usr/bin/env python3
"""videoEditing 业务入口；参数与运行约定见 references。"""
from _video_runtime import run, get_api_key, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/videoEditing"
SLUG = "linkfox-aigc-video-edit"

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
        list_models("video", 95, SLUG, resolve_data_path, inline, allowed)
        return 0

    return run(API_PATH, SLUG + "-videoEditing", force_no_cache=False)

if __name__ == "__main__":
    main()
