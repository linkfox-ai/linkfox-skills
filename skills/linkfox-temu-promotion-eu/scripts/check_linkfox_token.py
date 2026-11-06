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
from call_api import _is_cacheable

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
    status = result.get("transportHttpStatus")
    billing_error = status == 402 or str(result.get("errcode")).strip() == "402"
    normal = (type(status) is int and 200 <= status < 300
              and _is_cacheable(200, result)
              and not result.get("error") and str(result.get("code")) != "1003")
    if auth_error or billing_error or not normal:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": (
                        "linkfox_billing_error" if billing_error else
                        "linkfox_token_invalid" if auth_error else "gateway_request_failed"
                    ),
                    "message": result.get("message") or result,
                    "hint": (
                        "按 references/onboarding.md 处理算力或余额问题。" if billing_error else
                        "Set LINKFOXAGENT_API_KEY or pass token in JSON." if auth_error else
                        "检查网关错误与网络；认证或算力问题见 references/onboarding.md。"
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
