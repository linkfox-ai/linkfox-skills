---
name: linkfox-workflow
description: 用自然语言设计、修改、解释、校验 linkfox-workflow agentflow v2 工作流；用户确认生成或修改方案后，将合法 JSON 落盘并幂等上传到 linkfox-workflow 系统，返回 workflowId；用户明确要求时还能执行一次该工作流并查看它的执行记录。适用于“生成工作流”“修改 flow”“校验 agentflow”“上传/部署到 linkfox-workflow 系统”“跑一下这个流程”“看下执行记录/上次为什么失败”等请求；不发布、不删除 flow，不删改执行记录。
---

# linkfox-workflow Agentflow v2 生成器

## 响应预算(硬约束,减少 agent 空转)

- **每段 thinking ≤ 500 字**;不在 thinking 里枚举节点参数、默写 references 表格、反复自问"要不要再加个 sticky note"。参数以 `references/` 为准,拿到答案立刻推进。
- **每轮工具调用总预算 ≤ 8 次**(Write / Read / Bash 各算 1 次;`LinkfoxHTTP` 节点的业务接口查询不计入,见下一条)。典型 generate:Read SKILL.md(如未读)→ Read 3 个固定 references(`node-catalog` / `flow-structure` / `output-and-state`)+ 至多 1-2 个本轮用到的节点分类 → `rm -f` 旧 fragment → Write fragment → save_workflow → upload_workflow。**已读过的文件不重复 Read**;同会话连续第二轮 generate 通常 3-4 次;**refine 每轮固定多一次 `fetch_workflow.py`**(见「执行流程」第 5 步),约 4-5 次。
- **flow 里每出现一个 `LinkfoxHTTP` 节点,就必须对它单独做一次"业务接口查询"**(用 `scripts/query_tools_matrix.py`,**不要用 `curl` / `WebFetch`**;步骤见 `nodes-linkfox-custom.md`)。N 个 `LinkfoxHTTP` 节点就是 N 次独立查询,每个节点都要取出自己那个端点、核对 path/method/body。**用户规格里只列了 skill 名或 endpoint_path、没给完整请求体字段,也算"没给完整入参"**,同样要查。查完后 `body` 必须是按文档字段组好的真实 JSON,**不允许**把 `body` 落成占位 `"{}"` 上传。
- **节点级 refine(标签带 `nodeId`)通常 4-5 次**:fetch → 在基线里定位该节点并搜一次 `{{<nodeId>.output`(一次 Grep,**不能省**,漏了下游引用是该场景最常见的错)→ `rm -f` + Write fragment → save → upload。不重读节点分类 references(除非换节点类型),不通读整份基线 JSON。
- **`run` / `runs` 预算 ≤ 2 次**:Read `references/runtime-execution.md`(如未读)→ 跑一次 `run_workflow.py` 或 `list_executions.py`,拿到 stdout 直接回复。不读节点契约、不写 fragment、不跑 save/upload。
- **`history` 预算 ≤ 3 次**:Read `references/version-history.md`(如未读)→ `workflow_history.py`(查看 1 次;还原是预览 + `--confirm` 两次)。不 fetch、不写 fragment、不跑 save/upload。
- **上面的预算只管"拼 JSON + 落盘上传"和单次查看**。用户明确要求**调试 / 端到端验证 / 多轮迭代**时换一套规则:每一轮(改 → 存 → 传 → 跑 → 查)最多 15 次调用,而且每一轮都要得出一个可验证的结论,比如"断言 PASS"、"定位到某节点输入里缺某字段"。然后再决定要不要开下一轮。别为了凑预算省掉验证,也别在一轮里漫无目的地反复试。临时测试版的恢复(fetch + 恢复 + 上传)不计入这一轮。
- **同一 pattern 的 Glob / Grep 一轮内只出现一次**。
- **禁止读 linkfox-workflow 系统源码来推断字段**:节点 `data.name` / `data.type` / `inputs` / credential 字段名一律以本 skill 的 `references/` 为准;references 缺就补 references,不去猜源码。
- **不读上一次遗留的 `workflow.fragment.json`**:Write 前不 Read 该文件,直接覆盖写。
- **生成 / 修改阶段禁止 Read `scripts/` 下任何 `.py`**(包括 `workflow_spec.py` / `input_params_specs.py` / `save_workflow.py`):校验规则以 `save_workflow.py` **实际报的 `ERROR:` 行**为准。读完固定 references 后,下一步就是 Write fragment + 跑 save,**先写后改**,按报错逐条修。拿不准某个字段时也是先写一版让脚本说话,不要去源码里找答案——读校验器源码不会让片段更对,只会把预算耗光(会话 99b8c675:97 次 Read、0 次 Write)。
- **refine 不通读基线 JSON**:fetch 的 stdout 已给出节点数;要定位节点 / 下游引用用一次 Grep,不要按 offset 分块 Read 整份基线。没动的节点在片段里怎么写见「执行流程」第 5 步。

## 目标

把自然语言需求归一为一份**合法 linkfox-workflow agentflow v2 JSON**(顶层 `{description, usecases, nodes, edges}`)。只用 24 个节点(原生 15 + LinkFox 自定义 9;原生 Start 已弃用,开始节点一律用 BusinessStart);运行时对象(模型、凭据、Document Store、Vector Store、Tool credential、目标 flowId)一律留占位。用户确认后把 JSON 落盘并幂等上传到 linkfox-workflow 系统,由用户随后在 linkfox-workflow 系统中绑定运行时对象(`linkfoxAgentApi` 凭据除外——后台自动绑定,不要提示用户去页面上绑)。

## 按需读取参考(严格按需,未用到的分类禁读)

固定读三个:`references/node-catalog.md`(节点身份索引)+ `references/flow-structure.md`(顶层结构/edge/id 规则)+ `references/output-and-state.md`(各节点真实 output 字段 / `$flow.state` 读写 / 内置变量)。任何 generate/refine/validate 都要读,不能靠"这轮应该用不到"跳过 `output-and-state.md`(引用错字段运行时不报错也不替换)。`run` / `runs` 不属于此列,见本节末尾。

再按**本轮实际用到的节点**追加,没用到就**不读**:

| 本轮 flow 里出现 | 追加读 |
| --- | --- |
| Agent / LLM / Tool / Retriever | `references/nodes-ai-and-knowledge.md` |
| Condition / ConditionAgent / Loop / Iteration / HumanInput | `references/nodes-control-flow.md` |
| HTTP / CustomFunction / ExecuteFlow / DirectReply | `references/nodes-integration-and-output.md` |
| 任何 LinkFox 自定义节点(BusinessStart / CrossBorderExpert / DataReader / FillForm / SendNotification / WriteFile / **LinkfoxHTTP** / **End**) | `references/nodes-linkfox-custom.md` |
| **异步任务接口**(AI 生图/生文/生视频等 `/aigc/*Async`,以及任何"创建只回 `taskId`、结果要另查"的接口) | `references/nodes-linkfox-custom.md` 的「异步任务接口」一节 **+ 必须追加 `references/nodes-integration-and-output.md`(CustomFunction 当延时节点)和 `references/nodes-control-flow.md`(Condition / Loop)** |
| 字段含 `{{...}}`,**且**该节点的 `inputParams` 要你自己写(Agent / LLM / Tool / Retriever / ConditionAgent / ExecuteFlow / Loop / Iteration / DataReader / DirectReply) | `references/variable-substitution.md`(管"字段要不要标 `acceptVariable`") |

> `inputParams` 由脚本代填的节点(见「`inputParams` 交给脚本」一节)不需要为此读 `variable-substitution.md`。

按需读:意图分类模糊读 `references/intent-routing.md`;不清楚 lifecycle 动作读 `references/lifecycle-actions.md`;不清楚"要不要单独求确认"读 `references/confirmation-policy.md`;不清楚回复格式读 `references/response-contract.md`;不清楚会话边界读 `references/chat-runtime-contract.md`。**已经知道就不重复 Read。**

