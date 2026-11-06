#!/usr/bin/env python3
"""极鲸云 Temu 图搜业务封装。

调用 /geekbi/temu/goodsImageSearch 接口。

用法：
  python geekbi_temu_goods_image_search.py '<JSON parameters>'
  python geekbi_temu_goods_image_search.py '<JSON parameters>' --inline

完整响应始终写入 LinkFox 会话 data 目录。响应不超过 8 KB 时额外全量
输出；更大响应只输出摘要。--inline 强制全量输出，但仍会落盘。
"""

import hashlib
import json
import os
import secrets
import sys
import time
from _linkfox_transport import request, is_success

_SESSION_CACHE: dict[str, str] = {}


def get_api_base() -> str:
    """网关基础地址：env LINKFOX_TOOL_GATEWAY 优先，缺省回退正式地址。"""
    return (os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")


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


API_PATH = "/geekbi/temu/goodsImageSearch"
SLUG = "linkfox-geekbi-temu-search-by-image"
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_LAST_HTTP_STATUS = None


def get_api_key():
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://agent.linkfox.com → 设置 → API KEY to obtain your Key\n"
            "2. Set the environment variable: export LINKFOX_AGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params):
    global _LAST_CALL_WAS_HTTP_ERROR, _LAST_HTTP_STATUS
    _LAST_HTTP_STATUS, result = request(API_PATH, SLUG, params)
    _LAST_CALL_WAS_HTTP_ERROR = _LAST_HTTP_STATUS is None or not 200 <= _LAST_HTTP_STATUS < 300
    return result


def _cache_key(params):
    api_key_fingerprint = hashlib.sha256(get_api_key().encode("utf-8")).hexdigest()[:12]
    raw = json.dumps(
        {
            "apiBase": get_api_base(),
            "apiPath": API_PATH,
            "apiKeyFingerprint": api_key_fingerprint,
            "params": params,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    path = os.path.join(os.getcwd(), "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as file:
            payload = json.load(file)
        # 读取缓存时核对业务成功条件，不复用 errcode=0 等失败响应。
        return payload if _is_success_payload(200, payload) else None
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _is_success_result(result):
    return _is_success_payload(_LAST_HTTP_STATUS, result)


def _is_success_payload(status, result):
    if not is_success(status, result) or result.get("error"):
        return False
    if result.get("success") is False:
        return False
    # 核对其他业务失败标记；errcode 按公共基础规则判断。
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


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    argv = sys.argv[1:]
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not argv:
        print(
            "Usage: geekbi_temu_goods_image_search.py '<JSON parameters>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f"Invalid parameter format: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("Invalid parameter format: top-level JSON must be an object", file=sys.stderr)
        sys.exit(1)

    get_api_key()  # 请求前检查认证；--no-cache 同样输出认证提示。
    try:
        out_path = resolve_data_path(SLUG, time.time())
        # 先实际打开目标文件，当前目录或 data 目录不可写时不产生付费请求。
        with open(out_path, "w", encoding="utf-8") as file:
            cache_path = _cache_path(params) if use_cache else None
            result = _load_cache(cache_path) if cache_path else None
            cache_hit = result is not None
            if result is None:
                result = call_api(params)
                if cache_path and _is_success_result(result):
                    _save_cache(cache_path, result)
            serialized = json.dumps(result, ensure_ascii=False, indent=2)
            serialized_bytes = serialized.encode("utf-8")
            file.write(serialized)
    except OSError as exc:
        print(f"Failed to save response in current directory: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Saved full response: {out_path} ({len(serialized_bytes)} bytes)")
    if cache_hit:
        print(f"Cache hit: {cache_path}")

    if inline or len(serialized_bytes) <= SMALL_THRESHOLD:
        if cache_hit:
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
