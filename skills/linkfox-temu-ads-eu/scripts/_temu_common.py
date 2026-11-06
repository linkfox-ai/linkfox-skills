#!/usr/bin/env python3
"""Shared helpers for LinkFox Temu API skill scripts."""

import json
import os
import sys
import time
import io
from contextlib import ExitStack, redirect_stdout
from unittest.mock import patch

import call_api as api

from _temu_token_store import get_token

BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("TEMU_API_BASE_URL")
    or os.environ.get("STORE_API_BASE_URL", "https://tool-gateway.linkfox.com")
)
BASE_URL = BASE_URL.rstrip("/")
PROXY_URL = f"{BASE_URL}/temu/proxy"
FILE_DOWNLOAD_URL = f"{BASE_URL}/temu/fileDownload"

VALID_SITES = frozenset({"cn", "partner", "us", "global", "eu"})
VALID_MANAGEMENT_TYPES = frozenset({"full-managed", "semi-managed"})

# LinkFox 用户 Token（网关鉴权），勿与 Body 中的 Temu accessToken 混淆
LINKFOX_TOKEN_PARAM_KEYS = ("token", "linkfoxToken", "linkfox_token")

def get_linkfox_token(params=None) -> str:
    """
    LinkFox 用户鉴权 Token，与 linkfox-amazon-store-auth 一致。
    优先级：请求 JSON 中的 token / linkfoxToken > 环境变量 LINKFOXAGENT_API_KEY。
    """
    if params:
        for key in LINKFOX_TOKEN_PARAM_KEYS:
            value = params.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "LinkFox user Token not configured. Same as linkfox-amazon-store-auth:\n"
            "1. Visit https://skill.linkfox.com/linkfoxskills/guide.htm to obtain your Key\n"
            "2. export LINKFOXAGENT_API_KEY=your-key-here\n"
            "   Or pass \"token\" in the JSON parameters of proxy/fileDownload scripts.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key

def build_gateway_headers(linkfox_token: str) -> dict:
    """网关鉴权：Authorization（全站通用）+ Token（TEMU_API_SPEC 约定）。"""
    return {
        "Authorization": linkfox_token,
        "Token": linkfox_token,
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }

def load_json_arg(argv: list) -> dict:
    if len(argv) < 2:
        return {}
    try:
        params = json.loads(argv[1])
        if not isinstance(params, dict):
            raise ValueError("JSON parameters must be an object")
        return params
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

def require_text(params: dict, key: str, label=None) -> str:
    value = params.get(key)
    if value is None or not str(value).strip():
        print(f"Error: '{label or key}' is required.", file=sys.stderr)
        sys.exit(1)
    return str(value).strip()

def validate_site(site: str) -> str:
    if site not in VALID_SITES:
        print(
            f"Error: invalid site '{site}'. Must be one of: {', '.join(sorted(VALID_SITES))}",
            file=sys.stderr,
        )
        sys.exit(1)
    return site

def validate_management_type(management_type: str) -> str:
    if management_type not in VALID_MANAGEMENT_TYPES:
        print(
            "Error: invalid managementType. Must be: full-managed, semi-managed",
            file=sys.stderr,
        )
        sys.exit(1)
    return management_type

