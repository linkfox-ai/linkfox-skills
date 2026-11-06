"""Shared runners for Sponsored Brands V3/V4 coexistence scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from _common import (  # noqa: E402
    DEFAULT_MAX_PAGES,
    DEFAULT_PAGE_SIZE,
    _developer_proxy_call,
    _list_failure,
    _upstream_ok,
    build_filter_body,
    emit_result,
    ensure_auth_skill_available,
    lf_inline_flag,
    list_sp_entities,
    mutate_entity,
    parse_argv_params,
    require_fields,
)

# Re-export for entry scripts.
__all__ = [
    "build_filter_body",
    "emit_structured_error",
    "parse_argv_params",
    "run_get_offset_list",
    "run_get_token_list",
    "run_mutation",
    "run_post_token_list",
]

TARGET_FILTER_MAP = {
    "campaignIdFilter": "CAMPAIGN_ID",
    "adGroupIdFilter": "AD_GROUP_ID",
    "stateFilter": "TARGETING_STATE",
    "targetIdFilter": "TARGET_ID",
    "creativeTypeFilter": "CREATIVE_TYPE",
}

SINGLE_VALUE_QUERY_KEYS = {"nameFilter", "name", "keywordText", "locale"}


def _values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, dict):
        value = value.get("include", [])
    if not isinstance(value, list):
        value = [value]
    return [str(item) for item in value if item is not None]


def _parse_bool(value: Any, *, default: bool, field: str) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
    emit_structured_error(
        code="SB_INVALID_BOOLEAN",
        message=f"Invalid boolean for '{field}': {value!r}",
        extra={"field": field, "value": value},
    )
    return default  # unreachable


def _as_boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
    return None


def _normalize_structure(value: Any) -> str:
    text = str(value or "").strip().upper().replace("-", "_").replace(" ", "_")
    while "__" in text:
        text = text.replace("__", "_")
    compact = text.replace("_", "")
    aliases = {
        "MULTIADGROUP": "MULTI_AD_GROUP",
        "MULTIADGROUPS": "MULTI_AD_GROUP",
        "ISMULTIADGROUPSENABLED": "MULTI_AD_GROUP",
    }
    return aliases.get(compact, text)


def emit_structured_error(
    *,
    code: str,
    message: str,
    extra: dict[str, Any] | None = None,
    exit_code: int = 1,
) -> None:
    payload = {"success": False, "code": code, "message": message}
    if extra:
        payload.update(extra)
    emit_result(payload, inline=lf_inline_flag())
    sys.exit(exit_code)


def _extract_structure_flags(node: Any) -> tuple[str | None, bool | None]:
    structure = None
    multi = None
    if isinstance(node, dict):
        if "campaignStructure" in node:
            structure = _normalize_structure(node.get("campaignStructure"))
        if "isMultiAdGroupsEnabled" in node:
            multi = _as_boolish(node.get("isMultiAdGroupsEnabled"))
        for value in node.values():
            child_structure, child_multi = _extract_structure_flags(value)
            if child_structure == "MULTI_AD_GROUP" or not structure:
                structure = child_structure
            if child_multi is True or multi is None:
                multi = child_multi
    elif isinstance(node, list):
        for item in node:
            child_structure, child_multi = _extract_structure_flags(item)
            if child_structure == "MULTI_AD_GROUP" or not structure:
                structure = child_structure
            if child_multi is True or multi is None:
                multi = child_multi
    return structure, multi


def _legacy_guard(params: dict[str, Any]) -> None:
    """Reject an identified multi-ad-group campaign on V3."""
    structure = _normalize_structure(params.get("campaignStructure"))
    multi = _as_boolish(params.get("isMultiAdGroupsEnabled"))
    payload_structure, payload_multi = _extract_structure_flags(params.get("payload"))
    if payload_structure == "MULTI_AD_GROUP" or not structure:
        structure = payload_structure or ""
    if payload_multi is True or multi is None:
        multi = payload_multi

    if structure == "MULTI_AD_GROUP" or multi is True:
        emit_structured_error(
            code="SB_V4_CAMPAIGN_NOT_SUPPORTED",
            message=(
                "This campaign uses the Sponsored Brands V4 multi-ad-group "
                "structure. Use scripts/sb/v4 instead of V3."
            ),
            extra={
                "apiVersion": "V3",
                "campaignStructure": "MULTI_AD_GROUP",
            },
        )


def _prepare(
    params: dict[str, Any],
    *,
    api_version: str,
) -> tuple[int, str]:
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()
    require_fields(params, ["profileId", "region"])
    if api_version == "V3":
        _legacy_guard(params)
    profile_id = int(params["profileId"])
    return profile_id, str(params["region"])


def _emit_list(
    result: dict[str, Any],
    *,
    response_key: str,
    api_version: str,
    resource_version: str,
) -> None:
    if "error" in result:
        result = {**result, 'apiVersion': api_version,
                  'amazonResourceVersion': resource_version}
        emit_result(result, inline=lf_inline_flag())
        sys.exit(1)
    items = result.get("items", [])
    output = {
        "success": True,
        "apiVersion": api_version,
        "amazonResourceVersion": resource_version,
        response_key: items,
        "total": len(items),
        "pagesFetched": result.get("pagesFetched", 0),
        "truncated": result.get("truncated", False),
    }
    emit_result(output, inline=lf_inline_flag())


def _map_target_filters(params: dict[str, Any], request_body: dict[str, Any]) -> None:
    """Map top-level *Filter fields into Amazon SB target filters[]."""
    existing = request_body.get("filters")
    filters: list[dict[str, Any]] = []
    if isinstance(existing, list):
        filters.extend(existing)
    elif existing is not None:
        emit_structured_error(
            code="SB_INVALID_TARGET_FILTERS",
            message="'filters' must be an array of {filterType, values} objects.",
            extra={"filters": existing},
        )

    present_types = {
        str(item.get("filterType")).upper()
        for item in filters
        if isinstance(item, dict) and item.get("filterType")
    }

    for key, filter_type in TARGET_FILTER_MAP.items():
        if key not in params or params[key] is None:
            continue
        if filter_type in present_types:
            continue
        values = _values(params[key])
        if filter_type == "TARGETING_STATE":
            values = [value.lower() for value in values]
        if values:
            filters.append({"filterType": filter_type, "values": values})
            present_types.add(filter_type)

    if filters:
        request_body["filters"] = filters


def run_get_offset_list(
    usage: str,
    *,
    path: str,
    accept: str | None = None,
    response_key: str,
    query_keys: list[str],
    api_version: str = "V3",
    resource_version: str = "V3",
    params: dict[str, Any] | None = None,
) -> None:
    """Run legacy GET lists using startIndex/count offset pagination."""
    params = params if params is not None else parse_argv_params(usage)
    profile_id, region = _prepare(params, api_version=api_version)
    page_size = max(1, min(int(params.get("maxResults") or DEFAULT_PAGE_SIZE), 100))
    fetch_all = _parse_bool(params.get("fetchAll"), default=True, field="fetchAll")
    max_pages = int(params.get("maxPages") or DEFAULT_MAX_PAGES)

    base_query: dict[str, str] = {}
    for key in query_keys:
        if key not in params or params[key] is None:
            continue
        values = _values(params[key])
        if not values:
            continue
        query_name = "name" if key in {"nameFilter", "name"} else key
        if key in {"stateFilter", "matchTypeFilter", "creativeType"}:
            values = [value.lower() for value in values]
        if key in SINGLE_VALUE_QUERY_KEYS or query_name in SINGLE_VALUE_QUERY_KEYS:
            base_query[query_name] = values[0]
        else:
            base_query[query_name] = ",".join(values)

    collected: list[Any] = []
    start_index = 0
    pages = 0
    truncated = False
    while True:
        query = dict(base_query)
        query["startIndex"] = str(start_index)
        query["count"] = str(page_size)
        resp = _developer_proxy_call(
            region=region,
            path=path,
            method="GET",
            profile_id=profile_id,
            body=None,
            content_type=None,
            query_string=urlencode(query),
            accept=accept,
        )
        if "error" in resp:
            _emit_list(
                _list_failure(resp, collected, pages, response_key),
                response_key=response_key,
                api_version=api_version,
                resource_version=resource_version,
            )
            return
        status = resp.get("httpStatus")
        if not _upstream_ok(status):
            _emit_list(
                _list_failure({
                    **resp,
                    "error": f"Upstream HTTP {status}",
                }, collected, pages, response_key),
                response_key=response_key,
                api_version=api_version,
                resource_version=resource_version,
            )
            return
        try:
            parsed = json.loads(resp.get("body") or "[]")
        except (json.JSONDecodeError, TypeError) as exc:
            _emit_list(
                _list_failure({
                    **resp,
                    "error": f"Failed to parse upstream body: {exc}",
                }, collected, pages, response_key),
                response_key=response_key,
                api_version=api_version,
                resource_version=resource_version,
            )
            return
        if not isinstance(parsed, (list, dict)):
            _emit_list(
                _list_failure({**resp, 'error': '上游分页响应必须是数组或 JSON 对象'},
                              collected, pages, response_key),
                response_key=response_key, api_version=api_version,
                resource_version=resource_version,
            )
            return
        page_items = parsed if isinstance(parsed, list) else parsed.get(response_key, [])
        if not isinstance(page_items, list):
            _emit_list(
                _list_failure({**resp, 'error': f'上游 {response_key} 必须是数组'},
                              collected, pages, response_key),
                response_key=response_key, api_version=api_version,
                resource_version=resource_version,
            )
            return
        collected.extend(page_items)
        pages += 1
        if not fetch_all or len(page_items) < page_size:
            break
        if pages >= max_pages:
            truncated = True
            break
        start_index += page_size

    _emit_list(
        {
            "items": collected,
            "pagesFetched": pages,
            "truncated": truncated,
        },
        response_key=response_key,
        api_version=api_version,
        resource_version=resource_version,
    )


def run_post_token_list(
    usage: str,
    *,
    path: str,
    content_type: str,
    accept: str | None = None,
    response_key: str,
    api_version: str,
    resource_version: str,
    params: dict[str, Any] | None = None,
    request_body: dict[str, Any] | None = None,
    map_target_filters: bool = False,
) -> None:
    """Run POST /list resources that paginate with nextToken."""
    params = params if params is not None else parse_argv_params(usage)
    profile_id, region = _prepare(params, api_version=api_version)
    body = dict(request_body if request_body is not None else (params.get("payload") or {}))
    for key in ("filters", "maxResults", "nextToken", "includeExtendedDataFields"):
        if key in params and key not in body:
            body[key] = params[key]
    if map_target_filters:
        _map_target_filters(params, body)
    result = list_sp_entities(
        region=region,
        profile_id=profile_id,
        entity_path=path,
        entity_content_type=content_type,
        response_key=response_key,
        request_body=body,
        fetch_all=_parse_bool(params.get("fetchAll"), default=True, field="fetchAll"),
        max_pages=int(params.get("maxPages") or DEFAULT_MAX_PAGES),
        accept=accept,
    )
    _emit_list(
        result,
        response_key=response_key,
        api_version=api_version,
        resource_version=resource_version,
    )


def run_get_token_list(
    usage: str,
    *,
    path: str,
    accept: str | None = None,
    response_key: str,
    api_version: str,
    resource_version: str,
    params: dict[str, Any] | None = None,
    page_size_key: str | None = None,
    response_body_keys: list[str] | None = None,
) -> None:
    """Run GET list resources that paginate with a nextToken query."""
    params = params if params is not None else parse_argv_params(usage)
    profile_id, region = _prepare(params, api_version=api_version)
    token = params.get("nextToken")
    page_size = max(1, min(int(params.get("pageSize") or params.get("maxResults") or DEFAULT_PAGE_SIZE), 100))
    fetch_all = _parse_bool(params.get("fetchAll"), default=True, field="fetchAll")
    max_pages = int(params.get("maxPages") or DEFAULT_MAX_PAGES)
    items: list[Any] = []
    pages = 0
    truncated = False
    while True:
        query_params: dict[str, str] = {}
        if page_size_key:
            query_params[page_size_key] = str(page_size)
        if token:
            query_params["nextToken"] = str(token)
        query = urlencode(query_params) if query_params else None
        resp = _developer_proxy_call(
            region=region,
            path=path,
            method="GET",
            profile_id=profile_id,
            body=None,
            content_type=None,
            query_string=query,
            accept=accept,
        )
        status = resp.get("httpStatus")
        if "error" in resp or not _upstream_ok(status):
            _emit_list(
                _list_failure({
                    **resp,
                    "error": resp.get("error") or f"Upstream HTTP {status}",
                }, items, pages, response_key),
                response_key=response_key,
                api_version=api_version,
                resource_version=resource_version,
            )
            return
        try:
            parsed = json.loads(resp.get("body") or "{}")
        except (json.JSONDecodeError, TypeError) as exc:
            _emit_list(
                _list_failure({
                    **resp,
                    "error": f"Failed to parse upstream body: {exc}",
                }, items, pages, response_key),
                response_key=response_key,
                api_version=api_version,
                resource_version=resource_version,
            )
            return
        if not isinstance(parsed, dict):
            _emit_list(
                _list_failure({**resp, 'error': '上游分页响应必须是 JSON 对象'},
                              items, pages, response_key),
                response_key=response_key, api_version=api_version,
                resource_version=resource_version,
            )
            return
        keys = response_body_keys or [response_key, f"{response_key}Details"]
        page_items = []
        for key in keys:
            candidate = parsed.get(key)
            if isinstance(candidate, list):
                page_items = candidate
                break
            if candidate is not None:
                _emit_list(
                    _list_failure({**resp, 'error': f'上游 {key} 必须是数组'},
                                  items, pages, response_key),
                    response_key=response_key, api_version=api_version,
                    resource_version=resource_version,
                )
                return
        if isinstance(page_items, list):
            items.extend(page_items)
        pages += 1
        token = parsed.get("nextToken")
        if not token or not fetch_all:
            break
        if pages >= max_pages:
            truncated = True
            break
    _emit_list(
        {"items": items, "pagesFetched": pages, "truncated": truncated},
        response_key=response_key,
        api_version=api_version,
        resource_version=resource_version,
    )


def run_mutation(
    usage: str,
    *,
    path: str,
    method: str,
    content_type: str,
    accept: str | None = None,
    api_version: str,
    resource_version: str,
    params: dict[str, Any] | None = None,
) -> None:
    params = params if params is not None else parse_argv_params(usage)
    profile_id, region = _prepare(params, api_version=api_version)
    require_fields(params, ["payload"])
    result = mutate_entity(
        region=region,
        profile_id=profile_id,
        path=path,
        method=method,
        content_type=content_type,
        payload=params["payload"],
        accept=accept,
    )
    status = result.get("httpStatus")
    if "error" in result or not _upstream_ok(status):
        if "error" not in result:
            result["error"] = f"Upstream HTTP {status}"
            result["success"] = False
        emit_result(result, inline=lf_inline_flag())
        sys.exit(1)
    result["apiVersion"] = api_version
    result["amazonResourceVersion"] = resource_version
    emit_result(result, inline=lf_inline_flag())
