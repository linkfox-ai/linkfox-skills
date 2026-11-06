#!/usr/bin/env python3
"""处理 Temu 双请求头、认证与输出约定，传输统一交给公共调用器。"""

from contextlib import contextmanager, redirect_stdout
import io
import json
import os
from pathlib import Path
import threading
import time

import call_api

SLUG = "linkfox-temu-promotion-us"
_LOCK = threading.RLock()
_PENDING_OUTPUT = None


@contextmanager
def _override(**attrs):
    """仅在当前串行 CLI 调用中临时适配，退出时恢复公共模块。"""
    original = {name: getattr(call_api, name) for name in attrs}
    try:
        for name, value in attrs.items():
            setattr(call_api, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(call_api, name, value)


def _cwd_root():
    root = (Path.cwd() / "linkfox").resolve()
    if root == Path('/tmp') or Path('/tmp') in root.parents:
        raise OSError("响应必须保存到可写的工作目录，禁止写入 /tmp")
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


def _prepare_output():
    """先验证实际会话目录可写，失败发生在任何网络请求之前。"""
    sid = call_api._session_id(time.time())
    if not sid or sid in (".", "..") or "/" in sid or "\\" in sid or Path(sid).drive:
        raise ValueError("SESSION_ID 必须是非空的单级目录名，不能包含路径或盘符")
    with _override(_linkfox_root=_cwd_root, _session_id=lambda ts: sid):
        output = call_api.resolve_data_path(SLUG, time.time())
    with open(output, "x", encoding="utf-8"):
        pass
    return output


def invoke(url, body, key, timeout=150):
    """通过公共调用器 run 发送一次请求。"""
    global _PENDING_OUTPUT
    for api_path in ("/temu/proxy", "/temu/fileDownload"):
        if url.endswith(api_path):
            base = url[:-len(api_path)]
            break
    else:
        raise ValueError("不支持的 Temu 网关路径")

    with _LOCK:
        _PENDING_OUTPUT = None
        output = _prepare_output()
        original_open = call_api.urlopen
        original_call = call_api.call_api
        captured = {}
        response_status = None

        def compatible_open(request, timeout=150):
            # 设置 Temu Token 请求头和 timeout，HTTP 及错误处理由 call_api.py 完成。
            nonlocal response_status
            request.add_header("Token", key)
            response = original_open(request, timeout=invoke_timeout)
            response_status = response.status
            return response

        def capture_call(path, params):
            try:
                status, result = original_call(path, params)
            except json.JSONDecodeError as exc:
                # 公共调用器无法解析成功状态下的非 JSON；保留原文，避免响应丢失。
                status = response_status
                result = {"error": "网关响应不是有效 JSON", "details": exc.doc}
            if not isinstance(result, dict):
                result = {"rawResponse": result}
            result["transportHttpStatus"] = status
            captured["result"] = result
            return status, result

        invoke_timeout = timeout
        try:
            with _override(
                get_api_base=lambda: base,
                get_api_key=lambda: key,
                urlopen=compatible_open,
                call_api=capture_call,
                _linkfox_root=_cwd_root,
                _resolve_output_path=lambda slug, ts: output,
            ), redirect_stdout(io.StringIO()):
                call_api.run(api_path, SLUG, argv=[json.dumps(body, ensure_ascii=False), "--no-cache"])
            result = captured["result"]
            _PENDING_OUTPUT = (result, output)
            return result
        except BaseException:
            # 请求若已返回，公共 run 保存的原始数据应保留。
            if not captured and os.path.exists(output) and os.path.getsize(output) == 0:
                os.remove(output)
            raise


def emit_result(result, slug=SLUG, inline=False):
    """解析后的响应更新同一文件，只输出一次，不建立第二层响应缓存。"""
    global _PENDING_OUTPUT
    with _LOCK:
        if _PENDING_OUTPUT is not None and _PENDING_OUTPUT[0] is result:
            output = _PENDING_OUTPUT[1]
        else:
            output = _prepare_output()
        _PENDING_OUTPUT = None
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        # 写失败直接报错，不隐藏为成功，也不回退到其他目录。
        Path(output).write_text(serialized, encoding="utf-8")
        print(f"Saved full response: {output} ({len(serialized.encode('utf-8'))} bytes)")
        if inline or len(serialized.encode("utf-8")) <= call_api.SMALL_THRESHOLD:
            print(serialized)
        else:
            call_api.summarize(result)
