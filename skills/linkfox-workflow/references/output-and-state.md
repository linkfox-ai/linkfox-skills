# linkfox-workflow Agentflow v2：跨节点取值与 Flow State

**任何 flow 里出现 `{{ }}` 引用、或需要在节点间共享数据时读本文件。** 本文件是"引用什么字段"的唯一真相源；"字段要不要标 `acceptVariable`"见 `variable-substitution.md`，两者不重复。

## 0. 一条最容易错的规则：锚名 ≠ 输出字段

`outputAnchors[].name`（`data` / `sent` / `written` / `completed` / `submitted`）是**画布上的连线句柄**，只出现在 edge 的 `sourceHandle` 里。它**不是** `output` 对象里的字段名。

```text
sourceHandle: dataReaderAgentflow_0-output-data     ✅ 锚点，连线用
{{ dataReaderAgentflow_0.output.data }}             ❌ 该字段不存在，模板不会被替换
{{ dataReaderAgentflow_0.output.tableData }}        ✅ 真实字段（= outputVariableName）
```

同类错法：`SendNotification` 没有 `output.sent`、`WriteFile` 没有 `output.written`、`CrossBorderExpert` 没有 `output.completed`、`FillForm` 没有 `output.submitted`。取值一律查第 2 节的表。

引用了不存在的字段时运行时**不报错**：模板原样保留，用户在画布或通知里看到字面量 `{{ x.output.data }}`。`save_workflow.py` 会按节点校验 output 根字段。

## 1. 连线不等于自动传值

edge 只决定执行顺序、谁是上游、变量选择器能列出哪些节点。**它不会把上游输出自动填进下游的 prompt 或参数。**

每个节点默认的 `input` 始终来自本次触发输入，不是上一个节点的结果。要用上游结论，必须在支持变量的字段里**显式引用**。

## 2. 各节点 output 字段速查

### 2.1 默认引用 `{{nodeId}}` 的取值顺序

默认引用 `{{nodeId}}` 按顺序取 `output.content`，没有则取 `output.http.data`。所以 `HTTP` / `LinkfoxHTTP` 回退到 `output.http.data`；两者都没有的节点（`Condition` / `Iteration` / `End`）默认引用取不到值，模板保留原样。

**生产 flow 一律用精确引用 `{{nodeId.output.<路径>}}`**，不要依赖默认回退。

### 2.2 LinkFox 自定义节点

| 节点 | 固定 output 字段 | 常用引用 |
| --- | --- | --- |
| `BusinessStart` | `question`（手动启动恒为 `""`）；`storeAuthorization`（仅店铺授权，含 `sellerId` / `region` / `marketplaceIds` / `changeType` / `checkIntervalMinutes`）；`tableRecordTrigger`（仅记录触发，含 `notebookId` / `tableId` / `eventType` / `checkIntervalMinutes`，按事件多带 `watchFieldNames` 或 `condition`）；**`recordEvent` / `rows` / `recordRows`**（仅记录触发**且真收到变更载荷**时才存在，见 2.4） | `{{businessStartAgentflow_0.output.recordEvent.recordId}}` |
| `CrossBorderExpert` | `content` / `expertId` / `status` / `messageId?` / `stopReason?` / `expertResult` | `{{crossBorderExpertAgentflow_0.output.expertResult}}` |
| `DataReader` | `content` / `status` / `rowCount` / `truncated` / **`<outputVariableName>`**（默认 `tableData`） | `{{dataReaderAgentflow_0.output.tableData.rows}}` |
| `FillForm` | `content` / `filledForm` | `{{fillFormAgentflow_0.output.filledForm.<字段名>}}` |
| `SendNotification` | `content` / `status` / `successChannels` / `failedChannels` | `{{sendNotificationAgentflow_0.output.status}}` |
| `WriteFile` | `content` / `status` / `target` / `recordCount` / `result` | `{{writeFileAgentflow_0.output.recordCount}}` |
| `LinkfoxHTTP` | `http`（`.data` / `.status` / `.statusText` / `.headers`） | `{{linkfoxHttpAgentflow_0.output.http.data}}` |
| `End` | 无（`output` 是 `{}`） | 不要引用 `End` |

要点：

