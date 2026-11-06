#!/usr/bin/env python3
"""
SP 搜索词展示份额报告 - LinkFox Skill
调用 /amazonAds/developerProxy 接口。

Usage:
  python get_sp_search_impression_share.py '<JSON parameters>'           # 自动：小结果全量；大结果写文件+摘要
  python get_sp_search_impression_share.py '<JSON parameters>' --inline  # 强制全量打印到 stdout
  python get_sp_search_impression_share.py '<JSON parameters>' --no-cache # 跳过 24h 成功结果缓存

输出策略（脚本默认行为）：
  - **始终**将完整响应写入 `<根>/<YYYY-MM-DD>/<session>/data/linkfox-amazon-ads-sp-insights-report-<timestamp>.json`；根目录优先为 `ACPX_WORKSPACES` 第一个路径下的 `linkfox/`，其次为 `<cwd>/linkfox/`，均不可写则报错，不回退家目录或系统临时目录。会话标识优先由 `SESSION_ID` 清理生成，未设置时自动生成并在进程内稳定。
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
import subprocess
from pathlib import Path

from reporting_v1_workflow import run_report_workflow
from _linkfox_transport import invoke_proxy


SLUG = "linkfox-amazon-ads-sp-insights-report"
REPORT_KIND = "search-impression-share"
REQUIRED_SKILL = "linkfox-amazon-ads-auth"
DEPENDENCY_EXIT_CODE = 42

# 响应小于等于该字节数时，落盘后全量输出
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60

_SESSION_CACHE: dict[str, str] = {}


def ensure_auth_skill_available():
    """Use the same local dependency guard as the existing Amazon Ads skills."""
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    if not checker.exists():
        print(
            "DEPENDENCY_MISSING: " + json.dumps({
                "missingSkill": REQUIRED_SKILL,
                "reason": "check_auth_dependency.py not found next to the entry script",
            }, ensure_ascii=False),
            file=sys.stderr,
        )
        sys.exit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run(
            [sys.executable, str(checker)], capture_output=True, text=True, timeout=10
        )
    except Exception as exc:
        print(
            "DEPENDENCY_MISSING: " + json.dumps({
                "missingSkill": REQUIRED_SKILL,
                "reason": "Failed to run dependency check: %s" % exc,
            }, ensure_ascii=False),
            file=sys.stderr,
        )
        sys.exit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        sys.exit(DEPENDENCY_EXIT_CODE)


def call_api(params):
    """保留业务缓存，通过公共调用器执行每个 LinkFox 操作。"""
    return invoke_proxy(params, resolve_data_path, SLUG)


def _cache_key(params):
    raw = json.dumps({"reportKind": REPORT_KIND, "params": params}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG, _cache_session_id())
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _cache_session_id():
    """Keep caches isolated by explicit session while remaining stable across CLI processes."""
    raw = (os.environ.get("SESSION_ID") or "default").strip() or "default"
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in raw)[:80]
    return safe if safe and safe not in (".", "..") else "default"


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, dict) or payload.get("success") is not True:
            return None
        if payload.get("_cacheable") is False or not isinstance(payload.get("dataFiles"), list):
            return None
        for item in payload["dataFiles"]:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                return None
            if not os.path.isfile(item["path"]):
                return None
        payload["_cache"] = {"hit": True}
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


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
    """选择可写的 linkfox 根目录。

    优先级：$ACPX_WORKSPACES 第一个路径下的 linkfox/，其次为当前工作目录下的 linkfox/。
    两处均不可写时明确报错，不回退到家目录或系统临时目录。
    选定结果在进程内缓存，保证同一次运行内所有落盘路径稳定一致。
    """
    cached = _SESSION_CACHE.get("_root")
    if cached:
        return cached
    candidates = []
    # 1. ACPX_WORKSPACES（真实的工作目录，优先级最高）
    acpx = (os.environ.get("ACPX_WORKSPACES") or "").strip()
    if acpx:
        acpx = acpx.split(os.pathsep)[0].strip()
        if acpx:
            candidates.append(os.path.join(acpx, "linkfox"))
    # 2. 当前工作目录
    candidates.append(os.path.join(os.getcwd(), "linkfox"))
    for root in candidates:
        try:
            os.makedirs(root, exist_ok=True)
            probe = os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("")
            os.remove(probe)
        except OSError:
            continue
        root = os.path.abspath(root)
        _SESSION_CACHE["_root"] = root
        return root
    raise OSError("No writable workspace directory available for LinkFox outputs")

def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))

def _session_id(ts: float) -> str:
    """优先 env SESSION_ID；缺省按 HHMMSS-<6 hex> 生成（同一进程内稳定）。"""
    env = os.environ.get("SESSION_ID")
    if env:
        raw = env.strip()
        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in raw)[:80]
        if safe and safe not in (".", ".."):
            return safe
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
    """落到所选工作区根目录的 <日期>/<session>/data/，会话标识由 _session_id 解析。"""
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
            "Usage: get_sp_search_impression_share.py '<JSON parameters>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    ensure_auth_skill_available()
    # 在发起请求前确认业务输出目录可写，不允许公共调用器回退到临时目录。
    _ensure_session(time.time())

    cache_path = _cache_path(params)
    result = _load_cache(cache_path) if use_cache else None
    if result is None:
        result = run_report_workflow(params, call_api, resolve_data_path, REPORT_KIND, SLUG)
        if use_cache and result.get("_cacheable", True):
            _save_cache(cache_path, result)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = time.time()
    out_path = _resolve_output_path(ts)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized)} bytes)")
        if result.get("_cache", {}).get("hit"):
            print(f"Cache hit: {cache_path}")
    except OSError as e:
        print(f"Failed to save to {out_path}: {e}", file=sys.stderr)

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        if result.get("_cache", {}).get("hit"):
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