`run` / `runs` 固定读 `references/runtime-execution.md`,**且只读它**,上面三个固定项一个字都不用读。`history`(查看 / 对比 / 还原历史版本)同理,只读 `references/version-history.md`;`automation`(启停 / 查看多维表自动化)只读 `references/table-automation.md`。flow 含记录触发(`tableRecordTrigger`)的 generate / refine 追加读 `references/table-automation.md` §1–§2(上传后怎么回报关联结果、字段 ID 怎么写);含**挂在多维表下的定时启动**(`scheduleInput` + `linkfoxTableAutomationContext`)的追加读 §1–§1.5。

**一轮 generate 追加的 references 上限 4 个**(不含 SKILL.md 与三个固定项);超过就说明选错了参考,回头判断意图。

## 执行流程

1. **识别意图**:按 `intent-routing.md` 分类为 `generate` / `refine` / `explain` / `validate` / `export` / `run` / `runs` / `history` / `automation` / `not_workflow`,看完整语义不只靠关键词。**`run` / `runs` / `history` / `automation` 不生成 JSON**,识别到就直接跳到第 7 / 第 8 / 第 9 / 第 10 步,不读节点契约、不写 fragment、不跑 save/upload。
2. **`not_workflow`**:走普通对话,不强行生成 flow。
3. **`explain` / `validate`**:直接执行,不需要确认。validate 把 JSON 写成临时文件后跑 `save_workflow.py --content-file <临时文件> --dry-run`。它做完整的补齐和校验,但不写文件、不动门禁。按退出码和 `ERROR:` / `warnings` 分 error / warning 输出,再按 `lifecycle-actions.md` 的清单补充脚本查不到的语义问题。不修改用户贴来的 JSON。**dry-run 只给 validate 用**,generate / refine 直接正式保存。
4. **`generate`**:先判断需求是否足够明确,参考 `confirmation-policy.md`。
   - **需求明确**(用户点出具体节点组合、"最简"流程、"不用 AI/API"、明确输入输出,或已在催"立即生成/不要再问"):**当轮直接执行**。用 1-3 句自然语言宣布方案(起点、主线、结束、关键 prompt 简述),按 `flow-structure.md` 生成 JSON、自修、走"落盘与上传流程"、回复结果。不再问"是否确认"。
   - **需求含糊**(触发方式、AI/知识库/外部 API 都没说,或只有模糊目标):按 `needs_input` 一次问 1-2 个具体问题,或展示自然语言方案并请求确认;确认前不输出 JSON、不落盘。
   - 挑节点原则:业务动作 → 匹配 24 个节点之一 → 决定分支/循环/迭代结构;涉及店铺事件/业务定时/邮件飞书钉钉通知/跨境专家/多维表/CSV/Excel 时**优先用 LinkFox 自定义节点**,不用 HTTP + CustomFunction 手工模拟。**涉及模型/AI 推理优先用 `CrossBorderExpert`,不默认生成原生 `Agent`/`LLM`/`ConditionAgent`**;只有确实依赖 Tool 调用、RAG 知识库检索、Structured Output,或需要节点内动态语言分支判断时才用这三个原生节点兜底,并在方案里点出兜底原因(`Tool`/`Retriever` 不受此限)。先按 `node-catalog.md` 路由,再读已选节点分类说明。
   - 生成 JSON 前自查(节点选型、连线拓扑、`{{ }}` 引用路径、prompt 内容),样板字段交给脚本补;然后按"落盘与上传流程"执行,`save_workflow.py` 报 error 就照 stderr 逐条修后重跑。
5. **`refine`**:
   - **唯一身份是 `workflowId`,不是文件名**。拿到 workflowId 后,所有落盘/上传都用它定位,不必记本地路径。
   - **先看对话里有没有 `<linkfox-flow-info id="<workflowId>">`**:有则用户要改的是**已在 linkfox-workflow 系统上的** workflow。**标签带 `nodeId` 属性时是节点级 refine**,见「节点级 refine」。**每轮 refine 都先调 `scripts/fetch_workflow.py --workflow-id <id>`** 拉回服务端真实 flowData 作为改动基线,再 `save_workflow.py --workflow-id <id>` 原地覆盖、`upload_workflow.py --workflow-id <id>` 更新同一 flow。**不重走首次创建流程,不另存副本。**
   - **不要因为"本地已经有 `workflow.fragment.json`"就跳过 fetch**:那份不含用户在界面上手工调过的 `position`,也不含用户补填的 credential / model / documentStore;拿它当基线会冲掉这些改动。
   - **本地文件只是基线的缓存**。`fetch_workflow.py` 每次都重新拉取并覆盖本地文件;stdout 的 `reusedLocalFile: true` 只表示复用了同一个文件名/路径(basename 就是 sourceKey,不能变),不代表复用旧内容。门禁兜底:本轮没 fetch 过、或 fetch 下来的本地文件已被改动,`save_workflow.py --workflow-id` 会拒绝落盘。拿到门禁报错就去 fetch,不绕过脚本手写文件。
   - **`save_workflow.py` 返回 `layoutNotes` 时要当回事**:说明基线里有节点没带 `position`,基本等于漏了 fetch,先 fetch 重来,不要继续上传。首次生成时出现则提醒用户画布是自动排版的、可自行拖动。
   - 没有标签时:优先复用当前会话上一轮 `upload_workflow.py` stdout 里的 `workflowId`。既没有 workflowId、又无法唯一确定是哪个 flow 时,问用户一句要改哪个流程,不按路径猜、不退化为新建文件。用户贴来的 JSON 只够 explain / validate;要改线上 flow 仍需 workflowId。
   - 只改用户指定的部分,其余(位置、label、已填 inputs 值)一字不动。
   - **片段怎么写(省掉手抄基线)**:`save_workflow.py --workflow-id` 会按节点 id 把基线里的字段补回片段中**缺失**的键,所以:
     - **没动的基线节点**(含开始节点)只写 `{"id": "<原 id>", "data": {"name": "<原 data.name>"}}`。`position` / `width` / `height`、`data.id` / `type` / `label` / `description` / `inputs` / `credential`,以及手写类节点(Agent / LLM / DataReader 等)的 `inputParams`,脚本都从基线拷回。锚点、`version` 等样板照常由 `data.name` 推导。stdout 的 `inheritedFromBaseline` 是补回的字段数。
     - **要改的基线节点**:只写要改的那个键,其余照样省略。注意粒度是**整个键**:写了 `inputs` 就是整份 `inputs` 以你写的为准,基线里的其他 inputs 字段不会合并进来,所以改 inputs 时要把这个节点的 inputs 写全。
     - **新增节点**:按 generate 的写法写(样板与代填类 `inputParams` 照常省略)。
     - 要删的节点从 `nodes` 里去掉即可。`edges` 写完整的最终列表(edge 不从基线补)。
     - 只有片段里**没写**的键才会补。写成 `""` / `{}` 也算写了,不会被基线覆盖。所以别用空值占位来表示"保持原样",省略那个键就行。
   - 增/删节点时同步维护 edges;新增节点用 `<data.name>_<现有最大 index + 1>`。**基线里已有的节点 id 一律原样保留**(画布上建的节点后缀是随机数,别"归一化"成 `_0` / `_1`:改 id 等于删旧建新,edge 和下游 `{{ }}` 引用会一起失效)。
   - 展示差异,然后自修、按"落盘与上传流程"执行,回复完整 JSON + 本次实际改动清单。
