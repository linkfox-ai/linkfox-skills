#!/usr/bin/env python3
"""Apply status-only post-processing for token query auth scripts."""
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
    out = dict(result)
    out.pop("accessToken", None)
    out.pop("refreshToken", None)
    return out


def print_status_note(result: dict) -> None:
    if result.get("error"):
        return
    print("\n✓ Token status retrieved.", file=sys.stderr)
    for key in STATUS_FIELDS:
        if key in result and result[key] is not None:
            print(f"  {key}: {result[key]}", file=sys.stderr)
    print(
        "Note: Response is status/metadata only. "
        "Use account selectors (sellerId+region, profileId, shopId, openId, etc.) "
        "with developerProxy; do not fetch raw tokens for proxy calls.",
        file=sys.stderr,
    )
