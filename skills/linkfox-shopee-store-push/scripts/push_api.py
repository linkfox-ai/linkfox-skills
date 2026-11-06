#!/usr/bin/env python3
"""Shopee Push 通用入口；JSON 含 api 操作名，支持 --inline / --no-cache。"""
import json
import sys
from _push_api_runner import run_push_api
from _push_endpoints import list_api_names


def main():
    args = [a for a in sys.argv[1:] if a not in ("--inline", "--no-cache")]
    if not args:
        print(f"Usage: push_api.py '<JSON with api field>' [--inline] [--no-cache]\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(args[0])
        if not isinstance(params, dict):
            raise ValueError("JSON parameters must be an object")
    except (ValueError, TypeError) as exc:
        print(f"Invalid parameter format: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        raise SystemExit(1)
    run_push_api(str(params["api"]), params, "push_api.py")


if __name__ == "__main__":
    main()
