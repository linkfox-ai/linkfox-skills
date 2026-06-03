# 08 子 agent 协议

Evaluator 的评估有效性**完全依赖子 agent 的独立与隔离**。本文档规定 spawn 规则、读写边界、降级方案。

## 4 个角色

| 角色 | 阶段 | 任务 | subagent_type 建议 |
|------|-----|------|-------------------|
| A | E1 | 盲读目标 skill，提取 process 和 rules | `general-purpose` 或 `Explore` |
| B | E2 | 仅读 SKILL.md 回答三问；再读 references 画执行图 | `general-purpose` |
| C | E4 合成任务 | 加载目标 skill 跑一个真实任务 | `general-purpose` |
| D | E4 反例测试 | 对每条反例独立 spawn，执行 skill 并判定 | `general-purpose` |

每个角色的读写边界在 SKILL.md 已概述。本文档给出**可执行的 spawn prompt 模板**。

## 通用规则

1. **每个角色每次评估独立 spawn**：A、B、C、D 不共享会话（即使是 A 的两次查询也分开）
2. **主评估 agent 不下场执行 skill 流程**：主 agent 只负责 spawn、收集轨迹、对照 interview-record 打分
3. **子 agent 不加载 evaluator 自身**：prompt 里明确"不要读 linkfox-skill-evaluator 目录"
4. **物理隔离 > 口头约束**：spawn 时尽量用 subagent_type + 相对路径限制，而不仅仅是 prompt 里说"不许读 xx"
5. **隔离失败要记录**：若确认子 agent 违规读了禁止文件，报告标 `isolation: violated`，该维度标 `integrity: suspect`

## 子 agent A：E1 盲读

### prompt 模板

```
你是一个负责从 skill 文件中提取流程和规则的分析助手。

目标 skill 目录：{skill_absolute_path}

你只能读以下 3 个文件：
  {skill_absolute_path}/SKILL.md
  {skill_absolute_path}/references/workflow.md
  {skill_absolute_path}/references/rules-and-boundaries.md

严禁读：
  {skill_absolute_path}/references/interview-record.md
  {skill_absolute_path}/.eval/ 下任何文件
  上述 3 文件以外的任何 references/ 内容

任务：
读完上述 3 个文件，用严格 JSON 格式输出：

{
  "process": [
    { "id": "step_1", "name": "...", "description": "...", "deterministic": true }
  ],
  "rules": [
    { "id": "R1", "text": "...", "type": "hard" }
  ]
}

若你读取上述 3 文件之外的任何文件，在输出末尾附加 {"violation": true, "file": "<path>"}
```

### 完成判定

- 子 agent 返回结构化 JSON → 直接解析
- 返回自然语言 → 主 agent 尽力解析
- 返回空 / 报错 → 重试一次；再失败 → 降级为主 agent 自己读

## 子 agent B：E2 三问 + 执行图

### 阶段一 prompt（只给 SKILL.md）

```
你是一个从未见过这个 skill 的助手。现在请你读：

  {skill_absolute_path}/SKILL.md

严禁读：
  {skill_absolute_path}/references/ 下任何文件
  {skill_absolute_path}/scripts/ 下任何文件
  {skill_absolute_path}/.eval/ 下任何文件

读完后，请用简短语言回答以下 3 个问题：

1. 什么情况下我应该调用这个 skill？
2. 如果要调用，我应该先读哪个文件？
3. 这个 skill 最容易出错的地方是什么？

如果 SKILL.md 没说清楚某一问，如实回答"SKILL.md 没说清楚"。不要编造内容。
```

### 阶段二 prompt（追加 references）

**新开一个 spawn**（B 的两次是独立的），否则阶段一的三问答案会污染执行图：

```
你是一个助手，请读以下文件：

  {skill_absolute_path}/SKILL.md
  {skill_absolute_path}/references/*.md

严禁读：
  {skill_absolute_path}/references/interview-record.md
  {skill_absolute_path}/.eval/ 下任何文件

根据这些文件，用 ASCII 图或有序列表画出这个 skill 的执行图：
- 主流程步骤（按顺序）
- 每步的决策分支（如果有）
- 脚本调用点（如果有）

不要推断文件里没写的内容，只画可以明确从文字中读出的东西。
```

