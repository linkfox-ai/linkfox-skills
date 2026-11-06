"""通过公共调用器取得响应；业务脚本保留缓存、落盘与摘要策略。"""

import io
import json
import os
from contextlib import redirect_stdout
from urllib.error import HTTPError
from unittest.mock import patch

import call_api as transport


def is_normal_response(status, payload):
    """遵循接口公共响应规则；0 和 false 均不是空状态码。"""
    if status is None or not 200 <= status < 300:
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


def is_cacheable_result(status, payload):
    """缓存同时检查显式失败标记。"""
    if (not is_normal_response(status, payload) or not isinstance(payload, dict)
            or payload.get("error") or payload.get("success") is False):
        return False
    # 辅助状态字段用于缓存校验，不替代公共 HTTP/errcode 判断。
    return all(key not in payload or str(payload[key]).lower() in ("0", "200", "ok", "success")
               for key in ("errorCode", "code"))


def request_json(api_path, params):
    """仅供串行 CLI 使用：禁用公共缓存，并将中间输出送至空设备。

    预签名凭证只能留在内存中。公共调用器不生成第二份数据或缓存；
    普通商品响应由商品业务入口保存。所有临时替换在返回或异常时恢复。
    """
    captured = {}
    send = transport.call_api
    opener = transport.urlopen

    def tolerant_http_errors(*args, **kwargs):
        """按既有错误处理约定替换非法字符，保留真实 HTTP 状态及错误正文。"""
        try:
            return opener(*args, **kwargs)
        except HTTPError as exc:
            body = exc.read() if exc.fp else b""
            exc.close()
            body = body.decode("utf-8", errors="replace").encode("utf-8")
            raise HTTPError(exc.url, exc.code, exc.reason, exc.headers, io.BytesIO(body)) from exc

    def capture(path, body):
        try:
            status, payload = send(path, body)
        except json.JSONDecodeError as exc:
            status, payload = None, {"error": "Invalid JSON response", "details": exc.doc[:500]}
        except TimeoutError:
            status, payload = None, {"error": "Connection timed out"}
        captured.update(status=status, payload=payload)
        # 公共 CLI 要求对象；仍向业务脚本返回未经改写的原始响应。
        printable = dict(payload) if isinstance(payload, dict) else {"body": payload}
        printable.pop("_cache", None)
        return status, printable

    with patch.object(transport, "call_api", capture), \
            patch.object(transport, "urlopen", tolerant_http_errors), \
            patch.object(transport, "_cache_path", lambda *args: os.devnull), \
            patch.object(transport, "_resolve_output_path", lambda *args: os.devnull), \
            patch.dict(os.environ, {"SESSION_ID": (os.environ.get("SESSION_ID") or "").strip()}), \
            redirect_stdout(io.StringIO()):
        transport.run(api_path, "linkfox-chuhaijiang-tiktok-product",
                      [json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"])
    return captured["status"], captured["payload"]
