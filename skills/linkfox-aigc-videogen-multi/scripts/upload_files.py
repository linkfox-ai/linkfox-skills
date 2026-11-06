import json, os, secrets, sys, tempfile, time
from urllib.error import HTTPError
from _linkfox_transport import request_json

CONTENT_TYPES = {
    "md": "text/markdown; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
    "csv": "text/csv; charset=utf-8",
    "json": "application/json; charset=utf-8",
    "html": "text/html; charset=utf-8",
    "webp": "image/webp",
}

_SESSION_ID = None
_SESSION_ROOT = None


def get_voucher():
    base = (os.getenv("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")
    key = os.getenv("LINKFOX_AGENT_API_KEY") or os.getenv("LINKFOXAGENT_API_KEY")
    if not key:
        raise RuntimeError("缺少环境变量 LINKFOX_AGENT_API_KEY")
    last = None
    for attempt in range(3):
        if attempt:
            time.sleep(1 << (attempt - 1))
        try:
            body = request_json("/oss/getStsVoucherByAPI", {}, slug="linkfox-aigc-videogen-multi-upload",
                                timeout=30, persist=False, absolute_url=base + "/oss/getStsVoucherByAPI")
            if not isinstance(body, dict):
                raise RuntimeError("上传凭证响应格式异常")
            if body.get("error"):
                last = RuntimeError(f"获取上传凭证失败：{body.get('error')}")
                status = body.get("httpStatus")
                if status not in (408, 429, 500, 502, 503, 504) and body.get("errorCode") not in ("CONNECTION_ERROR", "REQUEST_TIMEOUT", "HTTP_READ_ERROR"):
                    raise last
                continue
            break
        except RuntimeError:
            raise
        except HTTPError as e:
            raw = e.read().decode(errors="replace")[:300]
            last = RuntimeError(f"获取上传凭证失败：HTTP {e.code}: {raw}")
            if e.code not in (408, 429, 500, 502, 503, 504):
                raise last
        except Exception as e:
            last = RuntimeError(f"获取上传凭证失败：{e}")
    else:
        raise last
    if not isinstance(body, dict):
        raise RuntimeError("上传凭证响应格式异常")
    v = body.get("data") if "data" in body else body
    if not isinstance(v, dict):
        raise RuntimeError("上传凭证响应缺少有效 data 对象")
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
    global _SESSION_ID, _SESSION_ROOT
    roots = []
    if os.getenv("ACPX_WORKSPACES"):
        roots.append(os.path.join(os.getenv("ACPX_WORKSPACES").split(os.pathsep)[0], "linkfox"))
    roots += [os.path.join(os.getcwd(), "linkfox"), os.path.join(os.path.expanduser("~"), "linkfox"), os.path.join(tempfile.gettempdir(), "linkfox")]
    if _SESSION_ROOT is None:
        for candidate in roots:
            try:
                os.makedirs(candidate, exist_ok=True)
                probe = os.path.join(candidate, ".write_probe")
                open(probe, "w").close(); os.remove(probe)
                _SESSION_ROOT = os.path.abspath(candidate); break
            except OSError:
                pass
    if _SESSION_ROOT is None:
        raise RuntimeError("找不到可写的会话目录")
    if _SESSION_ID is None:
        _SESSION_ID = (os.getenv("SESSION_ID") or (time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3))).strip()
    root, sid = _SESSION_ROOT, _SESSION_ID
    day = time.strftime("%Y-%m-%d", time.localtime(ts))
    path = os.path.join(root, day, sid); os.makedirs(path, exist_ok=True)
    meta_path = os.path.join(path, "_meta.json")
    if not os.path.exists(meta_path):
        meta = {"session_id": sid, "date": day, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts)), "skills_called": [], "deliverables": [], "data_files": [], "media_files": []}
        with open(meta_path, "w", encoding="utf-8") as f: json.dump(meta, f, ensure_ascii=False, indent=2)
        try:
            with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f: f.write(json.dumps({"session_id": sid, "date": day, "path": os.path.relpath(path, root), "started_at": meta["started_at"]}, ensure_ascii=False) + "\n")
        except OSError: pass
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
    if sys.argv[1:] in (["--help"], ["-h"]):
        print("用法：upload_files.py <文件> [<文件> ...]；上传前须确认文件可以公开")
    else:
        raise SystemExit(main(sys.argv[1:]))
