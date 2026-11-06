"""复杂报告工作流与公共调用器的兼容层；不自行实现 HTTP 或缓存。"""

import io
import json
import time
from contextlib import redirect_stdout
from unittest.mock import patch

import call_api as shared_api
from reporting_v1_workflow import WorkflowError, _redact_presigned_urls


def _record_payload(node):
    """解析代理 body 字符串后脱敏，原始下载地址仅保留在内存。"""
    if isinstance(node, dict):
        result = {}
        for key, value in node.items():
            if key == "body" and isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            result[key] = _record_payload(value)
        return _redact_presigned_urls(result)
    if isinstance(node, list):
        return [_record_payload(value) for value in node]
    if isinstance(node, str) and node.lower().startswith(("http://", "https://")):
        return "[redacted]"
    return node


def _normal_errcode(value):
    if value is None:
        return True
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return True
        if len(value) != 3 or not value.isascii() or not value.isdigit():
            return False
        value = int(value)
    return type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0


def invoke_proxy(params, resolve_data_path, slug):
    """由 run 执行传输和脱敏落盘，成功结果缓存仅由业务层管理。

    两个 CLI 入口均为串行工作流。临时替换仅影响本次 run，并在异常时恢复。
    """
    record_path = resolve_data_path(slug + "-proxy", time.time())
    original_transport = shared_api.call_api
    captured = []

    def capture(api_path, payload):
        http_status, response = original_transport(api_path, payload)
        captured.append((http_status, response))
        safe = _record_payload(response)
        # 公共 CLI 的落盘后输出路径要求对象，原始类型留给工作流做业务检查。
        return http_status, safe if isinstance(safe, dict) else {"response": safe}

    with patch.object(shared_api, "call_api", capture), \
            patch.object(shared_api, "_resolve_output_path", lambda *_: record_path), \
            redirect_stdout(io.StringIO()):
        shared_api.run(
            "/amazonAds/developerProxy", slug + "-proxy",
            [json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"],
        )

    if len(captured) != 1:
        raise WorkflowError("公共调用器未执行唯一一次网关请求")
    http_status, response = captured[0]
    if type(http_status) is not int or not 200 <= http_status < 300:
        raise WorkflowError(
            "LinkFox 网关请求失败",
            {"gatewayHttpStatus": http_status, "response": _record_payload(response)},
        )
    if isinstance(response, dict) and not _normal_errcode(response.get("errcode")):
        raise WorkflowError(
            "LinkFox 网关业务错误",
            {"gatewayHttpStatus": http_status, "response": _record_payload(response)},
        )
    return response
