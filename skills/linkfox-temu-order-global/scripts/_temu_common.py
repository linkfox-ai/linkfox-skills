#!/usr/bin/env python3
"""Shared helpers for LinkFox Temu API skill scripts."""

import json
import re
import os
import sys
import time
import tempfile
from contextlib import redirect_stdout
import io
from unittest.mock import patch
from urllib.parse import urlsplit
import call_api

from _temu_token_store import get_token

BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("TEMU_API_BASE_URL")
    or os.environ.get("STORE_API_BASE_URL")
    or "https://tool-gateway.linkfox.com"
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
        return json.loads(argv[1])
    except json.JSONDecodeError as e:
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

# 只记录最近一次公共 run 的落盘结果，避免外层 emit_result 重复写文件；不是响应缓存。
_LAST_SAVED = None


def call_temu_api(
    url: str,
    body: dict,
    timeout: int = 150,
    linkfox_params=None,
) -> dict:
    """以公共 run 调用网关，应用认证、地址、超时设置并解析 Temu body。"""
    global _LAST_SAVED
    _LAST_SAVED = None
    linkfox_token = get_linkfox_token(linkfox_params)
    _lf_root()  # 请求前验证当前工作目录可写；不回退到其他目录。
    parsed_url = urlsplit(url)
    api_path = parsed_url.path
    if parsed_url.query:
        api_path += "?" + parsed_url.query
    operation = re.sub(r"[^A-Za-z0-9_-]+", "-", str(body.get("type") or "fileDownload"))
    slug = f"{SLUG}-{operation}"
    original_request = call_api.Request
    original_open = call_api.urlopen
    original_transport = call_api.call_api
    original_output = call_api._resolve_output_path
    recorded = {}

    def request_with_legacy_headers(*args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers.update(build_gateway_headers(linkfox_token))
        kwargs["headers"] = headers
        return original_request(*args, **kwargs)

    def open_with_timeout(request, **kwargs):
        kwargs["timeout"] = timeout
        return original_open(request, **kwargs)

    def transport(path, params):
        status, result = original_transport(path, params)
        if not isinstance(result, dict):
            result = {"body": result}
        result["transportHttpStatus"] = status
        if api_path.split("?", 1)[0].endswith("/temu/proxy"):
            parse_nested_body(result)
        recorded["result"] = result
        return status, result

    def output_path(slug, ts):
        return recorded["path"]

    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if lf_inline_flag():
        argv.append("--inline")
    # 兼容仅在单次调用内生效；不修改公共调用器文件，也不污染环境变量。
    with patch.object(call_api, "get_api_key", return_value=linkfox_token), \
         patch.object(call_api, "get_api_url", return_value=url), \
         patch.object(call_api, "Request", request_with_legacy_headers), \
         patch.object(call_api, "urlopen", open_with_timeout), \
         patch.object(call_api, "call_api", transport), \
         patch.object(call_api, "_linkfox_root", _lf_root), \
         patch.object(call_api, "_resolve_output_path", output_path), \
         redirect_stdout(io.StringIO()):
        # 在请求前检查实际 data 目录，避免请求已执行才发现无法保存结果。
        # 公共 run 使用秒级时间；业务封装使用微秒时间戳生成文件名。
        recorded["path"] = original_output(slug, time.time())
        with tempfile.NamedTemporaryFile(
            dir=os.path.dirname(recorded["path"]), prefix=".write_probe-", delete=True
        ):
            pass
        call_api.run(api_path, slug, argv)
    result = recorded["result"]
    _LAST_SAVED = (result, recorded["path"])
    return result


def is_linkfox_auth_error(result: dict) -> bool:
    msg = " ".join(str(result.get(key) or "") for key in ("message", "error", "errmsg", "msg"))
    return "无法识别当前用户" in msg or "重新登录" in msg


def is_gateway_response_normal(result: dict) -> bool:
    """仅判断外层 HTTP 与 errcode，保留公共响应码基本规则。"""
    status = result.get("transportHttpStatus")
    if type(status) is not int or not 200 <= status < 300:
        return False
    errcode = result.get("errcode")
    if errcode is None:
        return True
    if isinstance(errcode, str):
        errcode = errcode.strip()
        if not errcode:
            return True
        try:
            errcode = int(errcode)
        except ValueError:
            return False
    return type(errcode) in (int, float) and 200 <= errcode < 300 and errcode % 1 == 0

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
# 统一输出辅助函数，供各入口脚本调用 emit_result()。
# 依赖：json, os, sys, time, secrets, tempfile（共享模块通常已 import json/os/sys；
#       若缺 time/secrets/tempfile，请在文件顶部补 import）。

import time as _lf_time
import secrets as _lf_secrets

LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict = {}

SLUG = "linkfox-temu-order-global"


def _lf_root() -> str:
    """只使用 cwd/linkfox，不回退到家目录或临时目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    # 使用唯一探测文件，避免影响已有文件或并发调用。
    with tempfile.NamedTemporaryFile(dir=root, prefix=".write_probe-", delete=True):
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
    """复用公共 run 已保存的完整结果，按 CLI 摘要策略和 --inline 选项输出。"""
    global _LAST_SAVED
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    if _LAST_SAVED is not None and _LAST_SAVED[0] is result:
        out = _LAST_SAVED[1]
        _LAST_SAVED = None
        if not os.path.isfile(out):
            raise OSError(f"完整响应未保存：{out}")
    else:
        ts = time.time()
        date_str = _lf_time.strftime("%Y-%m-%d", _lf_time.localtime(ts))
        sid = _lf_session_id(ts)
        root = _lf_root()
        session_dir = os.path.join(root, date_str, sid)
        os.makedirs(session_dir, exist_ok=True)
        _lf_ensure_meta(root, session_dir, date_str, sid, ts)
        data_dir = os.path.join(session_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        out = os.path.join(data_dir, f"{slug}-{int(ts * 1_000_000)}.json")
        with open(out, "w", encoding="utf-8") as f:
            f.write(serialized)
        _lf_update_meta(session_dir, skill=slug, file_rel=os.path.relpath(out, session_dir), ts=ts)
    print(f"Saved full response: {out} ({len(serialized.encode('utf-8'))} bytes)")
    if inline or len(serialized.encode("utf-8")) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        _lf_summarize(result)


def lf_inline_flag() -> bool:
    """入口脚本用：从 sys.argv 判断是否 --inline。"""
    return "--inline" in sys.argv
