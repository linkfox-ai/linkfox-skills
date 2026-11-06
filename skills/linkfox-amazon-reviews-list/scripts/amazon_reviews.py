#!/usr/bin/env python3
"""
Amazon Product Reviews - LinkFox Skill
仅调用异步提交和轮询接口。

Usage:
  python amazon_reviews.py '<JSON parameters>'           # 默认异步：提交或查询一次后立即返回
  python amazon_reviews.py '<JSON parameters>' --inline  # 强制全量打印到 stdout

输出策略（脚本默认行为）：
  - **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-reviews-list-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
  - 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
  - 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
  - 加 `--inline` 强制全量打印到 stdout（同样落盘）
"""

import json
import hashlib
import os
import sys
import time
import secrets
import contextlib
import io
from unittest.mock import patch

import call_api as api


ASYNC_SUBMIT_API_PATH = "/amazon/reviews/async/submit"
ASYNC_RESULT_API_PATH = "/amazon/reviews/async/result"
SLUG = "linkfox-amazon-reviews-list"

# 响应小于等于该字节数时，落盘后全量输出
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
ASYNC_OBSERVATION_LIMIT_SEC = 200

# 经验等待时间，只用于提示 Agent 何时再次查询，不是供应商 SLA。
PROVIDER_READY_WINDOWS_SEC = {
    "PANGOLINFO": (10, 30),
    "PANGO": (10, 30),
    "APIFY": (15, 60),
}
DEFAULT_READY_WINDOW_SEC = (10, 60)

_SESSION_CACHE: dict[str, str] = {}


def _errcode_ok(value):
    """按网关响应码判断成功，0 和 false 均不是空值。"""
    if value is None:
        return True
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return True
        if len(value) != 3 or not value.isascii() or not value.isdigit():
            return False
        value = int(value)
    return type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0


def call_api(path, params, timeout=30):
    """通过公共 run 发起请求，使用业务超时、响应头及任务处理约定。"""
    # 先准备会话目录，禁止公共调用器回退到家目录或临时目录。
    _ensure_session(time.time())
    state = {}
    saved_call = api.call_api
    saved_open = api.urlopen
    saved_request = api.Request

    def request(*args, **kwargs):
        req = saved_request(*args, **kwargs)
        req.add_header("Accept", "application/json")
        return req

    def open_with_metadata(req, **kwargs):
        # 公共调用器提供网络传输；使用业务超时并读取费用头。
        response = saved_open(req, timeout=timeout)
        state["costToken"] = response.headers.get("X-Cost-Token")
        state["httpStatus"] = response.status
        return response

    def capture(api_path, data):
        try:
            http_status, payload = saved_call(api_path, data)
        except TimeoutError:
            http_status, payload = None, {"error": f"Request timed out: {api_path}"}
        except (ValueError, UnicodeError) as error:
            http_status = state.get("httpStatus")
            payload = {"error": f"Invalid JSON response: {api_path}",
                       "details": str(getattr(error, "doc", error))[:2000], "retryable": False}
        if not isinstance(payload, dict):
            payload = {"error": "Invalid async API response", "details": payload, "retryable": False}
        if http_status is not None and not 200 <= http_status < 300:
            payload["httpStatus"] = http_status
            if not payload.get("error"):
                payload["error"] = payload.get("errmsg") or f"HTTP {http_status}"
        if not _errcode_ok(payload.get("errcode")):
            if not payload.get("error"):
                payload["error"] = payload.get("errmsg") or f"Business error: {payload['errcode']}"
            payload["retryable"] = False
        cost = state.get("costToken")
        if cost is not None:
            try:
                payload["costToken"] = int(cost)
            except ValueError:
                payload["costToken"] = cost
        state["result"] = payload
        return http_status, payload

    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(api, "call_api", capture))
        stack.enter_context(patch.object(api, "Request", request))
        stack.enter_context(patch.object(api, "urlopen", open_with_metadata))
        stack.enter_context(patch.object(api, "_resolve_output_path",
                                        lambda slug, ts: resolve_data_path(slug, time.time())))
        # run 即使禁用缓存也会调用 _cache_path；使用同一任务路径，不建第二套缓存。
        stack.enter_context(patch.object(api, "_cache_path", lambda slug, data: _cache_path(data)))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        try:
            api.run(path, SLUG + "-" + path.rsplit("/", 1)[-1],
                    argv=[json.dumps(params, ensure_ascii=False), "--no-cache", "--inline"])
        except OSError as error:
            # 任务结果可能已被后端删除；让业务层继续保存或完整打印已领取的数据。
            if "result" not in state:
                raise
            print(f"保存接口原始响应失败，将继续输出已领取的数据：{error}", file=sys.stderr)
    return state["result"]


