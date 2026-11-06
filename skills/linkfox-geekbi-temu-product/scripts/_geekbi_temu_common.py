"""GeekBI Temu 业务兼容层：独立接口缓存、会话输出及公共调用器适配。"""

import hashlib
import json
import os
import secrets
import sys
import time

import call_api as api

SLUG = "linkfox-geekbi-temu-product"
CACHE_TTL_SEC = 24 * 60 * 60
_SESSION_CACHE = {}
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
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
    except OSError:
        pass


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


def _is_success_result(http_status, result):
    # 公共基础状态判定优先，同时检查业务 error/success/errorCode/code 状态。
    # 公共缓存器只收 HTTP 200；业务缓存须按文档支持全部正常 2xx。
    if http_status is None or not 200 <= http_status < 300:
        return False
    if not api._is_cacheable(200, result):
        return False
    if result.get("error") or result.get("success") is False:
        return False
    for key in ("errorCode", "code"):
        if key in result and str(result[key]).lower() not in ("0", "200", "ok", "success"):
            return False
    return True


def main(api_path, argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    args = list(sys.argv[1:] if argv is None else argv)
    inline = "--inline" in args
    use_cache = "--no-cache" not in args
    values = [a for a in args if a not in ("--inline", "--no-cache")]
    if not values:
        print("用法：python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(values[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 无效：{exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("参数 JSON 顶层必须是对象", file=sys.stderr)
        raise SystemExit(1)

    # 请求前验证 cwd 可写，不回退到其他输出目录。
    _SESSION_CACHE.pop("_root", None)
    _linkfox_root()
    cache_path = _cache_path(api_path, params) if use_cache else None
    transport = api.call_api
    previous = {name: getattr(api, name) for name in
                ("call_api", "_cache_path", "_resolve_output_path", "summarize")}
    old_sid = os.environ.get("SESSION_ID")
    result = None

    def cached_transport(path, request):
        nonlocal result
        result = _load_cache(cache_path) if cache_path else None
        # 读取裸 JSON 成功响应缓存，拒绝失败或损坏的缓存。
        if result is not None and not _is_success_result(200, result):
            result = None
        if result is not None:
            print(f"Cache hit: {cache_path}")
            if inline or len(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")) <= api.SMALL_THRESHOLD:
                print(f"Cache hit: {cache_path}", file=sys.stderr)
            return 200, result
        try:
            status, result = transport(path, request)
        except json.JSONDecodeError as exc:
            status, result = None, {"error": "Invalid JSON response", "details": exc.doc[:500]}
        except TimeoutError:
            status, result = None, {"error": "Connection timed out"}
        if cache_path and _is_success_result(status, result):
            _save_cache(cache_path, result)
        return status, result

    api.call_api = cached_transport
    # run 即使 --no-cache 也计算缓存路径；阻止它创建第二套缓存目录。
    api._cache_path = lambda *_: None
    # 微秒时间戳防止输出文件覆盖，并记录完整会话元数据。
    api._resolve_output_path = lambda slug, _ts: resolve_data_path(slug, time.time())
    api.summarize = summarize
    if old_sid is not None:
        os.environ["SESSION_ID"] = old_sid.strip()
    try:
        run_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            run_argv.append("--inline")
        try:
            api.run(api_path, SLUG, argv=run_argv)
        except AttributeError:
            # 公共 run 会把 _cache 当本地元数据；原响应中的空值或其他
            # JSON 类型也须像非对象响应一样原样输出，此时数据已落盘。
            invalid_cache_marker = (
                isinstance(result, dict)
                and "_cache" in result
                and not isinstance(result["_cache"], dict)
            )
            if isinstance(result, dict) and not invalid_cache_marker:
                raise
            serialized = json.dumps(result, ensure_ascii=False, indent=2)
            if inline or len(serialized.encode("utf-8")) <= api.SMALL_THRESHOLD:
                print(serialized)
            else:
                summarize(result)
    finally:
        for name, value in previous.items():
            setattr(api, name, value)
        if old_sid is None:
            os.environ.pop("SESSION_ID", None)
        else:
            os.environ["SESSION_ID"] = old_sid
