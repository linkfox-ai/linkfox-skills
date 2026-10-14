# 生命周期动作

## 目标

Agent 的主要产物是一份合法的 linkfox-workflow agentflow v2 JSON(顶层 `{description, usecases, nodes, edges}`)及其 `workflowId`。用户确认 generate/refine 计划后,Agent 通过受控脚本创建或更新当前 workflow;**用户明确要求时还可以执行一次该 workflow 并查看它的执行记录**;但不发布、不删除 flow,不删改执行记录。

## 动作分类

| 动作 | 说明 | 需要用户确认 | 成功证据 |
|---|---|---|---|
| `generate` | 从自然语言需求生成一份新的 flow JSON | 需求明确时否;含糊时是 | 已落盘 + 已上传并验证 mapping + 展示完整 JSON和 workflowId |
| `refine` | 在已有 flow 上做增/删/改(加节点、改连线、改 prompt、加分支等) | 结构性改动是;仅改单节点 prompt/描述否 | 已落盘 + 幂等上传 + 展示增量差异、新 JSON和 workflowId |
| `explain` | 解释某段 flow 或某个节点在做什么 | 否 | 自然语言说明 |
| `validate` | 只读校验(结构/命名/连接/环路/未连出口) | 否 | 问题列表(可能为空) |
| `export` | 输出并同步上一轮已确认的最终 JSON | 否(用户已在 refine/generate 确认过) | 已落盘 + 已上传 + JSON 内容和 workflowId |
| `run` | 真实执行一次已在 linkfox-workflow 系统上的 workflow | **是** —— 只在用户明确要求执行时才跑 | `run_workflow.py` 退出码 0 + `runStatus` + `executionId`,并如实转述节点状态 |
| `runs` | 查看某 workflow 的执行记录(列表或单次详情) | 否(纯读) | `list_executions.py` 退出码 0 + 中文汇总的执行情况 |
| `history` | 查看 / 对比 / 还原历史版本 | 查看否;**还原是**(先预览) | `workflow_history.py` 退出码 0;还原另需 `restored: true` + `newVersion` |

`history` 的完整规则在 **`version-history.md`**。`run` / `runs` 的完整规则在 **`runtime-execution.md`**;它们是运行时动作,不产出 JSON,本文件下面那些节点契约与落盘规则一条都不适用。

## 通用前提

- 每次生成或修改都必须**先给出自然语言方案**(用哪些节点、如何连接、每个节点的关键 prompt / 参数)。是否需要用户单独确认再执行,按 `confirmation-policy.md`:需求明确或用户催促时,方案和落盘上传可在同一轮完成,方案作为落盘前的说明输出,不再等下一轮"确认"。
- 涉及运行时目录字段(model / credential / documentStore / vectorStore / tool credential / flowId)一律**留占位**:字符串字段用 `""`,数组字段用 `[]` 或给一个骨架项让用户填。生成的 JSON 里绝不写死 `FLOWISE_CREDENTIAL_ID` 或具体 UUID。
- 明确告知用户"上传后需要在 linkfox-workflow 系统节点上选择模型、指定 Document Store"等(按实际用到的节点)。`linkfoxAgentApi` 凭据由后台自动绑定,**不要**提示用户去绑。
- 无法用现有 24 个节点(原生 15 + LinkFox 自定义 9)表达的需求,先尝试组合(Condition + Agent + Tool + Iteration…),仍无法覆盖时明确说"当前 linkfox-workflow agentflow v2 不支持此形态",给出最接近的替代方案。

## generate:从零生成

**必需信息**:

- 业务目标(一句话说明这个 flow 干什么)
- 触发方式(`BusinessStart.startInputType`,只有四种:chatInput / scheduleInput / storeAuthorization / tableRecordTrigger;**没有** formInput / webhookTrigger)
- 主要步骤(自然语言列表,由 Agent 翻译成节点)
- 是否有人工审批环节
- 是否需要循环/迭代
- 是否需要知识库(Document Store / Vector Store)
- 是否需要外部 API 调用
- 是否需要状态跨节点传递(Flow State)

**执行流程**:

