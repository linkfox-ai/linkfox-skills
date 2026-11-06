#!/usr/bin/env python3
"""GeekBI 店铺接口的缓存、会话与输出兼容封装；HTTP 统一委托公共调用器。"""

import hashlib
import json
import os
import secrets
import sys
import time
from contextlib import ExitStack
from unittest.mock import patch
from urllib.error import HTTPError

import call_api as api

SLUG = "linkfox-geekbi-temu-shop"
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_SESSION_CACHE: dict[str, str] = {}
get_api_base = api.get_api_base
get_api_key = api.get_api_key


def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))


def _session_id(ts: float) -> str:
    """优先 env SESSION_ID；缺省按 HHMMSS-<6 hex> 生成（进程内稳定）。"""
    env = (os.environ.get("SESSION_ID") or "").strip()
    if env:
        return env
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
    return _SESSION_CACHE["_auto"]


def _linkfox_root() -> str:
    """返回当前工作目录下的 linkfox 根目录；不可写时由调用方报错。"""
    cached = _SESSION_CACHE.get("_root")
    if cached:
        return cached
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write_probe")
    with open(probe, "w", encoding="utf-8"):
        pass
    os.remove(probe)
    _SESSION_CACHE["_root"] = root
    return root


def _ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    if os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _format_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "session_id": sid,
                "date": date_str,
                "path": os.path.relpath(session_dir, root),
                "started_at": _format_iso(ts),
            }, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _ensure_session(ts: float) -> tuple[str, str]:
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    sid = _session_id(ts)
    root = _linkfox_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir


def _update_meta(session_dir: str, *, skill: str, file_rel: str, ts: float) -> None:
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
    meta["last_used_at"] = _format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def resolve_data_path(slug: str, ts: float, ext: str = "json") -> str:
    """将完整响应写入当前会话的 data 目录，并更新会话元数据。"""
    _, session_dir = _ensure_session(ts)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    out = os.path.join(data_dir, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out


def _cache_key(api_path, params):
    api_key_fingerprint = hashlib.sha256(get_api_key().encode("utf-8")).hexdigest()[:12]
    raw = json.dumps(
        {
            "apiBase": get_api_base(),
            "apiPath": api_path,
            "apiKeyFingerprint": api_key_fingerprint,
            "params": params,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(api_path, params):
    path = os.path.join(os.getcwd(), "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(api_path, params)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as file:
            payload = json.load(file)
        return payload if _is_success_result(200, payload) else None
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _is_success_result(http_status, result):
    """仅缓存成功响应；基础状态按公共规则判断，errcode 为零或 false 时不成功。"""
    if not isinstance(http_status, int) or not 200 <= http_status < 300:
        return False
    if not isinstance(result, dict) or result.get("error") or result.get("success") is False:
        return False
    if not api._is_cacheable(200, result):
        return False
    for key in ("errorCode", "code"):
        if key in result and str(result[key]).lower() not in ("0", "200", "ok", "success"):
            return False
    return True


def _find_main_list(obj):
    """递归找到元素数最多的业务 list，忽略 columns 渲染元数据。"""
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for key, value in node.items():
                if key == "columns":
                    continue
                walk(value, f"{path}.{key}" if path else key)

    walk(obj, "")
    return best[0], best[1]


def summarize(result):
    """打印紧凑摘要：顶层状态字段和最大业务列表前 3 条。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")
    for key in (
        "errcode", "errorCode", "code", "errmsg", "msg", "total", "totalCount",
        "count", "currentPage", "page", "perPage", "size", "costTime", "success",
    ):
        value = result.get(key)
        if isinstance(value, (int, float, bool, str)):
            print(f"  {key}: {value}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        sample = main_list[:3]
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))


class _RawResponse(Exception):
    """绕过公共 runner 的对象/缓存标记假设，原样保存并输出响应。"""

    def __init__(self, payload):
        self.payload = payload


class _HTTPFailure(Exception):
    """将 HTTP 错误状态和已解码正文交回业务封装。"""

    def __init__(self, status, payload):
        self.status = status
        self.payload = payload


def _emit_raw(result, inline):
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    path = resolve_data_path(SLUG, time.time())
    with open(path, "w", encoding="utf-8") as file:
        file.write(serialized)
    print(f"Saved full response: {path} ({len(serialized.encode('utf-8'))} bytes)")
    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


def run_endpoint(api_path, argv=None):
    """为三个入口提供 JSON / --inline / --no-cache CLI 与唯一业务缓存。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    argv = list(sys.argv[1:] if argv is None else argv)
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not argv:
        print(f"用法: {os.path.basename(sys.argv[0])} '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f"参数格式错误: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("参数格式错误: 顶层 JSON 必须是对象", file=sys.stderr)
        raise SystemExit(1)

    # 在请求前确认 cwd 可写，防止公共 runner 回退到其他目录。
    _SESSION_CACHE.pop("_root", None)
    _linkfox_root()
    cache_path = _cache_path(api_path, params) if use_cache else None
    transport = api.call_api
    opener = api.urlopen

    def error_preserving_opener(*args, **kwargs):
        try:
            return opener(*args, **kwargs)
        except HTTPError as exc:
            try:
                body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
                try:
                    result = json.loads(body) if body else {"error": f"HTTP {exc.code}: {exc.reason}"}
                except json.JSONDecodeError:
                    result = {"error": f"HTTP {exc.code}: {exc.reason}", "details": body}
                raise _HTTPFailure(exc.code, result) from None
            finally:
                exc.close()

    def cached_transport(path, request_params):
        result = _load_cache(cache_path) if cache_path else None
        if result is not None:
            print(f"Cache hit: {cache_path}")
            print(f"Cache hit: {cache_path}", file=sys.stderr)
            status = 200
        else:
            try:
                status, result = transport(path, request_params)
            except _HTTPFailure as exc:
                status, result = exc.status, exc.payload
            except json.JSONDecodeError as exc:
                status, result = None, {"error": "Invalid JSON response", "details": exc.doc[:500]}
            except UnicodeDecodeError as exc:
                status, result = None, {"error": "Invalid response encoding", "details": str(exc)}
            except TimeoutError:
                status, result = None, {"error": "Connection timed out"}
            if status is not None and not 200 <= status < 300:
                print(f"HTTP status: {status}", file=sys.stderr)
            if cache_path and _is_success_result(status, result):
                _save_cache(cache_path, result)
        # _cache 可能是上游业务字段。公共 runner 会把它当作自身缓存标记；
        # 不能因此崩溃、误报命中或修改原始响应，缓存命中也走相同兼容分支。
        if not isinstance(result, dict) or "_cache" in result:
            raise _RawResponse(result)
        return status, result

    # 临时适配公共 runner 的扩展点，调用结束全部恢复；不修改公共文件。
    with ExitStack() as stack:
        stack.enter_context(patch.dict(os.environ, {"SESSION_ID": (os.environ.get("SESSION_ID") or "").strip()}))
        replacements = {
            "urlopen": error_preserving_opener,
            "call_api": cached_transport,
            "_cache_path": lambda _slug, _params: "",
            "_resolve_output_path": lambda _slug, _ts: resolve_data_path(SLUG, time.time()),
            "summarize": summarize,
        }
        for name, value in replacements.items():
            stack.enter_context(patch.object(api, name, value))
        run_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            run_argv.append("--inline")
        try:
            api.run(api_path, SLUG, argv=run_argv)
        except _RawResponse as exc:
            _emit_raw(exc.payload, inline)
