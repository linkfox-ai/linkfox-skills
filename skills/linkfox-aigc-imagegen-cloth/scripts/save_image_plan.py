#!/usr/bin/env python3
"""imagePlanList 增量落盘到会话 data/（抗上下文压缩，避免 S3 凭记忆 Write 大 JSON）。"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time


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


def _session_datadir() -> str:
    return os.path.join(session_root(time.time()), "data")


def _load_plan(path: str) -> dict:
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"imagePlanList": []}


def _save_plan(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Save imagePlanList to session data/")
    parser.add_argument("--datadir", action="store_true", help="Print session data/ path and exit")
    parser.add_argument("--init", action="store_true", help="Create empty image-plan.json")
    parser.add_argument("--out", help="Plan file path (default: <datadir>/image-plan.json)")
    parser.add_argument("--input", help="Replace full plan from JSON file")
    parser.add_argument("--stdin", action="store_true", help="Replace full plan from stdin JSON")
    parser.add_argument("--append-task-file", help="Append one task object from JSON file")
    args = parser.parse_args()

    if args.datadir:
        print(_session_datadir())
        return 0

    out = os.path.abspath(args.out or os.path.join(_session_datadir(), "image-plan.json"))

    if args.init:
        _save_plan(out, {"imagePlanList": []})
        print(f"Saved full response: {out}")
        return 0

    if args.input or args.stdin:
        if args.stdin:
            payload = json.load(sys.stdin)
        else:
            with open(os.path.abspath(args.input), encoding="utf-8") as f:
                payload = json.load(f)
        if not isinstance(payload.get("imagePlanList"), list):
            print("ERROR: JSON 须含 imagePlanList 数组", file=sys.stderr)
            return 1
        _save_plan(out, payload)
        print(f"Saved full response: {out} ({len(payload['imagePlanList'])} tasks)")
        return 0

    if args.append_task_file:
        tf = os.path.abspath(args.append_task_file)
        if not os.path.isfile(tf):
            print(f"ERROR: task 文件不存在: {tf}", file=sys.stderr)
            return 1
        with open(tf, encoding="utf-8") as f:
            task = json.load(f)
        if not isinstance(task, dict) or not task.get("type"):
            print("ERROR: task JSON 须为含 type 字段的对象", file=sys.stderr)
            return 1
        payload = _load_plan(out)
        payload.setdefault("imagePlanList", []).append(task)
        _save_plan(out, payload)
        print(f"Saved full response: {out} ({len(payload['imagePlanList'])} tasks)")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
