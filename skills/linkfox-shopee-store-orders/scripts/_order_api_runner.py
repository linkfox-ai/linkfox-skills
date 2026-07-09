"""Run any Shopee Order module API via developerProxy."""

from __future__ import annotations

import json
import sys
from typing import Any, List, Optional

from _order_endpoints import ORDER_ENDPOINTS, ORDER_STATUS_VALUES, RESERVED_PARAM_KEYS
from _shopee_orders_common import (
    developer_proxy_call,
    ensure_auth_skill_available,
    merge_shopee_body,
    qs_add,
    resolve_store_tokens,
)


def _comma_join_list(val: object, field: str, max_items: int) -> str:
    items: List[str] = []
    if isinstance(val, str):
        items = [x.strip() for x in val.split(",") if x.strip()]
    elif isinstance(val, list):
        items = [str(x).strip() for x in val if str(x).strip()]
    else:
        print(f"{field} must be string or string[]", file=sys.stderr)
        sys.exit(1)
    if not items:
        print(f"{field} cannot be empty", file=sys.stderr)
        sys.exit(1)
    if len(items) > max_items:
        print(f"{field} supports at most {max_items} values", file=sys.stderr)
        sys.exit(1)
    return ",".join(items)


def _validate_get_order_list(params: dict) -> None:
    trf = str(params.get("time_range_field", "")).strip()
    if trf not in ("create_time", "update_time"):
        print("time_range_field must be create_time or update_time", file=sys.stderr)
        sys.exit(1)
    page_size = int(params["page_size"])
    if page_size < 1 or page_size > 100:
        print("page_size must be between 1 and 100", file=sys.stderr)
        sys.exit(1)
    status = params.get("order_status")
    if status:
        status = str(status).strip().upper()
        if status not in ORDER_STATUS_VALUES:
            print(f"Invalid order_status: {status}", file=sys.stderr)
            sys.exit(1)
        params["order_status"] = status


def _normalize_list_fields(params: dict) -> None:
    if "order_sn_list" in params:
        params["order_sn_list"] = _comma_join_list(params["order_sn_list"], "order_sn_list", 50)
    if "package_number_list" in params:
        params["package_number_list"] = _comma_join_list(
            params["package_number_list"], "package_number_list", 50
        )
    if "booking_sn_list" in params:
        params["booking_sn_list"] = _comma_join_list(params["booking_sn_list"], "booking_sn_list", 50)


def _build_get_query(params: dict, api_name: str) -> str:
    if api_name == "get_order_list":
        _validate_get_order_list(params)
    _normalize_list_fields(params)

    parts: list[str] = []
    for key, val in params.items():
        if key in RESERVED_PARAM_KEYS or val is None:
            continue
        if isinstance(val, bool):
            qs_add(parts, key, str(val).lower())
        elif isinstance(val, (dict, list)):
            continue
        else:
            qs_add(parts, key, str(val))
    return "&".join(parts)


def _build_post_body(params: dict, spec: dict) -> str:
    if "body" in params:
        body = params["body"]
        if isinstance(body, str):
            return body
        return json.dumps(body, ensure_ascii=False, separators=(",", ":"))

    if "requestBody" in params:
        rb = params["requestBody"]
        if isinstance(rb, str):
            return rb
        return json.dumps(rb, ensure_ascii=False, separators=(",", ":"))

    body_obj: dict[str, Any] = {}
    for key in spec.get("body_fields") or []:
        if key in params and params[key] is not None:
            body_obj[key] = params[key]

    for key in spec.get("body_nested_keys") or []:
        if key in params and params[key] is not None:
            body_obj[key] = params[key]

    if not body_obj:
        print(
            "POST requires 'body' / 'requestBody' or documented body fields in params",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))


def run_order_api(api_name: str, params: dict, caller: Optional[str] = None) -> dict:
    if api_name not in ORDER_ENDPOINTS:
        print(f"Unknown api: {api_name}. Valid: {', '.join(sorted(ORDER_ENDPOINTS))}", file=sys.stderr)
        sys.exit(1)

    spec = ORDER_ENDPOINTS[api_name]
    for field in spec.get("required") or []:
        if field not in params or params[field] is None or params[field] == "":
            print(f"Missing required field: {field}", file=sys.stderr)
            sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available(caller or f"{api_name}.py")

    method = spec["method"]
    path = spec["path"]
    response_key = spec["response_key"]

    query_string: Optional[str] = None
    body: Optional[str] = None
    content_type = str(params.get("contentType") or "application/json")

    if method == "GET":
        query_string = _build_get_query(params, api_name)
    else:
        body = _build_post_body(params, spec)

    tokens = resolve_store_tokens(params)
    if "error" in tokens or "accessToken" not in tokens:
        return tokens

    proxy = developer_proxy_call(
        tokens["accessToken"],
        path,
        method,
        shop_id=params.get("shopId"),
        merchant_id=params.get("merchantId"),
        query_string=query_string,
        body=body,
        content_type=content_type,
    )

    out: dict = {
        "api": api_name,
        "developerProxy": proxy,
        "resolvedPath": path,
    }
    if query_string:
        out["queryString"] = query_string
    if body is not None:
        out["requestBody"] = json.loads(body) if body else None

    merge_shopee_body(out, proxy, response_key)
    return out