- `content` 在这些节点里都是"整个结果的 JSON 字符串"，适合塞进通知正文；要取字段就用结构化字段，不要对 `content` 再点路径。
- `SendNotification` **没有** `output.details`；各渠道明细只在 `output.content` 的 JSON 字符串里。
- `WriteFile` 的 `target`：写已有表分支是 `{type, notebookId, tableId}`（散表 / 存量流程 `notebookId` 为 `null`）；`updateLinkfoxTable`（改已有行）分支再加 `recordId`；新建分支额外带 `notebookId` / `notebookName` / `addedToExistingNotebook` / `tableName` / `createdTime` / `idempotentHit` / `fields`，走 `addTable`（新建位置选了已有容器）时 `notebookName` 为 `null`、`idempotentHit` 恒为 `false`。写已有表 / 改已有行时若摘掉了计算列，`target` 多一个 `droppedComputedFields`。
- `BusinessStart` 的 `tableRecordTrigger` 是**订阅配置的静态回显**，不是"这次改了哪一行"。本次变更的数据在 `recordEvent` / `rows` / `recordRows` 三个字段里（见 2.4），二者别混。
- `CrossBorderExpert` 失败时 `status = "error"`，`expertResult` 通常是 `{error, statusCode?, messageId?, stopReason?}`。

### 2.3 DataReader 的 `output.<outputVariableName>`

`outputVariableName`（默认 `tableData`）是**结果别名**，不是重命名 `output`。节点同时写两处：

```text
output.<outputVariableName>          # 结构化表格对象
$flow.state.<outputVariableName>     # 自动写入共享状态，无需 Update Flow State
```

`content` / `status` / `rowCount` / `truncated` 四个固定字段在所有数据源下都存在。

`csv` / `excel` / `linkfoxTable` 三种数据源的形状：

```json
{
  "columns": [{ "key": "<字段名>", "label": "<列标题>", "index": 0, "type": "string" }],
  "rows": [{ "<字段名>": "<值>" }],
  "pageInfo": { "limit": 2000, "returned": 2, "total": 2, "hasMore": false, "truncated": false }
}
```

`amazonStore` 是例外：直接返回解析后的对象，**没有 `columns` / `pageInfo`**，形状随 `amazonDataType` 变化：

| `amazonDataType` | `output.<变量名>` 形状 | 取数组的路径（变量名按实填） |
| --- | --- | --- |
| `orderList` | `{ orders: [] }` | `.output.tableData.orders` |
| `listing` | `{ listings: [] }` | `.output.tableData.listings` |
| `fbaInventory` | `{ inventorySummaries: [] }` | `.output.tableData.inventorySummaries` |
| `afterSalesOrder` | `{ reportType, reportId, rows: [] }` | `.output.tableData.rows` |
| `removalOrder` | `{ reportType, reportId, rows: [] }` | `.output.tableData.rows` |

**变量名规则**：推荐 `^[A-Za-z_][A-Za-z0-9_]*$` 的 camelCase。**禁止**用 `content` / `status` / `rowCount` / `truncated`（同名会覆盖固定字段），也避免 `output` / `state` / `question` / `$flow` / `$vars` / `__proto__` / `prototype` / `constructor`。别用点号、方括号、空格、连字符、中文。留空则用默认 `tableData`。

多个 DataReader 用不同变量名：`output.<name>` 靠 nodeId 隔离没问题，但它们写的是**同一个** `$flow.state.<name>`，后执行的会覆盖先执行的。

CSV / Excel 文件上限 5MB，超出直接报错；`maxRows` 上限 2000。

### 2.4 BusinessStart 记录触发的三个变更字段

记录触发时，变更上下文**原样进 `BusinessStart` 自己的 output**。三个字段并列，用途不同：

| 字段 | 内容 | 拿来干什么 |
| --- | --- | --- |
| `recordEvent` | 原始载荷，不裁剪：`eventId` / `eventType` / `tableId` / `notebookId` / `recordId` / `occurredAt`（变更**发生**时间，不是投递时间）/ `triggeredBy` / `changedFieldIds` / `changedFieldNames` / `record`（key 是字段 id `fldXXX`）/ `recordByName`（key 是字段名） | 读单个值、做条件判断 |
| `rows` | 同一行翻成 **name-keyed** 的数组 | **直接接 `WriteFile`**（就是它的入参形状） |
| `recordRows` | `{rows, recordId?, tableId, keyedBy}`，另可带 `droppedComputedFields` / `warnings` | 回写那一行（`WriteFile` 的 `updateLinkfoxTable` 自己读 `recordId`）、在执行记录里回溯 |

```text
{{businessStartAgentflow_0.output.recordEvent.recordId}}
{{businessStartAgentflow_0.output.recordEvent.recordByName.<字段名>}}
{{businessStartAgentflow_0.output.recordEvent.changedFieldNames}}
{{businessStartAgentflow_0.output.rows}}                       # 接 WriteFile，一般不用手写引用
```

