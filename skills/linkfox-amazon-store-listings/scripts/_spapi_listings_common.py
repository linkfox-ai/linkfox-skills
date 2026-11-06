"""Listing 参数映射后的统一调用与兼容输出；原技能不启用响应缓存。"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import call_api as api
from call_api import run
from check_auth_dependency import locate_dependency, emit, searched_locations_for_report

API_PATH = "/spApi/developerProxy"
SLUG = "linkfox-amazon-store-listings"


def ensure_auth_skill_available():
    found = locate_dependency()
    if found is not None:
        emit(False, True, {"skill": "linkfox-amazon-store-auth", "skillMdPath": str(found)})
        return
    emit(False, False, {
        "missingSkill": "linkfox-amazon-store-auth",
        "reason": "本技能依赖已安装并完成授权的 linkfox-amazon-store-auth。",
        "searchedRoots": searched_locations_for_report(),
        "marketplaceUrl": "https://skill.linkfox.com/",
    })
    raise SystemExit(42)


def run_proxy(operation, method, region, path, seller_id, query_string, *, result_field, body_obj=None):
    params = {"region": region, "path": path, "method": method, "sellerId": seller_id}
    if query_string:
        params["queryString"] = query_string
    if body_obj is not None:
        params["body"] = json.dumps(body_obj, ensure_ascii=False)
        params["contentType"] = "application/json"

    # Keep the original parsed-result fields while delegating HTTP, persistence and CLI output to run().
    transport = api.call_api

    def with_listing_result(api_path, request_params):
        http_status, proxy = transport(api_path, request_params)
        result = {
            "developerProxy": proxy,
            "resolvedPath": path,
            "queryString": query_string,
            "transportHttpStatus": http_status,
        }
        if body_obj is not None:
            result["requestBody"] = body_obj
        if http_status == 200 and isinstance(proxy, dict) and api._is_cacheable(http_status, proxy) and proxy.get("httpStatus") == 200:
            raw = proxy.get("body") or "{}"
            try:
                result[result_field] = json.loads(raw) if isinstance(raw, str) else raw
            except (TypeError, json.JSONDecodeError):
                result[result_field] = None
                result[result_field + "Raw"] = raw
        return http_status, result

    # The copied runner supports fallback directories; this skill requires a writable cwd.
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    api._SESSION_CACHE["_root"] = str(root)
    if not previous_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = (os.environ.get("STORE_API_BASE_URL") or os.environ.get("SPAPI_BASE_URL") or api.get_api_base())
    api.call_api = with_listing_result
    # Preserve each response when repeated calls finish within the same second.
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        run(API_PATH, f"{SLUG}-{operation}", argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output_path
        for key, old in (("ACPX_WORKSPACES", previous_workspace), ("LINKFOX_TOOL_GATEWAY", previous_gateway)):
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
