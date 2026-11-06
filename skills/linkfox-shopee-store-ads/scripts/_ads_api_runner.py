"""Shopee 广告参数映射、请求体校验与兼容结果加工。"""

from __future__ import annotations

import json
import sys
from typing import Any, List, Optional

from _ads_endpoints import LIST_QUERY_FIELDS, ADS_ENDPOINTS, RESERVED_PARAM_KEYS
from _shopee_ads_common import (
    build_proxy_params,
    ensure_auth_skill_available,
    is_normal_response,
    merge_shopee_body,
    qs_add,
    run_proxy,
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


def run_ads_api(api_name: str, params: dict, caller: Optional[str] = None, *, emit: bool = False, inline: bool = False) -> dict:
    if not isinstance(params, dict):
        raise ValueError("JSON 参数必须为对象")
    if "accessToken" in params or "appType" in params:
        raise ValueError("禁止向 developerProxy 传 accessToken 或 appType；请先确认 AD 授权")
    if api_name not in ADS_ENDPOINTS:
        print(f"Unknown api: {api_name}. Valid: {', '.join(sorted(ADS_ENDPOINTS))}", file=sys.stderr)
        sys.exit(1)

    spec = ADS_ENDPOINTS[api_name]
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
        # 发送前解析，避免广告写入已发生才因非法 JSON 退出。
        body_obj = json.loads(body)
        if isinstance(body_obj, dict) and ({"accessToken", "appType"} & body_obj.keys()):
            raise ValueError("广告 body 禁止包含 accessToken 或 appType")

    shop_id = params.get("shopId")
    merchant_id = params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)

    request = build_proxy_params(
        path,
        method,
        shop_id=shop_id,
        merchant_id=merchant_id,
        query_string=query_string or None,
        body=body,
        content_type=content_type,
    )

    def transform(http_status, proxy):
        out = {
            "api": api_name,
            "developerProxy": proxy,
            "resolvedPath": path,
            "transportHttpStatus": http_status,
        }
        if query_string:
            out["queryString"] = query_string
        if body is not None:
            out["requestBody"] = body_obj
        if is_normal_response(http_status, proxy):
            merge_shopee_body(out, proxy, response_key)
        return out

    return run_proxy(request, api_name, transform, emit=emit, inline=inline)


def cli_main(api_name: Optional[str] = None) -> None:
    """独立脚本和通用入口共享 JSON CLI，并支持统一输出选项。"""
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print("用法：python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]")
        if api_name is None:
            print("通用入口必须提供 api；可用值：" + ", ".join(sorted(ADS_ENDPOINTS)))
        return
    params_args = [arg for arg in args if arg not in ("--inline", "--no-cache")]
    if len(params_args) != 1:
        print("用法：python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(params_args[0])
        if not isinstance(params, dict):
            raise ValueError("JSON 参数必须为对象")
        selected = api_name or params.get("api")
        if not selected:
            raise ValueError("Missing required field: api")
        run_ads_api(str(selected), params, sys.argv[0], emit=True, inline="--inline" in args)
    except (ValueError, TypeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