6. **`export`**:输出上一轮已确认的计划,直接按"落盘与上传流程"执行后输出 JSON、配置指引与 workflowId 标签。
7. **`run`**(用户明确要求执行一次;细节见 `references/runtime-execution.md`):
   - 从对话里的 `<linkfox-flow-info id="<workflowId>">` 取 workflowId;取不到就问,不猜。**不需要 fetch**。
   - **执行有真实副作用**(SendNotification 发通知、WriteFile 写表、LinkfoxHTTP/HTTP 打接口)。含这些节点时先一句话点出实际动作,用户已说"直接跑/我知道"就不再问。
   - 脚本执行前会按本 flow 用到的节点查必需资源(模型 / 表 / 店铺 / 专家 / 子流程 / 通知机器人;`linkfoxAgentApi` 凭据后台自动绑定,不查)。有缺口就**退出 66、不执行**,把 stdout 的 `missing` 按"节点 → 缺什么"转述给用户。用户明确坚持带缺口试跑时才加 `--skip-preflight`。
   - 用户要"测一下 / 验证一下"时,带上 `--expect-reached <nodeId>` / `--expect-not-reached <nodeId>`,写明这次预期走哪条路。
   - `python scripts/run_workflow.py --workflow-id <id>`,按 stdout 如实回报。**`runStatus` 不是 `FINISHED` 就不许说"执行成功"**;`nodeErrors` 非空时逐条转述节点名 + 错误。**`FINISHED` 也不等于业务通过**:`businessCheck=FAIL`、`notReachedNodes` 里有必须发生的动作、`actionResults` 有 `status=error`,三者任一出现都要如实说明。
   - 为测分支或非手动触发临时改 flow 时,测完必须恢复并重新上传,按 `references/runtime-execution.md` 的「临时测试版与恢复」执行。
   - **禁止在 generate / refine / export 上传成功后"顺手跑一次验证"**。
8. **`runs`**(查看执行记录;纯读,不需要确认;细节见 `references/runtime-execution.md`):
   - 列表 `python scripts/list_executions.py --workflow-id <id> --limit <Number>`;要看某次细节再加 `--execution-id <executionId>`。
   - 用中文业务语言汇总(成功/失败次数、时间、失败节点 + 错误摘要),不贴原始 JSON 数组。记录为空就直说还没有执行记录。
9. **`history`**(历史版本:查看 / 对比 / 还原;细节见 `references/version-history.md`):
   - "看下历史版本 / 刚才改了什么 / 谁改的" → `python scripts/workflow_history.py list|show|diff --workflow-id <id> ...`,纯读。
   - "撤销刚才的修改 / 回到第 N 版" → 先 `restore --version <N> --expect-latest <M>` 预览、转述 `willChange`,用户同意再加 `--confirm`(`--expect-latest` 换成预览 stdout 的 `latestVersion`)。"撤销刚才的修改"的 N / M 就是上一轮上传 stdout 里的 `history.previousVersion` / `history.version`;对话里没有就先 `list` 让用户选,不猜。
   - **退出 69 = AI 改完之后又有人保存过**:不还原,把 stdout 的 `newerVersions`(谁、何时、改了哪些节点)转述给用户,问要一起撤掉还是只撤 AI 那次。不许把 `--expect-latest` 改成最新值硬过检查。
   - **只有属主能还原**(退出 68);不要用 `save_workflow.py --restore-from` 或手工重放 JSON 绕过。
   - 还原成功后不贴 JSON,**最后一行输出 flow info 标签**(画布靠它重新拉取,不输出画布就停在旧内容上,用户再点保存会把还原冲掉);只预览或失败时不输出。下一轮 refine 照常先 fetch。
10. **`automation`**(多维表自动化启停 / 查看;细节见 `references/table-automation.md` §3):
   - "停用 / 关掉 / 暂停自动化" → `python scripts/table_automation.py set --workflow-id <id> --enabled false`;"重新打开" → `--enabled true`。用户原话就是授权,可逆,不另外确认;`--enabled` 永远显式带。
   - "自动化开着吗 / 这张表挂了哪些流程" → `list --workflow-id <id>` / `by-notebook --notebook-id <nbk> --table-id <tbl>`,纯读。
   - 请求体由脚本从服务端开始节点推导,**不手写 curl、不手填表 / 条件 / 字段 ID**;换表、换事件、改条件、补字段 ID 走 refine 开始节点。
   - **定时任务不经 `set`**:它的启停在画布顶部排期开关,订阅的 `enabled` 管不了排期,脚本退出 66;回复里引导用户去关开关,或 refine 改成手动启动。
   - 按退出码回报:0 看 `tableSync.status`;66 推不出订阅 / 是定时任务;68 被拒(别的成员绑定 / 无表权限);70 已保存但没生效。不输出 flow info 标签(画布没变)。
   - 预算 ≤ 2 次:Read `references/table-automation.md`(如未读)→ 一次脚本。

## 从 `<linkfox-flow-info>` 恢复已有 flow(refine 前置)

对话历史出现 `<linkfox-flow-info id="<workflowId>">` 时,该 `id` 就是 refine 的目标 workflow。标签可能带 `nodeId` 属性(前台"引用节点"功能),那是**节点级 refine**,见「节点级 refine」。

```
<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>
<linkfox-flow-info id="<workflowId>" nodeId="<nodeId>"></linkfox-flow-info>
```

取值规则:

- **按属性分别抓,不要整体匹配整个标签**:`id` 用 `id="([A-Za-z0-9_-]+)"`,`nodeId` 用 `nodeId="([A-Za-z0-9_]+)"`。**不要**用"`id` 后面必须直接是 `>`"的写法,带 `nodeId` 的标签会整条匹配不上。
- 只有一个 `id` → 直接使用;多个 → 取用户本轮明确引用的那个;都不明确时反问。
- `id` 只由 linkfox-workflow 系统生成,不可猜、不可从文件名反推。
- `nodeId` 是节点的顶层 `id`(与 `data.id` 相同)。画布上新增节点的后缀是随机数,不要当成顺序号,也不要归一化成 `_0` / `_1`。

拿到 id 后**先 fetch,再进入正常的落盘/上传流程**:

```
Bash(
  command="python scripts/fetch_workflow.py \
    --workflow-id <id> \
    --slug linkfox-workflow-<english-slug>"
)
```

- 认证与 `upload_workflow.py` 一致(只用 LinkFox API Key,不用系统内部 API Key)。
- stdout 返回 `{path, workflowId, name, flowType, bytes, nodes, edges, mode: "fetched", baselineSource: "server", fetchedAt, reusedLocalFile}`。该 id 之前已绑定过本地文件时,`path` 就是原来那个文件,`reusedLocalFile: true`(只指路径复用,内容永远是这次拉回来的)。
- 此后该 workflowId 的所有 refine 都走 `save_workflow.py --workflow-id <id>` 原地覆盖 + `upload_workflow.py --workflow-id <id>` 更新同一 flow,**禁止**为同一 workflowId 另建文件、换 slug/文件名。
- **每轮 refine 都要重新 fetch**。上一轮的本地文件已过时,且 `save_workflow.py` 落盘成功后会作废 fetch 留下的凭据,拿旧文件接着改会在门禁处被拒。重复 fetch 幂等,不会造出第二份 workflow。
- fetch 本身不修改 linkfox-workflow 系统上任何数据;展示 refine 计划后,按确认策略决定是否落盘上传。
- fetch 失败(404、非法 flowData、网络失败)如实反馈,不偷偷退化为"新建 workflow",也不改用本地旧副本硬改。

## 开始节点锁定(refine 时 BusinessStart 触发配置原样保留)

**基线里的 BusinessStart 是用户配好的,不是你推断出来的。** refine(含"画布上只有开始节点、让 AI 把后面的步骤补上"的首轮构建)时,开始节点的 `id` / `data.inputs` 全部字段 / `data.credential` 与 fetch 基线保持一致,只允许改 `label` / `description`。**最省事也最不容易错的写法**:片段里开始节点只写 `{"id": "<基线开始节点 id>", "data": {"name": "businessStartAgentflow"}}`,`inputs` / `credential` 整个省略,`save_workflow.py` 会从基线拷回。不要通读基线去手抄这两个字段。

典型场景是**从多维表新建工作流**:界面先建好一条只有开始节点的流(记录触发、选好了表和条件),再把用户需求加上 `<linkfox-flow-info id="<workflowId>">` 发给你。这时:

