# linkfox-workflow Agentflow v2：结构与起点节点

生成、修改或校验任意 agentflow v2 时先读本文件。

## 顶层与通用节点结构

顶层只允许这四个字段：

```json
{
  "description": "<一句话说明这个 flow 做什么>",
  "usecases": ["Extraction"],
  "nodes": [ /* 至少一个 BusinessStart；多节点时每个非 StickyNote 节点都必须被 edges 连上 */ ],
  "edges": [ /* 多节点 flow 的 edges 不得为空;每条边形状见下方 Edge 一节 */ ]
}
```

**多节点 flow 的 `edges` 不得为空**;每个应由 edge 连接的节点必须至少参与一条 edge。`save_workflow.py` 会拒绝孤立节点和 BusinessStart 无出边(exit 65)。生成前先把连线画通再落笔。

不计入连通性检查的两类节点：**StickyNote**（纯批注）和 **Iteration 子节点**（带 `parentNode` + `extent: "parent"`，靠父节点归属而非 edge 连接）。执行链**不要求**以 DirectReply 收尾，WriteFile / SendNotification / Agent 等作为末节点结束都合法。

`usecases` 是字符串数组，常用值为 `Agent` / `Extraction` / `Human In Loop` / `Hierarchical Agent Teams` / `RAG` / `Iteration`。

每个常规节点使用（`<data.name>_<index>` 是**新建**节点的写法；refine 时基线里已有的 id 一律原样保留，见下方 id 规则）：

```json
{
  "id": "<data.name>_<index>",
  "type": "agentFlow",
  "position": { "x": 0, "y": 0 },
  "width": 175,
  "height": 72,
  "positionAbsolute": { "x": 0, "y": 0 },
  "selected": false,
  "dragging": false,
  "data": {
    "id": "<同顶层 id>",
    "label": "<用户可读名称>",
    "version": 1,
    "name": "<固定 camelCase 名称>",
    "type": "<固定 PascalCase 类型>",
    "color": "<固定色号>",
    "baseClasses": ["<同 type>"],
    "category": "Agent Flows",
    "description": "<节点说明>",
    "inputParams": [],
    "inputAnchors": [],
    "inputs": {},
    "outputAnchors": [ /* 见"Anchor 形状规范"节，非空对象数组 */ ],
    "outputs": {},
    "selected": false
  }
}
```

> **样板字段可以省略。** 上面模板里，顶层 `type` / `position` / `positionAbsolute` / `width` / `height` / `selected` / `dragging`，`data.version` / `color` / `baseClasses` / `category` / `inputAnchors` / `outputs` / `outputAnchors`，以及**大部分节点的 `data.inputParams`** 全部由 `data.name` 机械推导，`save_workflow.py` 自动补齐（补了什么会列在 stdout 的 `normalized` 里）。refine 时基线里已有的节点还会按 id 从 fetch 基线补回 `position` / `inputs` / `credential` 等，见 SKILL.md「执行流程」第 5 步。
> 你只需要写有语义的部分：`id` / `data.id` / `data.label` / `data.name` / `data.type` / `data.description` / `data.inputs`，以及 edge 的 `source` / `sourceHandle` / `target` / `targetHandle`。`data.inputParams` 只有脚本不覆盖的节点才要写（见下一条）。
> 手抄这些常量只会增加出错机会。**但写了就必须写对**：写错的值不会被静默改写，而是按 error/warning 报出来。显式写成 `[]` 的 `outputAnchors` 视为明确表态，不会被代填，直接判 error。

- `data.id` 与顶层 `id` 必须完全一致,且形如 `<data.name>_<数字>`。**新建节点用顺序号**(`_0` / `_1`,同一 `data.name` 从 0 起递增)。`save_workflow.py` 校验**前缀逐字等于 `data.name`**、**后缀是纯数字**与 id 唯一性,**不要求后缀连号**:画布上新增的节点后缀是随机数(`fillFormAgentflow_415972`),同样合法。后缀里出现字母(`_a1`)会被拒,否则该节点的所有 `{{ }}` 引用检查会失效。**refine 时基线里已有的 id 一律原样保留**,不要归一化成顺序号:改 id 等于删旧建新,它的 edge 和下游 `{{ }}` 引用会一起失效。
- 顶层 `type` 仅可为 `agentFlow`、`iteration` 或 `stickyNote`；只有 Iteration 使用 `iteration`，只有 StickyNote 使用 `stickyNote`。
- `inputAnchors` 必须是空数组；`outputs` 通常为 `{}`；未填写的 inputs 用 `""` 或节点默认值。
- **`inputParams` 要么整个字段别写、要么写完整,不能是空数组**：BusinessStart / FillForm / CustomFunction / CustomPythonFunction / CrossBorderExpert / SendNotification / WriteFile / End / Condition / LinkfoxHTTP / HTTP / HumanInput(fixed) 由 `save_workflow.py` 代填，整个字段别出现即可。其余节点自己写完整元数据定义，支持变量替换的字段必须标记 `"acceptVariable": true`。写成 `[]` 是明确表态没有字段，不代填、直接报 error。详见 `variable-substitution.md` 与 SKILL.md 的「`inputParams` 交给脚本」。
- **`outputAnchors` 不能是空数组**（StickyNote 除外）：必须完整声明输出锚点对象，`sourceHandle` 靠 `outputAnchors[].id` 绑定到节点句柄；锚点缺 id 会导致所有 edge 被静默丢弃。形状规范见下一节。
- 运行时对象如 `FLOWISE_CREDENTIAL_ID`、Document Store UUID、Vector Store ID、目标 flowId 一律留空，导入后由用户绑定。
- **集合型字段（`inputParams` / `inputAnchors` / `outputAnchors`）以 linkfox-workflow 系统画布导出件为形状基准**；references 未定义的字段不许自行简化或省略。

