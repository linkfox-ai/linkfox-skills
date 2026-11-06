"""定价参数映射后的统一调用与兼容输出；禁用响应缓存。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import call_api as api

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-amazon-store-pricing"
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("STORE_API_BASE_URL")
                or os.environ.get("SPAPI_BASE_URL") or "https://tool-gateway.linkfox.com")

def ensure_auth_skill_available(caller_script: str = "pricing CLI") -> None:
    here = Path(__file__).resolve().parent
    checker = here / "check_auth_dependency.py"
    if not checker.exists():
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": f"check_auth_dependency.py not found next to {caller_script}",
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


def resolve_marketplace_id(params: dict, api_name: str) -> str:
    mid = params.get("marketplaceId")
    if mid is None and params.get("marketplaceIds") is not None:
        mids = params["marketplaceIds"]
        if isinstance(mids, list) and mids:
            mid = mids[0]
            if len(mids) > 1:
                print(
                    f"⚠️  Warning: {api_name} expects a single MarketplaceId; using first marketplaceIds only.",
                    file=sys.stderr,
                )
        elif isinstance(mids, str) and mids.strip():
            mid = mids.strip()
    if mid is None or (isinstance(mid, str) and not mid.strip()):
        raise ValueError("Missing marketplaceId (or non-empty marketplaceIds)")
    return str(mid).strip()


def normal_response(status, payload):
    """按公共规则判断外层 HTTP 与 errcode；0 和 false 均非空。"""
    return type(status) is int and 200 <= status <= 299 and api._is_cacheable(200, payload)


def _run_request(api_path, params, operation, transform=None):
    """由公共 run 完成 HTTP、落盘与摘要，业务封装仅加工响应。"""
    cwd = Path.cwd().resolve()
    forbidden = Path("/tmp").resolve()
    if cwd == forbidden or forbidden in cwd.parents:
        raise OSError("完整响应禁止写入 /tmp，请切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 不允许公共调用器因 cwd 不可写而回退家目录或临时目录。
    with tempfile.TemporaryFile(dir=root):
        pass
    transport = api.call_api
    old_output = api._resolve_output_path
    old_root = api._SESSION_CACHE.get("_root")
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    old_workspace = os.environ.get("ACPX_WORKSPACES")
    captured = {}

    def wrapped(path, request):
        status, payload = transport(path, request)
        captured["payload"] = payload
        return status, transform(status, payload) if transform else payload

    api.call_api = wrapped
    api._SESSION_CACHE["_root"] = str(root)
    os.environ["ACPX_WORKSPACES"] = str(cwd)
    if not old_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = (os.environ.get("STORE_API_BASE_URL")
                                               or os.environ.get("SPAPI_BASE_URL")
                                               or "https://tool-gateway.linkfox.com")
    try:
        # 在请求之前检查实际会话目录，避免请求完成后才发现 data 路径不可写。
        ts = time.time()
        data_dir = (root / time.strftime("%Y-%m-%d", time.localtime(ts))
                    / api._session_id(ts) / "data").resolve()
        if root not in data_dir.parents:
            raise ValueError("会话数据路径必须位于当前工作目录的 linkfox 内，请检查 SESSION_ID")
        output_path = api.resolve_data_path(SLUG + "-" + operation, ts)
        with tempfile.TemporaryFile(dir=Path(output_path).parent):
            pass
        api._resolve_output_path = lambda slug, ts: output_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        api.run(api_path, SLUG + "-" + operation, argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = old_output
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
        for key, value in (("LINKFOX_TOOL_GATEWAY", old_gateway), ("ACPX_WORKSPACES", old_workspace)):
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    return captured.get("payload")


def run_proxy(operation, method, region, path, seller_id, query_string=None, *, result_field, body_obj=None):
    params = {"region": region, "path": path, "method": method, "sellerId": seller_id}
    if query_string:
        params["queryString"] = query_string
    if body_obj is not None:
        params["body"] = json.dumps(body_obj, ensure_ascii=False)
        params["contentType"] = "application/json"

    def transform(status, proxy):
        result = {"developerProxy": proxy, "resolvedPath": path, "transportHttpStatus": status}
        if query_string is not None:
            result["queryString"] = query_string
        if body_obj is not None:
            result["requestBody"] = body_obj
        if normal_response(status, proxy) and proxy.get("httpStatus") == 200:
            raw = proxy.get("body") or "{}"
            try:
                result[result_field] = json.loads(raw) if isinstance(raw, str) else raw
            except (TypeError, json.JSONDecodeError):
                result[result_field] = None
                result[result_field + "Raw"] = raw
        return result

    return _run_request("/spApi/developerProxy", params, operation, transform)


