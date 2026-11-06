"""Feeds 参数加工与统一调用；使用 sellerId 和 region，不启用响应缓存。"""

from __future__ import annotations

import json
import io
from contextlib import contextmanager, redirect_stdout
import call_api as api
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable, Optional

from urllib.parse import quote

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42

FEEDS_API_VERSION = "2021-06-30"
FEEDS_PATH_PREFIX = f"feeds/{FEEDS_API_VERSION}"

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("STORE_API_BASE_URL")
    or os.environ.get("SPAPI_BASE_URL", "https://tool-gateway.linkfox.com")
).rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/spApi/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/spApi/developerProxy"

SUCCESS_HTTP_STATUSES = frozenset({200, 201, 202, 204})


def ensure_auth_skill_available(caller: str = "feeds script") -> None:
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


_LAST_CALL: dict = {}
SLUG = "linkfox-amazon-store-feeds"
LF_SMALL_THRESHOLD = 8000


@contextmanager
def _local_output_context():
    """会话数据写入当前目录，不使用公共调用器的目录回退。"""
    root = Path.cwd() / "linkfox"
    resolved = root.resolve().as_posix()
    if resolved == "/tmp" or resolved.startswith("/tmp/"):
        raise OSError("本技能禁止将会话数据写入 /tmp，请切换至可写的项目目录。")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_root = api._SESSION_CACHE.get("_root")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    try:
        api._SESSION_CACHE["_root"] = str(root)
        if not previous_gateway:
            os.environ["LINKFOX_TOOL_GATEWAY"] = (
                os.environ.get("STORE_API_BASE_URL")
                or os.environ.get("SPAPI_BASE_URL")
                or API_BASE_URL
            ).rstrip("/")
        # 仅探测 linkfox 根目录不足以保证会话 data 目录可写。
        # 在任何请求（包括有副作用的提交与上传）前检查实际目标目录。
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        yield
    finally:
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        if previous_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = previous_gateway


def ensure_output_available() -> None:
    """供预签名上传等非网关操作在请求前检查输出目录。"""
    with _local_output_context():
        pass


def call_api(endpoint: str, params: dict, timeout: int = 150) -> dict:
    """以指定端点、参数和超时调用；HTTP、持久化由 call_api.run 执行。"""
    # 默认超时为 150s；自定义超时由业务适配层传入底层请求。
    if endpoint == STORE_TOKENS_ENDPOINT:
        api_path = "/spApi/storeTokens"
    elif endpoint == DEVELOPER_PROXY_ENDPOINT:
        api_path = "/spApi/developerProxy"
    else:
        raise ValueError("Unsupported LinkFox endpoint")
    transport = api.call_api
    opener = api.urlopen
    resolver = api._resolve_output_path
    captured = {}
    _LAST_CALL.clear()

    def capture_transport(path, request):
        status, payload = transport(path, request)
        captured.update(status=status, payload=payload)
        return status, payload

    def capture_path(slug, _ts):
        output = api.resolve_data_path(slug, time.time())
        captured["output"] = output
        return output

    def with_timeout(request, **kwargs):
        # 仅调整公共 transport 的超时，不复制 HTTP、认证或重试逻辑。
        kwargs["timeout"] = timeout
        return opener(request, **kwargs)

    with _local_output_context():
        api.call_api = capture_transport
        api._resolve_output_path = capture_path
        if timeout != 150:
            api.urlopen = with_timeout
        try:
            # 所有操作（尤其创建与取消）始终绕过响应缓存读写。
            argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
            if lf_inline_flag():
                argv.append("--inline")
            with redirect_stdout(io.StringIO()):
                api.run(api_path, SLUG, argv=argv)
        finally:
            api.call_api = transport
            api.urlopen = opener
            api._resolve_output_path = resolver
    _LAST_CALL.update(captured)
    return captured["payload"]


def developer_proxy_call(
    region: str, path: str, method: str, seller_id: str, *,
    query_string: Optional[str] = None, body: Optional[str] = None,
    content_type: str = "application/json", timeout: int = 150,
) -> dict:
    params: dict[str, Any] = {
        "region": region, "path": path, "method": method, "sellerId": seller_id,
    }
    if query_string:
        params["queryString"] = query_string
    if body is not None:
        params["body"] = body
        params["contentType"] = content_type
    return call_api(DEVELOPER_PROXY_ENDPOINT, params, timeout=timeout)


def encode_path_segment(value: str) -> str:
    return quote(str(value).strip(), safe="")


def str_list(val: object, name: str) -> list[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    print(f"{name} must be a string or string[]", file=sys.stderr)
    sys.exit(1)


def norm_marketplace_ids(params: dict) -> list[str]:
    mids = params.get("marketplaceIds")
    if mids is None:
        mid = params.get("marketplaceId")
        if mid is not None:
            return [str(mid).strip()]
        return []
    return str_list(mids, "marketplaceIds")


def merge_success_json(
    out: dict,
    proxy: dict,
    result_key: str,
    *,
    success_http: Iterable[int] = SUCCESS_HTTP_STATUSES,
) -> None:
    # 基础规则由接口公共规则定义；外层失败时不解析为业务成功。
    external_status = _LAST_CALL.get("status", 200)
    if (not isinstance(external_status, int) or not 200 <= external_status < 300
            or not isinstance(proxy, dict) or not api._is_cacheable(200, proxy)):
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
        out[result_key] = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
    except json.JSONDecodeError:
        out[result_key] = None
        out[f"{result_key}Raw"] = body_raw


def load_cli_params() -> dict:
    if len(sys.argv) < 2:
        return {}
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        sys.exit(1)
    return params


def require_seller_region(params: dict) -> tuple[str, str]:
    for f in ("sellerId", "region"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)
    return str(params["sellerId"]), str(params["region"])


def emit_result(result, slug=SLUG, inline=False):
    """将解析结果覆盖至同次 run 的响应文件，输出业务字段且只展示一次。"""
    pending = bool(_LAST_CALL) and result.get("developerProxy") is _LAST_CALL.get("payload")
    if pending:
        result["transportHttpStatus"] = _LAST_CALL.get("status")
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    with _local_output_context():
        # 非 LinkFox 的预签名上传也沿用同一输出结构，但不经过网关。
        output = _LAST_CALL.get("output") if pending else api.resolve_data_path(slug, time.time())
        Path(output).write_text(serialized, encoding="utf-8")
    if pending:
        _LAST_CALL.clear()
    print(f"Saved full response: {output} ({len(serialized)} bytes)")
    if inline or len(serialized.encode("utf-8")) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        api.summarize(result)


def lf_inline_flag() -> bool:
    """检测 JSON 参数后的 --inline CLI 选项。"""
    return "--inline" in sys.argv
