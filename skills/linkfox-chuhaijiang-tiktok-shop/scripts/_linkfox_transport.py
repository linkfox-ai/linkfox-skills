"""经公共 run 调用网关，由业务入口管理缓存、完整响应和输出。"""

import contextlib
import io
import json
import os

import call_api as api


def request(api_path, slug, params):
    """返回 HTTP 状态与原始响应；不创建第二层缓存或重复数据文件。"""
    transport = api.call_api
    cache_path = api._cache_path
    output_path = api._resolve_output_path
    session_id = os.environ.get("SESSION_ID")
    captured = {}

    def capture(path, body):
        status, payload = transport(path, body)
        captured["result"] = (status, payload)
        # run 的输出要求对象；包裹任意 JSON 类型，返回时仍使用未经修改的原体。
        return status, {"payload": payload}

    try:
        api.call_api = capture
        # run 即使 --no-cache 也计算缓存路径；在此禁止其创建多余目录。
        api._cache_path = lambda *_: ""
        # 缓存、文件和摘要由业务入口统一处理，公共 run 的中间输出丢弃。
        api._resolve_output_path = lambda *_: os.devnull
        os.environ["SESSION_ID"] = (session_id or "").strip()
        with contextlib.redirect_stdout(io.StringIO()):
            api.run(api_path, slug, argv=[json.dumps(params, ensure_ascii=False), "--no-cache", "--inline"])
        return captured["result"]
    finally:
        api.call_api = transport
        api._cache_path = cache_path
        api._resolve_output_path = output_path
        if session_id is None:
            os.environ.pop("SESSION_ID", None)
        else:
            os.environ["SESSION_ID"] = session_id