def call_temu_api(
    url: str,
    body: dict,
    timeout: int = 150,
    linkfox_params=None,
) -> dict:
    """通过 call_api.run 执行网关请求，并适配 Temu 请求头、超时与输出目录。"""
    linkfox_token = get_linkfox_token(linkfox_params)
    # 业务要求当前目录可写；请求前探测，禁止公共调用器回退到其他目录。
    root = _lf_root()
    transport, request_factory, opener = api.call_api, api.Request, api.urlopen
    captured = {}

    def with_temu_body(api_path, request_params):
        status, result = transport(api_path, request_params)
        if isinstance(result, dict):
            result = dict(result)
            # HTTP 状态与网关 code / Temu errorCode 是不同层，必须随完整响应保留。
            result["transportHttpStatus"] = status
            if url.rstrip("/").endswith("/temu/proxy"):
                result = parse_nested_body(result)
        if status is None or not 200 <= status < 300:
            print(f"LinkFox 外层 HTTP 状态：{status}；完整错误见保存的响应。", file=sys.stderr)
        captured["result"] = result
        return status, result

    def with_legacy_headers(*args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers.update(build_gateway_headers(linkfox_token))
        kwargs["headers"] = headers
        return request_factory(*args, **kwargs)

    def with_legacy_timeout(request, **kwargs):
        kwargs["timeout"] = timeout
        return opener(request, **kwargs)

    output = io.StringIO()
    # 临时适配只作用于同步 CLI 调用；退出或异常时全部恢复，不改环境变量。
    with ExitStack() as stack:
        for name, value in {
            "get_api_key": lambda: linkfox_token,
            "get_api_url": lambda _path: url,
            "Request": with_legacy_headers,
            "urlopen": with_legacy_timeout,
            "call_api": with_temu_body,
            "_linkfox_root": lambda: root,
        }.items():
            stack.enter_context(patch.object(api, name, value))
        # 根目录可写不代表日期/会话/data 可写；请求前检查最终数据目录。
        out_path = api.resolve_data_path(SLUG, time.time())
        # 使用完整目标路径探测，也可在请求前发现 Windows 长路径或文件冲突。
        with open(out_path, "x", encoding="utf-8"):
            pass
        os.remove(out_path)
        stack.enter_context(patch.object(api, "_resolve_output_path", lambda _slug, _ts: out_path))
        stack.enter_context(redirect_stdout(output))
        argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
        if lf_inline_flag():
            argv.append("--inline")
        api.run("/temu/fileDownload" if url.rstrip("/").endswith("/temu/fileDownload") else "/temu/proxy", SLUG, argv=argv)
    result = _GatewayResult(captured["result"])
    result.output = output.getvalue()
    return result


class _GatewayResult(dict):
    """携带公共调用器已保存的输出，供 emit_result 展示而不重复落盘。"""

def is_linkfox_auth_error(result: dict) -> bool:
    msg = " ".join(str(result.get(key) or "") for key in ("message", "errmsg", "error"))
    return (
        result.get("transportHttpStatus") == 401
        or str(result.get("errcode", "")).strip() == "401"
        or "无法识别当前用户" in msg
        or "重新登录" in msg
    )


def is_normal_gateway_response(result: dict) -> bool:
    """按 references 公共规则判断 HTTP 与 errcode；不代替 Temu 业务判断。"""
    status = result.get("transportHttpStatus")
    if type(status) is not int or not 200 <= status < 300:
        return False
    # 公共调用器的该函数恰好实现同一 errcode 规则；200 仅用于检查响应体，
    # 实际 HTTP 的整个 2xx 范围已在上方验证，不启用任何响应缓存。
    return api._is_cacheable(200, result)

def resolve_access_token(params: dict) -> str:
    """Temu 店铺 accessToken：直接传入或从本地 storeKey 读取。"""
    if params.get("accessToken"):
        return str(params["accessToken"]).strip()
    store_key = params.get("storeKey")
    if not store_key:
        print(
            "Error: provide Temu 'accessToken' or 'storeKey' (+ site, managementType).",
            file=sys.stderr,
        )
        sys.exit(1)
    site = validate_site(require_text(params, "site"))
    management_type = validate_management_type(require_text(params, "managementType"))
    token_purpose = str(params.get("tokenPurpose", "default")).strip() or "default"
    token = get_token(str(store_key).strip(), site, management_type, token_purpose)
    if not token:
        print(
            f"Error: no Temu token for storeKey={store_key}, site={site}, "
            f"managementType={management_type}, tokenPurpose={token_purpose}. "
            "Run temu_token_guide.py and save_temu_access_token.py first.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token

def parse_nested_body(result: dict) -> dict:
    """If gateway returns a JSON string in body, parse it into temuBody."""
    body = result.get("body")
    if isinstance(body, str) and body.strip():
        try:
            result["temuBody"] = json.loads(body)
        except json.JSONDecodeError:
            pass
    return result

# ===== LinkFox 统一输出层（落盘 + 摘要，无缓存）=====
# 各入口脚本通过 emit_result() 保存完整响应并展示结果。

import time as _lf_time
import secrets as _lf_secrets
import tempfile as _lf_tempfile

LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict = {}

SLUG = "linkfox-temu-ads-eu"


def _lf_root() -> str:
    """只写 cwd；不可写时直接报错，不回退其他目录。"""
    cwd = os.path.abspath(os.getcwd())
    if cwd == "/tmp" or cwd.startswith("/tmp/"):
        raise OSError("本技能禁止将会话数据写入 /tmp，请切换到可写工作目录。")
    root = os.path.join(cwd, "linkfox")
    os.makedirs(root, exist_ok=True)
    with _lf_tempfile.TemporaryFile(dir=root):
        pass
    return root


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
    if isinstance(result, _GatewayResult):
        # 网关数据已由 run 保存并按 --inline 生成输出，避免重复保存同一响应。
        print(result.output, end="")
        return
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


def lf_inline_flag() -> bool:
    """入口脚本用：从 sys.argv 判断是否 --inline。"""
    return "--inline" in sys.argv
