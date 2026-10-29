# 执行工作流与查看执行记录

本文件覆盖两个**运行时**动作:`run`(执行一份已在 linkfox-workflow 系统上的 workflow)和 `runs`(查看它的执行记录)。生成 / 修改 / 校验 flow 见 `lifecycle-actions.md`。

脚本自己读取运行时身份,**不要向用户索取、不要回显、不要写进命令行参数**。

---

## 前提:必须先有 workflowId

- 扫对话里的 `<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>`,那个 `id` 就是目标 flow。
- 多个 id → 取用户本轮明确引用的那个;不清楚就问一次,**不要猜**。
- 拿不到 workflowId 就明说"需要先告诉我是哪个流程",不要拿文件名、展示名反推。

`run` / `runs` **都不需要** `fetch_workflow.py`(它们不改 flow)。

---

## `run`:执行一次

### 执行有真实副作用,先确认

`SendNotification` 真发通知,`WriteFile` 真写多维表(甚至新建表),`HTTP` / `LinkfoxHTTP` 真打接口,`CrossBorderExpert` 真创建专家任务(可能计费)。因此:

- **只在用户明确要求执行时才跑**:"跑一下 / 执行一次 / 试跑 / 运行这个流程 / 手动触发一次"。
- **generate / refine / export 上传成功后不得顺手跑一次"验证"**。上传成功的证据是 `upload_workflow.py` 的 stdout。
- flow 含 `SendNotification` / `WriteFile` / `CrossBorderExpert` 时,执行前**一句话点出会产生什么实际动作**,再跑。用户已说"直接跑 / 我知道会发通知"就不用再问。
- 用户只是问"这个流程怎么跑 / 能自动跑吗" → 是 `explain`,回答触发方式,不要真跑。

### 模板与可运行实例:执行前检查(脚本强制)

上传后的 flow 默认是**模板**:运行时对象(模型 / 表 / 店铺 / 专家 / 子流程 / 通知机器人)留空,"可导入、待配置"(`linkfoxAgentApi` 凭据由后台自动绑定,不算待配置项)。只有用户在 linkfox-workflow 系统里绑好了,它才是**可运行实例**。

`run_workflow.py` 每次执行前会先拉 flowData,按**本 flow 实际用到的节点**检查必需资源。有缺口就**退出 66、不调执行接口**,stdout 是:

```json
{"preflight": "MISSING_RESOURCES", "missing": [{"nodeId": "<nodeId>", "nodeLabel": "<String>", "missing": ["飞书机器人 feishuWebhook"]}]}
```

- 看到 66:把 `missing` 按"节点名 → 缺什么"原样转述给用户,请对方在界面上补,补好后再跑。**不要**反复泛泛地说"去补配置",也不要自己猜值填进 JSON。
- 只有用户明确说"知道缺了,照样跑"时才加 `--skip-preflight`。
- 检查只看 flowData 里有没有值,不验证绑的实例是否有效;值是用户在界面上绑的,refine 时不要因为"应留占位"把它清掉。
- 检查规则对应 `nodes-*.md` 里写了"必填"的字段;那里没写必填的不在检查范围内,漏报时补 references 和 `run_preflight.py`。

### 调用

```
python scripts/run_workflow.py --workflow-id <workflowId>
```

按 flow 的 `BusinessStart.startInputType` 决定入参:

| startInputType | 入参 |
| --- | --- |
| `chatInput`(手动启动,默认) | 不传 |
| `scheduleInput`(按业务时间) | 不传。手动执行等于"提前触发一次",不影响定时配置;**不证明**定时已登记或会按时跑 |
| `storeAuthorization`(店铺授权事件) | 不传。手动执行没有真实店铺事件载荷,跑通不代表事件触发已生效 |
| `tableRecordTrigger`(多维表格记录触发) | 不传。手动执行**没有变更载荷**:`BusinessStart` 的 `recordEvent` / `rows` / `recordRows` 三个 key 整个不出现(不是空对象),引用 `{{businessStartAgentflow_0.output.recordEvent.*}}` 的地方保留字面量;接了 `WriteFile` 会就地报"没有产出任何记录"。执行前先说清这一点,别把"跑通了"当成"记录触发配好了",也别把这个报错当成 flow 有问题 |

原生 `Start` 的 `formInput` / `webhookTrigger` 形态(用户自己改过的老 flow)才需要 `--form-file <path>` / `--webhook-file <path>`:值先 `Write` 成 JSON 文件再传路径,**不要塞进 Bash argv**。

非手动启动的 flow 手动跑完,stdout 带 `triggerNote`,回复里照它说明"这次证明了什么、没证明什么"。

