#!/usr/bin/env python3
"""极目细分市场洞察：提供 CLI 与本地缓存，使用公共调用和输出流程。

用法：python jiimore_get_niche_info.py '<JSON 参数>' [--inline] [--no-cache]
"""

import hashlib
import json
import os
import sys
import time
import call_api as api

API_PATH = "/jiimore/getNicheInfo"
SLUG = "linkfox-jiimore-get-niche-info"
CACHE_TTL_SEC = 24 * 60 * 60


def call_api(params):
    """Python 调用入口；HTTP 传输由公共调用器负责。"""
    return api.call_api(API_PATH, params)


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
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
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            payload.setdefault("_cache", {})["hit"] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _linkfox_root():
    """落盘只使用 cwd，不回退到其他工作区或临时目录。"""
    root = os.path.realpath(os.path.join(os.getcwd(), "linkfox"))
    normalized = root.replace("\\", "/")
    if normalized == "/tmp" or normalized.startswith("/tmp/"):
        raise OSError("按技能落盘约束，禁止写入 /tmp，请切换到可写的工作目录")
    os.makedirs(root, exist_ok=True)
    return root


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not argv:
        print("用法：jiimore_get_niche_info.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 格式无效：{exc}", file=sys.stderr)
        raise SystemExit(1)

    native_transport = api.call_api
    native_root = api._linkfox_root
    native_output = api._resolve_output_path
    try:
        api._linkfox_root = _linkfox_root
        # 请求前确认会话文件可写；公共流程复用此路径，避免重复落盘。
        _linkfox_root()
        cache_path = _cache_path(params)
        cached = _load_cache(cache_path) if use_cache else None
        if cached is None:
            api.get_api_key()
        out_path = api.resolve_data_path(SLUG, time.time())
        with open(out_path, "w", encoding="utf-8"):
            pass

        def fetch(api_path, request_params):
            if cached is not None:
                return cached
            result = native_transport(api_path, request_params)
            if use_cache:
                _save_cache(cache_path, result)
            return result

        api.call_api = fetch
        api._resolve_output_path = lambda slug, ts: out_path
        run_argv = [argv[0], "--no-cache"]
        if inline:
            run_argv.append("--inline")
        api.run(API_PATH, SLUG, argv=run_argv)
        # 公共调用器会捕获写入错误；在封装层确认完整落盘并返回失败状态。
        with open(out_path, encoding="utf-8") as saved:
            try:
                json.load(saved)
            except (ValueError, UnicodeError) as exc:
                raise OSError("完整响应未成功保存，请检查当前目录写入权限或磁盘空间") from exc
    except OSError as exc:
        print(f"当前目录无法保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1)
    finally:
        api.call_api = native_transport
        api._linkfox_root = native_root
        api._resolve_output_path = native_output


if __name__ == "__main__":
    main()