四个要点：

- **这三个 key 只在真收到变更载荷时存在**；手动点「启动任务」跑同一条流时整个不出现（不造空对象，也不报错）。引用它们的地方要能容忍取不到值。
- **不要用 `$webhook` 取这些**。它运行时仍能解析，但不落任何节点输出，引用写错时执行记录里无从对照；且原生 `webhookTrigger` 用的是 `$webhook.body` / `.headers` / `.query` 三段式，与这里平铺的形状毫不相干，混写必错。
- **写表一律用 `rows`，不要用 `recordEvent.record`**：后者 key 是字段 id，写入侧只认字段名，传 id 会失败。
- **只有变更后的值，没有旧值**：表达不了"从 A 变成 B 时才怎样"。`recordByName` 依赖载荷里带了字段字典，存量消息可能没有，该键不存在时要有兜底（例如把 `recordId` 传下去回查那一行）。

### 2.5 原生节点

| 节点 | 固定 output 字段 | 常用引用 |
| --- | --- | --- |
| `Agent` | `content` / `timeMetadata`；可选 `calledTools` / `usageMetadata` / `responseMetadata` / `usedTools` / `sourceDocuments` / `artifacts` / `availableTools` / `isWaitingForHumanInput` / `fileAnnotations` / `reasonContent`；structured output 的 key 直接挂在 `output` 同层 | `{{agentAgentflow_0.output.content}}`、`{{agentAgentflow_0.output.usedTools}}` |
| `LLM` | `content` / `timeMetadata`；可选同上（无 `usedTools` / `availableTools` / `sourceDocuments`）；structured output 同层 | `{{llmAgentflow_0.output.content}}` |
| `Tool` | `content`；可选 `artifacts` | `{{toolAgentflow_0.output.content}}` |
| `Retriever` | `content`（`text` = 各文档 `pageContent` 换行连接；`textWithMetadata` = 完整 Document 数组的 JSON 字符串） | `{{retrieverAgentflow_0.output.content}}` |
| `CustomFunction` | `content`（返回对象时被 JSON 序列化成字符串，**不能往下按字段取**） | `{{customFunctionAgentflow_0.output.content}}` |
| `CustomPythonFunction` | `content`（`result` 转成的字符串）/ `result`（**保留原类型**，未赋值为 `null`）/ `logs` / `stderr` | 按字段取：`{{customPythonFunctionAgentflow_0.output.result.<字段>}}`；整体：`{{customPythonFunctionAgentflow_0}}`。**`output.content.<字段>` 取不到**（字符串），`save_workflow.py` 报 error |
| `DirectReply` | `content`（无出边，一般不被引用） | — |
| `HTTP` | `http`（`.data` / `.status` / `.statusText` / `.headers`） | `{{httpAgentflow_0.output.http.data}}` |
| `ExecuteFlow` | `content`；可选 `sourceDocuments` / `usedTools` / `artifacts` / `fileAnnotations` | `{{executeFlowAgentflow_0.output.content}}` |
| `Condition` | `conditions[]`（每项含比较数据与 `isFulfilled`） | 一般不引用，靠分支锚点 |
| `ConditionAgent` | `conditions[]` / `content` / `timeMetadata`；可选 usage/response metadata | 一般不引用 |
| `Loop` | `content` / `nodeID` / `maxLoopCount` | 一般不引用 |
| `HumanInput` | 暂停时 `content`；恢复后 `content` + `conditions[]` | `{{humanInputAgentflow_0.output.content}}` |
| `Iteration` | `{}` | 不要引用 |
| `StickyNote` | 无运行时 output | — |

Agent / LLM 的 structured output key 与固定字段**同层**，所以不要把结构化字段命名成 `content` / `timeMetadata` / `usageMetadata` / `responseMetadata`，会覆盖原字段。

`HTTP` / `LinkfoxHTTP` 请求失败时直接报错，不会产生可供下游引用的成功 `output.http`。

### 2.6 节点结果的外层结构

每个节点的结果由 `id` / `name` / `input` / `output` / `state`（部分另有 `chatHistory`）组成。只有 `output` 用 `{{nodeId.output.xxx}}` 引用；`state` 通过 `{{$flow.state.xxx}}` 读；`input` / `id` / `name` / `chatHistory` 不作为业务结论引用。

## 3. 读取 Flow State

```text
{{$flow.state.summary}}
{{$flow.state.expertResult.title}}     # 支持点路径读嵌套字段
{{$flow.state.tableData.rows}}
```

