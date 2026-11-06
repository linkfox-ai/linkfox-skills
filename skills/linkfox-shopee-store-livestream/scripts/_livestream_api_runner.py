"""Run any Shopee Livestream module API via developerProxy."""

from __future__ import annotations

import json
import sys
from typing import Any, List, Optional

from _livestream_endpoints import LIST_QUERY_FIELDS, LIVESTREAM_ENDPOINTS, RESERVED_PARAM_KEYS
from _shopee_livestream_common import (
    developer_proxy_call,
    ensure_auth_skill_available,
    is_normal_response,
    merge_shopee_body,
    qs_add,
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


def run_livestream_api(api_name: str, params: dict, caller: Optional[str] = None, *, emit=False, inline=False) -> dict:
    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        raise SystemExit(1)
    if api_name not in LIVESTREAM_ENDPOINTS:
        print(f"Unknown api: {api_name}. Valid: {', '.join(sorted(LIVESTREAM_ENDPOINTS))}", file=sys.stderr)
        sys.exit(1)

    spec = LIVESTREAM_ENDPOINTS[api_name]
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

    def build_result(http_status, proxy):
        out = {
            "api": api_name,
            "developerProxy": proxy,
            "resolvedPath": path,
            "transportHttpStatus": http_status,
        }
        if query_string:
            out["queryString"] = query_string
        if body is not None:
            try:
                out["requestBody"] = json.loads(body) if body else None
            except json.JSONDecodeError:
                out["requestBody"] = body
        if is_normal_response(http_status, proxy):
            merge_shopee_body(out, proxy, response_key)
        return out

    return developer_proxy_call(
        path, method, shop_id=shop_id, merchant_id=merchant_id,
        query_string=query_string or None, body=body, content_type=content_type,
        result_builder=build_result, emit=emit, inline=inline, operation=api_name,
    )


def cli(api_name: Optional[str] = None) -> None:
    """保留 JSON CLI，统一提供完整落盘、摘要及 --inline。"""
    import argparse
    parser = argparse.ArgumentParser(description="Shopee 店铺直播操作")
    parser.add_argument("params", help="JSON 对象；通用入口需包含 api 字段")
    parser.add_argument("--inline", action="store_true", help="完整输出响应")
    parser.add_argument("--no-cache", action="store_true", help="保持无缓存行为（始终启用）")
    args = parser.parse_args()
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        parser.error(f"JSON 参数格式错误：{exc}")
    if not isinstance(params, dict):
        parser.error("JSON 参数必须是对象")
    operation = api_name or params.get("api")
    if not operation:
        parser.error("缺少 api；可用值：" + ", ".join(sorted(LIVESTREAM_ENDPOINTS)))
    run_livestream_api(str(operation), params, caller=sys.argv[0], emit=True, inline=args.inline)
