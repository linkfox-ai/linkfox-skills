#!/usr/bin/env python3
"""多图融合任务创建；接受 JSON CLI 参数，通过公共调用器执行。"""
from _aigc_runtime import run_entry, get_api_key, _ensure_session, _update_meta, resolve_data_path

API_PATH = "/aigc/multiImageFusion"
SLUG = "linkfox-aigc-multi-image-edit"


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
        list_models("image", 62, SLUG, resolve_data_path, inline, allowed)
        return 0

    return run_entry(API_PATH, force_no_cache=False)


if __name__ == "__main__":
    main()
