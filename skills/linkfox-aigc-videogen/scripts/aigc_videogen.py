#!/usr/bin/env python3
"""
AI生视频 - LinkFox Skill (异步模式)
调用 aigc/videoGenAsync 创建任务，然后轮询 aigc/taskQuery 获取结果。
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from http.client import HTTPException

from aigc_model_config import load_catalog, parse_model_args, print_catalog, save_catalog

CREATE_PATH = "/aigc/videoGenAsync"
QUERY_PATH = "/aigc/taskQuery"
SLUG = "linkfox-aigc-videogen"
MODEL_KIND = "video"
POLL_INTERVAL = 10
MAX_POLL_TIME = 1200
INITIAL_DELAY = 120


# ===== linkfox_paths 内联块（自包含，无外部依赖，无 oss2）=====
# 粘贴到各 aigc skill 的 py 脚本模块级，替代 `from linkfox_paths import ...`。
# 提供：get_api_base / resolve_data_path / session_root / download_media
#       / encode_nl / decode_nl / decode_nl_in_obj

import json as _lf_json
import os as _lf_os
import secrets as _lf_secrets
import time as _lf_time
import tempfile as _lf_tempfile

_LF_SESSION_CACHE = {}
NL_PLACEHOLDER = "⏎"


def get_api_base():
    """网关基础地址：env LINKFOX_TOOL_GATEWAY 优先，缺省回退正式地址。"""
    return (_lf_os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")


def _lf_format_iso(ts):
    return _lf_time.strftime("%Y-%m-%dT%H:%M:%S%z", _lf_time.localtime(ts))


def _lf_session_id(ts):
    env = _lf_os.environ.get("SESSION_ID")
    if env:
        return env.strip()
    if "_auto" not in _LF_SESSION_CACHE:
        _LF_SESSION_CACHE["_auto"] = (
            _lf_time.strftime("%H%M%S", _lf_time.localtime(ts)) + "-" + _lf_secrets.token_hex(3)
        )
    return _LF_SESSION_CACHE["_auto"]


def _lf_linkfox_root():
    cached = _LF_SESSION_CACHE.get("_root")
    if cached:
        return cached
    candidates = []
    acpx = (_lf_os.environ.get("ACPX_WORKSPACES") or "").strip()
    if acpx:
        acpx = acpx.split(_lf_os.pathsep)[0].strip()
        if acpx:
            candidates.append(_lf_os.path.join(acpx, "linkfox"))
    candidates.append(_lf_os.path.join(_lf_os.getcwd(), "linkfox"))
    candidates.append(_lf_os.path.join(_lf_os.path.expanduser("~"), "linkfox"))
    candidates.append(_lf_os.path.join(_lf_tempfile.gettempdir(), "linkfox"))
    for root in candidates:
        try:
            _lf_os.makedirs(root, exist_ok=True)
            probe = _lf_os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("")
            _lf_os.remove(probe)
        except OSError:
            continue
        root = _lf_os.path.abspath(root)
        _LF_SESSION_CACHE["_root"] = root
        return root
    fallback = _lf_os.path.abspath(candidates[-1])
    _LF_SESSION_CACHE["_root"] = fallback
    return fallback


def _lf_ensure_meta(root, session_dir, date_str, sid, ts):
    meta_path = _lf_os.path.join(session_dir, "_meta.json")
    if _lf_os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _lf_format_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        _lf_json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(_lf_os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(
                _lf_json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": _lf_os.path.relpath(session_dir, root),
                        "started_at": _lf_format_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass


def _lf_update_meta(session_dir, *, skill, kind, file_rel, ts):
    meta_path = _lf_os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = _lf_json.load(f)
    except (OSError, _lf_json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    bucket = {"data": "data_files", "deliverable": "deliverables", "media": "media_files"}.get(
        kind, "data_files"
    )
    files = meta.setdefault(bucket, [])
    if file_rel not in files:
        files.append(file_rel)
    meta["last_used_at"] = _lf_format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        _lf_json.dump(meta, f, ensure_ascii=False, indent=2)


def _lf_ensure_session(ts):
    date_str = _lf_time.strftime("%Y-%m-%d", _lf_time.localtime(ts))
    sid = _lf_session_id(ts)
    root = _lf_linkfox_root()
    session_dir = _lf_os.path.join(root, date_str, sid)
    _lf_os.makedirs(session_dir, exist_ok=True)
    _lf_ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir


def resolve_data_path(slug, ts, ext="json"):
    """普通 skill 的原始数据落到 <session>/data/<slug>-<ts>.<ext>。"""
    _, session_dir = _lf_ensure_session(ts)
    sub = _lf_os.path.join(session_dir, "data")
    _lf_os.makedirs(sub, exist_ok=True)
    out = _lf_os.path.join(sub, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _lf_update_meta(session_dir, skill=slug, kind="data", file_rel=_lf_os.path.relpath(out, session_dir), ts=ts)
    return out


def session_root(ts=None):
    """返回当前 session 目录。"""
    if ts is None:
        ts = _lf_time.time()
    _, session_dir = _lf_ensure_session(ts)
    return session_dir


def download_media(url, slug, ts=None, ext=None, timeout=300):
    """下载 URL 到 <session>/media/<slug>-<ts>.<ext>，返回本地路径；失败返回 None。"""
    import sys as _lf_sys
    from urllib.request import urlopen as _lf_urlopen, Request as _lf_Request
    import posixpath as _lf_posixpath

    if not url or not isinstance(url, str):
        return None

    if not url.startswith("http://") and not url.startswith("https://"):
        print(f"[download_media] Unsupported URL scheme: {url[:80]}", file=_lf_sys.stderr)
        return None

    if ts is None:
        ts = _lf_time.time()

    guessed_ext = ext
    if not guessed_ext:
        path_part = url.split("?")[0]
        candidate = _lf_posixpath.splitext(path_part)[1].lstrip(".")
        if candidate and len(candidate) <= 5 and candidate.isalnum():
            guessed_ext = candidate
        else:
            guessed_ext = "bin"

    _, session_dir = _lf_ensure_session(ts)
    media_dir = _lf_os.path.join(session_dir, "media")
    _lf_os.makedirs(media_dir, exist_ok=True)
    tmp_filename = f".tmp-{slug}-{int(ts * 1_000_000)}.download"
    tmp_path = _lf_os.path.join(media_dir, tmp_filename)

    req = _lf_Request(url, headers={"User-Agent": "LinkFox-Skill/2.0"})
    try:
        with _lf_urlopen(req, timeout=timeout) as resp:
            if guessed_ext == "bin":
                ct = resp.headers.get("Content-Type", "")
                if "mp4" in ct:
                    guessed_ext = "mp4"
                elif "webm" in ct:
                    guessed_ext = "webm"
                elif "png" in ct:
                    guessed_ext = "png"
                elif "jpeg" in ct or "jpg" in ct:
                    guessed_ext = "jpg"
                elif "webp" in ct:
                    guessed_ext = "webp"
                elif "gif" in ct:
                    guessed_ext = "gif"
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)

        ts_us = int(ts * 1_000_000)
        final_path = _lf_os.path.join(media_dir, f"{slug}-{ts_us}.{guessed_ext}")
        _lf_os.replace(tmp_path, final_path)
        _lf_update_meta(session_dir, skill=slug, kind="media", file_rel=_lf_os.path.relpath(final_path, session_dir), ts=ts)
        return final_path
    except Exception as e:
        print(f"[download_media] Failed to download {url}: {e}", file=_lf_sys.stderr)
        try:
            if _lf_os.path.exists(tmp_path):
                _lf_os.remove(tmp_path)
        except OSError:
            pass
        return None


def encode_nl(text):
    if not isinstance(text, str):
        return text
    text = text.replace("\\r\\n", NL_PLACEHOLDER)
    text = text.replace("\\n", NL_PLACEHOLDER)
    text = text.replace("\\r", NL_PLACEHOLDER)
    text = text.replace("\r\n", NL_PLACEHOLDER)
    text = text.replace("\r", NL_PLACEHOLDER)
    text = text.replace("\n", NL_PLACEHOLDER)
    return text


def decode_nl(text):
    if not isinstance(text, str):
        return text
    return text.replace(NL_PLACEHOLDER, "\n")


def decode_nl_in_obj(obj):
    if isinstance(obj, str):
        return decode_nl(obj)
    if isinstance(obj, list):
        return [decode_nl_in_obj(item) for item in obj]
    if isinstance(obj, dict):
        return {k: decode_nl_in_obj(v) for k, v in obj.items()}
    return obj

_get_base = get_api_base


def get_api_base():
    return _get_base()


def get_api_key():
    """
