"""Shared helpers for linkfox-shopee-store-product (storeTokens + developerProxy)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import secrets
from pathlib import Path
from typing import Any, Optional
from contextlib import redirect_stdout
from io import StringIO
from urllib.parse import quote
import call_api as _gateway

API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "product script") -> None:
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


class GatewayResponse(dict):
    """保留原始响应字段，同时向加工层传递外层HTTP状态。"""

    transport_http_status: Optional[int] = None


def call_api(endpoint: str, params: dict) -> dict:
    """使用公共run调用网关，关闭响应缓存，复用公共HTTP传输。"""
    if not endpoint.startswith(API_BASE_URL + "/"):
        raise ValueError("接口地址必须属于配置的LinkFox网关")
    api_path = endpoint[len(API_BASE_URL):]
    root = _lf_root()  # 必须在请求前确认当前目录可写。
    _gateway._SESSION_CACHE["_root"] = root
    if not (os.environ.get("SESSION_ID") or "").strip():
        _gateway._SESSION_CACHE["_auto"] = _lf_session_id(time.time())
    recorded = {}
    original_call = _gateway.call_api

    def capture(path, payload):
        status, result = original_call(path, payload)
        recorded.update(status=status, result=result)
        return status, result

    old_base = os.environ.get("LINKFOX_TOOL_GATEWAY")
    os.environ["LINKFOX_TOOL_GATEWAY"] = API_BASE_URL
    _gateway.call_api = capture
    output = StringIO()
    try:
        with redirect_stdout(output):
            operation = (params.get("path") or api_path).rsplit("/", 1)[-1]
            # 公共run使用秒级文件时间戳，为原始响应增加标识，避免同秒调用覆盖。
            raw_slug = SLUG + "-" + operation + "-raw-" + secrets.token_hex(4)
            _gateway.run(api_path, raw_slug,
                         [json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"])
    finally:
        _gateway.call_api = original_call
        if old_base is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_base
        # 保留完整原始数据文件位置，避免重复打印大响应。
        for line in output.getvalue().splitlines():
            if line.startswith(("Saved full response:", "Failed to save to")):
                print(line)
    result = recorded["result"]
    if not isinstance(result, dict):
        raise ValueError("网关响应应为JSON对象")
    response = GatewayResponse(result)
    response.transport_http_status = recorded["status"]
    return response


def resolve_store_tokens(params: dict) -> dict:
    shop_id = params.get("shopId")
    merchant_id = params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)
    token_req: dict[str, str] = {}
    if shop_id:
        token_req["shopId"] = str(shop_id)
    if merchant_id:
        token_req["merchantId"] = str(merchant_id)
    return call_api(STORE_TOKENS_ENDPOINT, token_req)


def developer_proxy_call(
    path: str,
    method: str,
    shop_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    query_string: Optional[str] = None,
    body: Optional[str] = None,
    content_type: str = "application/json",
    access_token: Optional[str] = None,
) -> dict:
    if not path.startswith("api/v2"):
        print(f"Error: path must start with 'api/v2', got {path!r}", file=sys.stderr)
        sys.exit(1)
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)
    proxy: dict[str, Any] = {
        "path": path,
        "method": method,
    }
    if shop_id:
        proxy["shopId"] = str(shop_id)
    if merchant_id:
        proxy["merchantId"] = str(merchant_id)
    if access_token:
        proxy["accessToken"] = access_token
    if query_string:
        proxy["queryString"] = query_string
    if body is not None:
        proxy["body"] = body
        proxy["contentType"] = content_type
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    status = getattr(proxy, "transport_http_status", 200)
    if not gateway_response_ok(status, proxy):
        return
    try:
        upstream_status = int(proxy.get("httpStatus") or 0)
    except (ValueError, TypeError):
        return
    if upstream_status != 200:
        return
    body_raw = proxy.get("body")
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except json.JSONDecodeError:
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


def gateway_response_ok(status, payload: dict) -> bool:
    """遵循公共基础规则：0、false均不是空状态码。"""
    if status is None or not 200 <= status < 300:
        return False
    code = payload.get("errcode")
    if code is None or (isinstance(code, str) and not code.strip()):
        return True
    if isinstance(code, str):
        code = code.strip()
        if len(code) != 3 or not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


# ===== LinkFox 统一输出层（落盘 + 摘要，无缓存）=====
# 各入口脚本通过 emit_result() 使用统一输出层。
# 依赖：json, os, sys, time, secrets, tempfile（共享模块通常已 import json/os/sys；
#       若缺 time/secrets/tempfile，请在文件顶部补 import）。

import time as _lf_time
import secrets as _lf_secrets

LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict = {}

SLUG = "linkfox-shopee-store-product"


def _lf_root() -> str:
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    probe = root / (".write_probe-" + secrets.token_hex(6))
    with probe.open("w", encoding="utf-8"):
        pass
    probe.unlink()
    return str(root.resolve())


def _lf_iso(ts: float) -> str:
    return _lf_time.strftime("%Y-%m-%dT%H:%M:%S%z", _lf_time.localtime(ts))


def _lf_session_id(ts: float) -> str:
    env = os.environ.get("SESSION_ID")
    if env:
        return env.strip()
    if "_auto" not in _LF_SESSION_CACHE:
        _LF_SESSION_CACHE["_auto"] = (
            _lf_time.strftime("%H%M%S", _lf_time.localtime(ts)) + "-" + _lf_secrets.token_hex(3)
        )
    return _LF_SESSION_CACHE["_auto"]


def _lf_find_main_list(obj):
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    return best[0], best[1]


def _lf_summarize(result) -> None:
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costToken", "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")
    list_path, main_list = _lf_find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))


def _lf_ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    if os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _lf_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": os.path.relpath(session_dir, root),
                        "started_at": _lf_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass


def _lf_update_meta(session_dir: str, *, skill: str, file_rel: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    files = meta.setdefault("data_files", [])
    if file_rel not in files:
        files.append(file_rel)
    meta["last_used_at"] = _lf_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def emit_result(result, slug=SLUG, inline=False):
    """落盘完整响应到 linkfox/<date>/<session>/data/<slug>-<ts>.json；大响应只打印摘要。无缓存。"""
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = _lf_time.time()
    date_str = _lf_time.strftime("%Y-%m-%d", _lf_time.localtime(ts))
    sid = _lf_session_id(ts)
    root = _lf_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _lf_ensure_meta(root, session_dir, date_str, sid, ts)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    out = os.path.join(data_dir, f"{slug}-{int(ts * 1_000_000)}.json")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out} ({len(serialized)} bytes)")
    except OSError as e:
        print(f"Failed to save to {out}: {e}", file=sys.stderr)
    _lf_update_meta(session_dir, skill=slug, file_rel=os.path.relpath(out, session_dir), ts=ts)
    if inline or len(serialized.encode("utf-8")) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        _lf_summarize(result)


def load_cli_params(api_name: Optional[str] = None) -> dict:
    """解析JSON CLI参数、帮助与选项。"""
    args = sys.argv[1:]
    usage = f"Usage: {Path(sys.argv[0]).name} '<JSON>' [--inline] [--no-cache]"
    if "--help" in args or "-h" in args:
        print(usage)
        if api_name is None:
            from _product_endpoints import list_api_names
            print("Available: " + ", ".join(list_api_names()))
        sys.exit(0)
    args = [arg for arg in args if arg not in ("--inline", "--no-cache")]
    if len(args) != 1:
        print(usage, file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"Invalid parameter format: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        sys.exit(1)
    return params


def lf_inline_flag() -> bool:
    """入口脚本用：从 sys.argv 判断是否 --inline。"""
    return "--inline" in sys.argv