`$flow.state` 是**当前 flow 本次执行**的共享状态，不跨工作流、不跨用户。平台级配置是另一套：`{{$vars.<name>}}`，`Update Flow State` 改不了它。

路径不存在时模板保留原样，不会替换成空。

## 4. 写入 Flow State

### 4.1 BusinessStart 不能预声明初始 State

原生 `Start` 有 `startState[]` 可以集中声明 key，但开始节点强制是 `BusinessStart`，它的面板里**没有** `startState` / `startEphemeralMemory` / `startPersistState`。

由此：

1. 以 `BusinessStart` 为起点时，**初始 State 是空对象**，无法在设计阶段集中声明状态结构。不要在 `BusinessStart` 的 `inputs` 里写 `startState`，该字段不存在。
2. 原生节点（Agent / LLM / Tool / Retriever / CustomFunction / ExecuteFlow / Loop）以及 `CustomPythonFunction` 的 `Update Flow State → Key` 下拉框在此情形下会**加载失败**。只有 `CrossBorderExpert` 会返回空列表。
3. **运行时写入不受影响**：写入时不校验 key 是否声明过。

**生成 flow 时的实际影响**：State key 只能由节点在运行时创建。给用户的补配置指引里，凡是让用户去原生节点下拉框里选 key 的说法都是错的。要么让用户手工填 key（`CrossBorderExpert` 支持自由输入），要么改用 Node Output 精确引用。**能用 `{{nodeId.output.<路径>}}` 表达的依赖就别绕 State。**

### 4.2 哪些节点有 Update Flow State

**只有这 9 个**：`Agent` / `LLM` / `Tool` / `Retriever` / `CustomFunction` / `CustomPythonFunction` / `ExecuteFlow` / `Loop` / `CrossBorderExpert`（字段名分别是 `<name>UpdateState[]`，如 `agentUpdateState` / `crossBorderExpertUpdateState`）。

其余节点的写入行为是固定的，**不要给它们造 `UpdateState` 字段**：

- `DataReader`：自动写 `$flow.state.<outputVariableName>`。
- `FillForm`：固定写 `state.filledForm`。
- `WriteFile` / `SendNotification` / `LinkfoxHTTP` / `HTTP` / `End`：原样透传 State，不写入。要把它们的结果放进 State，只能在**下游**某个有 `UpdateState` 的节点里引用，例如 `Value: {{writeFileAgentflow_0.output.result}}`。

### 4.3 `{{ output }}` 指当前节点，不是上游

在 `UpdateState[]` 的 `value` 里：

```text
{{ output }}                 # 当前节点本次执行的主要结果
{{ output.<字段名> }}        # 当前结果的嵌套字段
```

它**不是**上游引用，也不是节点的真实字段名，只在支持 `UpdateState` 的节点完成后被替换成实际结果。引用上游永远用 `{{nodeId}}` 或 `{{nodeId.output.<路径>}}`。

各节点给 `{{ output }}` 的值不同：Agent / LLM / Tool / Retriever / CustomFunction 给最终文本结果，`CrossBorderExpert` 给结构化的 `expertResult`，`CustomPythonFunction` 给 `result`（`{{ output.<字段名> }}` 直接取字段，**不用写 `.result`**，值保留原类型）。

`value` 本身支持变量，所以也能存上游结果或复制已有 State：

```text
Key: retrievedDocuments   Value: {{retrieverAgentflow_0.output.content}}
Key: previousSummary      Value: {{$flow.state.summary}}
```

### 4.4 合并语义与 key 命名

写入是浅合并：key 不存在则新增，存在则覆盖，其余不变。

**key 不要带点号**：`Key: customer.name` 得到的是名为 `customer.name` 的普通 key，而读取 `{{$flow.state.customer.name}}` 按嵌套路径查找，两者对不上。用 camelCase 存整个对象，再用点路径读字段。

## 5. 内置变量速查

| 分类 | 变量 |
| --- | --- |
| Chat Context | `{{question}}` / `{{chat_history}}` / `{{current_date_time}}` / `{{runtime_messages_length}}` / `{{loop_count}}` / `{{file_attachment}}` |
| Flow Variables | `{{$flow.sessionId}}` / `{{$flow.chatId}}` / `{{$flow.chatflowId}}` / `{{$flow.state.<key>}}` |
| 平台变量 | `{{$vars.<name>}}` |
| 表单 | `{{$form.<字段名>}}`（原生 Start 的 `formInput` / `scheduleInput` form 模式） |
| Webhook（**只有**原生 `webhookTrigger` 用） | `{{$webhook.query.<k>}}` / `{{$webhook.body.<k>}}` / `{{$webhook.headers.<k>}}` |
| 多维表记录触发的变更数据 | **不走 `$webhook`**，用节点引用 `{{businessStartAgentflow_0.output.recordEvent.*}}` / `.output.rows` / `.output.recordRows.recordId`（见 2.4） |
| Iteration | `{{$iteration}}` / `{{$iteration.<字段>}}` |
| FillForm | `{{$flow.state.filledForm.<字段名>}}` |

