"""Uploads 参数加工与兼容输出；LinkFox 请求统一经过公共 run，无响应缓存。"""
from __future__ import annotations

import base64
from contextlib import contextmanager, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Iterable, Optional
from urllib.parse import quote

import call_api as api

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42
UPLOADS_API_VERSION = "2020-11-01"
UPLOADS_PATH_PREFIX = f"uploads/{UPLOADS_API_VERSION}"
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("STORE_API_BASE_URL")
                or os.environ.get("SPAPI_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/spApi/developerProxy"
SUCCESS_HTTP_STATUSES = frozenset({200, 201})
SLUG = "linkfox-amazon-store-uploads"


def ensure_auth_skill_available(caller: str = "uploads script") -> None:
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


def is_normal_response(http_status, payload):
    """严格遵循公共 2xx 与 errcode 规则，bool 不作为空值或状态码。"""
    if type(http_status) is not int or not 200 <= http_status < 300 or not isinstance(payload, dict):
        return False
    code = payload.get("errcode")
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        if len(code) != 3 or not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


def resolve_upload_destination(value):
    """兼容 Uploads 的 errors/payload 包装与已有扁平目的地。"""
    if not isinstance(value, dict) or not is_normal_response(200, value) or value.get("errors"):
        return None
    destination = value.get("payload") if "payload" in value else value
    if not isinstance(destination, dict) or not is_normal_response(200, destination) or destination.get("errors"):
        return None
    return destination

@contextmanager
def output_context():
    """强制 cwd 落盘；提前检查会话目录可写，退出时恢复公共模块与环境。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    previous_cache = dict(api._SESSION_CACHE)
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    previous_resolver = api._resolve_output_path
    api._SESSION_CACHE["_root"] = str(root)
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    try:
        _, session_dir = api._ensure_session(time.time())
        data = Path(session_dir) / "data"
        data.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data):
            pass
        api._resolve_output_path = lambda slug, ts: api.resolve_data_path(slug, time.time())
        yield
    finally:
        api._resolve_output_path = previous_resolver
        auto_session = api._SESSION_CACHE.get("_auto")
        api._SESSION_CACHE.clear()
        api._SESSION_CACHE.update(previous_cache)
        if auto_session:
            api._SESSION_CACHE.setdefault("_auto", auto_session)
        if previous_workspace is None:
            os.environ.pop("ACPX_WORKSPACES", None)
        else:
            os.environ["ACPX_WORKSPACES"] = previous_workspace

def call_api(endpoint: str, params: dict, timeout: int = 150, *, result_builder=None, quiet=False):
    """辅助调用入口；HTTP、落盘和摘要由公共 call_api.run 处理。"""
    api_path = next((path for path in ("/spApi/storeTokens", "/spApi/developerProxy") if endpoint.endswith(path)), None)
    if api_path is None:
        raise ValueError("不支持的 LinkFox 端点")
    base = endpoint[:-len(api_path)]
    transport = api.call_api
    original_open = api.urlopen
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    captured = {}
    def mapped(path, request):
        status, payload = transport(path, request)
        captured["payload"] = payload
        if path == "/spApi/storeTokens":
            result = {"redacted": True, "transportHttpStatus": status}
        else:
            result = result_builder(status, payload) if result_builder else payload
        return status, result
    os.environ["LINKFOX_TOOL_GATEWAY"] = base
    try:
        with output_context():
            api.call_api = mapped
            if timeout != 150:
                # 按 timeout 参数设置超时；HTTP 由公共调用器构造与执行。
                api.urlopen = lambda request, **kwargs: original_open(request, timeout=timeout)
            argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
            if lf_inline_flag():
                argv.append("--inline")
            operation = "store-tokens" if api_path.endswith("storeTokens") else "create-upload-destination"
            if quiet or api_path.endswith("storeTokens"):
                with redirect_stdout(io.StringIO()):
                    api.run(api_path, f"{SLUG}-{operation}", argv=argv)
            else:
                api.run(api_path, f"{SLUG}-{operation}", argv=argv)
    finally:
        api.call_api = transport
        api.urlopen = original_open
        if previous_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = previous_gateway
    return captured.get("payload")


def developer_proxy_post(region: str, path: str, seller_id: str, *, query_string: Optional[str] = None,
                         timeout: int = 150, result_builder=None) -> dict:
    params = {"region": region, "path": path, "method": "POST", "sellerId": seller_id,
              "contentType": "application/json"}
    if query_string:
        params["queryString"] = query_string
    return call_api(DEVELOPER_PROXY_ENDPOINT, params, timeout=timeout, result_builder=result_builder)

def path_for_upload_destination(resource: str) -> str:
    """构造 Uploads greedy path；保留 resource 内作为路径分隔符的斜杠。"""
    res = str(resource).strip().lstrip("/")
    enc = quote(res, safe="/")
    return f"{UPLOADS_PATH_PREFIX}/uploadDestinations/{enc}"


def content_md5_base64(data: bytes) -> str:
    return base64.b64encode(hashlib.md5(data).digest()).decode("ascii")


def load_file_bytes(params: dict) -> bytes:
    if params.get("filePath"):
        p = Path(str(params["filePath"])).expanduser()
        if not p.is_file():
            print(f"filePath not found: {p}", file=sys.stderr)
            sys.exit(1)
        return p.read_bytes()
    if params.get("contentBase64"):
        try:
            return base64.b64decode(str(params["contentBase64"]))
        except Exception as e:
            print(f"Invalid contentBase64: {e}", file=sys.stderr)
            sys.exit(1)
    if "content" in params:
        raw = params["content"]
        if isinstance(raw, str):
            return raw.encode("utf-8")
        print("content must be a string", file=sys.stderr)
        sys.exit(1)
    return b""


def resolve_content_md5(params: dict) -> str:
    if params.get("contentMD5"):
        return str(params["contentMD5"]).strip()
    data = load_file_bytes(params)
    if not data:
        print(
            "Missing contentMD5, or provide filePath/content/contentBase64 to auto-compute.",
            file=sys.stderr,
        )
        sys.exit(1)
    return content_md5_base64(data)


def resolve_marketplace_id(params: dict) -> str:
    mid = params.get("marketplaceId")
    if mid is None and params.get("marketplaceIds") is not None:
        mids = params["marketplaceIds"]
        if isinstance(mids, list) and mids:
            mid = mids[0]
            if len(mids) > 1:
                print(
                    "Warning: createUploadDestinationForResource uses one marketplaceId; using first.",
                    file=sys.stderr,
                )
        elif isinstance(mids, str) and mids.strip():
            mid = mids.strip()
    if mid is None or not str(mid).strip():
        print("Missing marketplaceId (or marketplaceIds).", file=sys.stderr)
        sys.exit(1)
    return str(mid).strip()


def merge_success_json(
    out: dict,
    proxy: dict,
    result_key: str,
    *,
    success_http: Iterable[int] = SUCCESS_HTTP_STATUSES,
    transport_status: int | None = 200,
) -> None:
    if not is_normal_response(transport_status, proxy):
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
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(f"用法: {Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]\n字段与限制见 references/api.md")
        raise SystemExit(0)
    args = [a for a in sys.argv[1:] if a not in ("--inline", "--no-cache")]
    if not args:
        return {}
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须是对象", file=sys.stderr)
        raise SystemExit(1)
    return params

def require_seller_region(params: dict) -> tuple[str, str]:
    for f in ("sellerId", "region"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)
    return str(params["sellerId"]), str(params["region"])

def emit_result(result, slug=SLUG, inline=False):
    """非 LinkFox PUT 结果的本地落盘与摘要，不另起 HTTP 或缓存。"""
    with output_context():
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        out = api.resolve_data_path(f"{slug}-upload-file", time.time())
        Path(out).write_text(serialized, encoding="utf-8")
        print(f"Saved full response: {out} ({len(serialized.encode('utf-8'))} bytes)")
        if inline or len(serialized.encode("utf-8")) <= api.SMALL_THRESHOLD:
            print(serialized)
        else:
            api.summarize(result)

def lf_inline_flag() -> bool:
    return "--inline" in sys.argv[1:]