## Anchor 形状规范

每个锚点必须是完整对象，最少包含以下 4 个字段：

```json
{
  "id": "<nodeId>-output-<anchorName>",
  "name": "<anchorName>",
  "label": "<UI 显示名>",
  "description": "<锚点说明，可为空串>"
}
```

- `id` 必须严格等于 `<nodeId>-output-<anchorName>`，与 edge 的 `sourceHandle` 完全一致；对不上则指向该锚点的 edge 会被丢掉。
- `name` 与各节点分类文件里"输出锚点"一节记录的锚名一致。
- `label` 是 UI 上显示的锚点标签；一般节点用 `data.label` 或锚名首字母大写即可。
- `description` 用节点说明或空串（字段本身不能省略）。

**常规节点单锚点**（AI / Knowledge / Integration / LinkFox 自定义节点等）：

```json
"outputAnchors": [
  {
    "id": "agentAgentflow_0-output-agentAgentflow",
    "name": "agentAgentflow",
    "label": "Agent",
    "description": ""
  }
]
```

**Condition / ConditionAgent 双锚点**（锚名固定为 `0` 和 `1`）：

```json
"outputAnchors": [
  { "id": "conditionAgentflow_0-output-0", "name": "0", "label": "0", "description": "任一 condition 满足" },
  { "id": "conditionAgentflow_0-output-1", "name": "1", "label": "1", "description": "Else" }
]
```

**HumanInput 双锚点**（锚名固定为 `proceed` 和 `reject`）：

```json
"outputAnchors": [
  { "id": "humanInputAgentflow_0-output-proceed", "name": "proceed", "label": "proceed", "description": "" },
  { "id": "humanInputAgentflow_0-output-reject", "name": "reject", "label": "reject", "description": "" }
]
```

**LinkFox 自定义节点**（`BusinessStart` / `CrossBorderExpert` / `DataReader` / `FillForm` / `SendNotification` / `WriteFile`）：`name` 用 `nodes-linkfox-custom.md` 中记录的自定义锚名（`businessStartAgentflow` / `completed` / `data` / `submitted` / `sent` / `written`），`id` 依然是 `<nodeId>-output-<name>`。

**Start**：`name` = `startAgentflow`，`id` = `<nodeId>-output-startAgentflow`。

**Loop / DirectReply / End / StickyNote 无出边**：`outputAnchors` 保持空数组即可（省略该字段更好，由 `save_workflow.py` 补齐）。

## Edge

```json
{
  "source": "<sourceNodeId>",
  "sourceHandle": "<sourceNodeId>-output-<anchorName>",
  "target": "<targetNodeId>",
  "targetHandle": "<targetNodeId>",
  "data": {
    "sourceColor": "<source 色号>",
    "targetColor": "<target 色号>",
    "isHumanInput": false
  },
  "type": "agentFlow",
  "id": "<source>-<sourceHandle>-<target>-<targetHandle>"
}
```

- `targetHandle` 直接等于目标节点 ID，不使用 `-input-*` 后缀。
- 普通节点的 `sourceHandle` 是 `<sourceNodeId>-output-<data.name>`。
- Condition、ConditionAgent 和 HumanInput 的特殊分支锚点见 `nodes-control-flow.md`。
- HumanInput 的出边必须带 `isHumanInput: true` 和 `edgeLabel`；Condition / ConditionAgent 出边带相应的 `edgeLabel`。

## Start（已弃用，禁止生成）

> ⚠️ 开始节点一律使用 `BusinessStart`（详见 `nodes-linkfox-custom.md`）。生成、修改、export 任何 flow 时**禁止**输出 `data.name=startAgentflow` / `data.type=Start` 的节点；`save_workflow.py` 会直接拒绝含原生 Start 的 fragment（exit 65）。
> 以下字段说明仅供读取历史 flowData 时参考，**不作为生成模板**。

