"""Shopee 折扣的依赖、参数编码与公共调用器兼容封装，无响应缓存。"""

from __future__ import annotations

import json
import argparse
import call_api as api
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

API_BASE_URL = os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com"
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "discount script") -> None:
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


def gateway_ok(http_status, payload) -> bool:
    """与公共响应规则一致：errcode 的 0、false 和非 2xx 值均非成功。"""
    if type(http_status) is not int or not 200 <= http_status < 300 or not isinstance(payload, dict):
        return False
    errcode = payload.get("errcode")
    if errcode is None or (isinstance(errcode, str) and not errcode.strip()):
        return True
    if isinstance(errcode, str):
        value = errcode.strip()
        if len(value) != 3 or not value.isascii() or not value.isdigit():
            return False
        errcode = int(value)
    return type(errcode) in (int, float) and 200 <= errcode < 300 and errcode % 1 == 0


def call_api(endpoint: str, params: dict, *, result_builder=None, operation="proxy") -> dict:
    """经公共 run 完成传输与唯一一次落盘，并返回业务响应结构。"""
    # 本封装负责地址兼容、cwd 保护和业务响应加工。
    get_api_key()
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 自定义网关基础地址可能带路径前缀，不能把整个 URL path 都剥掉。
    base, suffix = endpoint.rsplit("/shopee/", 1)
    api_path = "/shopee/" + suffix
    transport = api.call_api
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output = api._resolve_output_path
    captured = {}

    def with_result(api_path, request_params):
        status, proxy = transport(api_path, request_params)
        result = result_builder(status, proxy) if result_builder else proxy
        captured["result"] = result
        return status, result

    os.environ["LINKFOX_TOOL_GATEWAY"] = base.rstrip("/")
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    api._SESSION_CACHE["_root"] = str(root)
    api.call_api = with_result
    output_path = None
    output_reserved = False
    try:
        # 请求前检查真实会话目录和目标文件，不能只探测 linkfox 根目录。
        # 独占创建也避免同一时间戳的请求覆盖已保存的响应。
        output_path = api.resolve_data_path(f"linkfox-shopee-store-discount-{operation}", time.time())
        with open(output_path, "x", encoding="utf-8"):
            pass
        output_reserved = True
        api._resolve_output_path = lambda slug, _ts: output_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        api.run(api_path, f"linkfox-shopee-store-discount-{operation}", argv=argv)
        return captured["result"]
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        for env_name, previous in (("LINKFOX_TOOL_GATEWAY", previous_gateway), ("ACPX_WORKSPACES", previous_workspace)):
            if previous is None:
                os.environ.pop(env_name, None)
            else:
                os.environ[env_name] = previous
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        if output_reserved:
            # 只移除本次成功预留、但未写入响应的空文件。
            try:
                reserved = Path(output_path)
                if reserved.stat().st_size == 0:
                    reserved.unlink()
            except OSError:
                pass


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
    return call_api(STORE_TOKENS_ENDPOINT, token_req, operation="store-tokens")


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
    operation="proxy",
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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, result_builder=result_builder, operation=operation)




def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    try:
        status = int(proxy.get("httpStatus") or 0)
    except (TypeError, ValueError):
        return
    if status != 200:
        return
    body_raw = proxy.get("body")
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]

def discount_cli(api_name=None) -> None:
    """提供专用和通用 JSON CLI，统一帮助、参数错误与输出。"""
    from _discount_api_runner import run_discount_api
    from _discount_endpoints import list_api_names

    parser = argparse.ArgumentParser(description="Shopee 店铺折扣管理：" + (api_name or "、".join(list_api_names())))
    parser.add_argument("params", help="JSON 对象；通用入口需包含 api")
    parser.add_argument("--inline", action="store_true", help="完整输出，同时落盘")
    parser.add_argument("--no-cache", action="store_true", help="兼容选项；所有操作始终禁用响应缓存")
    if len(sys.argv) == 1:
        parser.print_usage(sys.stderr)
        raise SystemExit(1)
    args = parser.parse_args()
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        print(f"Invalid parameter format: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        raise SystemExit(1)
    selected = api_name or params.get("api")
    if not selected:
        print("Missing required field: api", file=sys.stderr)
        raise SystemExit(1)
    run_discount_api(str(selected), params, Path(sys.argv[0]).name)
