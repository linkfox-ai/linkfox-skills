"""通过公共调用器运行请求，兼容业务缓存、严格落盘和上传 CLI。"""

import contextlib
import io
import json
import tempfile
import time
from pathlib import Path

import call_api as api


def prepare_output_root():
    """在读取缓存或请求前检查落盘位置，禁止先在 /tmp 建缓存。"""
    cwd = Path.cwd()
    if cwd == Path('/tmp') or Path('/tmp') in cwd.parents:
        raise OSError('响应不得保存到 /tmp')
    root = cwd / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    # 请求前确认当前工作目录可写，禁止公共调用器回退到其他位置。
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def run_gateway(api_path, slug, params, *, inline=False, cached_result=None,
                cached_status=None, cache_hit=False):
    """返回 (HTTP 状态, 完整响应, CLI 输出)，公共调用器不再缓存响应。"""
    root = prepare_output_root()

    previous_root = api._SESSION_CACHE.get('_root')
    previous_transport = api.call_api
    previous_output_path = api._resolve_output_path
    captured = {}
    output = io.StringIO()
    try:
        api._SESSION_CACHE['_root'] = str(root)
        # 在网络请求前分配文件；保留微秒，避免同秒调用覆盖完整响应。
        out_path = api.resolve_data_path(slug, time.time())

        def transport(path, payload):
            if not cache_hit and cached_result is None:
                status, result = previous_transport(path, payload)
            else:
                # 业务缓存已经命中，不再次产生网络请求或重复费用。
                status, result = cached_status, cached_result
            captured.update(status=status, result=result)
            return status, result

        api.call_api = transport
        api._resolve_output_path = lambda _slug, _ts: out_path
        argv = [json.dumps(params, ensure_ascii=False), '--no-cache']
        if inline:
            argv.append('--inline')
        with contextlib.redirect_stdout(output):
            try:
                api.run(api_path, slug, argv=argv)
            except AttributeError as exc:
                # 公共调用器在保存后假定响应为对象并读取 .get('_cache')。
                # 只兼容这里的非对象 JSON；其他程序异常仍向上抛出。
                result = captured.get('result')
                if (
                    not captured or isinstance(result, dict)
                    or exc.name != 'get' or exc.obj is not result
                    or not Path(out_path).is_file()
                ):
                    raise
                serialized = json.dumps(result, ensure_ascii=False, indent=2)
                if inline or len(serialized.encode('utf-8')) <= api.SMALL_THRESHOLD:
                    print(serialized)
                else:
                    api.summarize(result)
        # 公共脚本会记录写入错误；业务流程要求完整响应确实落盘才继续。
        if not Path(out_path).is_file():
            raise OSError(f'完整响应未能保存：{out_path}')
        return captured['status'], captured['result'], output.getvalue()
    finally:
        api.call_api = previous_transport
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop('_root', None)
        else:
            api._SESSION_CACHE['_root'] = previous_root


def is_normal_response(status, result):
    """正常响应条件：HTTP 2xx 且 errcode 缺失、为空或为 2xx。"""
    return (
        status is not None
        and 200 <= status < 300
        and isinstance(result, dict)
        and api._is_cacheable(200, result)
    )
