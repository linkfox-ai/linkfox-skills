"""映射 Shopee Shop 参数，经公共调用器转发并解析业务结果。"""

from __future__ import annotations

import json
import sys
from typing import Any, Optional

from _shop_endpoints import RESERVED_PARAM_KEYS, SHOP_ENDPOINTS
from _shopee_shop_common import (
    developer_proxy_call,
    emit_result,
    ensure_auth_skill_available,
    lf_inline_flag,
    merge_shopee_body,
    qs_add,
)


def _build_get_query(params: dict) -> str:
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

    if not body_obj:
        print(
            "POST requires 'body' / 'requestBody' or documented body fields in params",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))


def run_shop_api(api_name: str, params: dict, caller: Optional[str] = None) -> dict:
    if api_name not in SHOP_ENDPOINTS:
        print(f"Unknown api: {api_name}. Valid: {', '.join(sorted(SHOP_ENDPOINTS))}", file=sys.stderr)
        sys.exit(1)

    spec = SHOP_ENDPOINTS[api_name]
    if not isinstance(params, dict):
        print("参数错误：JSON 参数必须为对象", file=sys.stderr)
        sys.exit(1)
    method = spec["method"]
    body = _build_post_body(params, spec) if method == "POST" else None
    try:
        body_obj = json.loads(body) if body is not None else None
    except json.JSONDecodeError as exc:
        print(f"参数错误：POST 请求体不是有效 JSON：{exc}", file=sys.stderr)
        sys.exit(1)
    if method == "POST" and not isinstance(body_obj, dict):
        print("参数错误：POST 请求体必须为 JSON 对象", file=sys.stderr)
        sys.exit(1)
    fields = body_obj if method == "POST" else params
    for field in spec.get("required") or []:
        if field not in fields or fields[field] is None or fields[field] == "":
            print(f"Missing required field: {field}", file=sys.stderr)
            sys.exit(1)
    if api_name == "update_profile" and not any(
        k in body_obj and body_obj[k] is not None
        for k in ("shop_name", "shop_logo", "description")
    ):
        print("update_profile requires at least one of: shop_name, shop_logo, description", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available(caller or f"{api_name}.py")

    path = spec["path"]
    response_key = spec["response_key"]

    query_string: Optional[str] = None
    content_type = str(params.get("contentType") or "application/json")

    if method == "GET":
        query_string = _build_get_query(params)

    shop_id = params.get("shopId")
    merchant_id = params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)

    proxy = developer_proxy_call(
        path,
        method,
        shop_id=shop_id,
        merchant_id=merchant_id,
        query_string=query_string or None,
        body=body,
        content_type=content_type,
    )

    out: dict = {
        "api": api_name,
        "developerProxy": proxy,
        "resolvedPath": path,
        "transportHttpStatus": getattr(proxy, "transport_http_status", None),
    }
    if query_string:
        out["queryString"] = query_string
    if body is not None:
        out["requestBody"] = json.loads(body) if body else None

    merge_shopee_body(out, proxy, response_key)
    return out
