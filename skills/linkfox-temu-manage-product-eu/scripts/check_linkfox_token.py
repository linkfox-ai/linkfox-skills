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

    status = result.get("transportHttpStatus")
    errcode = result.get("errcode")
    errcode_empty = errcode is None or isinstance(errcode, str) and not errcode.strip()
    errcode_ok = errcode_empty or (
        type(errcode) in (int, float) and 200 <= errcode < 300 and errcode % 1 == 0
    ) or (
        isinstance(errcode, str) and errcode.strip().isascii()
        and errcode.strip().isdigit() and 200 <= int(errcode.strip()) < 300
    )
    transport_ok = type(status) is int and 200 <= status < 300 and errcode_ok and not result.get("error")
    if is_linkfox_auth_error(result) or not transport_ok:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid" if is_linkfox_auth_error(result) else "gateway_probe_failed",
                    "message": result.get("message") or result,
                    "hint": "Set LINKFOXAGENT_API_KEY or pass token in JSON.",
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
                "gatewayReachable": transport_ok,
                "note": "LinkFox user Token accepted by gateway.",
            },
            indent=2,
            ensure_ascii=False,
        )
    )

if __name__ == "__main__":
    main()
