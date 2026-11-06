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

from call_api import _is_cacheable
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

    if is_linkfox_auth_error(result):
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "linkfox_token_invalid",
                    "message": result.get("message") or result.get("errmsg") or result.get("error") or result,
                    "hint": "Set LINKFOXAGENT_API_KEY or pass token in JSON.",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    status = result.get("transportHttpStatus")
    errcode = result.get("errcode")
    message = " ".join(str(result.get(key) or "") for key in ("message", "error", "errmsg")).lower()
    blocked = any(text in message for text in (
        "算力不足", "算力余额不足", "计费不足", "余额不足", "配额超限", "套餐到期", "充值",
        "quota", "insufficient", "无权限", "forbidden", "permission denied",
    ))
    known_response = (
        result.get("code") in (1002, "1002", 200, "200")
        or (errcode is not None and bool(str(errcode).strip()))
        or isinstance(result.get("temuBody"), dict)
    )
    if (status is None or not 200 <= status < 300 or result.get("error") or blocked
            or not _is_cacheable(200, result)
            or result.get("code") not in (None, "", 200, "200", 1002, "1002")
            or not known_response):
        print(json.dumps({"ok": False, "reason": "gateway_check_failed", "response": result}, ensure_ascii=False, indent=2))
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
