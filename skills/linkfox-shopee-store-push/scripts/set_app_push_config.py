#!/usr/bin/env python3
"""设置推送配置；参数见 references/apis/set-app-push-config.md。"""
import json
import sys
from _push_api_runner import run_push_api


def main():
    args = [a for a in sys.argv[1:] if a not in ("--inline", "--no-cache")]
    if not args:
        print("Usage: set_app_push_config.py '<JSON>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(args[0])
        if not isinstance(params, dict):
            raise ValueError("JSON parameters must be an object")
    except (ValueError, TypeError) as exc:
        print(f"Invalid parameter format: {exc}", file=sys.stderr)
        raise SystemExit(1)
    run_push_api("set_app_push_config", params, "set_app_push_config.py")


if __name__ == "__main__":
    main()
