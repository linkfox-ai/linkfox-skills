# linkfox-workflow Agentflow v2：LinkFox 自定义节点

在原生 15 个节点之外（其中原生 `Start` 已被 `BusinessStart` 取代，禁止生成），linkfox-workflow 系统额外提供 **8 个定制 Agentflow v2 节点**。生成、修改或校验涉及以下能力时必读本文件：

- 亚马逊授权店铺事件 / 业务定时启动 / 手动"点一下就跑" → `BusinessStart`
- 调用跨境专家平台已配置的专家 → `CrossBorderExpert`
- 读取 CSV / Excel / 多维表 / 亚马逊授权店铺订单 → `DataReader`
- 暂停流程、让用户填一组结构化字段（含单文件上传）后再继续 → `FillForm`
- 并行投递邮件 / 飞书 / 钉钉通知 → `SendNotification`
- 将上游结果写入 Linkfox 多维表（写已有表 / 新建表 / **改已有行**）→ `WriteFile`
- 调 Linkfox 工具网关 / 其他 Linkfox 内部服务的 HTTP 接口 → `LinkfoxHTTP`
- 显式标记流程结束 → `End`

所有节点：

- `category`: `"Agent Flows"`
- 顶层 `type`: `"agentFlow"`
- `data.id` = 顶层 `id` = `<data.name>_<数字>`（新建节点用顺序号 `_0` / `_1`；refine 时基线里画布生成的随机数字后缀如 `_415972` 原样保留，详见 `flow-structure.md`）
- **`inputParams` 整个字段别写**：本文件这 8 个节点（`HumanInput` / `CustomPythonFunction` 不在此文件，但同理）的 `inputParams` 由 `save_workflow.py` 按 `data.name` 代填，`acceptVariable` 也已标好。写成 `[]` 不算省略 —— 空数组不代填、直接报 error。下面各节的「核心字段」表说的是 `inputs`（字段**值**），那部分仍要你自己填。细节见 SKILL.md 的「`inputParams` 交给脚本」
- **锚名 ≠ output 字段名**：下面每个节点表格里的"输出锚点"（`data` / `sent` / `written` / `completed` / `submitted`）只用于 edge 的 `sourceHandle`，**不是** `output` 里的字段。跨节点取值一律查 `output-and-state.md` 的字段表——写 `{{ <id>.output.data }}` / `.output.sent` / `.output.written` 这类锚名路径，运行时不报错但模板不会被替换
- 除 `FillForm` 和 `End` 外，凭据都是 `linkfoxAgentApi`；生成时 credential id 一律留 `""`
- **`linkfoxAgentApi` 凭据由后台自动绑定**：上传后服务端会给这些节点自动绑上，用户不需要在页面上手工绑。补配置指引、计划里的「上传后要补什么」、执行前缺项转述里**都不要**出现「绑定 `linkfoxAgentApi` 凭据」这类提示；只点名真正要用户配的东西（店铺、专家、表、机器人地址、模型等）
- **credential 落点固定**：credential 类型名（`linkfoxAgentApi`）写在下面每个节点表格的 `credential` 一行——它落到节点 JSON 的 `data.credential`；credential 实例 id 一律留 `""`，与 `FLOWISE_CREDENTIAL_ID` 用同一套占位规则。不要把 credential 字段插进 `inputs` / `inputParams`，也不要造 `data.inputs.credential`、`data.inputs.linkfoxAgentApi` 这类名字。本表就是权威写法，不必再去别处验证。
- **`data.credential` 的值绝不能是类型名**。表格里 `credential` 一行写的 `linkfoxAgentApi` 是**凭据类型**，说明该节点需要哪种凭据，不是合法的字段值：

  ```json
  "credential": ""                                        // ✅ 生成时：空占位
  "credential": "<credentialId>"                          // ✅ refine 时：fetch 基线里已绑定的实例 id，原样保留
  "credential": "linkfoxAgentApi"                         // ❌ 类型名，不是实例
  ```

  写成类型名时导入不报错、画布看不出异常，要跑到那个节点才失败；`save_workflow.py` 对此按 error 拦截。
- refine 时 `data.credential` 与 `inputs.FLOWISE_CREDENTIAL_ID` 指同一个凭据，**要么都是那个实例 id，要么都空**；只填一处通常是漏改（脚本报 warning）。fetch 回来的基线里带着已绑好的 id（后台自动绑定或用户在界面上选的）是正常的，**不要把它"修正"成空串**——那会清掉已有的绑定。
- 所有 `asyncOptions` 字段（`amazonStore` / `expertId` / `executeFlowSelectedFlow` 等）**必须留空字符串**，导入后由用户在界面上刷新选择。**多维表（`notebookId` / `tableId`）例外**：用智能表格 skill 查出用户的表、问用户选哪张后填真实 id，见 `SKILL.md`「选表」一节

---

## BusinessStart（业务开始）

| 字段 | 值 |
| --- | --- |
| `data.name` | `businessStartAgentflow` |
| `data.type` | `BusinessStart` |
| `version` | `1.8` |
| `color` | `#8B5CF6` |
| `baseClasses` | `["Start"]` |
| `credential` | `linkfoxAgentApi`（`storeAuthorization` 与 `tableRecordTrigger` 两种启动方式都必填） |
| 输出锚点 | `<id>-output-businessStartAgentflow` |

**用途**：面向运营的开始节点，**LinkFox 分支的唯一开始节点**。每个 flow 必须且只能有一个 `BusinessStart`；**禁止使用原生 `Start`**（`save_workflow.py` 会直接拒绝）。

**核心字段（`inputs`）**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `startInputType` | options，卡片式 | 只有四个合法值：`chatInput` = 手动启动（默认，无对话框，聊天面板显示"启动任务"按钮）；`scheduleInput` = 按业务时间；`storeAuthorization` = 店铺授权事件；`tableRecordTrigger` = 多维表格记录触发。**没有** `formInput` / `webhookTrigger`——那两个只在原生 `Start` 上，而原生 Start 已禁止生成 |
| `amazonStore` | asyncOptions | `storeAuthorization` 时必填；值格式 `<sellerId>\|<region>\|<marketplaceIds>`（三段，与 DataReader 的「亚马逊授权店铺」共用同一份下拉；老流程存的两段 `<sellerId>\|<region>` 仍能解析，此时 `marketplaceIds` 为空数组）；生成时留 `""` |
| `storeChangeType` | options，默认 `orderList` | 只有五个合法值：`listing` / `orderList` / `afterSalesOrder` / `fbaInventory` / `removalOrder`（与 DataReader 的 `amazonDataType` 同一套枚举），列表外的值保存会被拒绝 |
| `storeCheckIntervalMinutes` | number，默认 `10` | 必须为正整数 |
| `notebookId` | asyncOptions | `tableRecordTrigger` 时的**第一级**：多维表格（容器，`nbk` 前缀；散表 `__loose__`）；填用户选定的表所在容器 |
| `tableId` | asyncOptions | `tableRecordTrigger` 时的**第二级**：数据表（`tbl` 前缀），必填；填用户选定的数据表 |
| `recordEventType` | options，卡片式，默认 `recordCreated` | `recordCreated` / `recordUpdated` / `recordConditionMet` 三种可用；`recordTimeReached`（到达记录中的时间时）卡片显示但**禁用**，写它保存会被拒绝 |
| `recordWatchFieldNames` | asyncMultiOptions | 仅 `recordUpdated`；可选，空 = 任意字段修改都触发；值是**字段名**数组（不是 `fldXXX`）；生成时留 `""` |
| `recordConditionFieldName` | asyncOptions | 仅 `recordConditionMet`，必填；值是**字段名**；生成时留 `""` |
| `recordConditionOperator` | options，默认 `equal` | `equal` / `notEqual` / `contains` / `notContains` / `isGreater` / `isLess` / `isEmpty` / `notEmpty` |
| `recordConditionValue` | string | 仅 `recordConditionMet`，且算子不是 `isEmpty` / `notEmpty` 时必填（那两个算子在面板上隐藏此项） |
| `recordCheckIntervalMinutes` | number，默认 `10` | `tableRecordTrigger` 时必须为正整数（当前不影响触发时机，见下方"记录触发是推模式"） |
| `schedule*` | 复用原生 `Start` 的 schedule 字段 | 默认视觉配置为每周、`09:00`、周一、`Asia/Shanghai`。`BusinessStart` **没有** `scheduleCronExpression` / `scheduleInputMode` / `scheduleDefaultInput`——排期固定走 `visualPicker`、无 Cron、无默认文本。需要 Cron 或默认输入的场景本节点表达不了 |

