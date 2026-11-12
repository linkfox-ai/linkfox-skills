"""POD 专用业务适配；与原产品检测的 api_support/call_api 状态相互独立。"""

from contextlib import redirect_stdout
import io
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import pod_call_api as common_api


def _check_session_boundaries(root, ts):
    """在公共调用器创建/更新元数据前检查真实路径，包含 junction/symlink。"""
    cwd = Path.cwd().resolve()
    real_root = root.resolve()
    if not real_root.is_relative_to(cwd):
        raise OSError('会话输出根目录超出当前工作目录')
    sid = common_api._session_id(ts)
    if not sid or sid in ('.', '..') or any(c in sid for c in ('/', '\\', ':')):
        raise ValueError('SESSION_ID 必须为不含路径分隔符的会话标识')
    date_dir = root / time.strftime('%Y-%m-%d', time.localtime(ts))
    session_dir = date_dir / sid
    for candidate in (date_dir, session_dir, session_dir / 'data',
                      session_dir / '_meta.json', root / 'index.jsonl'):
        if not candidate.resolve().is_relative_to(real_root):
            raise OSError('会话输出路径超出当前工作目录')


def prepare_root(ts=None):
    """在创建响应缓存或会话数据前确认真实路径边界及当前目录可写。"""
    ts = time.time() if ts is None else ts
    cwd = Path.cwd().resolve()
    if cwd == Path('/tmp').resolve() or Path('/tmp').resolve() in cwd.parents:
        raise OSError('禁止将会话数据写入 /tmp，请切换工作目录')
    root = cwd / 'linkfox'
    _check_session_boundaries(root, ts)
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    # 业务封装将响应根目录固定到本次工作目录。
    common_api._SESSION_CACHE['_root'] = str(root)
    return root


def prepare_output(slug):
    """请求前确认输出目录可写，不使用公共调用器的目录回退。"""
    ts = time.time()
    root = prepare_root(ts)
    _check_session_boundaries(root, ts)
    path = Path(common_api.resolve_data_path(slug, ts))
    if not path.resolve().is_relative_to(root.resolve()):
        raise OSError('会话输出路径超出当前工作目录')
    # 公共元数据更新会容忍旧文件读取失败；此入口在收费前显式检查。
    with (path.parent.parent / '_meta.json').open('r+', encoding='utf-8') as metadata:
        json.load(metadata)
    with tempfile.TemporaryFile(dir=path.parent):
        pass
    while True:
        try:
            with path.open('x', encoding='utf-8'):
                pass
            break
        except FileExistsError:
            ts += 0.000001
            _check_session_boundaries(root, ts)
            path = Path(common_api.resolve_data_path(slug, ts))
    return path


def invoke_api(api_path, slug, params, output_path=None):
    """通过 run 调用；禁用公共缓存，上传和检测使用各自的缓存约定。

    run 不返回结果和 HTTP 状态，故临时记录已有 transport 的返回值及
    预先确认的输出路径；不实现额外 HTTP transport。两个入口均为串行 CLI。
    """
    output_path = Path(output_path) if output_path is not None else prepare_output(slug)
    transport = common_api.call_api
    resolver = common_api._resolve_output_path
    observed = {}
    log = io.StringIO()

    def tracked_transport(path, body):
        status, payload = transport(path, body)
        payload = common_api.redact(payload)
        observed['status'] = status
        observed['payload'] = payload
        # 公共 run 的输出阶段要求对象且 _cache 为对象。兼容异常 JSON，
        # 仅在内部包裹，落盘后恢复原响应，不修改公共脚本或另发请求。
        observed['wrapped'] = (
            not isinstance(payload, dict)
            or not isinstance(payload.get('_cache', {}), dict)
        )
        if observed['wrapped']:
            return status, {'response': payload}
        return status, payload

    try:
        common_api.call_api = tracked_transport
        common_api._resolve_output_path = lambda _slug, _ts: str(output_path)
        with redirect_stdout(log):
            common_api.run(api_path, slug, [json.dumps(params, ensure_ascii=False), '--no-cache'])
        # run 会捕获写入错误；读取文件确保落盘失败不会误报成功。
        payload = json.loads(output_path.read_text(encoding='utf-8'))
        if observed.get('wrapped'):
            payload = observed['payload']
            output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        return observed.get('status'), payload, output_path, log.getvalue()
    finally:
        common_api.call_api = transport
        common_api._resolve_output_path = resolver


def normal_response(status, payload):
    """按公共响应规则判断，0 和 false 不视为空。"""
    if type(status) is not int or not 200 <= status < 300 or not isinstance(payload, dict):
        return False
    code = payload.get('errcode')
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


