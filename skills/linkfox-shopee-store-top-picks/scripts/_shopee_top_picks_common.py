"""精选集合调用适配、认证依赖和兼容输出；HTTP 统一交给公共调用器。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import contextlib
import io

import call_api as api
import tempfile
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("SHOPEE_API_BASE_URL")
    or "https://tool-gateway.linkfox.com"
).rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "top-picks script") -> None:
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


def get_api_key() -> str:
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和算力问题** 处理。
    """
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key 未配置",
            file=sys.stderr,
        )
        sys.exit(1)
    return key



SLUG = "linkfox-shopee-store-top-picks"


@contextlib.contextmanager
def _runtime():
    """固定可写工作目录及兼容网关别名，退出时恢复公共模块状态。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    old_workspace = os.environ.get("ACPX_WORKSPACES")
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    old_root = api._SESSION_CACHE.get("_root")
    old_resolver = api._resolve_output_path
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    os.environ["LINKFOX_TOOL_GATEWAY"] = API_BASE_URL
    api._SESSION_CACHE["_root"] = str(root)
    # 公共 runner 传入秒级时间戳；业务层使用微秒级时间戳命名。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        # 先检查实际会话 data 目录，避免请求完成后才发现无法保存结果。
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        yield
    finally:
        api._resolve_output_path = old_resolver
        for name, old in (("ACPX_WORKSPACES", old_workspace), ("LINKFOX_TOOL_GATEWAY", old_gateway)):
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root


def _token_snapshot(payload):
    """令牌接口无已知完整 schema，只在内存保留原值，持久化非状态字段一律隐藏。"""
    if not isinstance(payload, dict):
        return {"redacted": True}
    safe = {"errcode", "code", "httpStatus", "success"}
    return {
        key: value if key in safe and (value is None or type(value) in (int, float, bool)) else "[REDACTED]"
        for key, value in payload.items()
    }


def call_api(endpoint: str, params: dict, result_builder=None) -> dict:
    """通过 run 完成 HTTP、落盘和输出，关闭响应缓存。"""
    get_api_key()
    endpoint_map = {
        STORE_TOKENS_ENDPOINT: "/shopee/storeTokens",
        DEVELOPER_PROXY_ENDPOINT: "/shopee/developerProxy",
    }
    if endpoint not in endpoint_map:
        raise ValueError("不支持的精选模块端点")
    private = endpoint == STORE_TOKENS_ENDPOINT
    transport = api.call_api
    captured = {}

    def process(api_path, request_params):
        status, payload = transport(api_path, request_params)
        result = result_builder(payload, status) if result_builder else payload
        captured["result"] = result
        snapshot = _token_snapshot(result) if private else result
        return status, snapshot

    operation = params.get("path", "storeTokens").rsplit("/", 1)[-1]
    with _runtime():
        api.call_api = process
        try:
            argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
            if lf_inline_flag():
                argv.append("--inline")
            # 内部令牌响应不打印；保存的副本仍由 run 写入且已脱敏。
            with contextlib.redirect_stdout(io.StringIO()) if private else contextlib.nullcontext():
                api.run(endpoint_map[endpoint], f"{SLUG}-{operation}", argv=argv)
        finally:
            api.call_api = transport
    return captured["result"]


def resolve_store_tokens(params: dict) -> dict:
    shop_id, merchant_id = params.get("shopId"), params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)
    request = {}
    if shop_id:
        request["shopId"] = str(shop_id)
    if merchant_id:
        request["merchantId"] = str(merchant_id)
    return call_api(STORE_TOKENS_ENDPOINT, request)


def developer_proxy_call(
    path: str,
    method: str,
    shop_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    query_string: Optional[str] = None,
    body: Optional[str] = None,
    content_type: str = "application/json",
    access_token: Optional[str] = None,
    result_builder=None,
) -> dict:
    if not path.startswith("api/v2/top_picks/"):
        print(f"Error: path must start with 'api/v2/top_picks/', got {path!r}", file=sys.stderr)
        sys.exit(1)
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)
    proxy: dict[str, Any] = {"path": path, "method": method}
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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, result_builder=result_builder)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    status = proxy.get("httpStatus")
    if str(status) != "200":
        return
    raw = proxy.get("body")
    if not raw or not str(raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


def lf_inline_flag() -> bool:
    """判断 CLI 是否指定 --inline。"""
    return "--inline" in sys.argv


def load_cli_params() -> dict:
    """CLI 接受 JSON 对象；在请求前报告无效 JSON 或错误的顶层类型。"""
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误：{exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须是对象", file=sys.stderr)
        sys.exit(1)
    return params
