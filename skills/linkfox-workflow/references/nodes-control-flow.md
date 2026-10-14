# linkfox-workflow Agentflow v2：分支、循环、迭代与人工审批

计划使用 Condition、ConditionAgent、Loop、Iteration 或 HumanInput 时读取本文件。通用结构与 edge 规则见 `flow-structure.md`。

## Condition

- `data.name`: `conditionAgentflow`；`data.type`: `Condition`；`version`: `1.0`；`color`: `#FFB938`。
- 静态 if/else，按字段值做规则匹配。
- 必填 `inputs.conditions[]`：每项 `{type, value1, operation, value2}`，至少一条。
- `operation` 必须逐字匹配以下枚举：
  - string：`contains` / `endsWith` / `equal` / `notContains` / `notEqual` / `regex` / `startsWith` / `isEmpty` / `notEmpty`；
  - number：`smaller` / `smallerEqual` / `equal` / `notEqual` / `larger` / `largerEqual` / `isEmpty` / `notEmpty`；
  - boolean：`equal` / `notEqual`。
- 是 `equal`，不是 `equals`。
- **固定两个输出锚点**（不随 conditions 数量变化）：`<id>-output-0` 对应"任一 condition 满足"，`<id>-output-1` 是 Else。`sourceHandle` 只能是 `<id>-output-0` 或 `<id>-output-1`，`edgeLabel` 用 `"0"` / `"1"`。
- 想要多路分支时用 ConditionAgent（同样固定 2 个锚点）或串联多个 Condition。
- 判定顺序：按顺序遍历 conditions，任一命中即走 `output-0`，全部未命中走 `output-1`（Else）；`regex` 的值里可直接写字面量 `\ [ ] *`。
- 类型默认值：`type` 默认 `string`；string 的 `value2` 在 `operation ∈ [isEmpty, notEmpty]` 时隐藏；number 的 `value2` 默认 `0`；boolean 的 `value1`/`value2` 默认 `false`。
- **`inputParams` 整个字段别写**：Condition 的 `inputParams`（含完整 `operation` 枚举、`value1`/`value2` 的 `acceptVariable`）由 `save_workflow.py` 代填。写成 `[]` 不算省略、会报 error。你只填 `inputs.conditions`（字段**值**）。

## ConditionAgent

> ⚠️ **同属模型推理场景的兜底节点，不是默认选择**。`CrossBorderExpert` 不支持节点内动态分支判断；只有确实需要"由 LLM 直接读场景描述做分支"时才用本节点，并在方案里点出兜底原因（见 `node-catalog.md` 选择规则、`nodes-linkfox-custom.md`）。可枚举的确定规则仍应优先用 `Condition`。

- `data.name`: `conditionAgentAgentflow`；`data.type`: `ConditionAgent`；`version`: `2.0`；`color`: `#ff8fab`。
- 由 LLM 根据自然语言场景做动态分支。
- 必填：`conditionAgentModel`、`conditionAgentModelConfig`、`conditionAgentInstructions`、`conditionAgentInput`（默认 `{{ question }}`）、`conditionAgentScenarios[]`（至少 1 项，默认 2 个空 scenario；每项 `{scenario:"<场景描述>"}`）。
- **固定两个输出锚点**：`<id>-output-0` 表示"任一 scenario 匹配"，`<id>-output-1` 是兜底 Else。`sourceHandle` 只能是 `<id>-output-0` 或 `<id>-output-1`；`edgeLabel` 用 `"0"` / `"1"` 或对应 scenario 文本。
- 内存字段（可选，与 Agent 一致）：`conditionAgentEnableMemory`（默认 `true`）、`conditionAgentMemoryType`（`allMessages` / `windowSize` / `conversationSummary` / `conversationSummaryBuffer`）、`conditionAgentMemoryWindowSize`（`show: memoryType==='windowSize'`，默认 `'20'`）、`conditionAgentMemoryMaxTokenLimit`（`show: memoryType==='conversationSummaryBuffer'`，默认 `'2000'`）、`conditionAgentUserMessage`（`show: enableMemory===true`）。
- 覆盖 system prompt：`conditionAgentOverrideSystemPrompt`（布尔）+ `conditionAgentSystemPrompt`（string，仅 override 为 true 时用）。
- 该节点没有 `conditionAgentReturnResponseAs` 与 `conditionAgentStructuredOutput`（与 Agent/LLM 不同）；结构化输出章节的说明仅对 Agent 和 LLM 生效。
- `conditionAgentInstructions` 要让模型只在给定场景里选，避免输出场景之外的内容。

## Loop

