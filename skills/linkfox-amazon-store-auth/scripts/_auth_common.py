"""授权业务封装：兼容处理、脱敏和 CLI；HTTP 与输出统一委托公共 run。"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
import io
import json
import os
from pathlib import Path
import secrets
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError
from xml.etree import ElementTree

import call_api as api
from _token_status_output import strip_raw_tokens

SLUG = 'linkfox-amazon-store-auth'
WARNING = '警告：必须在你日常登录店铺的安全IP（或紫鸟浏览器）下打开授权链接！'


def get_api_base():
    return (os.environ.get('LINKFOX_TOOL_GATEWAY')
            or os.environ.get('STORE_API_BASE_URL')
            or os.environ.get('SPAPI_BASE_URL')
            or 'https://tool-gateway.linkfox.com').rstrip('/')


def response_ok(status, result):
    if status is None or not 200 <= status < 300 or not isinstance(result, dict):
        return False
    value = result.get('errcode')
    if value is None or type(value) is int and value == 0:
        valid = True
    elif isinstance(value, str):
        value = value.strip()
        valid = value in ("", "0") or (len(value) == 3 and value.isascii() and value.isdigit()
                              and 200 <= int(value) < 300)
    else:
        valid = type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0
    return valid and not result.get('error') and result.get('success') is not False


def validate_params(operation, params):
    if not isinstance(params, dict):
        raise ValueError('参数必须是 JSON 对象')
    params = dict(params)
    required = {
        'authorizeUrl': ('region', 'sellerName', 'central', 'marketplace'),
        'authorizedStores': (),
        'refreshToken': ('sellerId',),
        'storeTokens': ('sellerId', 'region'),
        'cancelAuthorization': ('sellerId', 'region'),
    }
    for name in required[operation]:
        value = params.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{name} 必须为非空字符串')
        params[name] = value.strip()
    if 'region' in params:
        region = params['region']
        if not isinstance(region, str) or region.strip() not in ('NA', 'EU', 'FE'):
            raise ValueError('region 必须明确为 NA、EU 或 FE')
        params['region'] = region.strip()
    if operation == 'authorizeUrl' and params['central'] != 'seller':
        raise ValueError('central 必须为 seller')
    if operation == 'cancelAuthorization':
        if len(params['sellerId']) > 64:
            raise ValueError('sellerId 不得超过 64 字符')
        return {key: params[key] for key in ('sellerId', 'region')}
    return params


def parse_json_cli(operation, argv=None):
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            print(f'参数错误：{message}', file=sys.stderr)
            raise SystemExit(1)

    parser = Parser(description='Amazon 店铺授权与连接管理')
    parser.add_argument('params', nargs='?' if operation == 'authorizedStores' else None,
                        default='{}', help='JSON 参数对象')
    parser.add_argument('--inline', action='store_true', help='保存并全量打印响应')
    parser.add_argument('--no-cache', action='store_true', help='兼容选项；本技能始终关闭缓存')
    args = parser.parse_args(argv)
    try:
        return validate_params(operation, json.loads(args.params)), args.inline
    except (ValueError, TypeError) as error:
        print(f'参数错误：{error}', file=sys.stderr)
        raise SystemExit(1)


def normalize_xml(result):
    """将公共调用器返回的 XML 错误正文规范化为 errcode/errmsg。"""
    if not isinstance(result, dict) or not isinstance(result.get('details'), str):
        return result
    try:
        root = ElementTree.fromstring(result['details'])
    except ElementTree.ParseError:
        return result
    if root.tag.rsplit('}', 1)[-1] != 'ToolErrorResponse':
        return result
    fields = {node.tag.rsplit('}', 1)[-1]: node.text or '' for node in root}
    code = fields.get('errcode')
    try:
        code = int(code)
    except (TypeError, ValueError):
        pass
    return {'errcode': code, 'errmsg': fields.get('errmsg', '')}


def oauth_safe_metadata(result):
    """自动授权只在内存保留链接，清理嵌套副本及消息中的重复链接。"""
    urls = set()

    def collect(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'authorizeUrl' and isinstance(value, str) and value:
                    urls.add(value)
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)

    def clean(node):
        if isinstance(node, dict):
            return {key: clean(value) for key, value in node.items() if key != 'authorizeUrl'}
        if isinstance(node, list):
            return [clean(value) for value in node]
        if isinstance(node, str):
            for url in sorted(urls, key=len, reverse=True):
                node = node.replace(url, '[授权链接已隐藏]')
        return node

    collect(result)
    return clean(result)


def invoke(operation, params, *, inline=False, machine=False):
    """返回脱敏业务结果；自动入口只将最终单 JSON 交给调用方安全捕获。"""
    params = validate_params(operation, params)
    # 写请求前验证本地目录，不继承公共资源的用户目录/临时目录回退。
    root = Path.cwd() / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    transport = api.call_api
    opener = api.urlopen
    observed_headers = {}
    state = {}

    @contextmanager
    def observe_response(request, **kwargs):
        # 只观察公共传输层的响应头，网络请求由 call_api 发起。
        try:
            with opener(request, **kwargs) as response:
                observed_headers.update(response.headers or {})
                raw = response.read()
                state['httpStatus'] = response.status
                state['rawBody'] = raw
                yield SimpleNamespace(status=response.status, read=lambda: raw)
        except HTTPError as error:
            observed_headers.update(error.headers or {})
            raise

    def processed_response(path, body):
        try:
            status, result = transport(path, body)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            status = state.get('httpStatus')
            raw = state.get('rawBody', b'').decode('utf-8', errors='replace')
            result = normalize_xml({'error': f'网关响应格式错误：{error}', 'details': raw})
        result = normalize_xml(result)
        if not isinstance(result, dict):
            result = {'error': '网关响应必须为 JSON 对象', 'response': result}
        # 先脱敏后交给公共 run，避免原始 token 进入文件或摘要。
        result = strip_raw_tokens(result)
        headers = {key.lower(): value for key, value in observed_headers.items()}
        for header, field in (('x-cost-token', 'costToken'), ('x-cost-credit', 'costCredit')):
            if header in headers:
                value = headers[header]
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    pass
                result[field] = value
        if status is None or not 200 <= status < 300:
            result['transportHttpStatus'] = status
        state['result'] = result
        state['ok'] = response_ok(status, result)
        if machine and operation == 'authorizeUrl':
            # 完整 OAuth URL 只留在内存；公共落盘仅记录非敏感状态。
            return status, oauth_safe_metadata(result)
        return status, result

    def strict_output_path(slug, _ts):
        # 低精度时钟、时钟回拨或并发调用也不覆盖已保存的响应。
        path = api.resolve_data_path(slug, time.time(), ext=f'{secrets.token_hex(8)}.json')
        state['outputPath'] = path
        return path

    # 响应缓存始终禁用，无需创建空缓存目录。
    def unused_cache_path(slug, _params):
        return str(root / '.cache' / slug / 'disabled.json')

    captured = io.StringIO()
    try:
        with patch.object(api, 'get_api_base', get_api_base), \
             patch.object(api, 'call_api', processed_response), \
             patch.object(api, 'urlopen', observe_response), \
             patch.object(api, '_linkfox_root', lambda: str(root)), \
             patch.object(api, '_resolve_output_path', strict_output_path), \
             patch.object(api, '_cache_path', unused_cache_path), \
             redirect_stdout(captured):
            argv = [json.dumps(params, ensure_ascii=False), '--no-cache']
            if inline:
                argv.append('--inline')
            api.run('/spApi/' + operation, SLUG + '-' + operation, argv=argv)
    except OSError as error:
        if 'result' in state:
            state['result']['outputError'] = str(error)
            if not machine:
                print(json.dumps(state['result'], ensure_ascii=False))
            print('请求已完成但响应落盘失败，请先核验结果，勿直接重放。', file=sys.stderr)
            return state['result'], False
        raise
    output = captured.getvalue()
    if not Path(state['outputPath']).is_file():
        # 公共 run 吞掉保存错误；业务封装继续如实报告，且不让重放请求。
        state['ok'] = False
        state['result']['outputError'] = '请求已完成但响应落盘失败，请先核验结果，勿直接重放。'
        print(state['result']['outputError'], file=sys.stderr)
    if not machine:
        print(output, end='')
    return state['result'], state['ok']


def run_json(operation, argv=None):
    params, inline = parse_json_cli(operation, argv)
    try:
        result, ok = invoke(operation, params, inline=inline)
    except OSError as error:
        print(f'本地输出错误：{error}', file=sys.stderr)
        return 1
    if ok and operation == 'authorizeUrl':
        if not result.get('authorizeUrl'):
            return 1
        print('请在浏览器打开以下链接并完成授权：', file=sys.stderr)
        print(result['authorizeUrl'], file=sys.stderr)
        print(WARNING, file=sys.stderr)
    elif ok and operation == 'authorizedStores':
        print(f"已授权店铺数：{result.get('total', len(result.get('stores', [])))}", file=sys.stderr)
    elif ok and operation in ('refreshToken', 'storeTokens'):
        from _token_status_output import print_status_note
        print_status_note(result)
    elif ok and operation == 'cancelAuthorization':
        if result.get('success') is not True:
            return 1
        print('当前成员连接已解绑或原本不存在；令牌、其他成员连接与 Amazon 授权保留。', file=sys.stderr)
    return 0 if ok else 1