**保存会被服务端 400 拒绝的情况**：未选 Credential；`tableId` 不以 `tbl` 开头；`recordEventType` 不在三种可用事件里（`recordTimeReached` 报 "The selected Record Event is not available yet."）；`recordConditionMet` 缺条件字段 / 算子非法 / 该带值的算子没给值；`recordCheckIntervalMinutes` 或 `storeCheckIntervalMinutes` 不是正整数；`storeChangeType` 不在五种之内。**生成阶段把 `tableId` 留 `""` 是对的**，但留占位的记录触发 flow 在 `upload_workflow.py` 阶段可能被服务端 400 顶回来（报 "Data Table is required on the Start node."）。要为记录触发出 flow 时，先跟用户确认这一点：**要么由用户在界面上先绑好表再保存，要么这条流先用手动启动上线、之后在界面上切成记录触发**。

**没有 `startState`（重要）**：`BusinessStart` 的 `startState` / `startEphemeralMemory` / `startPersistState` 三项都不存在。所以：

- **不要**在 `BusinessStart` 的 `inputs` 里写 `startState` —— 写了也不会生效。
- 以 `BusinessStart` 为起点的 flow **初始 Flow State 是空对象**，无法在设计阶段集中声明状态结构；State key 只能由下游节点在运行时创建。
- 原生节点（Agent / LLM / Tool / Retriever / CustomFunction / ExecuteFlow / Loop）的 `Update Flow State → Key` 下拉框会**加载失败**；只有 `CrossBorderExpert` 返回空列表并支持自由输入新 key。
- 运行时写入不受影响。完整后果与应对见 `output-and-state.md` 第 4.1 节 —— 简单说：**能用 `{{nodeId.output.<路径>}}` 精确引用就别绕 Flow State**。

**手动启动的运行时约定**：`input.question` 与 `output.question` 恒为 `""`，下游节点读到的 `<id>.output.question` 恒为空串——依赖用户文本输入的场景本节点表达不了（原生 `Start` 的 `chatInput` / `formInput` 已禁止生成）。

**店铺授权的运行时输出**（非敏感字段，不含 API Key / Credential）：

```json
{
  "storeAuthorization": {
    "sellerId": "<sellerId>",
    "region": "<region>",
    "marketplaceIds": ["<marketplaceId>"],
    "changeType": "fbaInventory",
    "checkIntervalMinutes": 10
  },
  "question": " "
}
```

### 多维表格记录触发（`tableRecordTrigger`）

**面板是三段式**：先两级选表（多维表格 → 数据表），再选记录事件（四张卡片），最后按事件展开条件字段。

- **选表严格二级联动**：第二级只显示所选多维表格下的数据表。散表归在合成容器 `__loose__`（页面名「未归属多维表」）下。
- **切换上一级不会自动刷新下一级**：换了多维表格要点数据表右侧的刷新按钮。生成时这两个值由你先用 `linkfox-smart-table` 的 `listMyTables` / `listSharedTables` 查出候选、问用户选定后填真实 id，**不要留空让用户自己去界面上选**（缺陷 #7130931254）；用户明确说以后再选才留空并带 `--table-later`。
- **字段按名称寻址**：`recordWatchFieldNames` / `recordConditionFieldName` 存的是**字段名**，不是 `fldXXX`。
- `isEmpty` / `notEmpty` 两个算子选中时「条件值」隐藏，运行输出的 `condition` 也不带 `value`。

**记录触发的运行时输出**（凭据不进出参）：

```json
{
  "tableRecordTrigger": {
    "notebookId": "<notebookId>",
    "tableId": "<tableId>",
    "eventType": "recordConditionMet",
    "checkIntervalMinutes": 10,
    "condition": { "fieldName": "<字段名>", "operator": "equal", "value": "<String>" }
  },
  "question": " ",

  "recordEvent": {
    "eventId": "<eventId>",
    "eventType": "record.updated",
    "tableId": "<tableId>",
    "notebookId": "<notebookId>",
    "recordId": "<recordId>",
    "occurredAt": "<Date>",
    "triggeredBy": "<userId>",
    "changedFieldIds": ["<fldXXX>"],
    "changedFieldNames": ["<字段名>"],
    "record": { "<fldXXX>": "<String>" },
    "recordByName": { "<字段名>": "<String>" }
  },
  "rows": [{ "<字段名>": "<String>" }],
  "recordRows": {
    "rows": [{ "<字段名>": "<String>" }],
    "recordId": "<recordId>",
    "tableId": "<tableId>",
    "keyedBy": "recordByName"
  }
}
```

后三个 key（`recordEvent` / `rows` / `recordRows`）**只在真的收到变更载荷时出现**；手动点「启动任务」跑同一条流时整个不存在，不是空对象。前两个（`tableRecordTrigger` / `question`）恒在。

`watchFieldNames`（`string[]`）只在 `eventType = recordUpdated` 时出现；`condition` 只在 `recordConditionMet` 时出现。**这份输出是"这条流订阅了什么"的静态回显，不是"这次改了哪一行"**——本次变更的数据在另外三个 output 字段里，见下。

### 记录触发时怎么取"这次变的那一行"

`BusinessStart` 会把变更上下文原样带进自己的 output。一律用节点引用取，**不要用 `$webhook`**：

```text
{{businessStartAgentflow_0.output.recordEvent.eventType}}          record.created / record.updated
{{businessStartAgentflow_0.output.recordEvent.recordId}}
{{businessStartAgentflow_0.output.recordEvent.tableId}}  ….notebookId
{{businessStartAgentflow_0.output.recordEvent.occurredAt}}          变更**发生**时间，不是投递时间
{{businessStartAgentflow_0.output.recordEvent.triggeredBy}}         触发变更的用户 id
{{businessStartAgentflow_0.output.recordEvent.eventId}}             幂等键
{{businessStartAgentflow_0.output.recordEvent.changedFieldIds}}     ["<fldXXX>", ...]
{{businessStartAgentflow_0.output.recordEvent.changedFieldNames}}   ["<字段名>", ...]
{{businessStartAgentflow_0.output.recordEvent.recordByName.<字段名>}}  整行里某一格，按字段名取
{{businessStartAgentflow_0.output.recordEvent.record.<fldXXX>}}       同一格，按字段 id 取
```

**不用 `$webhook` 的原因**：它不落任何节点输出，引用取错时执行记录里无从对照"这次到底收到了什么"；且与原生 `webhookTrigger` 的 `$webhook.body` / `.headers` / `.query` 是两套毫不相干的载荷，混写必出错。

两个写法约束，**错了不报错，只是原样留下花括号**：

- **`.output.` 是字面量，不能省**。`{{businessStartAgentflow_0.recordEvent.record}}` 取不到；裸写 `{{businessStartAgentflow_0}}` 也取不到。
- **前缀是 node id，不是画布上显示的节点名字**，也不带 `$` 前缀。

三个要点，写模板前必须知道：

- **`record` 的 key 是 `fldXXX`**，按名字取一律用 `recordByName`；`recordByName` 依赖事件携带的字段字典，**没带时这个键整个不存在**，所以关键路径上给它留个兜底（例如同时把 `recordId` 传给下游节点回查那一行）。
- **只有变更后的值，没有旧值**：表达不了"从 A 变成 B 时才怎样"。
- 手动点「启动任务」跑同一条流时**这三个 key 整个不出现**（节点不造空对象），模板保留字面量。所以一条流既支持手动启动又支持自动触发是可行的，但**不要假设它一定有值**。

