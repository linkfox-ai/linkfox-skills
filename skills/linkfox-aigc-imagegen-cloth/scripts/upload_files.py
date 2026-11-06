#!/usr/bin/env python3
"""本地素材上传：公共 run 获取凭证，oss2 上传；保留批内复用与部分失败输出。"""

import contextlib
import io
import json
import os
import re
import secrets
import sys
import time

import call_api as api

CONTENT_TYPES = {
    "md": "text/markdown; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
    "csv": "text/csv; charset=utf-8",
    "json": "application/json; charset=utf-8",
    "html": "text/html; charset=utf-8",
    "webp": "image/webp",
}

API_PATH = "/oss/getStsVoucherByAPI"
SLUG = "linkfox-aigc-imagegen-cloth-upload-voucher"
RETRY_HTTP = {408, 429, 500, 502, 503, 504}


class VoucherRequestError(RuntimeError):
    """携带上传凭证请求的有界重试标记。"""

    def __init__(self, message, *, retryable=False):
        super().__init__(message)
        self.retryable = retryable


def _request_voucher():
    """HTTP、保存与输出交给公共 run；捕获输出以免泄露 STS。

    观察公共 transport 的 HTTP 状态，不另建 Request、不自行实现 HTTP。
    兼容适配仅在本次顺序调用期间生效，finally 恢复所有公共模块属性。
    """
    if not (os.getenv("LINKFOX_AGENT_API_KEY") or os.getenv("LINKFOXAGENT_API_KEY")):
        raise VoucherRequestError("缺少环境变量 LINKFOX_AGENT_API_KEY 或 LINKFOXAGENT_API_KEY")
    transport, opener = api.call_api, api.urlopen
    output_path = api._resolve_output_path
    observed = {"http_status": None, "body": None, "transport_error": None}

    def observe_open(*args, **kwargs):
        try:
            response = opener(*args, **kwargs)
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            observed["http_status"] = status
            return response
        except api.HTTPError as error:
            observed["http_status"] = error.code
            raise
        except Exception as error:
            observed["transport_error"] = error
            raise

    def capture_result(path, params):
        body = transport(path, params)
        observed["body"] = body
        # 公共 run 的输出要求 object；异常响应仍交由业务层判失败。
        return body if isinstance(body, dict) else {"error": "上传凭证响应格式异常"}

    api.call_api = capture_result
    api.urlopen = observe_open
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        # 上传凭证请求不使用响应缓存；批内复用 voucher 不等于落盘响应缓存。
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            api.run(API_PATH, SLUG, argv=["{}", "--inline", "--no-cache"])
    except (api.HTTPError, api.URLError, OSError, ValueError) as error:
        status = observed["http_status"]
        retryable = status is None or 200 <= status <= 299 or status in RETRY_HTTP
        raise VoucherRequestError(f"获取上传凭证失败：{error}", retryable=retryable) from error
    finally:
        api.call_api, api.urlopen = transport, opener
        api._resolve_output_path = output_path
    status = observed["http_status"]
    body = observed["body"]
    if status is not None and not 200 <= status <= 299:
        raise VoucherRequestError(f"获取上传凭证失败：HTTP {status}", retryable=status in RETRY_HTTP)
    if observed["transport_error"] is not None:
        raise VoucherRequestError(f"获取上传凭证失败：{observed['transport_error']}", retryable=True)
    if not isinstance(body, dict):
        raise VoucherRequestError("上传凭证响应格式异常")
    if body.get("error"):
        message = str(body["error"])
        match = re.search(r"HTTP (\d{3})", message)
        retryable = bool(match and int(match.group(1)) in RETRY_HTTP) or message.startswith("Connection failed:")
        raise VoucherRequestError(f"获取上传凭证失败：{message}", retryable=retryable)
    return body


def _normal_errcode(code):
    if code is None or (isinstance(code, str) and not code.strip()):
        return True
    if isinstance(code, bool):
        return False
    try:
        return 200 <= float(code) <= 299
    except (TypeError, ValueError, OverflowError):
        return False


def get_voucher():
    last = None
    for attempt in range(3):
        if attempt:
            time.sleep(1 << (attempt - 1))
        try:
            body = _request_voucher()
            break
        except VoucherRequestError as error:
            last = error
            if not error.retryable:
                raise
    else:
        raise last
    if not _normal_errcode(body.get("errcode")):
        raise RuntimeError(f"上传凭证业务错误：{body.get('errmsg') or body.get('message')}")
    voucher = body.get("data") if "data" in body else body
    if not isinstance(voucher, dict):
        raise RuntimeError("上传凭证响应缺少有效 data")
    if "ErrorCode" in voucher:
        raise RuntimeError(f"上传凭证错误：{voucher['ErrorCode']} - {voucher.get('ErrorMessage', '')}")
    required = ("accessKeyId", "accessKeySecret", "securityToken", "endpoint", "bucketName")
    missing = [key for key in required if not voucher.get(key)]
    if missing:
        raise RuntimeError(f"上传凭证缺少字段：{missing}")
    for key in ("maxFileSize", "maxFileCount"):
        if isinstance(voucher.get(key), str) and voucher[key].strip().isdigit():
            voucher[key] = int(voucher[key].strip())
    return voucher


