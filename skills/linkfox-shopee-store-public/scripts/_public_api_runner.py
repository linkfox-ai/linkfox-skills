"""Public 操作编排、参数映射和响应解析。"""
from __future__ import annotations
import argparse
import json
import sys
from typing import Any, Optional
from _public_endpoints import LIST_QUERY_FIELDS, PUBLIC_ENDPOINTS, RESERVED_PARAM_KEYS
from _shopee_public_common import (
    SLUG, developer_proxy_call, ensure_auth_skill_available, merge_shopee_body, qs_add,
)


def _comma_join_list(val: object, field: str, max_items: int) -> str:
    if isinstance(val, str):
        items = [x.strip() for x in val.split(",") if x.strip()]
    elif isinstance(val, list):
        items = [str(x).strip() for x in val if str(x).strip()]
    else:
        print(f"{field} 必须是字符串或字符串数组", file=sys.stderr)
        raise SystemExit(1)
    if not items or len(items) > max_items:
        print(f"{field} 不能为空且最多支持 {max_items} 个值", file=sys.stderr)
        raise SystemExit(1)
    return ",".join(items)


def _normalize_list_fields(params: dict) -> None:
    for field in LIST_QUERY_FIELDS:
        if field in params:
            params[field] = _comma_join_list(params[field], field, 50)


def _build_get_query(params: dict) -> str:
    _normalize_list_fields(params)
    parts = []
    for key, val in params.items():
        if key in RESERVED_PARAM_KEYS or val is None:
            continue
        if isinstance(val, bool):
            qs_add(parts, key, str(val).lower())
        elif not isinstance(val, (dict, list)):
            qs_add(parts, key, str(val))
    return "&".join(parts)


def _build_post_body(params: dict, spec: dict) -> str:
    if "body" in params:
        body = params["body"]
        return body if isinstance(body, str) else json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    if "requestBody" in params:
        body = params["requestBody"]
        return body if isinstance(body, str) else json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    body_obj: dict[str, Any] = {}
    for key in spec.get("body_fields") or []:
        if key in params and params[key] is not None:
            body_obj[key] = params[key]
    if not body_obj:
        print("POST 需要完整 body/requestBody，或注册表明确的正文顶层字段", file=sys.stderr)
        raise SystemExit(1)
    return json.dumps(body_obj, ensure_ascii=False, separators=(",", ":"))


def run_public_api(api_name: str, params: dict, caller: Optional[str] = None, *, inline: bool = False) -> dict:
    if api_name not in PUBLIC_ENDPOINTS:
        print(f"未知 api：{api_name}；可用值：{', '.join(sorted(PUBLIC_ENDPOINTS))}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须是对象", file=sys.stderr)
        raise SystemExit(1)
    spec = PUBLIC_ENDPOINTS[api_name]
    for field in spec.get("required") or []:
        if field not in params or params[field] is None or params[field] == "":
            print(f"缺少必要字段：{field}", file=sys.stderr)
            raise SystemExit(1)
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available(caller or f"{api_name}.py")
    method, path, response_key = spec["method"], spec["path"], spec["response_key"]
    query_string = _build_get_query(params) if method == "GET" else None
    body = _build_post_body(params, spec) if method != "GET" else None
    if not params.get("shopId") and not params.get("merchantId"):
        print("缺少必要字段：shopId 或 merchantId", file=sys.stderr)
        raise SystemExit(1)

    def transform(status, proxy):
        out = {"api": api_name, "developerProxy": proxy, "resolvedPath": path, "transportHttpStatus": status}
        if query_string:
            out["queryString"] = query_string
        if body is not None:
            try:
                out["requestBody"] = json.loads(body) if body else None
            except (ValueError, TypeError):
                out["requestBody"] = body
        if isinstance(proxy, dict):
            merge_shopee_body(out, proxy, response_key)
        return out

    return developer_proxy_call(
        path, method, shop_id=params.get("shopId"), merchant_id=params.get("merchantId"),
        query_string=query_string or None, body=body,
        content_type=str(params.get("contentType") or "application/json"),
        access_token=params.get("accessToken"), transform=transform,
        slug=f"{SLUG}-{api_name}", inline=inline,
    )


def invoke_public_cli(api_name: Optional[str] = None) -> None:
    parser = argparse.ArgumentParser(description="Shopee Public 操作：" + ", ".join(sorted(PUBLIC_ENDPOINTS)))
    parser.add_argument("params", help="JSON 对象；通用入口必须包含 api")
    parser.add_argument("--inline", action="store_true", help="强制完整打印并落盘")
    parser.add_argument("--no-cache", action="store_true", help="保留兼容选项；本技能始终禁用响应缓存")
    args = parser.parse_args()
    try:
        params = json.loads(args.params)
    except ValueError as exc:
        parser.error(f"JSON 格式不正确：{exc}")
    if not isinstance(params, dict):
        parser.error("JSON 参数必须是对象")
    selected = api_name or params.get("api")
    if not selected:
        parser.error("通用入口缺少必要字段：api")
    run_public_api(str(selected), params, caller=sys.argv[0], inline=args.inline)
