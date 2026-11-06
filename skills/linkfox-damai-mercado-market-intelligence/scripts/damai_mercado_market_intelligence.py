#!/usr/bin/env python3
"""大麦美客多查询：提供 CLI 与 24 小时缓存，通过公共调用器请求和落盘。"""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import xml.etree.ElementTree as ET

import call_api as api

API_PATH = "/damai/call"
SLUG = "linkfox-damai-mercado-market-intelligence"
CACHE_TTL_SEC = 24 * 60 * 60


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    directory = Path.cwd() / "linkfox" / ".cache" / SLUG
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{SLUG}-{_cache_key(params)}.json"


def _cacheable(status, payload):
    # 公共响应判断只控制正常状态；业务错误另行排除，避免复用失败响应。
    return api._is_cacheable(status, payload) and not payload.get("error")


def _load_cache(path):
    path = Path(path)
    if not path.is_file() or time.time() - path.stat().st_mtime > CACHE_TTL_SEC:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not _cacheable(200, payload):
            return None
        payload["_cache"] = {"hit": True}
        return payload
    except (OSError, ValueError, TypeError):
        return None


def _save_cache(path, payload):
    try:
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def _normalise_xml(text):
    """兼容 HTTP 200 携带的 ToolErrorResponse；不实现第二套 HTTP。"""
    try:
        root = ET.fromstring(text)
        fields = {node.tag.rsplit("}", 1)[-1].lower(): node.text for node in root.iter()}
        if root.tag.rsplit("}", 1)[-1] == "ToolErrorResponse":
            return {
                "errcode": fields.get("errcode") or fields.get("code") or 1003,
                "errmsg": fields.get("errmsg") or fields.get("message") or "上游业务错误",
            }
    except ET.ParseError:
        pass
    return {"errcode": 1003, "errmsg": "网关返回无法解析的响应"}


def run_request(api_path, slug, params, *, inline=False, use_cache=False, quiet=False):
    """在业务层管理缓存，HTTP、落盘与输出通过 call_api.run 处理。"""
    root = Path.cwd() / "linkfox"
    cwd = Path.cwd().resolve()
    if str(cwd) == "/tmp" or "/tmp" in (str(p) for p in cwd.parents):
        raise OSError("会话数据禁止写入 /tmp")
    root.mkdir(parents=True, exist_ok=True)

    cache_path = _cache_path(params) if use_cache else None
    transport = api.call_api
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output = api._resolve_output_path
    captured = {}

    def cached_transport(path, request):
        result = _load_cache(cache_path) if cache_path else None
        if result is not None:
            status = 200
        else:
            try:
                status, result = transport(path, request)
            except json.JSONDecodeError as exc:
                status, result = 200, _normalise_xml(exc.doc)
            except TimeoutError:
                status, result = None, {"error": "请求超时，结果不确定；请勿自动重试"}
            if isinstance(result, dict) and isinstance(result.get("details"), str):
                if "ToolErrorResponse" in result["details"]:
                    result = _normalise_xml(result["details"])
            if not isinstance(result, dict):
                result = {"errcode": 1003, "errmsg": "网关响应不是对象"}
            if cache_path and _cacheable(status, result):
                _save_cache(cache_path, result)
        captured.update(status=status, body=result)
        return status, result

    api.call_api = cached_transport
    api._SESSION_CACHE["_root"] = str(root)
    argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    try:
        # 请求前确认实际会话目录和目标文件可写，避免请求完成后才发现落盘失败。
        out_path = Path(api.resolve_data_path(slug, time.time()))
        with out_path.open("x", encoding="utf-8"):
            pass
        api._resolve_output_path = lambda _name, _ts: str(out_path)
        with contextlib.ExitStack() as stack:
            if quiet:
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            api.run(api_path, slug, argv=argv)
        # 公共调用器会捕获写文件异常；业务入口必须把落盘失败传回 CLI。
        try:
            saved = json.loads(out_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise OSError("完整响应未成功保存；请求可能已完成，请勿自动重试") from exc
        if saved != captured["body"]:
            raise OSError("保存内容与完整响应不一致；请勿自动重试")
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
    return captured["status"], captured["body"]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv == ["--help"] or argv == ["-h"]:
        print("用法：damai_mercado_market_intelligence.py '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stdout if argv else sys.stderr)
        return 0 if argv else 1
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    args = [item for item in argv if item not in ("--inline", "--no-cache")]
    if len(args) != 1:
        print("请提供一个 JSON 参数对象。", file=sys.stderr)
        return 1
    try:
        params = json.loads(args[0])
        if not isinstance(params, dict):
            raise ValueError("请求必须为 JSON 对象")
    except ValueError as exc:
        print(f"参数格式错误：{exc}", file=sys.stderr)
        return 1
    try:
        run_request(API_PATH, SLUG, params, inline=inline, use_cache=use_cache)
    except OSError as exc:
        print(f"无法保存会话数据：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
