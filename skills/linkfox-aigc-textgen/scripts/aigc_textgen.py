#!/usr/bin/env python3
"""
AI生文 - LinkFox Skill (异步模式)
调用 aigc/textGenAsync 创建任务，然后轮询 aigc/textTaskQuery 获取结果。

Usage:
  python aigc_textgen.py '<JSON parameters>'                  # 自动：小结果全量；大结果写文件+摘要
  python aigc_textgen.py --stdin                              # 从 stdin 读取 JSON 参数
  python aigc_textgen.py '<JSON parameters>' --inline         # 强制全量打印到 stdout
  python aigc_textgen.py --stdin --content-only               # 只输出 content 文本（同样已是单行）

输出契约（面向被其他 agent 调用）：
  - stdout 只放机器数据：默认/--inline 为完整响应 JSON；大结果为 JSON 信封 {ok, truncated, savedPath, bytes, content}；
    --content-only 例外（stdout 为纯文本 content）。
  - 所有提示/摘要/诊断（CHAIN-HINT、Saved full response、summarize）一律走 stderr，stdout 始终可 json.loads。
  - 失败（网络错误 / errcode 非 200 / status==FAILED）时退出码非 0，agent 可凭退出码判错。

默认行为：
  - 响应体 <= SMALL_THRESHOLD 字节：完整响应 JSON 打印到 stdout
  - 响应体较大：写入 <cwd>/linkfox/<YYYY-MM-DD>/.../linkfox-aigc-textgen-<timestamp>.json，stdout 输出 JSON 信封

换行符压平（默认开启，无需任何 flag）：
  无论哪种输出模式，content 中的换行都会统一替换为单字符占位符 ⏎（U+23CE），
  同时覆盖两种形态：真实换行控制符（\r\n / \r / \n）与字面量两字符转义序列（\n / \r\n / \r）。
  该字符在 shell 单引号和 JSON 字符串中均无需转义，可安全捕获进变量并内联拼接进下游参数 JSON。
  下游脚本会自动把 ⏎ 还原为真实换行符（decode_nl），因此文本无损传递。
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


CREATE_PATH = "/aigc/textGenAsync"
QUERY_PATH = "/aigc/textTaskQuery"
SLUG = "linkfox-aigc-textgen"
POLL_INTERVAL_START = 10
POLL_INTERVAL_MIN = 5
POLL_INTERVAL_STEP = 1
MAX_POLL_TIME = 600
HTTP_TIMEOUT = 120
SMALL_THRESHOLD = 8000


def _encode_nl(text):
    """把 content 内真实换行符压平为单字符占位符 ⏎，供链式调用安全传递（复用共享实现）。"""
    return encode_nl(text)


def _decode_params(params):
    """入参解码：把上游 --content-only 注入的换行符占位符 ⏎ 还原为真实换行符。"""
    return decode_nl_in_obj(params)


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
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://skill.linkfox.com/linkfoxskills/guide.htm to obtain your Key\n"
            "2. Set the environment variable: export LINKFOX_AGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def _post(url, params):
    api_key = get_api_key()
    data = json.dumps(params, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }
    req = Request(url, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=HTTP_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            return json.loads(body) if body else {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception:
            return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def create_task(params):
    return _post(get_api_base() + CREATE_PATH, params)


def query_task(task_id, member_id):
    return _post(get_api_base() + QUERY_PATH, {"taskId": task_id, "memberId": member_id})


def poll_until_done(task_id, member_id):
    start = time.time()
    interval = POLL_INTERVAL_START
    while time.time() - start < MAX_POLL_TIME:
        time.sleep(interval)
        result = query_task(task_id, member_id)
        if result.get("error"):
            print(f"  Poll error: {result['error']}", file=sys.stderr)
            interval = max(interval - POLL_INTERVAL_STEP, POLL_INTERVAL_MIN)
            continue
        status = result.get("status")
        if status == "SUCCESS":
            return result
        if status == "FAILED":
            return result
        elapsed = int(time.time() - start)
        print(f"  Polling... status={status}, elapsed={elapsed}s, next in {interval}s", file=sys.stderr)
        interval = max(interval - POLL_INTERVAL_STEP, POLL_INTERVAL_MIN)
    return {"error": f"Polling timeout after {MAX_POLL_TIME}s", "taskId": task_id}


def _find_main_list(obj):
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
    """人类可读摘要——全部输出到 stderr，保持 stdout 干净可解析。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False)[:500], file=sys.stderr)
        return

    print(f"Top-level keys: {list(result.keys())}", file=sys.stderr)

    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "costTime", "success", "status"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}", file=sys.stderr)

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})", file=sys.stderr)
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):", file=sys.stderr)
        print(json.dumps(sample, indent=2, ensure_ascii=False), file=sys.stderr)