- **走 refine,不走 generate**:先 fetch,在基线上补下游节点,`--workflow-id` 落盘上传。不新建流程。
- **不要套用"没说触发方式就默认手动"**:该默认值(`linkfox-workflow-prompt-compiler` 的推断规则、`intent-routing.md` 的"先按 `chatInput` 上线")**只适用于从零 generate**。基线已有触发配置就原样继承,哪怕用户需求没提触发。
- **不要因为 `tableId` / `notebookId` 已有真实值、或带着不认识的 `linkfoxTableAutomation*` / `formInputTypes` 字段就"规范化"它们**:那是界面写进去的订阅上下文,删了触发就断了。表格入口建出来的流 `startInputType` 可能是 `formInput`(配合 `linkfoxTableAutomationTrigger`),同样原样保留,不改成 `tableRecordTrigger` 或 `chatInput`。
- **下游必须消费"这次变的那一行"**:记录触发流用 `{{<startId>.output.recordEvent.recordByName.<字段名>}}` / `.output.rows`,或开始节点直连 WriteFile;`startInputType=formInput` 的表格入口流用 `{{$form.recordJson}}` / `{{$form.recordId}}`。**不要**读 `<startId>.output.question`(恒为空串),**不要**插 FillForm 让人手填本该来自触发记录的数据。

**脚本硬拦**:`save_workflow.py --workflow-id` 会把新片段的开始节点和基线逐字段比对,`inputs` / `credential` / 节点 id 有任何差异就 exit 65,stderr 逐条列出改动。看到这个报错,就把片段里开始节点的 `inputs` / `credential` 删掉(让脚本从基线补)再重跑,**不要**带 `--allow-trigger-change` 过门禁。

**只有用户本轮原话明确要求换触发方式或改触发条件**("改成<触发时间>跑""换成监听另一张表""条件改成<条件>")时,才带 `--allow-trigger-change`。放行后 stdout 会带 `triggerChanges`,回复里必须逐条告诉用户触发配置变了什么;改的是记录触发时,上传会按新配置重新登记订阅,按 stdout 的 `tableAutomation` 告诉用户新配置有没有生效(见 `references/table-automation.md`)。

## 选表:先查用户的表,再问用哪张(不要留空让用户自己配)

流程里只要有**要选多维表的槽位**——`BusinessStart` 记录触发(`tableRecordTrigger`)、`DataReader`(`sourceType=linkfoxTable`)、`WriteFile`(`linkfoxTable` / `updateLinkfoxTable`)——就**由你把表选好**,不要把 `notebookId` / `tableId` 留 `""` 再说一句"上传后请在界面上选表"。那是缺陷 #7130931254 记录的偷懒:用户的表一查就有,让他去界面上两级下拉自己找,是把本该你做的活推给用户。

1. **列出用户的表**:`python ../linkfox-smart-table/scripts/smart_table.py listMyTables '{}'`;没找到或用户说是别人共享的,再跑 `python ../linkfox-smart-table/scripts/smart_table.py listSharedTables '{}'`。出参两层:数据表在 `notebooks[].tables[]` **和** `looseTables.tables[]` 两处,顶层 `notebookId`(`nbk…`)是容器、不是表。
2. **反问用户用哪张**(这是 `needs_input`,本轮不落盘):
   - 用户需求里点了表名、且按名字**唯一命中**:直接用,在方案里写一句"读/写的是「<多维表格>/<数据表>」",不再问。
   - 命中多张同名表、或用户没说表名:把候选列成"多维表格 / 数据表 / 创建时间"让用户挑,**一次问完流程里所有槽位**(例如"触发用哪张表、写回哪张表"),不要一个槽位问一轮。
   - 一张表都没有:问用户是要先建一张(`WriteFile` 用 `newLinkfoxTable` 让流程自己建),还是表以后在界面上选。
3. **写真实 id**:`notebookId` 填数据表所在容器的 `nbk…`(散表填 `__loose__`),`tableId` 填 `tbl…`。两级都要写。
4. **字段名用真表头**:要引用 `recordByName.<字段名>`、或给 `WriteFile` 拼写入字段时,先跑 `python ../linkfox-smart-table/scripts/smart_table.py listFields '{"tableId":"tbl…"}'` 拿表头,不要猜字段名;`isComputed` 的列写不进去。

**脚本硬拦**(规则与后端对齐):`save_workflow.py` 遇到下面任一情况就 exit 65,stderr 点名是哪个节点、缺什么:
- 任何选表槽位 `tableId` 为空,或是 `tbl__…` 占位值(后端不认它是真实表);
- `tableId` 不以 `tbl` 开头(多半是把 `nbk…` 填到了第二级);
- **记录触发缺 `notebookId`**:后端保存会成功,但登记不到多维表侧,触发永远不跑。

读表 / 写表缺 `notebookId`、或 `notebookId` 不是 `nbk…` / `__loose__` 只给 warning:后端不校这一级,运行时只认 `tableId`。

**只有用户本轮明确说"表以后自己在界面上选 / 先不绑表"**时才带 `--table-later` 放行;stdout 的 `tableLater` 列出还空着的槽位,回复里逐个点名让用户去配。不要因为"查表麻烦"自己替用户做这个决定。

refine 时:基线里**已选好**的表原样保留(开始节点锁定照旧);基线里本来就空着、这一轮也没动的槽位不拦,脚本只给一条 warning,在回复里顺带问一句要不要现在选;基线里空着的触发表这轮由你按用户挑的表填上,不算"换触发",不需要 `--allow-trigger-change`。

## 节点级 refine(标签带 `nodeId`)

标签带 `nodeId` 时,用户只想改画布上点中的那一个节点。**改动面收窄到"被引用节点 + 因它而必须联动的地方",其余一个字符都不动。**

流程与普通 refine 相同(每轮先 `fetch_workflow.py` → 改 → `save_workflow.py --workflow-id` → `upload_workflow.py --workflow-id`)。上传的是整份 flowData,"只改一个节点"约束的是改动面;没有"只推一个节点"的方式,不要发明。

**第一步:在 fetch 回来的基线里定位该 `nodeId`。** 找不到就**直接说"这个流程里没有 `<nodeId>` 这个节点,确认一下是不是要改别的"并停下**,不按 label 猜、不退化成整流程 refine。找到后搜一遍 `{{<该 nodeId>.output`,列出所有引用它的节点,那就是本次允许的联动范围。

**允许改的**:

- 被引用节点自己的 `inputs` / `label` / `description`。
- 联动项(仅在确实被牵连时改):
  - 该节点**输出字段名变了**(如 `DataReader` 的 `outputVariableName`、`FillForm` 的表单字段名、`Agent`/`LLM` 的 structured output key),下游 `{{<该 nodeId>.output.<旧字段>}}` 必须同步改。
  - 该节点**换了类型**(如 `LinkfoxHTTP` 改成 `HTTP`):它自己的 `data.name` / `type` / 锚点和相连 edge 的 `sourceHandle` / `targetHandle` / 颜色要一起改;nodeId 前缀要跟着变(校验前缀等于 `data.name`),下游引用同样要改。这是结构性改动,按 `confirmation-policy.md` 先确认。
  - 用户明确要求"在它后面加一步"时新增的节点和 edge。

**禁止碰的**:

- 其它任何节点的 `inputs`。
- 所有节点的 `position`(含被引用节点自己)。
- 用户在界面里补填的 `credential` / model / `documentStore` 等运行时对象。
- 与本次改动无关的 edge。
- **"同类节点全扫"在节点级 refine 下不生效**。用户点名其中一个节点,就只改那一个;其余同类节点的同类问题**写在回复里提示用户**,等他说了再动。**例外**:脚本报 error 拒绝落盘时仍要全修(不修就传不上去)。

**联动范围要搜出来,不要凭感觉判断"应该没影响"**(漏改的下游引用运行时不报错,用户看到的是字面量 `{{ ... }}`)。

**回复要点出改动面**:一句"本次只改了 <节点 label>";有联动就接一句"因它的输出字段改名,连带更新了 <下游节点> 的引用";没有联动就明说"仅改动 1 个节点,其余节点与连线未变"。最后一行的标签**只带 `id`、不回带 `nodeId`**。

## `inputParams` 交给脚本(省掉近四成 JSON)