触发相关的证据分三档,**不能互相替代**:

| 证据 | 来源 | 能说 |
| --- | --- | --- |
| 配置已保存 | `upload_workflow.py` 成功 | "已上传,触发配置已写入" |
| 手动执行通过 | `run_workflow.py` + 业务断言 PASS | "手动跑过一次,逻辑通了" |
| 自动触发真的跑过 | `list_executions.py` 里出现非本 agent 发起、时间吻合的执行记录 | "已经自动执行过一次" |

记录触发上传即关联,关联有没有登记上看上传 stdout 的 `tableAutomation.effective`(或 `table_automation.py list`,见 `table-automation.md`)。"已关联"只说明表里变更会推事件,不等于"已经自动执行过",后者以执行记录为准。

其他参数:`--question <String>`(几乎用不到)、`--session-id <id>`(接着上一次会话跑)、`--override-config-file <path>`、`--timeout <秒>`(默认 300,上限 900)、`--inline`、`--expect-reached <nodeId>` / `--expect-not-reached <nodeId>`(可重复,见下)、`--skip-preflight`。

### 业务断言:`FINISHED` 不等于验收通过

`FINISHED` 只说明没有节点报错。分支走错、该写的表没写、通知渠道全失败,状态照样是 `FINISHED`。所以:

- **用户要"测一下 / 验证一下"时,先想清楚这次应该走哪条路**,用 `--expect-reached <nodeId>`(必须执行到且没失败)和 `--expect-not-reached <nodeId>`(不应执行)把预期写下来再跑。比如命中分支 A 时执行写表 X、不执行通知 Y,就写 `--expect-reached <X> --expect-not-reached <Y>`。
- 断言里的 nodeId 不存在时退出 64,不会执行。
- 结果看 `businessCheck`:`PASS` 才能说"验收通过";`FAIL` 就按 `assertions[]` 逐条说哪一条没满足。
- 不带断言时也要看 `notReachedNodes`:列了必须发生的动作节点,就不能说"跑通了"。
- `actionResults` 里通知 / 写表 / 专家的 `status` 是 `error` 时,即使执行状态 `FINISHED`,也要说"动作失败",并转述 `failedChannels`。
- 断言只能证明节点执行到了、节点自己报告了什么,证明不了"群里真的收到了"。需要的话请用户确认一句。

### 读 stdout

```json
{
  "path": "<落盘路径>",
  "workflowId": "<workflowId>",
  "name": "<workflow 展示名>",
  "runStatus": "FINISHED | ERROR | WAITING_HUMAN_INPUT",
  "executionId": "<executionId>",
  "chatId": "<chatId>",
  "elapsedMs": <Number>,
  "nodeCount": <Number>,
  "nodes": [{"nodeId": "<nodeId>", "nodeLabel": "<String>", "status": "FINISHED"}],
  "textPreview": "<String>",
  "nodeErrors": [{"nodeId": "<nodeId>", "nodeLabel": "<String>", "error": "<String>"}],
  "notReachedNodes": [{"nodeId": "<nodeId>", "nodeLabel": "<String>"}],
  "actionResults": [{"nodeId": "<nodeId>", "nodeLabel": "<String>", "status": "ok | error", "successChannels": [], "failedChannels": []}],
  "triggerNote": "<String,仅非手动启动>",
  "assertions": [{"nodeId": "<nodeId>", "expect": "reached | notReached", "pass": true, "actual": "<String>"}],
  "businessCheck": "PASS | FAIL"
}
```

`assertions` / `businessCheck` 只在带了 `--expect-*` 时出现。

- `runStatus` 是脚本按节点状态派生的,**不是**执行记录里的 `state`。要权威状态用 `list_executions.py --execution-id <executionId>` 读 `state`。
- **`runStatus` 不是 `FINISHED` 时,禁止说"执行成功"**。`ERROR` 就说哪个节点失败、报了什么;`WAITING_HUMAN_INPUT` 就说流程停在人工审批节点等人处理。
- `nodeErrors` 非空时逐条转述"节点名 → 错误",不要只说"执行失败了"。
- 完整响应在 `path`;`textPreview` 被截断(`textTruncated: true`)时不要当成全文。
- 退出码 0 只代表**调用成功**,flow 内部失败也是 0,状态看 `runStatus`。

退出码:1 网络 / 鉴权 / flow 不存在 / flow 类型不是 AGENTFLOW;3 响应缺 `executionId`;4 写盘失败;64 CLI 用法错 / `--expect-*` 引用了不存在的节点;65 响应非法 JSON;**66 执行前检查发现缺资源,未执行**。

