#!/usr/bin/env python3
"""通过公共调用器取上传凭证；仅向调用方内存返回密钥，落盘与展示脱敏。"""

import argparse
import contextlib
import io
import json
import os
import sys
import time
from unittest.mock import patch

import call_api

API_PATH = "/oss/getStsVoucherByAPI"
SLUG = "linkfox-aigc-imagegen-brand-gene-extract-upload-voucher"
SECRET_FIELDS = {"accessKeyId", "accessKeySecret", "securityToken"}
RETRY_STATUS = {408, 429, 500, 502, 503, 504}


def _redact(value):
    if isinstance(value, dict):
        return {k: "[已隐藏]" if k in SECRET_FIELDS else _redact(v)
                for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    return value


def _normal_code(code):
    if code is None or (isinstance(code, str) and not code.strip()):
        return True
    if isinstance(code, bool):
        return False
    try:
        return 200 <= float(code) <= 299
    except (TypeError, ValueError):
        return False


def _error_message(body):
    """保留网关可读错误原因，不把整份凭证或非 JSON 原文写入日志。"""
    if not isinstance(body, dict):
        return ""
    safe = _redact(body)
    for field in ("errmsg", "message", "error"):
        value = safe.get(field)
        if isinstance(value, str) and value.strip():
            return value[:300]
    return ""


def _invoke_once(inline=False):
    """在 run 的业务适配层记录 HTTP 状态，并在公共落盘前脱敏。

    URL、认证、POST 与 HTTP 错误解析全部由 call_api 执行。
    观察器只记录其已有 transport 的状态，不重新构造请求。
    """
    captured = {}
    transport = call_api.call_api
    opener = call_api.urlopen

    def observe(*args, **kwargs):
        try:
            response = opener(*args, **kwargs)
            captured["status"] = response.getcode()
            return response
        except Exception as exc:
            captured["status"] = getattr(exc, "code", None)
            raise

    def adapt(path, params):
        body = transport(path, params)
        captured["body"] = body
        # run 要求顶层为对象；异常类型在业务校验中报错，不在通用脚本崩溃。
        safe = _redact(body) if isinstance(body, dict) else {"error": "上传凭证响应格式异常"}
        safe["transportHttpStatus"] = captured.get("status")
        return safe

    output = io.StringIO()
    # run 即使收到 --no-cache 仍会调用 _cache_path 并创建 cwd/.cache。
    # 本接口不读写缓存，跳过该目录副作用，允许当前目录只读时回退到其他可写根目录。
    with patch.object(call_api, "urlopen", observe), \
            patch.object(call_api, "call_api", adapt), \
            patch.object(call_api, "_cache_path", return_value=""):
        with contextlib.redirect_stdout(output):
            argv = ["{}", "--no-cache"] + (["--inline"] if inline else [])
            call_api.run(API_PATH, SLUG, argv=argv)
    return captured.get("body"), captured.get("status"), output.getvalue()


def get_voucher(show_output=False, inline=False):
    if not (os.getenv("LINKFOX_AGENT_API_KEY") or os.getenv("LINKFOXAGENT_API_KEY")):
        raise RuntimeError("缺少环境变量 LINKFOX_AGENT_API_KEY 或 LINKFOXAGENT_API_KEY")
    last = RuntimeError("获取上传凭证失败")
    for attempt in range(3):
        if attempt:
            time.sleep(1 << (attempt - 1))
        try:
            body, status, output = _invoke_once(inline)
        except Exception:
            # 连接、JSON 等非 HTTP 异常最多尝试三次。
            last = RuntimeError("获取上传凭证失败：连接或响应解析异常")
            continue
        if show_output:
            print(output, end="")
        if status is not None and not 200 <= status <= 299:
            message = _error_message(body)
            last = RuntimeError(f"获取上传凭证失败：HTTP {status}" +
                                (f"：{message}" if message else ""))
            if status not in RETRY_STATUS:
                raise last
            continue
        if status is None and isinstance(body, dict) and body.get("error"):
            last = RuntimeError("获取上传凭证失败：连接或响应解析异常")
            continue
        break
    else:
        raise last

    if not isinstance(body, dict):
        raise RuntimeError("上传凭证响应格式异常")
    if not _normal_code(body.get("errcode")):
        raise RuntimeError(f"上传凭证业务错误：{body.get('errmsg') or body.get('message') or body.get('errcode')}")
    voucher = body.get("data") if "data" in body else body
    if not isinstance(voucher, dict):
        raise RuntimeError("上传凭证响应缺少有效 data")
    if "ErrorCode" in voucher:
        raise RuntimeError(f"上传凭证错误：{voucher['ErrorCode']} - {voucher.get('ErrorMessage', '')}")
    required = ("accessKeyId", "accessKeySecret", "securityToken", "endpoint", "bucketName")
    missing = [k for k in required if not voucher.get(k)]
    if missing:
        raise RuntimeError(f"上传凭证缺少字段：{missing}")
    for key in ("maxFileSize", "maxFileCount"):
        if isinstance(voucher.get(key), str) and voucher[key].strip().isdigit():
            voucher[key] = int(voucher[key].strip())
    return voucher


def main(argv=None):
    parser = argparse.ArgumentParser(description="获取上传凭证；仅展示和保存脱敏响应")
    parser.add_argument("params", nargs="?", default="{}", help="仅接受空 JSON 对象 {}")
    parser.add_argument("--inline", action="store_true", help="完整展示脱敏响应")
    parser.add_argument("--no-cache", action="store_true", help="兼容公共 CLI；始终禁用缓存")
    args = parser.parse_args(argv)
    try:
        if json.loads(args.params) != {}:
            raise ValueError("上传凭证接口只接受空 JSON 对象 {}")
        get_voucher(show_output=True, inline=args.inline)
        return 0
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
