"""通过公共 run 执行 Temu 网关请求，支持双请求头鉴权与已解析响应。"""

import contextlib
import hashlib
import io
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import call_api as api


SLUG = "linkfox-temu-manage-product-global"


def run_gateway(url, body, key, timeout=150, inline=False):
    """返回 (原响应对象, 公共调用器输出)；不启用响应缓存或自行实现 HTTP。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 在请求前检查 cwd 可写，不允许公共调用器回退到授权范围以外的目录。
    with tempfile.TemporaryFile(dir=root):
        pass

    original_transport = api.call_api
    original_request = api.Request
    original_open = api.urlopen
    captured = {}

    def request_with_legacy_headers(*args, **kwargs):
        request = original_request(*args, **kwargs)
        request.add_header("Token", key)
        return request

    def delegate_timeout(request, timeout=150):
        # 由公共调用器发起请求，并传递辅助函数的 timeout 参数。
        return original_open(request, timeout=captured["timeout"])

    def with_temu_body(path, params):
        status, result = original_transport(path, params)
        if isinstance(result, dict) and isinstance(result.get("body"), str):
            try:
                result["temuBody"] = json.loads(result["body"])
            except json.JSONDecodeError:
                pass
        captured["result"] = result
        return status, result

    captured["timeout"] = timeout
    operation = str(body.get("type") or "file-download").replace("local.goods.", "").replace("local.", "").replace(".", "-")
    # 参数为固定业务 type 或用户自定义 type，均不可形成文件路径。
    operation = "".join(ch if ch.isascii() and (ch.isalnum() or ch in "-_") else "_" for ch in operation)
    if len(operation) > 40:
        operation = operation[:27] + "-" + hashlib.sha256(operation.encode()).hexdigest()[:12]
    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    output = io.StringIO()

    def output_path(slug, _ts):
        path = api.resolve_data_path(slug, time.time())
        captured["path"] = path
        return path

    old_root = api._SESSION_CACHE.get("_root")
    api._SESSION_CACHE["_root"] = str(root)
    try:
        with patch.object(api, "get_api_url", lambda _path: url), \
             patch.object(api, "get_api_key", lambda: key), \
             patch.object(api, "Request", request_with_legacy_headers), \
             patch.object(api, "urlopen", delegate_timeout), \
             patch.object(api, "call_api", with_temu_body), \
             patch.object(api, "_resolve_output_path", output_path), \
             contextlib.redirect_stdout(output):
            api.run("/temu/fileDownload" if url.endswith("/temu/fileDownload") else "/temu/proxy",
                    f"{SLUG}-{operation}", argv=argv)
            if not Path(captured["path"]).is_file():
                raise OSError("完整响应保存失败：" + captured["path"])
    finally:
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
    return captured["result"], output.getvalue()