记录触发里 `$webhook` 虽仍能解析，但不要这么写（理由与限制见 2.4）。

`BusinessStart` 手动启动时 `question` 恒为 `""`，`{{question}}` 拿不到用户文本，依赖用户输入的场景不要设计成手动启动。

花括号内允许空格（`{{ question }}` 与 `{{question}}` 等价）。

## 6. 序列化与分支行为

- 字符串直接插入；数组 / 对象插入文本字段时按 JSON 字符串插入。
- 精确路径或 State 路径不存在时**不替换**模板（用户会看到字面量）。
- `UpdateState` 的 `value` 恰好等于 `{{ output }}` 时，部分节点能保留对象类型而非字符串。
- 分支未执行时，其节点变量拿不到值，模板保持未替换。**只引用当前执行路径上必然完成的上游节点。**
- 同一节点在 Loop 里执行多次时，取**最近一次**执行的输出。

## 7. Node Output 还是 Flow State

优先 Node Output（`{{nodeId.output.<路径>}}`）：数据从一个明确上游流向少数下游、依赖关系要清晰。

优先 Flow State：多个下游分支都要读同一份数据、Condition / Loop 需要共读共写。

不要为了相邻两个节点传值就把所有输出复制进 State。BusinessStart 分支下 State 无法预声明、原生节点 key 下拉框还会加载失败，Node Output 通常更省事。

## 8. 排查清单

模板没被替换，按顺序查：

1. 字段在 `inputParams` 里标了 `acceptVariable: true` 吗（见 `variable-substitution.md`）。
2. 引用的字段**真实存在**吗：是不是把锚名 (`data` / `sent` / `written`) 当成了 output 字段（见第 0 节）。
3. nodeId 拼对了吗：**逐字**跟实际节点的 `id` 对上（新建节点是 `_0` / `_1`，画布上建的是随机数字后缀如 `_415972`，不要凭印象写成顺序号）。
4. 那个分支在本次执行里跑到了吗。
5. State key 拼写一致吗、写入节点先执行了吗。

## 9. 外部调用的失败语义

调外部接口、发通知、解析外部内容的节点,"节点执行完成"不等于"动作成功"。这类节点失败时往往不报错,流程照样 `FINISHED`。设计期按下面四条检查;运行期用 `run_workflow.py` 的 `actionResults` 和 `list_executions.py --node-io` 核对。

| 规则 | 设计上要怎么做 |
| --- | --- |
| **HTTP 200 不等于业务成功** | `HTTP` / `LinkfoxHTTP` 的 `output.http.status` 是 2xx 时,响应体里的业务码仍可能是失败(比如飞书机器人返回 `{"code": 19001}`、网关返回 `{"errcode": 400}`)。下游要据此分支或记账时,Condition 判断的是**业务码**(`output.http.data.<码字段>`),不是 `http.status`。业务码字段名以该接口的文档为准,不要猜 |
| **解析失败要有出口** | 解析外部内容(网页、接口文本)的 `CustomFunction` / `CustomPythonFunction` 要显式返回"解析失败"标记(比如 `{ok: false, reason}`),不要抛异常或返回空结果。下游 Condition 先判断 `ok`,失败分支**不写任何持久化状态**(多维表、基线),只通知或结束 |
| **首次运行失败不能固化成基准** | 用"上一次结果"做比较的流程(变化监测、增量同步),写入基线的那一步只能挂在**本次取数成功**的分支上。异常页、空结果、错误响应一旦写进基线,之后每次比较都是错的 |
| **首次运行路径要能走通** | 设计时单独推演"还没有基线 / 计数为 0 / 状态为空"这一种输入:它走哪条分支、那条分支会不会**建立**这个状态。常见死锁是建立状态的动作挂在"状态已存在"的分支上,结果首次之后永远不写。推演完用一次带 `--expect-reached <写入节点>` 的执行实际验证 |

`SendNotification` 自己会汇总渠道结果:至少一个渠道成功时 `output.status` 为 `ok`,全部失败为 `error`,明细在 `successChannels` / `failedChannels`。要求"某个渠道必须送达"时,判断 `failedChannels`,不要只看 `status`。
