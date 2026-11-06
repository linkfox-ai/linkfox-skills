"""服装套图的兼容层：复用公共调用器，支持单层缓存、XML 与费用头。"""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError
from xml.etree import ElementTree

import call_api as common

CACHE_TTL_SEC = 24 * 60 * 60


def is_2xx(value):
    if isinstance(value, str):
        value = value.strip()
        if len(value) != 3 or not value.isascii() or not value.isdigit():
            return False
        value = int(value)
    return type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0


def api_error(result):
    """严格沿用公共响应规则；业务 code/error 仅作为额外失败信息。"""
    if not isinstance(result, dict) or result.get('error'):
        return True
    status = result.get('transportHttpStatus', 200)
    if not is_2xx(status):
        return True
    for field in ('errcode', 'code'):
        code = result.get(field)
        if code is None or isinstance(code, str) and not code.strip():
            continue
        if not is_2xx(code):
            return True
    return False


def check_output_directory():
    configured = (os.environ.get('ACPX_WORKSPACES') or '').split(os.pathsep)[0].strip()
    if configured and Path(configured).resolve() != Path.cwd().resolve():
        raise RuntimeError('请取消 ACPX_WORKSPACES，并从可写的任务目录运行')
    output = Path.cwd() / 'linkfox'
    output.mkdir(exist_ok=True)
    probe = output / ('.write-probe-' + str(time.time_ns()))
    try:
        probe.write_bytes(b'')
    finally:
        probe.unlink(missing_ok=True)
    # 在业务层预检后固定当前目录，禁止公共调用器回退到其他目录。
    common._SESSION_CACHE['_root'] = str(output.resolve())


def normalize(body, status, headers, reason=None):
    try:
        result = json.loads(body)
    except (ValueError, TypeError):
        result = None
        try:
            root = ElementTree.fromstring(body)
            if root.tag.rsplit('}', 1)[-1] == 'ToolErrorResponse':
                fields = {child.tag.rsplit('}', 1)[-1]: child.text or '' for child in root}
                code = fields.get('errcode')
                try:
                    code = int(code)
                except (ValueError, TypeError):
                    pass
                result = {'errcode': code, 'errmsg': fields.get('errmsg', '')}
        except ElementTree.ParseError:
            pass
        if result is None:
            result = {'error': f'HTTP {status}: {reason}' if reason else '网关响应格式无效'}
            if body:
                result['details'] = body
    if not isinstance(result, dict):
        result = {'error': '网关响应不是 JSON 对象', 'details': result}
    result['transportHttpStatus'] = status
    for header, field in (('X-Cost-Token', 'costToken'), ('X-Cost-Credit', 'costCredit')):
        value = headers.get(header) if headers is not None else None
        if value is not None:
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass
            result[field] = value
    return result


@contextlib.contextmanager
def response_compatibility():
    """只适配公共 transport 的响应，不另行实现或发起 HTTP 请求。"""
    opener = common.urlopen

    @contextlib.contextmanager
    def adapted(*args, **kwargs):
        try:
            with opener(*args, **kwargs) as response:
                payload = normalize(response.read().decode('utf-8'), response.status, response.headers)
                # 公共调用器只消费 status 与 read()。
                response_view = io.BytesIO(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
                response_view.status = response.status
                yield response_view
        except HTTPError as error:
            raw = error.read().decode('utf-8') if error.fp else ''
            payload = normalize(raw, error.code, error.headers, error.reason)
            raise HTTPError(error.url, error.code, error.reason, error.headers,
                            io.BytesIO(json.dumps(payload, ensure_ascii=False).encode('utf-8'))) from error

    common.urlopen = adapted
    try:
        yield
    finally:
        common.urlopen = opener


def _load_cache(path):
    if not path.is_file() or time.time() - path.stat().st_mtime > CACHE_TTL_SEC:
        return None
    try:
        result = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(result, dict) or api_error(result):
            return None
        result['_cache'] = {'hit': True}
        return result
    except (OSError, ValueError):
        return None


def run_entry(api_path, slug, argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv == ['--help'] or argv == ['-h']:
        print("用法：python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]")
        return 0 if argv else 1
    raw = [arg for arg in argv if arg not in ('--inline', '--no-cache')]
    if len(raw) != 1:
        raise ValueError('请提供一个 JSON 参数对象')
    params = json.loads(raw[0])
    if not isinstance(params, dict):
        raise ValueError('参数必须为 JSON 对象')
    check_output_directory()
    # 先准备完整会话路径，避免 Windows 长路径或目录权限错误在收费后才暴露。
    # 同秒内的上传、创建和轮询分别预留文件，不覆盖已接受任务的响应。
    output_path = common.resolve_data_path(slug, time.time_ns() / 1_000_000_000)
    Path(output_path).write_text('', encoding='utf-8')
    # 使用单层响应缓存的格式、键、路径与 TTL；查询始终绕过缓存。
    use_cache = '--no-cache' not in argv and api_path != '/aigc/taskQuery'
    cache_path = Path(common._cache_path(slug, params))
    cached = _load_cache(cache_path) if use_cache else None
    transport = common.call_api

    def dispatch(path, payload):
        if cached is not None:
            return 200, cached
        with response_compatibility():
            status, result = transport(path, payload)
        if isinstance(result, dict):
            result.setdefault('transportHttpStatus', status)
        if use_cache and common._is_cacheable(status, result) and not api_error(result):
            try:
                cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            except OSError:
                pass
        return status, result

    common.call_api = dispatch
    resolve_output = common._resolve_output_path
    common._resolve_output_path = lambda name, stamp: output_path
    try:
        # 禁用公共 runner 的第二层缓存。
        common.run(api_path, slug, argv=argv + ['--no-cache'])
    finally:
        common.call_api = transport
        common._resolve_output_path = resolve_output
    return 0


def request(api_path, slug, params):
    """提供 call_api(params) 入口，HTTP 经公共 run。"""
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        run_entry(api_path, slug, [json.dumps(params, ensure_ascii=False), '--no-cache'])
    match = re.search(r'^Saved full response: (.+?) \(\d+ bytes\)$', capture.getvalue(), re.M)
    if not match:
        raise RuntimeError('接口响应未保存')
    return json.loads(Path(match.group(1)).read_text(encoding='utf-8'))
