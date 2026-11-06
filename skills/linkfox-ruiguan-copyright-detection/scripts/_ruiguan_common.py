"""睿观业务封装：复用公共调用器，在当前目录落盘并按 CLI 策略输出。"""

import contextlib
import io
import json
import sys
import time
from pathlib import Path

import call_api as api


def is_normal_response(http_status, payload):
    """按公共响应码规则判断，0 和 false 均不表示正常响应。"""
    if http_status is None or not 200 <= http_status < 300:
        return False
    if not isinstance(payload, dict):
        return False
    code = payload.get("errcode")
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        if len(code) != 3 or not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


def run_request(api_path, slug, params, *, inline=False, transport=None, quiet=False):
    """调用 run；外层业务管理缓存，公共调用器始终禁用响应缓存。"""
    # 业务层固定当前目录，并在收费请求前检查实际输出文件。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)

    original_transport = api.call_api
    original_output = api._resolve_output_path
    previous_root = api._SESSION_CACHE.get("_root")
    captured = {}

    def record(path, body):
        status, payload = (transport or original_transport)(path, body)
        captured.update(status=status, payload=payload)
        # HTTP 状态独立于响应体；JSON 错误未必重复包含 errcode。
        # 仅在 stderr 展示本地诊断，保留响应体及上传 stdout 的既有结构。
        print(f"HTTP status: {status if status is not None else 'unavailable'}", file=sys.stderr)
        # 非对象响应也需保存；不让公共输出对 .get 的依赖掩盖原始错误。
        rendered = payload if isinstance(payload, dict) else {
            "error": "接口响应不是 JSON 对象", "response": payload,
        }
        return status, rendered

    try:
        api._SESSION_CACHE["_root"] = str(root)
        # 文件名使用微秒时间戳；独占创建避免覆盖同一时刻已有的结果。
        out_path = api.resolve_data_path(slug, time.time())
        with open(out_path, "x", encoding="utf-8"):
            pass
        api.call_api = record
        api._resolve_output_path = lambda key, _ts: out_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            argv.append("--inline")
        # 公共 run 会吞掉写入 OSError；先缓冲输出，业务层确认原始数据保存后再展示。
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            api.run(api_path, slug, argv=argv)
        payload = captured["payload"]
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        with open(out_path, "w", encoding="utf-8") as file:
            file.write(serialized)
        destination = sys.stderr if quiet else sys.stdout
        if isinstance(payload, dict):
            print(output.getvalue(), end="", file=destination)
        else:
            # 包装对象仅用于兼容公共 run；原始 JSON 和最终输出均不改变结构。
            with contextlib.redirect_stdout(destination):
                print(f"Saved full response: {out_path} ({len(serialized)} bytes)")
                if inline or len(serialized.encode("utf-8")) <= api.SMALL_THRESHOLD:
                    print(serialized)
                else:
                    api.summarize(payload)
    finally:
        api.call_api = original_transport
        api._resolve_output_path = original_output
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
    return captured["status"], captured["payload"]
