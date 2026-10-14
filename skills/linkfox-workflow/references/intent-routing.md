# 意图识别

## 判定顺序

先判断用户是否要生成或修改一份 linkfox-workflow agentflow v2 flow;再识别具体动作。不要因为出现"流程""步骤""自动化"等词就强制路由为 generate。

| 意图 | 典型表达 | 处理 |
|---|---|---|
| `generate` | "创建一个从用户提问到 RAG 回答的 flow" / "帮我做一个客服 agent" / "写一个每天定时抓数据的工作流" | 澄清缺失关键信息(触发方式/是否有人工审批/是否需要循环),生成计划并等确认 |
| `refine` | "在上一步的 flow 里加一个人工审批" / "把这个节点的 prompt 改成……" / "去掉 HTTP 节点" | 解析用户附带的 JSON,给差异并等确认 |
| `refine`(节点级) | 标签带 `nodeId`("这个节点改成…" / "把它的提示词换掉");前台"引用节点"功能带上来的 | 同 refine,但**改动面收窄到被引用节点及其联动项**,规则见 SKILL.md 的「节点级 refine」 |
| `explain` | "这个 flow 在做什么" / "解释一下这个 Condition 分支" | 按执行顺序自然语言说明,不产生新 JSON |
| `validate` | "帮我校验一下这个 JSON" / "这个 flow 有问题吗" | 跑结构校验,给问题列表 |
| `export` | "给我最终 JSON" / "输出" / "直接给结果" | 若已有确认过的计划,直接输出 JSON |
| `run` | "跑一下这个流程" / "执行一次" / "手动触发一次试试" / "帮我跑起来看看" | 取 workflowId,按 `runtime-execution.md` 调 `run_workflow.py` 真实执行一次 |
| `runs` | "看下执行记录" / "这个流程跑过几次" / "上次为什么失败" / "最近一次跑成功了吗" | 取 workflowId,按 `runtime-execution.md` 调 `list_executions.py` 只读查询 |
| `history` | "看下历史版本" / "刚才改了什么" / "谁改的这个流程" / "撤销刚才的修改" / "回到第 3 版" | 取 workflowId,按 `version-history.md` 调 `workflow_history.py`;查看纯读,还原先预览再 `--confirm` |
| `not_workflow` | "介绍一下 linkfox-workflow 系统" / "Retriever 节点原理是啥" / "写段代码给我" | 普通对话,不生成 flow |

当前会话已经有唯一 workflow 文件时,“继续改”“优化一下”“把名字改成…”均路由为 `refine`,沿用原文件名。只有用户明确说“新建一份”“另做一个”“保留原来的再生成”时才路由为新的 `generate` 并创建新文件。

## 触发方式识别

开始节点一律是 `BusinessStart`,它的 `startInputType` **只有四个合法值**(`formInput` /
`webhookTrigger` 只存在于已禁用的原生 `Start` 上,别再往这里路由):

- 用户描述"我需要时点一下就跑 / 手动触发":`chatInput`(默认。**无对话文本**,聊天面板是一枚
  「启动任务」按钮;下游读到的 `question` 恒为空串)
- 用户描述"每天 / 每周 / 每月定时跑":`scheduleInput`,同时问频率与时间。**没有 Cron 子模式**,
  只有可视化配置;需要 cron 表达式或"每次调度带一段默认文本"的场景本分支表达不了
- 用户描述"店铺有新订单 / 库存变了 / Listing 变了就跑":`storeAuthorization`,同时问监听哪类变化
  (五种:`listing` / `orderList` / `afterSalesOrder` / `fbaInventory` / `removalOrder`)
- 用户描述"多维表里加了一行 / 改了某个字段 / 某列变成 X 就跑":`tableRecordTrigger`,同时确认
  记录事件(新增 / 修改 / 满足条件)。**这一种有两个必须先跟用户讲清的前提**,见下

需要"用户填一个表单再跑"时不要路由到触发方式:`BusinessStart` 没有 `formInput`,
用 `chatInput` + 下游 `FillForm` 节点表达。

不明确时默认 `chatInput` 并说明"如需其他触发方式请告知"。

**以上默认值只用于从零 generate**。对话里带 `<linkfox-flow-info id>`(refine,含从多维表新建、画布上只有开始节点的首轮构建)时,触发方式**不是你来识别的**:fetch 基线里 BusinessStart 配的是什么就是什么,原样保留(见 SKILL.md「开始节点锁定」)。用户需求原文没提触发词,不等于"不明确、可以默认手动"。

### `tableRecordTrigger` 的两个前提(生成前必须说)

