# 02 E2 可读性评估

回答一个问题：**一个没有背景的新 agent 第一次读这份 skill，能不能在 3 个问题内说清"何时触发、下一步读什么、要避免什么"？**

## 方法

### 步骤 1：spawn 子 agent B，阶段一（三问）

prompt 只暴露 SKILL.md 一个文件，问 3 个问题：

```
你读完这份 SKILL.md，请回答：
1. 什么情况下我应该调用这个 skill？
2. 如果要调用，我应该先读哪个文件？
3. 这个 skill 最容易出错的地方是什么？

请用最简短的语言回答，不要编造 SKILL.md 没写的内容。
如果 SKILL.md 里没写清楚某一问的答案，如实说"没说清楚"。
```

### 步骤 2：spawn 子 agent B，阶段二（执行图）

把 `references/*.md` 全部给它（仍然不给 interview-record.md），要求它画出执行图：

```
请根据 SKILL.md 和 references/ 里的文件，画出这个 skill 的执行图：
- 主流程步骤（按顺序列出）
- 每步的决策分支（如果有）
- 脚本调用点（如果有）

用 ASCII 图或有序列表表达即可。
```

### 步骤 3：主评估 agent 按 10 项清单打分

每项 10 分，通过得 10 分，不通过得 0 分，满分 100 分。

| # | 检查项 | 判定方法 |
|---|--------|---------|
| 1 | "何时触发"三问答案准确 | 子 agent B 阶段一问 1 的答案，主 agent 对照 description + 正文"何时使用"，≥ 80% 意图一致 |
| 2 | "先读哪个文件"有明确指向 | 问 2 答出了具体文件名（如 `references/workflow.md`） |
| 3 | "最易出错点"命中 D5 | 问 3 的答案与 `references/rules-and-boundaries.md` 的边界或踩坑章节有 ≥ 1 条直接对应 |
| 4 | 执行图至少 3 步 | 阶段二画出的主流程步骤 ≥ 3 步 |
| 5 | 执行图决策分支无歧义 | 子 agent B 没说"这里不清楚" / "看不出下一步"；主 agent 对照 workflow.md 也未发现分支遗漏 |
| 6 | 内部一致性 | SKILL.md / workflow.md / rules-and-boundaries.md 三者无明显矛盾：同一 step id、同一规则 id、同一 script 路径应前后一致 |
| 7 | SKILL.md ≤ 200 行 | 文件行数 |
| 8 | 无技术术语泄漏 | 扫描 SKILL.md 正文，不应出现 `prompt` / `frontmatter` / `tokens` / `YAML` / `schema` / `LLM` / `agent`（在路由说明中 "agent" 可出现）/ `JSON` / `API` / `regex` 等；允许在 `references/` 的协议类文件（如 07/08/09 号）中出现 |
| 9 | scripts 调用点说明 | SKILL.md 或 workflow.md 中，每个 `scripts/*.py` 都有明确的"何时调、参数是什么、输出如何读"三件说明 |
| 10 | 触发语覆盖 ≥ 6 种口语 | description 或"何时使用"列表中，至少 6 种不同的用户口语表达（如：帮我检查 / 过一遍 / 打个分 / 能用吗 / 质量如何 / 看一下） |

## 评分公式

```
readability_score = 通过项数 × 10
```

**Hard gate 阈值：60 分**（至少通过 6 项）。

## 打分细则

### 关于"何时触发"准确（#1）

子 agent B 阶段一给出的答案与 SKILL.md "何时使用"或 frontmatter description 意图是否一致：

- 若子 agent B 说的触发场景是 SKILL.md 里写过的 → 通过
- 若子 agent B 编造了 SKILL.md 没写的触发场景 → **不通过**（这条特别严重，说明 description 引导错了）
- 若子 agent B 明确说"SKILL.md 没说清楚什么时候用" → 不通过

### 关于"最易出错点"命中 D5（#3）

子 agent B 的回答需与 `references/rules-and-boundaries.md` 或 SKILL.md "典型踩坑"章节中的某一条有直接对应。**仅仅泛泛说"可能理解错业务"不算命中**——必须对应具体踩坑条目。

### 关于内部一致性（#6）

主评估 agent 做的机械检查：

- SKILL.md 引用的 `references/` 文件是否都存在
- workflow.md 里的 step id 是否和 SKILL.md 里的 step id 一致
- rules-and-boundaries.md 里的 rule id 是否在 workflow.md 里被正确引用
- scripts 路径在 SKILL.md / workflow.md 中是否完全一致（不能一处是 `scripts/check-brand.py` 另一处是 `scripts/check_brand.py`）

任一项不一致 → 本项不通过，evidence 里引用原文行号。

### 关于术语泄漏（#8）

黑名单（严格）：`prompt` `frontmatter` `tokens` `LLM` `JSON`（SKILL.md 正文中出现即算泄漏；在代码块示例内出现不算）`API`（同左）`regex` `parse` `YAML`（同 JSON 规则）`schema`

允许：`agent` 在"spawn 子 agent"等表述中出现（若 SKILL.md 没有明确 spawn 子 agent 的语境，仍算泄漏）

**判定原则**：SKILL.md 是给没有背景的人读的，技术词出现 = 可读性扣分。`references/` 内部的技术协议文件（07/08/09）不受此约束。

### 关于触发语口语覆盖（#10）

description 字段里"触发："后面的口语列表 + "何时使用"条目中的口语短语，合计统计去重后 ≥ 6 种不同表达。

## 输出结构

```yaml
readability:
  score: 80
  pass_count: 8
  checks:
    - id: 1
      name: "何时触发三问准确"
      passed: true
      note: "子 agent B 答'用户生成新 skill 后自动触发'，与 SKILL.md 一致"
    - id: 2
      name: "先读哪个文件明确"
      passed: true
      note: "子 agent B 答 references/00-workflow-overview.md"
    - id: 3
      name: "最易出错点命中 D5"
      passed: false
      note: "子 agent B 答'可能理解错业务'，未命中 rules-and-boundaries.md 任何具体踩坑"
    # ...
  agent_b_answers:
    when: "用户生成新 skill 后自动触发"
    first_file: "references/00-workflow-overview.md"
    pitfall: "可能理解错业务"
  agent_b_execution_graph: |
    E3 → E2 → E1 → E4 → 汇总
    （执行图简述）
```

## 子 agent 隔离确认

spawn 子 agent B 前，主 agent 必须：

1. 在 prompt 中明确列出允许读的文件（绝对路径）
2. 在 prompt 中明确禁止的文件
3. 选择 `Explore` 或 `general-purpose` 子 agent 类型，避免 Plan 类 agent 把 interview-record 当作"上下文补充"

违反隔离（子 agent 声称读过 interview-record）→ 记录 `isolation: violated`，但继续评估；报告中该维度标 `integrity: suspect`。
