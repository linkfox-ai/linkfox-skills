"""`data.inputParams` 的确定性模板 —— 按 `data.name` 索引。

## 为什么存在这个文件

`inputParams` 是**字段元数据**(label / type / options / acceptVariable),不是字段值。
同一种节点的这份元数据永远一样:值住在 `data.inputs` 里,`inputParams` 只描述"这个
节点有哪些字段、哪些字段支持 `{{ }}` 替换"。也就是说它和 `version` / `color` /
`baseClasses` / `outputAnchors` 完全同类 —— 100% 由 `data.name` 推导。

而实测一份 22 节点的 flow 里,`inputParams` 占了 JSON 全文的 39.5%(21,884 / 55,461 字),
比真正有语义的 `inputs` 还长。让模型逐节点手抄这坨东西,只有两个后果:每次生成多花
四成 output token,以及漏标 `acceptVariable: true` —— 漏了运行时不报错也不替换,用户
在飞书通知里看到字面量 `{{ x.output.y }}`。历史上就出过这个 bug。

所以这里把它变成模板,`workflow_spec.normalize()` 在**字段缺失时**按 `data.name` 填上。

## 关键点:`array` 是 schema,不是数据

`conditions` / `formFields` / `headers` 这些 `type: "array"` 字段,它的 `inputParams`
条目里那个 `array` 列表描述的是**单项的字段结构**,与实际有几项无关 —— 实际条目住在
`inputs.conditions` 里。所以模板不需要按条目数展开,直接常量即可。

## 收录标准(不要凭记忆往里加)

只收两类来源可查证的:

- **A 类(已上传 flow 实测)**:从一份已通过 `save_workflow.py` 全部校验、并成功上传到
  linkfox-workflow 系统的真实 flow 里原样取出。
  **注意**:这不等于"从 UI 导出件取出" —— 该 flow 由模型手写、脚本校验通过,但没有逐
  节点在画布上核对过面板渲染。发现某个模板与 UI 实际不符时,以 UI 导出件为准并订正这里。
- **B 类(references 里逐字给出完整 JSON)**:`references/variable-substitution.md`
  第 2/3 节把 Condition / HTTP 的 `inputParams` 整块贴了出来,原样复制。
- **C 类(节点组件定义逐字对照)**:`BusinessStart` 等节点的字段声明逐字对照组件定义
  (label / name / type / options / default / show / hide)。**只有能逐字比对时才允许走
  这一类**,不是"看着字段表补齐"。`BusinessStart` 的 `schedule*` 一组仍未收录(联动复杂)。

**其余节点故意不收**(Agent / LLM / Tool / Retriever / ConditionAgent / ExecuteFlow /
Loop / DataReader / StickyNote / Start):它们字段多、带 `show` 条件联动,references 只
给了字段清单没给完整 `inputParams` JSON,凭清单反推 label / loadMethod 就是在编。
这些节点仍由模型手写 —— 缺了会被 `validate` 按 error 拦下,不会静默放行。

往里加新节点前,先拿一份该节点的真实导出件比对,不要从 references 的字段表反推。
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# 复用片段
# ---------------------------------------------------------------------------

def _kv_array_items() -> list[dict]:
    """`{key, value}` 型 array 字段的单项 schema(headers / queryParams / form body)。"""
    return [
        {"label": "Key", "name": "key", "type": "string", "acceptVariable": True},
        {"label": "Value", "name": "value", "type": "string", "acceptVariable": True},
    ]


# Condition 的 operation 枚举。逐字来自组件定义(references/variable-substitution.md
# 第 2 节)。写错任何一个(例如 `equals` / `startWith` / `greaterThan`)都会让运行时找不
# 到比较函数,永远走 Else 分支。
_CONDITION_OPERATION_OPTIONS = [
    {"label": "Contains", "name": "contains"},
    {"label": "Not Contains", "name": "notContains"},
    {"label": "Ends With", "name": "endsWith"},
    {"label": "Starts With", "name": "startsWith"},
    {"label": "Equal", "name": "equal"},
    {"label": "Not Equal", "name": "notEqual"},
    {"label": "Regex", "name": "regex"},
    {"label": "Is Empty", "name": "isEmpty"},
    {"label": "Not Empty", "name": "notEmpty"},
    {"label": "Smaller", "name": "smaller"},
    {"label": "Smaller Equal", "name": "smallerEqual"},
    {"label": "Larger", "name": "larger"},
    {"label": "Larger Equal", "name": "largerEqual"},
]

_HTTP_BODY_TYPE_OPTIONS = [
    {"label": "JSON", "name": "json"},
    {"label": "Raw", "name": "raw"},
    {"label": "Form Data", "name": "formData"},
    {"label": "x-www-form-urlencoded", "name": "xWwwFormUrlencoded"},
]

_HTTP_RESPONSE_TYPE_OPTIONS = [
    {"label": "JSON", "name": "json"},
    {"label": "Text", "name": "text"},
    {"label": "Array Buffer", "name": "arraybuffer"},
    {"label": "Base64", "name": "base64"},
]

# 源码里 `body` 是两个同名字段:bodyType ∈ [json, raw] 用 string 版;
# ∈ [formData, xWwwFormUrlencoded] 用 array of {key,value} 版。
_FORM_BODY_TYPES = {"formData", "xWwwFormUrlencoded"}


def _http_body_param(body_type: str) -> dict:
    if body_type in _FORM_BODY_TYPES:
        return {
            "label": "Body",
            "name": "body",
            "type": "array",
            "acceptVariable": True,
            "optional": True,
            "array": _kv_array_items(),
        }
    return {
        "label": "Body",
        "name": "body",
        "type": "string",
        "acceptVariable": True,
        "optional": True,
    }


# ---------------------------------------------------------------------------
# A 类:线上导出件实测
# ---------------------------------------------------------------------------

# 逐字取自 BusinessStart 组件定义(C 类,见文件头「收录标准」)。schedule* 那一组不收:
# 字段多且带 frequency 联动,凭字段表反推 label / options 就是在编 —— 与 Agent / LLM 同处理。
_BUSINESS_START = [
    {
        "label": "启动方式",
        "name": "startInputType",
        "type": "options",
        "renderAs": "startTriggerCards",
        "options": [
            {"label": "手动启动", "name": "chatInput"},
            {"label": "按业务时间启动", "name": "scheduleInput"},
            {"label": "店铺授权", "name": "storeAuthorization"},
            {"label": "多维表格记录触发", "name": "tableRecordTrigger"},
        ],
        "default": "chatInput",
    },
    {
        "label": "授权店铺",
        "name": "amazonStore",
        "type": "asyncOptions",
        "loadMethod": "listAmazonStores",
        "refresh": True,
        "show": {"startInputType": "storeAuthorization"},
    },
    {
        "label": "检查哪些数据变化",
        "name": "storeChangeType",
        "type": "options",
        "options": [
            {"label": "Listing", "name": "listing"},
            {"label": "订单列表", "name": "orderList"},
            {"label": "售后订单", "name": "afterSalesOrder"},
            {"label": "FBA 库存明细", "name": "fbaInventory"},
            {"label": "移除订单", "name": "removalOrder"},
        ],
        "default": "orderList",
        "show": {"startInputType": "storeAuthorization"},
    },
    {
        "label": "查询间隔（分钟）",
        "name": "storeCheckIntervalMinutes",
        "type": "number",
        "default": 10,
        "show": {"startInputType": "storeAuthorization"},
    },
    {
        "label": "多维表格",
        "name": "notebookId",
        "type": "asyncOptions",
        "loadMethod": "listLinkfoxNotebooks",
        "refresh": True,
        "show": {"startInputType": "tableRecordTrigger"},
    },
    {
        "label": "数据表",
        "name": "tableId",
        "type": "asyncOptions",
        "loadMethod": "listRecordTriggerTables",
        "refresh": True,
        "show": {"startInputType": "tableRecordTrigger"},
    },
    {
        "label": "选择记录事件",
        "name": "recordEventType",
        "type": "options",
        "renderAs": "recordEventCards",
        "options": [
            {"label": "新增记录时", "name": "recordCreated"},
            {"label": "修改记录时", "name": "recordUpdated"},
            {"label": "新增或修改后满足条件时", "name": "recordConditionMet"},
            # 卡片渲染但禁用;服务端保存与画布校验都会拒绝这个值。
            {"label": "到达记录中的时间时", "name": "recordTimeReached", "disabled": True},
        ],
        "default": "recordCreated",
        "show": {"startInputType": "tableRecordTrigger"},
    },
    {
        "label": "监听字段（可选）",
        "name": "recordWatchFieldNames",
        "type": "asyncMultiOptions",
        "loadMethod": "listRecordTriggerFields",
        "refresh": True,
        "optional": True,
        "show": {
            "startInputType": "tableRecordTrigger",
            "recordEventType": "recordUpdated",
        },
    },
    {
        "label": "条件字段",
        "name": "recordConditionFieldName",
        "type": "asyncOptions",
        "loadMethod": "listRecordTriggerFields",
        "refresh": True,
        "show": {
            "startInputType": "tableRecordTrigger",
            "recordEventType": "recordConditionMet",
        },
    },
    {
        "label": "判断方式",
        "name": "recordConditionOperator",
        "type": "options",
        "options": [
            {"label": "等于", "name": "equal"},
            {"label": "不等于", "name": "notEqual"},
            {"label": "包含", "name": "contains"},
            {"label": "不包含", "name": "notContains"},
            {"label": "大于", "name": "isGreater"},
            {"label": "小于", "name": "isLess"},
            {"label": "为空", "name": "isEmpty"},
            {"label": "非空", "name": "notEmpty"},
        ],
        "default": "equal",
        "show": {
            "startInputType": "tableRecordTrigger",
            "recordEventType": "recordConditionMet",
        },
    },
    {
        "label": "条件值",
        "name": "recordConditionValue",
        "type": "string",
        "show": {
            "startInputType": "tableRecordTrigger",
            "recordEventType": "recordConditionMet",
        },
        # 这两个算子在 listRecords filter 里不接受 value,面板上隐藏该项。
        "hide": {"recordConditionOperator": ["isEmpty", "notEmpty"]},
    },
    {
        "label": "记录变更检查间隔（分钟）",
        "name": "recordCheckIntervalMinutes",
        "type": "number",
        "default": 10,
        "show": {"startInputType": "tableRecordTrigger"},
    },
]

# C 类:逐字对照 FillForm 组件定义(version 1.2)。不要再加 `formTitle` / `description` /
# `defaultValue`,这三个字段已不存在。
_FILL_FORM = [
    {
        "label": "表单字段",
        "name": "formFields",
        "type": "array",
        "array": [
            # 源码里 `type` 排在第一个,顺序照抄(面板按 inputParams 顺序渲染)。
            {
                "label": "类型",
                "name": "type",
                "type": "options",
                "options": [
                    {"label": "单行文本", "name": "text"},
                    {"label": "多行文本", "name": "textarea"},
                    {"label": "数字", "name": "number"},
                    {"label": "布尔（复选框）", "name": "boolean"},
                    {"label": "日期", "name": "date"},
                    {"label": "单选", "name": "radio"},
                    {"label": "多选", "name": "checkbox"},
                    # 单个文件,前端选完立即直传 OSS,字段值是公开 HTTPS URL。
                    # 用了它该节点需要 linkfoxAgentApi 凭据(后台自动绑定)。
                    {"label": "多媒体（单个文件）", "name": "media"},
                ],
                "default": "text",
            },
            {"label": "显示名称", "name": "label", "type": "string"},
            {"label": "变量名", "name": "name", "type": "string"},
            {
                "label": "是否必填",
                "name": "required",
                "type": "boolean",
                "default": False,
                "optional": True,
            },
            {
                "label": "选项",
                "name": "addOptions",
                "type": "array",
                # 源码里这一项带 show,只在 radio / checkbox 时出现
                "show": {"formFields[$index].type": ["radio", "checkbox"]},
                "array": [{"label": "选项", "name": "option", "type": "string"}],
            },
        ],
    },
    {
        "label": "提交按钮文案",
        "name": "submitButtonText",
        "type": "string",
        "default": "Submit",
        "optional": True,
    },
]

# C 类:逐字对照 CustomPythonFunction 组件定义取 name / type / default / acceptVariable。
# 两处有意偏离源码:
#   - 不抄 codeExample / description 长文案(纯 UI 提示,不影响执行)。
#   - Update Flow State 的 Key 源码是 asyncOptions + listRuntimeStateKeys,那个 loadMethod
#     对 BusinessStart 的 undefined startState 直接 `.map()` 抛错;与 CustomFunction 一样
#     改成可自由输入的 string,否则面板上 Key 永远选不出来。
_CUSTOM_PYTHON_FUNCTION = [
    {
        "label": "Python Code",
        "name": "customPythonFunctionCode",
        "type": "code",
        "codeLanguage": "python",
    },
    {
        "label": "Libraries",
        "name": "customPythonFunctionLibraries",
        "type": "string",
        "optional": True,
        "placeholder": "requests,pandas",
    },
    {
        "label": "Input Variables",
        "name": "customPythonFunctionInputVariables",
        "type": "array",
        "optional": True,
        "acceptVariable": True,
        "array": [
            {"label": "Variable Name", "name": "variableName", "type": "string"},
            {
                "label": "Variable Value",
                "name": "variableValue",
                "type": "string",
                "acceptVariable": True,
            },
        ],
    },
    {
        "label": "Timeout (ms)",
        "name": "customPythonFunctionTimeout",
        "type": "number",
        "optional": True,
        "default": 60000,
    },
    {
        "label": "Update Flow State",
        "name": "customPythonFunctionUpdateState",
        "type": "array",
        "optional": True,
        "acceptVariable": True,
        "array": [
            {
                "label": "Key",
                "name": "key",
                "type": "string",
                "acceptVariable": True,
            },
            {
                "label": "Value",
                "name": "value",
                "type": "string",
                "acceptVariable": True,
                "acceptNodeOutputAsVariable": True,
            },
        ],
    },
]

_CUSTOM_FUNCTION = [
    {
        "label": "Function",
        "name": "customFunctionJavascriptFunction",
        "type": "code",
    },
    {
        "label": "Input Variables",
        "name": "customFunctionInputVariables",
        "type": "array",
        "optional": True,
        "array": [
            {"label": "Variable Name", "name": "variableName", "type": "string"},
            {
                "label": "Variable Value",
                "name": "variableValue",
                "type": "string",
                "acceptVariable": True,
            },
        ],
    },
    {
        "label": "Update State",
        "name": "customFunctionUpdateState",
        "type": "array",
        "optional": True,
        "array": [
            {
                "label": "Key",
                "name": "key",
                "type": "string",
                "acceptVariable": True,
            },
            {
                "label": "Value",
                "name": "value",
                "type": "string",
                "acceptVariable": True,
                "acceptNodeOutputAsVariable": True,
            },
        ],
    },
]

# 只覆盖 descriptionType = fixed(默认)分支。dynamic 分支要额外的
# humanInputModel / humanInputModelConfig / humanInputModelPrompt,references 没给
# 完整 inputParams JSON(尤其 asyncOptions 的 loadMethod 名),不猜 —— 见
# `input_params_for()` 里的分支处理。
_HUMAN_INPUT_FIXED = [
    {
        "label": "Description Type",
        "name": "humanInputDescriptionType",
        "type": "options",
        "options": [
            {"label": "Fixed", "name": "fixed"},
            {"label": "Dynamic", "name": "dynamic"},
        ],
    },
    {
        "label": "Enable Feedback",
        "name": "humanInputEnableFeedback",
        "type": "boolean",
        "default": True,
    },
    {
        "label": "Description",
        "name": "humanInputDescription",
        "type": "string",
        "rows": 6,
        "acceptVariable": True,
    },
]

_CROSS_BORDER_EXPERT = [
    {
        "label": "Expert ID",
        "name": "expertId",
        "type": "asyncOptions",
        "loadMethod": "listExperts",
    },
    {
        "label": "Task Instruction",
        "name": "taskInstruction",
        "type": "string",
        "rows": 6,
        "acceptVariable": True,
    },
    {"label": "Timeout (ms)", "name": "timeoutMs", "type": "number", "default": 120000},
    {
        "label": "Poll Interval (ms)",
        "name": "pollIntervalMs",
        "type": "number",
        "default": 2000,
    },
    {
        "label": "Update State",
        "name": "crossBorderExpertUpdateState",
        "type": "array",
        "optional": True,
        "array": [
            # 注意:这里 Key 用 freeSolo(BusinessStart 没有 startState,State key 下拉
            # 会加载失败,只有本节点补了兜底并允许自由输入),与 CustomFunction 的
            # acceptVariable 写法不同 —— 两处都来自实测导出件,不要"统一"。
            {"label": "Key", "name": "key", "type": "string", "freeSolo": True},
            {
                "label": "Value",
                "name": "value",
                "type": "string",
                "acceptVariable": True,
                "acceptNodeOutputAsVariable": True,
            },
        ],
    },
]

_SEND_NOTIFICATION = [
    {
        "label": "Channels",
        "name": "channels",
        "type": "multiOptions",
        "options": [
            {"label": "Email", "name": "email"},
            {"label": "Feishu", "name": "feishu"},
            {"label": "DingTalk", "name": "dingtalk"},
        ],
        "default": ["feishu"],
    },
    {
        "label": "Recipients",
        "name": "recipients",
        "type": "string",
        "rows": 3,
        "acceptVariable": True,
    },
    {
        "label": "Message Content",
        "name": "messageContent",
        "type": "string",
        "rows": 6,
        "acceptVariable": True,
    },
    {
        "label": "Email Subject",
        "name": "emailSubject",
        "type": "string",
        "acceptVariable": True,
        "optional": True,
    },
    {
        "label": "Email CC",
        "name": "emailCc",
        "type": "string",
        "acceptVariable": True,
        "optional": True,
    },
    {
        "label": "Feishu Webhook",
        "name": "feishuWebhook",
        "type": "password",
        "optional": True,
    },
    {
        "label": "Feishu Sign Secret",
        "name": "feishuSignSecret",
        "type": "password",
        "optional": True,
    },
    {
        "label": "DingTalk Webhook",
        "name": "dingtalkWebhook",
        "type": "password",
        "optional": True,
    },
    {
        "label": "DingTalk Sign Secret",
        "name": "dingtalkSignSecret",
        "type": "password",
        "optional": True,
    },
    {"label": "Timeout (ms)", "name": "timeoutMs", "type": "number", "default": 15000},
]

# C 类:逐字对照 WriteFile 组件定义。选已有表是**两级**下拉
# (notebookId → tableId),新建表先选建在哪(newTableNotebookId)再填表名。
_WRITE_FILE = [
    {
        "label": "写入目标",
        "name": "writeDestination",
        "type": "options",
        "options": [
            {"label": "多维表", "name": "linkfoxTable"},
            {"label": "新建多维表", "name": "newLinkfoxTable"},
            # 改已有行(PATCH 语义,走 updateRecords)。源码 2026-09-23 新增,
            # 代填漏了它会让「更新已有记录」在面板上压根不出现。
            {"label": "更新已有记录", "name": "updateLinkfoxTable"},
        ],
        "default": "linkfoxTable",
    },
    {
        "label": "多维表格",
        "name": "notebookId",
        "type": "asyncOptions",
        "loadMethod": "listLinkfoxNotebooks",
        "refresh": True,
        "show": {"writeDestination": ["linkfoxTable", "updateLinkfoxTable"]},
    },
    {
        "label": "数据表",
        "name": "tableId",
        "type": "asyncOptions",
        "loadMethod": "listLinkfoxTables",
        "refresh": True,
        "show": {"writeDestination": ["linkfoxTable", "updateLinkfoxTable"]},
    },
    {
        "label": "记录 ID",
        "name": "updateRecordId",
        "type": "string",
        # 支持变量引用:记录触发的流程留空即可(节点自己从上一步结果里取 recordId)
        "acceptVariable": True,
        "optional": True,
        "show": {"writeDestination": "updateLinkfoxTable"},
    },
    {
        "label": "新建位置",
        "name": "newTableNotebookId",
        "type": "asyncOptions",
        "loadMethod": "listNewTableNotebooks",
        "refresh": True,
        "default": "__new__",
        "show": {"writeDestination": "newLinkfoxTable"},
    },
    {
        "label": "新建数据表名称",
        "name": "newTableName",
        # 此前漏了 `type`(源码声明是 string),代填出来的条目缺这一项面板无从知道渲染成
        # 什么控件 —— 与本文件其它条目不一致,补上。
        "type": "string",
        # ⚠️ 源码声明里**没有** acceptVariable —— 这里刻意多标一个 True。变量替换只看
        # flowData 里的 `inputParams`(buildAgentflow 读 reactFlowNodeData.inputParams),
        # 不标就无法把表名拼成 `报表-{{...}}`。用户在 UI 上打开该节点重存时可能被源码
        # 声明覆盖回去,那时表名里的模板会退化成字面量。
        "acceptVariable": True,
        "show": {"writeDestination": "newLinkfoxTable"},
    },
    {
        "label": "超时时间（毫秒）",
        "name": "timeoutMs",
        "type": "number",
        "default": 180000,
        "optional": True,
    },
]


def _linkfox_http(body_type: str) -> list[dict]:
    return [
        {
            "label": "Method",
            "name": "method",
            "type": "options",
            "options": [
                {"label": "GET", "name": "GET"},
                {"label": "POST", "name": "POST"},
                {"label": "PUT", "name": "PUT"},
                {"label": "DELETE", "name": "DELETE"},
                {"label": "PATCH", "name": "PATCH"},
            ],
            "default": "POST",
        },
        {"label": "Path", "name": "path", "type": "string", "acceptVariable": True},
        {
            "label": "Headers",
            "name": "headers",
            "type": "array",
            "acceptVariable": True,
            "optional": True,
            "array": _kv_array_items(),
        },
        {
            "label": "Query Params",
            "name": "queryParams",
            "type": "array",
            "acceptVariable": True,
            "optional": True,
            "array": _kv_array_items(),
        },
        {
            "label": "Body Type",
            "name": "bodyType",
            "type": "options",
            "options": list(_HTTP_BODY_TYPE_OPTIONS),
            "default": "json",
        },
        _http_body_param(body_type),
        {
            "label": "Response Type",
            "name": "responseType",
            "type": "options",
            "options": list(_HTTP_RESPONSE_TYPE_OPTIONS),
            "default": "json",
        },
        {"label": "Timeout", "name": "timeout", "type": "number", "default": 60000},
    ]


# ---------------------------------------------------------------------------
# B 类:references/variable-substitution.md 逐字给出
# ---------------------------------------------------------------------------

_CONDITION = [
    {
        "label": "Conditions",
        "name": "conditions",
        "type": "array",
        "description": "Values to compare",
        "acceptVariable": True,
        "default": [
            {"type": "string", "value1": "", "operation": "equal", "value2": ""}
        ],
        "array": [
            {
                "label": "Type",
                "name": "type",
                "type": "options",
                "options": [
                    {"label": "String", "name": "string"},
                    {"label": "Number", "name": "number"},
                    {"label": "Boolean", "name": "boolean"},
                ],
                "default": "string",
            },
            {
                "label": "Value 1",
                "name": "value1",
                "type": "string",
                "acceptVariable": True,
            },
            {
                "label": "Operation",
                "name": "operation",
                "type": "options",
                "options": list(_CONDITION_OPERATION_OPTIONS),
                "default": "equal",
            },
            {
                "label": "Value 2",
                "name": "value2",
                "type": "string",
                "acceptVariable": True,
            },
        ],
    },
]


def _http(body_type: str) -> list[dict]:
    return [
        {
            "label": "Method",
            "name": "method",
            "type": "options",
            "options": [
                {"label": "GET", "name": "GET"},
                {"label": "POST", "name": "POST"},
                {"label": "PUT", "name": "PUT"},
                {"label": "PATCH", "name": "PATCH"},
                {"label": "DELETE", "name": "DELETE"},
            ],
            "default": "GET",
        },
        {"label": "URL", "name": "url", "type": "string", "acceptVariable": True},
        {
            "label": "Headers",
            "name": "headers",
            "type": "array",
            "acceptVariable": True,
            "optional": True,
            "array": _kv_array_items(),
        },
        {
            "label": "Query Params",
            "name": "queryParams",
            "type": "array",
            "acceptVariable": True,
            "optional": True,
            "array": _kv_array_items(),
        },
        {
            "label": "Body Type",
            "name": "bodyType",
            "type": "options",
            "options": list(_HTTP_BODY_TYPE_OPTIONS),
            "default": "json",
        },
        _http_body_param(body_type),
        {
            "label": "Response Type",
            "name": "responseType",
            "type": "options",
            "options": list(_HTTP_RESPONSE_TYPE_OPTIONS),
            "default": "json",
        },
    ]


# ---------------------------------------------------------------------------
# 索引
# ---------------------------------------------------------------------------

# 值为 None 的项:形状随 `inputs` 里某个字段变,走 `input_params_for()` 的分支。
_STATIC_SPECS: dict[str, list[dict]] = {
    # A 类
    "businessStartAgentflow": _BUSINESS_START,
    "fillFormAgentflow": _FILL_FORM,
    "customFunctionAgentflow": _CUSTOM_FUNCTION,
    "customPythonFunctionAgentflow": _CUSTOM_PYTHON_FUNCTION,
    "crossBorderExpertAgentflow": _CROSS_BORDER_EXPERT,
    "sendNotificationAgentflow": _SEND_NOTIFICATION,
    "writeFileAgentflow": _WRITE_FILE,
    # End 没有任何可配置字段,真实导出件里就是空数组。
    "endAgentflow": [],
    # B 类
    "conditionAgentflow": _CONDITION,
}

# 形状随 inputs 分支的节点。
_DYNAMIC_NAMES = {
    "linkfoxHttpAgentflow",
    "httpAgentflow",
    "humanInputAgentflow",
}

COVERED_NAMES: frozenset[str] = frozenset(_STATIC_SPECS) | frozenset(_DYNAMIC_NAMES)


def _deep_copy(value: Any) -> Any:
    """模板必须按值返回 —— 调用方会把它挂进 flow 再被别处改。"""
    if isinstance(value, dict):
        return {k: _deep_copy(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_copy(v) for v in value]
    return value


def input_params_for(name: str, inputs: Any = None) -> list[dict] | None:
    """按 `data.name`(+ 必要时 `data.inputs` 的分支字段)返回 `inputParams` 模板。

    返回 `None` 表示"本表不覆盖这个节点/这个分支",调用方不要代填 —— 让模型自己写,
    写漏了由 `validate` 报 error。**不要为了"看起来覆盖率高"给没有可查证来源的节点
    编一份模板**:填错 `acceptVariable` 比不填更糟,不填至少会被拦下。
    """
    inputs_dict = inputs if isinstance(inputs, dict) else {}

    if name in ("linkfoxHttpAgentflow", "httpAgentflow"):
        body_type = inputs_dict.get("bodyType")
        body_type = body_type if isinstance(body_type, str) else "json"
        builder = _linkfox_http if name == "linkfoxHttpAgentflow" else _http
        return builder(body_type)

    if name == "humanInputAgentflow":
        desc_type = inputs_dict.get("humanInputDescriptionType")
        # dynamic 分支要 humanInputModel / ModelConfig / ModelPrompt,references 没给
        # 完整 JSON,不猜。
        if isinstance(desc_type, str) and desc_type == "dynamic":
            return None
        return _deep_copy(_HUMAN_INPUT_FIXED)

    spec = _STATIC_SPECS.get(name)
    if spec is None:
        return None
    return _deep_copy(spec)
