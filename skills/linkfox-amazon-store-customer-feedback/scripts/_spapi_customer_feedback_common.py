"""Shared helpers for linkfox-amazon-store-customer-feedback (Customer Feedback API v2024-06-01)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import call_api as api
from pathlib import Path
from typing import Iterable, Optional

from urllib.parse import quote

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42

CUSTOMER_FEEDBACK_VERSION = "2024-06-01"
API_PREFIX = f"customerFeedback/{CUSTOMER_FEEDBACK_VERSION}"

SORT_BY_ENUM = frozenset({"MENTIONS", "STAR_RATING_IMPACT"})

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("STORE_API_BASE_URL")
    or os.environ.get("SPAPI_BASE_URL", "https://tool-gateway.linkfox.com")
).rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/spApi/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/spApi/developerProxy"

SUCCESS_HTTP_STATUSES = frozenset({200})


def ensure_auth_skill_available(caller: str = "customer-feedback script") -> None:
    here = Path(__file__).resolve().parent
    checker = here / "check_auth_dependency.py"
    if not checker.exists():
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": f"check_auth_dependency.py not found next to {caller}",
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run(
            [sys.executable, str(checker)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover
        payload = {"missingSkill": REQUIRED_SKILL, "reason": str(exc)}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        sys.exit(DEPENDENCY_EXIT_CODE)


SLUG = "linkfox-amazon-store-customer-feedback"


def call_api(endpoint: str, params: dict, timeout: int = 150, *, result_key=None) -> dict:
    """通过公共 run 请求、落盘并输出完整网关响应及解析字段。"""
    if timeout != 150:
        raise ValueError("公共调用器的 HTTP 超时固定为 150 秒")
    if endpoint not in (STORE_TOKENS_ENDPOINT, DEVELOPER_PROXY_ENDPOINT):
        raise ValueError("仅允许本技能定义的 LinkFox 端点")
    api_path = "/spApi/storeTokens" if endpoint == STORE_TOKENS_ENDPOINT else "/spApi/developerProxy"
    transport = api.call_api
    response = {}

    def with_result(path, request_params):
        http_status, proxy = transport(path, request_params)
        response["raw"] = proxy
        if result_key is None:
            return http_status, proxy
        out = {
            "developerProxy": proxy,
            "resolvedPath": params["path"],
            "queryString": params.get("queryString", ""),
            "transportHttpStatus": http_status,
        }
        if isinstance(http_status, int) and 200 <= http_status <= 299 and isinstance(proxy, dict):
            merge_success_json(out, proxy, result_key)
        return http_status, out

    # 先验证当前工作目录可写，禁止公共调用器回退到家目录或临时目录。
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("本技能禁止将会话数据写入 /tmp")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output = api._resolve_output_path
    os.environ["LINKFOX_TOOL_GATEWAY"] = API_BASE_URL
    os.environ["ACPX_WORKSPACES"] = str(cwd)
    api._SESSION_CACHE["_root"] = str(root)
    api.call_api = with_result
    try:
        # 请求前确认真正的会话 data 目录可写；仅检测根目录不能保证落盘。
        # 使用微秒时间戳文件名，避免连续响应相互覆盖。
        output_path = api.resolve_data_path(SLUG, time.time())
        with tempfile.TemporaryFile(dir=Path(output_path).parent):
            pass
        api._resolve_output_path = lambda _slug, _ts: output_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if lf_inline_flag():
            argv.append("--inline")
        api.run(api_path, SLUG, argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        for key, old in (("LINKFOX_TOOL_GATEWAY", previous_gateway), ("ACPX_WORKSPACES", previous_workspace)):
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
    return response["raw"]


def developer_proxy_get(
    region: str,
    path: str,
    seller_id: str,
    query_string: Optional[str] = None,
    timeout: int = 150,
    result_key=None,
) -> dict:
    params: dict = {
        "region": region,
        "path": path,
        "method": "GET",
        "sellerId": seller_id,
    }
    if query_string:
        params["queryString"] = query_string
    return call_api(DEVELOPER_PROXY_ENDPOINT, params, timeout=timeout, result_key=result_key)


def encode_path_segment(value: str) -> str:
    return quote(str(value).strip(), safe="")


def resolve_marketplace_id(params: dict) -> str:
    mid = params.get("marketplaceId")
    if mid is None and params.get("marketplaceIds") is not None:
        mids = params["marketplaceIds"]
        if isinstance(mids, list) and mids:
            mid = mids[0]
            if len(mids) > 1:
                print(
                    "Warning: Customer Feedback uses a single marketplaceId; using first only.",
                    file=sys.stderr,
                )
        elif isinstance(mids, str) and mids.strip():
            mid = mids.strip()
    if mid is None or not str(mid).strip():
        print("Missing marketplaceId (or marketplaceIds with at least one id).", file=sys.stderr)
        sys.exit(1)
    return str(mid).strip()


def query_marketplace_only(params: dict) -> str:
    mid = resolve_marketplace_id(params)
    return f"marketplaceId={quote(mid, safe='')}"


def query_marketplace_and_sort_by(params: dict) -> str:
    mid = resolve_marketplace_id(params)
    sort_by = params.get("sortBy")
    if not sort_by:
        print("Missing required field: sortBy (MENTIONS | STAR_RATING_IMPACT).", file=sys.stderr)
        sys.exit(1)
    sort_s = str(sort_by).strip().upper()
    if sort_s not in SORT_BY_ENUM:
        print(f"sortBy must be one of: {sorted(SORT_BY_ENUM)}", file=sys.stderr)
        sys.exit(1)
    return (
        f"marketplaceId={quote(mid, safe='')}"
        f"&sortBy={quote(sort_s, safe='')}"
    )


def merge_success_json(
    out: dict,
    proxy: dict,
    result_key: str,
    *,
    success_http: Iterable[int] = SUCCESS_HTTP_STATUSES,
) -> None:
    if not api._is_cacheable(200, proxy):
        return
    try:
        status = int(proxy.get("httpStatus") or 0)
    except (TypeError, ValueError):
        return
    if status not in success_http:
        return
    body_raw = proxy.get("body")
    if body_raw is None or not str(body_raw).strip():
        out[result_key] = None
        return
    try:
        out[result_key] = json.loads(str(body_raw))
    except json.JSONDecodeError:
        out[result_key] = None
        out[f"{result_key}Raw"] = body_raw


def load_cli_params() -> dict:
    if len(sys.argv) < 2:
        return {}
    try:
        return json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def require_seller_region(params: dict) -> tuple[str, str]:
    for f in ("sellerId", "region"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)
    return str(params["sellerId"]), str(params["region"])


def run_item_get(
    params: dict,
    *,
    path_suffix: str,
    result_key: str,
    query_builder,
    caller: str,
) -> None:
    if not params:
        print(f"Usage: {caller} '<JSON>' — see SKILL.md", file=sys.stderr)
        sys.exit(1)
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available(caller)
    if "asin" not in params:
        print("Missing required field: asin", file=sys.stderr)
        sys.exit(1)

    seller_id, region = require_seller_region(params)
    asin = encode_path_segment(params["asin"])
    path = f"{API_PREFIX}/items/{asin}/{path_suffix}"
    qs = query_builder(params)

    developer_proxy_get(region, path, seller_id, query_string=qs, result_key=result_key)


def run_browse_node_get(
    params: dict,
    *,
    path_suffix: str,
    result_key: str,
    query_builder,
    caller: str,
) -> None:
    if not params:
        print(f"Usage: {caller} '<JSON>' — see SKILL.md", file=sys.stderr)
        sys.exit(1)
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available(caller)
    if "browseNodeId" not in params:
        print("Missing required field: browseNodeId", file=sys.stderr)
        sys.exit(1)

    seller_id, region = require_seller_region(params)
    bn = encode_path_segment(params["browseNodeId"])
    path = f"{API_PREFIX}/browseNodes/{bn}/{path_suffix}"
    qs = query_builder(params)

    developer_proxy_get(region, path, seller_id, query_string=qs, result_key=result_key)


def lf_inline_flag() -> bool:
    """检测入口命令行中的 --inline 标志。"""
    return "--inline" in sys.argv
