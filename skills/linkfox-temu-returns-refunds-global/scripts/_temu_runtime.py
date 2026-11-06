"""公共调用器的 Temu 兼容封装：双鉴权头、无响应缓存和业务 CLI 输出。"""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import time

import call_api as api

SLUG = "linkfox-temu-returns-refunds-global"
_OUTPUTS = {}


def invoke_gateway(url, body, token, timeout=150):
    """实际传输、落盘和摘要均由 call_api.run 完成。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    names = ("get_api_url", "get_api_key", "Request", "urlopen", "call_api", "_resolve_output_path")
    previous = {name: getattr(api, name) for name in names}
    previous_root = api._SESSION_CACHE.get("_root")
    captured = {}

    def request_with_token(*args, **kwargs):
        request = previous["Request"](*args, **kwargs)
        request.add_header("Token", token)
        return request

    def with_result(path, params):
        status, result = previous["call_api"](path, params)
        if isinstance(result, dict):
            # 保留外层 HTTP 状态，避免仅凭 body 或参数类错误误判认证成功。
            result["transportHttpStatus"] = status
            if url.rstrip("/").endswith("/temu/proxy"):
                raw = result.get("body")
                if isinstance(raw, str) and raw.strip():
                    try:
                        result["temuBody"] = json.loads(raw)
                    except json.JSONDecodeError:
                        pass
        captured["result"] = result
        return status, result

    api.get_api_url = lambda path: url
    api.get_api_key = lambda: token
    api.Request = request_with_token
    api.urlopen = lambda request, **kwargs: previous["urlopen"](request, timeout=timeout)
    api.call_api = with_result
    api._SESSION_CACHE["_root"] = str(root)
    output = StringIO()
    try:
        # 在任何网关请求之前确认实际会话 data 目录可写，不只检查根目录。
        out_path = api.resolve_data_path(SLUG, time.time())
        with tempfile.TemporaryFile(dir=Path(out_path).parent):
            pass
        api._resolve_output_path = lambda slug, ts: out_path
        argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        with redirect_stdout(output):
            api.run("/temu/fileDownload" if url.endswith("/temu/fileDownload") else "/temu/proxy", SLUG, argv=argv)
        result = captured["result"]
        _OUTPUTS[id(result)] = (result, output.getvalue())
        return result
    finally:
        for name, value in previous.items():
            setattr(api, name, value)
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


def take_output(result, *, inline=None):
    """业务 CLI 复用 run 的输出，不重复保存同一份响应。"""
    pending = _OUTPUTS.pop(id(result), None)
    if pending is None or pending[0] is not result:
        return None
    if inline is None:
        return pending[1]
    # emit_result 的 Python inline 参数也须有效，不能只依赖调用时的 sys.argv。
    # 复用公共摘要逻辑；完整响应已经由 run 保存，只重建最终展示。
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    output = StringIO()
    with redirect_stdout(output):
        print(pending[1].splitlines()[0])
        if inline or len(serialized.encode("utf-8")) <= api.SMALL_THRESHOLD:
            print(serialized)
        else:
            api.summarize(result)
    return output.getvalue()