`inputParams` 是**字段元数据**(label / type / options / acceptVariable),不是字段值(值在 `inputs` 里)。同一种节点的这份元数据永远一样,和 `version` / `color` / `outputAnchors` 同类,由 `data.name` 推导。

**下面这些节点:整个 `inputParams` 字段别写**,`save_workflow.py` 落盘时自动代填(补了会列进 `normalized`;模板不用读):

| 节点 | 备注 |
| --- | --- |
| BusinessStart / FillForm / CustomFunction / CustomPythonFunction / CrossBorderExpert / SendNotification / WriteFile / End | 固定形状 |
| Condition | 固定形状,含完整 `operation` 枚举 |
| LinkfoxHTTP / HTTP | `body` 字段形状随 `inputs.bodyType` 自动挑(`json`/`raw` → string 版;`formData`/`xWwwFormUrlencoded` → array 版) |
| HumanInput | **仅 `humanInputDescriptionType: "fixed"`**;`dynamic` 分支要自己写 |

**其余节点仍要自己写完整 `inputParams`**:Agent / LLM / Tool / Retriever / ConditionAgent / ExecuteFlow / Loop / Iteration / DataReader / DirectReply / StickyNote。漏了会被 error 拦下。

两条边界:

- **`[]` 不等于省略**。显式写成空数组脚本不代填,`validate` 直接报 error。要代填就整个 key 别出现。
- **`acceptVariable` 只补布尔、不补字段**。字段已在 `inputParams` 里声明、值里确实有 `{{ }}`、只漏了 `acceptVariable: true` → 脚本自动补(仅 `string` / `array` / `json` 类型;`options` / `password` / `number` 里出现 `{{ }}` 是填错字段,仍报 error)。字段**整块没声明**也是 error。

## 落盘与上传流程(generate / refine / export 强制)

用户确认之后,禁止只在对话里贴 JSON;必须先落到会话 workspace,再上传到 linkfox-workflow 系统,最后返回路径 + JSON + 配置指引 + workflowId 标签。用户没显式说"上传"也照走。

**Step A** — Write JSON 片段到临时文件

**先删掉可能残留的旧片段,再 Write**,两步在同一轮里连着发:

```
Bash(command="rm -f ./workflow.fragment.json")   # 忽略退出码,文件不存在也正常
Write ./workflow.fragment.json                   # 内容:纯 JSON,顶层 {description, usecases, nodes, edges}
```

必须先删:Write 对已存在的文件强制 read-before-write,不删会失败一次并迫使整份 JSON 重发。

禁止把 JSON 塞进 Bash `command` 参数、shell 变量、`python -c` 内联。**永远 Write 落文件 + `--content-file` 传路径**。

**不要 Read 已存在的 `workflow.fragment.json`**:它是上一轮的中间产物,不是会话状态。先删再写,别解析它、别和它做 diff。当前 workflow 的唯一权威副本是 Step B 落盘后的那份。

**Step B** — 调 `scripts/save_workflow.py` 落盘

首次创建 workflow(当前会话还没有该流程的已保存路径,或用户明确要求新建另一份流程):

```
Bash(
  command="python scripts/save_workflow.py \
    --content-file ./workflow.fragment.json \
    --slug linkfox-workflow-<english-slug>"
)
```

后续修改同一 workflow(refine/export/继续对话修改)—— **一律用 workflowId**:

```
Bash(
  command="python scripts/save_workflow.py \
    --content-file ./workflow.fragment.json \
    --workflow-id <上一次 fetch / upload 返回的 workflowId>"
)
```

`--existing-file` 已移除;拿不到 workflowId 时按第 5 步规则问用户一句,不猜文件。

**三类文件各管各的**(容易混,写清楚):

| 文件 | 角色 | 能不能改 |
| --- | --- | --- |
| 索引绑定的 workflow 文件(fetch / save 返回的 `path`) | 基线 + 落盘目标;basename 就是 sourceKey | **不要直接改**。改了 `--workflow-id` 门禁会拒绝落盘;只通过 save_workflow.py 覆盖 |
| `workflow.fragment.json` 或任意临时副本 | 承载本次改动 | 随便改;可以先把 fetch 回来的内容拷一份进来再改 |
| `--content-file` | 只是内容来源,可以指向任意路径 | 传 fragment 的路径 |
| `workflow-snapshots/<id>/snapshot-*.json` | fetch 时留的服务端原文,**只给临时测试版恢复用** | 不要改;只喂给 `--restore-from`。用户要"撤销 / 回到第 N 版"走服务端历史(`workflow_history.py`),不用它 |

"不得另存副本"约束的是**落盘目标路径**(它决定 sourceKey),不是 `--content-file` 从哪里读。

`--workflow-id` 带**基线门禁**:该 workflowId 绑定的本地文件必须是**刚由 `fetch_workflow.py --workflow-id <同一个 id>` 拉下来、之后没被改动过**的服务端原文。不满足就退出 64,stderr 会给出该跑哪条 fetch 命令。落盘成功后凭据作废,**下一轮想再改仍要先 fetch**。该 id 从没绑定过本地文件时同样报错退出 64(不会悄悄新建),此时先跑 `fetch_workflow.py --workflow-id <id>`。

同步/前台调用(不要 `run_in_background`)。`--slug` 只允许首次创建新流程时使用,必须以 `linkfox-workflow` 开头;`--slug` 与 `--workflow-id` 互斥。已存在的 workflow 必须原地覆盖,即使展示名、业务标题或需求描述变了也不得改文件名(**文件名就是 sourceKey,换名字 = 造出新 workflow**)。stdout 返回:

```json
{
  "path": "/.../linkfox/<YYYY-MM-DD>/<session>/data/<slug>-<ts_us>.json",
  "bytes": <Number>,
  "nodes": <Number>,
  "edges": <Number>,
  "mode": "created | updated",
  "workflowId": "<该文件已绑定的 flowId,未绑定时该字段不出现>",
  "normalized": ["<脚本代填的样板字段,没有代填时该字段不出现>"],
  "warnings": ["<不阻塞落盘的提示,没有时该字段不出现>"]
}
```

脚本会做三件事:

1. **补齐样板字段(normalize)**。节点的顶层 `type`、`position` / `positionAbsolute`、`data.version` / `color` / `baseClasses` / `category` / `inputAnchors` / `outputs` / `outputAnchors`、**大部分节点的 `data.inputParams`**,以及 edge 的 `type` / `id` / `data.sourceColor` / `targetColor` / `isHumanInput` / `edgeLabel`,全部由 `data.name` 推导,**可以直接省略**,补了什么会列在 stdout 的 `normalized` 里。你只写有语义的部分:`id` / `label` / `name` / `data.type` / `description` / `inputs`,以及 edge 的 `source` / `sourceHandle` / `target` / `targetHandle`。
   - 已经写了但与 spec 不一致的值**不会**被改写,而是由校验报 error/warning。
   - 显式写成 `[]` 的 `outputAnchors` / `inputParams` 不算"缺失",不会被补;想让脚本代填就整个字段别写。
   - `inputParams` 的代填范围见「`inputParams` 交给脚本」一节。
   - `acceptVariable` 的自愈边界见同一节。
2. **骨架 + 深度校验**。顶层 4 字段;三位一体 id;锚点形状与 edge 绑定;连通性;节点身份字段、`{{ }}` 变量的 `acceptVariable` 标记与引用目标、裸 `.output`、Condition 的 `operation` 枚举、Iteration 父子关系、HumanInput 出边标记。**error 拒绝落盘,warning 只提示**。
3. **原子落盘**。首次创建落到会话 `data/`;修改时先验证本地文件确实是本脚本生成的 workflow、且仍是本轮 fetch 下来的服务端原文,再原子覆盖同一路径,并作废 fetch 凭据。

**退出码**:0 成功;3 片段为空;4 写盘失败;64 CLI 用法错 / `--workflow-id` 门禁未通过(基线不是服务端原文);65 JSON 非法 / 骨架不合规 / 深度校验有 error。非 0 时读 stderr 里的 `ERROR:` 行逐条修,别静默继续、别绕过脚本手写文件。