### 记录触发 → 直接接 WriteFile（不要再塞 CustomFunction 搬数据）

`recordEvent.record` 的 key 是字段 id，而写入侧只认**字段名**，传 `fldXXX` 会被当成不存在的字段回 404。所以 `BusinessStart` 另外吐了两个 key，专为写入侧准备：

| 字段 | 内容 |
| --- | --- |
| `output.rows` | 同一行翻成 **name-keyed** 的数组，形状就是 `WriteFile` 的入参约定，可**直接连线** |
| `output.recordRows` | `{rows, recordId?, tableId, keyedBy}`，另可带 `droppedComputedFields` / `warnings`；`keyedBy` 记录这份行是怎么翻出来的（`recordByName` / `fieldsMeta` / `listFields`），便于在执行记录里回溯 |

- **写到另一张表**：`BusinessStart` → `WriteFile`（`writeDestination=linkfoxTable`）直连即可，`WriteFile` 自己读上一步的 `rows`，**不需要**在中间放 `CustomFunction`，也不需要在 `WriteFile` 里引用任何变量。
- **回写触发的那一行**：`BusinessStart` → `WriteFile`（`writeDestination=updateLinkfoxTable`），`updateRecordId` **留空**即可——节点会从上一步结果里取 `recordRows.recordId`。
- 标了 `isComputed` 的列（公式 / 汇总 / 自动编号）会被自动摘掉，被摘的列名列在 `recordRows.droppedComputedFields`。
- 翻不动时 `rows` 是**空数组而不是报错**（手动启动就是这种情况），此时 `WriteFile` 会报「没有产出任何记录」。

### ⚠️ 画布上配的记录触发不会跑

记录触发只有在 **linkfox-workflow 系统界面上保存过一次**才会生效。后果：

- 只在画布上配、或只经本 skill 上传的记录触发配置**不会生效**，表里来了变更事件也**静默不跑**。
- 事后在画布上改配置（换表、换事件）**也不会更新**已生效的触发，仍按老配置跑；需要在系统界面上重新保存一次。

所以生成含 `tableRecordTrigger` 的 flow 时，**必须在补配置指引里明确告诉用户**：这条流要在 linkfox-workflow 系统界面上保存一次，触发才会生效；只在画布上配等于没配。

**记录触发是推模式，不是轮询**：表里记录一变更就推送触发，并按所选事件 / 监听字段 / 条件过滤。`recordCheckIntervalMinutes` 当前**不影响触发时机**，但仍要是正整数才能过保存校验。

---

## CrossBorderExpert（跨境专家）

| 字段 | 值 |
| --- | --- |
| `data.name` | `crossBorderExpertAgentflow` |
| `data.type` | `CrossBorderExpert` |
| `version` | `1.1` |
| `color` | `#2563EB` |
| `baseClasses` | `["CrossBorderExpert"]` |
| `credential` | `linkfoxAgentApi`（必填） |
| 输出锚点 | `<id>-output-completed`（`edgeLabel: "Completed"`） |

**核心字段**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `expertId` | asyncOptions | 从专家平台拉取列表；生成时留 `""` |
| `taskInstruction` | string（`acceptVariable: true`，rows 6）| 任务指令；支持 `{{变量}}` 和 `{{$flow.state.*}}` |
| `timeoutMs` | number，默认 `120000` | 任务创建 + 轮询总超时 |
| `pollIntervalMs` | number，默认 `2000` | 单次轮询间隔 |
| `crossBorderExpertUpdateState[]` | array，可选 | 每项 `{key, value}`，把专家结果写进 `$flow.state.<key>` |

**运行时输出**（字段表见 `output-and-state.md`）：`content` / `expertId` / `status` / `messageId?` / `stopReason?` / `expertResult`。结构化结果位于 `{{ <id>.output.expertResult }}`；错误时 `<id>.output.status = "error"`、`expertResult` 通常是 `{error, statusCode?, messageId?, stopReason?}`。下游要复用请直接读 `output.expertResult`，或用 `crossBorderExpertUpdateState` 写入 state（`value` 里的 `{{ output }}` 指本节点的 `expertResult`）。**没有** `output.completed`——`completed` 只是锚名。

### `taskInstruction` 有 10000 字符硬上限，禁止内联整体响应

专家平台对 prompt 有硬限制（早期 1000，现为 10000），超了直接返回（下面是 1000 时代的报错原文）：

```json
{"status": "error", "expertResult": {"error": "Task creation failed (400): prompt 必须为字符[0,1000]"}}
```

`save_workflow.py` 按 9000 字符卡字面量（留余量给变量展开）。

**变量替换后**的长度才是平台看到的长度。所以致命错法是把整体响应引用塞进 `taskInstruction`——一个搜索响应就有几十条商品、几十 KB，必然撞穿：

```text
{{ linkfoxHttpAgentflow_0.output.http.data }}          ❌ 整个响应体
{{ linkfoxHttpAgentflow_0.output.http }}               ❌ 整个 http 对象
{{ crossBorderExpertAgentflow_0.output.expertResult }} ❌ 上游专家的完整结果
{{ dataReaderAgentflow_0.output.tableData }}           ❌ 整张表
{{ <任何节点>.output.content }}                         ❌ 整个结果的 JSON 字符串
```

两种正解：

```text
# 1) 精确到叶子字段（引用路径继续往下取，体积可控）
分析 ASIN {{ linkfoxHttpAgentflow_0.output.http.data.products[0].asin }} 的竞品情况

# 2) 数据量大时先过一个 CustomFunction 精简，再引用它的 content
#    CustomFunction 输出 {"asins":"<ASIN>,<ASIN>,...","total":<Number>}
聚合去重 ASIN 池并标注相关性：{{ customFunctionAgentflow_0.output.content }}
```

**反面案例**：为了压字符数把变量引用**整个删掉**换成纯文字描述——

```text
基于Amazon搜索结果和Sif ASIN关键词数据，执行关键词本地化处理，聚合去重ASIN池…   ❌
```

字符数降下来了，但专家节点什么真实数据都拿不到。**"减字符"和"保留数据引用"必须同时满足**，精简的是数据体积，不是引用本身。

`save_workflow.py` 会机械拦这两条（整体响应引用 → error；字面量 > 9000 → error），但**它只看得见字面量**：叶子字段引用展开后到底多大，只有真跑一次才知道。指令文本本身建议压到 7000 字符以内，把冗长的评分规则挪到专家侧配置里。

`crossBorderExpertUpdateState` 的 key 是 `BusinessStart` 起点的 flow 里**唯一支持自由输入新 key** 的 State 入口；其余带 `UpdateState` 的原生节点在 `BusinessStart` 起点的 flow 里下拉框会加载失败。详见 `output-and-state.md` 第 4 节。

**与原生 Agent / LLM / ConditionAgent 的选择关系（见 `node-catalog.md` 选择规则）**：涉及模型 / AI 推理的场景默认用本节点，不要默认生成原生 `Agent` / `LLM` / `ConditionAgent`。`CrossBorderExpert` 没有 `agentTools`（Tool 调用）、`agentKnowledgeDocumentStores` / `agentKnowledgeVSEmbeddings`（RAG 知识库检索）、`agentStructuredOutput`（结构化输出）——只有 `expertId` / `taskInstruction` / `timeoutMs` / `pollIntervalMs`。需求确实依赖这些能力，或需要节点内直接由 LLM 做动态自然语言分支判断（对应 `ConditionAgent`）时，才允许原生节点兜底，并在方案里点出兜底原因。

---

## DataReader（数据读取）

| 字段 | 值 |
| --- | --- |
| `data.name` | `dataReaderAgentflow` |
| `data.type` | `DataReader` |
| `version` | `1.0` |
| `color` | `#0F766E` |
| `baseClasses` | `["DataReader"]` |
| `credential` | `linkfoxAgentApi`（仅 `linkfoxTable` / `amazonStore` 时必填） |
| 输出锚点 | `<id>-output-data`（`edgeLabel: "Data"`） |

