#!/usr/bin/env python3
"""EU / Partner seller cancel-order API helpers; local gateway helpers."""

import json

from _temu_common import (
    FILE_DOWNLOAD_URL,
    PROXY_URL,
    call_temu_api,
    emit_result,
    lf_inline_flag,
    load_json_arg,
    parse_nested_body,
    resolve_access_token,
)

# Partner EU 取消订单（买家+卖家）接口：默认欧洲站半托管 + 订单 token
DEFAULT_SITE = "eu"
DEFAULT_MANAGEMENT_TYPE = "semi-managed"
DEFAULT_TOKEN_PURPOSE = "order-shipping"

RESERVED_KEYS = frozenset(
    {
        "token",
        "linkfoxToken",
        "linkfox_token",
        "accessToken",
        "storeKey",
        "site",
        "managementType",
        "tokenPurpose",
        "type",
        "params",
    }
)

def extract_business_params(params: dict) -> dict:
    if isinstance(params.get("params"), dict):
        return dict(params["params"])
    return {k: v for k, v in params.items() if k not in RESERVED_KEYS}

def build_eu_proxy_body(params: dict, api_type: str, business=None) -> dict:
    site = str(params.get("site", DEFAULT_SITE)).strip().lower() or DEFAULT_SITE
    management_type = (
        str(params.get("managementType", DEFAULT_MANAGEMENT_TYPE)).strip().lower()
        or DEFAULT_MANAGEMENT_TYPE
    )
    if "tokenPurpose" not in params and params.get("storeKey") and not params.get("accessToken"):
        params = dict(params)
        params.setdefault("tokenPurpose", DEFAULT_TOKEN_PURPOSE)
        params.setdefault("site", site)
        params.setdefault("managementType", management_type)

    body = {
        "site": site,
        "managementType": management_type,
        "accessToken": resolve_access_token(params),
        "type": api_type,
    }
    biz = business if business is not None else extract_business_params(params)
    if biz:
        body["params"] = biz
    return body

def eu_proxy_call(params: dict, api_type: str, business=None, timeout: int = 60) -> dict:
    body = build_eu_proxy_body(params, api_type, business)
    return call_temu_api(PROXY_URL, body, timeout=timeout, linkfox_params=params)

def eu_file_download_call(params: dict, timeout: int = 120) -> dict:
    if "tokenPurpose" not in params and params.get("storeKey") and not params.get("accessToken"):
        params = dict(params)
        params.setdefault("tokenPurpose", DEFAULT_TOKEN_PURPOSE)

    from _temu_common import require_text  # noqa: E402

    site = str(params.get("site", DEFAULT_SITE)).strip().lower() or DEFAULT_SITE
    management_type = (
        str(params.get("managementType", DEFAULT_MANAGEMENT_TYPE)).strip().lower()
        or DEFAULT_MANAGEMENT_TYPE
    )
    body = {
        "site": site,
        "managementType": management_type,
        "accessToken": resolve_access_token(params),
        "url": require_text(params, "url"),
    }
    return call_temu_api(FILE_DOWNLOAD_URL, body, timeout=timeout, linkfox_params=params)

def run_and_print(params: dict, api_type: str, business=None) -> None:
    result = parse_nested_body(eu_proxy_call(params, api_type, business))
    emit_result(result, inline=lf_inline_flag())