def _task_id(payload):
    """Read taskId from the direct response or a common gateway wrapper."""
    candidates = [payload]
    if isinstance(payload, dict):
        candidates.extend(payload.get(key) for key in ("data", "result"))
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate.get("taskId"):
            return str(candidate["taskId"])
    return None


def _task_provider(payload):
    """Read the backend-selected provider from the submit response."""
    candidates = [payload]
    if isinstance(payload, dict):
        candidates.extend(payload.get(key) for key in ("data", "result"))
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate.get("provider"):
            return str(candidate["provider"])
    return None


def _task_status(payload):
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("status") or "").strip().upper()


def _timing_hint(provider, recheck=False):
    normalized_provider = str(provider or "").strip().upper()
    ready_min, ready_max = PROVIDER_READY_WINDOWS_SEC.get(
        normalized_provider,
        DEFAULT_READY_WINDOW_SEC,
    )
    return {
        "estimatedReadyInSeconds": {
            "min": ready_min,
            "max": ready_max,
        },
        "suggestedNextCheckAfterSeconds": 10 if recheck else ready_min,
    }


def _task_age_seconds(response, submitted_at=None):
    raw_created_at = response.get("createdAt") if isinstance(response, dict) else None
    raw_timestamp = raw_created_at if raw_created_at is not None else submitted_at
    if raw_timestamp is None:
        return None
    try:
        timestamp = float(raw_timestamp)
    except (TypeError, ValueError):
        return None
    if timestamp > 10_000_000_000:
        timestamp /= 1000.0
    return max(0, int(time.time() - timestamp))


def _poll_timeout_result(task_id, provider, elapsed_seconds=None, limit_seconds=None):
    effective_limit = limit_seconds or ASYNC_OBSERVATION_LIMIT_SEC
    return {
        "status": "POLL_TIMEOUT",
        "taskId": task_id,
        "provider": provider,
        "elapsedSeconds": elapsed_seconds,
        "costToken": 0,
        "retryable": True,
        "upstreamCancellationSupported": False,
        "message": (
            f"No result within {effective_limit} seconds. Ask the user whether to query the same "
            "taskId again or stop polling; do not submit a new task."
        ),
    }


def _async_task_marker(task_id, provider, status="PENDING", **metadata):
    task = {
        "taskId": task_id,
        "provider": provider,
        "status": status,
    }
    task.update({key: value for key, value in metadata.items() if value is not None})
    return {"_asyncTask": task}


def _is_async_task_marker(payload):
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("_asyncTask"), dict)
        and bool(payload["_asyncTask"].get("taskId"))
    )


def submit_async(params):
    submit_params = dict(params)
    submit_params.pop("provider", None)
    response = call_api(ASYNC_SUBMIT_API_PATH, submit_params)
    if not isinstance(response, dict) or response.get("error"):
        return response, None
    task_id = _task_id(response)
    if not task_id:
        return {"error": "Async submit response did not include taskId", "details": response}, None
    provider = _task_provider(response)
    marker = _async_task_marker(
        task_id,
        provider,
        status=_task_status(response) or "PENDING",
        pollAfterMillis=response.get("pollAfterMillis", 2000),
        submittedAt=int(time.time()),
        **_timing_hint(provider),
    )
    return marker, task_id


def _is_retryable_poll_error(response):
    """A failed query is not a failed task; never retry a known missing task."""
    message = " ".join(str(response.get(key) or "") for key in ("error", "errmsg")).lower()
    if any(text in message for text in (
        "任务不存在", "任务已过期", "task missing", "task not found", "task expired",
    )):
        return False
    codes = []
    for key in ("httpStatus", "errcode"):
        try:
            codes.append(int(response.get(key)))
        except (TypeError, ValueError):
            pass
    if any(code in (400, 401, 402, 403, 404, 405, 410, 422) for code in codes):
        return False
    return (
        any(code == 429 or 500 <= code <= 599 for code in codes)
        or message.startswith(("connection failed", "request timed out", "invalid json response"))
        or "查询异步任务失败，请稍后重试" in message
    )


