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


def is_expected_probe_response(result):
    """仅预期的参数响应可作为认证线索，外层失败不能被 code=1002 覆盖。"""
    status = result.get("transportHttpStatus")
    if type(status) is not int or not 200 <= status < 300:
        return False
    errcode = result.get("errcode")
    if "code" not in result:
        # 兼容仅用 errcode 表达旧版 1002 参数响应的网关。
        return str(errcode).strip() == "1002"
    if str(result["code"]).strip() != "1002":
        return False
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

    if not is_expected_probe_response(result):
        print(json.dumps({
            "ok": False,
            "reason": "linkfox_token_unverified",
            "gatewayReachable": result.get("transportHttpStatus") is not None,
            "message": result,
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
