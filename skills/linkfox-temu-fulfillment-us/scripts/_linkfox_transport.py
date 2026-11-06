"""通过公共调用器请求，使用 Temu 封装的认证和输出行为。"""

import io
import json
import os
import threading
from contextlib import ExitStack, redirect_stdout
from unittest.mock import patch

import call_api

_LOCK = threading.RLock()


def request_json(url, body, headers, timeout=150):
    """run 负责唯一 HTTP 请求；响应加工、落盘与摘要由业务层负责。"""
    with _LOCK:
        original_call = call_api.call_api
        original_request = call_api.Request
        original_urlopen = call_api.urlopen
        captured = {}

        def make_request(*args, **kwargs):
            kwargs['headers'] = dict(headers)
            return original_request(*args, **kwargs)

        def open_request(req, timeout=150):
            # 支持 call_temu_api 的自定义 timeout，不额外实现 HTTP transport。
            return original_urlopen(req, timeout=captured['timeout'])

        def capture(api_path, params):
            status, result = original_call(api_path, params)
            # Temu 包装对空的 HTTP 错误正文也保留 details。
            if isinstance(result, dict) and status is not None and status >= 400:
                if str(result.get('error', '')).startswith('HTTP '):
                    result.setdefault('details', '')
            captured['result'] = result
            captured['status'] = status
            # run 只接收中间输出对象；隔离上游同名 _cache 字段，且兼容任意 JSON 根类型。
            # 真正响应保存在 captured，由业务层完整处理与输出。
            return status, {'payload': result}

        captured['timeout'] = timeout
        with ExitStack() as stack:
            stack.enter_context(patch.object(call_api, 'get_api_url', lambda _: url))
            stack.enter_context(patch.object(call_api, 'get_api_key', lambda: headers['Authorization']))
            stack.enter_context(patch.object(call_api, 'Request', make_request))
            stack.enter_context(patch.object(call_api, 'urlopen', open_request))
            stack.enter_context(patch.object(call_api, 'call_api', capture))
            # 公共 run 的缓存关闭；中间输出交给业务 emit_result，避免重复保存和打印。
            stack.enter_context(patch.object(call_api, '_cache_path', lambda *_: os.devnull))
            stack.enter_context(patch.object(call_api, '_resolve_output_path', lambda *_: os.devnull))
            stack.enter_context(redirect_stdout(io.StringIO()))
            call_api.run(
                '/temu/fileDownload' if url.endswith('/fileDownload') else '/temu/proxy',
                'linkfox-temu-fulfillment-us',
                [json.dumps(body, ensure_ascii=False), '--no-cache'],
            )
        result = captured['result']
        status = captured['status']
        # HTTP 状态独立于网关业务码，供认证恢复与结果判断使用。
        # 非对象或同名上游字段使用原值包裹，避免覆盖实际响应。
        if isinstance(result, dict) and '_http_status' not in result:
            return {**result, '_http_status': status}
        return {'_http_status': status, '_raw_response': result}