- `data.name`: `loopAgentflow`；`data.type`: `Loop`；`version`: `1.2`；`color`: `#FFA07A`；`hideOutput: true`。
- 把执行游标跳回上游节点，用于有上限的重试。
- 必填：`loopBackToNode`（值形如 `<上游 nodeId>-<label>`，可手填）和 `maxLoopCount`（type `number`，默认 `5`，无 min/max/step）。
- 没有 output anchor（`hideOutput: true`）；禁止从 Loop 连出 edge。
- 提示：Loop 回跳的 LLM/Agent 节点应打开 memory，否则每次循环都是无上下文调用。
- 回跳消息中的 `{{ output }}` 会被替换为上一轮结果字符串；写入 state 时可用此占位。
- 循环体仅放只读节点：Agent / LLM / Retriever / Tool / CustomFunction / Condition / ConditionAgent；不要把 HTTP 写请求、ExecuteFlow、HumanInput 或 DirectReply 放入循环。**查询类的 HTTP / LinkfoxHTTP 是例外**——轮询异步任务时它就该在环里（见下条）。
- **轮询异步任务**（`/aigc/*Async` 这类只回 `taskId` 的接口）是 Loop 的主要用法：`CustomFunction(await sleep(<毫秒>))` → 查询接口 → `Condition(status equal SUCCESS)`，Else 分支接 `Loop` 回跳到 **sleep 节点**（不是创建任务的节点——指错会每轮重建任务、真实扣算力）。`maxLoopCount` 生图/生文给 `20`、生视频给 `40`。下载、写表、发通知一律放 SUCCESS 分支，别留在回跳路径上。完整规则见 `nodes-linkfox-custom.md` 的"异步任务接口：必须自己搭轮询循环"。

## Iteration

- `data.name`: `iterationAgentflow`；`data.type`: `Iteration`；`version`: `1.0`；`color`: `#9C89B8`；顶层 `type`: `iteration`。
- 对数组的每项运行内部节点。
- 唯一输入 `inputs.iterationInput`（type `string`，`acceptVariable: true`，rows 4）：数组表达式或上游输出引用；必须指向实际叶子字段，不要使用裸 `.output`。
- 输入必须解析为数组，否则执行失败；引号、方括号、花括号不要多余转义。
- 输出锚点：`<id>-output-iterationAgentflow`（未设 `hideOutput`）。
- 每个子节点是独立 node，带 `parentNode: "<iterationNodeId>"` 和 `extent: "parent"`，自身顶层 `type` 仍为 `agentFlow`。外部节点用普通 edge 连入 Iteration；子节点之间也使用普通 edge。

## HumanInput

- `data.name`: `humanInputAgentflow`；`data.type`: `HumanInput`；`version`: `1.0`；`color`: `#6E6EFD`。
- 暂停等待人工 proceed / reject，可带反馈。
- 必填：`humanInputDescriptionType`（`fixed` 或 `dynamic`，无默认值——生成 flow 时必须显式填一个）、`humanInputEnableFeedback`（默认 `true`，非 optional）。
  - fixed 时填 `humanInputDescription`（HTML，`show: humanInputDescriptionType==='fixed'`，`placeholder: "Are you sure you want to proceed?"`）。
  - dynamic 时填 `humanInputModel`、`humanInputModelConfig`、`humanInputModelPrompt`（`show: humanInputDescriptionType==='dynamic'`）。
- 模型不要选 `LlamaIndex` 类的 chat 模型。
- **两个输出锚点的 `name` 分别是 `proceed` 和 `reject`**——`sourceHandle` 是 `<id>-output-proceed` / `<id>-output-reject`，**不是** `-output-0` / `-output-1`。两条出边都必须设置 `data.isHumanInput: true`，并有 `data.edgeLabel: "proceed"` 或 `"reject"`。

## 分支选择与限制

- 可枚举的确定规则 → Condition；需要语言理解判定 → ConditionAgent。
- 逐项处理列表 → Iteration；带上限的重试 → Loop；人工审批 → HumanInput。
- HumanInput 的两个出口都应接到明确分支；少接 Else 虽允许，但必须提示用户该路径会无出口。

## 运行时已观察到、尚未定位根因的两个问题

以下两条来自 2026-10-08 一次真实执行的复盘。静态校验都能通过，`save_workflow.py` 只报 warning，不拦。根因确认后要回来改这一节，不要把这里的绕法当成永久规则。

| 现象 | 已验证可行的做法 | 不要推广成 |
| --- | --- | --- |
| `CustomPythonFunction` 的 `output.result` 保留 Python 原类型。布尔值被引用进 Condition 的比较值时报 `output.replace is not a function` | 在 Python 里把该字段转成字符串（如 `"true"` / `"false"`），Condition 用 string 比较 | "所有节点输出一律字符串化"：数字、对象、数组进 Condition 的行为没有逐一验证 |
| 互斥分支（同一个 Condition / ConditionAgent / HumanInput 的不同出口）汇到同一个下游节点。该节点运行时没被执行 | 必须发生的动作（写表、通知等）每个分支各接一份；或执行时用 `run_workflow.py --expect-reached <nodeId>` 核对它确实执行到 | "禁止一切多入边节点"：真正串行的多入边、公共 End 的行为没有反例 |

拿不准时，用一次带 `--expect-reached` / `--expect-not-reached` 的执行来验证实际走的路径，不要凭静态结构推断。
