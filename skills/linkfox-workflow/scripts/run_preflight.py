"""linkfox-workflow · 执行前检查 + 执行后业务断言(纯函数,无网络)。

**为什么要有执行前检查**

生成阶段运行时对象(模型 / 表 / 店铺 / 专家 / 子流程 / 通知目标)一律留占位,这是对的;
但带着占位去真跑,结果是确定的:第一个用到它的节点报错,留下一条注定失败的执行记录,
而写表 / 发通知这类副作用可能已经在前面的节点发生了。复盘(2026-10-08)里就是这样反复
"跑 → 报缺凭据 → 让用户去补 → 再跑"。所以执行前按**本 flow 实际用到的节点**逐个查必需
资源,缺了就在调用 Prediction API 之前列出"节点 → 缺什么",不执行。

只查本 flow 用到的节点、只看 flowData 里的值是否为空 —— 不查 model / credential 目录,
不判断绑定的实例是否真的有效(那是运行时的事)。规则与 references/nodes-*.md 的"必填"
逐条对应;references 没写必填的字段不在这里臆造。

LinkFox 自定义节点的 `linkfoxAgentApi` 凭据由后台自动绑定,不在这里查:flowData 里它留空
是常态,报成缺项会把用户引去页面上手工绑一个不需要绑的东西。ExecuteFlow v2.0 也收
`linkfoxAgentApi`,同样在上传时自动绑定,同样不查。

**为什么要有业务断言**

`FINISHED` 只说明"没有节点报错",不说明"该执行的动作执行了"。复盘里 17:36 那次执行
状态 FINISHED,保存基线的节点却根本没跑到。所以执行后额外给出:
- `notReachedNodes`:flow 里有、这次没执行到的节点;
- `actionResults`:通知 / 写表 / 专家节点自己报告的业务状态(通知 status=error 时
  执行状态照样是 FINISHED);
- 调用方用 `--expect-reached` / `--expect-not-reached` 声明的断言及 `businessCheck`。
"""

from __future__ import annotations

import json
from typing import Any

NON_EXEC_NAMES = {"stickyNoteAgentflow"}
START_NAME = "businessStartAgentflow"

# 有业务状态可读的动作节点:节点执行完成 ≠ 动作成功,要看它自己 output 里的 status。
ACTION_NODE_NAMES = {
    "sendNotificationAgentflow",
    "writeFileAgentflow",
    "crossBorderExpertAgentflow",
}


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    # multiOptions 在 flowData 里有时存成 JSON 字符串('["feishu"]')
    if isinstance(value, str) and value.strip().startswith("["):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else []
    return []


def _blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return not value
    return False


def parse_flow_data(flow: dict) -> dict | None:
    """从 GET /chatflows/<id> 的响应里取出 flowData 对象;取不到返回 None。"""
    raw = flow.get("flowData")
    if isinstance(raw, dict):
        data = raw
    elif isinstance(raw, str) and raw.strip():
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
    else:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        return None
    return data


def exec_nodes(flow_data: dict) -> list[dict]:
    """可执行节点(去掉 StickyNote),每项 {nodeId, nodeLabel, name, data}。"""
    out: list[dict] = []
    for node in _as_list(flow_data.get("nodes")):
        n = _as_dict(node)
        data = _as_dict(n.get("data"))
        name = str(data.get("name") or "")
        nid = str(n.get("id") or data.get("id") or "")
        if not nid or name in NON_EXEC_NAMES:
            continue
        out.append(
            {
                "nodeId": nid,
                "nodeLabel": str(data.get("label") or nid),
                "name": name,
                "data": data,
            }
        )
    return out


def start_input_type(flow_data: dict) -> str:
    for node in exec_nodes(flow_data):
        if node["name"] == START_NAME:
            return str(_as_dict(node["data"].get("inputs")).get("startInputType") or "chatInput")
    return ""


