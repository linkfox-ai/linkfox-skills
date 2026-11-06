"""A+ 参数映射与公共执行适配；使用 sellerId 和 region，不启用响应缓存。"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import call_api as api

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42
APLUS_API_VERSION = "2020-11-01"
APLUS_PATH_PREFIX = f"aplus/{APLUS_API_VERSION}"
SLUG = "linkfox-amazon-store-aplus-content"
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY")
                or os.environ.get("STORE_API_BASE_URL")
                or os.environ.get("SPAPI_BASE_URL")
                or "https://tool-gateway.linkfox.com")


def ensure_auth_skill_available(caller_script: str) -> None:
    """执行本地依赖探测，通过 stderr 和退出码 42 报告缺失，不联网。"""
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    if not checker.exists():
        payload = {"missingSkill": REQUIRED_SKILL,
                   "reason": f"check_auth_dependency.py not found next to {caller_script}"}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run([sys.executable, str(checker)], capture_output=True,
                                text=True, timeout=10, encoding="utf-8",
                                env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    except Exception as exc:
        payload = {"missingSkill": REQUIRED_SKILL, "reason": str(exc)}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        raise SystemExit(DEPENDENCY_EXIT_CODE)


def resolve_marketplace_id(params: dict, api_name: str) -> str:
    mid = params.get("marketplaceId")
    if mid is None and params.get("marketplaceIds") is not None:
        mids = params["marketplaceIds"]
        if isinstance(mids, list) and mids:
            mid = mids[0]
            if len(mids) > 1:
                print(f"⚠️  Warning: {api_name} uses a single marketplaceId; using first marketplaceIds only.",
                      file=sys.stderr)
        elif isinstance(mids, str) and mids.strip():
            mid = mids.strip()
    if mid is None or (isinstance(mid, str) and not mid.strip()):
        raise ValueError("Missing marketplaceId (or non-empty marketplaceIds)")
    return str(mid).strip()


def encode_path_segment(value: str) -> str:
    return quote(value, safe="")


def merge_success_json(out: dict, proxy: dict, result_key: str, *, success_http=(200,)) -> None:
    """网关基本规则与当前操作成功状态均满足后填充解析结果字段。"""
    if api._is_cacheable(200, proxy) and proxy.get("httpStatus") in success_http:
        raw = proxy.get("body") or "{}"
        try:
            out[result_key] = json.loads(raw) if isinstance(raw, str) else raw
        except (TypeError, json.JSONDecodeError):
            out[result_key] = None
            out[result_key + "Raw"] = raw


def _run_request(api_path: str, operation: str, params: dict,
                 result_builder=None, *, quiet=False, gateway_base=None) -> Any:
    """通过公共 run 包装结果、禁用缓存、限制落盘位置，随后恢复上下文。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("本技能禁止将会话数据保存到 /tmp")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 请求前探测写权限；不使用调用器的家目录/临时目录回退。
    with tempfile.TemporaryFile(dir=root):
        pass

    transport = api.call_api
    output_path = api._resolve_output_path
    old_root = api._SESSION_CACHE.get("_root")
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    raw_result = []

    def with_result(path, request_params):
        status, payload = transport(path, request_params)
        raw_result.append(payload)
        formatted = result_builder(status, payload) if result_builder else payload
        return status, formatted

    api.call_api = with_result
    api._SESSION_CACHE["_root"] = str(root)
    # 公共 run 以整秒命名；业务封装使用微秒，避免同秒响应覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    if gateway_base is not None:
        # call_api 兼容入口接受完整端点，显式地址必须优先于环境变量。
        os.environ["LINKFOX_TOOL_GATEWAY"] = gateway_base
    elif not old_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = (os.environ.get("STORE_API_BASE_URL")
                                               or os.environ.get("SPAPI_BASE_URL")
                                               or "https://tool-gateway.linkfox.com")
    try:
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        with contextlib.redirect_stdout(io.StringIO()) if quiet else contextlib.nullcontext():
            api.run(api_path, f"{SLUG}-{operation}", argv=argv)
        return raw_result[0] if raw_result else None
    finally:
        api.call_api = transport
        api._resolve_output_path = output_path
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
        if old_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_gateway


def run_proxy(operation, method, region, path, seller_id, query_string,
              *, result_field, body_obj=None, success_http=(200,), result_validator=None):
    params = {"region": region, "path": path, "method": method, "sellerId": seller_id}
    if query_string:
        params["queryString"] = query_string
    if method == "POST":
        params["contentType"] = "application/json"
    if body_obj is not None:
        params["body"] = json.dumps(body_obj, ensure_ascii=False)

    media_succeeded = False

    def format_result(status, proxy):
        nonlocal media_succeeded
        out = {"developerProxy": proxy, "resolvedPath": path,
               "queryString": query_string, "transportHttpStatus": status}
        if type(status) is int and 200 <= status < 300 and isinstance(proxy, dict):
            merge_success_json(out, proxy, result_field, success_http=success_http)
            if result_validator is not None and result_field in out:
                decoded = out[result_field]
                media_succeeded = (
                    isinstance(decoded, dict)
                    and api._is_cacheable(200, decoded)
                    and not proxy.get("error") and not proxy.get("errors")
                    and not decoded.get("error") and not decoded.get("errors")
                    and result_validator(decoded)
                )
                if not media_succeeded:
                    out["resultValidationError"] = "Media response is incomplete or does not match the requested asset."
                elif decoded.get("status") == []:
                    out["resultWarnings"] = [
                        "Upstream returned an empty aggregate media status; inspect each relatedMedia status. Availability is unknown."
                    ]
        return out

    _run_request("/spApi/developerProxy", operation, params, format_result)
    if result_validator is not None and not media_succeeded:
        raise SystemExit(1)


