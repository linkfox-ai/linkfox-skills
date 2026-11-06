#!/usr/bin/env python3
"""创建商品营销套图；支持 JSON CLI 和会话输出。"""
from _aigc_runtime import (
    SLUG, _ensure_session, _update_meta, get_api_key, resolve_data_path, run_entry,
)

API_PATH = "/aigc/productMarketMaterial"


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
        list_models("image", 71, SLUG, resolve_data_path, inline, allowed)
        return 0

    return run_entry(API_PATH)


if __name__ == "__main__":
    main()
