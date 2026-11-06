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
    PROXY_URL, call_temu_api, get_linkfox_token, is_empty_or_2xx,
    is_linkfox_auth_error, load_json_arg,
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

    if is_linkfox_auth_error(result):
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid",
                    "message": result.get("message") or result,
                    "hint": "Set LINKFOXAGENT_API_KEY or pass token in JSON.",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    status = result.get("transportHttpStatus")
    parameter_code = result.get("code", result.get("errcode"))
    errcode = result.get("errcode")
    # 预期的参数错误可用于判断密钥是否被接受，但不能掩盖另一层认证/用量错误。
    if (
        type(status) is not int or not 200 <= status < 300
        or parameter_code not in (1002, "1002")
        or not (is_empty_or_2xx(errcode) or errcode in (1002, "1002"))
        or result.get("error")
    ):
        print(json.dumps({
            "ok": False,
            "reason": "linkfox_token_probe_inconclusive",
            "gatewayReachable": result.get("transportHttpStatus") is not None,
            "response": result,
            "hint": "Probe did not return the expected parameter response; inspect authentication or network errors.",
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