def save_response(slug, result):
    path = prepare_output(slug)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return path


def detection_success(status, payload, mode):
    """检测必须真正完成；空候选数组属于有效结果。"""
    if not normal_response(status, payload) or payload.get('error'):
        return False
    if not isinstance(payload.get('results'), list):
        return False
    if mode == 'lite':
        return (payload.get('status') == 'completed' and payload.get('resultStatus') == 'success'
                and payload.get('checkMode') == 'lite')
    return payload.get('status') in ('success', 'completed')


def _detection_cache_path(api_path, slug, params):
    identity = hashlib.sha256(common_api.get_api_key().encode('utf-8')).hexdigest()
    cache_input = {'gateway': common_api.get_api_base(), 'endpoint': api_path,
                   'identity': identity, 'params': params}
    digest = hashlib.sha256(json.dumps(cache_input, ensure_ascii=False, sort_keys=True,
                                       separators=(',', ':')).encode('utf-8')).hexdigest()
    root = prepare_root()
    directory = root / '.cache' / slug
    cache_path = directory / f'{slug}-{digest}.json'
    for candidate in (root / '.cache', directory, cache_path):
        if not candidate.resolve().is_relative_to(root.resolve()):
            raise OSError('检测缓存路径超出当前工作目录')
    directory.mkdir(parents=True, exist_ok=True)
    return cache_path


def _load_detection_cache(path, mode):
    try:
        if time.time() - path.stat().st_mtime > 24 * 60 * 60:
            return None
        cached = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(cached, dict) or cached.get('_cache_version') != 2:
            return None
        payload = cached.get('body')
        if not detection_success(cached.get('http_status'), payload, mode):
            return None
        payload = common_api.redact(payload)
        payload['_cache'] = {'hit': True}
        return payload
    except (OSError, ValueError):
        return None


def run_detection(api_path, slug, mode, argv=None, validate=None):
    """共用检测入口；公共 run 完成传输及首次落盘，只维护一层成功缓存。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    usage = f"用法：{os.path.basename(sys.argv[0])} '<JSON 参数>' [--inline] [--no-cache]"
    if '--help' in argv or '-h' in argv:
        print(usage)
        return 0
    inline = '--inline' in argv
    use_cache = '--no-cache' not in argv
    positional = [arg for arg in argv if arg not in ('--inline', '--no-cache')]
    if len(positional) != 1:
        print(usage, file=sys.stderr)
        return 1
    try:
        params = json.loads(positional[0])
        if not isinstance(params, dict):
            raise ValueError('JSON 参数必须为对象')
        if validate is not None:
            validate(params)
        output_path = prepare_output(slug)
        # 缓存命中也需确认当前身份；不读取旧的参数单独哈希缓存。
        cache_path = _detection_cache_path(api_path, slug, params) if use_cache else None
        result = _load_detection_cache(cache_path, mode) if use_cache else None
        if result is None:
            status, result, _, _ = invoke_api(api_path, slug, params, output_path)
            if isinstance(result, dict):
                result = dict(result, _transportHttpStatus=status)
        else:
            status = result.get('_transportHttpStatus')
            print(f'Cache hit: {cache_path}', file=sys.stderr)
        result = common_api.redact(result)
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        output_path.write_text(serialized, encoding='utf-8')
        success = detection_success(status, result, mode)
        cache_meta = result.get('_cache') if isinstance(result, dict) else None
        cache_hit = isinstance(cache_meta, dict) and cache_meta.get('hit')
        if success and use_cache and not cache_hit:
            try:
                cache_path.write_text(json.dumps({'_cache_version': 2, 'http_status': status,
                                                  'body': result}, ensure_ascii=False, indent=2),
                                      encoding='utf-8')
            except OSError as exc:
                print(f'成功响应已保存，但缓存写入失败：{common_api.redact(str(exc))}', file=sys.stderr)
        print(f'Saved full response: {output_path} ({len(serialized.encode("utf-8"))} bytes)')
        print(f'HTTP 状态：{status}', file=sys.stderr)
        if inline or len(serialized.encode('utf-8')) <= common_api.SMALL_THRESHOLD:
            print(serialized)
        else:
            common_api.summarize(result)
        if not success:
            print('检测未成功完成，请按 references/api.md 处理；不自动重试', file=sys.stderr)
        return 0 if success else 1
    except (OSError, ValueError) as exc:
        print(f'执行失败：{common_api.redact(str(exc))}', file=sys.stderr)
        return 1
