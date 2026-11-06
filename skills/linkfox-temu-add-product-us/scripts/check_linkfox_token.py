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
    PROXY_URL, call_temu_api, get_linkfox_token, is_linkfox_auth_error,
    is_gateway_response_normal, load_json_arg,
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

    status = result.get("transportHttpStatus")
    # probe 仅能接受已到达网关的正常响应或预期参数错误，不能把连接失败当作成功。
    code = result.get("code")
    expected_business_code = is_gateway_response_normal({
        "transportHttpStatus": 200, "errcode": code,
    }) or (type(code) is int and code == 1002) or (
        isinstance(code, str) and code.strip() == "1002"
    )
    if (is_linkfox_auth_error(result) or not is_gateway_response_normal(result)
            or result.get("error") or not expected_business_code):
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid" if is_linkfox_auth_error(result) or status == 401 else "gateway_probe_failed",
                    "message": result.get("message") or result.get("errmsg") or result,
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