**核心字段**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `sourceType` | options | `csv` / `excel` / `linkfoxTable` / `amazonStore` |
| `csvFile` / `delimiter` / `encoding` | 文件与解析选项（`sourceType=csv`） | `delimiter`: `auto` / `comma` / `semicolon` / `tab` / `pipe`；`encoding`: `utf8` / `utf8Bom` |
| `excelFile` / `sheetName` / `headerRow` | 文件与解析选项（`sourceType=excel`） | `sheetName` 空则读第一个 sheet；`headerRow` 默认 `1` |
| `notebookId` | asyncOptions | `sourceType=linkfoxTable` 时的**第一级**：多维表格（容器，`nbk` 前缀；散表 `__loose__`）；填用户选定的表所在容器 |
| `tableId` | asyncOptions | `sourceType=linkfoxTable` 时的**第二级**：数据表（`tbl` 前缀），必填；填用户选定的数据表。读取只认它，填 `nbk` 会被拒 |
| `amazonStore` | asyncOptions | `sourceType=amazonStore`；值 `<sellerId>\|<region>\|<marketplaceIds>`（三段；老流程的两段仍能解析，`marketplaceIds` 为空数组）。与 BusinessStart 的「授权店铺」共用同一份下拉 |
| `amazonDataType` | options，默认 `orderList` | `listing` / `orderList` / `afterSalesOrder` / `fbaInventory` / `removalOrder`（与 BusinessStart 的 `storeChangeType` 同一套枚举）；列表外的值会被拒 |
| `amazonCheckIntervalMinutes` | number，默认 `10` | 亚马逊读取窗口（读取最近 N 分钟的数据） |
| `maxRows` | number，默认 `2000` | 硬上限 2000，不可超过 |
| `outputVariableName` | string，默认 `tableData` | **同时**是 output 字段名和 State key：结果写进 `{{ <id>.output.<名称> }}` 与 `{{$flow.state.<名称>}}`。禁止取 `content` / `status` / `rowCount` / `truncated`（会覆盖固定字段）；推荐 camelCase |

**选表是两级的，不是一级**：先选「多维表格」再选它下面的「数据表」，切换上一级后要点数据表右侧的刷新按钮。两个值都填用户选定的真实 id（见 `SKILL.md`「选表」）。`WriteFile` 与 `BusinessStart` 记录触发的选表行为与此一致。

**运行时输出**（字段表见 `output-and-state.md`）：固定字段 `content`（整个表格结果的 JSON 字符串）/ `status`（成功恒为 `ok`）/ `rowCount` / `truncated`，外加动态字段 `<outputVariableName>`。**没有** `output.data`——`data` 只是锚名，写 `{{ <id>.output.data }}` 模板不会被替换。

`outputVariableName` 用默认值时，表格对象在 `{{ <id>.output.tableData }}`；`csv` / `excel` / `linkfoxTable` 三种数据源的形状为

```json
{
  "columns": [{ "key": "<String>", "label": "<String>", "index": 0, "type": "string" }],
  "rows": [{ "<字段名>": "<String>" }],
  "pageInfo": { "limit": 2000, "returned": <Number>, "total": <Number>, "hasMore": false, "truncated": false }
}
```

`amazonStore` 是例外：**没有 `columns` / `pageInfo`**，形状随 `amazonDataType` 变（`orderList` → `{orders:[]}`、`listing` → `{listings:[]}`、`fbaInventory` → `{inventorySummaries:[]}`、`afterSalesOrder` / `removalOrder` → `{reportType, reportId, rows:[]}`）。完整表见 `output-and-state.md` 第 2.3 节。

CSV / Excel 上传有 5MB 硬上限，超出直接报错。

`WriteFile` 的"新建多维表"分支会自动识别上一步结果里的 `rows`，无需再手工映射列结构。

---

## FillForm（人工输入资料）

| 字段 | 值 |
| --- | --- |
| `data.name` | `fillFormAgentflow` |
| `data.type` | `FillForm` |
| `version` | `1.2` |
| `color` | `#F59E0B` |
| `baseClasses` | `["FillForm"]` |
| `credential` | `linkfoxAgentApi`（**仅当 `formFields` 里有 `media` 字段时需要**；纯文本表单不需要） |
| 输出锚点 | `<id>-output-submitted`（`edgeLabel: "Submitted"`） |

**执行到 `FillForm` 会暂停流程等用户填表**：节点落一条 `status: "STOPPED"` 的执行记录，前端弹出配置好的结构化表单；用户提交后 flow 从这个节点**原地恢复**，把用户提交的值写进 `output.filledForm` 与 `state.filledForm`。

> `FillForm` 是真正的人工输入检查点，会挡住流程。区别于 `HumanInput`：`FillForm` 收**结构化字段值**，`HumanInput` 只收**通过 / 驳回**。
>
> 含 `FillForm` 的 flow **试跑时不会一次跑完**。`run_workflow.py` 会在这个节点停住并返回 `STOPPED`，那**不是失败**，也不是超时——要有人在界面上填完表单提交才会继续。别把 `STOPPED` 当错误重跑。

**运行时输出**：只有 `content`（`filledForm` 的 JSON 字符串）和 `filledForm`（结构化对象）。下游取 `{{ <id>.output.filledForm.<name> }}` 或 `{{$flow.state.filledForm.<name> }}`；**没有** `output.submitted`——`submitted` 只是锚名。`FillForm` 固定写 `state.filledForm`，不需要也没有 `UpdateState` 字段。

**核心字段**：

- `formFields[]`：`{type, label, name, required?, addOptions?}`
  - `type`: `text` / `textarea` / `number` / `boolean` / `date` / `radio` / `checkbox` / `media`
  - `label`：表单里显示的名称
  - `name`：**驼峰命名**，下游通过 `{{$flow.state.filledForm.<name>}}` 引用
  - `required`：布尔，可选，默认 `false`
  - `addOptions[]`：仅 `radio` / `checkbox` 时使用，每项 `{option}`
- `submitButtonText`：字符串，可选，默认 `"Submit"`；同时是暂停时那个按钮的文案

> **没有 `formTitle` / `description` / `defaultValue` 三个字段**，不要写（面板不认、下游也读不到）。用户未填时的回落值固定：`text` / `textarea` / `date` / `radio` / `media` → `""`，`number` → `null`，`boolean` → `false`，`checkbox` → `[]`。**所以 `FillForm` 不能用来"声明一组带默认值的常量"**，值只能由用户在表单里填。需要流程级常量请在下游节点的字段里直接写字面量。

**`media`（多媒体）字段**：一个 `media` 字段只收**一个**文件。用户选完文件后立即上传，字段值是上传成功后的公开 HTTPS URL 字符串。用了它该节点就需要 `linkfoxAgentApi` 凭据（上传文件要用），生成时 `data.credential` 仍留 `""`，由后台自动绑定，补配置指引里不用提。

---

## SendNotification（发送通知）

| 字段 | 值 |
| --- | --- |
| `data.name` | `sendNotificationAgentflow` |
| `data.type` | `SendNotification` |
| `version` | `1.1` |
| `color` | `#0EA5E9` |
| `baseClasses` | `["SendNotification"]` |
| `credential` | `linkfoxAgentApi`（仅 `channels` 含 `email` 时必填） |
| 输出锚点 | `<id>-output-sent`（`edgeLabel: "Sent"`） |

**核心字段**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `channels` | multiOptions，默认 `["email"]` | `email` / `feishu` / `dingtalk`；**并行发送、单渠道失败不影响其它** |
| `recipients` | string（rows 3，`acceptVariable: true`） | `email` 渠道使用，按换行 / 逗号 / 空格分隔 |
| `messageContent` | string（rows 6，`acceptVariable: true`） | 所有渠道共用正文，支持 `{{变量}}` 和 `{{$flow.state.*}}` |
| `emailSubject` / `emailCc` | string，`acceptVariable: true` | 仅 email |
| `feishuWebhook` / `feishuSignSecret` | password | 仅 feishu；面板直填 webhook URL 与"加签"密钥 |
| `dingtalkWebhook` / `dingtalkSignSecret` | password | 仅 dingtalk |

