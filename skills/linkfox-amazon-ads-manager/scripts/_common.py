"""
Shared helpers for linkfox-amazon-ads-manager scripts.

All list_*.py scripts import from this module for:
  - Dependency check (linkfox-amazon-ads-auth must be installed)
  - LINKFOXAGENT_API_KEY retrieval
  - /amazonAds/storeTokens call to get access token
  - /amazonAds/developerProxy call with the right method / Content-Type per ad product
  - Auto-pagination across Sponsored Products / Sponsored Brands (nextToken) and
    Sponsored Display (startIndex + count offset)

This module is NOT intended to be run directly; it is imported by list_*.py siblings.

Import convention (at top of each list_*.py):

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _common import ensure_auth_skill_available, get_access_token, list_sp_entities
    # or list_sd_entities for Sponsored Display
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
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
                f"Install skill '{REQUIRED_SKILL}' before running linkfox-amazon-ads-manager.",
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
    "stateFilter":              "object",
    "campaignIdFilter":         "object",
    "adGroupIdFilter":          "object",
    "keywordIdFilter":          "object",
    "targetIdFilter":           "object",
    "negativeTargetIdFilter":   "object",  # SD negativeTargets
    "negativeKeywordIdFilter":  "object",  # SP negativeKeywords
    "creativeIdFilter":         "object",  # SD creatives
    "adIdFilter":               "object",
    "portfolioIdFilter":        "object",
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


# ---------- Sponsored Display (v3) 支持 ----------
#
# Sponsored Display v3 list endpoint 的形态：
#   - 方法：GET，参数位于 querystring
#   - 分页：startIndex + count 偏移分页
#   - 过滤器：扁平字符串（id 类逗号分隔；state 类逗号分隔小写）
#   - 扩展字段：通过路径区分（/sd/<entity> 与 /sd/<entity>/extended）
#
# 过滤字段统一接受 {"include":[...]} / 裸数组 / 单值字符串三种形态，转换为
# Sponsored Display 端所需的 querystring：
#   - build_sd_query()    将 *Filter 入参规范化为 querystring dict + 是否使用 /extended
#   - list_sd_entities()  按 startIndex + count 循环 GET，直到本页 < count 或达 max_pages

# *Filter 入参到 Sponsored Display querystring 字段的映射。
SD_QUERY_ID_FIELDS: dict[str, str] = {
    "campaignIdFilter":       "campaignIdFilter",
    "adGroupIdFilter":        "adGroupIdFilter",
    "adIdFilter":             "adIdFilter",
    "targetIdFilter":         "targetIdFilter",
    # /sd/negativeTargets querystring 不支持 negativeTargetIdFilter；保留映射避免
    # 静默丢字段，传入时上游会返回 400 / 422 由用户感知。
    "negativeTargetIdFilter": "negativeTargetIdFilter",
    "portfolioIdFilter":      "portfolioIdFilter",
    "creativeIdFilter":       "creativeIdFilter",
}

SD_STATE_FIELDS = ("stateFilter",)
SD_NAME_FIELDS = ("nameFilter",)  # SD 上游字段名是 `name`（精确匹配）


def _to_list(val) -> list:
    """把 {"include":[...]} / 裸数组 / 标量 都归一化成一个 list（用于 SD querystring 拼接）。"""
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if x is not None]
    if isinstance(val, dict):
        if isinstance(val.get("include"), list):
            return [str(x) for x in val["include"] if x is not None]
        return []
    return [str(val)]


def build_sd_query(params: dict, filter_keys: list[str]):
    """将 *Filter 入参规范化为 Sponsored Display GET endpoint 所需的扁平 querystring。

    返回 (query_dict, use_extended_path, client_filters)：
      - query_dict     : {"stateFilter": "enabled,paused", "campaignIdFilter": "1,2", ...}
      - use_extended_path : 传 includeExtendedDataFields=true 时为 True，否则 False
      - client_filters : {"asinFilter": ["B0XX"], ...}（上游不支持的过滤字段，由调用方拉回后本地匹配）

    规范化规则：
      - state 类做 .lower()（Sponsored Display 接口端要求 `enabled` 而非 `ENABLED`）
      - id 类合并为逗号分隔字符串
      - nameFilter：Sponsored Display 仅支持精确匹配；若传 queryTermMatchType=BROAD_MATCH，
        在 stderr 输出一次提示，并仅取 include[0] 作 `name` 参数
      - asinFilter / skuFilter：Sponsored Display 端不支持，转为 client-side 过滤
    """
    query: dict[str, str] = {}
    client_filters: dict[str, list] = {}

    # 1) id 类（含 portfolio / creative / target / negativeTarget）
    for key, sd_field in SD_QUERY_ID_FIELDS.items():
        if key not in filter_keys or key not in params or params[key] is None:
            continue
        values = _to_list(params[key])
        if values:
            query[sd_field] = ",".join(values)

    # 2) state 类（小写化）
    for key in SD_STATE_FIELDS:
        if key not in filter_keys or key not in params or params[key] is None:
            continue
        values = [str(v).lower() for v in _to_list(params[key])]
        if values:
            query[key] = ",".join(values)

    # 3) name（精确匹配；SD 没有 BROAD_MATCH）
    for key in SD_NAME_FIELDS:
        if key not in filter_keys or key not in params or params[key] is None:
            continue
        val = params[key]
        include: list = []
        match_type = None
        if isinstance(val, dict):
            include = _to_list(val.get("include"))
            match_type = val.get("queryTermMatchType")
        else:
            include = _to_list(val)
        if match_type and match_type != "EXACT_MATCH":
            print(
                f"⚠️  Sponsored Display nameFilter 仅支持精确匹配；忽略 queryTermMatchType={match_type}，"
                f"按 include[0]={include[0] if include else '(empty)'} 作 name 精确匹配。",
                file=sys.stderr,
            )
        if include:
            query["name"] = include[0]

    # 4) client-side 过滤（asin / sku）
    for fkey in ("asinFilter", "skuFilter"):
        if fkey not in filter_keys or fkey not in params or params[fkey] is None:
            continue
        values = _to_list(params[fkey])
        if values:
            client_filters[fkey] = values

    # 5) extended 路径开关
    use_extended_path = bool(params.get("includeExtendedDataFields"))

    return query, use_extended_path, client_filters


def list_sd_entities(region: str, profile_id: int, access_token: str,
                     entity_path: str,
                     response_key: str,
                     server_query: dict,
                     fetch_all: bool = True,
                     max_pages: int = DEFAULT_MAX_PAGES,
                     page_size: int = DEFAULT_PAGE_SIZE) -> dict:
    """GET 一个 Sponsored Display v3 list endpoint，并按 startIndex + count 自动翻页。

    Sponsored Display 响应顶层是数组（非 `{<entityKey>:[...]}` 结构）；本函数对两种形态都兼容。
    终止条件：本页返回长度 < count（已到最后一页），或累计 pages >= max_pages（兜底）。

    返回结构：
        {"items":[...], "pagesFetched":N, "truncated":bool}
        或 {"error":..., "httpStatus":..., "body":..., "pagesFetched":...}
    """
    if page_size < 1:
        page_size = DEFAULT_PAGE_SIZE
    if page_size > 100:
        page_size = 100

    collected: list = []
    start_index = 0
    pages = 0
    truncated = False

    while True:
        page_query = dict(server_query or {})
        page_query["startIndex"] = str(start_index)
        page_query["count"] = str(page_size)
        qs = urlencode(page_query, doseq=False)

        resp = _developer_proxy_call(
            region=region,
            path=entity_path,
            method="GET",
            access_token=access_token,
            profile_id=profile_id,
            body=None,
            content_type=None,
            query_string=qs,
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
            parsed = json.loads(resp.get("body") or "[]")
        except Exception as e:
            return {
                "error": f"Failed to parse upstream body as JSON: {e}",
                "body": resp.get("body"),
                "pagesFetched": pages,
            }

        if isinstance(parsed, list):
            page_items = parsed
        elif isinstance(parsed, dict):
            page_items = parsed.get(response_key) or []
        else:
            page_items = []

        if isinstance(page_items, list):
            collected.extend(page_items)

        pages += 1
        page_len = len(page_items) if isinstance(page_items, list) else 0

        if not fetch_all or page_len < page_size:
            break
        if pages >= max_pages:
            truncated = True
            break
        start_index += page_size

    return {
        "items": collected,
        "pagesFetched": pages,
        "truncated": truncated,
    }


# ---------- Mutation (POST create / PUT update) ----------

def mutate_entity(region: str, profile_id: int, access_token: str,
                  path: str, method: str, content_type: str,
                  payload) -> dict:
    """POST (create) or PUT (update) an entity batch via developerProxy.

    Returns either:
        {"success": True, "httpStatus": N, "data": <parsed response>}
    or:
        {"error": "...", ...}
    """
    body_str = json.dumps(payload) if payload is not None else None

    resp = _developer_proxy_call(
        region=region,
        path=path,
        method=method,
        access_token=access_token,
        profile_id=profile_id,
        body=body_str,
        content_type=content_type,
        query_string=None,
    )

    if "error" in resp:
        return resp

    http_status = resp.get("httpStatus")
    body_raw = resp.get("body") or ""

    try:
        parsed = json.loads(body_raw) if body_raw else {}
    except (json.JSONDecodeError, TypeError):
        parsed = body_raw

    return {"success": True, "httpStatus": http_status, "data": parsed}
