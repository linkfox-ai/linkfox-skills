#!/usr/bin/env python3
"""EU / Partner Promotion API helpers; local gateway helpers."""

import json

from _temu_common import FILE_DOWNLOAD_URL, PROXY_URL, call_temu_api, emit_result, lf_inline_flag, parse_nested_body, resolve_access_token

# Partner EU 促销：默认欧洲站半托管 + 商品/促销场景 token
DEFAULT_SITE = "eu"
DEFAULT_MANAGEMENT_TYPE = "semi-managed"
DEFAULT_TOKEN_PURPOSE = "product-inventory"

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

def _normalize_eu_params(params: dict) -> dict:
    """让请求体与本地令牌查找使用相同的区域和托管类型。"""
    normalized = dict(params)
    normalized["site"] = (
        str(params.get("site", DEFAULT_SITE)).strip().lower() or DEFAULT_SITE
    )
    normalized["managementType"] = (
        str(params.get("managementType", DEFAULT_MANAGEMENT_TYPE)).strip().lower()
        or DEFAULT_MANAGEMENT_TYPE
    )
    if params.get("storeKey") and not params.get("accessToken"):
        normalized.setdefault("tokenPurpose", DEFAULT_TOKEN_PURPOSE)
    return normalized

def build_eu_proxy_body(params: dict, api_type: str, business=None) -> dict:
    params = _normalize_eu_params(params)

    body = {
        "site": params["site"],
        "managementType": params["managementType"],
        "accessToken": resolve_access_token(params),
        "type": api_type,
    }
    biz = business if business is not None else extract_business_params(params)
    if biz:
        body["params"] = biz
    return body

def eu_proxy_call(params: dict, api_type: str, business=None, timeout: int = 150) -> dict:
    body = build_eu_proxy_body(params, api_type, business)
    return call_temu_api(PROXY_URL, body, timeout=timeout, linkfox_params=params)

def eu_file_download_call(params: dict, timeout: int = 150) -> dict:
    params = _normalize_eu_params(params)

    from _temu_common import require_text  # noqa: E402

    body = {
        "site": params["site"],
        "managementType": params["managementType"],
        "accessToken": resolve_access_token(params),
        "url": require_text(params, "url"),
    }
    return call_temu_api(FILE_DOWNLOAD_URL, body, timeout=timeout, linkfox_params=params)

def run_and_print(params: dict, api_type: str, business=None) -> None:
    result = parse_nested_body(eu_proxy_call(params, api_type, business))
    emit_result(result, inline=lf_inline_flag())
