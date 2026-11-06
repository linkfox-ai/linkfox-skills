"""Shopee 商户查询的认证依赖、参数兼容与公共调用器适配。"""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any, Optional
from urllib.parse import quote

import call_api as api

API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/shopee/developerProxy"
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-merchant"


def ensure_auth_skill_available(caller: str = "merchant script") -> None:
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


get_api_key = api.get_api_key


def is_normal_response(status, payload) -> bool:
    """严格按文档的外层 HTTP 与 errcode 基础规则判断。"""
    if type(status) is not int or not 200 <= status < 300 or not isinstance(payload, dict):
        return False
    return api._is_cacheable(200, payload)


def _prepare_output_root() -> Path:
    """要求当前目录可写，公共调用器不得回退至其他目录。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def call_api(endpoint: str, params: dict, *, transform=None, operation=None,
             emit_output=False, inline=False) -> Any:
    """通过公共 run 调用；返回 Python 结果并统一保存加工结果。"""
    endpoints = {
        DEVELOPER_PROXY_ENDPOINT: "/shopee/developerProxy",
        STORE_TOKENS_ENDPOINT: "/shopee/storeTokens",
    }
    if endpoint not in endpoints:
        raise ValueError("仅支持本技能定义的 LinkFox 端点")
    root = _prepare_output_root()
    transport = api.call_api
    previous_output_path = api._resolve_output_path
    previous_root = api._SESSION_CACHE.get("_root")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    result_holder = []

    def with_merchant_result(path, request_params):
        status, proxy = transport(path, request_params)
        result = transform(status, proxy) if transform else proxy
        result_holder.append(result)
        # 公共输出器要求对象；兼容辅助函数仍向 Python 调用方返回原始 JSON。
        return status, result if isinstance(result, dict) else {"response": result}

    argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    slug = f"{SLUG}-{operation}" if operation else SLUG
    try:
        # 适配仅在此次同步调用中生效，finally 恢复所有公共状态。
        api.call_api = with_merchant_result
        api._SESSION_CACHE["_root"] = str(root)
        os.environ["LINKFOX_TOOL_GATEWAY"] = API_BASE_URL
        # 请求前验证真实会话数据目录，而不只验证 linkfox 根目录。
        output_path = Path(api.resolve_data_path(slug, time.time()))
        with tempfile.TemporaryFile(dir=output_path.parent):
            pass
        api._resolve_output_path = lambda _slug, _ts: str(output_path)
        if emit_output:
            api.run(endpoints[endpoint], slug, argv=argv)
        else:
            with redirect_stdout(io.StringIO()):
                api.run(endpoints[endpoint], slug, argv=argv)
        # 公共 run 会捕获写入错误；封装必须将未完整保存视为失败。
        result = result_holder[0]
        saved_result = result if isinstance(result, dict) else {"response": result}
        if output_path.read_text(encoding="utf-8") != json.dumps(saved_result, ensure_ascii=False, indent=2):
            raise OSError(f"完整响应未成功保存：{output_path}")
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        if previous_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = previous_gateway
    return result_holder[0]


def resolve_store_tokens(params: dict) -> Any:
    """提供令牌查询兼容辅助入口；常规商户查询由 developerProxy 解析令牌。"""
    shop_id = params.get("shopId")
    merchant_id = params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)
    token_req = {}
    if shop_id:
        token_req["shopId"] = str(shop_id)
    if merchant_id:
        token_req["merchantId"] = str(merchant_id)
    return call_api(STORE_TOKENS_ENDPOINT, token_req, operation="storeTokens")


def developer_proxy_call(
    path: str, method: str, shop_id: Optional[str] = None,
    merchant_id: Optional[str] = None, query_string: Optional[str] = None,
    body: Optional[str] = None, content_type: str = "application/json",
    access_token: Optional[str] = None, *, transform=None, operation=None,
    emit_output=False, inline=False,
) -> Any:
    if not path.startswith("api/v2"):
        print(f"Error: path must start with 'api/v2', got {path!r}", file=sys.stderr)
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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, transform=transform,
                    operation=operation, emit_output=emit_output, inline=inline)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    if not isinstance(proxy, dict):
        return
    # int() 兼容数字和数字字符串；非法状态直接返回。
    try:
        status = int(proxy.get("httpStatus") or 0)
    except (TypeError, ValueError, OverflowError):
        return
    if status != 200:
        return
    body_raw = proxy.get("body")
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except (TypeError, json.JSONDecodeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


