"""业务脚本与公共执行器的适配；本模块不实现 HTTP 或响应缓存。"""

from contextlib import nullcontext, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import time

import call_api as api


def ensure_output_root():
    """遵守本技能的当前目录落盘约定，不使用公共执行器的目录回退。"""
    cwd = Path.cwd().resolve()
    if cwd.as_posix() == '/tmp' or cwd.as_posix().startswith('/tmp/'):
        raise OSError('完整响应禁止保存到 /tmp，请从可写的项目目录运行')
    root = cwd / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def is_normal_response(http_status, payload):
    """复用公共 errcode 判断，并允许文档规定的 HTTP 2xx。"""
    return (http_status is not None and 200 <= http_status < 300
            and api._is_cacheable(200, payload))


def run_request(api_path, slug, params, *, transform=None, cached=None,
                on_result=None, inline=False, quiet=False):
    """通过 run 调用并落盘一次，返回状态与原始响应；不启用第二层缓存。"""
    root = ensure_output_root()
    transport = api.call_api
    previous_root = api._SESSION_CACHE.get('_root')
    previous_output_path = api._resolve_output_path
    outcome = []
    reserved_path = None
    reserved_created = False

    def invoke(path, request_params):
        status, payload = ((200, cached) if cached is not None
                           else transport(path, request_params))
        outcome[:] = [status, payload]
        if cached is None and on_result is not None:
            on_result(payload)
        return status, payload

    def output_path(response_slug, _ts):
        return str(reserved_path)

    api._SESSION_CACHE['_root'] = str(root)
    try:
        # 根目录可写不代表会话 data 目录可写。先预留完整输出文件，
        # 再执行可能嵌套申请上传凭证的图片转换，最后进入收费图搜。
        reserved_path = Path(api.resolve_data_path(slug, time.time()))
        with reserved_path.open('x', encoding='utf-8'):
            pass
        reserved_created = True
        # 安装回调前完成预处理，避免嵌套上传复用图搜回调。
        # 缓存命中跳过认证、图片读取和上传。
        prepared = params
        if cached is None:
            api.get_api_key()
            if transform is not None:
                prepared = transform(params)
        api.call_api = invoke
        api._resolve_output_path = output_path
        argv = [json.dumps(prepared, ensure_ascii=False), '--no-cache']
        if inline:
            argv.append('--inline')
        with redirect_stdout(io.StringIO()) if quiet else nullcontext():
            api.run(api_path, slug, argv=argv)
        # 公共执行器会打印保存错误后返回；业务封装必须将不完整落盘报错。
        expected = json.dumps(outcome[1], ensure_ascii=False, indent=2)
        if reserved_path.read_text(encoding='utf-8') != expected:
            raise OSError(f'完整响应保存失败: {reserved_path}')
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop('_root', None)
        else:
            api._SESSION_CACHE['_root'] = previous_root
        if reserved_created and reserved_path.exists() and reserved_path.stat().st_size == 0:
            reserved_path.unlink()
    return tuple(outcome)
