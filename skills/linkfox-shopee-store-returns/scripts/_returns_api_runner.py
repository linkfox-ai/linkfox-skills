"""退货退款参数映射、响应加工和统一 CLI。"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, List, Optional

from _returns_endpoints import LIST_QUERY_FIELDS, RETURNS_ENDPOINTS, RESERVED_PARAM_KEYS
from _shopee_returns_common import (
    developer_proxy_call,
    gateway_ok,
    SLUG,
    ensure_auth_skill_available,
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
        print(f"{field} 必须为 string 或 string[]", file=sys.stderr)
        sys.exit(1)
    if not items:
        print(f"{field} 不能为空", file=sys.stderr)
        sys.exit(1)
    if len(items) > max_items:
        print(f"{field} 最多支持 {max_items} 个值", file=sys.stderr)
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
            "POST 需要 body / requestBody 或已配置的 body_fields 字段",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))


def run_returns_api(api_name: str, params: dict, caller: Optional[str] = None) -> dict:
    if api_name not in RETURNS_ENDPOINTS:
        print(f"未知 api： {api_name}. 可用操作： {', '.join(sorted(RETURNS_ENDPOINTS))}", file=sys.stderr)
        sys.exit(1)

    spec = RETURNS_ENDPOINTS[api_name]
    for field in spec.get("required") or []:
        if field not in params or params[field] is None or params[field] == "":
            print(f"缺少必填字段： {field}", file=sys.stderr)
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

    if body is not None:
        try:
            body_obj = json.loads(body) if body else None
        except json.JSONDecodeError as exc:
            print(f"body / requestBody 必须为合法 JSON：{exc}", file=sys.stderr)
            raise SystemExit(1)

    shop_id = params.get("shopId")
    merchant_id = params.get("merchantId")
    if not shop_id and not merchant_id:
        print("缺少必填字段： shopId OR merchantId", file=sys.stderr)
        sys.exit(1)

    def transform(status, proxy):
        out = {
            "api": api_name,
            "developerProxy": proxy,
            "resolvedPath": path,
            "transportHttpStatus": status,
        }
        if query_string:
            out["queryString"] = query_string
        if body is not None:
            out["requestBody"] = body_obj
        if gateway_ok(status, proxy):
            merge_shopee_body(out, proxy, response_key)
        return out

    return developer_proxy_call(
        path, method, shop_id=shop_id, merchant_id=merchant_id,
        query_string=query_string or None, body=body, content_type=content_type,
        transform=transform, slug=f"{SLUG}-{api_name}",
    )


def run_cli(api_name=None):
    parser = argparse.ArgumentParser(description="Shopee 店铺退货退款；完整字段见 references/apis/。")
    parser.add_argument("params", help="JSON 对象；通用入口须包含 api 字段")
    parser.add_argument("--inline", action="store_true", help="保存并打印完整响应")
    parser.add_argument("--no-cache", action="store_true", help="业务封装始终禁用响应缓存")
    args = parser.parse_args()
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        parser.error(f"JSON 参数无效：{exc}")
    if not isinstance(params, dict):
        parser.error("参数必须为 JSON 对象")
    selected = api_name or params.get("api")
    if not selected:
        parser.error("通用入口缺少 api 字段")
    run_returns_api(str(selected), params, f"{api_name or 'returns_api'}.py")
