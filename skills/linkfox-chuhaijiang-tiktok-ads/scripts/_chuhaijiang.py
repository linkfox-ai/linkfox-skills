#!/usr/bin/env python3
"""出海匠业务封装：提供单层缓存、业务摘要和当前目录落盘，传输交给公共调用器。"""

import builtins
import hashlib
import json
import os
import secrets
import sys
import time
from contextlib import ExitStack
from unittest.mock import patch

import call_api as common

SLUG = "linkfox-chuhaijiang-tiktok-ads"
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_SESSION_CACHE = {}
API_PATH = ""

get_api_base = common.get_api_base
get_api_key = common.get_api_key

def _cache_key(params):
    api_key_fingerprint = hashlib.sha256(get_api_key().encode("utf-8")).hexdigest()
    raw = json.dumps(
        {
            "version": 1,
            "apiBase": get_api_base(),
            "apiPath": API_PATH,
            "apiKeyFingerprint": api_key_fingerprint,
            "params": params,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")

def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        return payload
    except (OSError, json.JSONDecodeError):
        return None

def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

def _find_main_list(obj):
    """优先业务记录列表，避免把图片、SKU 选项或向量误判为主列表。"""
    best = None

    def priority(path):
        parts = path.lower().split(".") if path else []
        if any(part in ("embedding", "embeddings", "vector", "vectors") for part in parts):
            return -1
        if path.lower() in ("data.items", "items", "result.items"):
            return 3
        if parts and parts[-1] in ("items", "records", "rows", "results", "products"):
            return 2
        return 1

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            rank = priority(path)
            if rank >= 0:
                score = (rank, len(node))
                if best is None or score > best[0]:
                    best = (score, path, node)
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    if best is None:
        return None, None
    return best[1], best[2]

def summarize(result):
    """打印紧凑摘要。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")

    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))

def _ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    """会话首次出现时创建 _meta.json，并向 index.jsonl 追加一条。"""
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
            f.write(
                json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": os.path.relpath(session_dir, root),
                        "started_at": _format_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass

def _linkfox_root() -> str:
    """返回当前工作目录下的 linkfox 根目录；不可写时由调用方报错。"""
    cached = _SESSION_CACHE.get("_root")
    if cached:
        return cached
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write_probe")
    with open(probe, "w", encoding="utf-8") as f:
        f.write("")
    os.remove(probe)
    _SESSION_CACHE["_root"] = root
    return root

def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))

def _session_id(ts: float) -> str:
    """优先 env SESSION_ID；缺省按 HHMMSS-<6 hex> 生成（同一进程内稳定）。"""
    env = (os.environ.get("SESSION_ID") or "").strip()
    if env:
        return env
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = (
            time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
        )
    return _SESSION_CACHE["_auto"]

def _ensure_session(ts: float) -> tuple[str, str]:
    """返回 (linkfox_root, session_dir)；session_dir 一定存在。"""
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    sid = _session_id(ts)
    root = _linkfox_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir

def _update_meta(session_dir: str, *, skill: str, kind: str, file_rel: str, ts: float) -> None:
    """把本次输出写入 _meta.json 的对应分类列表。kind ∈ {data, deliverable, media}。"""
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    bucket = {"data": "data_files", "deliverable": "deliverables", "media": "media_files"}.get(
        kind, "data_files"
    )
    files = meta.setdefault(bucket, [])
    if file_rel not in files:  # 去重：并发或重复注册同一路径时不留重复条目
        files.append(file_rel)
    meta["last_used_at"] = _format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def resolve_data_path(slug: str, ts: float, ext: str = "json") -> str:
    """普通 skill 的原始数据落到 <session>/data/<slug>-<ts>.<ext>。"""
    _, session_dir = _ensure_session(ts)
    sub = os.path.join(session_dir, "data")
    os.makedirs(sub, exist_ok=True)
    out = os.path.join(sub, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, kind="data", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out

def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<日期>/<session>/data/<slug>-<ts>.json，按 SESSION_ID 聚合到同一会话。"""
    return resolve_data_path(SLUG, ts)


class _NonObjectResponse(Exception):
    """非对象响应通过业务封装保存完整原始内容，公共 CLI 处理对象响应。"""


class _BusinessResponse(dict):
    """保留原始字段，隔离公共 CLI 对内部 _cache 标记的读取。

    本技能仅使用业务缓存；上游同名字段不是本地缓存状态。
    JSON 序列化仍读取完整字典，不改写或删除上游的 _cache 值。
    """

    def get(self, key, default=None):
        if key == "_cache":
            return {}
        return super().get(key, default)


def main(api_path, argv=None):
    global API_PATH
    API_PATH = api_path
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass
    argv = list(sys.argv[1:] if argv is None else argv)
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    params_argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not params_argv:
        print(f"用法: {os.path.basename(sys.argv[0])} '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(params_argv[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式无效: {exc}", file=sys.stderr)
        raise SystemExit(1)

    # 在任何收费请求之前检查 cwd 可写；不采用公共调用器的家目录/临时目录回退。
    try:
        _linkfox_root()
        cache_path = _cache_path(params) if use_cache else None
    except OSError as exc:
        print(f"当前目录无法保存响应: {exc}", file=sys.stderr)
        raise SystemExit(1)
    cached = _load_cache(cache_path) if cache_path else None
    # 读取缓存后按公共响应基本规则校验，避免复用错误响应。
    if cached is not None and not _cacheable(200, cached):
        cached = None
    state = {"result": cached, "hit": cached is not None}
    transport = common.call_api

    def request(path, body):
        if state["hit"]:
            status, result = 200, cached
        else:
            # SESSION_ID 去除首尾空白后用于头部与落盘聚合。
            with patch.dict(os.environ, {"SESSION_ID": (os.environ.get("SESSION_ID") or "").strip()}):
                status, result = transport(path, body)
            if cache_path and _cacheable(status, result):
                _save_cache(cache_path, result)
        state["result"] = result
        if not isinstance(result, dict):
            raise _NonObjectResponse()
        return status, _BusinessResponse(result)

    def checked_open(path, *args, **kwargs):
        try:
            return builtins.open(path, *args, **kwargs)
        except OSError as exc:
            print(f"无法保存完整响应: {exc}", file=sys.stderr)
            raise SystemExit(1)

    # run 负责参数透传、完整响应保存与 CLI 输出；业务封装提供缓存、摘要与落盘路径。
    # --no-cache 关闭公共缓存，业务缓存是唯一缓存层。
    with ExitStack() as stack:
        stack.enter_context(patch.object(common, "call_api", request))
        stack.enter_context(patch.object(common, "_cache_path", lambda *args: ""))
        stack.enter_context(patch.object(common, "summarize", summarize))
        stack.enter_context(patch.object(common, "_resolve_output_path", lambda *args: _resolve_output_path(time.time())))
        stack.enter_context(patch.object(common, "open", checked_open, create=True))
        try:
            common.run(API_PATH, SLUG, [json.dumps(params, ensure_ascii=False), "--no-cache"] + (["--inline"] if inline else []))
        except _NonObjectResponse:
            result = state["result"]
            serialized = json.dumps(result, ensure_ascii=False, indent=2)
            out_path = _resolve_output_path(time.time())
            with checked_open(out_path, "w", encoding="utf-8") as file:
                file.write(serialized)
            print(f"Saved full response: {out_path} ({len(serialized.encode('utf-8'))} bytes)")
            if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
                print(serialized)
            else:
                summarize(result)
    if state["hit"]:
        print(f"Cache hit: {cache_path}")
        if inline or len(json.dumps(state["result"], ensure_ascii=False, indent=2).encode("utf-8")) <= SMALL_THRESHOLD:
            print(f"Cache hit: {cache_path}", file=sys.stderr)


def _cacheable(status, result):
    # 除 HTTP/errcode 基础规则外，显式失败标志也会阻止缓存。
    if not common._is_cacheable(status, result) or result.get("error") or result.get("success") is False:
        return False
    for key in ("errorCode", "code"):
        if key in result and str(result[key]).lower() not in ("0", "200", "ok", "success"):
            return False
    return True
