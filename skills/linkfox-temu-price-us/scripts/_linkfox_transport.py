#!/usr/bin/env python3
"""兼容 Temu 认证与网关配置，统一委托公共调用器。"""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import time


# 只共享进程内自动会话标识，不保存或复用接口响应。
_SESSION_STATE = {}


class GatewayResult(dict):
    """以字典接口返回结果，附带已保存的输出与 HTTP 状态。"""


def _load_caller():
    # 每次调用使用独立模块实例，兼容逻辑不修改公共文件或污染其他调用。
    spec = importlib.util.spec_from_file_location(
        "_temu_public_call_api", Path(__file__).with_name("call_api.py")
    )
    caller = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caller)
    return caller


def require_output_root():
    """在当前工作目录落盘；不可写时在请求前停止。"""
    cwd = Path.cwd().resolve()
    temporary = Path('/tmp').resolve()
    if cwd == temporary or temporary in cwd.parents:
        raise OSError('本技能禁止在 /tmp 落盘，请在项目工作目录运行。')
    root = cwd / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    probe = root / ('.temu-write-probe-' + str(time.time_ns()))
    try:
        with probe.open('x', encoding='utf-8'):
            pass
    finally:
        if probe.exists():
            probe.unlink()
    return str(root)


def run_gateway(url, body, token, headers, timeout=150):
    """调用 call_api.run；保留双请求头、URL、超时与无缓存行为。"""
    root = require_output_root()
    caller = _load_caller()
    original_request = caller.Request
    original_open = caller.urlopen
    original_call = caller.call_api
    result_box = []

    def request_with_headers(*args, **kwargs):
        kwargs['headers'] = {**kwargs.get('headers', {}), **headers}
        return original_request(*args, **kwargs)

    def open_with_timeout(request, **kwargs):
        kwargs['timeout'] = timeout
        return original_open(request, **kwargs)

    def capture_response(path, payload):
        status, raw = original_call(path, payload)
        result = GatewayResult(raw)
        result.transport_http_status = status
        result['transportHttpStatus'] = status
        # 代理接口在保存前完成业务解析，避免原始与加工结果重复落盘。
        if url.rstrip('/').endswith('/temu/proxy'):
            nested = result.get('body')
            if isinstance(nested, str) and nested.strip():
                try:
                    result['temuBody'] = json.loads(nested)
                except json.JSONDecodeError:
                    pass
        result_box.append(result)
        return status, result

    caller.get_api_key = lambda: token
    caller.get_api_url = lambda path: url
    caller.Request = request_with_headers
    caller.urlopen = open_with_timeout
    caller.call_api = capture_response
    caller._linkfox_root = lambda: root
    caller._SESSION_CACHE = _SESSION_STATE
    operation = body.get('type') if url.rstrip('/').endswith('/temu/proxy') else 'fileDownload'
    slug = 'linkfox-temu-price-us-' + str(operation or 'proxy').replace('.', '-')
    # 请求前确认实际会话 data 目录可写，防止店铺写入后才发现无法保存。
    out_path = Path(caller.resolve_data_path(slug, time.time()))
    probe = out_path.parent / ('.temu-write-probe-' + str(time.time_ns()))
    try:
        with probe.open('x', encoding='utf-8'):
            pass
    finally:
        if probe.exists():
            probe.unlink()
    caller._resolve_output_path = lambda slug, ts: str(out_path)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        caller.run(
            '/temu/proxy' if operation != 'fileDownload' else '/temu/fileDownload',
            slug,
            [json.dumps(body, ensure_ascii=False), '--inline', '--no-cache'],
        )
    result = result_box[0]
    # run 已保存一次完整结果；业务入口随后调用 emit_result 展示。
    lines = output.getvalue().splitlines()
    saved_prefix = 'Saved full response: ' + str(out_path) + ' ('
    if not lines or not lines[0].startswith(saved_prefix):
        raise OSError(f'完整响应保存失败：{out_path}。请先核对操作状态，不要自动重放请求。')
    result.saved_line = lines[0]
    return result
