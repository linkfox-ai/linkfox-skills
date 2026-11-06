"""构造 FBA 单操作请求并交给统一调用器执行。"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from _fba_endpoints import OPERATIONS, resolve_op
from _spapi_fba_common import (
    build_query,
    developer_proxy_call,
    enc_path_seg,
    ensure_auth_skill_available,
    merge_json_body,
)

RESERVED = {
    "sellerId",
    "region",
    "skipDepCheck",
    "api",
    "operation",
    "requestBody",
    "query",
    "queryString",
    "useAmazonRequestShape",
}


def _is_missing(params: dict, key: str) -> bool:
    if key not in params or params[key] is None:
        return True
    val = params[key]
    if isinstance(val, str) and not val.strip():
        return True
    if isinstance(val, (list, tuple)) and len(val) == 0:
        return True
    return False


def _fill_path(template: str, params: dict) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if _is_missing(params, key):
            raise ValueError(f"Missing path parameter: {key}")
        return enc_path_seg(params[key])

    return re.sub(r"\{(\w+)\}", repl, template)


def _normalize_marketplace_ids(params: dict) -> None:
    if _is_missing(params, "marketplaceIds") and not _is_missing(params, "marketplaceId"):
        mid = params["marketplaceId"]
        params["marketplaceIds"] = mid if isinstance(mid, list) else [mid]


def run_operation(op_name: str, params: dict, *, emit_output: bool = False) -> dict:
    if not isinstance(params, dict):
        raise ValueError("JSON parameters must be an object")
    op = resolve_op(op_name)
    amazon_op = op.get("amazonOp") or op["id"]

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available(f"{amazon_op}.py")

    for f in ("sellerId", "region"):
        if _is_missing(params, f):
            raise ValueError(f"Missing required field: {f}")

    _normalize_marketplace_ids(params)

    # special: eligibility
    if amazon_op == "getItemEligibilityPreview":
        prog = str(params.get("program", "")).upper()
        if prog not in ("INBOUND", "COMMINGLING"):
            raise ValueError("program must be INBOUND or COMMINGLING")
        params["program"] = prog
        if prog == "INBOUND" and _is_missing(params, "marketplaceIds"):
            raise ValueError("marketplaceIds (or marketplaceId) required when program=INBOUND")

    for f in op.get("required") or []:
        if _is_missing(params, f):
            raise ValueError(f"Missing required field: {f}")

    path = _fill_path(op["path"], params)

    # query
    qpairs: list[tuple[str, Any]] = []
    if isinstance(params.get("query"), dict):
        qpairs.extend(params["query"].items())
    for qk in op.get("query") or []:
        if qk in params and params[qk] is not None:
            qpairs.append((qk, params[qk]))
    # also allow raw queryString override
    qs = params.get("queryString")
    if not qs:
        qs = build_query(qpairs)

    body_str = None
    rb = None
    if op.get("body") or params.get("requestBody") is not None:
        if params.get("requestBody") is not None:
            rb = params["requestBody"]
        else:
            # remaining non-reserved, non-path, non-query fields become body
            path_keys = set(re.findall(r"\{(\w+)\}", op["path"]))
            query_keys = set(op.get("query") or [])
            rb = {}
            for k, v in params.items():
                if k in RESERVED or k in path_keys or k in query_keys:
                    continue
                rb[k] = v
            if not rb:
                rb = None
        if rb is not None:
            if not isinstance(rb, (dict, list)):
                raise ValueError("requestBody must be object or array")
            body_str = json.dumps(rb, ensure_ascii=False)

    def build_result(proxy, transport_status):
        out: dict[str, Any] = {
            "api": amazon_op,
            "developerProxy": proxy,
            "resolvedPath": path,
            "method": op["method"],
            "queryString": qs,
            "transportHttpStatus": transport_status,
        }
        if rb is not None:
            out["requestBody"] = rb
        merge_json_body(out, proxy, "payload")
        return out

    return developer_proxy_call(
        str(params["region"]),
        path,
        op["method"],
        str(params["sellerId"]),
        query_string=qs,
        body=body_str,
        result_builder=build_result,
        operation=op["id"],
        emit_output=emit_output,
    )


def main_for(op_name: str) -> None:
    if len(sys.argv) < 2:
        op = resolve_op(op_name)
        print(
            f"Usage: {op['script']} '<JSON>'\n"
            f"Required: sellerId, region"
            + (f", {', '.join(op.get('required') or [])}" if op.get("required") else "")
            + "\nOptional: requestBody, query, skipDepCheck, --inline, --no-cache",
            file=sys.stderr,
        )
        # list hint
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        run_operation(op_name, params, emit_output=True)
    except (ValueError, KeyError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def main_dispatch() -> None:
    if len(sys.argv) < 2:
        names = ", ".join(sorted(OPERATIONS.keys()))
        print(
            "Usage: fba_api.py '<JSON with api/operation field>'\n"
            f"Known operations ({len(OPERATIONS)}): {names}",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        sys.exit(1)
    op_name = params.get("api") or params.get("operation")
    if not op_name:
        print("Missing api or operation field", file=sys.stderr)
        sys.exit(1)
    try:
        run_operation(str(op_name), params, emit_output=True)
    except (ValueError, KeyError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
