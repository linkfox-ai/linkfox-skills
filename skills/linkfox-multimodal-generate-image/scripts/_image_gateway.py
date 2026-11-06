"""图片业务适配：统一调用、复用业务缓存、限定落盘位置。"""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import time

import call_api as gateway


def run(api_path, slug, params, *, inline=False, cached=None,
        on_response=None, quiet=False):
    """经公共 run 调用；返回 HTTP 状态与原始响应，不增加第二层缓存。

    公共 run 不返回业务对象，通过同步调用期间的 transport 包装取得原始
    响应；finally 恢复 transport。缓存命中仍交给公共 run 落盘和展示。
    """
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 不允许公共脚本因目录不可写而回退到家目录或临时目录。
    with tempfile.TemporaryFile(dir=root):
        pass
    gateway._SESSION_CACHE["_root"] = str(root.resolve())
    output = Path(gateway._resolve_output_path(slug, int(time.time())))
    with tempfile.TemporaryFile(dir=output.parent):
        pass
    # 临时短文件名可写不代表实际响应文件名可写（如 Windows 路径长度限制）。
    try:
        with output.open("x", encoding="utf-8"):
            pass
    except FileExistsError:
        pass
    else:
        output.unlink()

    original = gateway.call_api
    response = []

    def transport(path, body):
        if cached is not None:
            # 旧业务缓存没有 HTTP 状态，不能将其伪装成本次 HTTP 200。
            status = cached.get("_http_status")
            if type(status) is not int:
                status = None
            result = dict(cached, _http_status=status)
        else:
            status, result = original(path, body)
            if isinstance(result, dict):
                result = dict(result, _http_status=status)
            if on_response is not None:
                on_response(result)
        if not quiet and (status is None or not 200 <= status < 300):
            source = "Cached HTTP status" if cached is not None else "HTTP status"
            print(f"{source}: {status if status is not None else 'unknown'}", file=sys.stderr)
        response[:] = [status, result]
        return status, result

    argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    gateway.call_api = transport
    try:
        if quiet:
            with redirect_stdout(io.StringIO()):
                gateway.run(api_path, slug, argv=argv)
        else:
            gateway.run(api_path, slug, argv=argv)
    finally:
        gateway.call_api = original
    return tuple(response)
