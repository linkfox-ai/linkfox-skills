"""广告业务兼容层：参数加工后由公共 run 负责 HTTP、落盘与输出。"""

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
from typing import Callable
from urllib.parse import quote

import call_api as api

API_PATH = "/shopee/developerProxy"
API_BASE_URL = os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com"
DEVELOPER_PROXY_ENDPOINT = API_BASE_URL.rstrip("/") + API_PATH
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-ads"


def ensure_auth_skill_available(caller: str = "ads script") -> None:
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    try:
        if not checker.is_file():
            raise FileNotFoundError(f"check_auth_dependency.py not found next to {caller}")
        result = subprocess.run([sys.executable, str(checker)], capture_output=True, text=True, timeout=10)
    except Exception as exc:
        print("DEPENDENCY_MISSING: " + json.dumps({"missingSkill": REQUIRED_SKILL, "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        raise SystemExit(DEPENDENCY_EXIT_CODE)


def is_normal_response(http_status, payload) -> bool:
    """按 HTTP 2xx 与 errcode 判断响应，0 和 false 不是空值。"""
    if type(http_status) is not int or not 200 <= http_status < 300:
        return False
    if not isinstance(payload, dict):
        return False
    # 公共函数对 errcode 的判断与公共文档相同，HTTP 2xx 已在上面独立判断。
    return api._is_cacheable(200, payload)


def build_proxy_params(path: str, method: str, shop_id=None, merchant_id=None,
                       query_string=None, body=None, content_type="application/json") -> dict:
    if not path.startswith("api/v2/ads/"):
        raise ValueError(f"广告 path 必须以 api/v2/ads/ 开头：{path!r}")
    if not shop_id and not merchant_id:
        raise ValueError("Missing required field: shopId OR merchantId")
    proxy = {"path": path, "method": method}
    if shop_id:
        proxy["shopId"] = str(shop_id)
    if merchant_id:
        proxy["merchantId"] = str(merchant_id)
    if query_string:
        proxy["queryString"] = query_string
    if body is not None:
        proxy["body"] = body
        proxy["contentType"] = content_type
    return proxy


def run_proxy(params: dict, operation: str, transform: Callable, *, emit=False, inline=False):
    """通过公共调用器执行请求、落盘与输出，始终禁用响应缓存。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 请求前确认 cwd 可写，不允许公共输出层回退到其他目录。
    with tempfile.TemporaryFile(dir=root):
        pass
    # 公共 run 在发请求前创建缓存目录，--no-cache 保证不读取或保存缓存。
    transport = api.call_api
    previous_output = api._resolve_output_path
    previous_root = api._SESSION_CACHE.get("_root")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    captured = {}

    def with_business_result(api_path, request_params):
        http_status, payload = transport(api_path, request_params)
        result = transform(http_status, payload)
        captured["result"] = result
        return http_status, result

    api.call_api = with_business_result
    api._SESSION_CACHE["_root"] = str(root)
    # 保留同秒内多次调用的完整数据，避免公共 run 的秒级时间戳覆盖响应。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    if not previous_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = os.environ.get("SHOPEE_API_BASE_URL") or api.get_api_base()
    argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    try:
        if emit:
            api.run(API_PATH, f"{SLUG}-{operation}", argv=argv)
        else:
            # 程序内调用保持返回 dict；CLI 才打印统一输出。
            with redirect_stdout(io.StringIO()):
                api.run(API_PATH, f"{SLUG}-{operation}", argv=argv)
        return captured["result"]
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        for key, value in (("LINKFOX_TOOL_GATEWAY", previous_gateway), ("ACPX_WORKSPACES", previous_workspace)):
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def call_api(endpoint: str, params: dict):
    """辅助函数兼容入口，同样只通过公共 run 访问网关。"""
    if endpoint != DEVELOPER_PROXY_ENDPOINT:
        raise ValueError("仅允许当前广告 developerProxy 端点")
    return run_proxy(params, params["path"].rsplit("/", 1)[-1], lambda _status, payload: payload)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    if not isinstance(proxy, dict):
        return
    try:
        if int(proxy.get("httpStatus") or 0) != 200:
            return
    except (TypeError, ValueError, OverflowError):
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
        out[key + "Response"] = parsed["response"]
