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
  - 失败（网络错误 / HTTP 或业务错误 / status==FAILED）时退出码非 0，agent 可凭退出码判错。

默认行为：
  - 响应体 <= SMALL_THRESHOLD 字节：完整响应 JSON 打印到 stdout
  - 所有结果始终落盘；响应体较大时写入 <cwd>/linkfox/<YYYY-MM-DD>/.../linkfox-aigc-textgen-<timestamp>.json，stdout 输出 JSON 信封

换行符压平（默认开启，无需任何 flag）：
  无论哪种输出模式，content 中的换行都会统一替换为单字符占位符 ⏎（U+23CE），
  同时覆盖两种形态：真实换行控制符（\r\n / \r / \n）与字面量两字符转义序列（\n / \r\n / \r）。
  该字符在 shell 单引号和 JSON 字符串中均无需转义，可安全捕获进变量并内联拼接进下游参数 JSON。
  下游脚本会自动把 ⏎ 还原为真实换行符（decode_nl），因此文本无损传递。
"""

import json
import sys
import time
from _runtime import run_json, response_failed, retryable, session_id


CREATE_PATH = "/aigc/textGenAsync"
QUERY_PATH = "/aigc/textTaskQuery"
SLUG = "linkfox-aigc-textgen"
POLL_INTERVAL_START = 10
POLL_INTERVAL_MIN = 5
POLL_INTERVAL_STEP = 1
MAX_POLL_TIME = 600
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
import time as _lf_time

NL_PLACEHOLDER = "⏎"


def get_api_base():
    """网关基础地址：env LINKFOX_TOOL_GATEWAY 优先，缺省回退正式地址。"""
    return (_lf_os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")


def _lf_format_iso(ts):
    return _lf_time.strftime("%Y-%m-%dT%H:%M:%S%z", _lf_time.localtime(ts))


def _lf_session_id(ts):
    return session_id(ts)


def _lf_linkfox_root():
    """按金例要求在当前工作目录落盘，不静默回退。"""
    root = _lf_os.path.abspath(_lf_os.path.join(_lf_os.getcwd(), "linkfox"))
    _lf_os.makedirs(root, exist_ok=True)
    return root


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


def _post(url, params):
    base = get_api_base()
    path = url[len(base):] if url.startswith(base) else url
    operation = "create" if path == CREATE_PATH else "query"
    try:
        return run_json(path, params, f"{SLUG}-{operation}")
    except (OSError, ValueError, RuntimeError) as exc:
        return {"error": str(exc), "localError": True}


def _payload(result):
    if not isinstance(result, dict):
        return {}
    for key in ("data", "result"):
        if isinstance(result.get(key), dict):
            return result[key]
    return result


def create_task(params):
    return _post(get_api_base() + CREATE_PATH, params)


def query_task(task_id, member_id):
    return _post(get_api_base() + QUERY_PATH, {"taskId": task_id, "memberId": member_id})


def poll_until_done(task_id, member_id):
    start = time.monotonic()
    interval = POLL_INTERVAL_START
    failures = 0
    while time.monotonic() - start < MAX_POLL_TIME:
        time.sleep(min(interval, max(0, MAX_POLL_TIME - (time.monotonic() - start))))
        if time.monotonic() - start >= MAX_POLL_TIME:
            break
        result = query_task(task_id, member_id)
        result.setdefault("taskId", task_id)
        if _is_failure(result):
            if retryable(result) and failures < 3:
                failures += 1
                print(f"查询失败，保留 taskId={task_id}，重试 {failures}/3：{result}", file=sys.stderr)
                interval = max(interval - POLL_INTERVAL_STEP, POLL_INTERVAL_MIN)
                continue
            return result
        if _payload(result).get("status") in ("SUCCESS", "FAILED", 4):
            return result
        elapsed = int(time.monotonic() - start)
        print(f"查询中：taskId={task_id}, status={_payload(result).get('status')}, elapsed={elapsed}s", file=sys.stderr)
        interval = max(interval - POLL_INTERVAL_STEP, POLL_INTERVAL_MIN)
    return {"error": f"轮询超过 {MAX_POLL_TIME} 秒；可用 taskId 恢复查询", "taskId": task_id}


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
    if response_failed(result):
        return True
    return result.get("status") in (4, "FAILED") or _payload(result).get("status") in (4, "FAILED")


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

    remaining = [a for a in argv if a not in ("--inline", "--content-only", "--no-cache")]
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
    if "--help" in argv or "-h" in argv:
        print("用法：aigc_textgen.py '<JSON>' [--inline] [--content-only] [--no-cache]\n"
              "      aigc_textgen.py --stdin [--inline] [--content-only]\n"
              "仅查询已有任务：JSON 传 taskId 和可选 memberId；始终禁用响应缓存。")
        return
    inline = "--inline" in argv
    content_only = "--content-only" in argv
    params = _decode_params(_read_params(argv))
    if not isinstance(params, dict):
        print("JSON 参数必须是对象", file=sys.stderr)
        sys.exit(1)
    member_id = params.get("memberId", "")
    task_id = params.get("taskId")
    if task_id:
        result = poll_until_done(task_id, member_id)
    else:
        create_result = create_task(params)
        task_id = _payload(create_result).get("taskId")
        if _is_failure(create_result) or not task_id:
            result = create_result
            if not _is_failure(result):
                result = dict(result, error="创建响应缺少 taskId")
        else:
            print(f"任务已创建：taskId={task_id}", file=sys.stderr)
            result = poll_until_done(task_id, member_id)
    if task_id:
        result.setdefault("taskId", task_id)
    _encode_content_in_result(result)
    failed = _is_failure(result)
    # SUCCESS 的空内容不作为可用文本交付；保留原响应和任务标识。
    if _payload(result).get("status") == "SUCCESS" and not _extract_content(result):
        result["error"] = "任务返回空内容；请核查媒体可读性或考虑视频抽帧"
        failed = True
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    try:
        out_path = _resolve_output_path(time.time())
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized.encode('utf-8'))} bytes)", file=sys.stderr)
    except OSError as exc:
        print(f"响应保存失败：{exc}", file=sys.stderr)
        sys.exit(1)
    if content_only:
        content = _extract_content(result)
        if failed or not isinstance(content, str):
            print(serialized, file=sys.stderr)
            sys.exit(1)
        print(content)
    elif inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
        if _extract_content(result) is not None:
            print("# CHAIN-HINT: content 换行已编码为 ⏎；下游参数请用 JSON 编码器构造。", file=sys.stderr)
    else:
        print(json.dumps({
            "ok": not failed, "truncated": True, "savedPath": out_path,
            "bytes": len(serialized.encode("utf-8")), "content": _extract_content(result),
        }, ensure_ascii=False))
        summarize(result)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
