#!/usr/bin/env python3
"""
SIF 外观专利检测 - LinkFox Skill
调用 /ecDw/designSimilarSearch 接口。

Usage:
  python ec_dw_design_similar_search.py --params-file request.json  # UTF-8 JSON 文件，可用于 Base64 图片
  python ec_dw_design_similar_search.py '<JSON parameters>'           # 自动：小结果全量；大结果写文件+摘要
  python ec_dw_design_similar_search.py '<JSON parameters>' --inline  # 强制全量打印到 stdout

输出策略（脚本默认行为）：
  - **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sif-compliance-detection-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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
from contextlib import ExitStack, redirect_stdout
from unittest.mock import patch
from urllib.request import HTTPRedirectHandler, HTTPErrorProcessor, build_opener
from xml.etree import ElementTree

import call_api as _common

# 引用公共调用器入口，兼容包装只处理响应，不自行构建/发送 HTTP 请求。
_transport_call = _common.call_api

API_PATH = "/ecDw/designSimilarSearch"
SLUG = "linkfox-sif-compliance-detection"

# 响应不超过该字节数时全量输出；所有响应均落盘
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
SEARCH_RESPONSE_CONTRACT = "design-similar-v3"
_LAST_HTTP_STATUS = None

_SESSION_CACHE: dict[str, str] = {}

def get_api_base() -> str:
    """网关基础地址：env LINKFOX_TOOL_GATEWAY 优先，缺省回退正式地址。"""
    return (os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")



def get_api_key():
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://agent.linkfox.com/ settings to obtain or check your Key\n"
            "2. Set the environment variable: export LINKFOX_AGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def _decode_gateway_response(body, http_status=None, reason=None):
    """解析 JSON，兼容网关 ToolErrorResponse XML。"""
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
                    fields["errcode"] = code
                    return fields
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
        result["details"] = body
    return result


def _attach_gateway_cost_headers(result, headers):
    """将实际费用响应头合入结果，响应头优先。"""
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


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _GatewayResponseProcessor(HTTPErrorProcessor):
    """仅处理公共调用器的响应：阻止重定向，保留 HTTP 状态、XML 和费用。"""

    def http_response(self, request, response):
        global _LAST_HTTP_STATUS
        _LAST_HTTP_STATUS = response.getcode()
        try:
            body = response.read().decode("utf-8", errors="replace")
            if 300 <= _LAST_HTTP_STATUS < 400:
                result = {"error": "Redirect blocked", "httpStatus": _LAST_HTTP_STATUS}
            else:
                result = _decode_gateway_response(
                    body,
                    None if 200 <= _LAST_HTTP_STATUS < 300 else _LAST_HTTP_STATUS,
                    getattr(response, "reason", None),
                )
                if not 200 <= _LAST_HTTP_STATUS < 300 and isinstance(result, dict):
                    result.setdefault("httpStatus", _LAST_HTTP_STATUS)
            result = _attach_gateway_cost_headers(result, response.headers)
            # 公共 call_api 读取归一化 JSON，不重复创建请求或额外联网。
            return io.BytesIO(json.dumps(result, ensure_ascii=False).encode("utf-8"))
        finally:
            response.close()

    https_response = http_response


_OPENER = build_opener(_NoRedirect(), _GatewayResponseProcessor())


def call_api(params, api_path=API_PATH):
    """通过公共 run 请求一次，由业务入口负责缓存和落盘，不叠加公共缓存。"""
    global _LAST_HTTP_STATUS
    _LAST_HTTP_STATUS = None
    headers = {
        "Authorization": get_api_key(),
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }
    # 在公共调用器创建请求前校验；仅显示头名称，避免泄露 Authorization。
    for name, value in headers.items():
        try:
            value.encode("latin-1")
        except UnicodeEncodeError:
            return {"error": f"Invalid request header {name}: use Latin-1 text (ASCII recommended)"}
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            return {"error": f"Invalid request header {name}: control characters are not allowed"}
    captured = {}

    def collect(api_path, business_params):
        result = _transport_call(api_path, business_params)
        captured["result"] = result
        # 公共 run 的显示逻辑要求对象；非对象响应仍交回业务入口完整保存。
        return result if isinstance(result, dict) else {"rawResponse": result}

    try:
        with ExitStack() as stack:
            # 公共 transport 负责 Request 和发送，注入 opener 以禁止重定向并归一化响应。
            stack.enter_context(patch.object(_common, "urlopen", _OPENER.open))
            stack.enter_context(patch.object(_common, "call_api", collect))
            # 业务入口负责预检、缓存和落盘；run 的副作用限于内存，避免第二层缓存/文件。
            stack.enter_context(patch.object(_common, "_cache_path", lambda *args: ""))
            stack.enter_context(patch.object(_common, "_resolve_output_path", lambda *args: "<memory>"))
            stack.enter_context(patch.object(_common, "open", lambda *args, **kwargs: io.StringIO(), create=True))
            stack.enter_context(redirect_stdout(io.StringIO()))
            _common.run(api_path, SLUG, argv=[json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"])
        return captured["result"]
    except TimeoutError:
        return {"error": "Connection timed out; execution outcome may be unknown"}
    except OSError as exc:
        return {"error": f"Connection failed; execution outcome may be unknown: {exc}"}


def _cache_key(params, api_path=API_PATH):
    """隔离不同网关、端点、API Key；不保存原始 Key。"""
    fingerprint = hashlib.sha256(get_api_key().encode("utf-8")).hexdigest()
    cache_scope = {
        "apiBase": get_api_base(),
        "apiPath": api_path,
        "apiKeyFingerprint": fingerprint,
        "params": params,
    }
    if api_path == API_PATH:
        cache_scope["responseContract"] = SEARCH_RESPONSE_CONTRACT
    raw = json.dumps(cache_scope, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _cache_path(params, api_path=API_PATH):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params, api_path)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as file:
            payload = json.load(file)
        return payload if _is_success_payload(payload) else None
    except (OSError, json.JSONDecodeError):
        return None


def _is_2xx(value):
    """按公共基础规则识别数字或数字字符串，布尔值不视为状态码。"""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return False
    try:
        return 200 <= float(value) < 300
    except (TypeError, ValueError):
        return False


def _is_success_payload(result):
    """仅保存成功的网关响应；检查上游 envelope 的业务状态。"""
    if not isinstance(result, dict) or "data" not in result:
        return False
    upstream = result["data"]
    if not isinstance(upstream, dict) or upstream.get("code") != "OK":
        return False
    for envelope in (result, upstream):
        if not isinstance(envelope, dict):
            continue
        if ("error" in envelope and envelope["error"] is not None
                or envelope.get("success") is False or envelope.get("ok") is False):
            return False
        status = envelope.get("httpStatus")
        if status is not None and not _is_2xx(status):
            return False
        # errcode 严格复用公共基本规则，0/false 均不是空值或成功码。
        value = envelope.get("errcode")
        if value is not None and not (isinstance(value, str) and not value.strip()):
            if not _is_2xx(value):
                return False
        for name in ("errorCode", "code"):
            if name in envelope and str(envelope[name]).lower() not in ("0", "200", "ok", "success"):
                return False
    return True


def _is_success_result(result):
    return (
        _LAST_HTTP_STATUS is not None
        and 200 <= _LAST_HTTP_STATUS < 300
        and _is_success_payload(result)
    )


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
              "costToken", "costCredit", "upstreamRequestId", "httpStatus", "error", "costTime", "success"):
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
    """仅写当前任务目录，不回退家目录或系统临时目录。"""
    cached = _SESSION_CACHE.get("_root")
    if cached:
        return cached
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, ".write-probe-" + secrets.token_hex(6))
    with open(probe, "w", encoding="utf-8"):
        pass
    os.remove(probe)
    _SESSION_CACHE["_root"] = root
    return root


def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))

def _session_id(ts: float) -> str:
    """只接受安全的目录名，避免收费后才发现无法在 Windows 落盘。"""
    sid = os.environ.get("SESSION_ID") or ""
    if sid:
        stem = sid.split(".", 1)[0].upper()
        reserved = {"CON", "PRN", "AUX", "NUL", "CLOCK$"}
        reserved.update(f"{prefix}{digit}" for prefix in ("COM", "LPT") for digit in "123456789¹²³")
        if (
            sid != sid.strip()
            or sid.endswith(".")
            or stem in reserved
            or sid in (".", "..")
            or any(ord(char) < 32 or ord(char) == 127 for char in sid)
            or any(char in sid for char in '<>:"/\\|?*')
        ):
            raise ValueError("SESSION_ID must be a safe directory name without control characters or reserved names")
        return sid
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
    out = os.path.join(sub, f"{slug}-{int(ts * 1_000_000)}-{secrets.token_hex(6)}.{ext}")
    _update_meta(session_dir, skill=slug, kind="data", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out

def _resolve_output_path(ts):
    return resolve_data_path(SLUG, ts)


def main(argv=None, *, api_path=API_PATH, script_name="ec_dw_design_similar_search.py"):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    argv = list(sys.argv[1:] if argv is None else argv)
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    try:
        if len(argv) == 2 and argv[0] == "--params-file":
            with open(argv[1], encoding="utf-8-sig") as file:
                params = json.load(file)
        elif len(argv) == 1 and not argv[0].startswith("--"):
            params = json.loads(argv[0])
        else:
            print(f"Usage: {script_name} ('<JSON parameters>' | --params-file <path>) [--inline] [--no-cache]", file=sys.stderr)
            sys.exit(1)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Invalid parameter format: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("Invalid parameter format: top-level JSON must be an object", file=sys.stderr)
        sys.exit(1)
    # 缓存读取前仍要求配置当前 Key；落盘目录在可能计费的请求前检查。
    get_api_key()
    try:
        # 创建最终 session/data，并独占预留唯一文件，确认结果可保存后再请求。
        out_path = _resolve_output_path(time.time())
        with open(out_path, "x", encoding="utf-8"):
            pass
        cache_path = _cache_path(params, api_path) if use_cache else None
    except (OSError, ValueError) as exc:
        print(f"Cannot prepare task output directory: {exc}", file=sys.stderr)
        sys.exit(1)
    result = _load_cache(cache_path) if cache_path else None
    cache_hit = result is not None
    if result is None:
        result = call_api(params, api_path)
        if cache_path and _is_success_result(result):
            _save_cache(cache_path, result)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    try:
        with open(out_path, "w", encoding="utf-8") as file:
            file.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized.encode('utf-8'))} bytes)")
        if cache_hit:
            print(f"Cache hit: {cache_path}")
    except OSError as exc:
        print(f"Failed to save full response: {exc}", file=sys.stderr)
        sys.exit(1)
    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
