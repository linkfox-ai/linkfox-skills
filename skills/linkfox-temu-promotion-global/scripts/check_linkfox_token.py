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

import _temu_common as common
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

    if common.LAST_HTTP_STATUS == 401 or is_linkfox_auth_error(result):
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

    errcode = result.get("errcode")
    empty_code = errcode is None or (isinstance(errcode, str) and not errcode.strip())
    normal_code = (
        (type(errcode) in (int, float) and 200 <= errcode < 300 and errcode % 1 == 0)
        or (isinstance(errcode, str) and errcode.strip().isascii()
            and len(errcode.strip()) == 3 and errcode.strip().isdigit()
            and 200 <= int(errcode.strip()) < 300)
    )
    status = common.LAST_HTTP_STATUS
    probe_code = result.get("code")
    # 空对象不能证明认证有效；仅接受已知探测返回。
    expected_probe = probe_code in (1002, "1002") or (probe_code is None and normal_code)
    messages = "\n".join(
        str(result.get(key) or "") for key in ("message", "error", "errmsg", "msg")
    ).lower()
    usage_error = any(marker in messages for marker in (
        "算力余额不足", "计费不足", "余额不足", "quota exceeded",
        "insufficient balance", "套餐到期", "需充值", "请充值", "配额超限",
    ))
    if (
        status is None or not 200 <= status < 300 or result.get("error")
        or (not empty_code and not normal_code) or not expected_probe or usage_error
    ):
        print(json.dumps({
            "ok": False,
            "reason": "gateway_probe_failed",
            "message": result,
            "hint": "根据实际网关错误检查认证和连接；不要自动重试。",
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
