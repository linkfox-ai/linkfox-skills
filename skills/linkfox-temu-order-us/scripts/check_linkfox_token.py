#!/usr/bin/env python3
"""
Check LinkFox user Token before calling Temu gateway APIs.
Same role as LINKFOXAGENT_API_KEY in linkfox-amazon-store-auth.

Usage:
  python check_linkfox_token.py
  python check_linkfox_token.py '{"token": "your-linkfox-key"}'
"""

import json
import sys

from _temu_common import (
    PROXY_URL, call_temu_api, gateway_http_status, get_linkfox_token,
    is_gateway_response_ok, is_linkfox_auth_error, load_json_arg,
)

def main():
    params = load_json_arg(sys.argv) if len(sys.argv) >= 2 else {}
    linkfox_token = get_linkfox_token(params)
    masked = (
        linkfox_token[:6] + "..." + linkfox_token[-4:]
        if len(linkfox_token) > 12
        else "***"
    )

    # 最小探测请求：LinkFox Token 有效时应返回业务/参数类 1002，而非「无法识别当前用户」
    probe_body = {
        "site": "cn",
        "managementType": "full-managed",
        "accessToken": "probe",
        "type": "probe",
    }
    result = call_temu_api(PROXY_URL, probe_body, timeout=150, linkfox_params=params)

    auth_error = is_linkfox_auth_error(result)
    if auth_error or not is_gateway_response_ok(result) or result.get("code") in (1003, "1003"):
        status = gateway_http_status(result)
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid" if auth_error else "gateway_check_failed",
                    "message": (result.get("message") or result) if isinstance(result, dict) else result,
                    "transportHttpStatus": status,
                    "gatewayReachable": status is not None,
                    "hint": (
                        "Set LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY or pass token in JSON."
                        if auth_error else "Check gateway, billing, permissions and connection; token validity is unconfirmed."
                    ),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    print(
        json.dumps(
            {
                "ok": True,
                "linkfoxToken": masked,
                "gatewayReachable": True,
                "note": "LinkFox user Token accepted by gateway.",
            },
            indent=2,
            ensure_ascii=False,
        )
    )

if __name__ == "__main__":
    main()
