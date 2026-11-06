"""业务调用封装：通过公共 run 调用，固定工作目录并取回原始响应。"""

from contextlib import nullcontext, redirect_stdout
import json
from pathlib import Path
import time

import call_api as api


def run_request(api_path, slug, params, *, inline=False, transport=None, output=None):
    """不启用公共缓存；业务可提供缓存适配，返回 (HTTP 状态, 响应)。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    original_transport = api.call_api
    original_root = api._SESSION_CACHE.get("_root")
    original_output = api._resolve_output_path
    result = []
    request = transport or original_transport

    def capture(path, body):
        status, payload = request(path, body)
        result[:] = [status, payload]
        return status, payload

    argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    try:
        api.call_api = capture
        api._SESSION_CACHE["_root"] = str(root)
        # 请求前检查完整目标路径，覆盖目录可写但文件名过长等情况。
        # 使用微秒保留同秒内的每次响应；不使用公共调用器的回退目录。
        output_path = Path(api.resolve_data_path(slug, time.time()))
        with output_path.open("x", encoding="utf-8"):
            pass
        output_path.unlink()
        api._resolve_output_path = lambda _slug, _ts: str(output_path)
        with redirect_stdout(output) if output is not None else nullcontext():
            api.run(api_path, slug, argv=argv)
        # 公共 run 会捕获写文件错误；业务封装必须向 CLI 传播保存失败。
        expected = json.dumps(result[1], ensure_ascii=False, indent=2)
        try:
            saved = output_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise OSError(f"完整响应未保存：{output_path}") from exc
        if saved != expected:
            raise OSError(f"完整响应未保存：{output_path}")
        return tuple(result)
    finally:
        api.call_api = original_transport
        api._resolve_output_path = original_output
        if original_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = original_root


def is_normal_response(status, payload):
    """按接口公共规则判断 2xx 与 errcode，明确排除 0 和 false。"""
    if status is None or not 200 <= status < 300 or not isinstance(payload, dict):
        return False
    code = payload.get("errcode")
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
