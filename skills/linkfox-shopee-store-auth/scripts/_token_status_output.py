#!/usr/bin/env python3
"""授权状态响应的原始令牌剥离与元数据摘要；在任何落盘和输出前使用。"""
import sys

STATUS_FIELDS = (
    "status",
    "tokenExpiresAt",
    "expireIn",
    "expiresIn",
    "authRecordId",
    "appType",
    "shopId",
    "merchantId",
    "message",
    "accessTokenExpireIn",
    "refreshTokenExpireIn",
    "userType",
    "grantedScopes",
    "errcode",
    "errmsg",
)


def strip_raw_tokens(result):
    if isinstance(result, dict):
        return {
            key: strip_raw_tokens(value)
            for key, value in result.items()
            if key.replace("_", "").replace("-", "").lower()
            not in ("accesstoken", "refreshtoken")
        }
    if isinstance(result, list):
        return [strip_raw_tokens(value) for value in result]
    return result


def print_status_note(result: dict) -> None:
    if result.get("error"):
        return
    print("\n已读取授权状态。", file=sys.stderr)
    for key in STATUS_FIELDS:
        if key in result and result[key] is not None:
            print(f"  {key}: {result[key]}", file=sys.stderr)
    print(
        "仅展示状态和元数据，不含原始令牌。请匹配 shopId/merchantId 与 appType；"
        "developerProxy 只使用 path 与店铺或商户标识，不传 accessToken 或 appType。",
        file=sys.stderr,
    )
