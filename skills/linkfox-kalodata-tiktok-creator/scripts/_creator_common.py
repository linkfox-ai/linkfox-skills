"""提供达人查询的单层缓存与 CLI，通过公共 run 完成请求、落盘和输出。"""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time

import call_api as api


SLUG = "linkfox-kalodata-tiktok-creator"
CACHE_TTL_SEC = 24 * 60 * 60


def _cache_path(api_path, params):
    # 缓存键同时包含接口路径和参数，隔离榜单与详情响应。
    raw = json.dumps({"path": api_path, "params": params}, ensure_ascii=False, sort_keys=True)
    key = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    folder = Path.cwd() / "linkfox" / ".cache" / SLUG
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{SLUG}-{key}.json"


def _load_cache(path):
    try:
        if not path.is_file() or time.time() - path.stat().st_mtime > CACHE_TTL_SEC:
            return None
        with path.open(encoding="utf-8") as stream:
            cached = json.load(stream)
        # 仅复用版本 2 的缓存封装，确保能读取 HTTP 状态。
        if not isinstance(cached, dict) or cached.get("_cache_version") != 2:
            return None
        if "http_status" not in cached or not isinstance(cached.get("body"), dict):
            return None
        status = cached["http_status"]
        if status is not None and (type(status) is not int or not 100 <= status <= 599):
            return None
        payload = cached["body"]
        marker = payload.get("_cache")
        payload["_cache"] = {**(marker if isinstance(marker, dict) else {}), "hit": True}
        return status, payload
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _save_cache(path, payload, status):
    try:
        with path.open("w", encoding="utf-8") as stream:
            json.dump(
                {"_cache_version": 2, "http_status": status, "body": payload},
                stream, ensure_ascii=False, indent=2,
            )
    except OSError:
        pass


def run_creator(api_path, argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass
    argv = list(sys.argv[1:] if argv is None else argv)
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional:
        print(f"用法: {Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式无效: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须是对象", file=sys.stderr)
        raise SystemExit(1)

    # 请求前确认 cwd 可写，不采用公共脚本的目录回退。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    use_cache = "--no-cache" not in argv
    cache_path = _cache_path(api_path, params) if use_cache else None
    transport = api.call_api

    def with_creator_cache(path, request_params):
        cached = _load_cache(cache_path) if use_cache else None
        if cached is not None:
            status, payload = cached
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        else:
            status, payload = transport(path, request_params)
            # 公共输出器要求对象；异常 JSON 保留原值，避免落盘后 .get 崩溃。
            if not isinstance(payload, dict):
                payload = {"error": "接口返回的 JSON 不是对象", "rawResponse": payload}
            elif "_cache" in payload and not isinstance(payload["_cache"], dict):
                payload = dict(payload)
                payload["_cache"] = {"raw": payload["_cache"]}
            if use_cache:
                _save_cache(cache_path, payload, status)
        print(f"HTTP 状态码: {status if status is not None else '无（连接失败）'}", file=sys.stderr)
        return status, payload

    previous_root = api._SESSION_CACHE.get("_root")
    previous_output_path = api._resolve_output_path
    previous_cache_path = api._cache_path
    api.call_api = with_creator_cache
    api._SESSION_CACHE["_root"] = str(root)
    # 使用微秒时间生成文件名，避免相邻调用覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    # 公共 run 即使 --no-cache 也计算路径；命中提示必须显示业务缓存的真实路径。
    api._cache_path = lambda slug, request_params: str(
        cache_path if cache_path is not None else _cache_path(api_path, request_params)
    )
    try:
        # root 可写不代表已有的会话 data 目录可写，收费请求前检查实际目录。
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        run_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in argv:
            run_argv.append("--inline")
        api.run(api_path, SLUG, argv=run_argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output_path
        api._cache_path = previous_cache_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
