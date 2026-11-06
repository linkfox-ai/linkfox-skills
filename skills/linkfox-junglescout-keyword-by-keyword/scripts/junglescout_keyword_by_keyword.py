#!/usr/bin/env python3
"""Jungle Scout 种子词拓展：提供 CLI 和单层缓存，使用公共调用器。"""

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api as api

API_PATH = "/tool-jungle-scout/keywords/by-keyword"
SLUG = "linkfox-junglescout-keyword-by-keyword"
CACHE_TTL_SEC = 24 * 60 * 60


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


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


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    usage = "用法：junglescout_keyword_by_keyword.py '<JSON 参数>' [--inline] [--no-cache]"
    if argv == ["--help"] or argv == ["-h"]:
        print(usage)
        return 0
    params_args = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not params_args:
        print(usage, file=sys.stderr)
        return 1
    try:
        params = json.loads(params_args[0])
        if not isinstance(params, dict):
            raise ValueError("JSON 参数必须是对象")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"参数格式无效：{exc}", file=sys.stderr)
        return 1

    # 业务封装负责缓存读写和键计算；公共 run 的缓存始终关闭。
    use_cache = "--no-cache" not in argv
    transport = api.call_api
    old_root = api._linkfox_root
    old_output = api._resolve_output_path

    def with_original_cache(api_path, request_params):
        cache_path = _cache_path(request_params)
        result = _load_cache(cache_path) if use_cache else None
        if result is None:
            result = transport(api_path, request_params)
            if use_cache:
                _save_cache(cache_path, result)
        return result

    try:
        # 当前目录不可写时在请求前失败，禁止公共调用器回退其他目录。
        root = Path.cwd() / "linkfox"
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
        api._linkfox_root = lambda: str(root)
        out_path = api.resolve_data_path(SLUG, time.time())
        with tempfile.TemporaryFile(dir=Path(out_path).parent):
            pass
        api._resolve_output_path = lambda _slug, _ts: out_path
        api.call_api = with_original_cache
        run_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in argv:
            run_argv.append("--inline")
        api.run(API_PATH, SLUG, argv=run_argv)
        # 公共调用器记录写入错误后仍会返回；业务 CLI 必须确认完整响应已落盘。
        # 读取并解析也能发现磁盘写满等情况留下的空文件或截断 JSON，不追加请求。
        with open(out_path, encoding="utf-8") as saved:
            json.load(saved)
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"当前工作目录无法保存响应：{exc}", file=sys.stderr)
        return 1
    finally:
        api.call_api = transport
        api._linkfox_root = old_root
        api._resolve_output_path = old_output


if __name__ == "__main__":
    sys.exit(main())
