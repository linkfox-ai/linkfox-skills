"""External Fulfillment 参数组装后的统一调用；不读取或写入响应缓存。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote, urlencode

import call_api as api

PATH_INVENTORY_BATCH = "externalFulfillment/inventory/2024-09-11/inventories"
PATH_SHIPMENTS = "externalFulfillment/2024-09-11/shipments"
PATH_RETURNS = "externalFulfillment/2024-09-11/returns"
API_PATH = "/spApi/developerProxy"
SLUG = "linkfox-amazon-store-external-fulfillment"
REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42

def ensure_auth_skill_available(caller: str = "ef script") -> None:
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


def enc_path_seg(value: str) -> str:
    return quote(str(value).strip(), safe="")


def build_query(pairs: list[tuple[str, Any]]) -> Optional[str]:
    filtered: list[tuple[str, str]] = []
    for k, v in pairs:
        if v is None:
            continue
        s = str(v).strip()
        if s == "":
            continue
        filtered.append((k, s))
    if not filtered:
        return None
    # 网关按 RFC 3986 解码，字面 '+' 不代表空格。
    return urlencode(filtered, doseq=True, quote_via=quote)


def require_fields(params: dict, fields: list[str]) -> None:
    for f in fields:
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)


def load_params_or_exit(usage: str) -> dict:
    if len(sys.argv) < 2:
        print(usage, file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须是对象", file=sys.stderr)
        sys.exit(1)
    return params


def merge_json_body(out, proxy, key, ok_statuses=(200, 207)):
    """仅在网关正常且上游成功时解析业务结果；不以 errcode 替代上游状态。"""
    status = proxy.get("httpStatus")
    if isinstance(status, str) and status.isascii() and status.isdigit():
        status = int(status)
    if status == 204:
        out[key] = None
        out["success"] = True
        return
    if status not in ok_statuses:
        return
    raw = proxy.get("body")
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        out[key] = None
    elif isinstance(raw, (dict, list)):
        out[key] = raw
    else:
        try:
            out[key] = json.loads(str(raw))
        except json.JSONDecodeError:
            out[key] = None
            out[key + "Raw"] = raw


def run_proxy(region, path, method, seller_id, query_string=None, body=None,
              content_type="application/json", *, operation, result_field,
              ok_statuses=(200, 207), output_fields=None):
    """由公共 run 完成唯一 HTTP 请求、完整落盘及摘要；本层只加工业务数据。"""
    params = {"region": region, "path": path, "method": method, "sellerId": seller_id}
    if query_string:
        params["queryString"] = query_string
    if body is not None:
        params.update(body=body, contentType=content_type)
    transport = api.call_api

    def with_ef_result(api_path, request_params):
        status, proxy = transport(api_path, request_params)
        result = {"developerProxy": proxy, "resolvedPath": path,
                  "transportHttpStatus": status}
        result.update(output_fields or {})
        # _is_cacheable(200, ...) 仅用于判定网关 errcode 是否正常；本技能不使用缓存。
        if (type(status) is int and 200 <= status < 300
                and api._is_cacheable(200, proxy)):
            merge_json_body(result, proxy, result_field, ok_statuses)
        return status, result

    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output = api._resolve_output_path
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    api._SESSION_CACHE["_root"] = str(root)
    if not previous_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = (os.environ.get("STORE_API_BASE_URL")
            or os.environ.get("SPAPI_BASE_URL") or api.get_api_base())
    try:
        # 在请求前验证实际会话 data 目录，不能仅检查 linkfox 根目录。
        # 同时固定本次输出路径，保留微秒文件名，避免重复调用覆盖响应。
        slug = f"{SLUG}-{operation}"
        output_path = api.resolve_data_path(slug, time.time())
        with tempfile.TemporaryFile(dir=Path(output_path).parent):
            pass
        api._resolve_output_path = lambda _slug, _ts: output_path
        api.call_api = with_ef_result
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        api.run(API_PATH, slug, argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        for key, value in (("ACPX_WORKSPACES", previous_workspace),
                           ("LINKFOX_TOOL_GATEWAY", previous_gateway)):
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
