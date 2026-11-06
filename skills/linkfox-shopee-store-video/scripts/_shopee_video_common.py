"""Shared helpers for linkfox-shopee-store-video (storeTokens + developerProxy)."""

from __future__ import annotations

import json
import io
from contextlib import contextmanager, redirect_stdout, redirect_stderr

import call_api as api
import os
import subprocess
import sys
import time
import tempfile
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("SHOPEE_API_BASE_URL")
    or "https://tool-gateway.linkfox.com"
)
API_BASE_URL = API_BASE_URL.rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/shopee/developerProxy"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "video script") -> None:
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
    """以字典返回网关数据，同时携带外层 HTTP 状态供业务解析判断。"""

    def __init__(self, payload, http_status):
        super().__init__(payload)
        self.transport_http_status = http_status


@contextmanager
def local_output_context():
    """在请求前验证 cwd 可写；公共资源本身保持不变。"""
    cwd = Path.cwd().resolve()
    temp_roots = {Path(tempfile.gettempdir()).resolve(), Path('/tmp').resolve()}
    if any(cwd == root or root in cwd.parents for root in temp_roots):
        raise OSError('本技能禁止在临时目录中保存数据，请选择可写的项目目录')
    root = cwd / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_workspace = os.environ.get('ACPX_WORKSPACES')
    previous_gateway = os.environ.get('LINKFOX_TOOL_GATEWAY')
    previous_root = api._SESSION_CACHE.get('_root')
    previous_path = api._resolve_output_path
    os.environ['ACPX_WORKSPACES'] = str(cwd)
    if not previous_gateway:
        os.environ['LINKFOX_TOOL_GATEWAY'] = API_BASE_URL
    api._SESSION_CACHE['_root'] = str(root)
    # 公共 run 使用秒级时间；业务层保留每次调用的独立微秒文件名。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        yield
    finally:
        api._resolve_output_path = previous_path
        for name, old in (('ACPX_WORKSPACES', previous_workspace), ('LINKFOX_TOOL_GATEWAY', previous_gateway)):
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old
        if previous_root is None:
            api._SESSION_CACHE.pop('_root', None)
        else:
            api._SESSION_CACHE['_root'] = previous_root


def gateway_ok(http_status, payload):
    """按固定基础规则判断网关状态，0 和 false 均为错误。"""
    if not isinstance(payload, dict) or http_status is None or not 200 <= http_status < 300:
        return False
    code = payload.get('errcode')
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


def call_api(endpoint: str, params: dict) -> dict:
    """按 endpoint 和 params 调用网关；所有 LinkFox 业务 HTTP 由公共 run 完成，无响应缓存。"""
    prefix = API_BASE_URL + '/'
    if not endpoint.startswith(prefix):
        raise ValueError('endpoint 必须属于当前配置的 LinkFox 网关')
    api_path = endpoint[len(API_BASE_URL):]
    transport = api.call_api
    received = {}

    def capture(path, request):
        status, payload = transport(path, request)
        if not isinstance(payload, dict):
            payload = {'error': '网关响应不是 JSON 对象', 'response': payload}
        result = GatewayResponse(payload, status)
        received['result'] = result
        return status, result

    with local_output_context():
        api.call_api = capture
        try:
            # run 负责原始响应落盘；最终加工结果由 emit_result 展示，避免重复打印。
            output, errors = io.StringIO(), io.StringIO()
            try:
                with redirect_stdout(output), redirect_stderr(errors):
                    api.run(api_path, SLUG + '-gateway', argv=[json.dumps(params, ensure_ascii=False), '--no-cache', '--inline'])
            finally:
                # 公共调用器将保存错误写到 stderr；认证退出时也须保留原诊断。
                sys.stderr.write(errors.getvalue())
            for line in output.getvalue().splitlines():
                if line.startswith('Saved full response:'):
                    print(line, file=sys.stderr)
                elif line.startswith('Failed to save'):
                    raise OSError(line)
            failures = [line for line in errors.getvalue().splitlines()
                        if line.startswith('Failed to save')]
            if failures:
                raise OSError('\n'.join(failures))
        finally:
            api.call_api = transport
    return received['result']


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
    status = getattr(proxy, 'transport_http_status', 200)
    if not gateway_ok(status, proxy):
        return
    try:
        upstream_ok = int(proxy.get('httpStatus') or 0) == 200
    except (TypeError, ValueError):
        upstream_ok = False
    if not upstream_ok:
        return
    body_raw = proxy.get('body')
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except (TypeError, json.JSONDecodeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get('response') is not None:
        out[f'{key}Response'] = parsed['response']


SLUG = 'linkfox-shopee-store-video'
LF_SMALL_THRESHOLD = api.SMALL_THRESHOLD


def emit_result(result, slug=SLUG, inline=False):
    """完整业务结果保存到 cwd；大响应输出公共摘要。"""
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    with local_output_context():
        path = api.resolve_data_path(slug, time.time())
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(serialized)
    print(f'Saved full response: {path} ({len(serialized.encode("utf-8"))} bytes)')
    if inline or len(serialized.encode('utf-8')) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        api.summarize(result)


def lf_inline_flag() -> bool:
    return '--inline' in sys.argv
