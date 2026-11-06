#!/usr/bin/env python3
"""业务封装共用的调用入口：使用公共调用器，约束落盘位置并保留响应。"""

import contextlib
import io
import os
import tempfile
import time

import call_api


def run_gateway(api_path, slug, params, *, inline=False, quiet=False, transport=None):
    """返回 (HTTP 状态, 响应体)，公共层始终关闭缓存，由检索脚本维护本地缓存。"""
    import json

    # 当前目录不可写时报错，不使用公共调用器的家目录/临时目录回退。
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    original_call = call_api.call_api
    original_root = call_api._linkfox_root
    original_path = call_api._resolve_output_path
    observed = {}
    request = transport or original_call

    def invoke(path, body):
        status, result = request(path, body)
        observed.update(status=status, result=result)
        return status, result

    def execute(argv):
        try:
            call_api.run(api_path, slug, argv=argv)
        except AttributeError:
            # 公共调用器的输出阶段假定响应及 _cache 均为对象；
            # 非标准 JSON 仍须保存原始内容，不能再次请求或改写业务响应。
            if "result" not in observed:
                raise
            result = observed["result"]
            if isinstance(result, dict) and isinstance(result.get("_cache", {}), dict):
                raise
            serialized = json.dumps(result, ensure_ascii=False, indent=2)
            if inline or len(serialized.encode("utf-8")) <= call_api.SMALL_THRESHOLD:
                print(serialized)
            else:
                call_api.summarize(result)

    try:
        call_api._linkfox_root = lambda: root
        # 请求前确认会话文件可写；使用微秒文件名防止连续调用互相覆盖。
        output_path = call_api.resolve_data_path(slug, time.time())
        with open(output_path, "w", encoding="utf-8"):
            pass
        call_api._resolve_output_path = lambda _slug, _ts: output_path
        call_api.call_api = invoke
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            argv.append("--inline")
        if quiet:
            with contextlib.redirect_stdout(io.StringIO()):
                execute(argv)
        else:
            execute(argv)
        return observed["status"], observed["result"]
    finally:
        call_api.call_api = original_call
        call_api._linkfox_root = original_root
        call_api._resolve_output_path = original_path


def normal_response(http_status, payload):
    """按公共规则判断 HTTP 和 errcode；0、false 不为空。"""
    if http_status is None or not 200 <= http_status < 300 or not isinstance(payload, dict):
        return False
    code = payload.get("errcode")
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        try:
            code = int(code)
        except ValueError:
            return False
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0
