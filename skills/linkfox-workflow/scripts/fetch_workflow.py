#!/usr/bin/env python3
"""linkfox-workflow · 按 workflowId 从 linkfox-workflow 系统拉回一份 agentflow v2 JSON。

用于对话中给定 `<linkfox-flow-info id="xxx"></linkfox-flow-info>` 时,把该 workflow
的完整 flowData 反查回来落到当前会话 workspace,后续 refine 走
`save_workflow.py --workflow-id <本次 workflowId>` 原地覆盖,
`upload_workflow.py --workflow-id <本次 workflowId>` 直接 PUT 回同一 flowId。

**这个脚本必须每轮 refine 都跑一次**:linkfox-workflow 系统侧的 flowData 才是改动基线,
本地文件只是它的一份缓存(用户在画布上手工调的 `position`、在 UI 上补填的 credential /
model / documentStore 只存在于服务端,拿旧本地文件当基线会把它们整份冲掉)。
`save_workflow.py --workflow-id` 会校验本次落盘的对象仍是这里刚拉下来的原封副本,
所以"跳过 fetch 直接改本地文件"在脚本层就走不通。

流程:
  1. 从环境读取 LinkFox API Key + 代理地址(与 upload 一致)。
  2. GET /api/v1/chatflows/<workflowId> 拿到 workflow 对象。
  3. 解析 flowData(字符串 JSON),做顶层 4 字段骨架校验。
  4. 通过 resolve_data_path 落到会话 data/,文件名不 leak workflowId,只用 slug + ts。
  5. 把 `workflowId -> path` 写进跨会话索引(workflow_identity),并记下本次落盘内容的
     sha256 作为 `serverHash` —— 后续 save 靠它判断这份基线还是不是服务端原文。
  6. stdout 返回 {path, workflowId, name, flowType, bytes, nodes, edges} 以及一行
     `Saved full response: <path> (<bytes> bytes)`,与 save/upload 保持一致。
     `baselineSource` 恒为 `server`,`reusedLocalFile` 只表示**复用了同一份文件名/路径**,
     与内容新鲜度无关 —— 内容永远是这一次 GET 回来的。

CLI:
  python scripts/fetch_workflow.py \
    --workflow-id <flowId>           # 必填。来自 <linkfox-flow-info id="..."/>
    [--slug linkfox-workflow-<s>]   # 可选。文件名前缀,默认 linkfox-workflow
    [--proxy-url <url>]             # 可选。同 upload_workflow.py

退出码:0 成功;1 网络 / 未找到 flow;3 flowData 空;4 写盘失败;
       64 CLI 用法错;65 JSON 非法 / 顶层骨架不合规。
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
from urllib.parse import quote
from urllib.request import Request, urlopen


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import get_api_base, resolve_data_path  # type: ignore  # noqa: E402
from workflow_auth import clean_key, with_auth_hint  # type: ignore  # noqa: E402
from workflow_identity import (  # type: ignore  # noqa: E402
    content_sha256,
    lookup_by_flow_id as lookup_flow_binding,
    register as register_flow_binding,
    save_snapshot,
)


_SLUG_ALLOWED_RE = re.compile(r"^linkfox-workflow(-[a-zA-Z0-9-]+)?$")
_SLUG_DEFAULT = "linkfox-workflow"
_FLOWID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {with_auth_hint(msg)}", file=sys.stderr)
    sys.exit(code)


def _env_first(*names: str) -> str:
    for n in names:
        v = clean_key(os.environ.get(n) or "")
        if v:
            return v
    return ""


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fetch a linkfox-workflow agentflow v2 by workflowId and save to workspace"
    )
    p.add_argument("--workflow-id", required=True)
    p.add_argument("--slug", default=_SLUG_DEFAULT)
    p.add_argument("--proxy-url")
    args = p.parse_args()
    if not _FLOWID_RE.match(args.workflow_id):
        _die(f"--workflow-id 格式非法:{args.workflow_id!r}", 64)
    if not _SLUG_ALLOWED_RE.match(args.slug):
        _die(
            "--slug 必须以 `linkfox-workflow` 开头(合法:`linkfox-workflow` 或 "
            "`linkfox-workflow-<后缀>`,后缀仅允许 [a-zA-Z0-9-])",
            64,
        )
    return args


def _resolve_api_key() -> str:
    api_key = _env_first("LINKFOX_AGENT_API_KEY", "LINKFOXAGENT_API_KEY")
    if not api_key:
        _die("missing LinkFox API key; set LINKFOX_AGENT_API_KEY", 1)
    return api_key


def _proxy_url(cli: str | None) -> str:
    """API 基础地址:CLI `--proxy-url` > `linkfox_paths.get_api_base()`。

    地址来源只有 `get_api_base()` 一处(env `LINKFOX_TOOL_GATEWAY`,缺省
    正式网关)—— 与其余 90+ 个 linkfox skill 共用同一个
    函数,本 skill 不另立环境变量、也不硬编码地址。
    """
    return ((cli or "").strip() or get_api_base()).rstrip("/")


def _get_flow(proxy_url: str, api_key: str, flow_id: str) -> dict[str, Any]:
    url = f"{proxy_url}/api/v1/chatflows/{quote(flow_id, safe='')}"
    req = Request(
        url,
        method="GET",
        headers={
            "Authorization": api_key,
            "User-Agent": "LinkFox-Workflow-Agent/1.0",
        },
    )
    try:
        with urlopen(req, timeout=60) as resp:
            body = resp.read()
    except HTTPError as e:
        payload = e.read().decode("utf-8", errors="replace")[:400]
        if e.code == 404:
            _die(f"workflowId 未找到:{flow_id} (HTTP 404: {payload})", 1)
        _die(f"拉取 workflow 失败 HTTP {e.code}: {payload}", 1)
    except (URLError, TimeoutError, OSError) as e:
        _die(f"拉取 workflow 网络失败:{e}", 1)
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        _die(f"workflow 响应不是合法 JSON:{e}", 65)
    if not isinstance(data, dict):
        _die("workflow 响应顶层必须是对象", 65)
    return data


def _normalize_skeleton(data: Any) -> tuple[dict[str, Any], list[str], list[str]]:
    """归一化 linkfox-workflow 系统存档的 flowData:强校验 nodes/edges,其他字段宽处理。

    linkfox-workflow 系统保存时会规范化 flowData,可能剥掉 description/usecases 或塞进 viewport
    等前端专用字段。fetch 只强校验 nodes/edges,让 refine 链路(拉回 → 改 → 推回)
    始终可用。返回 (data, defaulted_fields, stripped_fields)。
    """
    if not isinstance(data, dict):
        _die("flowData 顶层必须是对象", 65)
    if "nodes" not in data:
        _die("flowData 顶层缺 nodes", 65)
    if "edges" not in data:
        _die("flowData 顶层缺 edges", 65)
    if not (
        isinstance(data["nodes"], list)
        and all(isinstance(x, dict) for x in data["nodes"])
    ):
        _die("flowData.nodes 必须是对象数组", 65)
    if not (
        isinstance(data["edges"], list)
        and all(isinstance(x, dict) for x in data["edges"])
    ):
        _die("flowData.edges 必须是对象数组", 65)
    if not data["nodes"]:
        _die("flowData.nodes 为空", 65)

    defaulted: list[str] = []
    if "description" not in data or not isinstance(data.get("description"), str):
        data["description"] = ""
        defaulted.append("description")
    if "usecases" not in data or not (
        isinstance(data.get("usecases"), list)
        and all(isinstance(x, str) for x in data["usecases"])
    ):
        data["usecases"] = []
        defaulted.append("usecases")

    allowed = {"description", "usecases", "nodes", "edges"}
    stripped = [k for k in list(data.keys()) if k not in allowed]
    for k in stripped:
        data.pop(k, None)

    return data, defaulted, stripped  # type: ignore[return-value]


def _write_atomic(path: str, content: str) -> None:
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=os.path.dirname(path),
            prefix=".workflow-fetch-",
            suffix=".json.tmp",
            delete=False,
        ) as f:
            tmp_path = f.name
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except OSError as e:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        _die(f"写 workflow 失败 {path}: {e}", 4)


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
        sys.stderr.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except AttributeError:
        pass

    args = _parse_args()
    api_key = _resolve_api_key()
    proxy = _proxy_url(args.proxy_url)

    flow = _get_flow(proxy, api_key, args.workflow_id)
    flow_data_raw = flow.get("flowData")
    flow_name = str(flow.get("name") or "").strip()
    flow_type = str(flow.get("type") or "AGENTFLOW").strip().upper()

    if not flow_data_raw:
        _die("workflow 响应缺少 flowData 字段", 3)
    flow_data_obj: Any = None
    if isinstance(flow_data_raw, str):
        try:
            flow_data_obj = json.loads(flow_data_raw)
        except json.JSONDecodeError as e:
            _die(f"flowData 不是合法 JSON:{e.msg} (line {e.lineno} col {e.colno})", 65)
    elif isinstance(flow_data_raw, dict):
        flow_data_obj = flow_data_raw
    else:
        _die("flowData 必须是字符串或对象", 65)

    flow_data_obj, defaulted, stripped = _normalize_skeleton(flow_data_obj)

    # 同一个 workflowId 复用第一次绑定的文件路径(basename 就是 sourceKey,必须稳定);
    # 只有从没绑定过才新建文件,否则重复 fetch 会造出新 sourceKey 并让上传退化成新建。
    # 注意 `reusedLocalFile` 只讲路径复用,内容永远是上面这次 GET 的结果。
    bound = lookup_flow_binding(args.workflow_id)
    reused = bool(bound and os.path.isfile(bound["path"]))
    if reused:
        out_path = os.path.abspath(bound["path"])
    else:
        ts = time.time()
        out_path = os.path.abspath(resolve_data_path(args.slug, ts, "json"))
    final = json.dumps(flow_data_obj, ensure_ascii=False, indent=4)
    _write_atomic(out_path, final)
    fetched_at = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())
    # workflowId 是 workflow 的唯一身份;绑定到刚落盘的文件,后续 refine 无需再传路径。
    # serverHash 记的是"这份文件此刻就是服务端原文" —— save_workflow.py 落盘前会校验它,
    # 所以跳过 fetch 复用旧本地文件的路子在脚本层就走不通。
    register_flow_binding(
        args.workflow_id, out_path, flow_name, flow_type,
        server_hash=content_sha256(final),
    )
    # 回滚用的服务端原文快照(只保留最近几份);写失败不影响 fetch。
    snapshot_path = save_snapshot(args.workflow_id, final)

    summary: dict[str, Any] = {
        "path": out_path,
        "workflowId": args.workflow_id,
        "name": flow_name,
        "flowType": flow_type,
        "bytes": len(final.encode("utf-8")),
        "nodes": len(flow_data_obj["nodes"]),
        "edges": len(flow_data_obj["edges"]),
        "mode": "fetched",
        "baselineSource": "server",
        "fetchedAt": fetched_at,
        "reusedLocalFile": reused,
    }
    if snapshot_path:
        summary["snapshotPath"] = snapshot_path
    if defaulted:
        summary["defaultedFields"] = defaulted
    if stripped:
        summary["strippedFields"] = stripped
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved full response: {out_path} ({summary['bytes']} bytes)")


if __name__ == "__main__":
    main()