def poll_async_once(task_id, provider=None, timeout=30, submitted_at=None):
    """Query one task exactly once so the caller remains non-blocking."""
    response = call_api(
        ASYNC_RESULT_API_PATH,
        {"taskId": task_id},
        timeout=timeout,
    )
    if not isinstance(response, dict):
        return {"error": "Invalid async result response", "taskId": task_id}, True

    status = _task_status(response)
    # 网关失败时不依据残留业务状态领取成功结果或宣称取消免费。
    if response.get("error") and (
        response.get("httpStatus") is not None or not _errcode_ok(response.get("errcode"))
    ):
        status = ""
    if status == "SUCCEEDED":
        result = response.get("result")
        if not isinstance(result, dict):
            return {
                "error": "Async task succeeded without a result object",
                "taskId": task_id,
            }, True
        if "costToken" in response:
            result["costToken"] = response["costToken"]
        return result, True
    if status == "CANCELLED":
        return {
            "error": (
                "当前评论服务请求较多，任务在等待执行资源时已自动取消，"
                "未调用供应商且未产生费用。请稍后重新提交。"
            ),
            "details": response.get("error"),
            "taskId": task_id,
            "provider": response.get("provider") or provider,
            "status": status,
            "costToken": 0,
            "retryable": True,
        }, True
    if status == "FAILED":
        return {
            "error": response.get("error") or f"Amazon review async task {status.lower()}",
            "taskId": task_id,
            "provider": response.get("provider") or provider,
            "status": status,
            "costToken": 0,
        }, True
    if response.get("error"):
        response.setdefault("taskId", task_id)
        response["retryable"] = _is_retryable_poll_error(response)
        if response["retryable"]:
            elapsed_seconds = _task_age_seconds(response, submitted_at)
            if elapsed_seconds is not None and elapsed_seconds >= ASYNC_OBSERVATION_LIMIT_SEC:
                return _poll_timeout_result(task_id, provider, elapsed_seconds), False
            response["suggestedNextCheckAfterSeconds"] = 10
            response["message"] = "本次查询临时失败，请稍后查询同一 taskId，不要重新提交任务。"
        return response, not response["retryable"]
    if status not in ("PENDING", "RUNNING"):
        return {
            "error": f"Unexpected async task status: {status or 'missing'}",
            "taskId": task_id,
            "details": response,
        }, True

    actual_provider = response.get("provider") or provider
    elapsed_seconds = _task_age_seconds(response, submitted_at)
    if elapsed_seconds is not None and elapsed_seconds >= ASYNC_OBSERVATION_LIMIT_SEC:
        return _poll_timeout_result(
            task_id,
            actual_provider,
            elapsed_seconds,
            ASYNC_OBSERVATION_LIMIT_SEC,
        ), False

    metadata = {
        key: response.get(key)
        for key in (
            "pollAfterMillis",
            "createdAt",
            "startedAt",
            "completedAt",
            "expiresAt",
        )
    }
    metadata["submittedAt"] = submitted_at
    return _async_task_marker(
        task_id,
        actual_provider,
        status=status,
        **_timing_hint(actual_provider, recheck=True),
        **metadata,
    ), False


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    try:
        if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
            return None
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            payload.setdefault("_cache", {})["hit"] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _cache_timestamp(*paths):
    for path in paths:
        try:
            return os.path.getmtime(path)
        except OSError:
            continue
    return time.time()


