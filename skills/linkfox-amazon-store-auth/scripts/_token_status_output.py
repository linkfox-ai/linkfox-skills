#!/usr/bin/env python3
"""授权状态输出与旧网关令牌脱敏。"""
import json
import sys

STATUS_FIELDS = (
    "status",
    "tokenExpiresAt",
    "expireIn",
    "expiresIn",
    "authRecordId",
    "message",
    "accessTokenExpireIn",
    "refreshTokenExpireIn",
    "userType",
    "grantedScopes",
    "errcode",
    "errmsg",
)


def strip_raw_tokens(result: dict) -> dict:
    if isinstance(result, dict):
        return {key: strip_raw_tokens(value) for key, value in result.items()
                if key not in ("accessToken", "refreshToken", "access_token", "refresh_token")}
    if isinstance(result, list):
        return [strip_raw_tokens(value) for value in result]
    return result


def print_status_note(result: dict) -> None:
    if result.get("error"):
        return
    print("\n✓ 已获取授权状态。", file=sys.stderr)
    for key in STATUS_FIELDS:
        if key in result and result[key] is not None:
            print(f"  {key}: {result[key]}", file=sys.stderr)
    print(
        "说明：响应只用于状态与元数据。 "
        "下游使用账号选择信息（sellerId+region 等）"
        "调用 developerProxy，不获取 raw token。",
        file=sys.stderr,
    )
