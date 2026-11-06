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
from decimal import Decimal, InvalidOperation

from _temu_common import PROXY_URL, call_temu_api, get_linkfox_token, is_linkfox_auth_error, load_json_arg

def probe_accepted(result: dict) -> bool:
    """参数错误只能作为探测线索，不能覆盖 HTTP、身份或其他 errcode 错误。"""
    status = result.get("transportHttpStatus")
    if (type(status) is not int or not 200 <= status < 300
            or is_linkfox_auth_error(result)):
        return False
    errcode = result.get("errcode")
    if result.get("code", errcode) not in (1002, "1002"):
        return False
    # 认证探测兼容 errcode 中的参数错误；这一特例不能视为业务成功。
    if errcode in (1002, "1002"):
        return True
    if errcode is None or isinstance(errcode, str) and not errcode.strip():
        return True
    if isinstance(errcode, bool) or not isinstance(errcode, (int, float, str)):
        return False
    try:
        code = Decimal(str(errcode).strip())
        return code.is_finite() and 200 <= code < 300
    except InvalidOperation:
        return False


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

    if not probe_accepted(result):
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid" if is_linkfox_auth_error(result) else "probe_inconclusive",
                    "message": result.get("message") or result.get("errmsg") or result,
                    "hint": "核对响应状态；设置 LINKFOX_AGENT_API_KEY 或在 JSON 中传 token。",
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
