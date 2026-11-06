#!/usr/bin/env python3
"""创建视频翻译任务；参数与限制见 references/api.md。"""
import call_api
from call_api import get_api_key, resolve_data_path, _ensure_session, _update_meta
from _aigc_runtime import run_entry

API_PATH = "/aigc/videoTranslation"
SLUG = "linkfox-aigc-video-translate"


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
        list_models("video", 96, SLUG, resolve_data_path, inline, allowed)
        return 0

    return run_entry(API_PATH, "videoTranslation", argv, force_no_cache=False)


if __name__ == "__main__":
    main()
