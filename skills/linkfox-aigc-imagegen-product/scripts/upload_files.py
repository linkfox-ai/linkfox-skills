#!/usr/bin/env python3
"""商品图素材上传：保持本地路径 CLI，统一通过 call_api.run 取得凭证。"""

import json, os, secrets, sys, tempfile, time
import argparse
import io
from contextlib import redirect_stdout
from urllib.error import HTTPError

import call_api

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


API_PATH = "/oss/getStsVoucherByAPI"
SLUG = "linkfox-aigc-imagegen-product-sts"


def _normal_errcode(value):
    if value is None or (isinstance(value, str) and not value.strip()):
        return True
    if isinstance(value, str):
        value = value.strip()
        if len(value) != 3 or not value.isascii() or not value.isdigit():
            return False
        value = int(value)
    return type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0


def _safe_message(body, fallback):
    """保留原错误说明，并剔除响应中可能出现的 STS 值。"""
    message = str(body.get("errmsg") or body.get("message") or body.get("ErrorMessage") or fallback)
    def redact(node):
        nonlocal message
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("accessKeyId", "accessKeySecret", "securityToken") and value:
                    message = message.replace(str(value), "[已隐藏]")
                else:
                    redact(value)
        elif isinstance(node, list):
            for value in node:
                redact(value)
    redact(body)
    return message


class _LocalVoucherError(RuntimeError):
    """本地落盘异常不应触发第二次凭证请求。"""


def _request_voucher_once():
    # 公共 transport 只返回 body。观察其 urlopen 状态以落实公共 HTTP 判断，
    # 不自行发送请求；所有 LinkFox 请求由 call_api.run 发出。
    observed = {"status": None, "body": None}
    original_open, original_call = call_api.urlopen, call_api.call_api

    def observe_open(*args, **kwargs):
        try:
            response = original_open(*args, **kwargs)
            observed["status"] = response.status
            return response
        except HTTPError as exc:
            observed["status"] = exc.code
            raise

    def observe_call(*args, **kwargs):
        body = original_call(*args, **kwargs)
        observed["body"] = body
        # 防止公共输出流程对非对象调用 .get，实际异常仍由业务层判断。
        return body if isinstance(body, dict) else {"error": "上传凭证响应格式异常"}

    call_api.urlopen, call_api.call_api = observe_open, observe_call
    try:
        # 让公共原始响应与上传登记共用同一会话，支持可写目录回退。
        session_dir(time.time())
        call_api._SESSION_CACHE.update({"_root": _SESSION_ROOT, "_auto": _SESSION_ID})
        # 捕获公共脚本的完整凭证打印；完整响应仍由 run 落盘，不暴露到对话。
        output = io.StringIO()
        with redirect_stdout(output):
            call_api.run(API_PATH, SLUG, argv=["{}", "--no-cache"])
        if "Saved full response:" not in output.getvalue():
            raise _LocalVoucherError("上传凭证响应未保存；请检查会话目录")
    except Exception as exc:
        if observed["body"] is not None:
            raise _LocalVoucherError("上传凭证响应本地处理失败；请检查会话目录") from exc
        raise
    finally:
        call_api.urlopen, call_api.call_api = original_open, original_call
    return observed["status"], observed["body"]


def get_voucher():
    if not (os.getenv("LINKFOX_AGENT_API_KEY") or os.getenv("LINKFOXAGENT_API_KEY")):
        raise RuntimeError("缺少环境变量 LINKFOX_AGENT_API_KEY 或 LINKFOXAGENT_API_KEY")
    last = RuntimeError("获取上传凭证失败")
    for attempt in range(3):
        if attempt:
            time.sleep(1 << (attempt - 1))
        try:
            status, body = _request_voucher_once()
        except _LocalVoucherError:
            raise
        except Exception:
            last = RuntimeError("获取上传凭证失败：网络或本地处理异常")
            continue
        if status is None or status in (408, 429, 500, 502, 503, 504):
            last = RuntimeError(f"获取上传凭证失败：HTTP {status}" if status else "获取上传凭证失败：连接异常")
            continue
        if not 200 <= status < 300:
            reason = _safe_message(body, "请求未正常响应") if isinstance(body, dict) else "请求未正常响应"
            raise RuntimeError(f"获取上传凭证失败：HTTP {status}：{reason}")
        break
    else:
        raise last
    if not isinstance(body, dict):
        raise RuntimeError("上传凭证响应格式异常")
    if not _normal_errcode(body.get("errcode")):
        raise RuntimeError("上传凭证业务错误：" + _safe_message(body, "请在本地检查 errcode/errmsg"))
    v = body.get("data") if "data" in body else body
    if not isinstance(v, dict):
        raise RuntimeError("上传凭证响应缺少有效 data")
    if "ErrorCode" in v:
        raise RuntimeError("上传凭证错误：" + str(v["ErrorCode"]) + " - " + _safe_message(v, "请在本地检查 ErrorMessage"))
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
            if batch_limit is not None and upload_attempts >= batch_limit:
                results.append({"error": True, "input": path, "message": f"单次最多上传 {batch_limit} 个文件"}); failed = True; continue
            if voucher is None: voucher = get_voucher()
            if batch_limit is None and isinstance(voucher.get("maxFileCount"), int) and voucher["maxFileCount"] > 0:
                batch_limit = voucher["maxFileCount"]
            if batch_limit is not None and upload_attempts >= batch_limit:
                results.append({"error": True, "input": path, "message": f"单次最多上传 {batch_limit} 个文件"}); failed = True; continue
            upload_attempts += 1
            results.append(upload(path, voucher))
        except Exception as e:
            message = _safe_message({"message": str(e), "data": voucher}, "上传失败")
            results.append({"error": True, "input": path, "message": message}); voucher = None; failed = True
    print(json.dumps(results, ensure_ascii=False, indent=2))
    for r in results:
        if not r.get("error"):
            print(f"Saved full response: {r['url']} ({r['size']} bytes)")
            print(f"Uploaded {r['localPath']} -> {r['url']}")
    return int(failed)


def cli(argv=None):
    parser = argparse.ArgumentParser(description="上传已确认可公开的商品素材，输出公开 HTTPS URL")
    parser.add_argument("paths", nargs="*", help="本地文件路径，或含 files 数组的 JSON")
    parser.add_argument("--inline", action="store_true", help="全量输出上传结果（不输出 STS）")
    parser.add_argument("--no-cache", action="store_true", help="凭证始终禁用持久响应缓存")
    args = parser.parse_args(argv)
    paths = args.paths
    if len(paths) == 1 and paths[0].lstrip().startswith("{"):
        try:
            params = json.loads(paths[0])
            paths = params["files"]
            if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
                raise ValueError("files 必须是路径字符串数组")
        except (ValueError, KeyError, TypeError):
            print("ERROR: JSON 须含 files 路径数组", file=sys.stderr)
            return 1
    return main(paths)


if __name__ == "__main__":
    raise SystemExit(cli())
