#!/usr/bin/env python3
"""linkfox-workflow · 工作流历史版本:查看、对比、还原。

服务端(workflow-studio → Flowise)在历史记录开关打开时,每次保存自动记一版;本 skill 上传时
已经顺手打开了开关(见 upload_workflow.py 的 `history`)。这个脚本只读写**服务端**的历史,
不碰本地 workflow 文件 —— 版本的唯一真相源在服务端。

用户说"看下历史版本 / 刚才改了什么 / 撤销刚才的修改 / 回到第 3 版"时用它。

四个子命令:
  list     版本列表(倒序,最新在前),每版带变更人、类型、改了哪些节点
  show     某一版的摘要;完整快照落盘,stdout 只给节点清单
  diff     任意两版对比(from → to),只给结构化摘要,两份快照落盘
  restore  还原到某一版。**不带 --confirm 只预览**(当前最新版 → 目标版会改回哪些节点),
           带 --confirm 才真的还原。只有属主能还原(协作者 403)。
           `--expect-latest <N>`:调用方认为服务端最新是第 N 版;对不上就退出 69,stdout 列出
           第 N 版之后的保存(谁、何时、改了什么),不预览也不还原。`--confirm` 必须带它
           (值取预览 stdout 的 latestVersion),防止预览之后有人又保存、用户同意的不是实际改动。

还原走服务端 `POST /versions/{v}/restore`,不是本地重放:服务端拿当时的整张快照写回,
自己再记一条 RESTORE 版本,所以还原本身也能被撤销。

CLI:
  python scripts/workflow_history.py list    --workflow-id <id> [--page 1] [--limit 10]
  python scripts/workflow_history.py show    --workflow-id <id> --version <N>
  python scripts/workflow_history.py diff    --workflow-id <id> --from <N> --to <M>
  python scripts/workflow_history.py restore --workflow-id <id> --version <N> [--expect-latest <M>]
  python scripts/workflow_history.py restore --workflow-id <id> --version <N> --expect-latest <M> --confirm
  公共可选:[--proxy-url <url>]

退出码:0 成功;1 网络 / 鉴权 / 版本不存在;4 写盘失败;
       64 CLI 用法错;65 响应非法 JSON;
       67 历史记录没开且没有任何版本(无从查看 / 还原);
       68 还原被拒:不是属主(403)或工作流在此期间被别人改过(409);
       69 --expect-latest 对不上:第 N 版之后又有人保存过(stdout 列出那些版本),先问用户。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import get_api_base, resolve_data_path  # type: ignore  # noqa: E402
from workflow_auth import clean_key, with_auth_hint  # type: ignore  # noqa: E402
from workflow_identity import mark_edited  # type: ignore  # noqa: E402


# 不用 `linkfox-workflow` 前缀:那是 workflow 文件的命名空间(basename = sourceKey)。
HISTORY_SLUG = "linkfox-history"
_FLOWID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")
LIMIT_MAX = 100
# 退出 69 时最多列出多少个"之后又保存的版本";更多的只标 newerTruncated
NEWER_MAX = 10
# 列表里每版最多列几个节点名,多了只给计数 —— stdout 是给模型读的,不是给人翻的
NODE_NAMES_PER_KIND = 8

CHANGE_TYPE_TEXT = {
    "BASELINE": "开启历史记录",
    "UPDATE": "修改了工作流",
    "CONFIG": "修改了配置",
    "RESTORE": "还原",
}


class HistoryError(RuntimeError):
    def __init__(
        self,
        message: str,
        code: int = 1,
        status: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status = status
        # 非 0 退出时仍要给调用方的结构化信息(如 69 的"之后又有谁改了什么"),打到 stdout
        self.details = details


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {with_auth_hint(msg)}", file=sys.stderr)
    sys.exit(code)


def _env_first(*names: str) -> str:
    for n in names:
        v = clean_key(os.environ.get(n) or "")
        if v:
            return v
    return ""


def _positive(name: str):
    def parse(raw: str) -> int:
        try:
            value = int(raw)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{name} 必须是正整数") from None
        if value < 1:
            raise argparse.ArgumentTypeError(f"{name} 必须是正整数")
        return value

    return parse


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="View, diff and restore linkfox-workflow versions")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--workflow-id", required=True)
        sp.add_argument("--proxy-url")

    lp = sub.add_parser("list")
    common(lp)
    lp.add_argument("--page", type=_positive("--page"), default=1)
    lp.add_argument("--limit", type=_positive("--limit"), default=10)

    sp = sub.add_parser("show")
    common(sp)
    sp.add_argument("--version", type=_positive("--version"), required=True)

    dp = sub.add_parser("diff")
    common(dp)
    dp.add_argument("--from", dest="from_version", type=_positive("--from"), required=True)
    dp.add_argument("--to", dest="to_version", type=_positive("--to"), required=True)

    rp = sub.add_parser("restore")
    common(rp)
    rp.add_argument("--version", type=_positive("--version"), required=True)
    rp.add_argument(
        "--confirm",
        action="store_true",
        help="真的还原。不带时只预览会改回哪些节点,不写任何东西。必须同时带 --expect-latest",
    )
    rp.add_argument(
        "--expect-latest",
        type=_positive("--expect-latest"),
        help=(
            "调用方认为的服务端最新版本号。服务端最新版对不上(之后又有人保存过)就退出 69,"
            "列出多出来的版本,不预览也不还原"
        ),
    )

    args = p.parse_args(argv)
    if not _FLOWID_RE.match(args.workflow_id):
        _die(f"--workflow-id 格式非法:{args.workflow_id!r}", 64)
    if args.command == "list" and args.limit > LIMIT_MAX:
        _die(f"--limit 最大 {LIMIT_MAX}", 64)
    if args.command == "diff" and args.from_version == args.to_version:
        _die("--from 和 --to 是同一版,没有可比的", 64)
    if args.command == "restore" and args.confirm and args.expect_latest is None:
        # 预览给用户看的 willChange 是"那一刻的最新版 → 目标版"。确认前有人又保存过,
        # 用户同意的就不是真正会发生的改动 —— 所以确认必须带上预览时的 latestVersion。
        _die(
            "--confirm 必须带 --expect-latest <预览 stdout 里的 latestVersion>;"
            "先不带 --confirm 预览一次",
            64,
        )
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
        raise HistoryError(_error_message(e.code, payload), status=e.code) from None
    except (URLError, TimeoutError, OSError) as e:
        raise HistoryError(f"网络失败:{e}") from None
    try:
        return json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise HistoryError(f"响应不是合法 JSON:{e}", code=65) from None


def _error_message(status: int, payload: str) -> str:
    """服务端两种错误体都有 message(代理闸门 / Flowise),优先给它。"""
    try:
        parsed = json.loads(payload)
        message = parsed.get("message") if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        message = None
    return f"HTTP {status}: {message or payload}"


def _base(proxy: str, flow_id: str) -> str:
    return f"{proxy}/api/v1/chatflows/{quote(flow_id, safe='')}"


# ---- 摘要 -------------------------------------------------------------------


def _node_label(item: dict[str, Any]) -> str:
    return str(item.get("label") or item.get("name") or item.get("id") or "?")


def _names(items: Any, with_changes: bool = False) -> dict[str, Any]:
    if not isinstance(items, list):
        items = []
    names = []
    for item in items[:NODE_NAMES_PER_KIND]:
        if not isinstance(item, dict):
            continue
        label = _node_label(item)
        if with_changes and isinstance(item.get("changes"), list) and item["changes"]:
            label += "(" + "、".join(str(c) for c in item["changes"][:6]) + ")"
        names.append(label)
    return {"count": len(items), "names": names}


def summarize_change(summary: Any) -> dict[str, Any] | None:
    """把服务端的 changeSummary 压成"新增 / 删除 / 修改了哪些节点"。参数值服务端本来就不给。"""
    if not isinstance(summary, dict):
        return None
    out: dict[str, Any] = {"fields": summary.get("fields") or []}
    nodes = summary.get("nodes")
    if isinstance(nodes, dict):
        out["nodesAdded"] = _names(nodes.get("added"))
        out["nodesRemoved"] = _names(nodes.get("removed"))
        out["nodesModified"] = _names(nodes.get("modified"), with_changes=True)
    edges = summary.get("edges")
    if isinstance(edges, dict):
        out["edgesAdded"] = len(edges.get("added") or [])
        out["edgesRemoved"] = len(edges.get("removed") or [])
    if summary.get("truncated"):
        out["truncated"] = True
    return out


def summarize_version(row: dict[str, Any]) -> dict[str, Any]:
    change_type = str(row.get("changeType") or "")
    text = CHANGE_TYPE_TEXT.get(change_type, change_type)
    if change_type == "RESTORE" and row.get("restoredFromVersion"):
        text = f"还原到第 {row['restoredFromVersion']} 版"
    return {
        "version": row.get("version"),
        "changeType": change_type,
        "changeText": text,
        "changedBy": row.get("changedByName") or row.get("changedByMemberId"),
        "createdDate": row.get("createdDate"),
        **({"restoredFromVersion": row["restoredFromVersion"]} if row.get("restoredFromVersion") else {}),
        "change": summarize_change(row.get("changeSummary")),
    }


def _snapshot_nodes(snapshot: Any) -> list[dict[str, str]]:
    if not isinstance(snapshot, dict):
        return []
    raw = snapshot.get("flowData")
    try:
        flow = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        return []
    nodes = flow.get("nodes") if isinstance(flow, dict) else None
    out = []
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        data = node.get("data") if isinstance(node.get("data"), dict) else {}
        out.append({"id": str(node.get("id") or ""), "label": str(data.get("label") or data.get("name") or "")})
    return out


# ---- 落盘 -------------------------------------------------------------------


def _persist(payload: Any) -> tuple[str, int]:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    path = os.path.abspath(resolve_data_path(HISTORY_SLUG, time.time(), "json"))
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=os.path.dirname(path),
            prefix=".workflow-history-", suffix=".json.tmp", delete=False,
        ) as f:
            tmp_path = f.name
            f.write(text)
        os.replace(tmp_path, path)
    except OSError as e:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise HistoryError(f"写盘失败 {path}: {e}", code=4) from None
    return path, len(text.encode("utf-8"))


# ---- 子命令 -----------------------------------------------------------------


def _status(proxy: str, api_key: str, flow_id: str) -> dict[str, Any]:
    data = _request("GET", f"{_base(proxy, flow_id)}/version-history", api_key)
    return data if isinstance(data, dict) else {}


def cmd_list(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    status = _status(proxy, api_key, args.workflow_id)
    query = urlencode({"page": args.page, "limit": args.limit})
    payload = _request("GET", f"{_base(proxy, args.workflow_id)}/versions?{query}", api_key)
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise HistoryError("版本列表响应缺少 data 数组", code=65)
    rows = [r for r in payload["data"] if isinstance(r, dict)]
    if not rows and not status.get("enabled"):
        raise HistoryError(
            "这个工作流没开历史记录,也还没有任何历史版本;属主下次经本 skill 修改时会自动打开",
            code=67,
        )
    path, size = _persist(payload)
    return {
        "mode": "list",
        "workflowId": args.workflow_id,
        "enabled": status.get("enabled"),
        "canManage": status.get("canManage"),
        "total": payload.get("total"),
        "page": args.page,
        "returned": len(rows),
        "versions": [summarize_version(r) for r in rows],
        "path": path,
        "bytes": size,
    }


def _get_version(proxy: str, api_key: str, flow_id: str, version: int) -> dict[str, Any]:
    try:
        data = _request("GET", f"{_base(proxy, flow_id)}/versions/{version}", api_key)
    except HistoryError as e:
        if e.status == 404:
            raise HistoryError(f"没有第 {version} 版(不存在,或超过 365 天已被清理)") from None
        raise
    if not isinstance(data, dict):
        raise HistoryError("版本详情响应顶层必须是对象", code=65)
    return data


def cmd_show(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    detail = _get_version(proxy, api_key, args.workflow_id, args.version)
    path, size = _persist(detail)
    snapshot = detail.get("snapshot") if isinstance(detail.get("snapshot"), dict) else {}
    return {
        "mode": "show",
        "workflowId": args.workflow_id,
        **summarize_version(detail),
        "name": snapshot.get("name"),
        "nodes": _snapshot_nodes(snapshot),
        "path": path,
        "bytes": size,
    }


def _diff(proxy: str, api_key: str, flow_id: str, from_v: int, to_v: int) -> dict[str, Any]:
    try:
        data = _request("GET", f"{_base(proxy, flow_id)}/versions/{from_v}/diff/{to_v}", api_key)
    except HistoryError as e:
        if e.status == 404:
            raise HistoryError(f"第 {from_v} 版或第 {to_v} 版不存在(或已过期清理)") from None
        raise
    if not isinstance(data, dict):
        raise HistoryError("对比响应顶层必须是对象", code=65)
    return data


def cmd_diff(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    data = _diff(proxy, api_key, args.workflow_id, args.from_version, args.to_version)
    path, size = _persist(data)
    return {
        "mode": "diff",
        "workflowId": args.workflow_id,
        "from": args.from_version,
        "to": args.to_version,
        "change": summarize_change(data.get("summary")),
        "path": path,
        "bytes": size,
    }


def _latest_version(proxy: str, api_key: str, flow_id: str) -> int | None:
    payload = _request("GET", f"{_base(proxy, flow_id)}/versions?page=1&limit=1", api_key)
    rows = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        version = rows[0].get("version")
        return version if isinstance(version, int) else None
    return None


def _versions_after(proxy: str, api_key: str, flow_id: str, after: int, latest: int) -> list[dict[str, Any]]:
    """第 after 版之后(不含)的那些版本,倒序,最多 NEWER_MAX 条。"""
    limit = min(latest - after, NEWER_MAX)
    query = urlencode({"page": 1, "limit": limit})
    payload = _request("GET", f"{_base(proxy, flow_id)}/versions?{query}", api_key)
    rows = payload.get("data") if isinstance(payload, dict) else None
    return [
        summarize_version(r)
        for r in (rows if isinstance(rows, list) else [])
        if isinstance(r, dict) and isinstance(r.get("version"), int) and r["version"] > after
    ]


def check_expected_latest(
    proxy: str, api_key: str, flow_id: str, expected: int, latest: int, target: int
) -> None:
    """服务端最新版必须就是调用方以为的那一版,否则退出 69。

    典型场景:AI 改完记为第 7 版,用户又在画布上存了第 8、9 版,然后说"撤销刚才的修改"。
    直接还原到第 6 版会把第 8、9 版一起冲掉 —— 预览只列会改回哪些节点,看不出哪些是人改的。
    所以这里把多出来的版本(谁、什么时候、改了什么)摆出来,让调用方先问用户。
    """
    if latest == expected:
        return
    details: dict[str, Any] = {
        "mode": "restore",
        "workflowId": flow_id,
        "targetVersion": target,
        "expectedLatest": expected,
        "latestVersion": latest,
        "restored": False,
    }
    if latest > expected:
        newer = _versions_after(proxy, api_key, flow_id, expected, latest)
        details["newerVersions"] = newer
        if latest - expected > len(newer):
            details["newerTruncated"] = True
        message = (
            f"第 {expected} 版之后又有 {latest - expected} 次保存(最新是第 {latest} 版),"
            f"还原到第 {target} 版会把它们一起撤掉;先问用户,不要直接还原"
        )
    else:
        # 版本号只增不减;比服务端还新说明记错了流程或记错了数,别拿它当依据
        message = f"对话里记的第 {expected} 版比服务端最新的第 {latest} 版还新,版本号对不上;先 list 确认"
    raise HistoryError(message, code=69, details=details)


def cmd_restore(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    status = _status(proxy, api_key, args.workflow_id)
    if status.get("canManage") is False:
        raise HistoryError(
            "只有工作流的创建者可以还原;请让创建者在画布的「历史记录」里操作", code=68
        )
    latest = _latest_version(proxy, api_key, args.workflow_id)
    if latest is None:
        raise HistoryError("这个工作流还没有任何历史版本,无从还原", code=67)
    if args.expect_latest is not None:
        check_expected_latest(proxy, api_key, args.workflow_id, args.expect_latest, latest, args.version)
    if args.version > latest:
        raise HistoryError(f"没有第 {args.version} 版,最新是第 {latest} 版")

    # 预览:当前最新版 → 目标版,就是还原会造成的改动
    preview = None
    if args.version != latest:
        preview = summarize_change(_diff(proxy, api_key, args.workflow_id, latest, args.version).get("summary"))

    result: dict[str, Any] = {
        "mode": "restore",
        "workflowId": args.workflow_id,
        "targetVersion": args.version,
        "latestVersion": latest,
        "willChange": preview,
    }
    if not args.confirm:
        result["restored"] = False
        result["requiresConfirmation"] = True
        return result

    # 乐观锁:取当前 updatedDate 一起送上去,别人在这几秒内保存过就 409,不拿旧画面覆盖
    flow = _request("GET", _base(proxy, args.workflow_id), api_key)
    expected = flow.get("updatedDate") if isinstance(flow, dict) else None
    body = {"expectedUpdatedDate": expected} if expected else {}
    try:
        restored = _request(
            "POST", f"{_base(proxy, args.workflow_id)}/versions/{args.version}/restore", api_key, body
        )
    except HistoryError as e:
        if e.status in (403, 409):
            raise HistoryError(f"还原被拒:{e}", code=68, status=e.status) from None
        raise
    # 服务端内容已经变了:本地基线(若有)不再是服务端原文,下一轮 refine 必须重新 fetch
    mark_edited(args.workflow_id)
    new_latest = _latest_version(proxy, api_key, args.workflow_id)
    path, size = _persist(restored)
    result.update(
        {
            "restored": True,
            "newVersion": new_latest,
            "name": restored.get("name") if isinstance(restored, dict) else None,
            "path": path,
            "bytes": size,
        }
    )
    return result


COMMANDS = {"list": cmd_list, "show": cmd_show, "diff": cmd_diff, "restore": cmd_restore}


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
        summary = COMMANDS[args.command](args, proxy, api_key)
    except HistoryError as e:
        if e.details is not None:
            print(json.dumps(e.details, ensure_ascii=False, indent=2))
        _die(str(e), e.code)
        return
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary.get("path"):
        print(f"Saved full response: {summary['path']} ({summary['bytes']} bytes)")


if __name__ == "__main__":
    main()
