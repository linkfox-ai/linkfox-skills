import json, os, secrets, sys, time
from _aigc_api import call_api as _shared_call_api, request_json

CONTENT_TYPES = {
    "md": "text/markdown; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
    "csv": "text/csv; charset=utf-8",
    "json": "application/json; charset=utf-8",
    "html": "text/html; charset=utf-8",
    "webp": "image/webp",
}

def get_voucher():
    key = os.getenv("LINKFOX_AGENT_API_KEY") or os.getenv("LINKFOXAGENT_API_KEY")
    if not key:
        raise RuntimeError("缺少环境变量 LINKFOX_AGENT_API_KEY 或 LINKFOXAGENT_API_KEY")
    last = None
    for attempt in range(3):
        if attempt:
            time.sleep(1 << (attempt - 1))
        status, body = request_json("/oss/getStsVoucherByAPI", {}, "linkfox-aigc-imagegen-upload-voucher", timeout=30, private=True)
        if isinstance(body, dict) and not body.get("error"):
            break
        last = RuntimeError(f"获取上传凭证失败：HTTP {status}: {body.get('error') if isinstance(body, dict) else '响应格式异常'}")
        retryable_error = isinstance(body, dict) and body.get("errorCode") in ("CONNECTION_ERROR", "REQUEST_TIMEOUT", "HTTP_READ_ERROR", "EMPTY_RESPONSE", "INVALID_ENCODING", "INVALID_JSON_RESPONSE")
        # HTTP 错误先按状态判断，401/402 即使空体、非 JSON 或读取失败也不重试。
        if status is not None and not 200 <= status < 300:
            retryable = status in (408, 429, 500, 502, 503, 504)
        else:
            retryable = retryable_error
        if not retryable:
            raise last
    else:
        raise last
    if not isinstance(body, dict):
        raise RuntimeError("上传凭证响应格式异常")
    v = body.get("data") if "data" in body else body
    if not isinstance(v, dict):
        raise RuntimeError("上传凭证响应缺少有效 data")
    if "ErrorCode" in v:
        raise RuntimeError(f"上传凭证错误：{v['ErrorCode']} - {v.get('ErrorMessage', '')}")
    required = ("accessKeyId", "accessKeySecret", "securityToken", "endpoint", "bucketName")
    missing = [k for k in required if not v.get(k)]
    if missing:
        raise RuntimeError(f"上传凭证缺少字段：{missing}")
    for k in ("maxFileSize", "maxFileCount"):
        if isinstance(v.get(k), str) and v[k].strip().isdigit():
            v[k] = int(v[k].strip())
    return v


def session_dir(ts):
    return _shared_call_api._ensure_session(ts)[1]


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
        print("Usage: upload <local_path> [<local_path> ...]", file=sys.stderr); return 1
    results, voucher, failed = [], None, False
    batch_limit, upload_attempts = None, 0
    for path in paths:
        if not os.path.isfile(path):
            results.append({"error": True, "input": path, "message": "文件不存在"}); failed = True; continue
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


if __name__ == "__main__":
    if "--help" in sys.argv[1:]:
        print("Usage: upload_file.py <local_path> [<local_path> ...]")
    else:
        raise SystemExit(main(sys.argv[1:]))
