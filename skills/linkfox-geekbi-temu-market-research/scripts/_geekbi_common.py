"""提供 GeekBI 单层缓存、会话落盘及摘要；HTTP 统一交给公共调用器。"""

import hashlib
import json
import os
import secrets
import sys
import time
from contextlib import contextmanager
from urllib.error import HTTPError

import call_api as api

SLUG = "linkfox-geekbi-temu-market-research"
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_SESSION_CACHE: dict[str, str] = {}

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


def _cache_key(api_path, params):
    # 缓存键与目录隔离账号、网关、接口及参数。
    raw = json.dumps({
        "apiBase": api.get_api_base(),
        "apiPath": api_path,
        "apiKeyFingerprint": hashlib.sha256(api.get_api_key().encode("utf-8")).hexdigest()[:12],
        "params": params,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(api_path, params):
    path = os.path.join(os.getcwd(), "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(api_path, params)}.json")


def _is_success_result(status, payload):
    # 缓存要求明确成功标记；errcode 判断遵循公共响应规则。
    if type(status) is not int or not 200 <= status < 300:
        return False
    if not api._is_cacheable(200, payload) or payload.get("error") or payload.get("success") is False:
        return False
    errcode = payload.get("errcode")
    marked = payload.get("success") is True or (
        errcode is not None and (not isinstance(errcode, str) or bool(errcode.strip()))
    )
    for key in ("errorCode", "code"):
        if key in payload:
            marked = True
            if str(payload[key]).lower() not in ("0", "200", "ok", "success"):
                return False
    return marked


class _OutputObject(dict):
    """保留完整 JSON；不把上游 _cache 扩展字段解释为公共调用器的缓存标记。"""

    def get(self, key, default=None):
        if key == "_cache":
            return {}
        return super().get(key, default)


@contextmanager
def _compatibility(transport):
    # 仅在此次 run 中替换兼容钩子，不修改公共调用器。
    replacements = {
        "call_api": transport,
        "_cache_path": lambda _slug, _params: "",  # run 始终禁用缓存，不建第二层缓存目录
        "_resolve_output_path": lambda _slug, _ts: resolve_data_path(SLUG, time.time()),
        "summarize": summarize,  # 摘要不把 columns 当作业务列表
    }
    previous = {name: getattr(api, name) for name in replacements}
    session = os.environ.get("SESSION_ID")
    if session is not None:
        os.environ["SESSION_ID"] = session.strip()
    try:
        for name, value in replacements.items():
            setattr(api, name, value)
        yield
    finally:
        for name, value in previous.items():
            setattr(api, name, value)
        if session is not None:
            os.environ["SESSION_ID"] = session


def run(api_path, argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    argv = list(sys.argv[1:] if argv is None else argv)
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not args:
        print(f"用法: {os.path.basename(sys.argv[0])} '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 格式错误: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("参数 JSON 的顶层必须是对象", file=sys.stderr)
        raise SystemExit(1)

    # 仅使用 cwd；失败即报错，不使用公共调用器的目录回退。
    _SESSION_CACHE.pop("_root", None)
    _linkfox_root()
    cache_path = _cache_path(api_path, params) if use_cache else None
    cached = _load_cache(cache_path) if cache_path else None
    if cached is not None and not _is_success_result(200, cached):
        cached = None
    transport = api.call_api
    received = {}

    def with_cache(path, request):
        if cached is not None:
            status, result = 200, cached
            print(f"Cache hit: {cache_path}")
            if inline or len(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")) <= SMALL_THRESHOLD:
                print(f"Cache hit: {cache_path}", file=sys.stderr)
        else:
            try:
                status, result = transport(path, request)
            except json.JSONDecodeError as exc:
                status, result = None, {"error": "Invalid JSON response", "details": exc.doc[:500]}
            except TimeoutError:
                status, result = None, {"error": "Connection timed out"}
            except UnicodeDecodeError as exc:
                # HTTP 错误体可能含非 UTF-8 字节；保留状态和可读内容。
                http_error = exc.__context__
                if not isinstance(http_error, HTTPError):
                    raise
                status = http_error.code
                details = exc.object.decode("utf-8", errors="replace")
                print(f"HTTP {status}: {http_error.reason}", file=sys.stderr)
                try:
                    result = json.loads(details)
                except json.JSONDecodeError:
                    result = {"error": f"HTTP {status}: {http_error.reason}", "details": details[:500]}
            if cache_path and _is_success_result(status, result):
                _save_cache(cache_path, result)
        received["body"] = result
        return status, _OutputObject(result) if isinstance(result, dict) else result

    with _compatibility(with_cache):
        run_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            run_argv.append("--inline")
        try:
            api.run(api_path, SLUG, argv=run_argv)
        except AttributeError:
            # 公共 run 保存并打印路径后假定响应是字典；此入口也接受数组/标量响应。
            # 非对象响应保留原始 JSON，不能将其他 AttributeError 吞掉。
            if "body" not in received or isinstance(received["body"], dict):
                raise
            result = received["body"]
            serialized = json.dumps(result, ensure_ascii=False, indent=2)
            if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
                print(serialized)
            else:
                summarize(result)
