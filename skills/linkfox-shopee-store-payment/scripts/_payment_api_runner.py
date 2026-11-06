"""Run any Shopee Payment module API via developerProxy."""

from __future__ import annotations

import json
import sys
from typing import Any, List, Optional

from _payment_endpoints import LIST_QUERY_FIELDS, PAYMENT_ENDPOINTS, RESERVED_PARAM_KEYS
from _shopee_payment_common import (
    developer_proxy_call,
    ensure_auth_skill_available,
    merge_shopee_body,
    normal_gateway_response,
    qs_add,
)


def main_for_api(api_name=None) -> None:
    """保留位置 JSON CLI，帮助和参数错误均不触发网络。"""
    args = sys.argv[1:]
    if not args or args[0] in ("--help", "-h"):
        print(f"用法: {sys.argv[0]} '<JSON 参数>' [--inline] [--no-cache]")
        if api_name is None:
            print("api 可选值: " + ", ".join(sorted(PAYMENT_ENDPOINTS)))
        if not args:
            raise SystemExit(1)
        return
    if any(arg not in ("--inline", "--no-cache") for arg in args[1:]):
        print("未知 CLI 选项", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        raise SystemExit(1)
    chosen = api_name or params.get("api")
    if not chosen:
        print("Missing required field: api", file=sys.stderr)
        raise SystemExit(1)
    run_payment_api(str(chosen), params, sys.argv[0])


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


def _normalize_list_fields(params: dict) -> None:
    for field in LIST_QUERY_FIELDS:
        if field in params:
            params[field] = _comma_join_list(params[field], field, 50)


def _build_get_query(params: dict) -> str:
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

    if not body_obj:
        print(
            "POST requires 'body' / 'requestBody' or documented body fields in params",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))


def run_payment_api(api_name: str, params: dict, caller: Optional[str] = None) -> dict:
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        sys.exit(1)
    params = dict(params)
    if api_name not in PAYMENT_ENDPOINTS:
        print(f"Unknown api: {api_name}. Valid: {', '.join(sorted(PAYMENT_ENDPOINTS))}", file=sys.stderr)
        sys.exit(1)

    spec = PAYMENT_ENDPOINTS[api_name]
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
        query_string = _build_get_query(params)
    else:
        body = _build_post_body(params, spec)

    shop_id = params.get("shopId")
    merchant_id = params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)

    # 在请求前解析 POST JSON，避免请求已提交后才发现格式错误。
    body_obj = None
    if body is not None:
        try:
            body_obj = json.loads(body)
        except (TypeError, json.JSONDecodeError):
            print("body / requestBody 必须为合法 JSON", file=sys.stderr)
            sys.exit(1)

    def format_result(status, proxy):
        out: dict = {
            "api": api_name,
            "developerProxy": proxy,
            "resolvedPath": path,
            "transportHttpStatus": status,
        }
        if query_string:
            out["queryString"] = query_string
        if body is not None:
            out["requestBody"] = body_obj
        if normal_gateway_response(status, proxy):
            merge_shopee_body(out, proxy, response_key)
        return out

    return developer_proxy_call(
        path,
        method,
        shop_id=shop_id,
        merchant_id=merchant_id,
        query_string=query_string or None,
        body=body,
        content_type=content_type,
        transform=format_result,
        operation=api_name,
    )