## 子 agent C：E4 合成任务

```
你现在扮演一个加载了 {skill_name} skill 的助手。用户向你发送一个请求：

<用户请求>
{synthetic_task_description}
</用户请求>

你必须：
- 按 skill 的流程和规则执行
- 只能读目标 skill 的文件：{skill_absolute_path}/
- 不能读：
  - {evaluator_skill_path}/ 下任何文件
  - {skill_absolute_path}/references/interview-record.md
  - {skill_absolute_path}/.eval/ 下任何文件

输出约定：
- 每执行一个步骤，输出一个 <!-- trace:step --> 块，包含 STEP / NAME / INPUT / ACTION / SCRIPT_USED / OUTPUT / RULES_CHECKED
- STEP 字段必须匹配 skill references/workflow.md 中的 step id
- deterministic 步骤必须真调 scripts/*.py（Bash 工具），SCRIPT_USED=true
- 所有步骤结束后，输出一个 <!-- trace:summary --> 块（JSON），包含 task_id / steps / completed / final_output
- 轨迹块不会影响你回答用户的最终结果，用户看到的是你正常的回答

开始执行吧。task_id = "synthetic-main"
```

## 子 agent D：E4 反例（每条一次 spawn）

```
你现在扮演一个加载了 {skill_name} skill 的助手。用户向你发送一个请求：

<用户请求>
{counter_example.scenario}
</用户请求>

你必须：
（同 C，隔离要求一致）

task_id = "{counter_example.id}"

开始执行吧。
```

## 隔离的技术实现

在 Claude Code Agent 工具调用中：

- 用 `subagent_type: "general-purpose"` 或 `Explore`（有 Read/Grep/Glob，无 Edit/Write）
- prompt 明确"严禁读"清单是**核心屏障**
- 主 agent 事后自检：
  - 检查子 agent 返回内容里是否明显出现了禁止文件的特征（如 interview-record 的 `schema_version: 1`）
  - 若发现证据 → 标 `isolation: violated`

## 降级

| 场景 | 降级方式 |
|------|---------|
| 主 agent 没有 Agent 工具 | 全局降级为 `soft isolation`：主 agent 按 prompt 自己做 A/B/C/D 的工作，各角色之间用"角色切换"声明。报告 `isolation: soft`，overall_score 标 `confidence: lower` |
| Agent 工具调用失败 | 重试 1 次；仍失败 → 该角色任务降级为主 agent 自己做，标该维度 `integrity: degraded` |
| 子 agent 超时 | C/D 10 分钟超时 → 标 `skipped: timeout`，该条不算入 coverage |
| 子 agent 返回格式乱 | 最佳努力解析；仍无法 → 标 `parseability: fail`，该维度子分按 N/A 处理 |

## 违规的具体处置

**发现子 agent 确实读了 interview-record.md**：

- A 角色：整个 E1 作废，不信任任何标签结果。报告 fidelity 标 `skipped: isolation_violated`，fidelity_score 不计入 overall_score（权重转嫁给其他维度按比例放大）
- B 角色：E2 作废同理
- C / D 角色：E4 作废同理

权重转嫁规则（举例）：

- 正常：fidelity 0.30 + readability 0.20 + behavior 0.35 + contract 0.15
- fidelity 作废：剩下三项按 0.20/0.35/0.15 比例重新归一 → readability 0.286, behavior 0.5, contract 0.214
- 报告中显式记录转嫁事实

## 子 agent 日志保存

每次 spawn 的 prompt + 返回内容归档到：

```
{skill_dir}/.eval/trace-{YYYYMMDD-HHmm}.md
  ## A-prompt ...
  ## A-response ...
  ## B-阶段一-prompt ...
  ## B-阶段一-response ...
  ## B-阶段二-prompt ...
  ## B-阶段二-response ...
  ## 合成任务 (C) ...
  ## 反例 CE-1 (D) ...
  ## 反例 CE-2 (D) ...
  ...
```

保留 prompt 用于事后复现与隔离审计。
