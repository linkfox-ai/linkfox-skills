#!/usr/bin/env python3
"""
Google AI Search - LinkFox Skill
调用 /aiMode/googleSearch 接口。

用法:
  python google_ai_search.py '<JSON 参数>' [--no-cache]  # 自动：小结果全量；大结果写文件+摘要
  python google_ai_search.py '<JSON 参数>' --inline  # 强制全量打印到 stdout

输出策略（脚本默认行为）：
  - **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ai-mode-google-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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
import io
from contextlib import redirect_stdout

import call_api as _api


API_PATH = "/aiMode/googleSearch"
SLUG = "linkfox-ai-mode-google-search"

# 响应小于等于该字节数时，落盘后全量输出
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60

_SESSION_CACHE: dict[str, str] = {}


def call_api(params, out_path=None):
    """通过公共 run 调用一次；禁用其缓存，复用业务输出路径。"""
    out_path = out_path or _resolve_output_path(time.time())
    resolver = _api._resolve_output_path
    cache_path = _api._cache_path
    try:
        # run 无返回值，因此从其 UTF-8 落盘文件取得原始响应。
        # 路径由业务封装预先验证，避免公共脚本回退到其他目录。
        _api._resolve_output_path = lambda slug, ts: out_path
        # 公共 run 即使收到 --no-cache 也会先创建缓存目录。
        # 此处路径不会被读取或写入，避免禁用缓存时仍依赖缓存目录权限。
        _api._cache_path = lambda slug, params: ''
        with redirect_stdout(io.StringIO()):
            _api.run(API_PATH, SLUG, argv=[
                json.dumps(params, ensure_ascii=False), '--inline', '--no-cache'
            ])
    finally:
        _api._resolve_output_path = resolver
        _api._cache_path = cache_path
    with open(out_path, encoding='utf-8') as handle:
        return json.load(handle)


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            if not isinstance(payload.get("_cache"), dict):
                payload["_cache"] = {}
            payload["_cache"]["hit"] = True
        return payload
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
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
        print(f"响应类型: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"顶层字段: {list(result.keys())}")

    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costToken", "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        print(f"\n最大列表字段: `{list_path}` (长度={len(main_list)})")
        sample = main_list[:3]
        print(f"样本（共 {len(main_list)} 条中的前 {len(sample)} 条）:")
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
    """严格使用当前工作目录；不可写时由调用者报错，不回退。"""
    cwd = os.getcwd()
    if cwd == '/tmp' or cwd.startswith('/tmp/'):
        raise OSError('不能将会话数据写入 /tmp，请从项目目录运行')
    root = os.path.abspath(os.path.join(cwd, 'linkfox'))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, '.write_probe-' + secrets.token_hex(6))
    with open(probe, 'w', encoding='utf-8'):
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
    usage = "用法: google_ai_search.py '<JSON 参数>' [--inline] [--no-cache]"
    if '--help' in argv or '-h' in argv:
        print(usage)
        print('完整响应始终落盘；默认启用 24 小时缓存，超过 8000 字节仅输出摘要。')
        return
    inline = '--inline' in argv
    use_cache = '--no-cache' not in argv
    argv = [a for a in argv if a not in ('--inline', '--no-cache')]
    if not argv:
        print(usage, file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f'参数 JSON 格式错误: {exc}', file=sys.stderr)
        sys.exit(1)

    # 请求前建立并验证归档文件，目录不可写时不产生收费请求。
    try:
        out_path = _resolve_output_path(time.time())
        with open(out_path, 'w', encoding='utf-8'):
            pass
        cache_path = _cache_path(params) if use_cache else None
        result = _load_cache(cache_path) if use_cache else None
        if result is None:
            result = call_api(params, out_path)
            if use_cache:
                _save_cache(cache_path, result)
        else:
            with open(out_path, 'w', encoding='utf-8') as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f'无法保存当前目录的会话数据: {exc}', file=sys.stderr)
        sys.exit(1)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f'接口响应或归档文件不是有效的 UTF-8 JSON: {exc}；不自动重试请求。', file=sys.stderr)
        sys.exit(1)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    print(f'完整响应已保存: {out_path} ({len(serialized.encode("utf-8"))} bytes)')
    cache_hit = isinstance(result, dict) and result.get('_cache', {}).get('hit')
    if cache_hit:
        print(f'缓存命中: {cache_path}')
    if inline or len(serialized.encode('utf-8')) <= SMALL_THRESHOLD:
        if cache_hit:
            print(f'缓存命中: {cache_path}', file=sys.stderr)
        print(serialized)
    else:
        summarize(result)


if __name__ == '__main__':
    main()
