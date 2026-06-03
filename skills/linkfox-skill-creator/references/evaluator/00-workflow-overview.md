# 00 评估流程总览

本文档定义 Evaluator 的状态机、执行顺序、hard gate 规则。阅读本 skill 的任何 agent，在进入具体维度前必须先对照本文档确认当前状态。

## 状态机

```
[启动]
  ↓
[定位目标 skill] ── 找不到或不是 Creator 产出 ──→ [终止，告知用户]
  ↓
[E3 契约检查]
  ├─ fail ──→ [写部分报告：仅 E3] ──→ [终止，advice=block]
  └─ pass
      ↓
  [E2 可读性]
    ├─ score < 60 ──→ [写部分报告：E3+E2] ──→ [终止，advice=block]
    └─ score ≥ 60
        ↓
    [E1 忠实度]（评分，不 gate）
        ↓
    [E4 行为符合]（评分，不 gate）
        ↓
    [汇总 overall_score + publish_advice]
        ↓
    [写完整报告] ──→ [结束]
```

## 四个阶段的职责切分

| 阶段 | 谁在做 | 输入 | 输出 |
|------|-------|------|------|
| 定位目标 skill | 主评估 agent | 用户输入 / 上一会话 handoff | skill 目录绝对路径 |
| E3 契约 | 调用 `linkfoxskill skill lint <name> --json` | skill 目录 | `{passed, issues[]}` |
| E2 可读性 | 主评估 agent spawn 子 agent B | 目标 skill | 10 项打分 + score |
| E1 忠实度 | 主评估 agent spawn 子 agent A + 对照 interview-record | 目标 skill（不含 interview）、interview-record.md | 每条 process/rule 的标签 + score |
| E4 行为 | 主评估 agent spawn 子 agent C + D | 合成任务、反例集、目标 skill | 轨迹文件 + 多个子分 + 综合 score |
| 汇总 | 主评估 agent | 前四个阶段结果 | 报告 YAML frontmatter + markdown 详情 |

## Hard gate 规则

### E3 hard gate

- 只要 `contract.passed = false`（任一 C1-C10 fail），整个评估立刻终止
- 写一份"部分报告"：
  - `dimensions_evaluated: [e3]`
  - `overall_score: 0`
  - `publish_advice: block`
  - `blocking_issues`：列出所有 fail 的 check
  - `recommended_fixes`：每条 fail 给具体修复建议，引用 linter 原始 issue id
- 不 spawn 任何子 agent

### E2 hard gate

- `readability_score < 60`（通过不到 6 项）→ 终止
- 写一份"部分报告"：
  - `dimensions_evaluated: [e3, e2]`
  - E3 full
  - E2 full（含 10 项明细与具体 evidence）
  - `overall_score: 0`
  - `publish_advice: block`
  - `blocking_issues`：列出未通过的 E2 项
  - `recommended_fixes`：指向具体文件哪里应该补充或简化
- 不 spawn 子 agent C/D（E4 不跑）

### 为什么要 gate

- E3 fail：文件结构坏了，`deterministic: true` 的步骤找不到脚本，frontmatter 不合法……这种情况下跑 E1/E2/E4 都是在测一个"结构本身不完整"的东西，子 agent 会被乱文件误导。
- E2 fail：没人能看懂这个 skill。跑 E4 相当于测子 agent 瞎猜的行为，不反映 skill 本身。先让作者把 SKILL.md 和 references 捋清再说。

### 为什么 E1 / E4 不 gate

- 它们返回的是分数 + 标签，用户可以按严重度逐条改。二元通过/不通过不如明细单有用。
- E1 中的 `missing` 或 `hallucinated` 是重度扣分，但报告可以让用户看到"哪个步骤丢了 / 哪个规则是脑补"，比整体 fail 信息量大得多。

## 部分评估（--only）

用户明确要求"只重跑 E1 E2"：

1. 读上一份最新 `.eval/report-*.md`
2. 只对 `--only` 指定的维度重新评估
3. 其他维度复用上份结果，但在新报告中标 `from_cache: true` 并记录上份报告路径
4. `overall_score` 仍按完整公式算（使用缓存的分数）
5. `dimensions_evaluated` 列本次实际评的维度
6. `publish_advice` 按新 overall_score 给

**不允许的组合**：
- `--only e4` 但 E3 上一份是 fail：拒绝，提示"E3 fail 状态下 E4 不能跑，请先修 E3"
- `--only e2` 但没有上一份报告：拒绝，首跑必须全量

## 状态转移表

| 当前状态 | 事件 | 下一状态 | 产物 |
|---------|------|---------|------|
| 启动 | 用户触发 | 定位目标 | — |
| 定位目标 | 找到 skill | E3 | — |
| 定位目标 | 找不到 | 终止 | 告知 |
| E3 | pass | E2 | contract 结果 |
| E3 | fail | 写部分报告 | contract 结果 |
| E2 | score ≥ 60 | E1 | readability 结果 |
| E2 | score < 60 | 写部分报告 | readability 结果 |
| E1 | 完成 | E4 | fidelity 结果 |
| E4 | 完成 | 汇总 | behavior 结果 |
| 汇总 | 完成 | 结束 | 完整报告 |

## 路由到 references 的规则

- 进入 E3：读 `03-e3-contract.md`
- 进入 E2：读 `02-e2-readability.md` + spawn B 前先读 `08-sub-agent-protocol.md`
- 进入 E1：读 `01-e1-fidelity.md` + spawn A 前先读 `08-sub-agent-protocol.md`
- 进入 E4：读 `04-e4-behavior.md`, `05-synthetic-task.md`, `06-counter-example.md`, `07-trace-format.md`，spawn C/D 前读 `08-sub-agent-protocol.md`
- 写报告：读 `09-report-schema.md`

## 时间预算

- E3：< 3 秒（CLI 调用）
- E2：~2 分钟（单次 spawn）
- E1：~3 分钟（单次 spawn + 对照）
- E4：~10-15 分钟（2 次 spawn + 轨迹处理）
- **总计目标：< 30 分钟**

超时（> 45 分钟）：写当前已完成维度的报告，未完成维度标 `skipped: timeout`。
