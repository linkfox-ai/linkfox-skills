#!/usr/bin/env python3
"""
AI生视频 - LinkFox Skill (异步模式)
调用 aigc/videoGenAsync 创建任务，然后轮询 aigc/taskQuery 获取结果。
"""

import json
import os
import sys
import time
from _aigc_runtime import call_api as _shared_call_api, request

from aigc_model_config import load_catalog, parse_model_args, print_catalog, save_catalog

CREATE_PATH = "/aigc/videoGenAsync"
QUERY_PATH = "/aigc/taskQuery"
SLUG = "linkfox-aigc-videogen"
MODEL_KIND = "video"
POLL_INTERVAL = 10
MAX_POLL_TIME = 1200
INITIAL_DELAY = 120


# ===== linkfox_paths 内联块（自包含，无外部依赖，无 oss2）=====
# 会话路径与媒体下载在本模块内实现，无外部 linkfox_paths 依赖。
# 提供：get_api_base / resolve_data_path / session_root / download_media
#       / encode_nl / decode_nl / decode_nl_in_obj

import json as _lf_json
import os as _lf_os
import secrets as _lf_secrets
import time as _lf_time
import tempfile as _lf_tempfile

# 与接口响应共用进程内会话，未设置 SESSION_ID 时数据和媒体也落在同一目录。
_LF_SESSION_CACHE = _shared_call_api._SESSION_CACHE
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


def _post(url, params, timeout=150):
    path = url[len(get_api_base()):]
    operation = "create" if path == CREATE_PATH else "query"
    return request(path, SLUG + "-" + operation, params, timeout=timeout)


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
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print("用法：aigc_videogen.py '<JSON>' [--inline] [--no-cache]")
        print("查询目录：--list-models [--allowed-models '<JSON 字符串数组>'] [--inline]")
        print("生成保留本地媒体交付协议；--inline 不打印临时媒体 URL。原任务续查请调用 taskQuery。")
        return
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

    argv = [arg for arg in argv if arg != "--no-cache"]
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

    # 最终响应静默存档；面向用户仍只交付本地视频路径。
    try:
        out_path = _resolve_output_path(time.time())
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"无法保存最终响应：{error}", file=sys.stderr)
    media_paths = _download_results(result)

    if media_paths:
        print(f"Saved full response: {json.dumps(media_paths, ensure_ascii=False)}")
    else:
        _emit_failure({**result, "error": "No media was delivered; query the same taskId instead of creating a new task", "errorCode": "NO_MEDIA_DELIVERED", "taskId": task_id, "taskStatus": result.get("status", "UNKNOWN"), "status": "DELIVERY_FAILED", "canQuery": True})


if __name__ == "__main__":
    main()
