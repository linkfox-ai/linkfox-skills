"""Temu 网关运行封装：双鉴权、超时控制、无响应缓存及结果落盘。"""

import contextlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.parse import urlsplit

import call_api as api

SLUG = 'linkfox-temu-manage-product-us'
_LAST_OUTPUT = None
_LAST_HTTP_STATUS = None


def last_http_status():
    """返回最近一次网关 HTTP 状态；连接失败时为 None，不改动原响应。"""
    return _LAST_HTTP_STATUS


def _root():
    """仅允许当前工作目录，失败即报错。"""
    root = Path.cwd() / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def invoke(url, body, token, timeout=150):
    """HTTP 由 call_api 执行；本层负责运行约定和结果加工。"""
    global _LAST_OUTPUT, _LAST_HTTP_STATUS
    _LAST_OUTPUT = None
    _LAST_HTTP_STATUS = None
    parts = urlsplit(url)
    endpoint = parts.path
    # 保留覆盖地址可能带有的前缀；正式端点仍由 run 接收。
    for suffix in ('/temu/proxy', '/temu/fileDownload'):
        if endpoint.endswith(suffix):
            endpoint = suffix
            base = url[:-len(suffix)]
            break
    else:
        raise ValueError('不支持的 Temu 网关地址')

    previous = {name: getattr(api, name) for name in
                ('get_api_base', 'get_api_key', 'Request', 'urlopen', 'call_api',
                 '_linkfox_root', '_resolve_output_path')}
    root = _root()
    captured = {}
    stream = io.StringIO()

    def request_with_token(*args, **kwargs):
        headers = dict(kwargs.get('headers') or {})
        headers['Token'] = token
        kwargs['headers'] = headers
        return previous['Request'](*args, **kwargs)

    def original_timeout(request, **kwargs):
        kwargs['timeout'] = timeout
        return previous['urlopen'](request, **kwargs)

    def transformed(path, params):
        global _LAST_HTTP_STATUS
        status, result = previous['call_api'](path, params)
        _LAST_HTTP_STATUS = status
        if not isinstance(result, dict):
            # 公共 run 的输出层要求对象；完整非对象响应仍保留为 body。
            result = {'body': result}
        # 本地传输状态独立于下载接口返回的上游 httpStatus。
        result['_httpStatus'] = status
        if endpoint == '/temu/proxy':
            raw = result.get('body')
            if isinstance(raw, str) and raw.strip():
                try:
                    result['temuBody'] = json.loads(raw)
                except json.JSONDecodeError:
                    pass
        captured['result'] = result
        return status, result

    def output_path(slug, _ts):
        path = api.resolve_data_path(slug, time.time())
        captured['path'] = path
        return path

    api.get_api_base = lambda: base
    api.get_api_key = lambda: token
    api.Request = request_with_token
    api.urlopen = original_timeout
    api.call_api = transformed
    api._linkfox_root = lambda: root
    api._resolve_output_path = output_path
    argv = [json.dumps(body, ensure_ascii=False), '--no-cache']
    if '--inline' in sys.argv[1:]:
        argv.append('--inline')
    try:
        with contextlib.redirect_stdout(stream):
            operation = re.sub(r'[^A-Za-z0-9_-]+', '-', str(body.get('type') or 'fileDownload'))
            api.run(endpoint, f'{SLUG}-{operation}', argv=argv)
        path = Path(captured['path'])
        # 公共 run 对文件写失败只输出消息，本技能要求失败即报错。
        if not path.is_file():
            raise OSError('完整响应未能保存到当前工作目录')
        result = captured['result']
        _LAST_OUTPUT = (result, stream.getvalue(), path)
        return result
    finally:
        for name, value in previous.items():
            setattr(api, name, value)


def emit_result(result, slug=SLUG, inline=False):
    """复用 run 已保存的结果及输出，避免重复落盘。"""
    global _LAST_OUTPUT
    if _LAST_OUTPUT is not None and _LAST_OUTPUT[0] is result:
        _, output, path = _LAST_OUTPUT
        _LAST_OUTPUT = None
        # 调用入口可在返回后添加 temuBody，再 emit；同步最终加工结果。
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        path.write_text(serialized, encoding='utf-8')
        print(f"Gateway HTTP status: {result['_httpStatus']}")
        if inline:
            print(f'Saved full response: {path} ({len(serialized.encode("utf-8"))} bytes)')
            print(serialized)
        else:
            print(output, end='')
        return
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    previous_root = api._linkfox_root
    api._linkfox_root = _root
    try:
        path = api.resolve_data_path(slug, time.time())
        Path(path).write_text(serialized, encoding='utf-8')
    finally:
        api._linkfox_root = previous_root
    print(f'Saved full response: {path} ({len(serialized.encode("utf-8"))} bytes)')
    if inline or len(serialized.encode('utf-8')) <= api.SMALL_THRESHOLD:
        print(serialized)
    else:
        api.summarize(result)
