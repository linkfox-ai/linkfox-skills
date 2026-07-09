#!/usr/bin/env python3
"""
Temu API Proxy - LinkFox Skill
Forwards Temu platform API requests via /temu/proxy.

Usage:
  export LINKFOXAGENT_API_KEY="<linkfox-user-token>"
  python temu_proxy.py '{
    "site": "cn",
    "managementType": "full-managed",
    "accessToken": "your_temu_access_token",
    "type": "bg.goods.category.mapping",
    "params": {"goodsName": "测试商品", "goodsNameEn": "Test Product"}
  }'
"""

import json
import sys

from _temu_common import (
    emit_result,
    lf_inline_flag,
    PROXY_URL,
    call_temu_api,
    load_json_arg,
    parse_nested_body,
    require_text,
    resolve_access_token,
    validate_management_type,
    validate_site,
)

def build_request(params: dict) -> dict:
    site = validate_site(require_text(params, "site"))
    management_type = validate_management_type(
        require_text(params, "managementType")
    )
    access_token = resolve_access_token(params)
    api_type = require_text(params, "type")

    body = {
        "site": site,
        "managementType": management_type,
        "accessToken": access_token,
        "type": api_type,
    }
    if "params" in params and params["params"] is not None:
        if not isinstance(params["params"], dict):
            print("Error: 'params' must be a JSON object.", file=sys.stderr)
            sys.exit(1)
        body["params"] = params["params"]
    return body

def main():
    if len(sys.argv) < 2:
        print("Usage: temu_proxy.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: temu_proxy.py \'{"site":"cn","managementType":"full-managed",'
            '"accessToken":"TOKEN","type":"bg.goods.category.mapping",'
            '"params":{"goodsName":"测试","goodsNameEn":"Test"}}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    params = load_json_arg(sys.argv)
    body = build_request(params)
    result = call_temu_api(PROXY_URL, body, linkfox_params=params)
    emit_result(parse_nested_body(result), inline=lf_inline_flag())

if __name__ == "__main__":
    main()
