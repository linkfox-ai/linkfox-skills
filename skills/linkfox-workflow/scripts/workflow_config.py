#!/usr/bin/env python3
"""linkfox-workflow · 平台变量(`$vars`)与凭据(认证信息)管理。

两件不同的事,放一个脚本里只因为它们的调用方相同(生成/调整 flow 的人),不是同一层东西:

  变量 `vars`   名称 → 值的平台级键值对。任何 `acceptVariable` 字段都能写 `{{$vars.NAME}}`。
                运行时按 **flow 属主**的 groupId/memberId 查找(2026-10-30 起),跨成员/跨租户
                同名互不干扰;同一作用域内同名则服务端 409、运行时中止。所以名字不用再为防撞
                加前缀,但**密钥仍不要放变量**:value 是明文存库,组 OWNER 能从变量列表看到
                全组成员的变量值(凭据是加密的)。脚本不拦这类写,但会写进 stdout 的 warnings,
                回复里必须转述并建议改用凭据。

  凭据 `creds`   `name`(类型)+ `credentialName`(显示名)+ 加密后的 `credentialData`。
                行上带 groupId / memberId,成员只看得到自己的、组 owner 看得到全组的。
                密钥、token、机器人地址这类东西放这里,不要放变量。

安全约定(与 SKILL.md 的能力边界一致):
  - 脚本从不打印凭据内容;创建/更新只回 `id` / 类型 / 显示名 / 字段名。
  - 值只从文件或 stdin 进来(`--value-file -` / `--data-file -`),不走命令行参数。
  - 不调 `GET /credentials/:id`、不调 `/:id/reveal` —— 那两个会回解密后的内容。
  - 不把响应落盘:变量值是明文,落 workspace 等于留在会话目录里。

CLI:
  python scripts/workflow_config.py vars  list   [--reveal]
  python scripts/workflow_config.py vars  set    --name <NAME> --value-file <path|-> [--type static|runtime]
  python scripts/workflow_config.py vars  delete (--name <NAME> | --id <uuid>) --confirm
  python scripts/workflow_config.py creds list   [--type <credentialName>]
  python scripts/workflow_config.py creds create --type <credentialName> --credential-name <显示名> --data-file <path|->
  python scripts/workflow_config.py creds update --id <uuid> [--credential-name <显示名>] [--data-file <path|->]
  python scripts/workflow_config.py creds delete --id <uuid> --confirm
  公共可选:[--proxy-url <url>]

退出码:0 成功;1 网络 / 鉴权失败 / 资源不存在(401、404);
       3 响应结构不是预期(例如列表不是数组);
       64 CLI 用法错 / 入参不合法(缺必填字段、数据文件不是 JSON 对象等);
       65 服务端拒绝写操作(400 / 409),stderr 带服务端 message;
       68 权限不足(403)。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import get_api_base  # type: ignore  # noqa: E402
from workflow_auth import clean_key, with_auth_hint  # type: ignore  # noqa: E402


API_PREFIX = "/api/v1"
VAR_TYPES = ("static", "runtime")
NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
UUID_RE = re.compile(r"^[0-9a-fA-F-]{8,64}$")

# 名字像密钥 / 像地址的,写进变量等于明文落库且组 OWNER 可见 —— 只警告不拦(用户 2026-10-29 定的口径)
_SECRET_NAME_RE = re.compile(
    r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD|PWD|AUTH|CREDENTIAL|SIGN|WEBHOOK|COOKIE|SESSION)", re.I
)
_SECRET_VALUE_RES = (
    re.compile(r"^sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"^eyJ[A-Za-z0-9_-]{10,}\."),  # JWT
    re.compile(r"^https://[^\s]*/hook/[A-Za-z0-9-]{8,}"),  # 飞书 / 钉钉机器人
    re.compile(r"^https://[^\s]*(?:/open-apis/bot|/robot/send)"),
)

# 已知凭据类型 → 必填 / 可选字段(字段名取自各 credential 组件定义)。
# 未列出的类型按原样提交,只做 JSON 对象校验。
CREDENTIAL_SCHEMA: dict[str, dict[str, tuple[str, ...]]] = {
    "linkfoxAgentApi": {"required": ("apiKey",), "optional": ("baseUrl",)},
    "httpApiKey": {"required": ("key", "value"), "optional": ()},
    "httpBearerToken": {"required": ("token",), "optional": ()},
    "httpBasicAuth": {"required": ("basicAuthUsername", "basicAuthPassword"), "optional": ()},
}


class ConfigError(RuntimeError):
    def __init__(self, message: str, code: int = 1, status: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {with_auth_hint(msg)}", file=sys.stderr)
    sys.exit(code)


def _env_first(*names: str) -> str:
    for n in names:
        v = clean_key(os.environ.get(n) or "")
        if v:
            return v
    return ""


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Manage linkfox-workflow platform variables and credentials")
    resources = p.add_subparsers(dest="resource", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--proxy-url")

    def vars_group() -> argparse.ArgumentParser:
        return resources.add_parser("vars")

    vp = vars_group()
    vsub = vp.add_subparsers(dest="command", required=True)

    vl = vsub.add_parser("list")
    common(vl)
    vl.add_argument(
        "--reveal",
        action="store_true",
        help="把变量值原样打出来(默认脱敏)。值可能是密钥,只在用户明确要求看时用",
    )

    vs = vsub.add_parser("set")
    common(vs)
    vs.add_argument("--name", required=True)
    vs.add_argument(
        "--value-file",
        required=True,
        help="值所在文件路径;`-` 表示从 stdin 读。不要用命令行参数直接给值",
    )
    vs.add_argument("--type", choices=VAR_TYPES, default=None)

    vd = vsub.add_parser("delete")
    common(vd)
    group = vd.add_mutually_exclusive_group(required=True)
    group.add_argument("--name")
    group.add_argument("--id")
    vd.add_argument("--confirm", action="store_true", help="真的删除;不带时只报会删哪一条")

    cp = resources.add_parser("creds")
    csub = cp.add_subparsers(dest="command", required=True)

    cl = csub.add_parser("list")
    common(cl)
    cl.add_argument("--type", help="按凭据类型过滤,如 httpBearerToken")

    cc = csub.add_parser("create")
    common(cc)
    cc.add_argument("--type", required=True, help="凭据类型,如 httpApiKey / httpBearerToken / httpBasicAuth")
    cc.add_argument("--credential-name", required=True, help="给人看的显示名")
    cc.add_argument("--data-file", required=True, help="字段值 JSON 所在文件;`-` 表示从 stdin 读")

    cu = csub.add_parser("update")
    common(cu)
    cu.add_argument("--id", required=True)
    cu.add_argument("--credential-name")
    cu.add_argument("--data-file", help="只写要改的字段即可(服务端会与已有值合并)")

    cd = csub.add_parser("delete")
    common(cd)
    cd.add_argument("--id", required=True)
    cd.add_argument("--confirm", action="store_true", help="真的删除;不带时只报会删哪一条")

    args = p.parse_args(argv)

    if args.resource == "vars":
        if getattr(args, "name", None) is not None and not NAME_RE.match(args.name):
            _die(f"--name 只允许字母数字下划线、且不以数字开头:{args.name!r}", 64)
        if getattr(args, "id", None) and not UUID_RE.match(args.id):
            _die(f"--id 格式非法:{args.id!r}", 64)
    else:
        if getattr(args, "id", None) and not UUID_RE.match(args.id):
            _die(f"--id 格式非法:{args.id!r}", 64)
        if args.command == "update" and not (args.credential_name or args.data_file):
            _die("update 至少要给 --credential-name 或 --data-file 之一", 64)
    return args


# ---- HTTP -------------------------------------------------------------------


def _request(
    method: str,
    url: str,
    api_key: str,
    body: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    headers = {"Authorization": api_key, "User-Agent": "LinkFox-Workflow-Agent/1.0"}
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except HTTPError as e:
        payload = e.read().decode("utf-8", errors="replace")[:400]
        raise ConfigError(_error_message(e.code, payload), status=e.code) from None
    except (URLError, TimeoutError, OSError) as e:
        raise ConfigError(f"网络失败:{e}") from None
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ConfigError(f"响应不是合法 JSON:{e}", code=3) from None


def _error_message(status: int, payload: str) -> str:
    try:
        parsed = json.loads(payload)
        message = parsed.get("message") if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        message = None
    return f"HTTP {status}: {message or payload}"


def _url(proxy: str, path: str, query: dict[str, Any] | None = None) -> str:
    url = f"{proxy}{API_PREFIX}{path}"
    return f"{url}?{urlencode(query)}" if query else url


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise ConfigError(f"读不到 --value-file / --data-file 指定的文件 {path}:{e}", code=64) from None


def _read_json_object(path: str) -> dict[str, Any]:
    raw = _read_input(path).strip()
    if not raw:
        raise ConfigError("数据文件是空的", code=64)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ConfigError(f"数据文件不是合法 JSON:{e}", code=64) from None
    if not isinstance(parsed, dict) or not parsed:
        raise ConfigError("数据文件必须是**非空 JSON 对象**,例如 {\"token\": \"...\"}", code=64)
    for k, v in parsed.items():
        if isinstance(v, (dict, list)):
            raise ConfigError(f"字段 {k} 的值必须是标量(字符串 / 数字),不接受嵌套结构", code=64)
    return parsed


def _is_secret_name(name: str) -> bool:
    return bool(_SECRET_NAME_RE.search(name or ""))


def _is_secret_value(value: str) -> bool:
    return any(r.search(value or "") for r in _SECRET_VALUE_RES)


# ---- 变量 -------------------------------------------------------------------


def _list_variables(proxy: str, api_key: str) -> list[dict[str, Any]]:
    data = _request("GET", _url(proxy, "/variables"), api_key)
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        data = data["data"]
    if not isinstance(data, list):
        raise ConfigError("变量列表响应不是数组", code=3)
    return [row for row in data if isinstance(row, dict)]


def _mask_value(value: Any) -> tuple[str, int]:
    text = "" if value is None else str(value)
    if not text:
        return "empty", 0
    return "set", len(text)


def cmd_vars_list(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    rows = _list_variables(proxy, api_key)
    secret_names = []
    variables = []
    for row in rows:
        name = str(row.get("name") or "")
        value = row.get("value")
        state, length = _mask_value(value)
        item: dict[str, Any] = {
            "id": row.get("id"),
            "name": name,
            "type": row.get("type") or "static",
            "updatedDate": row.get("updatedDate"),
            "valueState": state,
            "valueLength": length,
        }
        if args.reveal:
            item["value"] = "" if value is None else str(value)
        else:
            item["value"] = "***" if state == "set" else ""
        if _is_secret_name(name) or (isinstance(value, str) and _is_secret_value(value)):
            secret_names.append(name)
        variables.append(item)

    warnings = _secret_warnings(secret_names)
    return {"mode": "vars.list", "total": len(variables), "variables": variables, "warnings": warnings}


def _secret_warnings(names: list[str]) -> list[str]:
    if not names:
        return []
    return [
        f"这些变量的名字或值像密钥:{'、'.join(names[:8])}{' 等' if len(names) > 8 else ''}。"
        "变量值以明文存在库里(凭据是加密的),而且组内 OWNER 能从变量列表看到全组成员的变量;"
        "密钥类值请改用凭据(creds),不要放变量"
    ]


def cmd_vars_set(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    value = _read_input(args.value_file)
    if value.endswith("\r\n"):
        value = value[:-2]
    elif value.endswith("\n"):
        value = value[:-1]

    warnings = _secret_warnings([args.name] if _is_secret_name(args.name) or _is_secret_value(value) else [])

    rows = _list_variables(proxy, api_key)
    matches = [r for r in rows if str(r.get("name") or "") == args.name]
    if len(matches) > 1:
        ids = "、".join(str(r.get("id")) for r in matches[:8])
        raise ConfigError(
            f"同名变量有 {len(matches)} 条({ids})。可能是同一作用域的历史脏数据(运行时会被中止,"
            "先 vars delete --id 删掉多余的),也可能是组 OWNER 看到的、分属不同成员的同名行"
            "(那是不同作用域,不算冲突,但脚本判不出哪条是你的)——两种情况都请用 vars list 看清 id 后再决定",
            code=65,
        )

    if not matches:
        body: dict[str, Any] = {"name": args.name, "value": value, "type": args.type or "static"}
        created = _request("POST", _url(proxy, "/variables"), api_key, body)
        variable_id = created.get("id") if isinstance(created, dict) else None
        if not variable_id:
            raise ConfigError("创建变量后响应缺少 id,不要当成成功", code=3)
        return {
            "mode": "vars.set",
            "action": "created",
            "id": variable_id,
            "name": args.name,
            "type": args.type or "static",
            "valueLength": len(value),
            "warnings": warnings,
        }

    row = matches[0]
    body = {"value": value}
    if args.type:
        body["type"] = args.type
    else:
        body["type"] = row.get("type") or "static"
    _request("PUT", _url(proxy, f"/variables/{quote(str(row.get('id')), safe='')}"), api_key, body)
    return {
        "mode": "vars.set",
        "action": "updated",
        "id": row.get("id"),
        "name": args.name,
        "type": body["type"],
        "valueLength": len(value),
        "warnings": warnings,
    }


def cmd_vars_delete(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    target: dict[str, Any]
    if args.id:
        target = {"id": args.id, "name": None}
    else:
        rows = [r for r in _list_variables(proxy, api_key) if str(r.get("name") or "") == args.name]
        if not rows:
            raise ConfigError(f"没有名为 {args.name} 的变量")
        if len(rows) > 1:
            ids = "、".join(str(r.get("id")) for r in rows[:8])
            raise ConfigError(
                f"同名变量有 {len(rows)} 条({ids});可能是历史脏数据,也可能是分属不同成员的同名行。"
                "请用 --id 指定要删哪一条",
                code=65,
            )
        target = rows[0]

    result: dict[str, Any] = {"mode": "vars.delete", "id": target.get("id"), "name": target.get("name"), "deleted": False}
    if not args.confirm:
        result["requiresConfirmation"] = True
        result["warnings"] = ["引用这个变量的 flow 会读到字面量 {{$vars...}}(运行时不会报错,只会不替换)"]
        return result

    _request("DELETE", _url(proxy, f"/variables/{quote(str(target.get('id')), safe='')}"), api_key)
    result["deleted"] = True
    return result


# ---- 凭据 -------------------------------------------------------------------


def _summarize_credential(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "type": row.get("name"),
        "credentialName": row.get("credentialName"),
        "updatedDate": row.get("updatedDate"),
    }


def _list_credentials(proxy: str, api_key: str) -> list[dict[str, Any]]:
    data = _request("GET", _url(proxy, "/credentials"), api_key)
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        data = data["data"]
    if not isinstance(data, list):
        raise ConfigError("凭据列表响应不是数组", code=3)
    return [r for r in data if isinstance(r, dict)]


def cmd_creds_list(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    # 不用服务端的 `?credentialName=` 过滤:它匹配的是显示名,不是类型;在本地按类型筛
    rows = [_summarize_credential(r) for r in _list_credentials(proxy, api_key)]
    if args.type:
        rows = [r for r in rows if r.get("type") == args.type]
    return {"mode": "creds.list", "total": len(rows), "credentials": rows}


def _check_credential_data(cred_type: str, data: dict[str, Any]) -> list[str]:
    schema = CREDENTIAL_SCHEMA.get(cred_type)
    if schema is None:
        return [f"未知凭据类型 {cred_type}:按原样提交,先在界面上确认它需要哪些字段"]
    missing = [f for f in schema["required"] if not str(data.get(f, "") or "").strip()]
    if missing:
        raise ConfigError(f"凭据类型 {cred_type} 缺必填字段:{'、'.join(missing)}", code=64)
    known = set(schema["required"]) | set(schema["optional"])
    unknown = [k for k in data if k not in known]
    if unknown:
        return [f"凭据类型 {cred_type} 不认这些字段:{'、'.join(unknown)}(多半是拼错,值仍会原样存进去)"]
    return []


def cmd_creds_create(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    if not args.credential_name.strip():
        raise ConfigError("--credential-name 不能为空;它是用户在这条凭据上看到的显示名", code=64)
    data = _read_json_object(args.data_file)
    warnings = _check_credential_data(args.type, data)
    if args.type == "linkfoxAgentApi":
        warnings.append(
            "linkfoxAgentApi 凭据通常由后台自动绑定;只有后台绑定失败、或用户明确要手工建时才建这一份"
        )
    body = {"name": args.type, "credentialName": args.credential_name, "plainDataObj": data}
    created = _request("POST", _url(proxy, "/credentials"), api_key, body)
    credential_id = created.get("id") if isinstance(created, dict) else None
    if not credential_id:
        raise ConfigError("创建凭据后响应缺少 id,不要当成成功", code=3)
    return {
        "mode": "creds.create",
        "id": credential_id,
        "type": args.type,
        "credentialName": args.credential_name,
        "fields": sorted(data.keys()),
        "warnings": warnings,
    }


def cmd_creds_update(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    # 更新必须带上 `name`(类型):服务端是 merge 语义,缺字段可能把类型冲掉
    rows = [r for r in _list_credentials(proxy, api_key) if str(r.get("id") or "") == args.id]
    if not rows:
        raise ConfigError(f"没有 id 为 {args.id} 的凭据(不存在,或不在你可见的范围内)")
    row = rows[0]
    cred_type = str(row.get("name") or "")
    warnings: list[str] = []

    body: dict[str, Any] = {
        "name": cred_type,
        "credentialName": args.credential_name or row.get("credentialName"),
    }
    if args.data_file:
        data = _read_json_object(args.data_file)
        warnings.extend(_check_credential_data(cred_type, data))
        body["plainDataObj"] = data
    updated = _request(
        "PUT", _url(proxy, f"/credentials/{quote(args.id, safe='')}"), api_key, body
    )
    return {
        "mode": "creds.update",
        "id": args.id,
        "type": cred_type,
        "credentialName": (updated.get("credentialName") if isinstance(updated, dict) else None)
        or body["credentialName"],
        "fields": sorted((body.get("plainDataObj") or {}).keys()),
        "warnings": warnings,
    }


def cmd_creds_delete(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    result: dict[str, Any] = {"mode": "creds.delete", "id": args.id, "deleted": False}
    if not args.confirm:
        result["requiresConfirmation"] = True
        result["warnings"] = ["引用这个凭据的节点运行时取不到认证信息;删之前先在画布上确认没有别的流在用"]
        return result
    _request("DELETE", _url(proxy, f"/credentials/{quote(args.id, safe='')}"), api_key)
    result["deleted"] = True
    return result


COMMANDS = {
    ("vars", "list"): cmd_vars_list,
    ("vars", "set"): cmd_vars_set,
    ("vars", "delete"): cmd_vars_delete,
    ("creds", "list"): cmd_creds_list,
    ("creds", "create"): cmd_creds_create,
    ("creds", "update"): cmd_creds_update,
    ("creds", "delete"): cmd_creds_delete,
}


def _exit_code_for(error: ConfigError) -> int:
    if error.status == 403:
        return 68
    if error.status == 401 or error.status == 404:
        return 1
    if error.status and 400 <= error.status < 500:
        return 65
    return error.code


def main(argv: list[str] | None = None) -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except AttributeError:
        pass
    args = _parse_args(argv)
    api_key = _env_first("LINKFOX_AGENT_API_KEY", "LINKFOXAGENT_API_KEY")
    if not api_key:
        _die("missing LinkFox API key; set LINKFOX_AGENT_API_KEY", 1)
    proxy = ((args.proxy_url or "").strip() or get_api_base()).rstrip("/")
    try:
        summary = COMMANDS[(args.resource, args.command)](args, proxy, api_key)
    except ConfigError as e:
        _die(str(e), _exit_code_for(e))
        return
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
