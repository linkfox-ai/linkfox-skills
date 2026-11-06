"""复用公共调用器，兼容 Temu 双请求头、旧地址与业务输出加工。"""

import io
import json
import os
import time
from contextlib import redirect_stdout
from unittest.mock import patch

import call_api

SLUG = "linkfox-temu-returns-refunds-eu"
_pending_output = None


def writable_root():
    """业务响应必须写入 cwd；请求前检查，禁止回退其他目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write_probe")
    with open(probe, "w", encoding="utf-8"):
        pass
    os.remove(probe)
    return root


def request(url, body, token, timeout=150):
    global _pending_output
    _pending_output = None
    root = writable_root()
    original_request = call_api.Request
    original_open = call_api.urlopen
    original_call = call_api.call_api
    captured = {}

    def make_request(*args, **kwargs):
        req = original_request(*args, **kwargs)
        req.add_header("Token", token)
        return req

    def open_request(req, timeout=150):
        return original_open(req, timeout=captured["timeout"])

    def invoke(api_path, params):
        status, result = original_call(api_path, params)
        if isinstance(result, dict):
            result["transportHttpStatus"] = status
        captured["result"] = result
        return status, result

    captured["timeout"] = timeout
    # 提前验证实际会话目录，而不只是 linkfox 根目录，避免写入操作后才发现无法保存。
    with patch.object(call_api, "_linkfox_root", lambda: root):
        captured["path"] = call_api.resolve_data_path(SLUG, time.time())
    with open(captured["path"], "x", encoding="utf-8"):
        pass
    with patch.object(call_api, "Request", make_request), \
         patch.object(call_api, "urlopen", open_request), \
         patch.object(call_api, "get_api_key", lambda: token), \
         patch.object(call_api, "get_api_url", lambda path: url), \
         patch.object(call_api, "call_api", invoke), \
         patch.object(call_api, "_linkfox_root", lambda: root), \
         patch.object(call_api, "_resolve_output_path", lambda slug, ts: captured["path"]), \
         redirect_stdout(io.StringIO()):
        call_api.run("/temu/fileDownload" if url.endswith("/temu/fileDownload") else "/temu/proxy",
                     SLUG, argv=[json.dumps(body, ensure_ascii=False), "--no-cache"])
    result = captured["result"]
    _pending_output = (result, captured["path"])
    return result


def take_output_path(result):
    """业务解析后回写同一个响应文件，避免重复落盘和重复展示。"""
    global _pending_output
    pending, _pending_output = _pending_output, None
    if pending is not None and pending[0] is result:
        return pending[1]
    return None