**机器人地址和加签密钥是用户的配置,不是 agent 的**：新建流程一律留 `""`，refine 时从 fetch 基线原样带回。不要把同会话里别的流程配过的地址抄进来（缺陷 #7130761097：B 的通知发进了 A 的群）。`save_workflow.py` 会拦，用户本轮亲手给了地址时才带 `--secrets-from-user`。
| `timeoutMs` | number，默认 `15000` | 单渠道超时 |

**运行时输出**（字段表见 `output-and-state.md`）：`content`（完整通知结果的 JSON 字符串）/ `status`（至少一个渠道成功为 `ok`，全失败为 `error`）/ `successChannels[]` / `failedChannels[]`。**没有** `output.sent`（`sent` 只是锚名），也**没有** `output.details`——各渠道明细只在 `output.content` 的 JSON 字符串里。取值走 `{{ <id>.output.status }}` / `.successChannels` / `.failedChannels`。本节点不写入 `$flow.state`。

---

## WriteFile（文件 / 表格写入）

| 字段 | 值 |
| --- | --- |
| `data.name` | `writeFileAgentflow` |
| `data.type` | `WriteFile` |
| `version` | `1.4` |
| `color` | `#7C3AED` |
| `baseClasses` | `["WriteFile"]` |
| `credential` | `linkfoxAgentApi`（三种写入目标都必填） |
| 输出锚点 | `<id>-output-written`（`edgeLabel: "Written"`） |

**核心字段**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `writeDestination` | options | 三个合法值：`linkfoxTable` = 往已有数据表**新增行**（默认）；`newLinkfoxTable` = 新建多维表；`updateLinkfoxTable` = **更新已有记录**（只改已存在的行、不新增）。**没有 `productLibrary`**，传它运行时报 `unsupported write destination` |
| `notebookId` | asyncOptions | `linkfoxTable` / `updateLinkfoxTable` 时的**第一级**：多维表格（容器，`nbk`）；只用于收窄第二级并把归属带给下游（`target.notebookId`），写入不用它；填用户选定的表所在容器 |
| `tableId` | asyncOptions | `linkfoxTable` / `updateLinkfoxTable` 时的**第二级**：数据表，必填；填用户选定的数据表。运行时要求以 `tbl` 开头，写入只认它 |
| `updateRecordId` | string（`acceptVariable: true`），可选 | 仅 `updateLinkfoxTable`：**要改哪一行**（`rec` 开头）。**留空时节点自己从上一步结果里取**（依次看 `recordRows.recordId` → `recordEvent.recordId` → 顶层 `recordId`）——记录变更触发的流程**直接留空即可**。手填时可用变量引用；填了但解析不出 `rec` 前缀会直接报错 |
| `newTableNotebookId` | asyncOptions，默认 `__new__` | 仅 `newLinkfoxTable`：**新数据表建在哪**。`__new__` = 连容器一起新建（重复执行在短时间内是幂等的）；选一个真实 `nbk` = 只往该容器里加一张数据表（**不幂等**，同名反复加会得到两张同名表）。`__loose__` 不在这个下拉里，写它运行时报错。生成时可以省略（默认即 `__new__`），要让用户自己选容器则留 `""` 并在指引里点名 |
| `newTableName` | string | `newLinkfoxTable` 时必填。**数据表名不去重**，可能被追加「 2」后缀，实际表名以 `output.target.tableName` 为准 |
| `timeoutMs` | number，默认 `180000` | 单次多维表调用超时 |

**写入数据来源**：节点自动读取**直接上一步**的 `output`，认 `{rows: [...]}` / `{records: [...]}` 这两种包装（`DataReader` 的结果、`BusinessStart` 记录触发的 `rows` 都是这个形状，所以都能直连）；找不到有效结果时阻止执行。**每条记录的 key 必须是字段名**，传 `fldXXX` 会被当成不存在的字段回 404。

**`updateLinkfoxTable` 一次只改一行**：上一步给了多条记录时直接报错（不会静默只改第一条）。要逐条更新请在上一步把结果收成一条，或用 `Iteration` 节点。

**写入前会自动摘掉计算列**：`linkfoxTable` / `updateLinkfoxTable` 写入前会把 `isComputed` 的列（公式 / 汇总 / 自动编号 / 创建人）滤掉——这类值由多维表自己算。被摘的列名出现在 `output.target.droppedComputedFields`。滤完一个字段都不剩时报错。

**新建表时图片列会被推成 `image` 类型**：列名含 `图片` / `参考图` / `image`（子串、大小写不敏感）**且**该列首个非空值是单个 http(s) 链接时，字段类型推 `image` 而不是文本。两个条件必须同时成立。

**运行时输出**（字段表见 `output-and-state.md`）：`content`（完整写入结果的 JSON 字符串）/ `status`（成功恒为 `ok`，失败抛错不产生成功 output）/ `target` / `recordCount` / `result`（写入返回的原始结果）。**没有** `output.written`——`written` 只是锚名。取值走 `{{ <id>.output.recordCount }}` / `.target` / `.result`。

`target` 按写入目标不同：

| `writeDestination` | `target` 内容 |
| --- | --- |
| `linkfoxTable` | `{type, notebookId, tableId}`（+ `droppedComputedFields?`）；散表 / 存量流程的 `notebookId` 为 `null` |
| `updateLinkfoxTable` | 同上再加 `recordId`（实际改的那一行） |
| `newLinkfoxTable` | `{type, notebookId, notebookName, addedToExistingNotebook, tableId, tableName, createdTime, idempotentHit, fields}`；往已有容器加表时 `notebookName` 为 `null`、`idempotentHit` 恒为 `false` |

本节点**没有** `UpdateState` 字段，也不写 `$flow.state`；需要把写入结果放进共享状态，只能在下游某个支持 `UpdateState` 的节点里引用 `{{ <id>.output.result }}`。

---

## LinkfoxHTTP（Linkfox HTTP 工具）

| 字段 | 值 |
| --- | --- |
| `data.name` | `linkfoxHttpAgentflow` |
| `data.type` | `LinkfoxHTTP` |
| `version` | `1.0` |
| `color` | `#0F766E` |
| `baseClasses` | `["LinkfoxHTTP"]` |
| `credential` | `linkfoxAgentApi`（**必填**） |
| 输出锚点 | `<id>-output-linkfoxHttpAgentflow` |

**用途**：调用 Linkfox 工具网关（`https://tool-gateway.linkfox.com`）或其他 Linkfox 内部服务。相比原生 `HTTP`：

- 运行时自动把凭据里的 `apiKey` 注入 `Authorization` 请求头，**不加 `Bearer` 前缀**
- 只填**相对路径**，不写完整 URL

**选择规则**：目标是 Linkfox 工具网关或内部服务 → 用本节点；目标是第三方外部 API（需要自定义鉴权头、或需要 `Bearer` 前缀）→ 用原生 `HTTP`。**不要**用原生 `HTTP` 手写 `https://tool-gateway.linkfox.com/...` 再自己拼认证头。

**核心字段（`inputs`）**：

| 字段 | 类型 | 默认 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `method` | options | `POST` | 是 | `GET` / `POST` / `PUT` / `DELETE` / `PATCH`（无 `HEAD`/`OPTIONS`） |
| `path` | string（`acceptVariable: true`） | — | 是 | **相对路径**，例 `/amazonAds/authorizeUrl`；留空运行时报错 |
| `headers` | array（`acceptVariable: true`） | `[]` | 否 | 每项 `{key, value}`；填 `Authorization` 会覆盖默认注入的 API Key |
| `queryParams` | array（`acceptVariable: true`） | `[]` | 否 | 每项 `{key, value}` |
| `bodyType` | options | `json` | 否 | `json` / `raw` / `formData` / `xWwwFormUrlencoded` |
| `body` | string 或 array | — | 否 | 与原生 HTTP 同构：`json`/`raw` 用字符串（rows 6），`formData`/`xWwwFormUrlencoded` 用 `{key, value}` 数组 |
| `responseType` | options | `json` | 否 | `json` / `text` / `arraybuffer` / `base64` |
| `timeout` | number | `60000` | 否 | 超时（毫秒） |

