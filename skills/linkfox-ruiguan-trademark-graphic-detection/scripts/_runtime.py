"""业务层约束：只在当前目录落盘，不改变公共调用器文件。"""

from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import time

import call_api as api


def response_object(payload):
    """公共 CLI 需要对象；异常响应保留完整原值供排查。"""
    if isinstance(payload, dict):
        if '_cache' in payload and not isinstance(payload['_cache'], dict):
            return {'error': '接口 _cache 字段不是 JSON 对象', 'response': payload}
        return payload
    return {'error': '接口响应不是 JSON 对象', 'response': payload}


def response_with_status(status, payload):
    """保留本次传输状态，供落盘、缓存和认证/用量错误判断。"""
    return {**response_object(payload), '_http_status': status}


@contextmanager
def output_in_cwd():
    cwd = Path.cwd().resolve()
    if any(cwd == p or p in cwd.parents for p in (Path('/tmp'), Path('/private/tmp'))):
        raise OSError('禁止将本技能响应写入 /tmp，请选择可写的工作目录')
    root = cwd / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    previous_root = api._SESSION_CACHE.get('_root')
    previous_output_path = api._resolve_output_path
    output_paths = []

    def resolve_output_path(slug, _ts):
        # 使用微秒时间，避免同一秒内的调用覆盖已保存的响应。
        path = api.resolve_data_path(slug, time.time())
        output_paths.append(path)
        return path

    api._SESSION_CACHE['_root'] = str(root)
    api._resolve_output_path = resolve_output_path
    try:
        yield
        # 公共 run 会打印而不抛出保存错误；业务流程必须在上传等后续步骤前失败。
        for path in output_paths:
            try:
                with open(path, encoding='utf-8') as saved:
                    json.load(saved)
            except (OSError, ValueError) as exc:
                raise RuntimeError(f'完整响应保存失败：{path}：{exc}') from exc
    finally:
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop('_root', None)
        else:
            api._SESSION_CACHE['_root'] = previous_root
