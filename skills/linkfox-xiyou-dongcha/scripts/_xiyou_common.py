#!/usr/bin/env python3
"""Shared helpers for 西柚找词 (Xiyou) LinkFox gateway calls."""

import json
import os
import sys
import time
import secrets
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GATEWAY_BASE = (os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/") + "/xiyou"
TIMEOUT_SEC = 60

LINKFOX_KEY_DOC = (
    "https://skill.linkfox.com/linkfoxskills/guide.htm"
)
XIYOU_OPENAPI_PORTAL = (
    "https://www.xydc.com/openapi?xiyou-insights-web=%2Fopenapi"
)


def get_linkfox_api_key() -> str:
    key = (os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY", "")).strip()
    if not key:
        print(
            "未配置 LinkFox API Key。请先完成授权：\n"
            f"1. 前往 {LINKFOX_KEY_DOC} 获取 Key\n"
            "2. 设置环境变量：export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def get_xiyou_credentials() -> tuple[str, str]:
    client_id = os.environ.get("XIYOU_CLIENT_ID", "").strip()
    client_secret = os.environ.get("XIYOU_CLIENT_SECRET", "").strip()
    missing = []
    if not client_id:
        missing.append("XIYOU_CLIENT_ID")
    if not client_secret:
        missing.append("XIYOU_CLIENT_SECRET")
    if missing:
        print(
            "未配置西柚找词 OpenAPI 凭证。请在环境变量中设置：\n"
            f"  export XIYOU_CLIENT_ID=<16位 Client ID>\n"
            f"  export XIYOU_CLIENT_SECRET=<24位 Client Secret>\n"
            f"凭证获取地址：{XIYOU_OPENAPI_PORTAL}\n"
            f"缺少：{', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return client_id, client_secret


def merge_auth(params: dict) -> dict:
    client_id, client_secret = get_xiyou_credentials()
    payload = dict(params)
    payload["clientId"] = client_id
    payload["clientSecret"] = client_secret
    return payload


def call_xiyou_api(route: str, params: dict) -> dict:
    api_key = get_linkfox_api_key()
    url = f"{GATEWAY_BASE}/{route.lstrip('/')}"
    body = json.dumps(merge_auth(params), ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=TIMEOUT_SEC) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        detail = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": detail}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


# ===== LinkFox 统一输出层（落盘 + 摘要，无缓存）=====
# 本块追加到共享模块（_xxx_common.py）末尾，供各入口脚本调用 emit_result()。
# 依赖：json, os, sys, time, secrets, tempfile（共享模块通常已 import json/os/sys；
#       若缺 time/secrets/tempfile，请在文件顶部补 import）。

import time as _lf_time
import secrets as _lf_secrets
import tempfile as _lf_tempfile

LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict = {}

SLUG = "linkfox-xiyou-dongcha"


def _lf_root() -> str:
    cached = _LF_SESSION_CACHE.get("_root")
    if cached:
        return cached
    candidates = []
    acpx = (os.environ.get("ACPX_WORKSPACES") or "").strip()
    if acpx:
        acpx = acpx.split(os.pathsep)[0].strip()
        if acpx:
            candidates.append(os.path.join(acpx, "linkfox"))
    candidates.append(os.path.join(os.getcwd(), "linkfox"))
    candidates.append(os.path.join(os.path.expanduser("~"), "linkfox"))
    candidates.append(os.path.join(_lf_tempfile.gettempdir(), "linkfox"))
    for root in candidates:
        try:
            os.makedirs(root, exist_ok=True)
            probe = os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("")
            os.remove(probe)
        except OSError:
            continue
        root = os.path.abspath(root)
        _LF_SESSION_CACHE["_root"] = root
        return root
    fallback = os.path.abspath(candidates[-1])
    _LF_SESSION_CACHE["_root"] = fallback
    return fallback


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
