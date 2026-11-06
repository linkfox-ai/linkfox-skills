"""业务封装：复用公共调用器，限定落盘目录并保留上传 CLI 输出。"""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import time

import call_api as api


def run_request(api_path, slug, params, *, transport=None, inline=False, quiet=False):
    """执行一次公共 run，返回捕获的 HTTP 状态和响应；不启用公共缓存。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    previous_transport = api.call_api
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output = api._resolve_output_path
    operation = transport or previous_transport
    captured = []

    def capture(path, request_params):
        status, body = operation(path, request_params)
        if not isinstance(body, dict):
            body = {"error": "接口响应不是 JSON 对象", "details": body}
        body = dict(body)
        body["_http_status"] = status
        captured[:] = [status, body]
        return status, body

    api.call_api = capture
    api._SESSION_CACHE["_root"] = str(root)
    try:
        # 请求前检查实际会话和数据文件，避免根目录可写但 data 不可写时仍扣费。
        # 文件名使用微秒时间戳；独占创建避免同名时覆盖已有响应。
        output_path = Path(api.resolve_data_path(slug, time.time()))
        output_path.touch(exist_ok=False)
        api._resolve_output_path = lambda _name, _ts: str(output_path)
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            argv.append("--inline")
        output = io.StringIO()
        with redirect_stdout(output):
            api.run(api_path, slug, argv=argv)
        # 公共 run 会捕获写入异常；在业务层确认完整落盘，上传才可继续。
        try:
            saved = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise OSError(f"完整响应未成功保存到 {output_path}: {exc}") from exc
        if not captured or saved != captured[1]:
            raise OSError(f"保存的完整响应与本次结果不一致: {output_path}")
        if not quiet:
            if not inline and len(json.dumps(saved, ensure_ascii=False, indent=2).encode("utf-8")) > api.SMALL_THRESHOLD:
                status = captured[0] if captured[0] is not None else "unknown"
                print(f"HTTP status: {status}")
            print(output.getvalue(), end="")
        return tuple(captured)
    finally:
        api.call_api = previous_transport
        api._resolve_output_path = previous_output
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


def is_normal_response(http_status, payload):
    """预签名业务按公共规则判断 HTTP 与 errcode，排除 0 和 false。"""
    if http_status is None or not 200 <= http_status < 300:
        return False
    if not isinstance(payload, dict):
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
