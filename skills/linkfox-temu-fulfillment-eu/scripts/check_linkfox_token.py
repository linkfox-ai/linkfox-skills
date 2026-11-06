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
    result = call_temu_api(PROXY_URL, probe_body, timeout=150, linkfox_params=params)

    if is_linkfox_auth_error(result):
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid",
                    "message": result.get("message") or result,
                    "response": result,
                    "hint": "Set LINKFOXAGENT_API_KEY or pass token in JSON.",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    http_status = result.get("_http_status")
    errcode = result.get("errcode")
    if isinstance(errcode, str):
        errcode = errcode.strip()
        if errcode.isascii() and errcode.isdigit():
            errcode = int(errcode)
    normal_errcode = errcode is None or errcode == "" or (
        type(errcode) in (int, float) and 200 <= errcode < 300
    )
    if http_status is None or not 200 <= http_status < 300 or not normal_errcode:
        print(json.dumps({
            "ok": False,
            "reason": "gateway_probe_failed",
            "gatewayReachable": http_status is not None,
            "response": result,
        }, indent=2, ensure_ascii=False))
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
