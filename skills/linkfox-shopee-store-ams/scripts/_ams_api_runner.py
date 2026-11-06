"""编排 AMS 参数，使用共享封装执行并输出结果。"""

from __future__ import annotations

import json
import sys
from typing import Any, List, Optional

from _ams_endpoints import LIST_QUERY_FIELDS, AMS_ENDPOINTS, RESERVED_PARAM_KEYS
from _shopee_ams_common import (
    developer_proxy_call,
    ensure_auth_skill_available,
    merge_shopee_body,
    qs_add,
    emit_result,
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


def run_ams_api(api_name: str, params: dict, caller: Optional[str] = None) -> dict:
    if api_name not in AMS_ENDPOINTS:
        print(f"Unknown api: {api_name}. Valid: {', '.join(sorted(AMS_ENDPOINTS))}", file=sys.stderr)
        sys.exit(1)

    spec = AMS_ENDPOINTS[api_name]
    for field in spec.get("required") or []:
        if field not in params or params[field] is None or params[field] == "":
            print(f"Missing required field: {field}", file=sys.stderr)
            sys.exit(1)

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

    # 写请求在网络调用之前验证 JSON，避免提交后才在构造输出时抛错。
    if body is not None and body:
        try:
            json.loads(body)
        except json.JSONDecodeError:
            print("POST body / requestBody 必须为合法 JSON", file=sys.stderr)
            sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available(caller or f"{api_name}.py")

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


def cli_main(api_name: Optional[str] = None) -> None:
    """专用与通用 CLI，共用参数协议并支持落盘及 --inline。"""
    from _ams_endpoints import list_api_names
    args = sys.argv[1:]
    usage = f"用法: {sys.argv[0]} '<JSON 参数>' [--inline] [--no-cache]"
    if not args or "--help" in args or "-h" in args:
        print(usage, file=sys.stdout if args else sys.stderr)
        if api_name is None:
            print("可用 api: " + ", ".join(list_api_names()))
        if not args:
            sys.exit(1)
        return
    inline = "--inline" in args
    args = [a for a in args if a not in ("--inline", "--no-cache")]
    if len(args) != 1:
        print(usage, file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        sys.exit(1)
    selected = api_name or params.get("api")
    if not isinstance(selected, str) or not selected:
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    try:
        result = run_ams_api(selected, params, sys.argv[0])
        emit_result(result, slug=f"linkfox-shopee-store-ams-{selected}", inline=inline)
    except OSError as exc:
        print(f"本地文件操作失败: {exc}", file=sys.stderr)
        sys.exit(1)