- `data.name`: `startAgentflow`；`data.type`: `Start`；`version`: `1.4`；`color`: `#7EE787`；`baseClasses`: `["Start"]`。
- 每个 flow 有且只有一个；`hideInput: true`，无入边。
- 必填 `inputs.startInputType`：`chatInput`（默认）/ `formInput` / `webhookTrigger` / `scheduleInput`。
- `formInput` 补 `formTitle` / `formDescription` / `formInputTypes[]`：每项 `{type: string|number|boolean|options, label, name, addOptions?}`；`name` **必须 camelCase**；`addOptions` 仅在 `type === 'options'` 时出现。
- `webhookTrigger` 补：
  - `webhookMethod`：`GET` / `POST`（默认）/ `PUT` / `PATCH` / `DELETE`。
  - `webhookInputMode`：`text`（默认）/ `payload` / `none`。
  - `webhookResponseMode`：`sync`（默认）/ `async`。
  - 条件字段：`webhookContentType`、`webhookDefaultInput`（`webhookInputMode==='text'` 时）、`webhookEnableAuth`、`webhookSecret` / `webhookSignatureHeader` / `webhookSignatureType`（鉴权开启后）。
- `scheduleInput` 补：
  - `scheduleType`：`visualPicker`（默认）/ `cronExpression`。
  - `visualPicker` 下 `scheduleFrequency`：`hourly` / `daily` / `weekly` / `monthly` / `once`，再按 frequency 填 `scheduleOnMinute` / `scheduleOnTime` / `scheduleOnDayOfWeek` / `scheduleOnDayOfMonth` / `scheduleEndDate`；`scheduleTimezone` 默认 `UTC`。
  - `cronExpression` 下填 `scheduleCronExpression`。
  - `scheduleInputMode`：`text`（默认）/ `form` / `none`；`form` 时补 `scheduleFormInputTypes[]`。
- 可选 `startEphemeralMemory`、`startState[]`（每项 `{key, value}` 初始化 state）、`startPersistState`。**这三项只属于原生 `Start`**，`BusinessStart` 没有，别照抄到 `BusinessStart` 上（见 `output-and-state.md` 第 4.1 节）。
- 输出锚点：`<id>-output-startAgentflow`。

## StickyNote

- `data.name`: `stickyNoteAgentflow`；`data.type`: `StickyNote`；`version`: `1.0`；`color`: `#fee440`；顶层 `type`: `stickyNote`。
- 可选 `inputs.note`（HTML）；没有执行语义、没有 output anchor、不参与 edge。

## State 与变量引用

细节见 `output-and-state.md`（跨节点取值或用到 `$flow.state` 时必读），这里只列硬规则：

- **不能在开始节点集中声明 state key**：开始节点强制是 `BusinessStart`，它没有 `startState` / `startPersistState`。初始 State 是空对象，key 只能由下游节点在运行时创建。
- 支持更新 state 的**只有 9 个节点**：Agent / LLM / Tool / Retriever / CustomFunction / CustomPythonFunction / ExecuteFlow / Loop / CrossBorderExpert，在自己的 `<name>UpdateState[]` 里写 `{key, value}`。其余节点写入行为固定（`DataReader` 自动写 `$flow.state.<outputVariableName>`、`FillForm` 固定写 `state.filledForm`），**不要给它们造 `UpdateState` 字段**。
- `UpdateState[]` 的 `value` 里 `{{ output }}` 指**当前节点**本次执行的结果，不是上游。
- state key 用简单 camelCase，**不要带点号**（`customer.name` 是普通 key，不会变成嵌套对象，而读取 `{{$flow.state.customer.name}}` 按嵌套路径查找，两者对不上）。
- 字符串 inputs 内用 `{{ $flow.state.<key> }}` 引用 state；CustomFunction 内用 `$flow.state.<key>`。
- 跨节点变量必须使用 `{{ <nodeId>.output.<实际字段路径> }}`；不得只写到 `.output`。**输出锚名不是 output 字段**：不存在 `output.data` / `output.sent` / `output.written` / `output.completed` / `output.submitted`。各节点真实字段以 `output-and-state.md` 的表为准。
- 能用 `{{nodeId.output.<路径>}}` 精确表达的依赖就别绕 State。

## 全局限制

- 不自造 `data.type` 或 `data.name`；只用索引列出的 24 个节点（原生 15 + LinkFox 自定义 9）。`save_workflow.py` 会机械校验 `data.name` / `data.type` / 顶层 `type`，未注册的节点直接拒绝落盘。
- BusinessStart 无入边（原生 Start 已弃用，禁止生成）；Loop / DirectReply / End 无出边。
- 不嵌套 Iteration，不嵌套 Loop，也不让 Loop 和 Iteration 互嵌。
- 需要用户可见回复的分支末端使用 DirectReply；详细限制见 `nodes-integration-and-output.md`。