def _save_cache(path, payload):
    # 同目录短文件名保留原子替换，避免回执路径追加后缀超过 Windows 路径限制。
    temporary_path = os.path.join(os.path.dirname(path), f".{secrets.token_hex(6)}.tmp")
    try:
        with open(temporary_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(temporary_path, path)
        return True
    except OSError as error:
        print(f"Failed to save task cache: {error}", file=sys.stderr)
        return False
    finally:
        try:
            if os.path.exists(temporary_path):
                os.remove(temporary_path)
        except OSError:
            pass


def _save_terminal_task(task_path, payload):
    # A delayed RUNNING/error writer must never overwrite a received result.
    suffix = ".received.json" if _is_received_task(payload) else ".terminal.json"
    if _save_cache(task_path + suffix, payload):
        try:
            if os.path.isfile(task_path):
                os.remove(task_path)
        except OSError as error:
            print(f"Failed to remove pending task marker: {error}", file=sys.stderr)


def _load_task_state(params, use_cache):
    """Resolve original parameters and taskId to one canonical task cache."""
    request_path = _cache_path(params)
    cached = _load_cache(request_path) if use_cache else None
    task_id = params.get("taskId") if isinstance(params, dict) else None
    if not task_id and isinstance(cached, dict):
        if _is_async_task_marker(cached):
            task_id = cached["_asyncTask"]["taskId"]
        else:
            task_id = cached.get("_asyncTaskRef") or cached.get("taskId")
    if not task_id:
        return request_path, None, None, cached

    task_id = str(task_id).strip()
    task_path = _cache_path({"taskId": task_id})
    canonical = _load_cache(task_path + ".received.json") if use_cache else None
    if canonical is None:
        canonical = _load_cache(task_path + ".terminal.json") if use_cache else None
    if canonical is None:
        canonical = _load_cache(task_path) if use_cache else None
    if canonical is not None:
        cached = canonical
    if cached is None or (isinstance(cached, dict) and cached.get("_asyncTaskRef")):
        submitted_at = params.get("submittedAt") if isinstance(params, dict) else None
        if submitted_at is None:
            submitted_at = _cache_timestamp(request_path) if cached is not None else time.time()
        # Even if the canonical cache expired, a known task must never be resubmitted.
        cached = _async_task_marker(task_id, None, status=None, submittedAt=submitted_at)
    return request_path, task_id, task_path, cached


def _is_received_task(payload):
    return (isinstance(payload, dict) and isinstance(payload.get("_asyncReceipt"), dict)
            and bool(payload["_asyncReceipt"].get("taskId")))


def _received_task_response(payload):
    receipt = payload["_asyncReceipt"]
    result_file = receipt.get("resultFile")
    file_exists = bool(result_file and os.path.isfile(result_file))
    response = {
        "status": "ALREADY_RECEIVED",
        "taskId": receipt["taskId"],
        "resultFile": result_file,
        "fileExists": file_exists,
        "costToken": 0,
        "_cache": {"hit": True},
        "message": "结果已领取，请读取 resultFile；本次未查询后端，也未重新提交任务。",
    }
    if not file_exists:
        response["error"] = "任务已领取，但本地结果文件不存在；请查找之前保存的文件或输出，不要自动重新提交。"
    return response


def _find_main_list(obj):
    """递归找到元素数最多的 list 字段。不写死字段名，适配任何结构。"""
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    return best[0], best[1]


def summarize(result):
    """打印紧凑摘要。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")

    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costToken", "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))

def _ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    """会话首次出现时创建 _meta.json，并向 index.jsonl 追加一条。"""
    meta_path = os.path.join(session_dir, "_meta.json")
    if os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _format_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": os.path.relpath(session_dir, root),
                        "started_at": _format_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass

def _linkfox_root() -> str:
    """只使用当前工作目录；不可写即报错，不回退到其他位置。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write_probe-" + secrets.token_hex(6))
    with open(probe, "w", encoding="utf-8"):
        pass
    os.remove(probe)
    return root


def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))

def _session_id(ts: float) -> str:
    """优先 env SESSION_ID；缺省按 HHMMSS-<6 hex> 生成（同一进程内稳定）。"""
    env = os.environ.get("SESSION_ID")
    if env:
        return env.strip()
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = (
            time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
        )
    return _SESSION_CACHE["_auto"]

def _ensure_session(ts: float) -> tuple[str, str]:
    """返回 (linkfox_root, session_dir)；session_dir 一定存在。"""
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    sid = _session_id(ts)
    root = _linkfox_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir

