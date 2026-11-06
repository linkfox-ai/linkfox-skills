"""业务适配：复用公共调用器，固定当前目录，保留 HTTP 状态及完整响应。"""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import time

import call_api as common_api


def prepare_root():
    """在创建响应缓存或会话数据前确认当前目录可写。"""
    cwd = Path.cwd().resolve()
    if cwd == Path('/tmp').resolve() or Path('/tmp').resolve() in cwd.parents:
        raise OSError('禁止将会话数据写入 /tmp，请切换工作目录')
    root = cwd / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    # 业务封装将响应根目录固定到本次工作目录。
    common_api._SESSION_CACHE['_root'] = str(root)
    sid = common_api._session_id(time.time())
    if not sid or sid in ('.', '..') or any(c in sid for c in ('/', '\\', ':')):
        raise ValueError('SESSION_ID 必须为不含路径分隔符的会话标识')
    return root


def prepare_output(slug):
    """请求前确认输出目录可写，不使用公共调用器的目录回退。"""
    root = prepare_root()
    path = Path(common_api.resolve_data_path(slug, time.time()))
    if not path.resolve().is_relative_to(root.resolve()):
        raise OSError('会话输出路径超出当前工作目录')
    with tempfile.TemporaryFile(dir=path.parent):
        pass
    return path


def invoke_api(api_path, slug, params):
    """通过 run 调用；禁用公共缓存，上传和检测使用各自的缓存约定。

    run 不返回结果和 HTTP 状态，故临时记录已有 transport 的返回值及
    预先确认的输出路径；不实现额外 HTTP transport。两个入口均为串行 CLI。
    """
    output_path = prepare_output(slug)
    transport = common_api.call_api
    resolver = common_api._resolve_output_path
    observed = {}
    log = io.StringIO()

    def tracked_transport(path, body):
        status, payload = transport(path, body)
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