**运行时输出**（与原生 HTTP 同构）：

```json
{
  "http": {
    "data": { "<字段名>": "<String>" },
    "status": 200,
    "statusText": "OK",
    "headers": { "content-type": "application/json" }
  }
}
```

下游取值走 `{{ <id>.output.http.data }}`（或 `.status` / `.statusText` / `.headers`），禁止裸 `.output`。请求失败时节点抛错。

**常用网关路径**：

| 用途 | `method` | `path` | `body` |
| --- | --- | --- | --- |
| 生成亚马逊广告授权链接 | `POST` | `/amazonAds/authorizeUrl` | `{"region":"<region>","accountName":"<String>"}` |
| 查询已授权店铺列表 | `POST` | `/spApi/authorizedStores` | `{}` |
| 调 SP-API developerProxy | `POST` | `/spApi/developerProxy` | `{"sellerId":"<sellerId>","region":"<region>","path":"<String>","method":"GET","queryString":"<String>"}` |

**如何确定 `path` / `body` / `headers` / `queryParams`（业务接口维度，不是节点 schema 维度）**：

> ⚠️ **每个 `LinkfoxHTTP` 节点都要单独走这个流程，没有例外**。用户提供的规格文档只给了 skill 名或 `endpoint_path`（形如 `linkfox-amazon-search` / `/amazon/search`）、没给完整请求体字段，**也算"没给完整入参"**——不能因为拿到了 path 就跳过 body 这一步。一个 flow 里有多少个 `LinkfoxHTTP` 节点就要查多少次（每个节点都要单独查出自己那个端点、各自填 `body`）。**`body` 落成占位 `"{}"` 就落盘上传，是需要修的错误，不是"以后再补"的遗留项**。

用户点名了某个具体业务接口，或规格文档里给出了 skill 名 / endpoint_path，但没有贴完整的 method / 请求体字段时，用 `scripts/query_tools_matrix.py` 查真实接口文档，不要凭猜测编。**只用这个脚本**，不要用 `curl` / `WebFetch` 自己下载。文档在会话内缓存，重复查询不重复下载。

1. **找工具 key**（只列已上线的工具）：

   ```bash
   python scripts/query_tools_matrix.py catalog --keyword <平台或关键词>   # 可重复，全部命中才算
   python scripts/query_tools_matrix.py catalog --slug <skill 名>          # 规格给了 skill 名时用，更准
   ```

   每行 `key | 标题 | 平台 | 类型 | 状态 | 关联 skill`。没有匹配时退出码 3。

2. **看该工具的端点清单**，定位目标端点：

   ```bash
   python scripts/query_tools_matrix.py endpoints --key <key>
   ```

   每行 `#编号 方法 路径 [| 端点标识=<标识>] [| 非网关:<host>] [| 标题] | 关联 skill`。按标题和关联 skill 定位。

3. **取目标端点的完整文档**：

   ```bash
   python scripts/query_tools_matrix.py endpoint --key <key> --index <编号>
   ```

   - **用上一步清单里的编号取**，最准确。也可以用 `--path <路径或端点标识>`，但转发类接口（多个端点共用 `/spApi/developerProxy` 这类路径）常有重名，匹配到多个时退出码 3 并列出候选编号。
   - 输出那一节包含请求地址、请求方式、请求参数表、响应结构、调用示例，**填 `path` / `method` / `body` 只需要这一节**。
   - 多个节点要查时，各自的 `endpoint` 命令可在同一轮里并发发出。
   - 标了 `非网关:<host>` 的端点不走 Linkfox 网关，不能用 LinkfoxHTTP。

4. 把文档请求地址里**去掉 `https://tool-gateway.linkfox.com` 前缀后的相对路径**填进 LinkfoxHTTP 的 `path`；`method` 按文档；请求参数表里的字段按 `bodyType=json` 组装成 `body` 字符串。文档里的 `Authorization: <api_key>` 头**不需要**在 `headers` 里手填——节点会自动注入（不加 `Bearer`）；只有文档要求别的鉴权头时才在 `headers` 里显式覆盖。
5. `developerProxy` 类接口（如 `/amazonAds/developerProxy`、`/spApi/developerProxy`）本身只是一层转发：LinkfoxHTTP 的 `path` 填这个转发入口本身，文档"请求参数表"里列出的内层 `path`（如 `sp/campaigns/list`）、`method`、`body`、`contentType` 等字段要按文档拼进 LinkfoxHTTP 的 `body` JSON 字符串里，**不要**把内层的 `path` 和 LinkfoxHTTP 节点自己的 `path` 字段搞混。
6. 只有 `catalog` 查不到已上线的匹配工具，或用户需求本身模糊到无法定位具体接口时，才把 `path` 留空、在补配置指引里让用户自己填——不要凭空编路径或参数。

### `body` 的必填参数必须真的接上游数据

查完文档只是拿到了**字段名**。字段名组好了、值全是空串，运行时照样 400：

```json
{"http": {"data": {"errcode": 400, "errmsg": "keyword 为必填参数"}, "status": 400}}
```

```text
"body": "{}"                              ❌ 占位，等于没查
"body": "{\"keyword\": \"\"}"             ❌ 字段名有了，值一个都没传 —— 报错形态同上
```

必填参数的取值只有两种来源，按参数语义选：

```text
# 1) 需要"用户输入的关键词"一类的流程级常量 → 取 FillForm 声明的字段
"body": "{\"keyword\": \"{{fillFormAgentflow_0.output.filledForm.keyword}}\"}"

# 2) 需要"某个具体商品的数据"→ 取上游搜索结果里的叶子字段
"body": "{\"asin\": \"{{linkfoxHttpAgentflow_0.output.http.data.products[0].asin}}\"}"
"body": "{\"imageUrl\": \"{{linkfoxHttpAgentflow_0.output.http.data.products[0].imageUrl}}\"}"
```

注意变量要**写在 JSON 字符串的引号里面**（`"keyword": "{{...}}"`），不是裸放。

**纯常量 body 是合法的**，不必为了"看起来接了上游"硬塞变量——`/amazonAds/authorizeUrl` 的 `{"region":"<region>"}` 就直接来自上面的常用路径表。

`save_workflow.py` 的机械拦截（`LinkfoxHTTP` 且 `path` 非空、`method` 不是 GET/DELETE 时）：

| 情况 | 结果 |
| --- | --- |
| `body` 是 `{}` / `""` / `null` / 空数组 | **error**，拒绝落盘 |
| `body` 解析后是空对象 | **error** |
| 所有参数值都为空 | **error** |
| 部分参数值为空 | warning（可能是可选参数） |
| `0` / `false` 作为参数值 | 不报（页码、开关是有意义的取值） |
| `path` 留空的占位节点 | 不报（还没定位到接口） |

**逃生门**：接口文档确实没有请求参数时（`/spApi/authorizedStores` 这类），在该节点的 `data.description` 里写上 `接口文档无请求参数` 即可放行。这句话要对着文档确认后才写——**不是**用来绕过校验的开关。

这一步查的是**业务接口的 path / body / headers 内容**，不影响节点本身的 schema：LinkfoxHTTP 的 `data.name` / `data.type` / `version` / `color` / `credential` 类型仍然只能按本文件表格填，不能从工具文档里反推。

### 异步任务接口：必须自己搭轮询循环

有一类接口**不会在一次调用里返回结果**：创建接口只回一个 `taskId`，结果要靠另一个查询接口反复问。AIGC 全家桶（`tools/linkfox_aigc.md`）都是这个形态：

