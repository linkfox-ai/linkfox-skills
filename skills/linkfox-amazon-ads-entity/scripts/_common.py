"""
Shared helpers for linkfox-amazon-ads-entity scripts.

All list_*.py scripts import from this module for:
  - Dependency check (linkfox-amazon-ads-auth must be installed)
  - LINKFOXAGENT_API_KEY retrieval
  - /amazonAds/storeTokens call to get access token
  - /amazonAds/developerProxy call with SP v3 Content-Type
  - nextToken-aware auto-pagination

This module is NOT intended to be run directly; it is imported by list_*.py siblings.

Import convention (at top of each list_*.py):

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _common import ensure_auth_skill_available, get_access_token, list_sp_entities
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = os.environ.get("AMAZON_ADS_BASE_URL") or "https://tool-gateway.linkfox.com"
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/amazonAds/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/amazonAds/developerProxy"

REQUIRED_SKILL = "linkfox-amazon-ads-auth"
DEPENDENCY_EXIT_CODE = 42
DEFAULT_MAX_PAGES = 50
DEFAULT_PAGE_SIZE = 100


# ---------- Dependency check ----------

def ensure_auth_skill_available() -> None:
    """Invoke check_auth_dependency.py sibling; exit 42 if auth skill missing."""
    here = Path(__file__).resolve().parent
    checker = here / "check_auth_dependency.py"
    if not checker.exists():
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": "check_auth_dependency.py not found next to this script",
            "suggestedActions": [
                f"Install skill '{REQUIRED_SKILL}' before running linkfox-amazon-ads-entity.",
            ],
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
    except Exception as exc:
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": f"Failed to run dependency check: {exc}",
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)

    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        sys.exit(DEPENDENCY_EXIT_CODE)


# ---------- LinkFox gateway plumbing ----------

def get_api_key() -> str:
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "❌ LINKFOXAGENT_API_KEY not configured. Please set:\n"
            "  export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_gateway(endpoint: str, payload: dict) -> dict:
    api_key = get_api_key()
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        endpoint,
        data=data,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def get_access_token(profile_id: int) -> str:
    """Fetch access token for the given profileId via /amazonAds/storeTokens."""
    print(f"🔑 Fetching access token for profileId={profile_id}…", file=sys.stderr)
    result = call_gateway(STORE_TOKENS_ENDPOINT, {"profileId": int(profile_id)})
    if "error" in result or "accessToken" not in result:
        print(f"❌ Failed to get access token: {result}", file=sys.stderr)
        sys.exit(1)
    return result["accessToken"]


def _developer_proxy_call(region: str, path: str, method: str, access_token: str,
                          profile_id: int, body: str | None, content_type: str | None,
                          query_string: str | None) -> dict:
    payload: dict[str, Any] = {
        "region": region,
        "path": path,
        "method": method,
        "amzAccessToken": access_token,
        "profileId": int(profile_id),
    }
    if body is not None:
        payload["body"] = body
    if content_type:
        payload["contentType"] = content_type
    if query_string:
        payload["queryString"] = query_string
    return call_gateway(DEVELOPER_PROXY_ENDPOINT, payload)


# ---------- SP list (POST, v3, nextToken paginated) ----------

def list_sp_entities(region: str, profile_id: int, access_token: str,
                     entity_path: str, entity_content_type: str, response_key: str,
                     request_body: dict, fetch_all: bool = True,
                     max_pages: int = DEFAULT_MAX_PAGES) -> dict:
    """
    POST a SP v3 list endpoint and optionally auto-paginate via nextToken.

    Returns either:
        {"items": [...], "pagesFetched": N, "truncated": bool}
    or:
        {"error": "...", "httpStatus": N, "body": "<raw>", "details": "..."}

    The caller re-keys "items" to the entity-specific key (campaigns / adGroups / …)
    on the way out, so this function stays entity-agnostic.
    """
    base_body = dict(request_body or {})
    base_body.setdefault("maxResults", DEFAULT_PAGE_SIZE)

    collected: list = []
    token: str | None = None
    pages = 0
    truncated = False

    while True:
        page_body = dict(base_body)
        if token:
            page_body["nextToken"] = token

        resp = _developer_proxy_call(
            region=region,
            path=entity_path,
            method="POST",
            access_token=access_token,
            profile_id=profile_id,
            body=json.dumps(page_body),
            content_type=entity_content_type,
            query_string=None,
        )

        if "error" in resp:
            return {
                "error": resp["error"],
                "details": resp.get("details"),
                "pagesFetched": pages,
            }

        http_status = resp.get("httpStatus")
        if http_status is None or http_status // 100 != 2:
            return {
                "error": f"Upstream HTTP {http_status}",
                "httpStatus": http_status,
                "contentType": resp.get("contentType"),
                "body": resp.get("body"),
                "pagesFetched": pages,
            }

        try:
            parsed = json.loads(resp.get("body") or "{}")
        except Exception as e:
            return {
                "error": f"Failed to parse upstream body as JSON: {e}",
                "body": resp.get("body"),
                "pagesFetched": pages,
            }

        page_items = parsed.get(response_key) or []
        if isinstance(page_items, list):
            collected.extend(page_items)

        pages += 1
        token = parsed.get("nextToken")

        if not token or not fetch_all:
            break
        if pages >= max_pages:
            truncated = True
            break

    return {
        "items": collected,
        "pagesFetched": pages,
        "truncated": truncated,
    }


# ---------- Argv / param helpers ----------

def parse_argv_params(usage_text: str) -> dict:
    """Read sys.argv[1] as JSON, print usage and exit(1) if missing / invalid."""
    if len(sys.argv) < 2:
        print(usage_text, file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def require_fields(params: dict, required: list[str]) -> None:
    missing = [f for f in required if f not in params]
    if missing:
        print(f"❌ Missing required parameters: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


# 字段结构规范表 —— 每个 filter 字段对应的请求体结构（封装层按此规范化入参后再发给上游）
#
# - "object"      : {"include":[...]} / {"exclude":[...]}（多数 id/state 类过滤器）
# - "array"       : 裸数组 ["EXACT","BROAD"]（matchType/expressionType 等枚举过滤器）
# - "scalar"      : 裸字符串 "AUTO"（campaignTargetingType 等单值字段）
# - "text_filter" : {"queryTermMatchType":"BROAD_MATCH","include":["soap"]}（文本搜索类）
# - "client_side" : 上游不支持，由本 skill 在拉回结果后本地过滤（asinFilter / skuFilter）
FILTER_STRUCTURE: dict[str, str] = {
    # 对象型（include/exclude 列表）
    "stateFilter":         "object",
    "campaignIdFilter":    "object",
    "adGroupIdFilter":     "object",
    "keywordIdFilter":     "object",
    "targetIdFilter":      "object",
    "adIdFilter":          "object",
    "portfolioIdFilter":   "object",
    # 裸数组型
    "matchTypeFilter":     "array",
    # 注意：expressionTypeFilter 实证是 object-include 结构（与 matchTypeFilter 不同）
    "expressionTypeFilter":"object",
    # 裸字符串型
    "campaignTargetingTypeFilter": "scalar",
    # 文本搜索型（queryTermMatchType + include）
    "nameFilter":          "text_filter",
    "keywordTextFilter":   "text_filter",
    # 本 skill 客户端过滤（上游 Amazon API 未原生支持）
    "asinFilter":          "client_side",
    "skuFilter":           "client_side",
}

# 参与客户端过滤的字段，匹配到返回条目中的哪个字段
CLIENT_SIDE_FILTER_TARGETS: dict[str, str] = {
    "asinFilter": "asin",
    "skuFilter":  "sku",
}


def _normalize_filter_value(stype: str, val):
    """把用户传入的灵活结构规范化为上游需要的形状。

    封装策略：对调用方常见的"写法变体"做宽松兼容，封装掉上游字段结构的差异。
    - "array"  目标形态 ["A","B"]
        接受：["A","B"] / {"include":["A","B"]} / "A"
    - "object" 目标形态 {"include":[...]}
        接受：{"include":[...]} / ["A","B"]（自动包 include） / "A"（包 include 单值）
    - "scalar" 目标形态 "AUTO"
        接受："AUTO" / {"include":["AUTO"]} / ["AUTO"]
    - "text_filter" 目标形态 {"queryTermMatchType":"...","include":[...]}
        原样透传（该字段必须用户按规范写）
    """
    if val is None:
        return None
    if stype == "array":
        if isinstance(val, list):
            return val
        if isinstance(val, dict) and isinstance(val.get("include"), list):
            return val["include"]
        if isinstance(val, str):
            return [val]
        return val
    if stype == "scalar":
        if isinstance(val, str):
            return val
        if isinstance(val, dict) and isinstance(val.get("include"), list) and val["include"]:
            return val["include"][0]
        if isinstance(val, list) and val:
            return val[0]
        return val
    if stype == "object":
        if isinstance(val, dict):
            return val  # 已是 {"include":[...]} / {"exclude":[...]}
        if isinstance(val, list):
            return {"include": val}  # 裸数组兜底包装
        if isinstance(val, str):
            return {"include": [val]}
        return val
    # text_filter / 未知 → 原样透传
    return val


def split_server_client_filters(params: dict, filter_keys: list[str]):
    """将入参拆成「上游请求体」+「本地需过滤的 client-side 过滤器」。

    返回 (server_body, client_filters)：
    - server_body：已按字段结构规范化，可直接作为 /list endpoint 的 JSON body
    - client_filters：{"asinFilter": ["B0XXX"], ...}，待拉回数据后本地筛
    """
    server_body: dict[str, Any] = {}
    client_filters: dict[str, list] = {}

    for k in filter_keys:
        if k not in params or params[k] is None:
            continue
        stype = FILTER_STRUCTURE.get(k, "object")
        val = params[k]
        if stype == "client_side":
            # 归一化成数组，便于后续本地匹配
            if isinstance(val, list):
                values = val
            elif isinstance(val, dict) and isinstance(val.get("include"), list):
                values = val["include"]
            elif isinstance(val, str):
                values = [val]
            else:
                values = []
            if values:
                client_filters[k] = values
        else:
            normalized = _normalize_filter_value(stype, val)
            if normalized is not None:
                server_body[k] = normalized

    # maxResults 透传
    if "maxResults" in params and params["maxResults"] is not None:
        server_body["maxResults"] = int(params["maxResults"])

    # 其他可选顶层字段（扩展数据/本地化）
    for extra in ("includeExtendedDataFields", "locale"):
        if extra in params and params[extra] is not None:
            server_body[extra] = params[extra]

    return server_body, client_filters


def build_filter_body(params: dict, filter_keys: list[str]) -> dict:
    """兼容旧调用方：仅返回上游请求体部分（忽略 client-side 过滤器）。

    新调用方建议直接用 `split_server_client_filters()`，以便拿到 client-side 过滤器做本地筛选。
    """
    server_body, _ = split_server_client_filters(params, filter_keys)
    return server_body


def apply_client_side_filters(items: list, client_filters: dict) -> list:
    """对已拉回的 items 按 client-side 过滤器筛选（用于上游不支持的过滤字段）。"""
    if not client_filters:
        return items
    filtered = items
    for fkey, values in client_filters.items():
        target_field = CLIENT_SIDE_FILTER_TARGETS.get(fkey)
        if not target_field:
            continue
        wanted = set(values)
        filtered = [it for it in filtered if it.get(target_field) in wanted]
    return filtered
