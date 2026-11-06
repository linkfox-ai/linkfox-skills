"""通过公共 run 发起请求；业务入口负责缓存、摘要和会话落盘。"""

import contextlib
import io
import json
import os
from unittest.mock import patch

import call_api as api


def request(api_path, slug, params):
    """返回 HTTP 状态与原始响应，不添加缓存字段，也不重复落盘。"""
    transport = api.call_api
    captured = {}

    def capture(path, body):
        try:
            status, payload = transport(path, body)
        except json.JSONDecodeError as exc:
            status, payload = None, {"error": "Invalid JSON response", "details": exc.doc[:500]}
        except UnicodeDecodeError as exc:
            # 公共调用器严格解码；HTTP 错误体包含无效 UTF-8 时使用替换解码。
            # 使用已读取的字节和异常上下文，不重发请求、不另建 HTTP transport。
            error = exc.__context__
            raw = exc.object.decode("utf-8", errors="replace")
            if isinstance(error, api.HTTPError):
                status = error.code
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    payload = {"error": f"HTTP {status}: {error.reason}", "details": raw[:500]}
            else:
                status, payload = None, {"error": "Invalid response encoding", "details": raw[:500]}
        except TimeoutError:
            status, payload = None, {"error": "Connection timed out"}
        if isinstance(payload, dict) and isinstance(payload.get("error"), str) \
                and payload["error"].startswith(f"HTTP {status}:") \
                and isinstance(payload.get("details"), str):
            payload = {**payload, "details": payload["details"][:500]}
        captured.update(status=status, payload=payload)
        # run 的输出逻辑要求对象；对非对象仍向入口返回原始响应。
        return status, payload if isinstance(payload, dict) else {}

    # 业务入口负责缓存与业务摘要；关闭 run 的缓存和中间文件输出。
    # 上下文退出后恢复公共模块，避免影响同进程后续调用。
    with patch.object(api, "call_api", capture), \
         patch.object(api, "_cache_path", return_value=None), \
         patch.object(api, "_resolve_output_path", return_value=os.devnull), \
         patch.dict(os.environ, {"SESSION_ID": (os.environ.get("SESSION_ID") or "").strip()}), \
         contextlib.redirect_stdout(io.StringIO()):
        api.run(api_path, slug, argv=[json.dumps(params, ensure_ascii=False), "--no-cache", "--inline"])
    return captured["status"], captured["payload"]


def normal_response(status, payload):
    """响应基础规则：HTTP 与 errcode 均正常，0/false 不视为空。"""
    if status is None or not 200 <= status < 300 or not isinstance(payload, dict):
        return False
    code = payload.get("errcode")
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        if not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0
