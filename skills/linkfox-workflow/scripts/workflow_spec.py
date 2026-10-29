"""linkfox-workflow · 节点契约表 + 深度结构校验。

**为什么要有这个模块**

`references/*.md` 用几千行散文描述了节点契约:每个节点的 `data.name` / `data.type` /
`version` / `color` / `baseClasses` 是固定值、`inputParams` 不能是空数组、Condition 的
operation 是 `equal` 而不是 `equals`、跨节点引用不能写裸 `.output`……但这些规则**全靠模型
自觉**。模型漏一个,linkfox-workflow 系统导入时通常不报错,而是静默产出坏节点或丢掉一条边,用户在画布上
才发现问题 —— 反馈链条极长。

本模块把散文规则变成落盘前的机械校验:

- `NODE_SPECS` 是节点契约的**单一真相源**(与 references 的表格一一对应)。
- `validate(flow)` 返回 `(errors, warnings)`。error 阻止落盘,warning 只提示。

**error 还是 warning 的判据**:会让 linkfox-workflow 系统静默产出坏 flow 的算 error(未知节点、
data.type 不匹配、边丢锚点、变量指向不存在的节点或不存在的 output 字段、缺
acceptVariable、给没有 Update Flow State 的节点造 UpdateState、Condition
operation 非法);只影响观感或能被 linkfox-workflow 系统规范化修正的算 warning(颜色、version、
edge id 拼写、edgeLabel 缺失、运行时占位被写死)。

改 `NODE_SPECS` 前先同步对应的 `references/nodes-*.md` 表格,反之亦然。
"""

from __future__ import annotations

import copy
import json
import keyword
import re
import sys
from typing import Any, NamedTuple

from input_params_specs import COVERED_NAMES as INPUT_PARAMS_COVERED
from input_params_specs import input_params_for
from table_sync import (
    EVENT_TYPES as RECORD_EVENT_TYPES,
    FIELD_ID_PREFIX,
    OPERATORS as RECORD_OPERATORS,
    SCHEDULE_CONTEXT_INPUT,
    SCHEDULE_TABLE_PLACEHOLDER,
    UNSUPPORTED_EVENT_TYPES as RECORD_UNSUPPORTED_EVENTS,
    VALUELESS_OPERATORS as RECORD_VALUELESS_OPERATORS,
)


class NodeSpec(NamedTuple):
    """一个节点的固定契约。字段与 references/nodes-*.md 的表格逐项对应。"""

    data_type: str
    version: object          # references 里记录的 version 字面值
    color: str
    base_classes: list[str]
    top_type: str            # 顶层 type:agentFlow / iteration / stickyNote
    anchors: list[str]       # outputAnchors[].name;空列表 = 无输出锚点
    edge_label: str = ""     # 单出口节点的约定 edgeLabel(空 = 无约定)
    deprecated: bool = False
    # 运行时 `output` 对象的根字段(references/output-and-state.md 的字段表)。
    # 空 tuple = 该节点没有可引用的 output(End / Iteration)。
    outputs: tuple[str, ...] = ()
    # True = 除上面这些固定字段外还有设计期决定的动态字段(Agent/LLM 的 structured
    # output key、DataReader 的 outputVariableName)。这类节点的未知根字段只报
    # warning,因为脚本不一定能把动态 key 全部解析出来。
    outputs_open: bool = False


# 原生 15 个 + LinkFox 自定义 9 个(8 个业务节点 + CustomPythonFunction)。这张表就是权威源,不要去 Grep linkfox-workflow 系统源码。
#
# `outputs` 一栏是**运行时 output 对象的根字段**,不是锚名。两者极易混淆:
# `data` / `sent` / `written` / `completed` / `submitted` 只是 outputAnchors[].name,
# 用在 edge 的 sourceHandle 里;写成 `{{ x.output.data }}` 运行时不报错,而是原样保留
# 模板 —— 用户在通知或画布上看到字面量。这是本 skill 历史上出过的真实 bug。
NODE_SPECS: dict[str, NodeSpec] = {
    # ---- 原生:开始与批注 ----
    "startAgentflow": NodeSpec(
        "Start", 1.4, "#7EE787", ["Start"], "agentFlow", ["startAgentflow"],
        deprecated=True,
        # startInputType 决定实际出现哪些:chatInput→question、formInput→form、
        # webhookTrigger→webhook(+question)、scheduleInput→question/form。
        outputs=("question", "form", "webhook", "ephemeralMemory", "persistState"),
    ),
    "stickyNoteAgentflow": NodeSpec(
        "StickyNote", 1.0, "#fee440", ["StickyNote"], "stickyNote", [],
    ),
    # ---- 原生:AI 与知识 ----
    "agentAgentflow": NodeSpec(
        "Agent", 3.2, "#4DD0E1", ["Agent"], "agentFlow", ["agentAgentflow"],
        outputs=(
            "content", "timeMetadata", "calledTools", "usageMetadata",
            "responseMetadata", "usedTools", "sourceDocuments", "artifacts",
            "availableTools", "isWaitingForHumanInput", "fileAnnotations",
            "reasonContent",
        ),
        outputs_open=True,  # agentStructuredOutput 的 key 与固定字段同层
    ),
    "llmAgentflow": NodeSpec(
        "LLM", 1.1, "#64B5F6", ["LLM"], "agentFlow", ["llmAgentflow"],
        outputs=(
            "content", "timeMetadata", "calledTools", "usageMetadata",
            "responseMetadata", "artifacts", "fileAnnotations", "reasonContent",
        ),
        outputs_open=True,  # llmStructuredOutput 的 key 与固定字段同层
    ),
    "toolAgentflow": NodeSpec(
        "Tool", 1.2, "#d4a373", ["Tool"], "agentFlow", ["toolAgentflow"],
        outputs=("content", "artifacts"),
    ),
    "retrieverAgentflow": NodeSpec(
        "Retriever", 1.1, "#b8bedd", ["Retriever"], "agentFlow", ["retrieverAgentflow"],
        outputs=("content",),
    ),
    # ---- 原生:控制流 ----
    "conditionAgentflow": NodeSpec(
        "Condition", 1.0, "#FFB938", ["Condition"], "agentFlow", ["0", "1"],
        outputs=("conditions",),
    ),
    "conditionAgentAgentflow": NodeSpec(
        "ConditionAgent", 2.0, "#ff8fab", ["ConditionAgent"], "agentFlow", ["0", "1"],
        outputs=(
            "conditions", "content", "timeMetadata", "usageMetadata",
            "responseMetadata",
        ),
    ),
    "loopAgentflow": NodeSpec(
        "Loop", 1.2, "#FFA07A", ["Loop"], "agentFlow", [],
        outputs=("content", "nodeID", "maxLoopCount"),
    ),
    "iterationAgentflow": NodeSpec(
        "Iteration", 1.0, "#9C89B8", ["Iteration"], "iteration", ["iterationAgentflow"],
        outputs=(),  # output 是 {};子节点结果由执行器迭代处理
    ),
    "humanInputAgentflow": NodeSpec(
        "HumanInput", 1.0, "#6E6EFD", ["HumanInput"], "agentFlow", ["proceed", "reject"],
        outputs=("content", "conditions"),  # conditions 仅恢复后出现
    ),
    # ---- 原生:结束标记 ----
    "endAgentflow": NodeSpec(
        "End", 1.0, "#EF4444", ["End"], "agentFlow", [],
        outputs=(),  # output 是空对象,hideOutput: true
    ),
    # ---- 原生:集成与输出 ----
    "httpAgentflow": NodeSpec(
        "HTTP", 1.1, "#FF7F7F", ["HTTP"], "agentFlow", ["httpAgentflow"],
        outputs=("http",),  # .data / .status / .statusText / .headers
    ),
    "customFunctionAgentflow": NodeSpec(
        "CustomFunction", 1.1, "#E4B7FF", ["CustomFunction"], "agentFlow",
        ["customFunctionAgentflow"],
        outputs=("content",),
    ),
    "executeFlowAgentflow": NodeSpec(
        "ExecuteFlow", 2.0, "#a3b18a", ["ExecuteFlow"], "agentFlow",
        ["executeFlowAgentflow"],
        outputs=(
            "content", "sourceDocuments", "usedTools", "artifacts", "fileAnnotations",
        ),
    ),
    "directReplyAgentflow": NodeSpec(
        "DirectReply", 1.0, "#4DDBBB", ["DirectReply"], "agentFlow", [],
        outputs=("content",),
    ),
    # ---- LinkFox 自定义 8 个 ----
    "businessStartAgentflow": NodeSpec(
        "BusinessStart", 1.8, "#8B5CF6", ["Start"], "agentFlow",
        ["businessStartAgentflow"],
        # 手动启动时 question 恒为 "";storeAuthorization / tableRecordTrigger 各多一个
        # 同名字段(那是**订阅配置的静态回显**,不是本次变更的数据)。
        # 注意:BusinessStart 没有 startState,所以没有 ephemeralMemory / persistState。
        #
        # 后三个只在 tableRecordTrigger **且真的收到了变更载荷**时出现(手动点「启动任务」
        # 跑同一条流时整个不存在),所以引用它们的 flow 要能容忍取不到值:
        #   recordEvent  studio 推来的原始载荷,原样不裁剪(recordId / record / recordByName / …)
        #   rows         同一行翻成 name-keyed 的数组,可直接接 WriteFile
        #   recordRows   rows + recordId + tableId + keyedBy(+ droppedComputedFields / warnings)
        outputs=(
            "question", "storeAuthorization", "tableRecordTrigger",
            "recordEvent", "rows", "recordRows",
        ),
    ),
    "crossBorderExpertAgentflow": NodeSpec(
        "CrossBorderExpert", 1.1, "#2563EB", ["CrossBorderExpert"], "agentFlow",
        ["completed"], edge_label="Completed",
        outputs=(
            "content", "expertId", "status", "messageId", "stopReason", "expertResult",
        ),
    ),
    "dataReaderAgentflow": NodeSpec(
        "DataReader", 1.0, "#0F766E", ["DataReader"], "agentFlow",
        ["data"], edge_label="Data",
        outputs=("content", "status", "rowCount", "truncated"),
        outputs_open=True,  # 外加动态字段 <outputVariableName>(默认 tableData)
    ),
    "fillFormAgentflow": NodeSpec(
        "FillForm", 1.2, "#F59E0B", ["FillForm"], "agentFlow",
        ["submitted"], edge_label="Submitted",
        outputs=("content", "filledForm"),
    ),
    "sendNotificationAgentflow": NodeSpec(
        "SendNotification", 1.1, "#0EA5E9", ["SendNotification"], "agentFlow",
        ["sent"], edge_label="Sent",
        # 注意:没有 details —— 渠道明细只在 content 的 JSON 字符串里。
        outputs=("content", "status", "successChannels", "failedChannels"),
    ),
    "writeFileAgentflow": NodeSpec(
        "WriteFile", 1.4, "#7C3AED", ["WriteFile"], "agentFlow",
        ["written"], edge_label="Written",
        outputs=("content", "status", "target", "recordCount", "result"),
    ),
    "linkfoxHttpAgentflow": NodeSpec(
        "LinkfoxHTTP", 1.0, "#0F766E", ["LinkfoxHTTP"], "agentFlow",
        ["linkfoxHttpAgentflow"],
        outputs=("http",),
    ),
    # LinkFox 新增的 Python 脚本节点(沙箱执行,没有本地回落)。
    #   content  `result` 转成的**字符串**,`{{nodeId}}` 默认取它;不能再往下按字段取
    #   result   `result` 原样保留类型(未赋值为 null)—— 按字段取值走这里
    #   logs     print() 的输出;stderr 不视为失败
    "customPythonFunctionAgentflow": NodeSpec(
        "CustomPythonFunction", 1.0, "#4B8BBE", ["CustomPythonFunction"], "agentFlow",
        ["customPythonFunctionAgentflow"],
        outputs=("content", "result", "logs", "stderr"),
    ),
}

# 只有这 9 个节点提供 `<name>UpdateState[]`(references/output-and-state.md 第 4.2 节)。
# 给别的节点造这个字段等于写了一个运行时永远读不到的配置。
UPDATE_STATE_FIELDS: dict[str, str] = {
    "agentAgentflow": "agentUpdateState",
    "llmAgentflow": "llmUpdateState",
    "toolAgentflow": "toolUpdateState",
    "retrieverAgentflow": "retrieverUpdateState",
    "customFunctionAgentflow": "customFunctionUpdateState",
    "executeFlowAgentflow": "executeFlowUpdateState",
    "loopAgentflow": "loopUpdateState",
    "crossBorderExpertAgentflow": "crossBorderExpertUpdateState",
    "customPythonFunctionAgentflow": "customPythonFunctionUpdateState",
}

# DataReader 的 outputVariableName 与这些固定 output 字段同名时会**覆盖**它们
# (动态属性写在对象字面量末尾)。例如取 `status` 会让 output.status 从 'ok' 变成表格对象。
DATA_READER_FIXED_OUTPUTS = ("content", "status", "rowCount", "truncated")
# 另外这些名字虽然能过运行时校验,但会与系统变量/原型链混淆。
DATA_READER_RESERVED_OUTPUTS = (
    "output", "state", "question", "$flow", "$vars",
    "__proto__", "prototype", "constructor",
)

