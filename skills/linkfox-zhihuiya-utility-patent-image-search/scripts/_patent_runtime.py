"""专利业务封装：复用公共调用器，限定落盘目录并保留预签名 CLI 输出。"""

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import time

import call_api as api

SLUG = "linkfox-zhihuiya-utility-patent-image-search"


def is_normal_response(http_status, payload):
    """按接口公共规则检查 HTTP 与 errcode，保留 false/0 为错误。"""
    if http_status is None or not 200 <= http_status < 300 or not isinstance(payload, dict):
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


def response_output(http_status, body):
    """保留本地 HTTP 诊断；非对象响应保留原文。"""
    output = dict(body) if isinstance(body, dict) else {"error": "接口未返回 JSON 对象", "response": body}
    output["_http_status"] = http_status
    return output


def run_request(api_path, operation, params, *, inline=False, quiet=False, transport=None, cache_path=None):
    """调用 run(--no-cache) 并捕获原始结果；缓存由检索脚本单独管理。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 在付费请求前确认当前目录可写，避免公共调用器回退到其他目录。
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_transport = api.call_api
    previous_path = api._resolve_output_path
    previous_cache_path = api._cache_path
    previous_root = api._SESSION_CACHE.get("_root")
    captured = {}

    def invoke(path, request_params):
        status, body = (transport or previous_transport)(path, request_params)
        captured.update(status=status, body=body)
        # 公共调用器的输出逻辑要求对象；非对象保留原文并明确标记异常。
        output = response_output(status, body)
        captured["output"] = output
        if not quiet:
            print(f"HTTP status: {status if status is not None else 'unknown'}")
        return status, output

    api.call_api = invoke
    if cache_path is not None:
        # run 即使禁用缓存也会计算并展示缓存路径；使用检索脚本的业务缓存路径，避免误报路径。
        api._cache_path = lambda _slug, _params: os.fspath(cache_path)
    api._SESSION_CACHE["_root"] = str(root)
    argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    try:
        # 在请求前验证实际输出路径；同秒调用也不会覆盖上一份响应。
        output_path = api.resolve_data_path(f"{SLUG}-{operation}", time.time())
        with open(output_path, "x", encoding="utf-8"):
            pass
        os.remove(output_path)
        api._resolve_output_path = lambda _slug, _ts: output_path
        if quiet:
            with contextlib.redirect_stdout(io.StringIO()):
                api.run(api_path, f"{SLUG}-{operation}", argv=argv)
        else:
            api.run(api_path, f"{SLUG}-{operation}", argv=argv)
        # 公共调用器只打印写盘异常；业务流程必须确认完整保存后才能继续上传。
        expected = json.dumps(captured["output"], ensure_ascii=False, indent=2)
        if Path(output_path).read_text(encoding="utf-8") != expected:
            raise OSError(f"完整响应未能保存: {output_path}")
    finally:
        api.call_api = previous_transport
        api._resolve_output_path = previous_path
        api._cache_path = previous_cache_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
    return captured["status"], captured["body"]
