#!/usr/bin/env python3
"""
TikTok 商品关联达人 - LinkFox 技能
调用 /chuhaijiang/products/related-creators 接口。

Usage:
  python chuhaijiang_product_related_creators.py '<JSON parameters>'           # 自动：小结果全量；大结果写文件+摘要
  python chuhaijiang_product_related_creators.py '<JSON parameters>' --inline  # 强制全量打印到 stdout

输出策略（脚本默认行为）：
  - **始终**将完整响应写入 `<linkfox-root>/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-product-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务聚合）
  - 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
  - 响应体 > 8 KB：落盘后 stdout 输出请求参数、顶层状态、嵌套计数、业务列表长度和主业务列表前 3 条样本
  - 加 `--inline` 强制全量打印到 stdout（同样落盘）
"""

import hashlib
import json
import os
import secrets
import sys
import time
from _chuhaijiang_transport import request_json, is_normal_response, is_cacheable_result

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


API_PATH = "/chuhaijiang/products/related-creators"
SLUG = "linkfox-chuhaijiang-tiktok-product"

# 响应小于等于该字节数时，落盘后额外全量输出到 stdout
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_LAST_CALL_WAS_HTTP_ERROR = False



def get_api_key():
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://skill.linkfox.com/linkfoxskills/guide.htm to obtain your Key\n"
            "2. Set the environment variable: export LINKFOX_AGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params):
    global _LAST_CALL_WAS_HTTP_ERROR
    _LAST_CALL_WAS_HTTP_ERROR = False
    status, result = request_json(API_PATH, params)
    _LAST_CALL_WAS_HTTP_ERROR = not is_normal_response(status, result)
    return result


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
    path = os.path.join(os.getcwd(), "linkfox", ".cache", SLUG)
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
        if not is_cacheable_result(200, payload):
            return None
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _is_success_result(result):
    # HTTP/errcode 遵循公共规则，显式 error/success 失败标记不写入缓存。
    return not _LAST_CALL_WAS_HTTP_ERROR and is_cacheable_result(200, result)



def _business_lists(result):
    """返回出海匠业务列表；避免把商品图片等嵌套数组误当作主列表。"""
    if not isinstance(result, dict):
        return []
    data = result.get("data")
    if not isinstance(data, dict):
        return []

    lists = []
    if isinstance(data.get("items"), list):
        lists.append(("data.items", data["items"]))
    for section in ("core", "channel"):
        node = data.get(section)
        if isinstance(node, dict) and isinstance(node.get("items"), list):
            lists.append((f"data.{section}.items", node["items"]))
    return lists


def summarize(result, params):
    """打印请求上下文、嵌套计数和端点业务列表的紧凑摘要。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")
    request_text = json.dumps(params, ensure_ascii=False, sort_keys=True)
    if len(request_text) > 2000:
        request_text = request_text[:2000] + "..."
    print(f"Request parameters: {request_text}")

    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costTime", "success", "request_id"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    data = result.get("data")
    if isinstance(data, dict):
        for key in ("total_count", "page", "page_size", "pageSize"):
            value = data.get(key)
            if isinstance(value, (int, float, bool, str)):
                print(f"  data.{key}: {value}")

    business_lists = _business_lists(result)
    if business_lists:
        print("\nBusiness list fields:")
        for path, items in business_lists:
            print(f"  `{path}`: length={len(items)}")

    main = next(((path, items) for path, items in business_lists if items), None)
    if main:
        list_path, main_list = main
        sample = main_list[:3]
        print(f"\nMain list sample: `{list_path}`")
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))


def _resolve_output_path(ts):
    """落到当前会话 data 目录，输出文件使用 Skill slug。"""
    return resolve_data_path(SLUG, ts)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    argv = sys.argv[1:]
    inline = False
    use_cache = True
    if "--inline" in argv:
        inline = True
        argv = [a for a in argv if a != "--inline"]
    if "--no-cache" in argv:
        use_cache = False
        argv = [a for a in argv if a != "--no-cache"]

    if len(argv) != 1:
        print(
            "Usage: chuhaijiang_product_related_creators.py '<JSON parameters>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("Invalid parameter format: top-level JSON must be an object", file=sys.stderr)
        sys.exit(1)

    cache_path = _cache_path(params) if use_cache else None
    result = _load_cache(cache_path) if cache_path else None
    cache_hit = result is not None
    if result is None:
        result = call_api(params)
        if cache_path and _is_success_result(result):
            _save_cache(cache_path, result)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    serialized_bytes = serialized.encode("utf-8")
    ts = time.time()
    try:
        out_path = _resolve_output_path(ts)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized_bytes)} bytes)")
        if cache_hit:
            print(f"Cache hit: {cache_path}")
    except OSError as e:
        print(f"Failed to save full response: {e}", file=sys.stderr)
        sys.exit(1)

    if inline or len(serialized_bytes) <= SMALL_THRESHOLD:
        if cache_hit:
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result, params)


if __name__ == "__main__":
    main()