def _update_meta(session_dir: str, *, skill: str, kind: str, file_rel: str, ts: float) -> None:
    """把本次输出写入 _meta.json 的对应分类列表。kind ∈ {data, deliverable, media}。"""
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    bucket = {"data": "data_files", "deliverable": "deliverables", "media": "media_files"}.get(
        kind, "data_files"
    )
    files = meta.setdefault(bucket, [])
    if file_rel not in files:  # 去重：并发或重复注册同一路径时不留重复条目
        files.append(file_rel)
    meta["last_used_at"] = _format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def resolve_data_path(slug: str, ts: float, ext: str = "json") -> str:
    """普通 skill 的原始数据落到 <session>/data/<slug>-<ts>.<ext>。"""
    _, session_dir = _ensure_session(ts)
    sub = os.path.join(session_dir, "data")
    os.makedirs(sub, exist_ok=True)
    out = os.path.join(sub, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, kind="data", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out

def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<日期>/<session>/data/<slug>-<ts>.json，按 SESSION_ID 聚合到同一会话。"""
    return resolve_data_path(SLUG, ts)


def main():
    argv = sys.argv[1:]
    inline = False
    use_cache = True
    if "--inline" in argv:
        inline = True
        argv = [a for a in argv if a != "--inline"]
    if "--no-cache" in argv:
        use_cache = False
        argv = [a for a in argv if a != "--no-cache"]
    if not argv:
        print(
            "用法: amazon_reviews.py '<JSON 参数>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        sys.exit(1)
    _ensure_session(time.time())
    cache_path, task_id, task_path, result = _load_task_state(params, use_cache)
    if (isinstance(result, dict) and result.get("error") and result.get("taskId")
            and _task_status(result) not in ("SUCCEEDED", "FAILED", "CANCELLED")
            and _is_retryable_poll_error(result)):
        # Resume the same task from a cached query error without submitting again.
        result = _async_task_marker(
            result["taskId"], result.get("provider"), status=None,
            submittedAt=_cache_timestamp(task_path + ".terminal.json", task_path, cache_path),
        )
    cache_hit = result is not None and not _is_async_task_marker(result)
    completed = False
    received_result = False

    if _is_received_task(result):
        result = _received_task_response(result)
    elif _is_async_task_marker(result):
        marker = result["_asyncTask"]
        result, completed = poll_async_once(
            marker["taskId"],
            marker.get("provider"),
            submitted_at=marker.get("submittedAt"),
        )
        received_result = completed and isinstance(result, dict) and not result.get("error")
        if use_cache:
            if not received_result:
                cached_result = result if completed or _is_async_task_marker(result) else {"_asyncTask": marker}
                if completed:
                    _save_terminal_task(task_path, cached_result)
                else:
                    _save_cache(task_path, cached_result)
    elif result is None:
        marker, task_id = submit_async(params)
        if task_id is None:
            result = marker
        else:
            task_path = _cache_path({"taskId": task_id})
            if use_cache:
                _save_cache(task_path, marker)
            result = marker

    if use_cache and task_id and cache_path != task_path:
        # 取消也保留原参数关联；只有明确重试并使用 --no-cache 才能创建新任务。
        existing = _load_cache(cache_path)
        if not isinstance(existing, dict) or existing.get("_asyncTaskRef") != task_id:
            _save_cache(cache_path, {"_asyncTaskRef": task_id})

    # 缓存结果中的费用属于历史消费；缺少 taskId 时也不能当作本次费用再次展示。
    if (cache_hit and isinstance(result, dict) and not result.get("error")
            and isinstance(result.get("data"), list)):
        result["costToken"] = 0  # Cached charges are historical, not a new expense.
        received_result = bool(task_id)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    # Preserve sub-second precision so a quick repeat cannot overwrite the result file.
    ts = time.time()
    out_path = None
    try:
        candidate_path = _resolve_output_path(ts)
        with open(candidate_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        out_path = os.path.abspath(candidate_path)
        print(f"Saved full response: {out_path} ({len(serialized)} bytes)")
        if cache_hit:
            print(f"Cache hit: {cache_path}")
    except OSError as e:
        print(f"Failed to save result: {e}", file=sys.stderr)
        inline = True  # The server already consumed the result; preserve it in stdout.

    if use_cache and task_id and received_result:
        _save_terminal_task(task_path, {"_asyncReceipt": {
            "taskId": task_id,
            "status": "SUCCEEDED",
            "resultFile": out_path,
            "receivedAt": ts,
        }})

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        if cache_hit:
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
