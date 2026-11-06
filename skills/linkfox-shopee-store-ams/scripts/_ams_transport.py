"""通过公共调用器执行请求，保留外层状态并兼容网关地址环境变量。"""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import io
import json
import sys
import threading
import time

import call_api as public_api

_LOCK = threading.RLock()
SLUG = "linkfox-shopee-store-ams"


class GatewayResponse(dict):
    """保持字典返回协议，同时记录与上游状态不同的 LinkFox HTTP 状态。"""

    def __init__(self, payload, http_status):
        super().__init__(payload)
        self.transport_http_status = http_status


def invoke(endpoint: str, params: dict, base_url: str, output_root: str) -> dict:
    """run 不返回响应；在业务适配层捕获其 transport 结果，不实现 HTTP。"""
    prefix = base_url.rstrip("/")
    if endpoint not in (prefix + "/shopee/developerProxy", prefix + "/shopee/storeTokens"):
        raise ValueError("不支持的 Shopee 网关端点")
    path = endpoint[len(prefix):]
    operation = params.get("path", "storeTokens").rsplit("/", 1)[-1]
    captured = {}
    output = io.StringIO()
    errors = io.StringIO()
    # 公共调用器不可修改。短暂适配其基址和会话根目录，并保证异常后恢复。
    # 锁保证同进程多个业务调用不会互相覆盖适配状态。
    with _LOCK:
        original_call = public_api.call_api
        original_base = public_api.get_api_base
        original_output_path = public_api._resolve_output_path
        old_root = public_api._SESSION_CACHE.get("_root")

        def capture(api_path, request_params):
            status, payload = original_call(api_path, request_params)
            if not isinstance(payload, dict):
                payload = {"error": "网关响应不是 JSON 对象", "body": payload}
            captured.update(status=status, payload=payload)
            return status, payload

        public_api.call_api = capture
        public_api.get_api_base = lambda: prefix
        # 公共 run 的时间戳只精确到秒；业务层使用微秒文件名，防止同秒覆盖。
        # slug 不附加纳秒时间，避免长操作名在 Windows 下超过路径上限。
        public_api._resolve_output_path = lambda slug, ts: public_api.resolve_data_path(slug, time.time())
        public_api._SESSION_CACHE["_root"] = output_root
        try:
            # 在请求前建好实际会话目录，确保深层 data 目录也可写。
            from pathlib import Path
            _, session_dir = public_api._ensure_session(time.time())
            data_dir = Path(session_dir) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            probe = data_dir / f".write_probe-{time.time_ns()}"
            try:
                with probe.open("x", encoding="utf-8"):
                    pass
            finally:
                if probe.exists():
                    probe.unlink()
            try:
                with redirect_stdout(output), redirect_stderr(errors):
                    public_api.run(
                        path,
                        f"{SLUG}-{operation}-raw",
                        argv=[json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"],
                    )
            finally:
                # 包括缺密钥等 SystemExit 路径，也必须保留公共调用器的诊断。
                sys.stderr.write(errors.getvalue())
        finally:
            public_api.call_api = original_call
            public_api.get_api_base = original_base
            public_api._resolve_output_path = original_output_path
            if old_root is None:
                public_api._SESSION_CACHE.pop("_root", None)
            else:
                public_api._SESSION_CACHE["_root"] = old_root
    # 原始响应已由公共调用器落盘；只展示其保存位置，业务结果由 CLI 入口统一输出。
    for line in (output.getvalue() + errors.getvalue()).splitlines():
        if line.startswith("Saved full response:"):
            print(line, file=sys.stderr)
        elif line.startswith("Failed to save to"):
            raise OSError(f"{line}；已发起请求，本地保存失败不代表上游未执行，请先核对店铺实际状态，勿自动重复提交。")
    if "payload" not in captured:
        raise RuntimeError("公共调用器未返回传输结果")
    return GatewayResponse(captured["payload"], captured["status"])