1. **记录触发必须由用户在 linkfox-workflow 系统界面上保存一次才会生效**。只经本 skill 上传的记录触发配置不会触发(事件来了静默不跑);事后在其他位置改配置也不会更新已有触发。
2. **`tableId` 留占位时,上传会被拒绝**(提示 `Data Table is required on the Start node.`)。
   所以触发表**由你查出来让用户选**:跑 `linkfox-smart-table` 的 `listMyTables`(必要时加 `listSharedTables`),把候选列给用户问"监听哪张表",选定后把 `notebookId` / `tableId` 写成真实 id 再生成(见 `SKILL.md`「选表」)。
   只有用户一张表都没有、或明确说表以后再绑时,才退到"先按 `chatInput` 上线、之后在 UI 上切成记录触发"。**这条退路只适用于从零 generate**;基线里已经配好记录触发(表已绑上)时,原样保留,不要降级成手动。

所以听到"表里数据一变就跑"时,先查表、问用户用哪张,再生成 ——
直接生成一份 `tableId: ""` 的记录触发 flow 会在上传那一步失败,`save_workflow.py` 也会先拦下。

## 节点级意图

- "让 LLM 挑工具、多步推理":Agent(必要时 + `agentTools[]`)
- "让 LLM 单次生成回复,不用工具":LLM
- "必须执行某个 tool / 调用某个已注册的插件":Tool
- "从知识库 / 文档库检索":Retriever
- "调用外部 REST API":HTTP
- "跑一段 JS 处理数据" / "等 N 秒":CustomFunction
- "跑一段 Python" / "用 pandas 统计" / "解析 PDF·Word·Excel·PPT" / 下游要按字段取结果:CustomPythonFunction(见 `nodes-integration-and-output.md`)
- "调用另一个 flow":ExecuteFlow
- "按值判断走不同分支(枚举/大小比较)":Condition
- "让 LLM 判断走哪个场景":ConditionAgent
- "等人工审批":HumanInput
- "对数组每一项跑一遍子流程":Iteration
- "重试到满足条件":Loop
- "直接给用户一段固定回复":DirectReply
- "给 Agent/LLM 定义结构化输出":`agentStructuredOutput` / `llmStructuredOutput`(字段,不是节点)

## 易混淆表达

- "分支":Condition(可枚举规则)vs ConditionAgent(自然语言判定)。不确定就问用户"分支条件是能用规则表达,还是需要 LLM 判断"。
- "循环":Iteration(遍历数组)vs Loop(跳回)。"逐条处理商品列表"= Iteration;"重试到成功"= Loop。
- "调用另一个流程":ExecuteFlow(调 linkfox-workflow 系统内部另一个 flow) vs HTTP(调外部 API)。
- "人工介入":HumanInput 只做"批准/驳回"决策;需要"上传附件、填资料"的场景用 `FillForm` 节点(`BusinessStart` 没有 `formInput`)。
- **"运行"分三种,别混**:
  - "跑一下 / 执行一次 / 手动触发一次 / 帮我跑起来看看" → `run`,真的执行一次(有副作用,见 `runtime-execution.md`)。
  - "这个流程怎么跑 / 怎么触发 / 能自动跑吗 / 上线后谁来调" → `explain`,回答触发方式和调用方式,**不要真跑**。
  - "跑成功了吗 / 跑过几次 / 上次为什么失败" → `runs`,查执行记录,不是再跑一次。
- **"记录"分三种**:"执行记录 / 运行历史 / 跑的日志" → `runs`;"历史版本 / 改动记录 / 谁改的 / 撤销修改 / 回滚到第 N 版" → `history`;"聊天记录 / 对话历史" 不在本 skill 范围,说明不支持即可。
- **"撤销 / 改回去"分两种**:要回到某个**已保存过的版本** → `history` 还原;要"把刚才加的节点去掉、其余保留后来的改动" → `refine`(在当前基线上删,不是还原)。分不清就问一句。
- `run` 和 `runs` 都要求已经有 workflowId(来自 `<linkfox-flow-info id="...">`)。用户是在同一轮里说"生成完直接跑一下"时,先走完 generate 的落盘上传,拿到 workflowId 再按 `run` 执行 —— 但要先提醒运行时对象还是占位。

## 短回复

- 上一轮有唯一待确认计划时,"继续"/"可以"/"确认"视为确认。
- 上一轮无待确认动作时,短回复不能触发 generate/refine,必须重新问目标。
- **短确认永远不能触发 `run`**。上一轮问的是"要不要执行"、用户答"可以/跑吧",那才是执行授权;上一轮问的是"要不要生成",短确认只授权落盘上传,不授权执行。分不清就再问一句。

## 置信度边界

- 高置信:需求包含明确起点(触发方式)、主线动作和终点。
- 中置信:描述了业务目标但没说触发方式/是否人工审批。先补一两个问题。
- 低置信:泛泛聊 linkfox-workflow 系统 / 询问节点原理 / 一次性代码请求。走 `not_workflow`。