| 能力 | 创建（只回 `taskId`） | 查询 | 对应 skill |
| --- | --- | --- | --- |
| AI 生图 | `POST /aigc/imageGenAsync` | `POST /aigc/taskQuery` | `linkfox-aigc-imagegen` |
| AI 生文 | `POST /aigc/textGenAsync` | `POST /aigc/textTaskQuery` | `linkfox-aigc-textgen` |
| AI 生视频 | `POST /aigc/videoGenAsync` | `POST /aigc/taskQuery` | `linkfox-aigc-videogen` |
| 多参考图生视频 | `POST /aigc/multiImageVideoGenAsync` | `POST /aigc/taskQuery` | `linkfox-aigc-videogen-multi` |

> 生图和两种生视频**共用** `/aigc/taskQuery`；只有生文用 `/aigc/textTaskQuery`。别混。

查询响应的关键字段（两个查询接口都一样的部分）：

| 字段 | 说明 |
| --- | --- |
| `status` | `PROCESSING` / `SUCCESS` / `FAILED` |
| `resultList[].url` | 图片或视频 URL（**仅 `taskQuery`，且仅 `SUCCESS` 时有值**） |
| `content` | 生成的文本（**仅 `textTaskQuery`，且仅 `SUCCESS` 时有值**） |
| `errorMsg` | 错误信息（仅 `FAILED` 时有值） |

**只放一个创建节点、然后直接引用图片 URL 是错的** —— 创建接口的响应体里只有 `taskId`，`{{...output.http.data.resultList[0].url}}` 永远取不到东西。必须搭出下面这个环：

```
LinkfoxHTTP（创建 /aigc/xxxAsync）
  ↓
CustomFunction（await sleep(30000)）  ←──────────┐
  ↓                                              │
LinkfoxHTTP（查 /aigc/taskQuery）                │
  ↓                                              │
Condition（status equal SUCCESS）                │
  ├─ 锚点 0（命中）→ 继续下游，取 resultList[0].url
  └─ 锚点 1（Else）→ Loop（回跳到 sleep 节点）───┘
```

**延时靠 `CustomFunction` 里的 `await sleep()`**（没有 delay / wait / sleep 节点）：

```javascript
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
await sleep(30000);
return 'waited 30000ms';
```

⚠️ **单个 sleep 不超过 50 秒**：`CustomFunction` 单次执行上限 60 秒。`sleep(30000)` 安全；要等 2 分钟就让 Loop 多转几轮，**不要**写 `sleep(120000)`——会超时报错。也**不要**拿 `CustomPythonFunction` 的 `time.sleep` 当延时：同样 60 秒上限，而且每轮都要多等一次沙箱启动。

⚠️ **不要用 `Atomics.wait`**。它是同步阻塞，会卡住整个实例上所有用户的流程。`await sleep()` 只挂起当前这条流程。

**关键的三处取值**（照这个填，别自己推）：

```text
# 1) 查询节点的 body：taskId 取自【创建节点】，不是它上游那个 sleep 节点
#    （sleep 的 CustomFunction 只返回一句 'waited 30000ms'，没有 taskId）
"body": "{\"taskId\": \"{{linkfoxHttpAgentflow_0.output.http.data.taskId}}\"}"

# 2) Condition 判任务状态：value1 取【查询节点】的 status
{"type": "string", "value1": "{{linkfoxHttpAgentflow_1.output.http.data.status}}",
 "operation": "equal", "value2": "SUCCESS"}

# 3) SUCCESS 分支取结果
{{ linkfoxHttpAgentflow_1.output.http.data.resultList[0].url }}   # 图片 / 视频
{{ linkfoxHttpAgentflow_1.output.http.data.content }}             # 生文（textTaskQuery）
```

`Loop` 的 `loopBackToNode` 值形如 `<sleep 节点 id>-<该节点 label>`（见 `nodes-control-flow.md`）。Condition 那两条出边记得各带 `data.edgeLabel`（`"0"` / `"1"`），否则 `save_workflow.py` 会给 warning——画布上看不出哪条是 SUCCESS、哪条是重试。

**四条硬规则**（每条都能踩死，且运行时不会提示你）：

1. **`loopBackToNode` 必须指向 sleep 节点，不是创建节点。** 指到创建节点上，每轮循环都会**重新创建一个 AIGC 任务** —— 真实扣算力，而且 `taskId` 每轮都变，永远等不到那个任务完成。
2. **`SUCCESS` 写成 condition、Else 接 Loop。** Condition 一条都没命中时会**强行走最后一个分支**，所以顺序不能反。要区分 `FAILED`（比如失败了发个通知），就在 Else 里再串一个 `Condition` 判 `FAILED`；不判的话 `FAILED` 会一路空转到 `maxLoopCount` 才停。
3. **先判 HTTP 状态码，再判业务 `status`。** `HTTP` / `LinkfoxHTTP` 的 4xx/5xx **不会中止流程**（见 `output-and-state.md`），下游拿到的是错误响应体。严谨的做法是查询节点后先 `Condition` 判 `{{<查询节点>.output.http.status}}` 是否 200。
4. **回跳路径里只放 sleep + 查询 + Condition。** 下载、写多维表、发通知全部放 `SUCCESS` 分支 —— 循环体里的副作用会**重复执行**。

**`maxLoopCount` 按模态给**（sleep 30 秒时）：

| 场景 | 轮询策略 | `maxLoopCount` |
| --- | --- | --- |
| 生图 / 生文 | 总超时约 10 分钟 | `20`（约 10 分钟） |
| 生视频 / 多图生视频 | 首查前先等约 2 分钟，总超时约 20 分钟 | `40`（约 20 分钟；前 4 轮相当于首查前的等待） |

**要在方案里对用户点明的代价**：生视频这条 flow 墙钟就是 10–20 分钟，而 `run_workflow.py` 的 `--timeout` 上限是 900 秒，网关也会先返 504。按 `runtime-execution.md` 的约定，**504 不代表执行失败**，服务端仍在后台跑 —— 这类 flow 的试跑结果要用 `list_executions.py` 查，**绝不能因为 504 就重跑**（重复触发会堆出多个进行中的执行，之后所有执行开始排队）。不提前说清这一条，用户第一次试跑看到 504 就会反复重跑。

---

## End（结束）

| 字段 | 值 |
| --- | --- |
| `data.name` | `endAgentflow` |
| `data.type` | `End` |
| `version` | `1.0` |
| `color` | `#EF4444` |
| `baseClasses` | `["End"]` |
| `credential` | 无 |
| 输出锚点 | **无**（`hideOutput: true`） |

**用途**：显式标记 flow 结束。`inputs` 为空对象，没有任何可配置字段，运行时 `input` / `output` 都是 `{}`——**它不产生任何值，也不向用户回复**。

**与 DirectReply 的区别**：需要给用户一段可见回复用 `DirectReply`；只是想在画布上标出"这条分支到此为止"用 `End`。

**限制**：无出边（与 Loop / DirectReply 同类）。**不要滥用**：flow 本来就可以停在最后一个动作节点上，只在用户明确要求标注结束、或多个分支需要在画布上收口时才加 `End`。

---

## Edge 命名速查

以 `BusinessStart` → `DataReader` → `SendNotification` 为例：

```json
{
  "source": "businessStartAgentflow_0",
  "sourceHandle": "businessStartAgentflow_0-output-businessStartAgentflow",
  "target": "dataReaderAgentflow_0",
  "targetHandle": "dataReaderAgentflow_0",
  "type": "agentFlow",
  "id": "businessStartAgentflow_0-businessStartAgentflow_0-output-businessStartAgentflow-dataReaderAgentflow_0-dataReaderAgentflow_0",
  "data": { "sourceColor": "#8B5CF6", "targetColor": "#0F766E", "isHumanInput": false, "edgeLabel": "" }
}
```

各节点单出口的 `sourceHandle` 后缀分别是：

| 节点 | sourceHandle 后缀 | edgeLabel |
| --- | --- | --- |
| `BusinessStart` | `-output-businessStartAgentflow` | `""` |
| `CrossBorderExpert` | `-output-completed` | `Completed` |
| `DataReader` | `-output-data` | `Data` |
| `FillForm` | `-output-submitted` | `Submitted` |
| `SendNotification` | `-output-sent` | `Sent` |
| `WriteFile` | `-output-written` | `Written` |
| `LinkfoxHTTP` | `-output-linkfoxHttpAgentflow` | `""` |
| `End` | 无输出锚点，不允许出边 | — |

