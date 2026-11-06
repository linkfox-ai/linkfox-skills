#!/usr/bin/env python3
"""按店铺或商户身份与应用类型查询授权状态，不输出原始令牌。"""

import sys

from _shopee_auth_common import normalize_app_type, read_params, run_request
from _token_status_output import print_status_note, strip_raw_tokens


def call_api(params):
    return run_request("/shopee/storeTokens", "store-tokens", params, transform=strip_raw_tokens)


def main():
    params = read_params(
        "用法：python store_tokens.py '<JSON 参数>' [--inline] [--no-cache]\n"
        "须提供 shopId 或 merchantId；appType 可选，默认 erp。"
    )
    if not any(params.get(key) is not None and str(params[key]).strip()
               for key in ("shopId", "merchantId")):
        print("必须提供非空 shopId 或 merchantId。", file=sys.stderr)
        raise SystemExit(1)
    normalize_app_type(params)
    result = call_api(params)
    print_status_note(result)


if __name__ == "__main__":
    main()
