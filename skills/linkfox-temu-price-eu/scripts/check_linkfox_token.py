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


def is_normal_gateway_response(result: dict) -> bool:
    """按公共响应规则判断；网关 code=1002 与外层 errcode 不同。"""
    status = result.get("transportHttpStatus")
    if type(status) is not int or not 200 <= status < 300:
        return False
    errcode = result.get("errcode")
    if errcode is None:
        return True
    if isinstance(errcode, str):
        errcode = errcode.strip()
        if not errcode:
            return True
        if len(errcode) != 3 or not errcode.isascii() or not errcode.isdigit():
            return False
        errcode = int(errcode)
    return type(errcode) in (int, float) and 200 <= errcode < 300 and errcode % 1 == 0


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
    if (auth_error or not is_normal_gateway_response(result)
            or "error" in result):
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid" if auth_error else "linkfox_token_or_gateway_error",
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
                "note": "LinkFox user Token accepted by gateway.",
            },
            indent=2,
            ensure_ascii=False,
        )
    )

if __name__ == "__main__":
    main()