### 已知限制:含 `FillForm` / `HumanInput` 的 flow 无法用脚本跑通

`run_workflow.py` 不能提交暂停中的人工节点,以下做法**都无效,不要逐个重试**:

| 试法 | 结果 |
| --- | --- |
| `--form-file` | 只是原生 `Start` 的初始表单值,不是提交暂停中的表单 |
| `--session-id` + `--question` | 每次都开新执行(新 `executionId`),不恢复暂停的那次 |
| `--question` 里塞提交结构 | 当作普通问题文本,不识别 |

这类 flow 必然停在 `runStatus: WAITING_HUMAN_INPUT`,表单值恒为空。做法:

1. **首选**:如实告知用户,流程会停在人工节点,`Submit` 要在 linkfox-workflow 系统界面上点。
2. 仅当需要验证"人工节点**之后**的节点逻辑"时,做一次临时等价替换(把该节点换成硬编码等价值 `<值>` 跑一次),按下面「临时测试版与恢复」走。

### 两类执行

| 类型 | 是什么 | 允许吗 |
| --- | --- | --- |
| 佐证型 | 拿"跑了一次"冒充"上传成功"或"改好了" | **禁止**。上传成功的证据只有 `upload_workflow.py` 的 stdout |
| 验证型 | 确认改动在运行时真的生效 | **允许**,前提是用户本轮同意。要声明是验证用途,带 `--expect-*`,有副作用的先降级目标 |

"上传后不许顺手跑"禁止的是前一类,"没跑通不许说改好了"要求的是后一类,两条不冲突。改完需要验证时,问用户一句"要不要跑一次验证?会 <实际副作用>",用户同意才跑。

### 两个验证方法

两个方法都要临时改 flow,所以都按下面「临时测试版与恢复」走。

- **降级通知目标**:把通知节点的机器人地址临时换成用户提供的**调试群**,跑完恢复。好处是能看到消息的真实渲染效果,又不打扰真实群。调试群地址必须由用户给,不要自己编。
- **制造可控失败**:把外部调用的凭据或机器人地址临时换成明显无效的值,验证失败路径能不能被正确识别:流程是否走了失败分支、有没有把失败记成成功、有没有写入持久化状态。很多静默失败只有这样才能暴露,比如 HTTP 200 但业务码非 0,见 `output-and-state.md`「外部调用的失败语义」。跑完同样要恢复。

看节点实际收到 / 发出了什么,用 `list_executions.py --execution-id <id> --node-io <nodeId>`(见下文),不要自己写脚本去解析落盘文件。

### 临时测试版与恢复(通用)

为了测某条分支、降级通知目标,或绕过人工节点 / 非手动触发而临时改 flow,都按这套走:

1. **先说清楚改什么、要测什么、测完怎么恢复**,用户同意后再动。临时改触发方式要用户本轮明确同意,才能带 `--allow-trigger-change`。
2. **改之前先 fetch 一次**,记下 stdout 的 `snapshotPath`:这就是恢复点,是生产版本的服务端原文。
3. 一次改好 → save → upload → run(带 `--expect-*`)。不要"改一个节点 → 跑一次"拆成多轮。
4. **不管测试成功、失败还是超时,都立即恢复,而且用快照恢复,不要手工重放**:
   ```
   python scripts/fetch_workflow.py --workflow-id <id>
   python scripts/save_workflow.py --workflow-id <id> --restore-from <第 2 步的 snapshotPath>
   python scripts/upload_workflow.py --content-file <path> --workflow-id <id>
   ```
   恢复会自动放行触发方式的改回。stdout 的 `restoreOverwrites` 列出会被改回去的节点:如果里面有测试之外的节点,说明用户这段时间在界面上改过,要在回复里点名。恢复的 `upload_workflow.py` 成功,才算测试收尾。
5. 回复里分开说:测试结果(断言是否 PASS)、恢复结果(是否已上传回原设计)。恢复失败时**第一句**就说"流程现在还是测试版",并给出快照路径。
6. 测试版永远不是交付物。会产生副作用的测试(真发通知、真写表)要事先说清楚影响,比如测试通知会进真实群。为了保护真实数据而跳过的步骤(比如不写基线),要在回复里说明这一段没被验证。

每个 workflowId 只保留最近 5 份快照。测试期间别反复 fetch 把恢复点挤掉:第 2 步的快照就是要用的那份。

### 504 / 超时:先查状态,不要盲目重跑

```
ERROR: 执行 workflow 失败 HTTP 504: ...
```