def _extract_content(result):
    """从响应中提取 content 字段，支持 data.content 和顶层 content 两种路径。"""
    if not isinstance(result, dict):
        return None
    data = result.get("data") or result.get("result")
    if isinstance(data, dict) and "content" in data:
        return data["content"]
    return result.get("content")


def _is_failure(result):
    """判定本次调用是否失败，供退出码使用。"""
    if not isinstance(result, dict):
        return True
    if "error" in result:
        return True
    for code_key in ("errcode", "errorCode", "code"):
        if code_key in result and result[code_key] not in (200, "200", None):
            return True
    data = result.get("data") if isinstance(result.get("data"), dict) else {}
    if result.get("status") in (4, "FAILED") or data.get("status") in (4, "FAILED"):
        return True
    return False


def _encode_content_in_result(result):
    """默认在原地把 result 里的 content 换行压平成单字符 ⏎。"""
    if not isinstance(result, dict):
        return result
    data = result.get("data") or result.get("result")
    if isinstance(data, dict) and "content" in data:
        data["content"] = _encode_nl(data["content"])
    elif "content" in result:
        result["content"] = _encode_nl(result["content"])
    return result


def _resolve_output_path(ts):
    return resolve_data_path(SLUG, ts)


def _read_params(argv):
    if "--stdin" in argv:
        raw = sys.stdin.read()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)

    remaining = [a for a in argv if a not in ("--inline", "--content-only")]
    if not remaining:
        print(
            "Usage: aigc_textgen.py '<JSON>' [--inline]\n"
            "       aigc_textgen.py --stdin [--inline]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        return json.loads(remaining[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    content_only = "--content-only" in argv

    params = _decode_params(_read_params(argv))
    member_id = params.get("memberId", "")

    create_result = create_task(params)
    if create_result.get("error"):
        print(json.dumps(create_result, ensure_ascii=False))
        sys.exit(1)

    task_id = create_result.get("taskId")
    if not task_id:
        print(json.dumps(create_result, ensure_ascii=False))
        sys.exit(1)

    print(f"Task created: taskId={task_id}", file=sys.stderr)

    result = poll_until_done(task_id, member_id)

    _encode_content_in_result(result)
    failed = _is_failure(result)

    if content_only:
        content = _extract_content(result)
        if content is None:
            print("ERROR: content field not found in response", file=sys.stderr)
            print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
            sys.exit(1)
        sys.stdout.write(content)
        sys.stdout.write("\n")
        sys.exit(1 if failed else 0)

    if inline:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1 if failed else 0)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)

    if len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
        if _extract_content(result) is not None:
            print(
                "# CHAIN-HINT: content 已压平为单行（换行=⏎），可直接提取后内联拼接进下游参数 JSON；"
                "也可用 --content-only 只取文本。下游脚本接收后会自动把 ⏎ 还原为换行符。",
                file=sys.stderr,
            )
        sys.exit(1 if failed else 0)

    ts = int(time.time())
    out_path = _resolve_output_path(ts)
    saved_path = None
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        saved_path = out_path
        print(f"Saved full response: {out_path} ({len(serialized)} bytes)", file=sys.stderr)
    except OSError as e:
        print(f"Failed to save to {out_path}: {e}", file=sys.stderr)

    envelope = {
        "ok": not failed,
        "truncated": True,
        "savedPath": saved_path,
        "bytes": len(serialized),
        "content": _extract_content(result),
    }
    print(json.dumps(envelope, ensure_ascii=False))
    summarize(result)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