stdout 里的 `warnings`(若有)要在回复里如实转述一句。

**深度校验里的两条运行时提示(warning)**:
- Condition 比较值引用了 `CustomPythonFunction` 的 `output.result`:已观察到布尔值传入 Condition 时报 `output.replace is not a function`。已验证可行的写法是让 Python 把该字段转成字符串后再比较。不要因此把所有输出都改成字符串。
- 互斥分支汇合:同一个分支节点的不同出口汇到同一个节点。已观察到这种汇合节点运行时没被执行。必须发生的动作建议每个分支各接一份,或执行时用 `--expect-reached` 核对。根因还没定位,所以只提示、不禁止。

**Step C** — 幂等上传到 linkfox-workflow 系统

**上传门禁(脚本强制)**:只能上传**最近一次 `save_workflow.py` 成功落盘、之后没被改动过**的文件。以下情况一律退出 65,且不发任何网络请求:
- 最近一次保存失败(校验 error、门禁拒绝、写盘失败)。
- 文件保存后又被手动改过。
- 文件根本没经过保存脚本。

看到 65 就回去把 Step B 跑到退出码 0。**不要上传旧文件,也不要接着执行**。

使用 Step B 返回的绝对路径调用:

```
Bash(
  command="python scripts/upload_workflow.py \
    --content-file <Step-B-path> \
    --name '<workflow-display-name>' \
    --flow-type AGENTFLOW"
)
```

修改任何**已经在 linkfox-workflow 系统上存在的 workflow** 时,都追加 `--workflow-id`:

```
Bash(
  command="python scripts/upload_workflow.py \
    --content-file <Step-B-path> \
    --name '<workflow-display-name>' \
    --flow-type AGENTFLOW \
    --workflow-id <fetch 时的 workflowId>"
)
```

- **`--name` 首次创建必填**:它就是用户在 linkfox-workflow 系统列表里看到的名字,用业务语言写,不拿文件名或 slug 顶替(脚本不回退到文件名)。带 `--workflow-id` 更新时可以省略,脚本沿用索引里上次的展示名,stdout 带 `nameReused: true`。要改名就显式传新的 `--name`。
- 上传脚本不接受自定义 `sourceKey`;它强制使用 Step B `path` 的真实 basename(含 `.json`)。换文件名 = 换 sourceKey = 产生新 workflow。唯一身份始终是 workflowId。
- 传了 `--workflow-id`:脚本先校验 flow 存在再更新;flow 不存在则报错,不自动创建。
- 没传 `--workflow-id`(首次创建,或没记住 id):脚本依次按服务端 sourceKey 映射、本地绑定兜底找目标 flow,都没有才新建。
- **脚本不按展示名认领 flow**:改名不影响身份,也不能指望"名字一样就会更新同一个 flow"。
- 上传成功后,下一轮 refine 照样要先 fetch。
- refine/export 必须落到 Step B 原地覆盖后的同一个 `path`;不得为了新标题重算 slug、重命名、另存或复制文件。只有用户明确要求新的独立流程时,才重走首次创建分支。
- 认证固定为 LinkFox API Key,由脚本从运行时环境读取;不读取、打印或向用户索取密钥;不调用或使用任何系统内部 API Key。出网地址只来自 `linkfox_paths.get_api_base()`。
- stdout 成功对象必须同时包含非空 `workflowId`、`mappingStatus: "saved"`,退出码为 0;`action` 是 `created` 或 `updated`。
- 非 0、缺 `workflowId`、映射不一致或 `mappingStatus` 不是 `saved` 都算失败:保留 Step B 的 workspace 文件并如实报错;脚本不自动重试写请求,调用方也不要重试首次创建(避免超时造成重复 workflow);不输出 flow info 标签。
- **`upload_workflow.py` 的 stdout 是唯一真相源**:成功就直接用 `workflowId` 进入 Step D。**禁止**再 Read 脚本源码、`ls scripts/`、写 `/tmp/*.py` / 内联 `python -c` / 另跑 fetch 来"再确认一次"。校验只在退出码非 0 时做,方式是读 stderr 并如实回报。

**Step D** — 返回给用户

顺序不能颠倒:

