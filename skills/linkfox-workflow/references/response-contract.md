# 响应契约

## 内部决策对象

以下结构用于约束思考,不直接展示给用户:

```json
{
  "action": "generate | refine | explain | validate | export | run | runs | history | automation | not_workflow",
  "confidence": "high | medium | low",
  "plannerStatus": "ready | needs_input | blocked",
  "requiresConfirmation": true,
  "missingInformation": [],
  "blockedReason": "",
  "workflowId": ""
}
```

- `ready`:计划已经足够清晰,可以展示待确认预览(尚未输出 JSON)。
- `needs_input`:缺关键信息,用一两个具体问题问用户,不要一次性抛一堆。
- `blocked`:超出节点表达能力、输入非法或用户要求 Agent 代调 linkfox-workflow 系统后端。

`not_workflow`:用户其实想要的是解释代码 / 讨论架构 / 一次性问答,不需要生成 flow。直接按普通对话回复。

## 用户可见输出顺序

1. 识别到的动作(一句话)。
2. 若是 `generate` / `refine`:
   - 自然语言展示计划或差异(节点链路 + 关键 prompt + 分支/循环结构 + 待补配置)。
   - 需求明确或用户催"立即生成"时,方案说明输出后当轮继续第 3 步直接落盘上传,不再单独求确认。仅在需求含糊或用户明确要求"先给我看看"时,才在此处一句话请求确认并停在本轮。
