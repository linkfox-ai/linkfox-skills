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
from _temu_runtime import take_output


def probe_accepted(result):
    """外层正常且未命中认证错误时，才识别正常返回或预期参数探测。"""
    status = result.get("transportHttpStatus")
    if not isinstance(status, int) or not 200 <= status < 300 or is_linkfox_auth_error(result):
        return False
    errcode = result.get("errcode")
    if isinstance(errcode, str):
        errcode = errcode.strip()
        if errcode.isascii() and errcode.isdigit():
            errcode = int(errcode)
    normal = errcode is None or errcode == "" or (
        type(errcode) in (int, float) and 200 <= errcode < 300 and errcode % 1 == 0
    )
    code = result.get("code")
    return normal and (code is None or code == "" or code in (1002, "1002", 200, "200")) and not result.get("error")

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
    take_output(result)  # 原始响应已落盘；本 CLI 保留自己的脱敏输出格式。

    if not probe_accepted(result):
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid" if is_linkfox_auth_error(result) else "gateway_probe_failed",
                    "gatewayReachable": result.get("transportHttpStatus") is not None,
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
