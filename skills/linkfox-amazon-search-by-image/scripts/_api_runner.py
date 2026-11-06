"""业务 CLI 对公共 run 的响应适配，不实现 HTTP transport 或第二层缓存。

公共 run 不返回响应，故在单线程 CLI 调用期间临时接入响应状态与输出路径，
读取其已保存的 JSON。所有接入点都在 finally 中恢复，不修改公共调用器文件。
"""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path

import call_api


def run_response(api_path, slug, params, output_path):
    """返回 (HTTP 状态, 响应体)，保留业务 CLI 自己的输出及缓存行为。"""
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # 在发送请求前确认业务输出目录可写，不使用公共调用器的回退目录。
    with target.open("a", encoding="utf-8"):
        pass
    previous_path = call_api._resolve_output_path
    previous_call = call_api.call_api
    status = None
    payload = None

    def capture(api_path, params):
        nonlocal status, payload
        status, payload = previous_call(api_path, params)
        # 公共 run 的输出阶段要求对象。异常 JSON 仅在内部临时包裹，
        # 完成后恢复原始响应，让业务入口判断结构，不改变基础响应码规则。
        return status, payload if isinstance(payload, dict) else {"_raw_response": payload}

    try:
        call_api._resolve_output_path = lambda *_: str(target)
        call_api.call_api = capture
        with redirect_stdout(StringIO()):
            call_api.run(api_path, slug, [json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"])
        if not isinstance(payload, dict):
            target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return status, payload
        saved = json.loads(target.read_text(encoding="utf-8"))
        if saved != payload:
            raise OSError(f"完整响应未能保存，拒绝复用已有文件: {target}")
        return status, saved
    finally:
        call_api._resolve_output_path = previous_path
        call_api.call_api = previous_call


def is_normal_response(status, payload):
    """匹配接口文档公共规则；0、false 不作为空值。"""
    if type(status) is not int or not 200 <= status < 300:
        return False
    code = payload.get("errcode") if isinstance(payload, dict) else None
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