3. 明确的需求当轮、或含糊需求经确认后,按顺序:
   1. 一句 `已保存到工作空间:<path>`(来自 `scripts/save_workflow.py` 的 stdout)。
   2. ```json 代码块贴完整 JSON。
   3. “下一步”补配置/试跑指引。
   3.5. flow 含记录触发或挂在多维表下的定时启动时,一句关联结果(来自 stdout 的 `tableAutomation`,话术见 `table-automation.md` §1);`effective` 不是 `true` 时这句挪到第一段。
   4. 一句版本说明(来自 stdout 的 `history`,话术见 `version-history.md` §1;没有可说的就省略)。
   5. 最后一行 `<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>`。
   顺序不能颠倒——路径先于 JSON,JSON 先于指引。
4. 若是 `explain`:自然语言按执行顺序说明每个节点的作用。
5. 若是 `validate`:问题列表,分 error / warning;无问题则明确说"结构合法,可以导入"。
6. 若 `blocked` / `needs_input`:说明原因或提问,不给 JSON,不落盘。
7. 若是 `export`:等同 generate/refine 确认后的输出顺序(先路径 → JSON → 指引 → flow info 标签)。
8. 上传失败:明确说明失败阶段与 workspace JSON 路径,不输出 flow info 标签。
9. 若是 `run`:**不贴 JSON、不贴 workspace 路径**(执行结果落盘是给自己留档的,用户要的是结果)。按顺序:
   1. 一句执行结论 —— 严格对齐 `runStatus`:`FINISHED` 说"已执行一次,流程跑完";`ERROR` 说"执行中断,某个节点失败";`WAITING_HUMAN_INPUT` 说"流程停在人工审批节点,等人处理"。`FINISHED` 后面紧跟业务结论:带了断言就报 `businessCheck`;`notReachedNodes` 里有动作节点、或 `actionResults` 有 `status=error` 时要直说,比如"流程跑完,但「写入基线」这次没执行到"。退出 66 时第一句是"没有执行,缺这些配置",然后逐节点列出。
   2. 关键产出:`textPreview` 有内容就转述(被截断时说明这是节选);节点报错时逐条列"节点名 → 错误"。
   3. 一句 `本次执行记录 executionId:<executionId>`,并说明可以据此查详细记录。
   4. 需要用户接着做什么(补配置重跑 / 去 linkfox-workflow 系统处理人工审批 / 无需动作)。
   **不输出 `<linkfox-flow-info>` 标签** —— 那个标签是"上传成功"的凭据,执行不是上传。
10. 若是 `runs`:纯文字汇总,**不贴原始 JSON 数组、不贴 workspace 路径**。按顺序:
   1. 一句总览:"最近 N 次执行,X 次成功、Y 次失败"(总次数用 `total`,本页条数用 `returned`,别混)。
   2. 按时间倒序列关键几条:时间 + 状态 + 失败的话带失败节点和错误摘要。条数多时只列最近几条并说明还有更多。
   3. 需要看某次细节时,告诉用户可以指名那次(或直接给出 `executionId`)。
   记录为空就一句"这个流程还没有执行记录",不编、不猜。**同样不输出 flow info 标签。**

11. 若是 `history`:纯文字,**不贴 JSON、不贴路径**。查看按"第 N 版 · 变更人 · 时间 · 改了什么"逐条列,不输出 flow info 标签;还原先说会改回哪些节点并请求确认(预览轮不输出标签),**还原成功后**说"已还原到第 N 版,记为第 M 版",最后一行输出 `<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>`,让前台画布重新拉取。
12. 若是 `automation`:纯文字,不贴 JSON、不输出 flow info 标签(画布没变)。启停按 `tableSync.status` 一句话说结果("已停用,表里变更不再触发" / "已重新启用");退出 70 说"订阅已保存,但自动化没生效"并转述 `detail`;查看按"流程 · 数据表 · 事件 · 开/关"逐条列。

## JSON 输出规范

- 顶层字段固定 4 个:`description` / `usecases` / `nodes` / `edges`。
- 严格按 `references/node-catalog.md` 的节点身份、必填 inputs、outputAnchor 命名。
- 运行时目录字段(model / credential / documentStore uuid / vectorStore / flowId)一律留占位空字符串或最短骨架项,不写具体值。
- 缩进 4 空格(可读性优先,不追求最短)。
- JSON 前后不加解释性文字混排;要说明的话写在 JSON 代码块之外。
- **落盘和上传先于展示**:generate / refine / export 的 JSON 必须先经 `scripts/save_workflow.py` 落到 workspace,再经 `scripts/upload_workflow.py` 上传并验证 mapping。拿到 `path` 和 `workflowId` 后才回复。禁止只贴 JSON,也禁止跳过上传。
- **路径稳定**:首次新建返回 `mode=created`;同一流程的 refine/export必须返回 `mode=updated`,且回复中的 `path` 与首次路径逐字符相同。不得因为标题、slug或展示名变化而改变文件名。
- 上传脚本返回的 `sourceKey` 必须等于 `basename(path)`,`workflowId` 必须与上一轮一致且 `action=updated`。只有用户明确要求新流程时才允许新的 path/sourceKey/workflowId。

## linkfox-workflow 系统的 ID 输出规范

- 只接受 `upload_workflow.py` 退出码 0时 stdout 的非空 `workflowId`;同时要求 `mappingStatus == "saved"`。唯一例外是 `workflow_history.py restore --confirm` 退出码 0 且 `restored: true`:服务端内容同样变了,输出同一个标签。
- 成功回复的最后一行严格为 `<linkfox-flow-info id="<workflowId>"></linkfox-flow-info>`。
- 标签不放入代码围栏,不转义尖括号,不增加空格/其他属性,每次只输出一个。
- **输出的标签只带 `id`,不回带 `nodeId`**。用户本轮引用节点时传进来的 `nodeId` 是前台给的"改哪个节点"凭据,不是上传结果的一部分;回带它会让前台以为这次输出仍绑定在那个节点上。
- 上传、解析 ID或映射验证任一步失败时,完全不输出该标签;不得猜测或沿用旧 ID。

## 不输出的东西

- 不输出 `<linkfox-suggestion-workflow>` / `<linkfox-suggestion-agent>` / `<linkfox-suggestion-ask>` 等 LinkFox 宿主的 XML 动作卡——本 Agent 不跑在 LinkFox 编辑器里。
- 不输出内部字段 / 方法名,对用户说"选择模型 / 选择知识库"即可。
- 只有上传脚本成功后才可以说“已上传到 linkfox-workflow 系统”;只有 `run_workflow.py` 退出码 0 且 `runStatus=FINISHED` 才可以说“已执行一次 / 流程跑完”。**“已发布 / 已上线 / 已经每天在跑”始终禁止**——上传不是发布,手动执行一次也不等于定时生效。
- `runStatus` 不是 `FINISHED` 时禁止任何“执行成功 / 跑通了”措辞;`ERROR` 就说中断和失败节点,`WAITING_HUMAN_INPUT` 就说停在人工审批。
- 不输出敏感字段的具体值(用户即使贴了带 credential UUID 的 JSON 也要提醒:导出前建议清空)。

## 下一步指引模板

上传成功后附带:

> 下一步:
> 1. 在 linkfox-workflow 系统中为每个 Agent/LLM 节点选模型并绑定 Credential;在 Retriever 节点上选 Document Store;在 Tool/HTTP 节点上选 Credential。
> 2. 配置完成后试跑一次。

按实际用到的节点裁剪:没用到 Retriever 就删第二行第 2 句,等等。
