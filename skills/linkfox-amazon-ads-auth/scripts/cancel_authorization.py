#!/usr/bin/env python3
"""解除当前成员的整份 Ads 授权连接；不撤销 Amazon 授权、不缓存、不重试。"""

import re
import sys
from _ads_auth_common import request, cli_params

API_PATH = "/amazonAds/cancelAuthorization"


def validate_params(params):
    if not isinstance(params, dict):
        raise ValueError("参数必须为 JSON 对象")
    auth_id = params.get("authRecordId")
    if type(auth_id) is int:
        auth_id = str(auth_id)
    if (not isinstance(auth_id, str)
            or re.fullmatch(r"[1-9][0-9]{0,18}", auth_id) is None
            or int(auth_id) > 9223372036854775807):
        raise ValueError("authRecordId 必须为Long范围内的正整数或正整数字符串；不能用profileId替代")
    return {"authRecordId": auth_id}


def call_api(params):
    return request(API_PATH, validate_params(params))


def main():
    try:
        params = validate_params(cli_params(sys.argv[1:], required=True))
    except ValueError as e:
        print(f"参数格式错误：{e}", file=sys.stderr)
        sys.exit(1)
    result = request(API_PATH, params, persist=True, inline="--inline" in sys.argv[1:])
    if result.get("error") or result.get("success") is not True:
        sys.exit(1)
    print("当前成员的目标连接已解除或原本不存在；令牌及其他成员绑定保留，未撤销 Amazon 授权。",
          file=sys.stderr)


if __name__ == "__main__":
    main()
