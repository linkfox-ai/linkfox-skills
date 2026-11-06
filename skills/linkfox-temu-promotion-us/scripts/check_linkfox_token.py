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

from _temu_common import PROXY_URL, call_temu_api, get_linkfox_token, is_linkfox_auth_error, load_json_arg, gateway_response_normal

def probe_code_ok(code):
    """1002 是探测请求预期的参数错误，其余 code 仅接受空或 2xx。"""
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        if not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and (code == 1002 or 200 <= code < 300) and code % 1 == 0

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

    code = result.get("code")
    code_ok = probe_code_ok(code)
    if is_linkfox_auth_error(result) or not gateway_response_normal(result) or not code_ok or result.get("error") or "rawResponse" in result:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid" if is_linkfox_auth_error(result) else "probe_failed",
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
                "gatewayReachable": True,
                "note": "网关可达，未明确拒绝当前 LinkFox Token；参数错误不能证明店铺授权有效。",
            },
            indent=2,
            ensure_ascii=False,
        )
    )

if __name__ == "__main__":
    main()
