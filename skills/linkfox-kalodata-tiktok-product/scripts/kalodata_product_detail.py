#!/usr/bin/env python3
"""
Kalodata TikTok 商品榜单与详情 - LinkFox 技能
调用 /kalodata/product/detail 接口。

用法:
  python kalodata_product_detail.py '<JSON 参数>'           # 自动：小结果全量；大结果写文件+摘要
  python kalodata_product_detail.py '<JSON 参数>' --inline  # 强制全量打印到 stdout

输出策略（脚本默认行为）：
  - **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-kalodata-tiktok-product-<接口标识>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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
import call_api as shared_api


API_PATH = "/kalodata/product/detail"
SLUG = "linkfox-kalodata-tiktok-product"

# 响应小于等于该字节数时，落盘后全量输出
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60

_SESSION_CACHE: dict[str, str] = {}


def call_api(params):
    """复用公共 run 的请求和落盘，业务脚本独占缓存与最终展示。"""
    root = _linkfox_root()
    previous_session = shared_api._SESSION_CACHE.copy()
    previous_resolver = shared_api._resolve_output_path
    previous_caller = shared_api.call_api
    shared_api._SESSION_CACHE["_root"] = root
    shared_api._SESSION_CACHE["_auto"] = _session_id(time.time())
    _SESSION_CACHE.pop("_output_path", None)

    def resolve_output(slug, ts):
        # 公共 run 使用整秒时间；业务层保留微秒并检查已有路径，防止同秒覆盖。
        path = resolve_data_path(slug, time.time())
        _SESSION_CACHE["_output_path"] = path
        return path

    def call_with_status(api_path, body):
        http_status, payload = previous_caller(api_path, body)
        if isinstance(payload, dict):
            payload = {**payload, "_http_status": http_status}
        return http_status, payload

    shared_api._resolve_output_path = resolve_output
    shared_api.call_api = call_with_status
    captured = io.StringIO()
    try:
        with redirect_stdout(captured):
            shared_api.run(API_PATH, _output_slug(), [
                json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"
            ])
    finally:
        shared_api.call_api = previous_caller
        shared_api._resolve_output_path = previous_resolver
        shared_api._SESSION_CACHE.clear()
        shared_api._SESSION_CACHE.update(previous_session)

    saved = _SESSION_CACHE.get("_output_path")
    if saved and os.path.isfile(saved):
        try:
            with open(saved, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    # 公共调用器落盘失败时只有 JSON 输出；外层仍会再次尝试同一路径。
    output = captured.getvalue()
    if output.startswith("Saved full response: "):
        output = output.partition("\n")[2]
    return json.loads(output)


def _cache_key(params):
    raw = json.dumps({"api_path": API_PATH, "params": params}, ensure_ascii=False, sort_keys=True)
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
            payload.setdefault("_cache", {})["hit"] = True
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
        print(f"响应类型: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"顶层字段: {list(result.keys())}")

    for k in ("_http_status", "errcode", "errorCode", "code", "errmsg", "msg", "error",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costToken", "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        print(f"\n主列表字段: `{list_path}` (条数={len(main_list)})")
        sample = main_list[:3]
        print(f"样本（前 {len(sample)} 条 / 共 {len(main_list)} 条）:")
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
    """只使用当前目录，不回退到家目录或临时目录。"""
    cwd = os.getcwd()
    normalized = cwd.replace("\\", "/").rstrip("/")
    if normalized == "/tmp" or normalized.startswith("/tmp/"):
        raise PermissionError("按技能约定，禁止将响应写入 /tmp；请切换到项目目录")
    root = os.path.abspath(os.path.join(cwd, "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write-probe-" + secrets.token_hex(6))
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
    stamp = int(ts * 1_000_000)
    out = os.path.join(sub, f"{slug}-{stamp}.{ext}")
    while os.path.exists(out):
        stamp += 1
        out = os.path.join(sub, f"{slug}-{stamp}.{ext}")
    _update_meta(session_dir, skill=SLUG, kind="data", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out

def _output_slug():
    """区分榜单与详情，避免同秒归档互相覆盖。"""
    return SLUG + "-" + API_PATH.rsplit("/", 1)[-1]


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<日期>/<session>/data/<slug>-<ts>.json，按 SESSION_ID 聚合到同一会话。"""
    saved = _SESSION_CACHE.pop("_output_path", None)
    return saved or resolve_data_path(_output_slug(), ts)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
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
            "用法: kalodata_product_detail.py '<JSON 参数>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"JSON 参数格式无效: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(params, dict):
        print("JSON 参数必须是对象", file=sys.stderr)
        sys.exit(1)

    _linkfox_root()  # 请求前确认当前目录可写，失败时不产生付费调用。
    cache_path = _cache_path(params)
    result = _load_cache(cache_path) if use_cache else None
    if result is None:
        result = call_api(params)
        if use_cache:
            _save_cache(cache_path, result)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = time.time()
    out_path = _resolve_output_path(ts)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"已保存完整响应: {out_path} ({len(serialized.encode('utf-8'))} 字节)")
        if result.get("_cache", {}).get("hit"):
            print(f"缓存命中: {cache_path}")
    except OSError as e:
        print(f"无法保存到 {out_path}: {e}", file=sys.stderr)

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        if result.get("_cache", {}).get("hit"):
            print(f"缓存命中: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