1. 一句 `已保存到工作空间:<path>`。
2. ```json 代码块贴完整 JSON。
3. "下一步"配置/试跑指引(按实际用到的节点裁剪,不再提示手工导入)。开头说清当前是**模板**,状态是"可导入、待配置",再按节点逐条点出要绑什么,比如"「通知」节点:飞书机器人地址",不要只写一句"补模型和凭据"。**不要提示绑定 `linkfoxAgentApi` 凭据**,它由后台自动绑定。用了 ExecuteFlow 时说明子工作流会**再扣一次积分**。用户配好之前执行会被执行前检查拦下。
3.5. **flow 含记录触发、或挂在多维表下的定时启动时**,一句关联结果,按 stdout 的 `tableAutomation`(话术见 `references/table-automation.md` §1 / §1.5;定时流再次保存回 `UNBOUND` 是正常成功,不说成停用)。`effective` 为 `false` 时这句挪到回复**第一段**说"工作流已保存,但自动化没生效"并给补救;为 `null` 时先跑一次 `table_automation.py list --workflow-id <id>` 再说。`tableAutomation` 不影响上传成功的判定、不影响输出 flow info 标签。
4. 一句版本说明,按 `upload_workflow.py` stdout 的 `history` 字段,话术见 `references/version-history.md` §1(例:「这次修改记为第 7 版;想撤销可以说"撤销刚才的修改"」)。`history` 不影响上传成功的判定。
5. 最后一行原样输出一个标签:`<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>`。

标签规则:

- `id` 只能取自本次 `upload_workflow.py` 的成功 stdout,禁止猜测、复用旧值或使用文件名。
- 标签不放进 Markdown 代码围栏,不加其他属性,不在同一回复中输出多个。
- 上传失败时完全不输出该标签。

## 能力边界

- **确认后只允许导入/更新**:只通过 `scripts/upload_workflow.py`;确认前禁止任何 linkfox-workflow 系统写调用。
- **执行只在用户明确要求时**:`scripts/run_workflow.py` 执行一次,`scripts/list_executions.py` 读取执行记录;**禁止**在上传成功后顺手跑一次"验证"。
- **历史版本只经 `scripts/workflow_history.py`**:上传时自动打开历史记录开关(只开不关);还原只在用户明确要求、预览之后才带 `--confirm`。
- **多维表自动化启停只经 `scripts/table_automation.py set`**:只在用户明确要求启用 / 停用时跑;不用 `linkfox-smart-table` 的 `registerWorkflow` / `updateWorkflowTriggerTable` / `unregisterWorkflow` 改关联(只改多维表侧,订阅行对不上)。
- **其他后端动作仍禁止**:不发布、不删除 flow,不删除也不修改执行记录,不查询 model / credential / documentStore 目录。
- **只用 LinkFox 认证**:不得获取、读取或使用系统内部 API Key。
- **密钥不出上下文**:LinkFox API Key 只由脚本从环境读取,不得写进命令参数、JSON、日志或用户回复。
- **一个文件对应一个 flow**:已有 workflow 的后续修改必须原地覆盖原 JSON,文件名和 sourceKey 保持不变;只有用户明确要求新流程才允许新文件。
- **只支持 agentflow v2**:不生成老 chatflow 结构,不生成 v1 multiagent。
- **只用 24 个节点**。原生 15:Start(**已弃用,禁止生成**)/ Agent / LLM / Tool / Retriever / Condition / ConditionAgent / Loop / Iteration / HumanInput / HTTP / CustomFunction / ExecuteFlow / DirectReply / StickyNote;LinkFox 自定义 9:BusinessStart / CrossBorderExpert / DataReader / FillForm / SendNotification / WriteFile / LinkfoxHTTP / End / CustomPythonFunction。开始节点一律 BusinessStart。不自造节点类型;`chatOpenAI` 是 Agent/LLM 节点里 `agentModel` 字段的选项值,不是独立节点。未注册的 `data.name` 会被 `save_workflow.py` 拒绝落盘。
- **运行时对象留占位**:`FLOWISE_CREDENTIAL_ID`、`documentStore` UUID、`executeFlowSelectedFlow`、Vector Store id 全写空字符串。
- **机器人地址 / 加签密钥只来自用户**(缺陷 #7130761097):`SendNotification` 的 `feishuWebhook` / `feishuSignSecret` / `dingtalkWebhook` / `dingtalkSignSecret`(以及任何 `type=password` 字段)新建时留 `""`,refine 时从 fetch 基线原样保留。**不得**从本会话里别的流程、上一轮生成、遗留的 `workflow.fragment.json` 或 memory 里沿用——那会把 B 的通知发进 A 的群;也不得把这些值写进 memory。`save_workflow.py` 对不是来自基线的值 exit 65;只有用户本轮在对话里亲手给了**这个流程**的地址 / 密钥时才带 `--secrets-from-user`,stdout 的 `secretsFromUser` 回显放行的字段(不含值)。
- **不做二次抽象**:不发明"子流程"、"变量声明块"、"错误处理块"这类 linkfox-workflow 系统里不存在的构造。

## 完成前检查

- 意图分类清晰;`not_workflow` 没被强推成 generate。
- 计划已用自然语言展示;仅在需求含糊或用户要求"先看方案"时才单独求确认,其他情形当轮直接落盘上传(explain / validate 除外)。
- 生成的 JSON 顶层只有 `description` / `usecases` / `nodes` / `edges` 四个字段。
- 每个节点 `data.name` ∈ 24 种(不含已弃用的原生 Start);`data.type` 与之匹配;顶层 `id == data.id`,且形如 `<data.name>_<数字>`(新建用顺序号,基线里画布生成的随机数字后缀原样保留;后缀带字母会被拒)。
- 每条 edge 的 `sourceHandle` 命中源节点锚点;`targetHandle` 等于 target 节点 id;Condition/ConditionAgent 出边索引与 conditions/scenarios 对齐。
- 跨节点引用使用实际运行时 `output` 的字段路径(完整表见 `references/output-and-state.md`):HTTP / LinkfoxHTTP 取 `output.http.data`,Agent / LLM / Tool / Retriever / CustomFunction / DirectReply / ExecuteFlow 取 `output.content`,DataReader 取 `output.<outputVariableName>`(默认 `tableData`),CrossBorderExpert 取 `output.expertResult`,SendNotification 取 `output.status` / `.successChannels` / `.failedChannels`,WriteFile 取 `output.recordCount` / `.target` / `.result`,FillForm 取 `output.filledForm`。**输出锚名不是 output 字段**——不存在 `output.data` / `output.sent` / `output.written` / `output.completed` / `output.submitted`。CustomFunction 输入变量一律使用 `{variableName, variableValue}`,并在代码中用 `$<variableName>` 读取。
- **代码节点默认用 JS 的 `CustomFunction`**:两者都能实现时不用 `CustomPythonFunction`。只有下游要按字段取 `result`、要 pandas / 解析 HTML·PDF·Word·Excel·PPT、或用户明确要 Python 时才用 Python(用户指定时在节点 `description` 写「用户指定用 Python」)。`save_workflow.py` 对不满足这几条的 Python 节点给 warning,见 `references/nodes-integration-and-output.md`「选择规则」。
- `$flow.state` 相关:只有 9 个节点有 `<name>UpdateState[]`(Agent / LLM / Tool / Retriever / CustomFunction / CustomPythonFunction / ExecuteFlow / Loop / CrossBorderExpert),别给别的节点造这个字段;`UpdateState` 里的 `{{ output }}` 指当前节点;**BusinessStart 没有 `startState`**,不能预声明初始 state,能用精确 Node Output 就别绕 state。
- `inputParams` 该省的省、该写的写:脚本代填的节点整个字段没出现;其余节点写了完整定义,用到 `{{ }}` 的字段带 `acceptVariable: true`。**任何节点都没有出现 `inputParams: []`**。
- 运行时字段全为占位,不写死具体 UUID(模型 / 凭据 / 知识库 / 店铺 / 专家 / 子流程)。**多维表例外**:见下一条。
- 通知机器人地址 / 加签密钥:新建为空、refine 与基线一致;没有从别的流程或记忆里抄值。带了 `--secrets-from-user` 的,用户本轮确实给过这个流程的地址。
- **选多维表的地方都写了两级、且是用户挑的真实表**:`DataReader`(`sourceType=linkfoxTable`)、`WriteFile`(`writeDestination=linkfoxTable` 或 `updateLinkfoxTable`)、`BusinessStart`(`startInputType=tableRecordTrigger`)都给了 `notebookId`(`nbk…` / `__loose__`)+ `tableId`(`tbl…`),来自智能表格 skill 查出的列表并经用户确认(见「选表」一节);只有用户明确说以后再选时才留 `""` 并带 `--table-later`。`WriteFile` 新建分支用 `newTableNotebookId`(默认 `__new__`)+ `newTableName`。
- **`WriteFile` 的 `writeDestination` 从三个值里选**:`linkfoxTable`(往已有表新增行)/ `newLinkfoxTable`(新建表)/ `updateLinkfoxTable`(改已有行,一次只改一行)。"改已有行"不要用"先删后加"或"写一条新记录"表达。
- **挂在多维表下的定时流**(`scheduleInput` + `linkfoxTableAutomationContext`):上下文至少有 `notebookId`、`tableId` 是真实 `tbl…`;回报时 `UNBOUND` 当正常成功说;没有说"表一改就会跑"(记录变更不触发定时流)。
- **含 `tableRecordTrigger` 的 flow**:① 触发表是用户挑好的真实表(`tableId` 留空时服务端保存会拒绝);② 监听 / 条件字段名字和 ID(`recordWatchFieldIds` / `recordConditionFieldId`,取自 `listFields`)都写了;③ 回复按上传 stdout 的 `tableAutomation` 说了关联结果,`effective` 不是 `true` 时第一段就说了"已保存但自动化没生效"和补救办法,没有说"已生效";从记录触发切走时提醒了原表的自动触发一起停了。取"这次变的那一行"用**节点引用** `{{businessStartAgentflow_0.output.recordEvent.recordId}}` / `.output.recordEvent.recordByName.<字段名>`(字段名来自 `list-fields` 的真表头),**不用** `{{$webhook.*}}`,也不是 `BusinessStart.output.tableRecordTrigger`(那是订阅配置的静态回显)。要写表时直接把 `BusinessStart` 接 `WriteFile`,用 `output.rows`(name-keyed),中间**不需要** `CustomFunction` 搬数据;回写触发的那一行用 `writeDestination=updateLinkfoxTable` 且 `updateRecordId` 留空。
- **refine 时开始节点原样保留**:BusinessStart 的 `id` / `inputs` / `credential` 与 fetch 基线一致;只有用户本轮明确要求换触发时才带过 `--allow-trigger-change`,且回复里逐条转述了 `triggerChanges`。记录触发流的下游用到了触发的那一行,没有读 `output.question`、没有插 FillForm 顶替。
- BusinessStart 唯一且无入边;其余执行节点都有入边(Iteration 子节点、Loop 回跳目标除外 —— 漏一条边运行时就报 `Multiple starting nodes are not allowed`);Loop / DirectReply / End 无出边;分支节点(Condition / ConditionAgent / HumanInput)每个都至少接一条下游;Iteration 子节点带 `parentNode` + `extent: "parent"`。
- flow 允许停在最后一个动作节点上,不必为了"看起来完整"硬接 DirectReply。
- 模型/AI 推理场景用了 `CrossBorderExpert`,没有默认落到原生 `Agent`/`LLM`/`ConditionAgent`;出现这三个节点时方案里已点出具体兜底原因(Tool 调用 / RAG 检索 / Structured Output / 节点内动态分支判断之一)。
- **每个 `LinkfoxHTTP` 节点的 `path`/`body` 都不是占位或抄用户原文的 endpoint_path 字面量**:已按 `nodes-linkfox-custom.md` 的流程用 `query_tools_matrix.py` 查过对应端点,`path` 是文档给的真实相对路径,`body` 是按文档参数表组好的字段(不是 `"{}"`)。查不到才允许留空占位,并在补配置指引里逐个点名哪些节点没查到、要用户自己补。
- **异步任务接口(创建只回 `taskId`,如 `/aigc/*Async`)都配了轮询环**:`CustomFunction(await sleep(<毫秒>))` → 查询接口 → `Condition(status equal SUCCESS)` → Else 接 `Loop` 回跳 **sleep 节点**(不是创建节点);副作用节点在 SUCCESS 分支、不在回跳路径;`maxLoopCount` 生图/生文 20、生视频 40;延时用 `await sleep()` 而**不是 `Atomics.wait`**。没有"只放一个创建节点就直接引用 `resultList[0].url`"。生视频这类 flow 已在方案里点明耗时很长、试跑可能先遇到 504(504 不代表失败,用 `list_executions.py` 查、不要重跑)。见 `nodes-linkfox-custom.md` 的「异步任务接口」。
- **同类节点全扫**:收到一条节点报错(或自己发现一处写错)时,先把 flow 里**所有同 `data.name` 的节点**过一遍同一项检查,一次全修。**例外**:标签带 `nodeId` 的节点级 refine 不做全扫,同类问题写在回复里问一句(见「节点级 refine」);脚本报 error 而必须返工时仍全扫。
- **`save_workflow.py` 报的 error 要按它给的修法改**,尤其 `outputAnchors` 这类样板字段:提示"删掉整个字段交给脚本代填"就照做,不要对着"应为 X"逐字段手改。
- **没跑通不许说"改好了"**:改动的证据是 `upload_workflow.py` 退出码 0;**流程能跑通的证据是一次真实执行:`runStatus=FINISHED`,并且带了 `--expect-*` 时 `businessCheck=PASS`**。两者不能互相顶替,也不能用"与已验证的那个改法相同"类比代替验证。这条与"上传后不许顺手跑"不冲突:需要验证时,先问用户要不要跑一次**验证型执行**(见 `references/runtime-execution.md`「两类执行」),用户同意才跑。没同意,或确实跑不了(服务端排队、含人工节点),就如实说"已上传但本次未验证"及原因。

> `version` / `color` / `baseClasses` / `category` / 锚点形状 / edge id / Condition operation 枚举,`save_workflow.py` 都会机械校验并在 error 时拒绝落盘,注意力应放在节点选型、prompt 内容和连线拓扑上。另有三条高频坑同样被拦截(细节见 `references/nodes-linkfox-custom.md`):`LinkfoxHTTP` 的 `body` 是占位 / 参数值全为空;`CrossBorderExpert` 的 `taskInstruction` 内联整体响应或字面量超 9000 字符;`data.credential` 写成类型名 `linkfoxAgentApi`。被拦下说明这一轮生成本来就要返工。

- **generate / refine / export 已跑完落盘与上传流程**:`scripts/save_workflow.py` 返回过 workspace 路径;`scripts/upload_workflow.py` 退出码为 0 并返回非空 `workflowId`、`mappingStatus=saved`。
- refine/export 的 `save_workflow.py` stdout 为 `mode=updated`,且 `path` 与首次保存完全一致;workspace 未新增 workflow 副本。`--workflow-id` 是唯一定位方式,且本轮先跑过 `fetch_workflow.py`。
- `upload_workflow.py` 返回的 `sourceKey` 等于 `basename(path)`;`action` 为 `updated`,`workflowId` 与上一轮一致。**二次编辑出现 `action=created` 或新 workflowId 就是 bug**,只有用户明确要求新流程时才允许。
- 回复第一行是 `已保存到工作空间:<path>`,最后一行严格为一个 `<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>`;上传失败则没有该标签。**输出的标签只带 `id`,不回带 `nodeId`**。
- **标签带 `nodeId`(节点级 refine)时**:只改了被引用节点及其确实被牵连的下游引用;其它节点的 `inputs`、所有 `position`、UI 补填的 credential / model 一字未动;没有顺手全扫批量改同类节点(有同类问题是**问**而不是改);基线里所有节点 id 原样保留;回复里点明了改动面。
- 输出附带补配置 + 试跑指引,并按实际用到的节点裁剪。
- 用户可见内容用简体中文,没有 `<linkfox-suggestion-*>` XML 标签、内部字段或方法名、颜色码。
- **没有静默响应**:读完 references 后就要产出方案;需求明确或用户催促时当轮直接落盘上传,需求含糊时才请求确认;短确认("继续"/"确认"/"可以")后必须立即走落盘与上传流程。禁止连续多轮回空消息,禁止对同一份明确需求反复求确认。

`history` 的检查:

- 还原前做过预览并转述了 `willChange`;只有用户明确同意(或本轮原话就是明确的还原指令)才带 `--confirm`。
- 预览和确认都带了 `--expect-latest`;退出 69 时转述了 `newerVersions` 并问了用户,没有改数硬过。
- 退出 68 时如实说"只有创建者能还原"或"有人刚保存过",没有改走 `--restore-from` / 手工重放绕过。
- 还原成功后没贴 JSON,报了 `newVersion`,最后一行输出了 flow info 标签;只预览 / 失败时没输出标签。
- 上传后的版本说明来自 stdout 的 `history`,没为拿版本号另跑 `list`。

`automation` 的检查:

- 只在用户明确要求启用 / 停用时跑了 `set`,`--enabled` 显式带了;没有在上传后顺手跑。
- 没手写 curl、没用 `linkfox-smart-table` 的 `registerWorkflow` / `updateWorkflowTriggerTable` 改关联;换表 / 换事件 / 补字段 ID 走的是 refine。
- 退出 70 / `tableSync.effective=false` 时说的是"订阅已保存但自动化没生效",转述了 `detail`;没说"已停用 / 已启用"。
- `list` 为空没有说成"这条流没有自动化"(只看得到自己的);`by-notebook` 带表回空时说了"可能无权限"。
- 回复里没输出 flow info 标签。

`run` / `runs` 另有一组检查(它们不产出 JSON,上面那些节点契约项一条都不适用):

- `run` 只在用户明确要求执行时跑过;**没有**在 generate / refine / export 上传成功后顺手跑一次"验证"。
- 含 SendNotification / WriteFile / CrossBorderExpert / HTTP 的 flow,执行前点出过会产生什么实际动作。
- 退出 66(执行前检查缺资源)时已按节点转述缺项,没有自作主张加 `--skip-preflight`。
- 回报状态严格来自 `run_workflow.py` 的 `runStatus`:不是 `FINISHED` 就没说过"执行成功";`nodeErrors` 已逐条转述节点名 + 错误。
- `FINISHED` 时也核对过 `notReachedNodes` / `actionResults` / `businessCheck`;有必须发生的动作没执行到、动作 `status=error` 或断言 `FAIL` 时,没说"跑通了 / 验收通过"。
- 为测试临时改过 flow 时,已恢复原设计并上传成功,回复里分开报了测试结果和恢复结果。
- 没有说"已发布""已上线""已经每天在跑";`scheduleInput` 的 flow 手动跑完已说清"这是手动触发的一次"。
- `runs` 用中文业务语言汇总,没有直接贴原始 JSON 数组;记录为空时直说还没有执行记录,没有编造。
- 没有为了"再确认一次"重复调用脚本、没有临场拼 curl 或写内联 python。
- 遇到 504 / 超时**没有立刻重跑** `run_workflow.py`,而是先 `list_executions.py` 查最近执行、确认没有 `INPROGRESS` 堆积(细节见 `references/runtime-execution.md`)。
- flow 含 `FillForm` / `HumanInput` 时,已如实说明"脚本无法提交人工节点、`Submit` 要在界面上点",没有反复尝试 `--form-file` / `--session-id` 各种参数组合;若为验证下游做过硬编码临时替换,**已恢复原始设计并再次上传**。
