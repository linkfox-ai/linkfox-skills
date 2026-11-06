"""Shopee Public 兼容映射；HTTP、落盘和输出统一委托公共调用器。"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import quote
import call_api as api

API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/shopee/developerProxy"
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-public"


def ensure_auth_skill_available(caller: str = "Public 脚本") -> None:
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    if not checker.is_file():
        payload = {"missingSkill": REQUIRED_SKILL, "reason": f"{caller} 旁缺少 check_auth_dependency.py"}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run([sys.executable, str(checker)], capture_output=True,
                                text=True, encoding="utf-8", timeout=10)
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


def normal_response(http_status, payload) -> bool:
    """外层 2xx 且 errcode 为空或 2xx；0/false 不是空。"""
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


def _writable_root() -> Path:
    root = Path.cwd().resolve() / "linkfox"
    if root == Path("/tmp") or Path("/tmp") in root.parents:
        raise OSError("本技能禁止写入 /tmp，请切换到可写项目目录。")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def call_api(endpoint: str, params: dict, *, transform: Optional[Callable] = None,
             slug: str = SLUG, inline: bool = False) -> dict:
    """将 HTTP 请求委托公共调用器，不启用响应缓存。"""
    if endpoint.startswith(API_BASE_URL + "/"):
        api_path = endpoint[len(API_BASE_URL):]
    elif endpoint.startswith("/"):
        api_path = endpoint
    else:
        raise ValueError("仅允许已配置网关的相对路径或兼容完整地址。")
    root = _writable_root()
    transport = api.call_api
    old_output = api._resolve_output_path
    old_root = api._SESSION_CACHE.get("_root")
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    result = {}

    def mapped_transport(path, request_params):
        nonlocal result
        status, payload = transport(path, request_params)
        result = transform(status, payload) if transform else payload
        return status, result

    # 仅映射业务结果；实际 HTTP 由公共调用器执行。
    api.call_api = mapped_transport
    api._SESSION_CACHE["_root"] = str(root)
    if not old_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = os.environ.get("SHOPEE_API_BASE_URL") or API_BASE_URL
    try:
        # 预检实际会话数据目录，避免请求完成后才发现 data 路径被文件占用或不可写。
        output_path = api.resolve_data_path(slug, time.time())
        with tempfile.TemporaryFile(dir=Path(output_path).parent):
            pass
        api._resolve_output_path = lambda _name, _ts: output_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            argv.append("--inline")
        api.run(api_path, slug, argv=argv)
        # 公共调用器打印写盘错误后仍会返回；业务封装必须把保存失败报告为错误。
        expected_text = json.dumps(result, ensure_ascii=False, indent=2)
        if not Path(output_path).is_file() or Path(output_path).read_text(encoding="utf-8") != expected_text:
            raise OSError(f"完整响应未成功保存：{output_path}")
        return result
    finally:
        api.call_api = transport
        api._resolve_output_path = old_output
        if old_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_gateway
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root


def resolve_store_tokens(params: dict) -> dict:
    shop_id, merchant_id = params.get("shopId"), params.get("merchantId")
    if not shop_id and not merchant_id:
        print("缺少必要字段：shopId 或 merchantId", file=sys.stderr)
        raise SystemExit(1)
    request = {}
    if shop_id:
        request["shopId"] = str(shop_id)
    if merchant_id:
        request["merchantId"] = str(merchant_id)
    return call_api(STORE_TOKENS_ENDPOINT, request, slug=f"{SLUG}-storeTokens")


def developer_proxy_call(path: str, method: str, shop_id: Optional[str] = None,
                         merchant_id: Optional[str] = None, query_string: Optional[str] = None,
                         body: Optional[str] = None, content_type: str = "application/json",
                         access_token: Optional[str] = None, *, transform: Optional[Callable] = None,
                         slug: str = SLUG, inline: bool = False) -> dict:
    if not path.startswith("api/v2"):
        print(f"path 必须以 api/v2 开头：{path!r}", file=sys.stderr)
        raise SystemExit(1)
    if not shop_id and not merchant_id:
        print("缺少必要字段：shopId 或 merchantId", file=sys.stderr)
        raise SystemExit(1)
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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, transform=transform, slug=slug, inline=inline)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    if not normal_response(out.get("transportHttpStatus", 200), proxy):
        return
    try:
        upstream_ok = int(proxy.get("httpStatus") or 0) == 200
    except (TypeError, ValueError):
        upstream_ok = False
    if not upstream_ok:
        return
    raw = proxy.get("body")
    try:
        parsed = json.loads(raw) if raw and str(raw).strip() else None
    except (TypeError, ValueError):
        parsed = None
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