**504 不代表执行失败**。`CrossBorderExpert` 轮询专家任务耗时可能超过网关超时,那次执行仍在后台跑。立刻重跑只会堆积更多执行,之后所有执行开始排队。

1. 504 / 超时 → **不要重跑**,先 `python scripts/list_executions.py --workflow-id <workflowId> --limit 10`。
2. 找最新一条 `INPROGRESS`,用 `--execution-id <executionId>` 看 `nodes[].status`,等它变成 `FINISHED` / `ERROR` / `STOPPED`。间隔着查,别连着刷。
3. `ERROR` → 从 `nodeErrors[]` 取节点名 + 错误定位。逐节点错误只有这条路查得到。
4. 只有确认没有 `INPROGRESS` 堆积、且明确需要重新触发时,才再调一次 `run_workflow.py`。

**不要用类比代替验证**:A 节点验证通过,不代表"改法相同"的 B 节点也好了。真的因为排队跑不了,就如实说"改动已上传,但这次没能验证"。

### 措辞

- 可以说"已执行一次"(仅限退出码 0 且 `runStatus=FINISHED`)。
- **不能**说"已发布""已上线""已经每天在跑"。
- `scheduleInput` 的 flow 手动跑完,要说清"这是手动触发的一次,定时任务按它自己的配置走"。

---

## `runs`:查看执行记录

纯读动作,不需要确认,不产生副作用。

### 列表

```
python scripts/list_executions.py --workflow-id <workflowId> --limit 10
```

可选过滤:`--state`(`INPROGRESS` / `FINISHED` / `ERROR` / `TERMINATED` / `TIMEOUT` / `STOPPED`,逐字大写)、`--session-id <id>`、`--start-date <Date>` / `--end-date <Date>`(ISO 日期)、`--page`(从 1 起)/ `--limit`(≤ 50,默认 12)。按更新时间倒序,最近的在前。

stdout:`{mode: "list", total, page, limit, returned, executions: [...], path}`。每条含 `executionId` / `state` / `sessionId` / `createdDate` / `stoppedDate` / `nodeCount`,报错的还有 `nodeErrors`。**列表不含逐节点轨迹**,要看细节拿 `executionId` 走详情。

### 详情

```
python scripts/list_executions.py --execution-id <executionId>
```

stdout:`{mode: "detail", execution: {..., nodes: [...], nodeErrors: [...]}, path}`。`nodes` 是逐节点 status,`nodeErrors` 是失败节点清单。

### 单个节点的实际输入 / 输出

要确认"节点干对了"(而不只是"跑完了"),比如通知正文里到底有没有某段内容、HTTP 节点实际发了什么请求体:

```
python scripts/list_executions.py --execution-id <executionId> --node-io <nodeId 或节点显示名> [--max-chars 2000]
```

stdout 的 `nodeIo` 包含:`path`(该节点 input / output / error 的完整文件,Loop / Iteration 里多次执行都在 `runs[]` 里)、`preview`(截断预览)、`truncated`、`redacted`。

- `truncated: true` 时预览不是全文,要看全文就 Read `path`。
- 输出已经**脱敏**:webhook 地址、加签密钥、鉴权头、token 一律替换成 `***已脱敏***`。不要为了"看原值"去读未脱敏的完整响应,也不要把原值贴给用户。
- 节点这次没执行到时退出 1,并列出本次执行到的节点。
- **不要自己写临时脚本去解析落盘的执行记录**,用这个参数。

`--state` / `--session-id` / `--start-date` / `--end-date` 在详情模式下会报错退出 64。

### 回复用户时

- 用中文业务语言:"最近 <N> 次执行里 <X> 次成功、<Y> 次失败",不要贴原始 JSON 数组。
- 有失败记录时点出**时间 + 失败节点 + 错误摘要**。
- `total` 是该 flow 的全部执行次数;`returned` 只是本页条数,别混。
- 记录为空就直说"这个流程还没有执行记录",不要编。
- `state=INPROGRESS` 且 `pendingAction: true` 时,通常是停在 HumanInput 等人审批,不是卡死。

---

## 边界

- **不删、不改执行记录**:用户要删 → 说明本 Agent 不做,请在 linkfox-workflow 系统界面上操作。
- **不发布、不删除 flow**:执行能力不等于发布能力。
- **不绕脚本**:执行和查记录一律走这两个脚本,不临场拼 curl、不写 `/tmp/*.py`、不用 `python -c` 内联。
- 脚本 stdout 是唯一真相源。拿到就回复,**不要**再 Read 脚本源码、`ls scripts/` 或另跑一次"确认一下"。要权威状态就明确调 `--execution-id`。
