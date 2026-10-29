#!/usr/bin/env python3
"""
EchoTik 三级商品类目 - LinkFox Skill
调用 /echotik/category/l3 接口。

Usage:
  python echotik_category_l3.py '<JSON parameters>'           # 自动：小结果全量；大结果写文件+摘要
  python echotik_category_l3.py '<JSON parameters>' --inline  # 强制全量打印到 stdout

输出策略（脚本默认行为）：
  - **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-echotik-category-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
  - 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
  - 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
  - 加 `--inline` 强制全量打印到 stdout（同样落盘）
"""

import json
from decimal import Decimal, InvalidOperation
import hashlib
import os
import sys
import time
import secrets
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from xml.etree import ElementTree


API_PATH = "/echotik/category/l3"
SLUG = "linkfox-echotik-category"

# 小结果落盘后全量输出，大结果落盘后输出摘要
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_LAST_CALL_WAS_HTTP_ERROR = False

_SESSION_CACHE: dict[str, str] = {}

def get_api_base() -> str:
    """网关基础地址：env LINKFOX_TOOL_GATEWAY 优先，缺省回退正式地址。"""
    return (os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")

def get_api_url():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared"))
    return get_api_base() + API_PATH


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


def _decode_gateway_response(body, http_status=None, reason=None):
    """Parse JSON responses and normalize gateway ToolErrorResponse XML."""
    if body:
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            try:
                root = ElementTree.fromstring(body)
                if root.tag.rsplit("}", 1)[-1] == "ToolErrorResponse":
                    fields = {
                        child.tag.rsplit("}", 1)[-1]: (child.text or "")
                        for child in root
                    }
                    code = fields.get("errcode")
                    if code is not None:
                        try:
                            code = int(code)
                        except ValueError:
                            pass
                    return {"errcode": code, "errmsg": fields.get("errmsg", "")}
            except ElementTree.ParseError:
                pass

    if http_status is not None:
        label = f"HTTP {http_status}"
        if reason:
            label += f": {reason}"
        result = {"error": label}
    else:
        result = {"error": "Invalid gateway response format"}
    if body:
        result["details"] = "Gateway returned a non-JSON/non-XML response"
    return result


def _attach_gateway_cost_headers(result, headers):
    """Expose gateway billing headers in the normalized JSON result."""
    if not isinstance(result, dict) or headers is None:
        return result
    for header, field in (
        ("X-Cost-Token", "costToken"),
        ("X-Cost-Credit", "costCredit"),
    ):
        value = headers.get(header)
        if value is None:
            continue
        try:
            value = int(value)
        except (TypeError, ValueError):
            pass
        # The gateway headers are the authoritative values for this request.
        result[field] = value
    return result


def _request_headers():
    """Validate header configuration without exposing credential values."""
    headers = {
        "Authorization": get_api_key(),
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }
    for name, value in headers.items():
        if "\r" in value or "\n" in value:
            raise ValueError(f"{name} must not contain CR or LF")
        try:
            value.encode("latin-1")
        except UnicodeEncodeError:
            raise ValueError(f"{name} must be encodable as a Latin-1 HTTP header") from None
    return headers


def call_api(params):
    global _LAST_CALL_WAS_HTTP_ERROR
    _LAST_CALL_WAS_HTTP_ERROR = False
    api_url = get_api_url()
    data = json.dumps(params).encode("utf-8")
    headers = _request_headers()
    req = Request(
        api_url,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(req, timeout=150) as response:
            body = response.read().decode("utf-8")
            result = _decode_gateway_response(body)
            return _attach_gateway_cost_headers(result, response.headers)
    except HTTPError as e:
        _LAST_CALL_WAS_HTTP_ERROR = True
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        result = _decode_gateway_response(body, e.code, e.reason)
        return _attach_gateway_cost_headers(result, e.headers)
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except TimeoutError:
        return {"error": "Connection timed out"}
    except UnicodeError:
        return {"error": "Invalid UTF-8 gateway response"}


def _cache_key(params):
    identity = hashlib.sha256(get_api_key().encode("utf-8")).hexdigest()
    raw = json.dumps({"gateway": get_api_base(), "endpoint": API_PATH,
                      "identity": identity, "params": params},
                     ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


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
        if not _is_success_result(payload):
            return None
        if isinstance(payload, dict):
            if not isinstance(payload.get("_cache"), dict):
                payload["_cache"] = {}
            payload["_cache"]["hit"] = True
        return payload
    except (OSError, UnicodeError, json.JSONDecodeError):
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
              "costToken", "costCredit", "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        sample_text = json.dumps(sample, indent=2, ensure_ascii=False)
        print(sample_text[:4000])
        if len(sample_text) > 4000:
            print("Sample truncated; read the saved JSON for complete fields.")

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
    """Only write below the caller's current working directory; never silently fall back."""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    return root


def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))

def _session_id(ts: float) -> str:
    value = (os.environ.get("SESSION_ID") or "").strip()
    if value:
        if value in (".", "..") or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-" for c in value) or len(value) > 128:
            value = "session-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]
        return value
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
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
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared"))
    return resolve_data_path(SLUG, ts)


def _is_success_result(result):
    if not isinstance(result, dict) or result.get("error") or result.get("success") is False:
        return False
    if "errcode" in result and str(result["errcode"]) != "200":
        return False
    if "code" in result and str(result["code"]) != "0":
        return False
    if not isinstance(result.get("data"), list):
        return False
    token = result.get("costToken")
    if type(token) not in (int, str):
        return False
    try:
        amount = Decimal(token)
        return amount.is_finite() and amount >= 0
    except InvalidOperation:
        return False


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if len(argv) != 1:
        print("Usage: echotik_category_l3.py '<JSON parameters>' [--inline] [--no-cache]", file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(argv[0])
        if not isinstance(params, dict):
            raise ValueError("top-level JSON must be an object")
    except ValueError as error:
        print(f"Invalid parameter format: {error}", file=sys.stderr)
        sys.exit(1)
    try:
        _request_headers()
    except ValueError as error:
        print(f"Invalid request header configuration: {error}", file=sys.stderr)
        sys.exit(1)
    try:
        cache_path = _cache_path(params) if use_cache else None
        out_path = _resolve_output_path(time.time())
        # Prove that the result can be persisted before making a paid network request.
        with open(out_path, "x", encoding="utf-8"):
            pass
        result = _load_cache(cache_path) if cache_path else None
        cache_hit = result is not None
        if result is None:
            result = call_api(params)
            if cache_path and not _LAST_CALL_WAS_HTTP_ERROR and _is_success_result(result):
                _save_cache(cache_path, result)
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        with open(out_path, "w", encoding="utf-8", newline="\n") as output:
            output.write(serialized)
    except OSError as error:
        print(f"Failed to persist response in the current working directory: {error}", file=sys.stderr)
        sys.exit(1)
    print(f"Saved full response: {out_path} ({len(serialized.encode('utf-8'))} bytes)")
    if cache_hit:
        print(f"Cache hit: {cache_path}")
    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)
    if _LAST_CALL_WAS_HTTP_ERROR or not _is_success_result(result):
        sys.exit(2)


if __name__ == "__main__":
    main()
