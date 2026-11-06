"""Shared helpers for linkfox-shopee-store-media-space (storeTokens + developerProxy)."""

from __future__ import annotations

import json
import base64
import mimetypes
import os
import subprocess
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from threading import RLock
import call_api as gateway
from urllib.parse import urlsplit
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

API_BASE_URL = os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com"
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"
UPLOAD_IMAGE_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/uploadMediaSpaceImage"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "media-space script") -> None:
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


_GATEWAY_LOCK = RLock()


def call_api(endpoint: str, params: dict) -> dict:
    """通过公共 run 调用网关，不创建响应缓存。"""
    get_api_key()
    parsed = urlsplit(endpoint)
    # 兼容自定义基础地址包含路径前缀；只剥离实际注册的末端点。
    api_path = next((suffix for suffix in (
        "/shopee/developerProxy", "/shopee/uploadMediaSpaceImage", "/shopee/storeTokens"
    ) if parsed.path.endswith(suffix)), None)
    if api_path is None:
        raise ValueError(f"Unsupported media-space endpoint: {endpoint}")
    base = endpoint[:-len(api_path)].rstrip("/")
    captured = {}
    with _GATEWAY_LOCK:
        original_call = gateway.call_api
        original_base = gateway.get_api_base
        original_root = gateway._linkfox_root
        original_path = gateway._resolve_output_path
        original_session = gateway._session_id

        def capture(path, payload):
            status, result = original_call(path, payload)
            captured.update(status=status, result=result)
            return status, result if isinstance(result, dict) else {"rawResponse": result}

        def output_path(slug, ts):
            return prepared_output

        # 在请求前验证当前工作目录可写，不使用公共调用器的目录回退。
        _lf_root()
        gateway.call_api = capture
        gateway.get_api_base = lambda: base
        gateway._linkfox_root = _lf_root
        gateway._resolve_output_path = output_path
        gateway._session_id = _lf_session_id
        try:
            slug = SLUG + "-" + api_path.rsplit("/", 1)[-1] + "-gateway"
            # 先创建真实会话目录和元数据并探测目标文件可写；避免请求后才发现落盘失败。
            prepared_output = gateway.resolve_data_path(slug, _lf_time.time())
            with open(prepared_output, "x", encoding="utf-8"):
                pass
            with redirect_stdout(io.StringIO()) as log, redirect_stderr(io.StringIO()) as errors:
                gateway.run(api_path, slug,
                            argv=[json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"])
            # 原始响应已落盘；只转发路径提示，业务结果由 CLI 输出。
            if errors.getvalue():
                sys.stderr.write(errors.getvalue())
            for line in (log.getvalue() + errors.getvalue()).splitlines():
                if line.startswith("Failed to save to"):
                    raise OSError(line)
                if line.startswith("Saved full response:"):
                    print(line, file=sys.stderr)
        finally:
            gateway.call_api = original_call
            gateway.get_api_base = original_base
            gateway._linkfox_root = original_root
            gateway._resolve_output_path = original_path
            gateway._session_id = original_session
    result = captured["result"]
    out = dict(result) if isinstance(result, dict) else {"rawResponse": result}
    out["transportHttpStatus"] = captured["status"]
    return out


def _normal_gateway_response(proxy: dict) -> bool:
    status = proxy.get("transportHttpStatus", 200)
    if type(status) not in (int, float) or not 200 <= status < 300:
        return False
    code = proxy.get("errcode")
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


def upload_media_space_image(params: dict) -> dict:
    shop_id = str(params.get("shopId") or "").strip()
    file_path_raw = str(params.get("filePath") or "").strip()
    if not shop_id:
        print("Missing required field: shopId", file=sys.stderr)
        sys.exit(1)
    if not file_path_raw:
        print("Missing required field: filePath", file=sys.stderr)
        sys.exit(1)

    file_path = Path(file_path_raw).expanduser()
    if not file_path.is_file():
        print(f"Image file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    file_size = file_path.stat().st_size
    if file_size <= 0:
        print("Image file is empty", file=sys.stderr)
        sys.exit(1)
    if file_size > 10 * 1024 * 1024:
        print("Image file must not exceed 10MB", file=sys.stderr)
        sys.exit(1)

    content_type = str(params.get("contentType") or mimetypes.guess_type(file_path.name)[0] or "")
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    content_type = content_type.lower().strip()
    if content_type not in allowed_types:
        print("Only JPEG, PNG, or WebP images are supported", file=sys.stderr)
        sys.exit(1)

    payload = {
        "shopId": shop_id,
        "fileBase64": base64.b64encode(file_path.read_bytes()).decode("ascii"),
        "fileName": file_path.name,
        "contentType": content_type,
    }
    return call_api(UPLOAD_IMAGE_ENDPOINT, payload)


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
    if not _normal_gateway_response(proxy):
        return
    try:
        if int(proxy.get("httpStatus") or 0) != 200:
            return
    except (TypeError, ValueError):
        return
    body_raw = proxy.get("body")
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except (json.JSONDecodeError, TypeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


# ===== LinkFox 统一输出层（落盘 + 摘要，无缓存）=====
# 各入口调用 emit_result()；与公共调用器共用会话标识，只在当前工作目录落盘。

import time as _lf_time
import secrets as _lf_secrets

LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict = {}

SLUG = "linkfox-shopee-store-media-space"


def _lf_root() -> str:
    """仅允许当前工作目录；在请求前验证可写，禁止静默回退。"""
    sid = (os.environ.get("SESSION_ID") or "").strip()
    if sid and (sid in (".", "..") or any(c in sid for c in ('/', '\\', ':'))):
        raise ValueError("SESSION_ID must be a single directory name")
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    probe = root / (".write_probe-" + _lf_secrets.token_hex(6))
    try:
        probe.write_text("", encoding="utf-8")
    finally:
        if probe.exists():
            probe.unlink()
    return str(root.resolve())


def _lf_iso(ts: float) -> str:
    return _lf_time.strftime("%Y-%m-%dT%H:%M:%S%z", _lf_time.localtime(ts))


def _lf_session_id(ts: float) -> str:
    env = (os.environ.get("SESSION_ID") or "").strip()
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
    if isinstance(result, dict) and result.get("api"):
        slug = f"{slug}-{result['api']}"
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = _lf_time.time()
    date_str = _lf_time.strftime("%Y-%m-%d", _lf_time.localtime(ts))
    sid = _lf_session_id(ts)
    if sid in ("", ".", "..") or any(c in sid for c in ('/', '\\', ':')):
        raise ValueError("SESSION_ID must be a single directory name")
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
    except OSError:
        raise
    _lf_update_meta(session_dir, skill=slug, file_rel=os.path.relpath(out, session_dir), ts=ts)
    if inline or len(serialized.encode("utf-8")) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        _lf_summarize(result)


def lf_inline_flag() -> bool:
    """入口脚本用：从 sys.argv 判断是否 --inline。"""
    return "--inline" in sys.argv
