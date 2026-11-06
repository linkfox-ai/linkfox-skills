#!/usr/bin/env python3
"""
Check LinkFox user Token before calling Temu gateway APIs.
Same role as LINKFOXAGENT_API_KEY in linkfox-amazon-store-auth.

Usage:
  python check_linkfox_token.py
  python check_linkfox_token.py '{"token": "your-linkfox-key"}'
"""

import json
import io
from contextlib import redirect_stdout
import sys

from _temu_common import PROXY_URL, call_temu_api, get_linkfox_token, is_linkfox_auth_error, load_json_arg

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
    response_meta = {}
    with redirect_stdout(io.StringIO()):
        result = call_temu_api(
            PROXY_URL, probe_body, timeout=150, linkfox_params=params,
            response_meta=response_meta,
        )

    status = response_meta.get("httpStatus")
    errcode = str(result.get("errcode", "")).strip()
    auth_error = status == 401 or errcode == "401" or is_linkfox_auth_error(result)
    billing_error = status == 402 or errcode == "402"
    if auth_error or not response_meta.get("normalResponse") or result.get("error"):
        if auth_error:
            reason = "linkfox_token_invalid"
        elif billing_error:
            reason = "linkfox_billing_error"
        else:
            reason = "gateway_probe_failed"
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": reason,
                    "message": result.get("message") or result.get("errmsg") or result.get("error") or result,
                    "hint": (
                        "Set LINKFOXAGENT_API_KEY or pass token in JSON; see references/onboarding.md."
                        if auth_error else
                        "See references/onboarding.md for billing errors."
                        if billing_error else
                        "Check the gateway response and network; do not automatically retry."
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
