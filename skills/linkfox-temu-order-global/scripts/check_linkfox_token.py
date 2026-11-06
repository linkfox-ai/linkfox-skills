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

    if is_linkfox_auth_error(result) or result.get("transportHttpStatus") == 401:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid",
                    "message": result.get("message") or result.get("errmsg") or result,
                    "hint": "Set LINKFOXAGENT_API_KEY or pass token in JSON.",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    if (not is_gateway_response_normal(result) or result.get("error")
            or result.get("code") not in (None, 200, "200", 1002, "1002")):
        print(json.dumps({
            "ok": False,
            "reason": "gateway_probe_failed",
            "gatewayReachable": result.get("transportHttpStatus") is not None,
            "response": result,
            "hint": "按 references/onboarding.md 处理认证或用量错误；连接错误不代表令牌有效。",
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    print(
        json.dumps(
            {
                "ok": True,
                "linkfoxToken": masked,
                "gatewayReachable": True,
                "note": "网关探测已响应；参数类 1002 不能单独证明令牌有效，也不代表 Temu 店铺授权或业务调用成功。",
            },
            indent=2,
            ensure_ascii=False,
        )
    )

if __name__ == "__main__":
    main()
