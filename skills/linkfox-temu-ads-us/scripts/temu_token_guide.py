#!/usr/bin/env python3
"""
Temu accessToken authorization guide - LinkFox Skill
按店铺类型返回与 references/access-token.md 对应的后台授权步骤。

Usage:
  python temu_token_guide.py '{"shopType":"semi-managed","tokenPurpose":"product-inventory","site":"cn"}'
  python temu_token_guide.py '{"shopType":"semi-managed","tokenPurpose":"order-shipping","site":"us"}'
  python temu_token_guide.py '{"shopType":"full-managed"}'
  python temu_token_guide.py '{"shopType":"local-native"}'
"""

import json
import sys

from _temu_auth_guide import build_guide

def main():
    if len(sys.argv) < 2:
        print("Usage: temu_token_guide.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: temu_token_guide.py \'{"shopType":"semi-managed",'
            '"tokenPurpose":"product-inventory","site":"cn"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    shop_type = params.get("shopType") or params.get("managementType")
    if not shop_type:
        print("Error: 'shopType' is required.", file=sys.stderr)
        sys.exit(1)

    token_purpose = params.get("tokenPurpose", "default")
    site = params.get("site")

    try:
        guide = build_guide(shop_type, token_purpose, site)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(guide, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
