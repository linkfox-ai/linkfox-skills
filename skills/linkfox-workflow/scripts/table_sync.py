"""linkfox-workflow · 工作流 ↔ 多维表关联结果的判定(upload_workflow / table_automation 共用)。

一条「订阅」= 哪个工作流,挂在哪本多维表的哪张数据表上,被哪种记录事件触发。订阅分两类:

- 记录触发(`recordCreated` / `recordUpdated` / `recordConditionMet`):登记触发表,表里记录变更推事件。
- 定时任务(`schedule`):Start 是 `scheduleInput` 且带 `linkfoxTableAutomationContext`。排期由 Flowise
  自己的调度器管,订阅只记"挂在哪本多维表 / 哪张表下"(侧栏可见、权限闸门可判),**不登记触发表**,
  所以再次保存回 `UNBOUND` 是正常成功;订阅的 enabled 也不管排期启停。

两条登记路径:

- 方式 A:`POST/PUT /api/v1/chatflows` 时服务端按 Start 节点自动登记,结果在响应头
  `X-Table-Automation-Sync`;**没有这个头 = 这次保存与多维表无关**。
- 方式 B:`POST /api/v1/proxy/table-automations` 直接 upsert,结果在响应体 `tableSync.status`。

**HTTP 2xx ≠ 关联成功**:工作流 / 本地订阅已落库,但多维表侧可能没登记上,那样记录变更根本
不会推事件。所以两个脚本都必须把状态分成"生效 / 未生效",不能只看 HTTP 码。
"""

from __future__ import annotations

import json
from typing import Any

SYNC_HEADER = "x-table-automation-sync"

# 状态 → (是否生效, 给模型 / 用户的一句话)。大小写按服务端原样:disabled / notSaved 是小写开头。
SYNC_STATUS: dict[str, tuple[bool, str]] = {
    "REGISTERED": (True, "首次登记成功,记录变更会触发这条工作流"),
    "UPDATED": (True, "已登记过,触发配置已更新为本次的表"),
    "REASSIGNED": (True, "已从另一本多维表换挂到本次的多维表"),
    "UNBOUND": (True, "触发表已解绑(停用的正常结果),记录变更不再触发"),
    "disabled": (True, "开始节点不再是记录触发(也不是挂在多维表下的定时启动),订阅已停用,多维表侧不再触发"),
    "SKIPPED_NO_NOTEBOOK": (False, "没带 notebookId,多维表侧无处登记,自动化不会跑;补上多维表格 id 后重试"),
    "FAILED": (False, "多维表侧登记失败(拒绝 / 超时等),自动化不会跑;原样重试即可(幂等)"),
    "notSaved": (False, "服务端本地校验没通过,订阅没保存,自动化不会跑;检查开始节点的触发配置"),
}

EVENT_TYPES = ("recordCreated", "recordUpdated", "recordConditionMet")
SCHEDULE_EVENT = "schedule"
# 查询过滤可用的全部 eventType(含定时);EVENT_TYPES 只是记录事件
ALL_EVENT_TYPES = (*EVENT_TYPES, SCHEDULE_EVENT)
EVENT_TEXT = {
    "recordCreated": "新增记录时",
    "recordUpdated": "修改记录时",
    "recordConditionMet": "新增或修改后满足条件时",
    SCHEDULE_EVENT: "定时任务(挂在该表下,按排期跑,记录变更不触发)",
}
# 定时流在 Start 上带的多维表来源上下文;缺 notebookId 就当没挂表
SCHEDULE_CONTEXT_INPUT = "linkfoxTableAutomationContext"
# 定时订阅 tableId 缺失 / 形状不对时服务端存的占位值:前端归不到具体表下
SCHEDULE_TABLE_PLACEHOLDER = "tbl__schedule__"
_SCHEDULE_UNBOUND_MEANING = "定时任务已挂在这本多维表下(定时流不登记触发表,再次保存回 UNBOUND 是正常成功)"
UNSUPPORTED_EVENT_TYPES = ("recordTimeReached",)
OPERATORS = (
    "equal", "notEqual", "contains", "notContains",
    "isGreater", "isLess", "isEmpty", "notEmpty",
)
VALUELESS_OPERATORS = ("isEmpty", "notEmpty")
FIELD_ID_PREFIX = "fld"


def schedule_context(inputs: dict[str, Any] | None) -> dict[str, Any] | None:
    """Start 是挂在多维表下的定时启动时返回 `{notebookId, tableId}`,否则 None。

    关联读的是 `linkfoxTableAutomationContext` 里的 id,**不是** Start 上记录触发那组
    `notebookId` / `tableId`(切到定时时会被显示条件清掉)。缺 notebookId = 普通定时流。
    """
    if not isinstance(inputs, dict) or inputs.get("startInputType") != "scheduleInput":
        return None
    ctx = inputs.get(SCHEDULE_CONTEXT_INPUT)
    if isinstance(ctx, str):
        try:
            ctx = json.loads(ctx)
        except ValueError:
            return None
    if not isinstance(ctx, dict) or not str(ctx.get("notebookId") or "").strip():
        return None
    table_id = str(ctx.get("tableId") or "").strip()
    return {"notebookId": str(ctx["notebookId"]).strip(), "tableId": table_id}


def classify(status: str | None, kind: str = "record") -> dict[str, Any]:
    """把一个同步状态归一成 `{status, effective, meaning}`;未知状态按未生效处理。

    `kind="schedule"` 时 UNBOUND 换成定时流的说法:那是再次保存的正常结果,不是停用。
    """
    raw = (status or "").strip()
    if raw == "UNBOUND" and kind == SCHEDULE_EVENT:
        effective, meaning = True, _SCHEDULE_UNBOUND_MEANING
    elif raw in SYNC_STATUS:
        effective, meaning = SYNC_STATUS[raw]
    else:
        # 新加的状态码在这里认不出来:宁可报"未确认",也不替用户说"已生效"
        effective, meaning = False, f"未知的关联状态 {raw!r},无法确认自动化是否生效"
    return {"status": raw, "effective": effective, "meaning": meaning}
