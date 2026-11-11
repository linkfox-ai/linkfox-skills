"""LinkFox gateway transport and session output."""
import argparse
from contextlib import contextmanager
from datetime import datetime
from http.client import HTTPException
import json
import os
from pathlib import Path
import re
import sys
import uuid
from urllib.error import HTTPError
from urllib.parse import unquote_plus
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

LIMIT = 8000
XML_ERROR_FIELDS = {
    "errcode": "errcode", "errmsg": "errmsg", "code": "code", "errorcode": "errorCode",
    "requestid": "requestId", "traceid": "traceId",
}
CODE_FIELDS = ("errcode", "errorCode", "code")
ID_FIELDS = ("requestId", "request_id", "traceId", "RequestId", "TraceId")
DIAGNOSTIC_FIELDS = (
    "success", *ID_FIELDS, "clientRequestId", "status", "error", "httpStatus", *CODE_FIELDS,
    "upstreamCode", "upstreamRequestId", "nextBeforeId",
)
SECRET_KEYS = {
    "authorization", "accesstoken", "refreshtoken", "token", "appsecret",
    "secret", "secretkey", "accesskeyid", "accesskeysecret", "securitytoken",
    "apikey", "sign", "signature", "authorizeurl", "authorizationcode",
    "clientsecret", "credential", "credentials", "idtoken", "password", "sessiontoken",
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def get_api_base():
    return (os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")


def get_api_key():
    return os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY") or ""


def configure_stdout():
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace")


def gateway_request(path, params, key, *, method="POST", base=None, timeout=150):
    base = base or get_api_base()
    headers = {
        "Authorization": key,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
    }
    for name in ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME"):
        headers[name] = os.environ.get(name, "")
    body = json.dumps(params).encode("utf-8") if method == "POST" else None
    request = Request(base + path, body, headers, method=method)
    try:
        with build_opener(NoRedirect).open(request, timeout=timeout) as response:
            return response.status, response.read()
    except HTTPError as error:
        with error:
            return error.code, error.read() if error.fp else b""


def decode(raw):
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            return payload
    except (ValueError, UnicodeError):
        pass
    if raw.lstrip().startswith(b"<") and b"<!DOCTYPE" not in raw.upper():
        try:
            root = ElementTree.fromstring(raw)
            if root.tag.split("}")[-1] == "ToolErrorResponse":
                result = {"error": "TOOL_ERROR"}
                for child in root:
                    name = normalized(child.tag.rsplit("}", 1)[-1])
                    if child.text and (name in XML_ERROR_FIELDS or name in SECRET_KEYS):
                        result[XML_ERROR_FIELDS.get(name, name)] = child.text.strip()
                errcode = result.get("errcode", "")
                result["errcode"] = int(errcode) if re.fullmatch(r"[0-9]{1,9}", errcode) else "TOOL_ERROR"
                return result
        except (ElementTree.ParseError, ValueError):
            pass
    return {"errcode": "INVALID_GATEWAY_RESPONSE"}


def ok(status, payload):
    if payload.get("error"):
        return False
    errcode = payload.get("errcode")
    if isinstance(errcode, str):
        errcode = errcode.strip()
        if len(errcode) == 3 and errcode.isascii() and errcode.isdigit():
            errcode = int(errcode)
    return 200 <= status < 300 and (
        errcode in (None, "") or type(errcode) in (int, float)
        and 200 <= errcode < 300 and errcode % 1 == 0
    )


def normalized(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def gateway_failure(status, payload):
    result = {"httpStatus": status}
    error = payload.get("error")
    if error:
        result["error"] = "TOOL_ERROR" if error == "TOOL_ERROR" else "GATEWAY_ERROR"
    for name in CODE_FIELDS:
        value = payload.get(name)
        if type(value) is int and -2147483648 <= value <= 2147483647:
            result[name] = value
        elif isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", value):
            result[name] = value
    for name in ID_FIELDS:
        value = payload.get(name)
        if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", value):
            result[name] = value
    return result


def secret_values(node, fields):
    if isinstance(node, dict):
        for name, value in node.items():
            if normalized(name) in fields and isinstance(value, str) and value:
                yield value
            yield from secret_values(value, fields)
    elif isinstance(node, list):
        for value in node:
            yield from secret_values(value, fields)


def sanitize(payload, source, key, private_fields):
    hidden = SECRET_KEYS | private_fields
    known = {key, *secret_values(source, hidden), *secret_values(payload, hidden)}
    secrets = sorted(known, key=len, reverse=True)

    def clean(value):
        if isinstance(value, dict):
            return {clean(name): clean(item) for name, item in value.items()
                    if normalized(name) not in hidden}
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, str):
            for secret in secrets:
                value = value.replace(secret, "[redacted]")
        return value

    return clean(payload)


@contextmanager
def lock_metadata(meta):
    lock_path = meta.with_suffix(".json.lock")
    if meta.resolve() != meta or lock_path.resolve() != lock_path:
        raise ValueError("会话元数据包含重定向路径")
    with lock_path.open("a+b") as lock:
        if os.name == "nt":
            import msvcrt

            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        yield


def read_metadata(meta):
    with meta.open("r+", encoding="utf-8") as stream:
        record = json.load(stream)
    if not isinstance(record, dict) or any(
        not isinstance(record.get(field, []), list) for field in ("skills_called", "data_files")
    ):
        raise ValueError("会话元数据格式无效")
    return record


def write_metadata(meta, record):
    staging = meta.with_name(f"._meta-{uuid.uuid4().hex}.tmp")
    stream = staging.open("x", encoding="utf-8")
    try:
        with stream:
            json.dump(record, stream, indent=2)
        staging.replace(meta)
    finally:
        staging.unlink(missing_ok=True)


def check_metadata_replace(meta):
    probe = meta.with_name(f"._meta-check-{uuid.uuid4().hex}.tmp")
    with probe.open("x", encoding="utf-8"):
        pass
    try:
        write_metadata(probe, {})
    finally:
        probe.unlink(missing_ok=True)


def output_path(slug):
    now = datetime.now()
    sid = os.environ.get("SESSION_ID") or now.strftime("%H%M%S") + "-" + uuid.uuid4().hex[:8]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", sid) or sid.endswith("."):
        raise ValueError("SESSION_ID 不是有效的会话目录名")
    cwd = Path.cwd().resolve()
    expected = cwd / "linkfox" / now.strftime("%Y-%m-%d") / sid
    data = expected / "data"
    if data.resolve() != data:
        raise ValueError("会话目录包含重定向路径")
    data.mkdir(parents=True, exist_ok=True)
    meta = expected / "_meta.json"
    with lock_metadata(meta):
        if meta.exists():
            read_metadata(meta)
            check_metadata_replace(meta)
        else:
            write_metadata(meta, {"session_id": sid, "date": now.strftime("%Y-%m-%d"),
                                  "started_at": now.astimezone().isoformat(), "skills_called": [],
                                  "deliverables": [], "data_files": [], "media_files": []})
    return data / (slug + "-" + now.strftime("%H%M%S%f") + "-" + uuid.uuid4().hex[:8] + ".json")


def register_output(path):
    session = path.parent.parent
    meta = session / "_meta.json"
    skill = Path(__file__).resolve().parents[1].name
    with lock_metadata(meta):
        record = read_metadata(meta)
        skills = record.setdefault("skills_called", [])
        if skill not in skills:
            skills.append(skill)
        record.setdefault("data_files", []).append(path.relative_to(session).as_posix())
        record["last_used_at"] = datetime.now().astimezone().isoformat()
        write_metadata(meta, record)


def summarize(result):
    best = ("", [])

    def visit(node, path):
        nonlocal best
        if isinstance(node, list) and (not best[0] or len(node) > len(best[1])):
            best = path, node
        elif isinstance(node, dict):
            for name, value in node.items():
                visit(value, path + "." + name if path else name)

    visit(result, "")
    summary = {"keys": list(result), **diagnostics(result)}
    if best[0]:
        with_list = {**summary, "listPath": best[0], "count": len(best[1]), "sample": []}
        if len(json.dumps(with_list, ensure_ascii=False, indent=2).encode("utf-8", "backslashreplace")) > LIMIT:
            return summary
        summary = with_list
        for row in best[1][:3]:
            summary["sample"].append(row)
            if len(json.dumps(summary, ensure_ascii=False, indent=2).encode("utf-8", "backslashreplace")) > LIMIT:
                summary["sample"].pop()
                break
    return summary


def diagnostics(result):
    return {name: result[name] for name in DIAGNOSTIC_FIELDS if name in result}


def run(api_path, slug, argv=None, *, prepare, interpret, private_fields=frozenset(),
        transient=None, error_diagnostics=None, private_output=False, failure_context=None):
    configure_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("params", help="JSON object")
    parser.add_argument("--inline", action="store_true")
    parser.add_argument("--no-cache", action="store_true", help="Requests are always live")
    args = parser.parse_args(argv)
    if private_output and args.inline:
        print("敏感结果仅保存到本地文件，不能使用 --inline", file=sys.stderr)
        return 2
    try:
        params = json.loads(args.params)
        if not isinstance(params, dict):
            raise ValueError("请求参数必须是 JSON 对象")
        params = prepare(params)
    except json.JSONDecodeError:
        print("请求参数必须是有效的 JSON", file=sys.stderr)
        return 2
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    key = get_api_key()
    if not key:
        print("缺少 LINKFOX_AGENT_API_KEY", file=sys.stderr)
        return 2

    try:
        path = output_path(slug)
        if private_output:
            output = open(path, "x", encoding="utf-8", errors="backslashreplace",
                          opener=lambda filename, flags: os.open(filename, flags, 0o600))
        else:
            output = path.open("x", encoding="utf-8", errors="backslashreplace")
    except (OSError, ValueError):
        print("当前工作目录下的 LinkFox 会话输出或元数据不可写", file=sys.stderr)
        return 2

    with output:
        recovery = failure_context(params) if failure_context else {}
        payload = {}
        try:
            status, raw = gateway_request(api_path, params, key)
            payload = decode(raw)
            if ok(status, payload):
                success, result = interpret(payload)
            else:
                success = False
                result = gateway_failure(status, payload)
                if error_diagnostics:
                    result.update(error_diagnostics(payload.get("errmsg")))
        except (HTTPException, OSError, ValueError):
            success, result = False, {"error": "GATEWAY_REQUEST_FAILED"}
        if not success and recovery:
            result = {**recovery, **result}
        temporary = transient(result) if transient and success else None
        safe = sanitize(result, payload, key, private_fields)
        if temporary:
            credentials = {key, *secret_values(payload, SECRET_KEYS - {"authorizeurl"})}
            decoded = unquote_plus(temporary)
            variants = (temporary, decoded, unquote_plus(decoded))
            if any(secret in variant for secret in credentials for variant in variants):
                temporary = None
                success = False
                safe["error"] = "INVALID_TRANSIENT_OUTPUT"
        safe["success"] = success
        serialized = json.dumps(safe, ensure_ascii=False, indent=2)
        try:
            output.write(serialized)
            output.flush()
        except OSError:
            print("无法保存 LinkFox 响应", file=sys.stderr)
            if recovery:
                print(json.dumps({**diagnostics(safe), "success": False, "error": "OUTPUT_SAVE_FAILED"},
                                 ensure_ascii=False))
            return 1

    try:
        register_output(path)
    except (OSError, ValueError):
        print("响应已保存，但无法更新 LinkFox 会话元数据", file=sys.stderr)
    if private_output:
        print(json.dumps(diagnostics(safe), ensure_ascii=False))
    elif args.inline or len(serialized.encode("utf-8", "backslashreplace")) <= LIMIT:
        print(serialized)
    else:
        print(json.dumps(summarize(safe), ensure_ascii=False, indent=2))
    if temporary and not private_output:
        print(temporary)
    print(f"Saved full response: {path}")
    return 0 if success else 1
