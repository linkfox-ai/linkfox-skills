# 05 合成任务构造

E4 需要一个"真实、覆盖分支、能触发主流程"的任务喂给子 agent C。本文档定义这个任务怎么编。

## 目标

构造**一个任务**（必要时可以是多任务组合，但建议一个主任务），使得：

- 目标 skill 定义的**主流程每个分支**被至少覆盖一次
- 任务描述**看起来像真实用户口吻**，不是抽象的"请测试 step_2"
- 任务内容**基于 D1 业务情境**（interview-record.scenario），不凭空捏造
- 任务有具体数字、具体名字、具体字符串——让子 agent 必须真处理

## 构造流程

### 步骤 1：读 interview-record 的 D1 和 D3

- `scenario`：描述 / primary_user / typical_trigger_moment / success_criteria
- `process`：步骤列表（每步有 inputs / outputs / decisions）

### 步骤 2：识别分支

扫描 `process`：

- 每个 step 的 `decisions` 字段列了"如果 X 则 Y，否则 Z"这种判定 → 这是一个分支
- 每条规则的 hard/soft 类型 → 至少应有一个任务让 hard 规则被检查
- deterministic step 的输出分支（脚本可能返回"match/mismatch"） → 至少一个任务能触发每个输出

### 步骤 3：选一个"覆盖最多分支的参数组合"

不要分支爆炸造 10 个任务。**一个任务尽量覆盖多个分支**，通过"输入参数的多维度巧合"实现：

例：skill 是"Amazon listing 侵权检查"，有这些分支：

- step_2 分支：title 含品牌关键词 vs 不含
- step_3 分支：brand 字段与 title 中品牌一致 vs 不一致
- step_4 分支：品类是否是"易发侵权高危品类"

**合成任务可以是**：

> 我有一条 listing，title 是 "Wireless Bluetooth Earbuds Compatible with AirPods Pro"，brand 填 "SonyBeats"，品类是 Electronics → Audio Headphones，价格 $29.99。帮我看看有没有侵权风险。

这一条任务同时触发：
- step_2：title 含品牌（AirPods）
- step_3：brand 不一致（SonyBeats ≠ AirPods）
- step_4：Electronics 是高危品类

### 步骤 4：口语化

构造好的"参数组合"要翻译成用户口吻：

- 不要写 "请按流程 step_1 到 step_5 执行"
- 要写 "我有一条 listing 想发，帮我看下有没有啥问题"
- 数据点可以自然带入用户描述中

### 步骤 5：避免"提示词泄漏"

合成任务**不能**包含：

- 目标 skill 的 step id（"请先做 step_2"）
- 目标 skill 的 rule id（"注意 R3"）
- 目标 skill 的 scripts 路径（"调 scripts/check.py"）
- 暗示性关键词（"请务必调用脚本而不是自己算"）

这些会污染子 agent C 的行为，导致评估失真。

## 分支覆盖清单

构造完任务后，主 agent 自检一张表：

| 分支来源 | 分支描述 | 是否被本任务触发 |
|---------|---------|----------------|
| step_2.decisions | title 含品牌关键词 | ✅ |
| step_2.decisions | title 不含品牌关键词 | ❌ (需另一任务或放弃) |
| step_3.decisions | brand 一致 | ❌ |
| step_3.decisions | brand 不一致 | ✅ |
| ... | ... | ... |

**目标**：单任务覆盖率 ≥ 60%。若 < 60%，追加一个补充任务。**最多 2 个任务**（以控制 E4 时间）。

## 任务描述的质量要求

- **具体**：有真实可查的字段值，不要"某款商品"
- **完整**：一次提供子 agent 需要的所有字段，避免来回问
- **不过度**：不要写 500 字的场景描述，100-150 字足够
- **业务真实**：数字合理（$29.99 比 $1 合理）、字段命名合理（brand 字段值像品牌名，不是"abc"）

## 输出

```yaml
synthetic_task:
  description: |
    我有一条 listing 想发，title 是 "Wireless Bluetooth Earbuds Compatible
    with AirPods Pro"，brand 填 "SonyBeats"，品类是 Electronics → Audio
    Headphones，价格 $29.99。帮我看下有没有侵权风险。
  coverage_map:
    - branch: "step_2: title 含品牌关键词"
      expected: true
      trigger_field: "title 中 'AirPods'"
    - branch: "step_3: brand 与 title 品牌不一致"
      expected: true
      trigger_field: "brand=SonyBeats ≠ title 中 AirPods"
    - branch: "step_4: 高危品类"
      expected: true
      trigger_field: "Electronics → Audio"
    - branch: "step_2: title 不含品牌"
      expected: false
      reason: "single-task budget doesn't cover this; acceptable trade-off"
```

## 降级

- 若 interview-record 的 scenario 描述不足以支撑"具体数字" → 主 agent 按行业常识填空，但在 `synthetic_task.assumptions` 字段记录哪些是补齐的
- 若 process 步骤太少（< 3）→ E3 应该已经 fail，但此处冗余检查一次；若仍小于 3，合成任务仍按流程来，coverage_pct 权重自动降低（step 少）
- 若 skill 完全没有 decisions（每步都是"必经步骤"） → 任务构造简化为"走一遍流程"，单任务覆盖率 = 100%

## 真实度判定（MVP 版）

MVP 阶段靠 LLM 自审：主 agent 构造完任务后，再问自己一次"这个任务场景真实吗？跨境电商卖家真会遇到吗？"——若自审觉得牵强，重构造。

未来版本：引入平台样本库（从 linkfox-skills-api 的真实查询日志里抽样作为种子），提高真实度。