获取配置在环境变量的API Key。
如果获取不到，按 SKILL.md 的 **## 解决认证和算力问题** 处理。
"""
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print("API Key 未配置", file=sys.stderr)
        sys.exit(1)
    return key


def _response_error(code, message, raw=b"", status=None, headers=None):
    headers = headers or {}
    result = {"error": message, "errorCode": code, "responseBytes": len(raw)}
    if status is not None:
        result["httpStatus"] = status
    content_type = headers.get("Content-Type")
    request_id = headers.get("X-Request-Id") or headers.get("X-Kong-Request-Id")
    if content_type:
        result["contentType"] = content_type
    if request_id:
        result["requestId"] = request_id
    if raw:
        # Kept in the failure data file, never printed as a raw body to stdout.
        result["details"] = raw.decode("utf-8", errors="replace")
    return result


def _decode_response(raw, status, headers):
    if not raw.strip():
        return _response_error("EMPTY_RESPONSE", f"Upstream returned an empty response (HTTP {status})", raw, status, headers)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _response_error("INVALID_ENCODING", f"Upstream response is not UTF-8 (HTTP {status})", raw, status, headers)
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return _response_error("INVALID_JSON_RESPONSE", f"Upstream response is not JSON (HTTP {status})", raw, status, headers)
    if not isinstance(result, dict):
        return _response_error("INVALID_RESPONSE", "Upstream JSON response must be an object", raw, status, headers)
    business_code = result.get("errcode", result.get("code"))
    business_failed = business_code is not None and str(business_code) not in ("0", "200")
    if result.get("error") or business_failed or not 200 <= status < 300:
        message = result.get("error") or result.get("errmsg") or result.get("msg") or result.get("message") or f"HTTP {status}: upstream request failed"
        result["error"] = message
        result.setdefault("errorCode", str(business_code) if business_failed else "HTTP_ERROR")
        metadata = _response_error(result["errorCode"], message, raw, status, headers)
        for key in ("httpStatus", "contentType", "requestId", "responseBytes"):
            if key in metadata:
                result.setdefault(key, metadata[key])
    return result


def _post(url, params, timeout=150):
    api_key = get_api_key()
    data = json.dumps(params, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }
    req = Request(url, data=data, headers=headers, method="POST")
    status, response_headers = None, {}
    try:
        with urlopen(req, timeout=timeout) as response:
            status = response.status
            response_headers = response.headers
            return _decode_response(response.read(), status, response_headers)
    except HTTPError as error:
        try:
            raw = error.read() if error.fp else b""
            return _decode_response(raw, error.code, error.headers or {})
        except (OSError, HTTPException) as read_error:
            return _response_error("HTTP_READ_ERROR", "Could not read upstream error response", getattr(read_error, "partial", b""), error.code, error.headers)
    except URLError as error:
        code = "REQUEST_TIMEOUT" if isinstance(error.reason, TimeoutError) else "CONNECTION_ERROR"
        return {"error": "Request timed out; submission outcome may be unknown" if code == "REQUEST_TIMEOUT" else f"Connection failed: {error.reason}", "errorCode": code}
    except TimeoutError:
        return _response_error("REQUEST_TIMEOUT", "Request timed out; submission outcome may be unknown", status=status, headers=response_headers)
    except (OSError, HTTPException) as error:
        return _response_error("HTTP_READ_ERROR", "Could not read upstream response; submission outcome may be unknown", getattr(error, "partial", b""), status, response_headers)


def create_task(params):
    url = get_api_base() + CREATE_PATH
    return _post(url, params)


def query_task(task_id, member_id, timeout=150):
    url = get_api_base() + QUERY_PATH
    return _post(url, {"taskId": task_id, "memberId": member_id}, timeout=timeout)


def _retryable_query_error(result):
    status = result.get("httpStatus")
    return (isinstance(status, int) and (status in (408, 429) or status >= 500)) or result.get("errorCode") in ("CONNECTION_ERROR", "REQUEST_TIMEOUT", "HTTP_READ_ERROR")


def poll_until_done(task_id, member_id):
    deadline = time.monotonic() + MAX_POLL_TIME
    last_status, last_error = "UNKNOWN", None
    print(f"  Waiting {INITIAL_DELAY}s before first poll...", file=sys.stderr)
    time.sleep(min(INITIAL_DELAY, MAX_POLL_TIME))
    while time.monotonic() < deadline:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        result = query_task(task_id, member_id, timeout=min(150, remaining))
        if result.get("error"):
            if not _retryable_query_error(result):
                return {**result, "taskId": task_id, "taskStatus": last_status, "canQuery": True}
            last_error = result
            print(f"  Poll error: {result['error']}", file=sys.stderr)
        else:
            status = result.get("status")
            if isinstance(status, str) and status:
                last_status = status
            if status in ("SUCCESS", "FAILED"):
                return result
            elapsed = int(MAX_POLL_TIME - (deadline - time.monotonic()))
            print(f"  Polling... status={status}, elapsed={elapsed}s", file=sys.stderr)
        time.sleep(min(POLL_INTERVAL, max(0, deadline - time.monotonic())))
    result = {
        "error": f"Polling timeout after {MAX_POLL_TIME}s; use the same taskId to query again, do not resubmit",
        "errorCode": "POLL_TIMEOUT", "status": "TIMEOUT", "taskStatus": last_status,
        "taskId": task_id, "pollTimedOut": True, "canQuery": True,
    }
    if last_error is not None:
        result["lastQueryError"] = last_error
    return result


def _resolve_output_path(ts):
    return resolve_data_path(SLUG, ts)


def _download_results(result):
    try:
        if not isinstance(result, dict):
            return []
        if result.get("error"):
            return []
        result_list = result.get("resultList") or []
        local_paths = []
        for i, item in enumerate(result_list):
            url = item.get("url") if isinstance(item, dict) else None
            if not url:
                continue
            ts = time.time() + i * 0.01
            path = download_media(url, SLUG, ts)
            if path:
                local_paths.append(path)
            else:
                print(f"  Download failed: {url}", file=sys.stderr)
        return local_paths
    except Exception as e:
        print(f"[_download_results] error: {e}", file=sys.stderr)
        return []


def summarize(result):
    if not isinstance(result, dict):
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "code", "msg", "costToken", "status"):
        if k in result:
            print(f"  {k}: {result[k]}")
    result_list = result.get("resultList") or []
    if result_list:
        print(f"\nresultList (length={len(result_list)}):")
        print(json.dumps(result_list[:3], indent=2, ensure_ascii=False))


def _emit_failure(result, exit_code=1):
    result = dict(result)
    result.setdefault("status", "ERROR")
    out_path = None
    try:
        out_path = _resolve_output_path(time.time())
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
        print(f"Saved full response: {out_path}")
    except OSError as error:
        print(f"Failed to save error response: {error}", file=sys.stderr)
        out_path = None
    keys = ("error", "errorCode", "errcode", "code", "errmsg", "msg", "traceId", "requestId", "httpStatus", "contentType", "responseBytes", "status", "taskStatus", "taskId", "pollTimedOut", "canQuery")
    summary = {key: result[key] for key in keys if key in result}
    summary["dataFile"] = out_path
    print(json.dumps(summary, ensure_ascii=False))
    sys.exit(exit_code)


def main():
    try:
        list_models, allowed_models, inline, argv = parse_model_args(sys.argv[1:])
    except ValueError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        sys.exit(1)

    if list_models:
        catalog = load_catalog(MODEL_KIND, allowed_models=allowed_models)
        out = save_catalog(catalog, resolve_data_path, SLUG)
        print_catalog(catalog, out, inline=inline)
        return

    if not argv:
        print("Usage: aigc_videogen.py '<JSON>'", file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        _emit_failure({"error": f"Invalid parameter JSON: {e}", "errorCode": "INVALID_PARAMETERS"})
    if not isinstance(params, dict):
        _emit_failure({"error": "Parameters must be a JSON object", "errorCode": "INVALID_PARAMETERS"})

    params = decode_nl_in_obj(params)

    member_id = params.get("memberId", "")

    create_result = create_task(params)
    if create_result.get("error"):
        _emit_failure(create_result)

    task_id = create_result.get("taskId")
    cost_token = create_result.get("costToken", 0)

    if not task_id:
        _emit_failure({**create_result, "error": "Task creation response did not contain taskId; do not resubmit automatically", "errorCode": "MISSING_TASK_ID"})

    print(f"Task created: taskId={task_id}, costToken={cost_token}", file=sys.stderr)

    result = poll_until_done(task_id, member_id)
    result["costToken"] = cost_token
    if result.get("error") or result.get("status") == "FAILED":
        result.setdefault("taskId", task_id)
        result.setdefault("error", result.get("errorMsg") or result.get("errmsg") or "Task generation failed")
        result.setdefault("errorCode", "TASK_FAILED")
        _emit_failure(result, 2 if result.get("errorCode") == "POLL_TIMEOUT" else 1)

    media_paths = _download_results(result)

    if media_paths:
        print(f"Saved full response: {json.dumps(media_paths, ensure_ascii=False)}")
    else:
        _emit_failure({**result, "error": "No media was delivered; query the same taskId instead of creating a new task", "errorCode": "NO_MEDIA_DELIVERED", "taskId": task_id, "taskStatus": result.get("status", "UNKNOWN"), "status": "DELIVERY_FAILED", "canQuery": True})


if __name__ == "__main__":
    main()