1. 判断需求是否明确:如果用户已经点出节点组合(如"最简"、"BusinessStart → DirectReply"、"不用 AI/API")、给了明确输入输出,或者显式催促("立即生成"、"不要再问"),直接跳到第 3 步在同一轮内落盘上传。只有当触发方式、有无 AI/知识库/外部 API 都没说、目标含糊时才走 `needs_input` 追问 1-2 个问题。
2. 挑选节点:先业务动作 → 匹配节点类型 → 决定分支/循环/迭代结构。
3. 用自然语言给出方案(1-3 段,简洁):
   - 起点是什么(Start 的输入类型)
   - 中间步骤(按顺序,列节点类型 + 每个节点在做什么)
   - 分支/循环/迭代如何嵌套
   - 每个 Agent/LLM 节点的关键 prompt 概要(不要贴大段模板文本)
   - 需要用户后续绑定的运行时对象(模型、Document Store、tool 凭据、目标 flowId;`linkfoxAgentApi` 凭据后台自动绑定,不列)
4. 需求明确时,方案输出后当轮继续第 5 步;需求含糊时,方案末尾一句请求确认,等下一轮短确认后再进入第 5 步。
5. 按 `references/node-catalog.md` 的骨架生成完整 JSON,再跑 `validate` 一遍,有问题当场修。
6. **首次落盘**:`Write ./workflow.fragment.json` → `python scripts/save_workflow.py --content-file ./workflow.fragment.json --slug linkfox-workflow-<english-slug>`拿到并记住路径。若当前会话已有 workflow,generate 只有在用户明确要求“新建另一份流程”时才能执行这一步;否则应路由为 refine并覆盖原文件。
7. **上传到 linkfox-workflow 系统**:`python scripts/upload_workflow.py --content-file <path> --name '<业务展示名>' --flow-type AGENTFLOW`。`--name` **首次创建必填**(更新时可省略,沿用上次的名字),是用户在 linkfox-workflow 系统列表里看到的名字,用业务语言写、不要拿文件名顶上。脚本以真实文件 basename作为 sourceKey,写请求成功后立刻把 `workflowId -> path` 绑定写进 `workflow-index.json`;只有退出码 0、非空 workflowId、`mappingStatus=saved` 才算成功。**脚本不会按展示名去认领已有 flow**(撞名会覆盖别人的 workflow),所以改名不改身份。
8. 回复顺序:`已保存到工作空间:<path>` → ```json 代码块 → 补配置/试跑指引 → `<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>`。

**"确认门槛"总结**:不要把用户已经说清楚的东西再让他/她说一遍。用户第一条消息里已经写了"最简 / 不用 AI / 不用 API / 只用 X 节点"这类明确边界,当轮就落盘上传;不要回空消息、也不要反复反问"是否确认"。

**成功证据**:workspace 路径 + 一份合法 JSON + 上传脚本确认过的 workflowId和 mapping + 简短配置指引。

## refine:改现有 flow

**必需信息**:

- 目标 workflowId(来自对话里的 `<linkfox-flow-info id="...">`;这是 workflow 的唯一身份)
- 当前 flow JSON(**以 `fetch_workflow.py` 拉回的 linkfox-workflow 系统侧 flowData 为准**;用户也可粘贴或引用)
- 想改什么(加节点 / 删节点 / 改连线 / 改 prompt / 换模型类型 / 加分支等)
- 标签里可选的 `nodeId`(前台"引用节点"功能带上来的):有它就是**节点级 refine**,改动面收窄到那一个节点及其联动项,规则见 SKILL.md 的「节点级 refine」一节

**执行流程**:

0. **先 fetch 拿基线**:refine 每轮都先跑 `python scripts/fetch_workflow.py --workflow-id <id>`,用 linkfox-workflow 系统侧真实 flowData 作为改动基线。**没有"只有第一次才需要 fetch"这回事**,也**不要因为本地已有 `workflow.fragment.json` 就跳过**——那份是上一轮自己写的,不含用户在画布上手工调过的 `position`、也不含用户在 UI 补填的 credential / model / documentStore,拿它当基线会把这些改动冲掉。已绑定过本地文件的 id 会复用同一文件(`reusedLocalFile: true`,只指路径复用,内容仍是这次拉回的服务端版本)。**跳过 fetch 在脚本层也走不通**:第 7 步的 `save_workflow.py --workflow-id` 会校验这份本地文件仍是当时 fetch 下来的原封副本,不符合直接退出 64。
1. 解析 fetch 回来的 JSON(或用户另行提供的 JSON),识别现有节点集合与 edge 拓扑。JSON 无法解析或明显不是 linkfox-workflow agentflow v2 时,立刻反馈,不要"猜结构"。
   - 标签带 `nodeId` 时,**在这一步先定位该节点**:找不到就直接说"这个流程里没有这个节点",停下,不按 label 猜、不退化成整流程 refine。找到了就搜一遍 `{{<nodeId>.output` 把下游引用者列出来,那就是本次允许的联动范围。
2. 用自然语言说明改动:哪些节点新增/删除、哪些 edge 变、哪些 `inputs` 值改。展示"改前 / 改后"的关键片段,不要贴整个 JSON。节点级 refine 要明确点出"只改了这一个节点"以及联动了哪些下游引用(没有联动就说没有)。
3. **保留用户原有的 `position`、`label`、`inputs` 里已填的具体值**。改动不涉及的地方一个字符都不动。
   - **开始节点整块原样保留**:BusinessStart 的 `id` / `inputs` / `credential` 从基线拷过来,不套"默认手动启动"(那只适用于从零 generate)。`save_workflow.py --workflow-id` 会比对,改了就 exit 65;只有用户本轮明确要求换触发时才带 `--allow-trigger-change`。规则见 SKILL.md「开始节点锁定」。
4. 增/删节点时同步维护 edges:被删节点的入边出边必须一起处理;新增节点必须补上下游 edges。
5. 生成新 id 时用 `<data.name>_<现有最大 index + 1>`,避免冲突。**已有节点的 id 一律原样保留** —— 画布上建的节点后缀是随机数(`fillFormAgentflow_415972`)不是顺序号,归一化它等于删旧建新,edge 和下游 `{{ }}` 引用会一起失效。
6. 生成后跑 `validate`。
7. **覆盖原文件并上传**:`python scripts/save_workflow.py --content-file ./workflow.fragment.json --workflow-id <原 workflowId>` → `python scripts/upload_workflow.py --content-file <返回的同一 path> --workflow-id <原 workflowId> ...`。**workflowId 是唯一身份**,也是 refine 唯一可用的定位方式(`--existing-file` 已移除,不再有"拿本地路径当身份"的退路)。文件名、basename/sourceKey和 workflowId必须保持同一身份;不得调用 `--slug`,不得另存副本。拿不到 workflowId 就问用户是哪个流程,不得擅自新建。
8. **检查 `save_workflow.py` 的 `layoutNotes`**:出现该字段说明有节点的 `position` 是脚本按拓扑自动生成的,即基线里没带坐标。refine 场景出现它,基本等于第 0 步没做、把用户的画布布局冲掉了 —— 应先 fetch 重来,而不是继续上传。
9. 回复顺序:`已保存到工作空间:<path>` → ```json 完整 JSON → "本次实际改动"清单/配置指引 → flow info 标签。

## explain:只读解释

- 不产生 JSON,也不建议改动(除非用户后续要求)。
- 按 edge 拓扑还原执行顺序,逐节点用自然语言说"这里在做什么"。
- 涉及分支(Condition / ConditionAgent / HumanInput)时列出所有出口指向的下游。
- 遇到用户手写的 CustomFunction 代码时,先读代码再解释,不要凭节点名硬猜。

## validate:结构校验

只读、可直接执行,不要用户确认。

**用机械校验,不要人工逐项核对**:把用户贴的 JSON 写成临时文件,跑

```
python scripts/save_workflow.py --content-file <临时文件> --dry-run
```

`--dry-run` 跑和正式保存完全相同的补齐与全部校验,但不写文件,不动 fetch 凭据和上传门禁。退出码 0 表示结构合法,stdout 的 `warnings` 照实转述;退出码 65 时,stderr 每条 `ERROR:` 就是一个 error。用户的 JSON 原样保留,不修改、不上传。

脚本覆盖不到的语义问题再对照下面的清单补充,比如"Condition 没接 Else 是不是故意的"、业务逻辑对不对。清单里标了"`save_workflow.py` 会拦下"的项,dry-run 已经检查过,不用再人工核对。

**dry-run 只用于 validate**。generate / refine 直接正式保存(报错就修了重跑),不要先 dry-run 一遍,那是白多一次调用。

检查项:

1. **顶层字段**:必须有 `description` / `usecases` / `nodes` / `edges`,且 `usecases` 是字符串数组。
2. **开始节点必须是 BusinessStart**:每个 flow 有且只有一个 `data.name=businessStartAgentflow`(`data.type=BusinessStart`)节点作为入口。**禁止使用原生 `Start` / `startAgentflow`**——LinkFox 分支已用 BusinessStart 全面替换,原生 Start 被视为过时节点,`save_workflow.py` 会直接拒绝。
3. **id 命名**:顶层 `id == data.id`,形如 `<data.name>_<数字>`(前缀必须逐字等于 `data.name`,后缀必须是纯数字),无重复 id。**后缀不要求连号**:新建节点用顺序号,画布上建的节点是随机数(`fillFormAgentflow_415972`),两者都合法 —— 不要把随机后缀当成错误报出来,也不要建议用户归一化。后缀里有字母(`_a1`)才是 error。
4. **type 匹配**:`data.type` ∈ 24 种允许值;`data.name` / `data.type` / 顶层 `type` / `version` / `color` / `baseClasses` 的映射符合 `node-catalog.md`,由 `save_workflow.py --dry-run` 机械校验。
5. **顶层 type**:Iteration 是 `iteration`,StickyNote 是 `stickyNote`,其余是 `agentFlow`。
6. **必填 inputs**:按 `node-catalog.md` 每个节点的必填清单核对,缺失就报。
7. **inputAnchors 全为空数组**。
8. **outputAnchors 结构**（error）:
   - 除 Loop / DirectReply / StickyNote 外,每个节点的 `data.outputAnchors` 必须非空,每个锚点是含 `id` / `name` / `label` / `description` 的完整对象。
   - 每个锚点 `id` 必须严格等于 `<nodeId>-output-<name>`;缺 id 或命名对不上 → error,linkfox-workflow 系统保存时会静默丢弃所有绑定到该锚点的 edge。
   - Condition / ConditionAgent 必须恰好两个锚点,`name` 分别为 `"0"` / `"1"`;HumanInput 恰好两个锚点,`name` 分别为 `proceed` / `reject`;其他节点单锚点,`name` 与本文件"输出锚点"记录一致。
9. **edges**:
   - 每条 edge 的 `source` / `target` 都能在 `nodes` 里找到
   - `sourceHandle` 命名符合规则(常规节点用 `<id>-output-<name>`,Condition/ConditionAgent 用 `-output-<index>`,HumanInput 用 `-output-proceed/reject`)
   - **`sourceHandle` 必须能在 source 节点的 `outputAnchors[].id` 里命中**;命中不上 → error,画布上会显示为孤立节点(即使脚本已上传成功)。
   - `targetHandle == target`
   - `id` = `<source>-<sourceHandle>-<target>-<targetHandle>`
   - `data.sourceColor` / `data.targetColor` 与节点 color 一致
   - HumanInput 出边必须 `data.isHumanInput=true` 且带 `edgeLabel: proceed/reject`
10. **拓扑**(前 4 项 `save_workflow.py` 会 exit 65 拦下):
    - BusinessStart 无入边;BusinessStart 至少有一条出边
    - Loop / DirectReply / End 无出边
    - 多节点 flow 的 `edges` 不得为空;每个非 StickyNote 节点必须至少参与一条 edge(无孤立节点)
    - 分支节点(Condition / ConditionAgent / HumanInput)必须至少接一条下游出边
    - **flow 可以停在最后一个动作节点上**(SendNotification 发完、WriteFile 写完、Agent 答完就是终点),不要因为末端不是 DirectReply 就报错;只在"用户明显需要一句可见回复却没有 DirectReply"时给 warning
    - HumanInput 的 `-output-proceed` 和 `-output-reject` 最好都有出边;只接一条时给 warning 并说明另一条路径会无出口
    - Condition / ConditionAgent 的两个分支(含 Else)都有出边,否则给 warning
    - 无非法嵌套:Iteration 内不嵌 Iteration/Loop;Loop 内不含写型节点
11. **变量替换**(`save_workflow.py` 按 error 拦下):`inputParams` 不是空数组(脚本代填的节点整个字段别写,`[]` 会被拦);手写的 `inputParams` 里用了 `{{ }}` 的字段带 `acceptVariable: true`(字段已声明只漏布尔时脚本自愈,字段整块没声明仍报 error);`{{ <nodeId>.output... }}` 的 nodeId 真实存在;不出现裸 `.output`。
12. **Condition operation**(`save_workflow.py` 按 error 拦下):逐字属于该 `type` 的合法枚举 —— `equal` 而不是 `equals`,`larger` 只对 number 合法。
13. **占位字段**:model / credentialId / documentStore uuid / flowId / `amazonStore` / `expertId` 若非空,提醒用户"这些应留占位;检测到具体值,是否确认要写死"(`save_workflow.py` 给 warning,不拦)。

问题分级:

- **error**:结构非法,导入 linkfox-workflow 系统会报错或渲染错乱。
- **warning**:可导入但语义可能不对(如 Condition 没接 Else、HumanInput 只接一个出口)。

## export:输出

- **先原地覆盖、上传再展示**:使用 `save_workflow.py --workflow-id <原 workflowId>`,再用同一 path + `--workflow-id` 调用 `upload_workflow.py`;export不得生成新文件。
- 回复顺序:`已保存到工作空间:<path>` → 校验通过的完整 JSON → 提醒在 linkfox-workflow 系统中补选 model/Document Store/目标 flow(`linkfoxAgentApi` 凭据后台自动绑定,不提) → flow info 标签。
- 明确说明运行时对象仍需在 linkfox-workflow 系统内绑定。

## run:执行一次

完整规则见 `runtime-execution.md`。要点:

**必需信息**:目标 workflowId(来自 `<linkfox-flow-info id="...">`)。**不需要** fetch,也不需要读节点契约。

**执行流程**:

1. 取 workflowId;取不到就问一次是哪个流程,不猜。
2. **判断副作用**:flow 里有 SendNotification / WriteFile / CrossBorderExpert / HTTP / LinkfoxHTTP 时,先一句话点出会产生什么实际动作(真发通知、真写表、真打接口、可能计费)。用户已经说"直接跑 / 我知道会发 / 就是要发"就不用再问。
3. `python scripts/run_workflow.py --workflow-id <id>`(要验证分支时带 `--expect-reached` / `--expect-not-reached`)。脚本先做执行前检查,缺资源就退出 66、不执行,按 `missing` 逐节点转述。触发方式与手动执行的关系、证据分档、断言用法、临时测试版的恢复,**以 `runtime-execution.md` 为唯一权威**,这里不重复。
4. 按 stdout 如实回报:`runStatus` 决定能不能说"执行完成";`FINISHED` 时还要看 `notReachedNodes` / `actionResults` / `businessCheck` 才能判断业务是否达标。`nodeErrors` 非空时逐条转述。
5. 给出 `executionId`,并说明可以用它查这次的详细记录。

**禁止**:在 generate / refine / export 上传成功后顺手跑一次"验证"。上传成功的证据是 `upload_workflow.py` 的 stdout,不是一次真实执行。

**成功证据**:退出码 0 + `runStatus` + 非空 `executionId` + 如实转述的节点状态。注意退出码 0 只代表调用成功,flow 内部失败也是 0。

**措辞**:可以说"已执行一次";不能说"已发布""已上线""已经每天在跑"。非手动启动的 flow 手动跑完照 stdout 的 `triggerNote` 说明这次证明了什么、没证明什么。

## runs:查看执行记录

纯读动作,不需要确认,不产生副作用。完整规则见 `runtime-execution.md`。

**必需信息**:目标 workflowId(列表),或某次的 executionId(详情)。

**执行流程**:

1. 列表:`python scripts/list_executions.py --workflow-id <id> --limit 10`。可加 `--state`(`INPROGRESS` / `FINISHED` / `ERROR` / `TERMINATED` / `TIMEOUT` / `STOPPED`)、`--session-id`、`--start-date` / `--end-date`、`--page` / `--limit`。
2. 用户问某一次的细节时,拿该条的 `executionId` 再跑 `--execution-id <executionId>` 看逐节点轨迹。
3. 用中文业务语言汇总:成功/失败次数、时间、失败节点 + 错误摘要。不要贴原始 JSON 数组。
4. 记录为空就直说"这个流程还没有执行记录",不编。

**成功证据**:退出码 0 + 一段让用户看得懂的执行情况汇总。

**注意**:`state` 是 linkfox-workflow 系统的权威状态,比 `run_workflow.py` 派生的 `runStatus` 更可信。`total` 是该 flow 的全部执行次数,`returned` 只是本页条数,别混。

## 什么时候返回 blocked

- 需求超出 agentflow v2 节点表达能力(子流程递归、无界并行、自定义节点类型),明确说"当前不支持",给替代建议。
  - **"要等一会儿 / 要轮询异步任务"不在此列**:`CustomFunction` 里 `await sleep(ms)` 可以延时,AIGC 这类只回 `taskId` 的接口按 sleep → 查询 → `Condition` → `Loop` 搭轮询环即可,正常生成,不要报 blocked。见 `nodes-linkfox-custom.md` 的「异步任务接口」。
- 用户提供的原 JSON 不是合法 agentflow v2 结构(缺顶层字段、`data.type` 未知),让用户确认来源。
- LinkFox API Key 无法从运行时环境解析,或导入/mapping 校验失败。保留 workspace 文件,不输出 flow info 标签。
- 用户要求发布、删除 flow,删除或修改执行记录,或查询 model / credential / documentStore 目录;说明当前授权边界只覆盖确认后的 workflow 创建/更新,以及明确要求时的执行与执行记录查询。
- 用户要求执行(`run`)或查执行记录(`runs`)但拿不到 workflowId(对话里没有 `<linkfox-flow-info id="...">`,也无法唯一确定是哪个流程);问一次是哪个流程,不猜、不拿展示名反推。