def session_dir(ts):
    # 与公共 run 使用同一会话；不另建第二层响应缓存。
    _, path = api._ensure_session(ts)
    return path


def register(url, slug, ts):
    path = os.path.join(session_dir(ts), "_meta.json")
    try:
        with open(path, encoding="utf-8") as f: meta = json.load(f)
    except (OSError, ValueError):
        return
    if slug not in meta.setdefault("skills_called", []): meta["skills_called"].append(slug)
    if url not in meta.setdefault("deliverables", []): meta["deliverables"].append(url)
    meta["last_used_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))
    with open(path, "w", encoding="utf-8") as f: json.dump(meta, f, ensure_ascii=False, indent=2)


def upload(local_path, voucher):
    try:
        import oss2
    except ImportError:
        raise RuntimeError("缺少 oss2 依赖；请由用户或环境管理员安装：python -m pip install oss2")
    ts = time.time(); size = os.path.getsize(local_path)
    name = os.path.basename(local_path); ext = os.path.splitext(name)[1].lstrip(".").lower() or "bin"
    maximum = voucher.get("maxFileSize")
    if isinstance(maximum, int) and maximum > 0 and size > maximum:
        raise RuntimeError(f"文件大小 {size} 字节超过上限 {maximum} 字节")
    supported = voucher.get("supportedTypes")
    if isinstance(supported, str) and supported.strip():
        allowed = {x.strip().lower() for x in supported.split(",") if x.strip()}
        if allowed and ext not in allowed:
            raise RuntimeError(f"文件类型 .{ext} 不在允许列表中：{sorted(allowed)}")
    endpoint = str(voucher["endpoint"]).rstrip("/")
    endpoint_url = endpoint if endpoint.startswith(("http://", "https://")) else "https://" + endpoint
    endpoint_host = endpoint_url.split("://", 1)[1]
    object_key = f"{str(voucher.get('dir') or 'tmp').rstrip('/')}/{time.strftime('%Y/%m', time.localtime(ts))}/{secrets.token_hex(16)}.{ext}"
    auth = oss2.StsAuth(voucher["accessKeyId"], voucher["accessKeySecret"], voucher["securityToken"])
    bucket = oss2.Bucket(auth, endpoint_url, voucher["bucketName"])
    headers = {"Content-Type": CONTENT_TYPES[ext]} if ext in CONTENT_TYPES else None
    with open(local_path, "rb") as f: bucket.put_object(object_key, f, headers=headers)
    url = f"https://{voucher['bucketName']}.{endpoint_host}/{object_key}"
    register(url, os.path.splitext(name)[0], ts)
    return {"url": url, "path": object_key, "name": name, "size": size, "ext": ext, "localPath": os.path.abspath(local_path)}


def main(paths):
    if not paths:
        print("用法：upload_files.py <文件路径> [<文件路径> ...]", file=sys.stderr); return 1
    results, voucher, failed = [], None, False
    batch_limit, upload_attempts = None, 0
    for path in paths:
        if not os.path.isfile(path):
            results.append({"error": True, "input": path, "message": "文件不存在"}); failed = True; continue
        if batch_limit is not None and upload_attempts >= batch_limit:
            results.append({"error": True, "input": path, "message": f"单次最多上传 {batch_limit} 个文件"}); failed = True; continue
        try:
            if voucher is None: voucher = get_voucher()
            if batch_limit is None and isinstance(voucher.get("maxFileCount"), int) and voucher["maxFileCount"] > 0:
                batch_limit = voucher["maxFileCount"]
            if batch_limit is not None and upload_attempts >= batch_limit:
                results.append({"error": True, "input": path, "message": f"单次最多上传 {batch_limit} 个文件"}); failed = True; continue
            upload_attempts += 1
            results.append(upload(path, voucher))
        except Exception as e:
            results.append({"error": True, "input": path, "message": str(e)}); voucher = None; failed = True
    print(json.dumps(results, ensure_ascii=False, indent=2))
    for r in results:
        if not r.get("error"):
            print(f"Saved full response: {r['url']} ({r['size']} bytes)")
            print(f"Uploaded {r['localPath']} -> {r['url']}")
    return int(failed)


def cli(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--help"] or args == ["-h"]:
        print('用法：upload_files.py <文件路径> [<文件路径> ...]')
        print('或：upload_files.py \'{"files":["<文件路径>"]}\' [--inline] [--no-cache]')
        print('凭证请求始终不缓存；输出保持完整上传结果。上传前由调用方确认文件可以公开。')
        return 0
    args = [item for item in args if item not in ("--inline", "--no-cache")]
    if len(args) == 1 and args[0].lstrip().startswith("{"):
        try:
            payload = json.loads(args[0])
            paths = payload.get("files")
            if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p for p in paths):
                raise ValueError("files 必须是非空文件路径字符串数组")
        except (json.JSONDecodeError, ValueError) as error:
            print(f"参数错误：{error}", file=sys.stderr)
            return 1
    else:
        paths = args
    return main(paths)


if __name__ == "__main__":
    raise SystemExit(cli())