START_NAMES = {"startAgentflow", "businessStartAgentflow"}
REQUIRED_START_NAME = "businessStartAgentflow"
DEPRECATED_START_NAME = "startAgentflow"
# ui2 表格入口不写 `startInputType=tableRecordTrigger`,而是写 `formInput` + 这个结构化
# 触发器输入(`linkfoxTableAutomationTrigger.kind`)。两种写法都要认成记录触发。
TABLE_AUTOMATION_TRIGGER_INPUT = "linkfoxTableAutomationTrigger"
# 记录触发下"这次变的那一行"的取值入口:节点引用的这三个 output 字段,或 `$webhook.*` /
# `$form.*`(表格入口那套 formInput 载荷)。一个都没用到 = 触发了但没消费那一行。
RECORD_TRIGGER_DATA_OUTPUTS = ("recordEvent", "rows", "recordRows")
# hideOutput: true 的节点 —— 没有输出锚点,不允许有出边。
TERMINAL_NAMES = {"loopAgentflow", "directReplyAgentflow", "endAgentflow"}
NON_EXEC_NAMES = {"stickyNoteAgentflow"}

# Condition 的 operation 枚举,逐字来自组件定义(references/nodes-control-flow.md)。
# 最常见的错法是写成 `equals`。
CONDITION_OPERATIONS: dict[str, set[str]] = {
    "string": {
        "contains", "endsWith", "equal", "notContains", "notEqual",
        "regex", "startsWith", "isEmpty", "notEmpty",
    },
    "number": {
        "smaller", "smallerEqual", "equal", "notEqual",
        "larger", "largerEqual", "isEmpty", "notEmpty",
    },
    "boolean": {"equal", "notEqual"},
}

# 运行时对象一律留占位,不写死 UUID(references/nodes-linkfox-custom.md 检查清单)。
# `newTableNotebookId` **不在**这里:它的默认值 `__new__` 是合法的字面量,不是运行时对象。
# `notebookId` / `tableId` **也不在**这里(缺陷 #7130931254):表能用智能表格 skill 列出来
# 让用户挑,挑完就该写真实 id —— 留空让用户自己去界面上选正是那条缺陷。
PLACEHOLDER_FIELDS = {
    "amazonStore", "expertId", "executeFlowSelectedFlow",
    "FLOWISE_CREDENTIAL_ID", "documentStore",
}

# 选多维表的槽位:两级下拉(多维表格容器 `nbk` → 数据表 `tbl`)。散表的第一级是合成容器
# `__loose__`;存量流程的 notebookId 可能为空,只要 tableId 有值照样能读写。
# 规则对齐后端(2026-10-09 核对):
#   - Flowise 保存只校记录触发的 tableId(`tbl` 开头,否则 400 `Data Table is required on the
#     Start node.`);DataReader / WriteFile 的空表能存进去,跑到节点才报错。
#   - workflow-studio 把 `tbl__` 开头的值当占位(如 `tbl__schedule__`),不是真实表。
#   - workflow-studio 不校 notebookId 的 `nbk` 前缀;但记录触发没带 notebookId 时登记不到多维表侧
#     (`tableSync=SKIPPED_NO_NOTEBOOK`),保存 200、自动化永远不跑。
TABLE_ID_PREFIX = "tbl"
TABLE_ID_PLACEHOLDER_PREFIX = "tbl__"
RECORD_TRIGGER_ROLE = "触发数据表"
NOTEBOOK_ID_PREFIX = "nbk"
LOOSE_NOTEBOOK_ID = "__loose__"
TABLE_SLOT_FIELDS = ("notebookId", "tableId")
# 用户明确说"表以后再在界面上选"时,save_workflow.py 带这个开关放行未选表的槽位。
TABLE_LATER_FLAG = "--table-later"

# credential **类型名**(节点表格里 `credential` 一行的值)。它只能出现在 credential 的
# 类型定义处,绝不能当成 `data.credential` 的值 —— 那个位置要么是空占位,要么是用户在 UI
# 上绑定的凭据实例 UUID。写成类型名时静态校验全绿、导入也不报错,要一直跑到该节点才炸
# "credential not found";历史上真发生过(会话 11b2bb9f,跑到第 15 个节点才定位到)。
CREDENTIAL_TYPE_NAMES = {"linkfoxAgentApi"}

# CrossBorderExpert 的 taskInstruction 经变量替换后发给专家平台,平台侧有 prompt 长度硬上限。
# 早期是 `prompt 必须为字符[0,1000]`(来源是运行时报错原文),现已放宽到 10000。
# 阈值留一成余量取 9000:替换后的实际长度还要算上引用展开的内容,设计期只能卡字面量。
EXPERT_PROMPT_FIELD = "taskInstruction"
EXPERT_PROMPT_HARD_LIMIT = 10000
EXPERT_PROMPT_MAX_CHARS = 9000

# "整体响应引用" —— 这些 output 路径指向的是**整个**上游结果对象(HTTP 响应体、专家结果、
# 表格对象、序列化后的完整 JSON 字符串)。把它们塞进 taskInstruction,运行时会把几十 KB 的
# JSON 展开进 prompt,很容易撞穿上面那个字符上限。
# 判定方式是机械的:引用路径**恰好**停在这些根字段上就拦;继续往下取叶子
# (`.output.http.data.products[0].asin`)则放行。
_WHOLE_RESPONSE_TAILS = {
    "http",           # LinkfoxHTTP / HTTP:整个 http 对象
    "http.data",      # 整个响应体
    "expertResult",   # 上游专家的完整结构化结果
    "content",        # 各节点的"整个结果的 JSON 字符串"
    "tableData",      # DataReader 默认变量名下的整张表
    "filledForm",     # FillForm 的整个表单对象(字段少,但同样应取具体字段)
}

# LinkfoxHTTP 的 body 为这些值时等于"没填" —— 必填参数一个都没传,运行时通常报
# `xxx 为必填参数`。文档确实无请求参数的接口(如 /spApi/authorizedStores)是合法例外,
# 用节点 data.description 里的这句声明放行。
_EMPTY_BODY_LITERALS = {"", "{}", "{ }", "null", "[]"}
NO_BODY_ESCAPE_HATCH = "接口文档无请求参数"

