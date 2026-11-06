"""FBA 请求映射、统一调用和兼容输出；业务调用不启用响应缓存。"""

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
from typing import Any, Optional
from urllib.parse import quote, urlencode
import call_api as api

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("STORE_API_BASE_URL")
    or os.environ.get("SPAPI_BASE_URL")
    or "https://tool-gateway.linkfox.com"
).rstrip("/")
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/spApi/developerProxy"

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-amazon-store-fba"


def ensure_auth_skill_available(caller: str = "fba script") -> None:
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


def call_api(endpoint: str, params: dict, *, result_builder=None,
             operation: str = "proxy", emit_output: bool = False) -> dict:
    """调用公共 run 并返回业务结果，不另实现 HTTP 或响应缓存。"""
    transport = api.call_api
    old_url = api.get_api_url
    old_output = api._resolve_output_path
    old_root = api._SESSION_CACHE.get("_root")
    old_workspace = os.environ.get("ACPX_WORKSPACES")
    received = {}

    def with_business_result(api_path, request_params):
        status, proxy = transport(api_path, request_params)
        result = result_builder(proxy, status) if result_builder else proxy
        received["result"] = result
        return status, result

    # 请求前确认当前目录可写，不回退到临时目录。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    api.call_api = with_business_result
    # 网关地址在导入时按三个兼容环境变量解析，通过公共调用器发送请求。
    api.get_api_url = lambda _path: endpoint
    api._SESSION_CACHE["_root"] = str(root)
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    # 公共调用器按秒命名；业务封装保留微秒，避免快速状态查询覆盖文件。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        output = contextlib.nullcontext() if emit_output else contextlib.redirect_stdout(io.StringIO())
        with output:
            api.run("/spApi/developerProxy", f"{SLUG}-{operation}", argv=argv)
        return received["result"]
    finally:
        api.call_api = transport
        api.get_api_url = old_url
        api._resolve_output_path = old_output
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
        if old_workspace is None:
            os.environ.pop("ACPX_WORKSPACES", None)
        else:
            os.environ["ACPX_WORKSPACES"] = old_workspace


def developer_proxy_call(
    region: str,
    path: str,
    method: str,
    seller_id: str,
    query_string: Optional[str] = None,
    body: Optional[str] = None,
    content_type: str = "application/json",
    *, result_builder=None, operation: str = "proxy", emit_output: bool = False,
) -> dict:
    params: dict[str, Any] = {
        "region": region,
        "path": path,
        "method": method,
        "sellerId": seller_id,
    }
    if query_string:
        params["queryString"] = query_string
    if body is not None:
        params["body"] = body
        params["contentType"] = content_type
    return call_api(DEVELOPER_PROXY_ENDPOINT, params, result_builder=result_builder,
                    operation=operation, emit_output=emit_output)


def enc_path_seg(value: str) -> str:
    return quote(str(value).strip(), safe="")


def build_query(pairs: list[tuple[str, Any]]) -> Optional[str]:
    """按 RFC 3986 编码查询串；列表/元组生成重复键，空格使用 %20。"""
    items: list[tuple[str, str]] = []
    for k, v in pairs:
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            for x in v:
                s = str(x).strip()
                if s:
                    items.append((k, s))
        else:
            if isinstance(v, bool):
                items.append((k, "true" if v else "false"))
            else:
                s = str(v).strip()
                if s != "":
                    items.append((k, s))
    if not items:
        return None
    return urlencode(items, doseq=True, quote_via=quote)


def _status_code(value) -> Optional[int]:
    """保留整数型 JSON 数值和三位数字字符串，排除布尔及小数状态码。"""
    if isinstance(value, str):
        value = value.strip()
        return int(value) if len(value) == 3 and value.isascii() and value.isdigit() else None
    if type(value) in (int, float) and 100 <= value < 600 and value % 1 == 0:
        return int(value)
    return None


def merge_json_body(
    out: dict,
    proxy: dict,
    key: str,
    ok_statuses: tuple[int, ...] = tuple(range(200, 300)),
) -> None:
    """外层及网关正常后解析上游；保留空响应和原始 body 字段。"""
    outer = out.get("transportHttpStatus", 200)
    if type(outer) is not int or not 200 <= outer < 300:
        return
    if not isinstance(proxy, dict) or not api._is_cacheable(200, proxy):
        return
    raw_status = proxy.get("httpStatus")
    status = _status_code(raw_status)
    # 兼容未提供 httpStatus 时由成功 errcode 表达上游状态；
    # 显式失败的上游状态不可被 errcode=200 覆盖。
    if raw_status is None:
        status = _status_code(proxy.get("errcode"))
    if status not in ok_statuses:
        return
    if status == 204:
        out[key] = None
        out["success"] = True
        return
    body_raw = proxy.get("body")
    if body_raw is None or (isinstance(body_raw, str) and not body_raw.strip()):
        out[key] = None
        out["success"] = True
        return
    if isinstance(body_raw, (dict, list)):
        out[key] = body_raw
        return
    try:
        out[key] = json.loads(str(body_raw))
    except json.JSONDecodeError:
        out[key] = None
        out[f"{key}Raw"] = body_raw