def _missing_for_node(name: str, data: dict) -> list[str]:
    """一个节点缺的必需资源(中文说明)。规则来源见各条注释。"""
    inputs = _as_dict(data.get("inputs"))
    missing: list[str] = []

    if name == START_NAME:
        mode = str(inputs.get("startInputType") or "chatInput")
        if mode == "storeAuthorization":
            if _blank(inputs.get("amazonStore")):
                missing.append("授权店铺 amazonStore")
        elif mode == "tableRecordTrigger":
            if _blank(inputs.get("tableId")):
                missing.append("触发数据表 tableId")
    elif name == "agentAgentflow":
        if _blank(inputs.get("agentModel")):
            missing.append("模型 agentModel")
    elif name == "llmAgentflow":
        if _blank(inputs.get("llmModel")):
            missing.append("模型 llmModel")
    elif name == "conditionAgentAgentflow":
        if _blank(inputs.get("conditionAgentModel")):
            missing.append("模型 conditionAgentModel")
    elif name == "retrieverAgentflow":
        stores = _as_list(inputs.get("retrieverKnowledgeDocumentStores"))
        if not stores or any(_blank(_as_dict(s).get("documentStore")) for s in stores):
            missing.append("知识库 documentStore")
    elif name == "executeFlowAgentflow":
        if _blank(inputs.get("executeFlowSelectedFlow")):
            missing.append("目标子流程 executeFlowSelectedFlow")
    elif name == "crossBorderExpertAgentflow":
        if _blank(inputs.get("expertId")):
            missing.append("专家 expertId")
    elif name == "dataReaderAgentflow":
        source = str(inputs.get("sourceType") or "")
        if source == "linkfoxTable" and _blank(inputs.get("tableId")):
            missing.append("读取数据表 tableId")
        elif source == "amazonStore" and _blank(inputs.get("amazonStore")):
            missing.append("授权店铺 amazonStore")
        elif source == "csv" and _blank(inputs.get("csvFile")):
            missing.append("CSV 文件 csvFile")
        elif source == "excel" and _blank(inputs.get("excelFile")):
            missing.append("Excel 文件 excelFile")
    elif name == "writeFileAgentflow":
        dest = str(inputs.get("writeDestination") or "linkfoxTable")
        if dest in {"linkfoxTable", "updateLinkfoxTable"} and _blank(inputs.get("tableId")):
            missing.append("写入数据表 tableId")
        elif dest == "newLinkfoxTable" and _blank(inputs.get("newTableName")):
            missing.append("新表名 newTableName")
    elif name == "sendNotificationAgentflow":
        channels = [str(c) for c in _as_list(inputs.get("channels"))]
        if not channels:
            missing.append("通知渠道 channels")
        if "email" in channels:
            if _blank(inputs.get("recipients")):
                missing.append("邮件收件人 recipients")
        if "feishu" in channels and _blank(inputs.get("feishuWebhook")):
            missing.append("飞书机器人 feishuWebhook")
        if "dingtalk" in channels and _blank(inputs.get("dingtalkWebhook")):
            missing.append("钉钉机器人 dingtalkWebhook")
    return missing


def preflight(flow_data: dict) -> list[dict]:
    """返回缺项清单:[{nodeId, nodeLabel, missing: [...]}];空列表 = 资源齐全。"""
    problems: list[dict] = []
    for node in exec_nodes(flow_data):
        missing = _missing_for_node(node["name"], node["data"])
        if missing:
            problems.append(
                {"nodeId": node["nodeId"], "nodeLabel": node["nodeLabel"], "missing": missing}
            )
    return problems


# ---- 执行后 -----------------------------------------------------------------


def _node_output(item: dict) -> dict:
    payload = _as_dict(item.get("data"))
    return _as_dict(payload.get("output"))


def action_results(executed: Any, flow_data: dict | None) -> list[dict]:
    """通知 / 写表 / 专家节点的业务结果。节点 FINISHED 但 status=error 的情况靠这里暴露。"""
    names = {n["nodeId"]: n["name"] for n in exec_nodes(flow_data or {})}
    out: list[dict] = []
    for item in _as_list(executed):
        it = _as_dict(item)
        nid = str(it.get("nodeId") or "")
        name = names.get(nid) or str(_as_dict(it.get("data")).get("name") or "")
        if name not in ACTION_NODE_NAMES:
            continue
        output = _node_output(it)
        entry: dict[str, Any] = {
            "nodeId": nid,
            "nodeLabel": str(it.get("nodeLabel") or nid),
            "status": str(output.get("status") or ""),
        }
        if name == "sendNotificationAgentflow":
            entry["successChannels"] = _as_list(output.get("successChannels"))
            entry["failedChannels"] = _as_list(output.get("failedChannels"))
        elif name == "writeFileAgentflow" and "recordCount" in output:
            entry["recordCount"] = output.get("recordCount")
        out.append(entry)
    return out


def not_reached(executed: Any, flow_data: dict | None) -> list[dict]:
    """flow 里有、这次没执行到的节点。flowData 拿不到时返回空(不猜)。"""
    if not flow_data:
        return []
    ran = {str(_as_dict(i).get("nodeId") or "") for i in _as_list(executed)}
    return [
        {"nodeId": n["nodeId"], "nodeLabel": n["nodeLabel"]}
        for n in exec_nodes(flow_data)
        if n["nodeId"] not in ran
    ]


def evaluate_assertions(
    executed: Any,
    expect_reached: list[str],
    expect_not_reached: list[str],
    actions: list[dict],
) -> list[dict]:
    """逐条判定。到达 = 节点出现在执行轨迹里且未报错;动作节点还要求自身 status 不是 error。"""
    by_id: dict[str, dict] = {}
    for item in _as_list(executed):
        it = _as_dict(item)
        by_id[str(it.get("nodeId") or "")] = it
    action_by_id = {a["nodeId"]: a for a in actions}

    results: list[dict] = []
    for nid in expect_reached:
        item = by_id.get(nid)
        if item is None:
            results.append({"nodeId": nid, "expect": "reached", "pass": False, "actual": "没有执行到"})
            continue
        status = str(item.get("status") or "").upper()
        if status == "ERROR":
            results.append({"nodeId": nid, "expect": "reached", "pass": False, "actual": "执行到但报错"})
            continue
        action = action_by_id.get(nid)
        if action and action.get("status") == "error":
            results.append(
                {"nodeId": nid, "expect": "reached", "pass": False, "actual": "执行到但动作失败(status=error)"}
            )
            continue
        results.append({"nodeId": nid, "expect": "reached", "pass": True, "actual": f"已执行({status or '无状态'})"})
    for nid in expect_not_reached:
        hit = nid in by_id
        results.append(
            {
                "nodeId": nid,
                "expect": "notReached",
                "pass": not hit,
                "actual": "执行到了" if hit else "没有执行到",
            }
        )
    return results