# `{{ <nodeId>.output... }}` 形态的跨节点引用。nodeId 形如 `httpAgentflow_1`。
_NODE_REF_RE = re.compile(r"\{\{\s*([A-Za-z][A-Za-z0-9_]*_\d+)\s*\.\s*output([^}]*)\}\}")
# 任意 `{{ ... }}`,用于判断某个字段是否使用了变量替换。
_ANY_VAR_RE = re.compile(r"\{\{[^}]*\}\}")


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _iter_strings(value: Any, path: str = "") -> list[tuple[str, str]]:
    """把嵌套 inputs 里所有字符串摊平成 [(路径, 值)],用于扫 `{{ }}` 引用。"""
    out: list[tuple[str, str]] = []
    if isinstance(value, str):
        out.append((path, value))
    elif isinstance(value, dict):
        for k, v in value.items():
            out.extend(_iter_strings(v, f"{path}.{k}" if path else str(k)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            out.extend(_iter_strings(v, f"{path}[{i}]"))
    return out


def _accept_variable_fields(input_params: Any) -> set[str]:
    """inputParams 中标了 acceptVariable / acceptNodeOutputAsVariable 的字段名集合。"""
    names: set[str] = set()
    for param in _as_list(input_params):
        p = _as_dict(param)
        if p.get("acceptVariable") or p.get("acceptNodeOutputAsVariable"):
            name = p.get("name")
            if isinstance(name, str):
                names.add(name)
    return names


def _declared_param_names(input_params: Any) -> set[str]:
    return {
        p["name"]
        for p in (_as_dict(x) for x in _as_list(input_params))
        if isinstance(p.get("name"), str)
    }


def _ref_root_field(tail: str) -> str:
    """从 `{{ id.output<tail> }}` 的 tail 里取出 output 的**根字段名**。

    `.http.data` → `http`;`.tableData.rows[0].Order_ID` → `tableData`。
    取不到(裸 `.output`)时返回空串,由裸 output 规则单独报。
    """
    head = tail.strip().lstrip(".").strip()
    for sep in (".", "[", " "):
        idx = head.find(sep)
        if idx >= 0:
            head = head[:idx]
    return head.strip()


def _dynamic_output_keys(name: str, data: dict) -> set[str]:
    """设计期决定、写在 inputs 里的动态 output 根字段。

    - DataReader:`outputVariableName`(留空则运行时兜底为 `tableData`)。
    - Agent / LLM:`<name>StructuredOutput[].key` 会与固定字段同层。
    """
    inputs = _as_dict(data.get("inputs"))
    keys: set[str] = set()
    if name == "dataReaderAgentflow":
        raw = inputs.get("outputVariableName")
        keys.add(raw.strip() if isinstance(raw, str) and raw.strip() else "tableData")
    elif name in ("agentAgentflow", "llmAgentflow"):
        field = "agentStructuredOutput" if name == "agentAgentflow" else "llmStructuredOutput"
        for item in _as_list(inputs.get(field)):
            key = _as_dict(item).get("key")
            if isinstance(key, str) and key.strip():
                keys.add(key.strip())
    return keys


def _check_output_field_refs(
    nodes: list, node_by_id: dict[str, dict], errors: list[str], warnings: list[str]
) -> None:
    """`{{ <nodeId>.output.<字段> }}` 的根字段必须真实存在于该节点的运行时 output。

    **为什么单独有这一条**:引用一个不存在的字段时,linkfox-workflow 系统运行时既不报错也不替换,
    模板原样留在正文里 —— 用户在飞书通知或多维表里看到字面量 `{{ x.output.data }}`,
    而 agent 这边一路绿灯。历史上真实踩过的坑是把**输出锚名当成了 output 字段**:
    `data` / `sent` / `written` / `completed` / `submitted` 只是 outputAnchors[].name,
    只能出现在 edge 的 sourceHandle 里。

    分级:锚名冲突和"该节点没有任何可引用 output"是 error(确定错);
    `outputs_open` 节点(Agent / LLM 的 structured output、DataReader 的
    outputVariableName)的未知根字段只报 warning —— 动态 key 未必都能从 inputs 解析出来。
    """
    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id") or "<node>"
        data = _as_dict(n.get("data"))
        if data.get("name") in NON_EXEC_NAMES:
            continue

        for path, text in _iter_strings(_as_dict(data.get("inputs"))):
            if not _ANY_VAR_RE.search(text):
                continue
            for ref_id, tail in _NODE_REF_RE.findall(text):
                target = node_by_id.get(ref_id)
                if target is None:
                    continue  # 节点不存在,已由 _check_variable_refs 报过
                target_data = _as_dict(target.get("data"))
                target_name = target_data.get("name")
                spec = NODE_SPECS.get(target_name) if isinstance(target_name, str) else None
                if spec is None:
                    continue  # 未注册节点,已由契约检查报过
                field = _ref_root_field(tail)
                if not field:
                    continue  # 裸 .output,已由 _check_variable_refs 报过

                allowed = set(spec.outputs) | _dynamic_output_keys(target_name, target_data)
                if field in allowed:
                    continue

                if field in spec.anchors:
                    hint = (
                        f"改用真实字段 {sorted(allowed)}"
                        if allowed
                        else "该节点没有可引用的 output"
                    )
                    errors.append(
                        f"{nid} inputs.{path} 引用了 {ref_id}.output.{field},但 "
                        f"{field!r} 是 {target_name} 的**输出锚名**(只能用在 edge 的 "
                        f"sourceHandle),不是 output 字段;运行时不会替换该模板。{hint}"
                    )
                elif not spec.outputs:
                    errors.append(
                        f"{nid} inputs.{path} 引用了 {ref_id}.output.{field},但 "
                        f"{target_name} 没有任何可引用的 output(运行时是空对象)"
                    )
                elif spec.outputs_open:
                    warnings.append(
                        f"{nid} inputs.{path} 引用了 {ref_id}.output.{field},"
                        f"不在 {target_name} 已知的 output 字段 {sorted(allowed)} 中;"
                        "若不是本节点动态产生的字段,运行时不会替换该模板"
                    )
                else:
                    errors.append(
                        f"{nid} inputs.{path} 引用了 {ref_id}.output.{field},但 "
                        f"{target_name} 的 output 只有 {sorted(allowed)};"
                        "运行时不会替换该模板(见 references/output-and-state.md)"
                    )


def _check_state_writes(nodes: list, errors: list[str], warnings: list[str]) -> None:
    """`<name>UpdateState[]` 与 `startState` 只存在于特定节点上。

    只有 9 个节点提供 `UpdateState` 数组;给别的节点写一个,linkfox-workflow 系统会直接忽略 ——
    模型以为结果进了 `$flow.state`,下游 `{{$flow.state.x}}` 永远是空。
    同理 `BusinessStart` 的面板 schema 里没有 `startState`,写了也不会有初始状态。
    """
    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id") or "<node>"
        data = _as_dict(n.get("data"))
        name = data.get("name")
        if not isinstance(name, str) or name not in NODE_SPECS:
            continue
        inputs = _as_dict(data.get("inputs"))
        expected = UPDATE_STATE_FIELDS.get(name)

        for key in inputs:
            if not key.endswith("UpdateState"):
                continue
            if expected is None:
                errors.append(
                    f"{nid} inputs.{key} 不存在:{name} 没有 Update Flow State 字段"
                    f"(只有 {sorted(UPDATE_STATE_FIELDS)} 这 8 个节点有);"
                    "该配置会被忽略,结果不会进 $flow.state"
                )
            elif key != expected:
                errors.append(
                    f"{nid} inputs.{key} 字段名不对,{name} 的 Update Flow State "
                    f"字段是 {expected!r}"
                )

        if name == REQUIRED_START_NAME:
            for key in ("startState", "startPersistState", "startEphemeralMemory"):
                if key in inputs:
                    errors.append(
                        f"{nid} inputs.{key} 不存在:BusinessStart 的构造函数把它从面板 "
                        "schema 里删掉了,写了不会生效。初始 Flow State 恒为空对象,"
                        "state key 只能由下游节点在运行时创建"
                        "(见 references/output-and-state.md 第 4.1 节)"
                    )

        if name == "dataReaderAgentflow":
            raw = inputs.get("outputVariableName")
            if isinstance(raw, str) and raw.strip():
                var = raw.strip()
                if var in DATA_READER_FIXED_OUTPUTS:
                    errors.append(
                        f"{nid} inputs.outputVariableName={var!r} 与 DataReader 的固定 "
                        f"output 字段重名,会把 output.{var} 覆盖成表格对象;"
                        f"换一个名字(禁用 {list(DATA_READER_FIXED_OUTPUTS)})"
                    )
                elif var in DATA_READER_RESERVED_OUTPUTS:
                    warnings.append(
                        f"{nid} inputs.outputVariableName={var!r} 与系统变量或原型链字段"
                        "同名,容易混淆;建议换成表达数据内容的 camelCase 名字"
                    )
                elif not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", var):
                    warnings.append(
                        f"{nid} inputs.outputVariableName={var!r} 含点号/方括号/空格等"
                        "字符,会被变量解析器当成路径分隔符;建议用 "
                        "^[A-Za-z_][A-Za-z0-9_]*$ 的 camelCase"
                    )


def validate(flow: dict) -> tuple[list[str], list[str]]:
    """深度校验一份 agentflow v2。

    返回 `(errors, warnings)`。这里只做"能机械判定"的规则;语义层面(prompt 写得好不好、
    节点选得对不对)不在范围内。骨架校验(顶层 4 字段)由 save_workflow.py 先跑。
    """
    errors: list[str] = []
    warnings: list[str] = []
    nodes = _as_list(flow.get("nodes"))
    edges = _as_list(flow.get("edges"))

    node_by_id: dict[str, dict] = {}
    name_by_id: dict[str, str] = {}
    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id")
        if isinstance(nid, str) and nid:
            node_by_id[nid] = n
            dn = _as_dict(n.get("data")).get("name")
            name_by_id[nid] = dn if isinstance(dn, str) else ""

    _check_node_contracts(nodes, errors, warnings)
    _check_variable_refs(nodes, node_by_id, errors, warnings)
    _check_output_field_refs(nodes, node_by_id, errors, warnings)
    _check_state_writes(nodes, errors, warnings)
    _check_linkfox_http_body(nodes, errors, warnings)
    _check_expert_prompt(nodes, errors, warnings)
    _check_condition_inputs(nodes, errors)
    _check_python_function(nodes, node_by_id, errors, warnings)
    _check_sandbox_env_vars(nodes, errors, warnings)
    _check_iteration_children(nodes, name_by_id, errors, warnings)
    _check_starting_nodes(nodes, edges, name_by_id, errors)
    _check_edge_metadata(edges, name_by_id, errors, warnings)
    _check_record_trigger_consumption(nodes, edges, errors, warnings)
    _check_table_slots(nodes, errors, warnings)
    _check_record_trigger_config(nodes, errors, warnings)
    _check_schedule_table_context(nodes, errors, warnings)
    _check_condition_value_types(nodes, warnings)
    _check_exclusive_branch_merge(edges, name_by_id, warnings)
    return errors, warnings


# CustomPythonFunction 的 `output.result` **保留 Python 原类型**(output-and-state.md)。
# 把它引用进 Condition 的比较值:复盘(2026-10-08,executionId f9e2fcea…)里布尔值进
# string 比较报 `output.replace is not a function`,改成字符串后消失。根因(变量替换还是
# Condition 输入处理)尚未定位,其它类型组合也没逐一验证 —— 所以只给 warning,不拦。
_PY_RESULT_REF_RE = re.compile(
    r"\{\{\s*(customPythonFunctionAgentflow_\d+)\s*\.\s*output\s*\.\s*result\b[^}]*\}\}"
)


def _check_condition_value_types(nodes: list, warnings: list[str]) -> None:
    for node in nodes:
        n = _as_dict(node)
        data = _as_dict(n.get("data"))
        if data.get("name") != "conditionAgentflow":
            continue
        nid = n.get("id") or "<condition>"
        for cidx, cond in enumerate(_as_list(_as_dict(data.get("inputs")).get("conditions"))):
            c = _as_dict(cond)
            for side in ("value1", "value2"):
                text = c.get(side)
                if not isinstance(text, str) or not _PY_RESULT_REF_RE.search(text):
                    continue
                warnings.append(
                    f"{nid} conditions[{cidx}].{side} 引用了 CustomPythonFunction 的 output.result"
                    "(保留 Python 原类型)。已观察到布尔值进 Condition 报 "
                    "`output.replace is not a function`;已验证可行的写法是让 Python 把该字段"
                    "转成字符串(如 \"true\"/\"false\")再用 string 比较。其它类型组合未验证,"
                    "执行后请核对实际走的分支"
                )


_BRANCH_NODE_NAMES = {"conditionAgentflow", "conditionAgentAgentflow", "humanInputAgentflow"}


def _check_exclusive_branch_merge(
    edges: list, name_by_id: dict[str, str], warnings: list[str]
) -> None:
    """同一分支节点的不同出口,下游汇到同一个多入边节点 → warning。

    复盘(2026-10-08)里互斥分支共用的保存节点静态合法,运行时没被执行;拆成每个分支各自
    一份后正常。引擎的汇合语义(等全部前驱 / 任一前驱)尚未确认,不能据此禁止所有汇合,
    所以只提示,并给出执行后核对的办法。
    """
    out_edges: dict[str, list[dict]] = {}
    in_degree: dict[str, int] = {}
    for edge in edges:
        e = _as_dict(edge)
        s, t = e.get("source"), e.get("target")
        if isinstance(s, str) and isinstance(t, str):
            out_edges.setdefault(s, []).append(e)
            in_degree[t] = in_degree.get(t, 0) + 1

    for bid, bname in name_by_id.items():
        if bname not in _BRANCH_NODE_NAMES:
            continue
        reach_by_handle: dict[str, set[str]] = {}
        for e in out_edges.get(bid, []):
            handle = str(e.get("sourceHandle") or "")
            seen = reach_by_handle.setdefault(handle, set())
            stack = [e.get("target")]
            while stack:
                cur = stack.pop()
                if not isinstance(cur, str) or cur in seen or cur == bid:
                    continue
                seen.add(cur)
                stack.extend(x.get("target") for x in out_edges.get(cur, []))
        if len(reach_by_handle) < 2:
            continue
        counts: dict[str, int] = {}
        for reached in reach_by_handle.values():
            for nid in reached:
                counts[nid] = counts.get(nid, 0) + 1
        for nid in sorted(counts):
            if counts[nid] >= 2 and in_degree.get(nid, 0) >= 2:
                warnings.append(
                    f"{nid} 同时是分支节点 {bid} 多个出口的下游(互斥分支汇合)。已观察到这种"
                    "汇合节点运行时未被执行;若它是必须发生的动作(写表 / 通知等),建议每个分支"
                    "各接一份,或执行时用 run_workflow.py --expect-reached 核对它确实执行到"
                )


def is_record_trigger(start_inputs: dict) -> bool:
    """BusinessStart 是不是多维表格记录触发。

    两条来路各留一个痕迹,取**或**:创建向导写 `startInputType=tableRecordTrigger`;
    ui2 表格入口写 `startInputType=formInput` + 结构化的 `linkfoxTableAutomationTrigger`
    (kind 为 `schedule` 时是定时,不算记录触发)。
    """
    if start_inputs.get("startInputType") == "tableRecordTrigger":
        return True
    trigger = _as_dict(start_inputs.get(TABLE_AUTOMATION_TRIGGER_INPUT))
    kind = trigger.get("kind")
    return isinstance(kind, str) and bool(kind) and kind != "schedule"


def _check_record_trigger_consumption(
    nodes: list, edges: list, errors: list[str], warnings: list[str]
) -> None:
    """记录触发的流程必须真的用上"这次变的那一行"。

    缺陷 #7114401338 的后半句:AI 生成时把记录触发流当成手动流来写,下游去读
    `<start>.output.question`(恒为空串)或者干脆不读触发数据,流程每次被触发都在
    处理空输入,运行时不报错。
    """
    start = next(
        (
            _as_dict(n)
            for n in nodes
            if _as_dict(_as_dict(n).get("data")).get("name") == REQUIRED_START_NAME
        ),
        None,
    )
    if start is None:
        return
    sid = start.get("id")
    if not isinstance(sid, str) or not is_record_trigger(
        _as_dict(_as_dict(start.get("data")).get("inputs"))
    ):
        return

    consumed = False
    for node in nodes:
        n = _as_dict(node)
        if n.get("id") == sid:
            continue
        nid = n.get("id") or "<node>"
        for path, text in _iter_strings(_as_dict(_as_dict(n.get("data")).get("inputs"))):
            if "$webhook." in text or "$form." in text:
                consumed = True
            for ref_id, tail in _NODE_REF_RE.findall(text):
                if ref_id != sid:
                    continue
                field = _ref_root_field(tail)
                if field in RECORD_TRIGGER_DATA_OUTPUTS:
                    consumed = True
                elif field == "question":
                    errors.append(
                        f"{nid} inputs.{path} 引用了 {sid}.output.question,但这是多维表格"
                        "记录触发流程,question 恒为空串;触发的那一行要从 "
                        f"{sid}.output.recordEvent.recordByName.<字段名> / "
                        f"{sid}.output.rows 取(见 references/nodes-linkfox-custom.md"
                        "「记录触发时怎么取这次变的那一行」)"
                    )

    # BusinessStart 直连 WriteFile:WriteFile 自己读上一步的 rows,不需要变量引用。
    if not consumed:
        name_by_id = {
            _as_dict(n).get("id"): _as_dict(_as_dict(n).get("data")).get("name")
            for n in nodes
        }
        consumed = any(
            _as_dict(e).get("source") == sid
            and name_by_id.get(_as_dict(e).get("target")) == "writeFileAgentflow"
            for e in edges
        )

    if not consumed:
        warnings.append(
            f"{sid} 是多维表格记录触发,但下游没有任何节点用到触发的那一行"
            f"({sid}.output.recordEvent / rows / recordRows 都没被引用,也没有直连 "
            "WriteFile);流程会被触发,却不知道是哪一行变了。若确实只需要"
            "「有变化就通知」可忽略本条"
        )


def table_slots(flow: dict) -> list[dict]:
    """流程里每一个"要选多维表"的槽位。

    返回 `[{nodeId, label, role, notebookId, tableId}]`,只收当前分支真的会用到表的节点:
    BusinessStart 记录触发、DataReader `sourceType=linkfoxTable`、WriteFile 写已有表 /
    改已有行。ui2 表格入口的 formInput 流由界面带着订阅上下文建好,表已绑定,不算待选槽位。
    """
    slots: list[dict] = []
    for raw in _as_list(flow.get("nodes")):
        n = _as_dict(raw)
        data = _as_dict(n.get("data"))
        inputs = _as_dict(data.get("inputs"))
        name = data.get("name")
        role = ""
        if name == REQUIRED_START_NAME and inputs.get("startInputType") == "tableRecordTrigger":
            role = RECORD_TRIGGER_ROLE
        elif name == "dataReaderAgentflow" and inputs.get("sourceType") == "linkfoxTable":
            role = "读取数据表"
        elif name == "writeFileAgentflow" and (
            inputs.get("writeDestination") or "linkfoxTable"
        ) in {"linkfoxTable", "updateLinkfoxTable"}:
            role = "写入数据表"
        if not role:
            continue
        slots.append({
            "nodeId": n.get("id"),
            "label": data.get("label") or name,
            "role": role,
            "notebookId": inputs.get("notebookId"),
            "tableId": inputs.get("tableId"),
        })
    return slots


def is_real_table_id(value: Any) -> bool:
    """与 workflow-studio `BusinessStartTriggerParser.isRealTableId` 同一条判据。"""
    return (
        isinstance(value, str)
        and value.strip().startswith(TABLE_ID_PREFIX)
        and not value.strip().startswith(TABLE_ID_PLACEHOLDER_PREFIX)
    )


# 用户本轮在对话里亲手给了机器人地址 / 加签密钥时,save_workflow.py 带这个开关放行。
SECRETS_FROM_USER_FLAG = "--secrets-from-user"


def _secret_param_names(data: dict) -> set[str]:
    """节点里 `type=password` 的字段名:取自 inputParams,再并上代填模板(基线可能没带)。"""
    names: set[str] = set()
    params = _as_list(data.get("inputParams"))
    template = input_params_for(str(data.get("name") or ""), data.get("inputs"))
    for p in params + _as_list(template):
        pd = _as_dict(p)
        if pd.get("type") == "password" and isinstance(pd.get("name"), str):
            names.add(pd["name"])
    return names


def _secret_values(flow: dict) -> dict[tuple[str, str], Any]:
    """{(nodeId, 字段名): 值},只收 password 字段。"""
    out: dict[tuple[str, str], Any] = {}
    for node in _as_list(flow.get("nodes")):
        n = _as_dict(node)
        data = _as_dict(n.get("data"))
        inputs = _as_dict(data.get("inputs"))
        nid = n.get("id")
        if not isinstance(nid, str):
            continue
        for key in _secret_param_names(data):
            if key in inputs:
                out[(nid, key)] = inputs[key]
    return out


def secret_value_changes(baseline: dict | None, flow: dict) -> list[str]:
    """password 字段(飞书 / 钉钉机器人地址、加签密钥等)里不是来自基线的值。

    缺陷 #7130761097:同一会话里给 A 配过飞书机器人地址,生成新流程 B 时 agent 把 A 的
    地址原样写进了 B,通知发进了 A 的群。这类值只能是用户在界面上填的(refine 时随 fetch
    基线带回来),或用户本轮亲口给的 —— 不能是 agent 从会话 / memory 里"记得"的。

    - 新建(baseline=None):任何非空值都算。
    - refine:同节点同字段与基线不同的非空值算;基线里有值、这一轮被清空也算(那是用户配好的)。
    返回的描述只带节点 id 和字段名,**不带值**(值本身就是密钥)。
    """
    old = _secret_values(baseline) if baseline is not None else {}
    new = _secret_values(flow)
    changes: list[str] = []
    for (nid, key), value in sorted(new.items()):
        before = old.get((nid, key))
        if _is_blank_param(value):
            if not _is_blank_param(before):
                changes.append(f"{nid} inputs.{key} 被清空(基线里是用户配好的值)")
            continue
        if before != value:
            where = "不在基线里" if _is_blank_param(before) else "与基线不同"
            changes.append(f"{nid} inputs.{key} 填了值,且{where}")
    return changes


def unselected_table_slots(flow: dict) -> list[dict]:
    """还没选好表的槽位,每项多带一个 `missing`(给人看的缺什么)。

    - tableId 空着,或是 `tbl__` 占位值;
    - 记录触发缺 notebookId:后端保存成功但登记不到多维表侧,触发永远不跑,所以同样算没选好。
      读表 / 写表运行时只认 tableId,缺 notebookId 只是界面显示问题,由 `_check_table_slots` 给 warning。
    """
    out: list[dict] = []
    for s in table_slots(flow):
        if _is_blank_param(s["tableId"]):
            missing = "tableId 为空"
        elif isinstance(s["tableId"], str) and s["tableId"].strip().startswith(TABLE_ID_PLACEHOLDER_PREFIX):
            missing = f"tableId={s['tableId']!r} 是占位值,不是真实数据表"
        elif s["role"] == RECORD_TRIGGER_ROLE and _is_blank_param(s["notebookId"]):
            missing = "notebookId 为空(保存能成功,但登记不到多维表侧,触发永远不跑)"
        else:
            continue
        out.append({**s, "missing": missing})
    return out


def _check_table_slots(nodes: list, errors: list[str], warnings: list[str]) -> None:
    """已填的表 id 必须形状正确。没填的由 save_workflow.py 按 `unselected_table_slots` 拦。

    两级填反(`tableId` 填了 `nbk…`)是最常见的错:运行时读写只认 `tbl`,服务端保存直接 400。
    """
    for slot in table_slots({"nodes": nodes}):
        nid, table_id, notebook_id = slot["nodeId"], slot["tableId"], slot["notebookId"]
        if not _is_blank_param(table_id):
            if not isinstance(table_id, str) or not table_id.startswith(TABLE_ID_PREFIX):
                errors.append(
                    f"{nid} inputs.tableId={table_id!r} 不是数据表 id(必须以 `{TABLE_ID_PREFIX}` 开头);"
                    f"`{NOTEBOOK_ID_PREFIX}` 开头的是多维表格容器,应填到 notebookId"
                )
            if _is_blank_param(notebook_id) and slot["role"] != RECORD_TRIGGER_ROLE:
                # 读表 / 写表运行时只认 tableId,存量流程 notebookId 本来就可能为空,所以不拦;
                # 但新填的表漏了第一级,界面上第二级会显示不出来。记录触发缺它是硬伤,
                # 由 unselected_table_slots 交给 save_workflow.py 拦。
                warnings.append(
                    f"{nid} 填了 tableId 却没填 notebookId;选表是两级下拉,"
                    "第一级应填该数据表所在的多维表格 id(散表填 `__loose__`),否则界面上第二级显示不出来"
                )
        if not _is_blank_param(notebook_id) and not (
            isinstance(notebook_id, str)
            and (notebook_id.startswith(NOTEBOOK_ID_PREFIX) or notebook_id == LOOSE_NOTEBOOK_ID)
        ):
            # 后端不校前缀,这里也不拦;查表 skill 给的值只会是这两种,出现别的多半是填错了位置。
            warnings.append(
                f"{nid} inputs.notebookId={notebook_id!r} 不是多维表格 id"
                f"(必须以 `{NOTEBOOK_ID_PREFIX}` 开头,散表用 `{LOOSE_NOTEBOOK_ID}`)"
            )


def _multi_value(value: Any) -> list[str]:
    """多值字段既可能是真数组,也可能是 JSON 字符串(`"[\\"状态\\"]"`),两种服务端都认。"""
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return [text]
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def _check_schedule_table_context(nodes: list, errors: list[str], warnings: list[str]) -> None:
    """定时启动挂到多维表下的 `linkfoxTableAutomationContext`(docs/WORKFLOW-TABLE-BINDING-API.md §3.6)。

    关联读的是上下文里的 notebookId / tableId,不是 Start 上记录触发那组。缺 notebookId 服务端
    当成没挂表;tableId 缺失 / 形状不对存成占位 `tbl__schedule__`,侧栏归不到具体表、权限闸门
    也不探。都不影响排期本身,所以只给 warning;tableId 填成 `nbk…` 是两级填反,算 error。
    """
    for raw in nodes:
        n = _as_dict(raw)
        data = _as_dict(n.get("data"))
        if data.get("name") != REQUIRED_START_NAME:
            continue
        inputs = _as_dict(data.get("inputs"))
        if SCHEDULE_CONTEXT_INPUT not in inputs:
            continue
        nid = n.get("id")
        ctx_raw = inputs.get(SCHEDULE_CONTEXT_INPUT)
        if isinstance(ctx_raw, str) and ctx_raw.strip():
            try:
                ctx_raw = json.loads(ctx_raw)
            except json.JSONDecodeError:
                errors.append(f"{nid} {SCHEDULE_CONTEXT_INPUT} 不是合法 JSON 对象")
                continue
        ctx = _as_dict(ctx_raw)
        if inputs.get("startInputType") != "scheduleInput":
            if ctx:
                warnings.append(
                    f"{nid} {SCHEDULE_CONTEXT_INPUT} 只对定时启动(scheduleInput)生效,当前启动方式下会被忽略"
                )
            continue
        notebook_id = ctx.get("notebookId")
        table_id = ctx.get("tableId")
        if _is_blank_param(notebook_id):
            warnings.append(
                f"{nid} {SCHEDULE_CONTEXT_INPUT} 缺 notebookId:服务端当成没挂表,"
                "这条定时流不会出现在多维表侧栏;要挂表就补上多维表格 id(散表 `__loose__`)"
            )
            continue
        if _is_blank_param(table_id):
            warnings.append(
                f"{nid} {SCHEDULE_CONTEXT_INPUT} 没带 tableId:会存成占位 `{SCHEDULE_TABLE_PLACEHOLDER}`,"
                "侧栏归不到具体表、权限闸门也不探;建议填挂载表的真实 `tbl…`"
            )
        elif not isinstance(table_id, str) or not table_id.startswith(TABLE_ID_PREFIX):
            errors.append(
                f"{nid} {SCHEDULE_CONTEXT_INPUT}.tableId={table_id!r} 不是数据表 id(必须以 `{TABLE_ID_PREFIX}` 开头);"
                f"`{NOTEBOOK_ID_PREFIX}` 开头的是多维表格容器,应填到 notebookId"
            )


def _check_record_trigger_config(nodes: list, errors: list[str], warnings: list[str]) -> None:
    """记录触发的事件 / 条件 / 字段 id,规则对齐订阅接口的 400(docs/WORKFLOW-TABLE-BINDING-API.md §5)。

    事件 / 算子 / 字段 id 前缀 / 间隔写错是 error:怎么写都是错的。条件缺字段名或值只给 warning:
    refine 时开始节点的 inputs 从 fetch 基线拷回,基线里用户没配完的条件不能把整次保存拦死;
    这种配置保存时服务端会回 `notSaved`,上传 stdout 的 `tableAutomation.effective=false`
    会再说一遍。新生成的流程不应出现这条 warning。
    """
    for raw in nodes:
        n = _as_dict(raw)
        data = _as_dict(n.get("data"))
        inputs = _as_dict(data.get("inputs"))
        if data.get("name") != REQUIRED_START_NAME or inputs.get("startInputType") != "tableRecordTrigger":
            continue
        nid = n.get("id")
        event = inputs.get("recordEventType") or "recordCreated"
        if event in RECORD_UNSUPPORTED_EVENTS:
            errors.append(
                f"{nid} recordEventType={event!r} 暂不支持(到达记录中的时间),服务端会拒绝;"
                f"只能用 {' / '.join(RECORD_EVENT_TYPES)}"
            )
            continue
        if event not in RECORD_EVENT_TYPES:
            errors.append(f"{nid} recordEventType={event!r} 非法,只能用 {' / '.join(RECORD_EVENT_TYPES)}")
            continue
        interval = inputs.get("recordCheckIntervalMinutes")
        if not _is_blank_param(interval) and not (
            isinstance(interval, (int, float)) and not isinstance(interval, bool)
            and int(interval) == interval and interval > 0
        ):
            errors.append(f"{nid} recordCheckIntervalMinutes={interval!r} 必须是正整数(默认 10)")

        if event == "recordUpdated":
            names = _multi_value(inputs.get("recordWatchFieldNames"))
            ids = _multi_value(inputs.get("recordWatchFieldIds"))
            for fid in ids:
                if not fid.startswith(FIELD_ID_PREFIX):
                    errors.append(f"{nid} recordWatchFieldIds 里的 {fid!r} 不是字段 id(必须以 `{FIELD_ID_PREFIX}` 开头)")
            if names and not ids:
                warnings.append(
                    f"{nid} 监听字段只写了名字没写 recordWatchFieldIds:用户改列名后订阅会静默失效。"
                    "新建时用 listFields 的 fieldId 一并写上;存量流程补 id 属于改触发配置,先问用户"
                )
        elif event == "recordConditionMet":
            field = inputs.get("recordConditionFieldName")
            op = inputs.get("recordConditionOperator") or "equal"
            ids = _multi_value(inputs.get("recordConditionFieldId"))
            if _is_blank_param(field):
                warnings.append(
                    f"{nid} 条件触发缺 recordConditionFieldName(条件字段名):订阅登记会失败,自动化不会跑"
                )
            if op not in RECORD_OPERATORS:
                errors.append(f"{nid} recordConditionOperator={op!r} 非法,只能用 {' / '.join(RECORD_OPERATORS)}")
            elif op not in RECORD_VALUELESS_OPERATORS and _is_blank_param(inputs.get("recordConditionValue")):
                warnings.append(
                    f"{nid} 算子 {op} 需要 recordConditionValue(空字符串视为未填):订阅登记会失败,自动化不会跑"
                )
            for fid in ids:
                if not fid.startswith(FIELD_ID_PREFIX):
                    errors.append(f"{nid} recordConditionFieldId 里的 {fid!r} 不是字段 id(必须以 `{FIELD_ID_PREFIX}` 开头)")
            if not _is_blank_param(field) and not ids:
                warnings.append(
                    f"{nid} 条件字段只写了名字没写 recordConditionFieldId(数组,如 [\"fld…\"]):"
                    "用户改列名后订阅会静默失效。新建时一并写上;存量流程补 id 先问用户"
                )


def start_trigger_changes(baseline: dict, flow: dict) -> list[str]:
    """对比服务端基线与新片段的开始节点,返回触发配置的变更列表(空 = 没动)。

    锁的是 BusinessStart 的**整个 `data.inputs`** 加 `data.credential`:这个节点上的
    inputs 全部是触发配置(启动方式、多维表/数据表、记录事件与条件、定时、店铺、
    ui2 写入的 linkfoxTableAutomation* 上下文),没有一项是可以"顺手改改"的。
    节点 id 变了或开始节点被删同样算变更 —— 那等于换了一个开始节点。
    """
    def find_start(f: dict) -> dict | None:
        for n in _as_list(f.get("nodes")):
            nd = _as_dict(n)
            if _as_dict(nd.get("data")).get("name") == REQUIRED_START_NAME:
                return nd
        return None

    old = find_start(baseline)
    if old is None:
        return []  # 基线没有 BusinessStart(老流程),无可锁定
    new = find_start(flow)
    oid = old.get("id")
    if new is None:
        return [f"开始节点 {oid} 被删除"]
    if new.get("id") != oid:
        return [f"开始节点 id 从 {oid} 变成了 {new.get('id')}"]

    changes: list[str] = []
    old_data, new_data = _as_dict(old.get("data")), _as_dict(new.get("data"))
    old_inputs = _as_dict(old_data.get("inputs"))
    new_inputs = _as_dict(new_data.get("inputs"))
    for key in sorted(set(old_inputs) | set(new_inputs)):
        if (
            key in TABLE_SLOT_FIELDS
            and _is_blank_param(old_inputs.get(key))
            and not _is_blank_param(new_inputs.get(key))
        ):
            # 基线里表还没选、这一轮按用户挑的表填上:是补槽位,不是换触发(缺陷 #7130931254)。
            continue
        if key not in new_inputs:
            changes.append(f"inputs.{key} 被删除(原值 {old_inputs[key]!r})")
        elif key not in old_inputs:
            changes.append(f"inputs.{key} 是新增的(值 {new_inputs[key]!r})")
        elif old_inputs[key] != new_inputs[key]:
            changes.append(
                f"inputs.{key}: {old_inputs[key]!r} → {new_inputs[key]!r}"
            )
    if old_data.get("credential", "") != new_data.get("credential", ""):
        changes.append(
            f"data.credential: {old_data.get('credential')!r} → {new_data.get('credential')!r}"
        )
    return changes


def _check_node_contracts(nodes: list, errors: list[str], warnings: list[str]) -> None:
    """data.name → NODE_SPECS 的逐字段比对。

    未知 data.name 是 error:linkfox-workflow 系统找不到对应组件,节点在画布上会直接渲染失败。
    data.type / 顶层 type 不匹配同理。version / color / baseClasses / category 只影响
    展示,linkfox-workflow 系统也会按组件定义规范化,所以只给 warning。
    """
    for idx, node in enumerate(nodes):
        n = _as_dict(node)
        nid = n.get("id") or f"nodes[{idx}]"
        data = _as_dict(n.get("data"))
        name = data.get("name")
        if not isinstance(name, str) or not name:
            continue  # 骨架校验已经报过
        spec = NODE_SPECS.get(name)
        if spec is None:
            errors.append(
                f"{nid} data.name={name!r} 不是受支持的节点;"
                f"只允许 {len(NODE_SPECS)} 个已注册节点,见 references/node-catalog.md"
            )
            continue
        if spec.deprecated and name == DEPRECATED_START_NAME:
            continue  # 由 save_workflow 的 Start 弃用检查统一报

        if data.get("type") != spec.data_type:
            errors.append(
                f"{nid} data.type={data.get('type')!r},{name} 必须是 {spec.data_type!r}"
            )
        top_type = n.get("type")
        if top_type != spec.top_type:
            errors.append(
                f"{nid} 顶层 type={top_type!r},{name} 必须是 {spec.top_type!r}"
            )

        if "version" not in data:
            warnings.append(f"{nid} 缺 data.version,应为 {spec.version}")
        elif data.get("version") != spec.version:
            warnings.append(
                f"{nid} data.version={data.get('version')!r},references 记录为 {spec.version}"
            )
        if "color" not in data:
            warnings.append(f"{nid} 缺 data.color,应为 {spec.color}")
        elif str(data.get("color")).lower() != spec.color.lower():
            warnings.append(
                f"{nid} data.color={data.get('color')!r},references 记录为 {spec.color}"
            )
        if "baseClasses" not in data:
            warnings.append(f"{nid} 缺 data.baseClasses,应为 {spec.base_classes}")
        elif _as_list(data.get("baseClasses")) != spec.base_classes:
            warnings.append(
                f"{nid} data.baseClasses={data.get('baseClasses')!r},"
                f"应为 {spec.base_classes}"
            )
        if "category" in data and data.get("category") != "Agent Flows":
            warnings.append(
                f"{nid} data.category={data.get('category')!r},应为 'Agent Flows'"
            )
        if "inputAnchors" in data and _as_list(data.get("inputAnchors")) != []:
            warnings.append(f"{nid} data.inputAnchors 应为空数组")
        # ExecuteFlow v2.0 删了 Base URL 字段,地址取 linkfoxAgentApi 凭据里的 baseUrl;
        # 还写它说明照着 v1.x 的旧字段表在生成。
        if name == "executeFlowAgentflow" and "executeFlowBaseURL" in _as_dict(data.get("inputs")):
            warnings.append(
                f"{nid} inputs.executeFlowBaseURL 是 v1.x 已删除的字段,运行时不读;"
                "删掉它,地址取 linkfoxAgentApi 凭据里的 baseUrl"
            )
        if not isinstance(_as_dict(n.get("position")).get("x"), (int, float)):
            warnings.append(f"{nid} 缺 position.x/position.y,画布上会堆在原点")


def _check_variable_refs(
    nodes: list, node_by_id: dict[str, dict], errors: list[str], warnings: list[str]
) -> None:
    """`{{ ... }}` 变量引用的三条硬规则(references/variable-substitution.md)。

    1. 用了 `{{ }}` 的字段,其 inputParams 定义必须标 `acceptVariable: true`,否则 linkfox-workflow 系统
       根本不做替换 —— 用户会在运行时看到字面量 `{{ x.output.y }}`。这是最高频的坑。
    2. `{{ <nodeId>.output... }}` 的 nodeId 必须真实存在,否则替换成空。
    3. 不允许裸 `.output`:必须取到具体叶子字段(如 `.output.http.data`)。
    """
    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id") or "<node>"
        data = _as_dict(n.get("data"))
        name = data.get("name")
        if name in NON_EXEC_NAMES:
            continue

        input_params = data.get("inputParams")
        inputs = _as_dict(data.get("inputs"))

        # inputParams 空数组:所有支持配置的节点都必须带完整字段元数据。
        # 注意区分两种情况:整个字段**缺失**时 normalize 会按 input_params_specs.py
        # 的模板代填(覆盖到的节点),走不到这里;能走到这里的是"显式写了空数组"
        # 或"该节点没有可查证模板、模型也没写"。
        if inputs and not _as_list(input_params):
            hint = (
                "整个字段别写(留给 save_workflow.py 按 data.name 代填)"
                if name in INPUT_PARAMS_COVERED
                else "必须补齐字段元数据"
            )
            errors.append(
                f"{nid} data.inputParams 是空数组,但 inputs 已填 "
                f"{sorted(inputs)[:3]}…;{hint},"
                "否则支持变量的字段不会被替换(见 references/variable-substitution.md)"
            )

        accept_var = _accept_variable_fields(input_params)
        declared = _declared_param_names(input_params)

        for path, text in _iter_strings(inputs):
            if not _ANY_VAR_RE.search(text):
                continue
            top_field = path.split(".")[0].split("[")[0]

            if top_field not in accept_var:
                if top_field in declared:
                    errors.append(
                        f"{nid} inputs.{path} 使用了 {{{{ }}}} 变量,但 inputParams 里 "
                        f"{top_field!r} 没有标 acceptVariable: true;linkfox-workflow 系统不会替换它"
                    )
                elif _as_list(input_params):
                    errors.append(
                        f"{nid} inputs.{path} 使用了 {{{{ }}}} 变量,但 inputParams 里"
                        f"没有 {top_field!r} 的定义"
                    )

            for ref_id, tail in _NODE_REF_RE.findall(text):
                if ref_id not in node_by_id:
                    errors.append(
                        f"{nid} inputs.{path} 引用了不存在的节点 {ref_id!r};"
                        "变量会被替换成空值"
                    )
                if not tail.strip(" ."):
                    errors.append(
                        f"{nid} inputs.{path} 使用了裸 {{{{ {ref_id}.output }}}};"
                        "必须取到具体字段(例如 .output.http.data / .output.content)"
                    )

        # 运行时对象必须留占位,不写死实例 id。
        for path, text in _iter_strings(inputs):
            leaf = path.split(".")[-1].split("[")[0]
            if leaf in PLACEHOLDER_FIELDS and text.strip():
                warnings.append(
                    f"{nid} inputs.{path}={text!r} 写死了运行时对象;"
                    "应留空字符串,导入后由用户在 linkfox-workflow 系统里绑定"
                )
        _check_credential_value(nid, data, errors, warnings)


def _check_credential_value(
    nid: str, data: dict, errors: list[str], warnings: list[str]
) -> None:
    """`data.credential` 的值域:空占位、或用户绑定的实例 UUID —— 绝不是类型名。

    以前这条判据是反的(`not credential.endswith("Api") and "-" in credential`):它给
    **正确的** UUID 报 warning,而 `"linkfoxAgentApi"` 因为以 `Api` 结尾被直接放行。结果
    类型名一路通过静态校验、导入也不报错,一直跑到那个节点才炸 —— 会话 11b2bb9f 里就是
    跑到第 15 个节点、查 `list_executions.py --execution-id` 才定位到的。

    分级:
    - 类型名 → error(确定跑不通)。
    - 实例 UUID → 不报。refine 时基线来自 `fetch_workflow.py`,里面本来就带着用户在 UI
      上绑好的凭据;把它当缺陷提示会诱导 agent 去"修正"成空串,反而清掉用户的配置。
      首次生成留空占位这条规则由生成侧的检查清单管,不在这里拦。
    - `credential` 与 `inputs.FLOWISE_CREDENTIAL_ID` 一有一无 → warning(两处指同一个
      凭据,只填一处通常是漏改)。
    """
    credential = data.get("credential")
    cred = credential.strip() if isinstance(credential, str) else ""
    if cred in CREDENTIAL_TYPE_NAMES:
        errors.append(
            f"{nid} data.credential={cred!r} 是 credential 的**类型名**,不是凭据实例;"
            "该位置只能是空字符串占位(生成时)或用户在 UI 上绑定的实例 UUID"
            "(refine 时从 fetch 的基线里带过来)。写类型名导入不报错,"
            "但运行到该节点会直接失败"
        )
        return

    cred_input_id = _as_dict(data.get("inputs")).get("FLOWISE_CREDENTIAL_ID")
    fid = cred_input_id.strip() if isinstance(cred_input_id, str) else ""
    if bool(cred) != bool(fid):
        filled, empty = (
            ("data.credential", "inputs.FLOWISE_CREDENTIAL_ID")
            if cred
            else ("inputs.FLOWISE_CREDENTIAL_ID", "data.credential")
        )
        warnings.append(
            f"{nid} {filled} 有值但 {empty} 为空;两处指同一个凭据,"
            "通常应同时填同一个实例 id 或同时留空"
        )


def _check_linkfox_http_body(nodes: list, errors: list[str], warnings: list[str]) -> None:
    """LinkfoxHTTP 的 `body` 不能是占位 —— 必填参数一个都没传等于这个节点必定 400。

    `references/nodes-linkfox-custom.md` 用加粗 + ⚠️ 写了三遍"不允许把 body 落成占位
    `"{}"` 上传",照样犯:会话 11b2bb9f 里 11 个 LinkfoxHTTP 节点的 body 全是 `"{}"`,
    直到用户贴出 `{"errcode":400,"errmsg":"keyword 为必填参数"}` 才被逐个补上。
    只写在散文里、脚本不拦的规则,执行率约等于零,所以这里机械拦死。

    **逃生门**:确实无请求参数的接口(`/spApi/authorizedStores` 这类)是合法的,在节点
    `data.description` 里写上 `接口文档无请求参数` 即可放行 —— 这是一句需要作者对着文档
    确认后才写得出的事实声明,比默默留 `"{}"` 多了一道人为确认。

    第二条判据针对**字段填了、值是空串**的写法(`{"keyword": ""}`):这正是会话里报
    `keyword 为必填参数` 的直接原因 —— 看起来 body 已经组好了,实际一个值都没传。全部值为空
    → error;部分值为空 → warning(有的接口确实有可选参数)。

    **不据"body 里没有 `{{ }}` 引用"报警**:常量 body 是合法的(`/amazonAds/authorizeUrl`
    的 `{"region":"NA"}` 就直接来自文档的常用路径表),那个判据只会制造噪音。
    """
    for node in nodes:
        n = _as_dict(node)
        if _as_dict(n.get("data")).get("name") != "linkfoxHttpAgentflow":
            continue
        nid = n.get("id") or "<node>"
        data = _as_dict(n.get("data"))
        inputs = _as_dict(data.get("inputs"))
        description = data.get("description")
        exempt = (
            isinstance(description, str) and NO_BODY_ESCAPE_HATCH in description
        )

        # path 留空是 references/nodes-linkfox-custom.md 允许的占位状态(工具矩阵里
        # 查不到已上线的匹配工具时)。这种节点还没定位到接口,谈不上 body 该填什么。
        path = inputs.get("path")
        if not (isinstance(path, str) and path.strip()):
            continue

        # GET / DELETE 没有请求体是正常的(文档也说 GET 填了 body 会被服务端忽略)。
        method = inputs.get("method")
        verb = method.strip().upper() if isinstance(method, str) and method.strip() else "POST"
        if verb in ("GET", "DELETE"):
            continue

        body = inputs.get("body")

        # formData / xWwwFormUrlencoded 用 {key, value} 数组;json / raw 用字符串。
        if isinstance(body, list):
            if not body and not exempt:
                errors.append(
                    f"{nid} inputs.body 是空数组,等于没填任何请求参数;"
                    "用 scripts/query_tools_matrix.py endpoint 查该端点的参数表补齐"
                    f"(接口确实无参数则在 data.description 里写明 {NO_BODY_ESCAPE_HATCH!r})"
                )
            continue

        raw = body.strip() if isinstance(body, str) else ""
        if raw in _EMPTY_BODY_LITERALS:
            if exempt:
                continue
            errors.append(
                f"{nid} inputs.body={body!r} 是占位,等于没填任何请求参数 —— "
                f"{verb} {path.strip()} 运行时通常直接报 `xxx 为必填参数`。按 "
                "references/nodes-linkfox-custom.md 的流程用 scripts/query_tools_matrix.py "
                "查该端点,把参数表里的字段组成真实 JSON;必填参数要引用上游"
                "具体字段(如 {{fillFormAgentflow_0.output.filledForm.keyword}})。"
                f"接口确实无请求参数时,在 data.description 里写明 {NO_BODY_ESCAPE_HATCH!r} 放行"
            )
            continue

        body_type = inputs.get("bodyType")
        if isinstance(body_type, str) and body_type.strip() not in ("json", ""):
            continue
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            # 带 {{ }} 引用的 body 常常不是合法 JSON 字面量(变量没加引号),不据此报错。
            continue
        if not isinstance(parsed, dict):
            continue
        if not parsed:
            if not exempt:
                errors.append(
                    f"{nid} inputs.body 解析后是空对象,等于没填任何请求参数;"
                    f"补齐参数表字段(接口确实无参数则在 data.description 里写明 "
                    f"{NO_BODY_ESCAPE_HATCH!r})"
                )
            continue

        blank = sorted(k for k, v in parsed.items() if _is_blank_param(v))
        if blank and len(blank) == len(parsed):
            errors.append(
                f"{nid} inputs.body 里的参数 {blank} 值全部为空 —— 字段名组好了但一个值都"
                f"没传,{verb} {path.strip()} 运行时会报 `xxx 为必填参数`。"
                "把它们接到上游的具体字段上,例如 "
                "{{fillFormAgentflow_0.output.filledForm.keyword}} 或 "
                "{{linkfoxHttpAgentflow_0.output.http.data.products[0].asin}}"
            )
        elif blank:
            warnings.append(
                f"{nid} inputs.body 里的参数 {blank} 值为空;"
                "如果它们是必填参数,运行时会报 `xxx 为必填参数`,需要接上游字段"
            )


def _is_blank_param(value: Any) -> bool:
    """请求参数的值是否等于"没填"。

    只把空串 / None / 空容器算空。`0` 和 `false` 是有意义的取值(页码、开关),不算。
    """
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return not value
    return False


def _check_expert_prompt(nodes: list, errors: list[str], warnings: list[str]) -> None:
    """CrossBorderExpert 的 taskInstruction:10000 字符硬上限 + 禁止内联整体响应。

    专家平台侧对 prompt 有硬限制(早期 1000,现为 10000),超了直接返回
    `Task creation failed (400): prompt 必须为字符[0,<上限>]`。会话 11b2bb9f 里 7 个专家
    节点全部把 `{{ ...output.http.data }}` 直接塞进 taskInstruction,替换后一个 Amazon
    搜索响应就有 60 条商品 × 30+ 字段,量级几十 KB —— 必然撞穿。

    **两条判据都是机械的**:

    1. 引用路径恰好停在整体响应根字段上(`.output.http.data` / `.output.expertResult` /
       `.output.content` / `.output.tableData` / `.output.filledForm`)→ error。继续往下
       取叶子(`.output.http.data.products[0].asin`)放行。
    2. 字面量长度 > EXPERT_PROMPT_MAX_CHARS → error。字面量还没算引用展开的部分,
       所以阈值留了余量。

    修法**不是**把引用删掉换成纯文字描述 —— 那样专家节点拿不到任何真实数据(会话里第一版
    就是这么改的,被用户当场否掉:"这样不行的,变成没有引用上游的数据了")。正确做法是插一个
    CustomFunction 节点把上游结果精简成几百字符,再引用它的 `.output.content`,或者直接
    引用上游的具体叶子字段。
    """
    for node in nodes:
        n = _as_dict(node)
        if _as_dict(n.get("data")).get("name") != "crossBorderExpertAgentflow":
            continue
        nid = n.get("id") or "<node>"
        inputs = _as_dict(_as_dict(n.get("data")).get("inputs"))
        text = inputs.get(EXPERT_PROMPT_FIELD)
        if not isinstance(text, str) or not text.strip():
            continue

        for ref_id, tail in _NODE_REF_RE.findall(text):
            path = tail.strip().lstrip(".").strip().rstrip(".")
            if path in _WHOLE_RESPONSE_TAILS:
                errors.append(
                    f"{nid} inputs.{EXPERT_PROMPT_FIELD} 内联了整体响应 "
                    f"{{{{ {ref_id}.output.{path} }}}} —— 替换后整个上游结果会展开进 "
                    f"prompt,专家平台会返回 `prompt 必须为字符[0,{EXPERT_PROMPT_HARD_LIMIT}]`。改成引用具体叶子"
                    "字段(如 .output.http.data.products[0].asin),或插一个 "
                    "CustomFunction 节点把上游结果精简后引用它的 .output.content。"
                    "**不要**直接删掉引用换成纯文字描述 —— 那样专家节点拿不到真实数据"
                )

        if len(text) > EXPERT_PROMPT_MAX_CHARS:
            errors.append(
                f"{nid} inputs.{EXPERT_PROMPT_FIELD} 字面量已有 {len(text)} 字符,"
                f"超过 {EXPERT_PROMPT_MAX_CHARS} 的安全线(专家平台硬上限 {EXPERT_PROMPT_HARD_LIMIT},"
                "变量替换后还会更长);精简指令文本,把长规则挪到专家侧配置"
            )
        elif len(text) > EXPERT_PROMPT_MAX_CHARS * 0.75 and _ANY_VAR_RE.search(text):
            warnings.append(
                f"{nid} inputs.{EXPERT_PROMPT_FIELD} 字面量 {len(text)} 字符且带变量引用,"
                f"替换后容易超过专家平台 {EXPERT_PROMPT_HARD_LIMIT} 字符上限;建议压到 "
                f"{int(EXPERT_PROMPT_MAX_CHARS * 0.75)} 字符以内"
            )


def _check_condition_inputs(nodes: list, errors: list[str]) -> None:
    """Condition 的 operation 必须逐字命中源码枚举 —— `equals` 是最常见的错法。"""
    for node in nodes:
        n = _as_dict(node)
        data = _as_dict(n.get("data"))
        if data.get("name") != "conditionAgentflow":
            continue
        nid = n.get("id") or "<condition>"
        conditions = _as_list(_as_dict(data.get("inputs")).get("conditions"))
        if not conditions:
            errors.append(f"{nid} Condition 必须至少有一条 inputs.conditions[]")
            continue
        for cidx, cond in enumerate(conditions):
            c = _as_dict(cond)
            ctype = c.get("type") if isinstance(c.get("type"), str) else "string"
            allowed = CONDITION_OPERATIONS.get(ctype)
            if allowed is None:
                errors.append(
                    f"{nid} conditions[{cidx}].type={ctype!r} 非法;"
                    f"只允许 {sorted(CONDITION_OPERATIONS)}"
                )
                continue
            operation = c.get("operation")
            if operation not in allowed:
                hint = ""
                if operation == "equals":
                    hint = ";正确写法是 'equal'(无 s)"
                errors.append(
                    f"{nid} conditions[{cidx}].operation={operation!r} 不在 {ctype} 的"
                    f"枚举 {sorted(allowed)} 中{hint}"
                )


PYTHON_NODE_NAME = "customPythonFunctionAgentflow"
PYTHON_CODE_FIELD = "customPythonFunctionCode"
PYTHON_VARS_FIELD = "customPythonFunctionInputVariables"
# 节点自己占用的名字:`flow` 由前导代码赋值,`result` 由尾部代码读取。
PYTHON_RESERVED_NAMES = {"flow", "result"}
_PYTHON_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# 顶格的 `return` —— Python 节点不是函数体,写了直接 SyntaxError。缩进里的 return
# 属于用户自己定义的函数,合法。
_PYTHON_TOPLEVEL_RETURN_RE = re.compile(r"^return\b", re.M)
_PYTHON_RESULT_ASSIGN_RE = re.compile(r"^result\s*(?::[^=\n]+)?=(?!=)", re.M)
# 从 JS 节点照搬过来最常见的三种写法:`$foo` 变量、`$flow`、`$vars`。
_PYTHON_JS_DOLLAR_RE = re.compile(r"\$(?:flow|vars|input)\b|\$[A-Za-z_]\w*")
# 功能都能实现时优先 JS CustomFunction(启动快、不出境)。Python 节点"非用不可"的机械信号:
# import 了标准库以外的包(pandas / bs4 / pdfplumber…),或下游 / 自己的 UpdateState
# 按字段取 `result`(JS 节点的输出是字符串,取不了字段)。两样都没有 → warning。
_PYTHON_IMPORT_RE = re.compile(r"^\s*(?:from\s+([A-Za-z_]\w*)|import\s+([A-Za-z_]\w*))", re.M)
_PYTHON_STDLIB = set(getattr(sys, "stdlib_module_names", ())) or {
    "json", "re", "math", "datetime", "time", "random", "collections", "itertools",
    "functools", "statistics", "string", "base64", "hashlib", "urllib", "decimal",
}
# 用户本轮明确要求用 Python 时,在节点 description 里写这句,跳过 JS 优先提醒。
PYTHON_EXPLICIT_MARK = "用户指定用 Python"


def _check_python_function(
    nodes: list, node_by_id: dict[str, dict], errors: list[str], warnings: list[str]
) -> None:
    """CustomPythonFunction 的写法与 JS CustomFunction 不同,照 JS 习惯写必错。

    - 结果要**赋值给 `result`**,顶格 `return` 是 SyntaxError;没赋值不报错,结果是空串。
    - Input Variables 是裸名字(不带 `$`),且必须是合法 Python 标识符,不能叫
      `flow` / `result`、不能以 `__` 开头 —— 运行时在建沙箱前就拒掉。
    - 下游按字段取值必须走 `output.result.<字段>`。`output.content` 是字符串,
      `output.content.<字段>` 运行时不报错也不替换,用户看到的是字面量。
    - 功能都能实现时优先 JS CustomFunction:没用到第三方包、也没人按字段取 result 的
      Python 节点给 warning(语义判断兜不全,所以不拦)。
    """
    # 这些 Python 节点有"非用 Python 不可"的信号,不提醒改 JS。
    needs_python: set[str] = set()
    explicit_python: set[str] = set()
    for node in nodes:
        n = _as_dict(node)
        data = _as_dict(n.get("data"))
        if data.get("name") != PYTHON_NODE_NAME:
            continue
        nid = n.get("id") or "<python>"
        inputs = _as_dict(data.get("inputs"))

        if PYTHON_EXPLICIT_MARK in str(data.get("description") or ""):
            explicit_python.add(nid)
        # 自己的 UpdateState 按字段取 `{{ output.<字段> }}` 也算按字段用 result。
        for _, s in _iter_strings(inputs.get(UPDATE_STATE_FIELDS[PYTHON_NODE_NAME])):
            if re.search(r"\{\{\s*output\s*[.\[]", s):
                needs_python.add(nid)

        code = inputs.get(PYTHON_CODE_FIELD)
        if not isinstance(code, str) or not code.strip():
            errors.append(f"{nid} inputs.{PYTHON_CODE_FIELD} 不能为空")
        else:
            for a, b in _PYTHON_IMPORT_RE.findall(code):
                if (a or b) not in _PYTHON_STDLIB:
                    needs_python.add(nid)
            if _PYTHON_TOPLEVEL_RETURN_RE.search(code):
                errors.append(
                    f"{nid} inputs.{PYTHON_CODE_FIELD} 有顶格 `return` —— Python 节点不是函数体,"
                    "运行时 SyntaxError。改成 `result = <值>`"
                )
            elif not _PYTHON_RESULT_ASSIGN_RE.search(code):
                warnings.append(
                    f"{nid} inputs.{PYTHON_CODE_FIELD} 没有顶格的 `result = ...`;"
                    "不赋值 result 时节点输出是空串(不报错),下游拿到的是空值"
                )
            if _PYTHON_JS_DOLLAR_RE.search(code):
                warnings.append(
                    f"{nid} inputs.{PYTHON_CODE_FIELD} 里出现 `$xxx` —— 那是 JS 节点的写法。"
                    "Python 里输入变量是裸名字,上下文是 `flow[\"state\"]` 这类 dict,没有 `$vars`"
                )

        for idx, item in enumerate(_as_list(inputs.get(PYTHON_VARS_FIELD))):
            var = _as_dict(item).get("variableName")
            if not isinstance(var, str) or not var:
                errors.append(f"{nid} inputs.{PYTHON_VARS_FIELD}[{idx}].variableName 不能为空")
                continue
            if var.startswith("$"):
                errors.append(
                    f"{nid} inputs.{PYTHON_VARS_FIELD}[{idx}].variableName={var!r}:"
                    "Python 节点的变量名不带 `$`,写成裸名字"
                )
            elif (
                not _PYTHON_IDENTIFIER_RE.match(var)
                or keyword.iskeyword(var)
                or var.startswith("__")
                or var in PYTHON_RESERVED_NAMES
            ):
                errors.append(
                    f"{nid} inputs.{PYTHON_VARS_FIELD}[{idx}].variableName={var!r} 会在建沙箱前被拒:"
                    "必须是合法 Python 标识符,不能是关键字、不能以 `__` 开头、不能叫 flow / result"
                )

    # 下游引用:`<python>.output.content.<字段>` 永远取不到。
    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id") or "<node>"
        data = _as_dict(n.get("data"))
        for path, text in _iter_strings(_as_dict(data.get("inputs"))):
            for ref_id, tail in _NODE_REF_RE.findall(text):
                target = node_by_id.get(ref_id)
                if _as_dict(_as_dict(target).get("data")).get("name") != PYTHON_NODE_NAME:
                    continue
                t = tail.strip().lstrip(".").strip()
                if t.startswith("result.") or t.startswith("result["):
                    needs_python.add(ref_id)
                if t.startswith("content.") or t.startswith("content["):
                    errors.append(
                        f"{nid} inputs.{path} 引用了 {ref_id}.output.{t} —— Python 节点的 "
                        "output.content 是字符串,往下取字段运行时不替换。改成 "
                        f"{{{{ {ref_id}.output.result{t[len('content'):]} }}}}"
                    )

    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id") or "<python>"
        if _as_dict(n.get("data")).get("name") != PYTHON_NODE_NAME:
            continue
        if nid in needs_python or nid in explicit_python:
            continue
        warnings.append(
            f"{nid} 是 CustomPythonFunction,但没用到标准库以外的包、下游也没按字段取 result ——"
            "这类拼接 / 截断 / 排序 / 格式转换优先用 JS 的 CustomFunction(customFunctionAgentflow,"
            "启动快、少一次沙箱冷启动)。用户本轮明确要求用 Python 时,在该节点 description 里写"
            f"「{PYTHON_EXPLICIT_MARK}」"
        )


# 两个自定义函数节点各有一个 Environment Variables 字段(不共用)。
# 规则来自 Flowise 侧实现在**起沙箱之前**的校验:违例直接报错,不会白付一次沙箱钱。
SANDBOX_ENV_FIELDS = {
    PYTHON_NODE_NAME: "customPythonFunctionEnvVariables",
    "customFunctionAgentflow": "customFunctionEnvVariables",
}
SANDBOX_ENV_MAX_ENTRIES = 32
SANDBOX_ENV_MAX_NAME_LEN = 128
SANDBOX_ENV_MAX_VALUE_LEN = 8192
# 变量名比 Python 输入变量宽松(不要求是标识符,只要这条正则),单独立一条,别和
# `_PYTHON_IDENTIFIER_RE` 共用 —— 后者改了不该连带改变沙箱环境变量的判定。
SANDBOX_ENV_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# 沙箱里 pip / npm 安装、解释器启动、动态库加载都读这几个,让作者改掉就是
# "代码跑了但依赖找不到"这类和自己配置看不出关系的故障。
SANDBOX_ENV_RESERVED = {
    "PATH", "HOME", "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP",
    "NODE_PATH", "NODE_OPTIONS", "LD_PRELOAD", "LD_LIBRARY_PATH",
}
# 运行时按工作流属主取的内置 key,只在这两个节点的 Environment Variables 里解析。
# 写进别的字段不会被替换,原样留着 —— 这层作用域就是安全边界。
_RUNTIME_KEY_RE = re.compile(
    r"\{\{\s*\$vars\.(LINKFOX_AGENT_API_KEY|LINKFOXAGENT_API_KEY)\s*\}\}"
)
# 名字里带这些词基本就是密钥(`AUTHOR_NAME` 这类不算,所以按 `_` 分段匹配)。
_SECRETISH_NAME_RE = re.compile(
    r"(?:^|_)(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|AUTH|CREDENTIAL)(?:_|$)", re.I
)


def _check_sandbox_env_vars(
    nodes: list, errors: list[str], warnings: list[str]
) -> None:
    """CustomFunction / CustomPythonFunction 的 Environment Variables。

    - 变量名、条数、长度、保留名、重名、值类型:运行时**起沙箱之前**就拒,报 error。
    - 密钥手填成字面量:值会明文落在编排 JSON 里(随导出文件、数据库、日志扩散),同样报
      error 拦在落盘前 —— 只用 `{{$vars.LINKFOX_AGENT_API_KEY}}` 这类绑定。
    - 内置 key 写错位置:不在 Environment Variables 里就永远不替换,给 warning。
    """
    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id") or "<node>"
        data = _as_dict(n.get("data"))
        field = SANDBOX_ENV_FIELDS.get(data.get("name"))
        if not field:
            continue
        inputs = _as_dict(data.get("inputs"))
        bindings = _as_list(inputs.get(field))
        if len(bindings) > SANDBOX_ENV_MAX_ENTRIES:
            errors.append(
                f"{nid} inputs.{field} 有 {len(bindings)} 条,超过上限 "
                f"{SANDBOX_ENV_MAX_ENTRIES} 条;运行时起沙箱前会拒"
            )
        seen: dict[str, int] = {}
        for idx, item in enumerate(bindings):
            b = _as_dict(item)
            var_name = b.get("variableName")
            value = b.get("variableValue")
            if not isinstance(var_name, str) or not var_name:
                errors.append(f"{nid} inputs.{field}[{idx}].variableName 不能为空")
                continue
            if not SANDBOX_ENV_NAME_RE.match(var_name):
                errors.append(
                    f"{nid} inputs.{field}[{idx}].variableName={var_name!r} 不合法:"
                    "只允许字母数字下划线、不能数字开头;运行时起沙箱前会拒"
                )
            elif len(var_name) > SANDBOX_ENV_MAX_NAME_LEN:
                errors.append(
                    f"{nid} inputs.{field}[{idx}].variableName 超过 "
                    f"{SANDBOX_ENV_MAX_NAME_LEN} 字符;运行时起沙箱前会拒"
                )
            if var_name in SANDBOX_ENV_RESERVED:
                errors.append(
                    f"{nid} inputs.{field}[{idx}].variableName={var_name!r} 是保留名"
                    "(pip / npm 安装、解释器启动都读它);留空由沙箱自己给默认值"
                )
            if var_name in seen:
                errors.append(
                    f"{nid} inputs.{field}[{idx}].variableName={var_name!r} 与第 "
                    f"{seen[var_name]} 条重复;运行时起沙箱前会拒"
                )
            else:
                seen[var_name] = idx

            if isinstance(value, (dict, list)):
                errors.append(
                    f"{nid} inputs.{field}[{idx}].variableValue 只能是文本 / 数字 / 布尔;"
                    f"传 {type(value).__name__} 运行时起沙箱前会拒"
                )
                continue
            if not isinstance(value, str):
                continue
            if len(value) > SANDBOX_ENV_MAX_VALUE_LEN:
                errors.append(
                    f"{nid} inputs.{field}[{idx}].variableValue 超过 "
                    f"{SANDBOX_ENV_MAX_VALUE_LEN} 字符;运行时起沙箱前会拒"
                )
            if (
                value.strip()
                and "{{" not in value
                and _SECRETISH_NAME_RE.search(var_name)
            ):
                errors.append(
                    f"{nid} inputs.{field}[{idx}] 的名字像密钥却写成了字面量 —— "
                    "明文会随编排 JSON 导出、进数据库和日志。密钥改用 "
                    "{{$vars.LINKFOX_AGENT_API_KEY}} 绑定;它本来就不是密钥"
                    "(如 TOKEN_TTL 这类配置数值)就换个不带 KEY / TOKEN / SECRET / "
                    "PASSWORD / AUTH / CREDENTIAL 的变量名"
                )

    # 内置 key 是**按字段作用域**解析的:出现在别处不会报错,只会原样留给用户看。
    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id") or "<node>"
        data = _as_dict(n.get("data"))
        env_field = SANDBOX_ENV_FIELDS.get(data.get("name"))
        for path, text in _iter_strings(_as_dict(data.get("inputs"))):
            if not _RUNTIME_KEY_RE.search(text):
                continue
            if env_field and path.split(".")[0].split("[")[0] == env_field:
                continue
            warnings.append(
                f"{nid} inputs.{path} 用了内置运行时 key($vars.LINKFOX_AGENT_API_KEY)—— "
                "这个名字只在 CustomFunction / CustomPythonFunction 的 Environment "
                "Variables 里解析,写在这里会原样留着;改绑进环境变量再读"
            )


def _check_iteration_children(
    nodes: list, name_by_id: dict[str, str], errors: list[str], warnings: list[str]
) -> None:
    """Iteration 子节点靠 parentNode + extent 关联,写错就成了画布上的游离节点。"""
    iteration_ids = {
        nid for nid, name in name_by_id.items() if name == "iterationAgentflow"
    }
    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id") or "<node>"
        parent = n.get("parentNode")
        if parent is None:
            continue
        if not isinstance(parent, str) or parent not in iteration_ids:
            errors.append(
                f"{nid} parentNode={parent!r} 不是本 flow 里的 Iteration 节点"
            )
            continue
        if n.get("extent") != "parent":
            errors.append(
                f"{nid} 有 parentNode 但 extent={n.get('extent')!r};必须是 'parent'"
            )
        if name_by_id.get(nid) == "iterationAgentflow":
            errors.append(f"{nid} 是 Iteration 且带 parentNode;不允许嵌套 Iteration")

    for nid in iteration_ids:
        has_child = any(
            _as_dict(x).get("parentNode") == nid for x in nodes
        )
        if not has_child:
            warnings.append(f"{nid} 是 Iteration 但没有任何子节点,循环体为空")


def _check_starting_nodes(
    nodes: list, edges: list, name_by_id: dict[str, str], errors: list[str]
) -> None:
    """除 BusinessStart 外,不允许再有"没有入边"的执行节点。

    linkfox-workflow 运行时把**所有入度为 0 的节点**都当起始节点(不只是 Start),多于一个
    就整条流报 `Multiple starting nodes are not allowed`,一个节点都不跑。排除口径与运行时
    一致:StickyNote、Iteration 子节点(`extent: "parent"`)、Loop 的回跳目标
    (`loopBackToNode` 不画线,天然没有入边)。

    典型成因是**漏了一条边**:节点有出边、没有入边,所以"孤立节点"那条校验看不见它。
    2026-10-19 生产上 13 条「竞品监控」流程都是这么坏的 —— 「闭合 + 守恒」→「闭合与守恒通过?」
    那条边没生成,S5 还把整段判断分支重复画了两份。完全孤立的节点由 save_workflow.py 报,这里跳过。
    """
    if REQUIRED_START_NAME not in name_by_id.values():
        return  # 缺开始节点由骨架校验报,这里再报只会刷屏

    has_incoming: set[str] = set()
    has_outgoing: set[str] = set()
    for edge in edges:
        e = _as_dict(edge)
        if isinstance(e.get("target"), str):
            has_incoming.add(e["target"])
        if isinstance(e.get("source"), str):
            has_outgoing.add(e["source"])

    loop_back_targets: set[str] = set()
    for node in nodes:
        data = _as_dict(_as_dict(node).get("data"))
        target = _as_dict(data.get("inputs")).get("loopBackToNode")
        if data.get("name") == "loopAgentflow" and isinstance(target, str) and target:
            # 形如 `${nodeId}-${nodeLabel}`,label 自己可能带 '-',只取第一段(与运行时一致)
            loop_back_targets.add(target.split("-")[0])

    for node in nodes:
        n = _as_dict(node)
        nid = n.get("id")
        name = name_by_id.get(nid, "") if isinstance(nid, str) else ""
        if (
            not isinstance(nid, str)
            or name in START_NAMES
            or name in NON_EXEC_NAMES
            or n.get("extent") == "parent"
            or nid in loop_back_targets
            or nid in has_incoming
            or nid not in has_outgoing
        ):
            continue
        label = _as_dict(n.get("data")).get("label") or name
        errors.append(
            f"{nid}({label}) 没有入边,运行时会被当成第二个起始节点,整条流报 "
            "`Multiple starting nodes are not allowed`、一个节点都不跑;"
            "多半是漏了一条从上游接过来的边,补上;若是重复画的分支就删掉"
        )


def _check_edge_metadata(
    edges: list, name_by_id: dict[str, str], errors: list[str], warnings: list[str]
) -> None:
    """edge 的 id 拼接、type、HumanInput 标记、分支 edgeLabel。

    HumanInput 出边缺 `isHumanInput: true` 会让 linkfox-workflow 系统不把它当审批分支渲染,是 error;
    id 拼写和 edgeLabel 只影响观感,给 warning。
    """
    for eidx, edge in enumerate(edges):
        e = _as_dict(edge)
        source = e.get("source")
        target = e.get("target")
        source_handle = e.get("sourceHandle")
        target_handle = e.get("targetHandle")
        if not isinstance(source, str) or not isinstance(target, str):
            continue  # 骨架校验已报

        if e.get("type") != "agentFlow":
            warnings.append(f"edges[{eidx}] type={e.get('type')!r},应为 'agentFlow'")

        want_id = f"{source}-{source_handle}-{target}-{target_handle}"
        if e.get("id") != want_id:
            warnings.append(
                f"edges[{eidx}].id={e.get('id')!r},约定拼法为 "
                "'<source>-<sourceHandle>-<target>-<targetHandle>'"
            )

        edge_data = _as_dict(e.get("data"))
        source_name = name_by_id.get(source, "")

        if source_name == "humanInputAgentflow":
            if edge_data.get("isHumanInput") is not True:
                errors.append(
                    f"edges[{eidx}] 从 HumanInput 出发,必须带 data.isHumanInput: true"
                )
            if not str(edge_data.get("edgeLabel") or "").strip():
                errors.append(
                    f"edges[{eidx}] 从 HumanInput 出发,必须带 data.edgeLabel "
                    "('proceed' 或 'reject')"
                )
        elif source_name in {"conditionAgentflow", "conditionAgentAgentflow"}:
            if not str(edge_data.get("edgeLabel") or "").strip():
                warnings.append(
                    f"edges[{eidx}] 从 {source_name} 出发,建议带 data.edgeLabel "
                    "标明走的是哪个分支"
                )
        else:
            spec = NODE_SPECS.get(source_name)
            if spec and spec.edge_label:
                actual = str(edge_data.get("edgeLabel") or "")
                if actual != spec.edge_label:
                    warnings.append(
                        f"edges[{eidx}] 从 {source_name} 出发,约定 "
                        f"edgeLabel={spec.edge_label!r},当前为 {actual!r}"
                    )


_LAYOUT_X_STEP = 300
_LAYOUT_Y_STEP = 160


def _compute_layout(nodes: list, edges: list) -> dict[str, dict[str, int]]:
    """按 edge 拓扑给节点算画布坐标:x 随深度递增,同层节点在 y 轴错开。

    为什么不能简单 `x = 250 * index`:那样并行分支会被画成一条水平直线,
    画布上跟串行结构长得一模一样。用户改完并行看不出任何变化,只能反馈
    "没生效",然后 agent 又白改一轮。深度分层能让分叉在视觉上真的分叉。

    深度 = 从入度为 0 的节点出发做 BFS 的层号。环、孤立节点、Iteration 子节点
    都能拿到一个确定坐标(未被 BFS 覆盖的按剩余顺序补到最后一层)。
    """
    ids: list[str] = []
    for n in nodes:
        if isinstance(n, dict) and isinstance(n.get("id"), str):
            ids.append(n["id"])
    if not ids:
        return {}

    id_set = set(ids)
    children: dict[str, list[str]] = {i: [] for i in ids}
    indegree: dict[str, int] = {i: 0 for i in ids}
    for e in edges:
        if not isinstance(e, dict):
            continue
        s, t = e.get("source"), e.get("target")
        if s in id_set and t in id_set and t not in children[s]:
            children[s].append(t)
            indegree[t] += 1

    # Iteration 子节点不参与主干分层:它们跟着父节点走,单独摆在父节点右下方。
    parent_of: dict[str, str] = {}
    for n in nodes:
        if not isinstance(n, dict):
            continue
        nid, parent = n.get("id"), n.get("parentNode")
        if isinstance(nid, str) and isinstance(parent, str) and parent in id_set:
            parent_of[nid] = parent

    depth: dict[str, int] = {}
    queue = [i for i in ids if indegree[i] == 0 and i not in parent_of]
    for i in queue:
        depth[i] = 0
    head = 0
    while head < len(queue):
        cur = queue[head]
        head += 1
        for nxt in children[cur]:
            if nxt in parent_of:
                continue
            cand = depth[cur] + 1
            if nxt not in depth or cand > depth[nxt]:
                depth[nxt] = cand
                queue.append(nxt)

    # 环上的节点或不可达节点:兜底放到当前最深一层之后,保证每个节点都有坐标。
    fallback_depth = (max(depth.values()) + 1) if depth else 0
    for i in ids:
        if i not in depth and i not in parent_of:
            depth[i] = fallback_depth

    by_depth: dict[int, list[str]] = {}
    for i in ids:
        if i in parent_of:
            continue
        by_depth.setdefault(depth[i], []).append(i)

    layout: dict[str, dict[str, int]] = {}
    for d, members in by_depth.items():
        # 同层多个节点(并行分支)以 0 为中心上下对称展开,视觉上更像分叉。
        offset = -((len(members) - 1) * _LAYOUT_Y_STEP) // 2
        for k, nid in enumerate(members):
            layout[nid] = {
                "x": d * _LAYOUT_X_STEP,
                "y": offset + k * _LAYOUT_Y_STEP,
            }

    for nid, parent in parent_of.items():
        base = layout.get(parent, {"x": 0, "y": 0})
        siblings = [c for c, p in parent_of.items() if p == parent]
        k = siblings.index(nid)
        layout[nid] = {
            "x": base["x"] + 80,
            "y": base["y"] + 100 + k * _LAYOUT_Y_STEP,
        }

    return layout


# 只对这些 param type 做 acceptVariable 自愈。`options` / `multiOptions` /
# `asyncOptions` / `number` / `boolean` / `code` / `password` 里出现 `{{ }}` 不是
# "漏标布尔",而是填错了字段(枚举值写成模板、把密钥写成变量),自愈会把真 bug 盖住
# —— 那些仍然报 error。
_ACCEPT_VARIABLE_HEALABLE_TYPES = {"string", "array", "json"}


def _heal_accept_variable(nid: str, data: dict, filled: list[str]) -> None:
    """给已声明、值里有 `{{ }}`、却漏标 `acceptVariable` 的字段补上这个布尔。

    只处理"字段已在 inputParams 里"这一支。字段整块没声明的情况不碰 —— 那是缺元数据,
    由 `_check_variable_refs` 报 error 要求补全,自动编一个条目等于替模型猜 schema。
    """
    if data.get("name") in NON_EXEC_NAMES:
        return
    input_params = data.get("inputParams")
    if not isinstance(input_params, list):
        return
    inputs = _as_dict(data.get("inputs"))

    # 值里带 `{{ }}` 的顶层字段名。
    templated: set[str] = set()
    for path, text in _iter_strings(inputs):
        if _ANY_VAR_RE.search(text):
            templated.add(path.split(".")[0].split("[")[0])
    if not templated:
        return

    for param in input_params:
        p = param if isinstance(param, dict) else None
        if p is None:
            continue
        pname = p.get("name")
        if not isinstance(pname, str) or pname not in templated:
            continue
        if p.get("acceptVariable") or p.get("acceptNodeOutputAsVariable"):
            continue
        if p.get("type") not in _ACCEPT_VARIABLE_HEALABLE_TYPES:
            continue
        p["acceptVariable"] = True
        filled.append(f"{nid}.data.inputParams[{pname}].acceptVariable=true")


# refine 时片段里可以省略、由脚本按节点 id 从 fetch 基线拷回来的字段。
# 只收"省略 = 保持原样"语义明确的字段:画布坐标 / 尺寸是用户拖出来的,label / description /
# inputs / credential 是用户或上一轮配好的内容。锚点、version 这类纯样板不在这里 ——
# 它们由 data.name(Condition 还要看条件条数)重新推导,拷旧值反而会和新 inputs 对不上。
_BASELINE_TOP_FIELDS = ("position", "positionAbsolute", "width", "height")
_BASELINE_DATA_FIELDS = ("id", "type", "label", "description", "inputs", "credential")


def inherit_from_baseline(flow: dict, baseline: dict) -> list[str]:
    """refine:片段里 id 与基线相同、`data.name` 也相同的节点,缺的字段从基线补回。

    让模型写 refine 片段时只需写**改了的**东西:没动的节点写 `id` + `data.name` 即可,
    不必通读、手抄基线 JSON(会话 99b8c675 里 agent 为此分块 Read 了 16 次基线)。
    只补**缺失**的键,片段里写了的值(哪怕是空串)一律不动 —— 那是模型的明确意图,
    开始节点锁定、密钥来源等校验照常对它生效。

    `inputParams` 只在 `input_params_for` 不覆盖该节点时才从基线补:覆盖到的节点交给
    `normalize` 按当前 inputs 重新生成(HTTP 的 body 形状随 bodyType 变,拷旧的会错)。
    """
    base_by_id: dict[str, dict] = {}
    for node in _as_list(baseline.get("nodes")):
        n = _as_dict(node)
        if isinstance(n.get("id"), str):
            base_by_id[n["id"]] = n

    filled: list[str] = []
    for node in _as_list(flow.get("nodes")):
        if not isinstance(node, dict):
            continue
        nid = node.get("id")
        base = base_by_id.get(nid) if isinstance(nid, str) else None
        data = node.get("data")
        if base is None or not isinstance(data, dict):
            continue
        base_data = _as_dict(base.get("data"))
        if data.get("name") != base_data.get("name"):
            continue  # 同 id 换了节点类型:不是"没动",基线字段不适用
        for key in _BASELINE_TOP_FIELDS:
            if key not in node and key in base:
                node[key] = copy.deepcopy(base[key])
                filled.append(f"{nid}.{key}")
        for key in _BASELINE_DATA_FIELDS:
            if key not in data and key in base_data:
                data[key] = copy.deepcopy(base_data[key])
                filled.append(f"{nid}.data.{key}")
        if (
            "inputParams" not in data
            and "inputParams" in base_data
            and input_params_for(str(data.get("name") or ""), data.get("inputs")) is None
        ):
            data["inputParams"] = copy.deepcopy(base_data["inputParams"])
            filled.append(f"{nid}.data.inputParams")
    return filled


def normalize(flow: dict) -> list[str]:
    """就地补齐**缺失**的固定样板字段,返回补了什么的可读列表。

    每个节点的 `type` / `version` / `color` / `baseClasses` / `category` / `outputAnchors`
    以及 edge 的 `type` / `id` / `data.sourceColor` / `data.targetColor` 都是从 `data.name`
    机械推导出来的常量。让模型逐个手抄这些值,除了消耗 token 就只是在制造出错机会 ——
    linkfox-workflow 系统自己保存时也会按组件定义规范化它们。

    因此这里只做一件事:**字段缺失时按 NODE_SPECS 填上**。已经存在但与 spec 不一致的值
    一律不动 —— 那可能是刻意为之(或是真 bug),交给 `validate` 报 error/warning,
    避免脚本悄悄改写模型的意图。

    `inputs` / `inputParams` / `label` / `description` 属于语义内容,永远不碰。
    """
    filled: list[str] = []
    nodes = _as_list(flow.get("nodes"))
    name_by_id: dict[str, str] = {}
    layout = _compute_layout(nodes, _as_list(flow.get("edges")))

    for node_index, node in enumerate(nodes):
        n = node if isinstance(node, dict) else None
        if n is None:
            continue
        data = n.get("data")
        if not isinstance(data, dict):
            continue
        name = data.get("name")
        spec = NODE_SPECS.get(name) if isinstance(name, str) else None
        if spec is None:
            continue
        nid = n.get("id")
        if isinstance(nid, str):
            name_by_id[nid] = name

        if "type" not in n:
            n["type"] = spec.top_type
            filled.append(f"{nid}.type={spec.top_type}")
        if "position" not in n:
            # 按 edge 拓扑分层摆放:x 随深度递增,同层的并行分支在 y 轴错开。
            # 纯线性的 (250*i, 0) 会把并行结构画成一条直线,用户在画布上看不出分叉,
            # 会误判"改并行没生效"。用户仍可随意拖动。
            n["position"] = layout.get(nid) or {"x": 250 * node_index, "y": 0}
            filled.append(f"{nid}.position")
        if "positionAbsolute" not in n and isinstance(n.get("position"), dict):
            n["positionAbsolute"] = dict(n["position"])
            filled.append(f"{nid}.positionAbsolute")
        if "version" not in data:
            data["version"] = spec.version
            filled.append(f"{nid}.data.version={spec.version}")
        if "color" not in data:
            data["color"] = spec.color
            filled.append(f"{nid}.data.color={spec.color}")
        if "baseClasses" not in data:
            data["baseClasses"] = list(spec.base_classes)
            filled.append(f"{nid}.data.baseClasses")
        if "category" not in data:
            data["category"] = "Agent Flows"
            filled.append(f"{nid}.data.category")
        if "inputAnchors" not in data:
            data["inputAnchors"] = []
            filled.append(f"{nid}.data.inputAnchors")
        if "outputs" not in data:
            data["outputs"] = {}
            filled.append(f"{nid}.data.outputs")
        if "outputAnchors" not in data:
            # 锚点形状完全由 spec 决定(id = <nodeId>-output-<name>),是最容易手抄错、
            # 且错了会让 linkfox-workflow 系统静默丢边的一处。字段缺失就直接按 spec 生成。
            # 注意:显式写成 `[]` 的情况不在这里补 —— 那由 validate 报 error,
            # 避免把"模型明确写了空数组"当成疏漏悄悄改掉。
            data["outputAnchors"] = [
                {
                    "id": f"{nid}-output-{a}",
                    "name": a,
                    "label": data.get("label") if len(spec.anchors) == 1 else a,
                    "description": "",
                }
                for a in spec.anchors
            ]
            for anchor in data["outputAnchors"]:
                if not isinstance(anchor["label"], str) or not anchor["label"]:
                    anchor["label"] = anchor["name"]
            filled.append(f"{nid}.data.outputAnchors")
        else:
            # 服务端往返差异:fetch 回来的锚点可能缺 `description`(条件锚点上实测出现过),
            # 校验又要求 id/name/label/description 齐全 —— 每次 refine 都得手补一个空串。
            # 这两个是纯展示字段,缺了就补;`id` / `name` 决定 edge 绑定,缺了仍交给校验报错,
            # 不在这里猜。
            for aidx, anchor in enumerate(_as_list(data.get("outputAnchors"))):
                if not isinstance(anchor, dict) or not anchor.get("name"):
                    continue
                if "description" not in anchor:
                    anchor["description"] = ""
                    filled.append(f"{nid}.data.outputAnchors[{aidx}].description")
                if not isinstance(anchor.get("label"), str) or not anchor.get("label"):
                    anchor["label"] = anchor["name"]
                    filled.append(f"{nid}.data.outputAnchors[{aidx}].label")

        # inputParams 与 outputAnchors 同类:它是**字段元数据**(label / type /
        # options / acceptVariable),不是字段值 —— 值住在 inputs 里。同一种节点的这份
        # 元数据永远一样,实测却占了 JSON 全文的近四成,还是漏标 acceptVariable 的
        # 主要来源。有可查证模板的节点直接代填,见 input_params_specs.py。
        #
        # 与 outputAnchors 一致:只在**字段缺失**时补。显式写成 `[]` 是"模型明确
        # 表态",不补,由 validate 报 error。
        if "inputParams" not in data:
            template = input_params_for(name, data.get("inputs"))
            if template is not None:
                data["inputParams"] = template
                filled.append(f"{nid}.data.inputParams")

        # acceptVariable 自愈:字段**已经在 inputParams 里声明了**、值里也确实有
        # `{{ }}`,只是漏了这个布尔 —— 这种是纯疏漏,补上即可(漏了运行时不报错也不
        # 替换,用户看到字面量)。字段完全没声明的情况不在这里处理:那说明缺的是整块
        # 字段元数据,由 validate 报 error 让模型补全。
        _heal_accept_variable(nid, data, filled)

    for eidx, edge in enumerate(_as_list(flow.get("edges"))):
        if not isinstance(edge, dict):
            continue
        if "type" not in edge:
            edge["type"] = "agentFlow"
            filled.append(f"edges[{eidx}].type=agentFlow")
        source = edge.get("source")
        target = edge.get("target")
        if (
            "id" not in edge
            and isinstance(source, str)
            and isinstance(target, str)
        ):
            edge["id"] = (
                f"{source}-{edge.get('sourceHandle')}-{target}-{edge.get('targetHandle')}"
            )
            filled.append(f"edges[{eidx}].id")
        edge_data = edge.get("data")
        if not isinstance(edge_data, dict):
            edge_data = {}
            edge["data"] = edge_data
        src_spec = NODE_SPECS.get(name_by_id.get(source or "", ""))
        tgt_spec = NODE_SPECS.get(name_by_id.get(target or "", ""))
        if "sourceColor" not in edge_data and src_spec:
            edge_data["sourceColor"] = src_spec.color
            filled.append(f"edges[{eidx}].data.sourceColor")
        if "targetColor" not in edge_data and tgt_spec:
            edge_data["targetColor"] = tgt_spec.color
            filled.append(f"edges[{eidx}].data.targetColor")
        if "isHumanInput" not in edge_data:
            # HumanInput 出边必须是 true;这里只给非 HumanInput 的边填 false,
            # 缺失的 true 由 validate 报 error,不替模型下结论。
            if name_by_id.get(source or "") != "humanInputAgentflow":
                edge_data["isHumanInput"] = False
                filled.append(f"edges[{eidx}].data.isHumanInput=false")
        if "edgeLabel" not in edge_data and src_spec and src_spec.edge_label:
            edge_data["edgeLabel"] = src_spec.edge_label
            filled.append(f"edges[{eidx}].data.edgeLabel={src_spec.edge_label}")

    return filled