---

## 生成检查清单

- [ ] 用户描述涉及"店铺事件 / 授权店铺 / 业务定时 / 邮件通知 / 飞书 / 钉钉 / 跨境专家 / 多维表 / CSV 或 Excel 读取"等场景时，**优先使用本文件的节点**，不要用原生 HTTP / CustomFunction 手工模拟。
- [ ] 同一 flow 只放一个开始节点，且是 `BusinessStart`，没有原生 `Start`。
- [ ] 所有 `asyncOptions` 值（`amazonStore` / `expertId`）、`credential`、`FLOWISE_CREDENTIAL_ID` 一律留 `""`（`credential` 由后台自动绑定，`asyncOptions` 导入后由用户选择）；多维表 `notebookId` / `tableId` 填用户选定的真实 id。
- [ ] `data.color`、`data.name`、`data.type`、`baseClasses`、`sourceHandle` 严格按本文件复制，禁止改写或翻译。
- [ ] **`inputParams` 整个字段没出现**（本文件这些节点全部由 `save_workflow.py` 代填，`taskInstruction` / `messageContent` / `recipients` / `emailSubject` / `emailCc` / `newTableName` 的 `acceptVariable` 与 `crossBorderExpertUpdateState.value` 的 `acceptNodeOutputAsVariable` 都已在模板里）。写成 `[]` 不算省略、会被 error 拦下。
- [ ] 下游取值用各节点**真实的 output 字段**（`output.expertResult` / `output.<outputVariableName>` / `output.status` / `output.successChannels` / `output.recordCount` / `output.result` / `output.filledForm` / `output.http.data` / `output.storeAuthorization`），禁止用裸 `.output`，也**禁止把锚名当字段**（不存在 `output.data` / `output.sent` / `output.written` / `output.completed` / `output.submitted`）。字段表见 `output-and-state.md`。
- [ ] 没给 `WriteFile` / `SendNotification` / `LinkfoxHTTP` / `DataReader` / `FillForm` / `End` 造 `UpdateState` 字段——只有 9 个节点有（见 `output-and-state.md` 第 4.2 节），其中本文件只有 `CrossBorderExpert` 一个。
- [ ] 没在 `BusinessStart` 的 `inputs` 里写 `startState` / `startPersistState`——它们不存在。
- [ ] `WriteFile` 的 `writeDestination` 只用 `linkfoxTable` / `newLinkfoxTable` / `updateLinkfoxTable` 三者之一，没有用 `productLibrary`。写已有表、改已有行时**两级都给了**（`notebookId` + `tableId`，填用户选定的表）；新建表时用 `newTableNotebookId`（默认 `__new__`）+ `newTableName`。
- [ ] **"改已有行"用的是 `updateLinkfoxTable`，不是先删后加、也不是写一条新记录**。记录触发的回写链里 `updateRecordId` **留空**（节点自己从上一步取 `recordRows.recordId`）；不是这条链时才手填或用变量引用。已确认上一步只给**一条**记录——多条会直接报错。
- [ ] **选多维表的地方都是两级下拉**：`DataReader`（`linkfoxTable` 分支）、`WriteFile`（`linkfoxTable` / `updateLinkfoxTable` 分支）、`BusinessStart`（`tableRecordTrigger`）都要写 `notebookId` + `tableId` 两个字段，值是查表后用户选定的真实 id；不要只写 `tableId` 当一级下拉用。
- [ ] **含 `tableRecordTrigger` 的 flow 已在回复里点明两件事**：① 记录触发要在 linkfox-workflow 系统界面上保存一次才会生效，只在画布上配或只经本 skill 上传等于没配；② `tableId` 留占位时服务端保存校验会 400（`Data Table is required on the Start node.`），所以触发表必须先问用户选定再生成。
- [ ] 记录触发的 flow 里取"这次变的那一行"用的是 **`{{businessStartAgentflow_0.output.recordEvent.*}}` 节点引用**（`.recordId` / `.recordByName.<字段名>` / `.changedFieldNames`），**没有**用 `{{$webhook.*}}`（不落执行记录、且与原生 webhookTrigger 的 `body/headers/query` 形状容易混），也没有拿 `BusinessStart.output.tableRecordTrigger` 当"本次变更数据"用（它只是订阅配置的静态回显）。
- [ ] **记录触发要写表时，直接把 `BusinessStart` 接到 `WriteFile`**，用它吐的 `output.rows`（name-keyed），**没有**在中间塞一个只为搬数据的 `CustomFunction`，也**没有**把 `recordEvent.record` 当写入数据用（那份 key 是 `fldXXX`，写入侧回 404）。
- [ ] 补配置指引里**没有**让用户去页面上绑定 `linkfoxAgentApi` 凭据——这个凭据由后台自动绑定。
- [ ] **含 `FillForm` 的 flow 已告知用户它会暂停流程等人填表**：试跑会停在这个节点并返回 `STOPPED`，那不是失败、也不是超时，要有人在界面上提交表单才继续。`formFields` 里**没有** `formTitle` / `description` / `defaultValue`。
- [ ] 调 Linkfox 工具网关 / 内部服务用 `LinkfoxHTTP` + 相对路径，**不要**用原生 `HTTP` 手写 `tool-gateway.linkfox.com` 全量 URL 再自拼认证头；调第三方外部 API 才用原生 `HTTP`。
- [ ] **逐个数了 flow 里的 `LinkfoxHTTP` 节点数量，并确认已对每一个都用 `query_tools_matrix.py` 查过对应端点**（见上方"如何确定 path/body/headers/queryParams"）；用户规格文档只给了 skill 名/endpoint_path 没给完整字段也算触发条件，不因为 path 已知就跳过 body。没有任何一个节点的 `body` 是占位 `"{}"` 或直接照抄规格文档字面量——确实查不到已上线的匹配工具才允许留空占位，并在补配置指引里逐个点名。
- [ ] **每个 `LinkfoxHTTP` 的 `body` 里，必填参数的值真的接到了上游字段**（`{{fillFormAgentflow_0.output.filledForm.<字段>}}` 或 `{{<上游>.output.http.data.<叶子路径>}}`），没有"字段名组好了、值全是空串"的形态——那个形态运行时报 `xxx 为必填参数`。见上方"`body` 的必填参数必须真的接上游数据"。
- [ ] **每个 `CrossBorderExpert` 的 `taskInstruction` 都没有内联整体响应**（`.output.http.data` / `.output.http` / `.output.expertResult` / `.output.content` / `.output.tableData` 这类停在根字段上的引用），且字面量在 9000 字符以内——专家平台硬上限 10000 字符。见上方"`taskInstruction` 有 10000 字符硬上限"。
- [ ] **`data.credential` 不是类型名 `linkfoxAgentApi`**：生成时留 `""`，refine 时保留 fetch 基线里已绑定的实例 id。
- [ ] `End` 只在明确需要标注流程结束时才加；它不回复用户、不产出值，也不允许有出边。
- [ ] **每个异步任务接口（`/aigc/*Async` 这类只回 `taskId` 的）都配了完整轮询环**：`CustomFunction(await sleep)` → 查询 → `Condition(status equal SUCCESS)` → Else 接 `Loop`，且 `loopBackToNode` 指向 **sleep 节点而不是创建节点**（指错会每轮重建任务、真实扣算力）；副作用节点都在 SUCCESS 分支外、不在回跳路径里；`maxLoopCount` 按模态给（生图/生文 20，生视频 40）。没有出现"只放一个创建节点就直接引用 `resultList[0].url`"的形态 —— 那个字段在创建响应里不存在。见上方"异步任务接口：必须自己搭轮询循环"。
- [ ] 用了延时的地方是 `await sleep(ms)`，**不是 `Atomics.wait`**（后者同步阻塞，会卡住整个实例上所有用户的流程）。
