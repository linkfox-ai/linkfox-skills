#!/usr/bin/env python3
"""出海匠直播业务封装：保留身份隔离缓存，由公共调用器负责 HTTP 与落盘。"""

import hashlib
import json
import os
import sys
import tempfile
import time

import call_api as runner

SLUG = "linkfox-chuhaijiang-tiktok-live"
CACHE_TTL_SEC = 24 * 60 * 60
get_api_base = runner.get_api_base
get_api_key = runner.get_api_key


class _RunnerResponse(dict):
    """保留服务端全部字段，但不把服务端 _cache 当作公共调用器的缓存元数据。"""

    def get(self, key, default=None):
        if key == "_cache":
            # JSON 序列化仍保留原字段；本地命中由业务层单独判断、输出。
            return {}
        return super().get(key, default)


def _cache_key(api_path, params):
    api_key_fingerprint = hashlib.sha256(get_api_key().encode("utf-8")).hexdigest()
    raw = json.dumps(
        {
            "version": 1,
            "apiBase": get_api_base(),
            "apiPath": api_path,
            "apiKeyFingerprint": api_key_fingerprint,
            "params": params,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _cache_path(api_path, params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(api_path, params)}.json")


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


def _is_success_result(http_status, result):
    """公共正常响应规则优先，同时按业务成功标记保守过滤缓存。"""
    if type(http_status) is not int or not 200 <= http_status < 300:
        return False
    if not isinstance(result, dict) or result.get("error") or result.get("success") is False:
        return False
    # 公共辅助函数限制 HTTP 200；此处仅借用其 errcode 判断，HTTP 已在上面按 2xx 判断。
    if not runner._is_cacheable(200, result):
        return False
    has_marker = result.get("success") is True or "errcode" in result
    for key in ("errorCode", "code"):
        if key in result:
            has_marker = True
            if str(result[key]).lower() not in ("0", "200", "ok", "success"):
                return False
    return has_marker


def main(api_path, argv=None):
    """支持 JSON、--inline、--no-cache CLI，公共调用器始终关闭自身缓存。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    usage = f"用法: {os.path.basename(sys.argv[0])} '<JSON 参数>' [--inline] [--no-cache]"
    if any(flag in argv for flag in ("--help", "-h")):
        print(usage)
        return
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    args = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not args:
        print(usage, file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式无效: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        raise SystemExit(1)

    transport = runner.call_api
    old_output_path = runner._resolve_output_path
    old_summary = runner.summarize
    old_root = runner._SESSION_CACHE.get("_root")
    old_session = os.environ.get("SESSION_ID")
    output_paths = []

    try:
        # 业务输出严格写入 cwd；即便 ACPX_WORKSPACES 已配置，也不改变落盘位置。
        root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
        os.makedirs(root, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
        runner._SESSION_CACHE["_root"] = root
        if old_session is not None:
            os.environ["SESSION_ID"] = old_session.strip()
        # 预先确认数据目录可写，失败时不发付费请求。
        _, session = runner._ensure_session(time.time())
        data_dir = os.path.join(session, "data")
        os.makedirs(data_dir, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        cache_path = _cache_path(api_path, params) if use_cache else None

        def cached_transport(path, request_params):
            result = _load_cache(cache_path) if cache_path else None
            if result is not None and _is_success_result(200, result):
                print(f"Cache hit: {cache_path}")
                if inline or len(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")) <= runner.SMALL_THRESHOLD:
                    print(f"Cache hit: {cache_path}", file=sys.stderr)
                return 200, _RunnerResponse(result)
            try:
                status, result = transport(path, request_params)
            except (ValueError, OSError) as exc:
                status, result = None, {"error": f"请求失败: {exc}"}
            if cache_path and _is_success_result(status, result):
                _save_cache(cache_path, result)
            if not isinstance(result, dict):
                result = {"error": "响应不是 JSON 对象", "details": result}
            if type(status) is int and not 200 <= status < 300:
                print(f"HTTP 状态码: {status}", file=sys.stderr)
            return status, _RunnerResponse(result)

        def output_path(slug, _ts):
            # 业务输出使用微秒文件名，避免同秒调用覆盖。
            path = runner.resolve_data_path(slug, time.time())
            output_paths.append(path)
            return path

        def summarize(result):
            old_summary(result)
            data = result.get("data") if isinstance(result, dict) else None
            if isinstance(data, dict) and "total_count" in data:
                print(f"  data.total_count: {data['total_count']}")

        runner.call_api = cached_transport
        runner._resolve_output_path = output_path
        runner.summarize = summarize
        flags = ["--no-cache"]
        if inline:
            flags.append("--inline")
        runner.run(api_path, SLUG, argv=[json.dumps(params, ensure_ascii=False)] + flags)
        # 公共调用器会回显保存错误；业务入口在保存失败时返回非零状态。
        if not output_paths or not os.path.isfile(output_paths[-1]) or os.path.getsize(output_paths[-1]) == 0:
            raise OSError("完整响应保存失败")
    except OSError as exc:
        print(f"业务数据目录或输出不可写: {exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        runner.call_api = transport
        runner._resolve_output_path = old_output_path
        runner.summarize = old_summary
        if old_root is None:
            runner._SESSION_CACHE.pop("_root", None)
        else:
            runner._SESSION_CACHE["_root"] = old_root
        if old_session is None:
            os.environ.pop("SESSION_ID", None)
        else:
            os.environ["SESSION_ID"] = old_session
