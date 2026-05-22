# 06 反例集构造

E4 除了合成任务，还需要一组反例——"看似合规实则违规 / 该拒绝的场景 / 已知踩坑"——专门测 skill 的边界识别。

## 反例集的来源（3 类，按优先级）

| 来源 | 说明 | 置信度 |
|------|------|-------|
| P1：`pitfalls`（踩坑） | 专家在访谈中明确说过"新人常踩的坑"，带 expert_verbatim | 最高（gold） |
| P2：`boundaries`（不适用场景） | 专家明确列了"本能力不覆盖" | 高 |
| P3：inferred（推导反例） | 从 `rules`（尤其 hard 规则）反推"如果用户输入看似合规但暗藏违反这条规则" | 中 |

**比例建议**：pitfalls ≥ 1 条，boundaries ≥ 2 条，inferred 补到总共 3-8 条。太少覆盖不足，太多 E4 时间爆炸。

## 构造方法

### P1：pitfalls 直接转反例

interview-record 的 `pitfalls[]` 已经是结构化反例，直接用：

```yaml
- id: P1-1
  source: pitfall
  scenario: "title 写 'FDA Registered' 但实际未注册 FDA"
  expert_verbatim: "常见踩坑，很多卖家以为写上这个显得专业，其实是高风险虚假声明"
  rule_targeted: R4  # 对应规则 id
  expected_behavior: "skill 应识别为虚假声明，按 R4 规则处理（警告 / 拒绝 / 标记）"
```

### P2：boundaries 转反例

interview-record 的 `boundaries[]` 描述"不适用场景"。构造成用户请求：

```yaml
- id: P2-1
  source: boundary
  scenario: "用户问的是 Shopify 独立站 listing 的合规性，而本 skill 专做 Amazon"
  expected_behavior: "skill 应识别为不适用，拒绝处理并建议用户换工具"
  construction: |
    模拟用户说："帮我看下这条我 Shopify 店的 listing 有没有合规问题：
    title xxx, brand xxx, ...（同 Amazon 那种场景，但明示平台是 Shopify）"
```

### P3：从 rules 推导

针对每条 hard 规则，设计"看似合规但违反规则"的场景：

```yaml
- id: P3-1
  source: inferred
  rule_targeted: R3
  rule_text: "品牌库匹配：title 若含品牌库中的品牌名，brand 字段必须完全一致"
  scenario: "title 含 'compatible with AirPods'，brand 字段填 'SonyBeats'——看起来 brand 很特别不像大厂，但 title 中 AirPods 命中品牌库"
  expected_behavior: "skill 应触发 R3 判定为蹭品牌"
  construction_note: "关键在'compatible with'看似合规描述，实则仍命中品牌库关键词"
```

## 反例的质量要求

- **看似合规**：表象上不违规（如果一眼看出来是违规，skill 识别它就没难度）
- **挂一个明确的 rule id 或 boundary id**：用于在报告里对应"哪条规则 / 哪条边界该起作用"
- **单点聚焦**：一条反例只测一个规则或边界，不要混合（否则失败时不好归因）
- **避免与合成任务重复**：合成任务已经覆盖主流程；反例专注**边界与异常**

## 反例测试执行

对每条反例开一个独立 spawn（子 agent D），**不共用上下文**：

```
用户请求：{reply_example.scenario}
```

判定"正确处理"的 3 种合法响应：

1. 识别为"不是我该干的"并拒绝
2. 按规则要求的行为执行（如触发 R4 → 标违规）
3. 按踩坑提示的避免方法执行（如 pitfall 说"应拒答"，子 agent 确实拒答了）

判定"错误处理"：

- 按正常流程硬跑（没识别出边界）
- 识别但判断方向错（如把"不适用"当成"适用但谨慎处理"）

## 覆盖度建议

反例集应尽量覆盖：

- 每条 hard 规则：至少 1 条反例测它
- 每条 boundary：至少 1 条反例测它
- 每条 pitfall：直接转 1 条反例

若 hard 规则有 5 条 + boundaries 3 条 + pitfalls 2 条 = 10 条目源 → 反例集上限 8 条（超过上限后按规则/踩坑优先级抽样）。

## 输出结构

```yaml
counter_examples:
  - id: P1-1
    source: pitfall
    scenario: "..."
    expected_behavior: "..."
    rule_targeted: R4
    expert_verbatim: "..."
  - id: P2-1
    source: boundary
    scenario: "..."
    expected_behavior: "..."
    boundary_targeted: B1
  - id: P3-1
    source: inferred
    scenario: "..."
    expected_behavior: "..."
    rule_targeted: R3
    construction_note: "..."
coverage_stats:
  pitfalls_total: 2
  pitfalls_covered: 2
  boundaries_total: 3
  boundaries_covered: 3
  hard_rules_total: 5
  hard_rules_with_inferred_example: 3   # 未必每条 hard 都 infer 得出来
```

## 降级

- **interview-record.pitfalls 为空** → 这是 D5 必挖维度，E3 的 C3 应会发现。若仍走到这里，反例集只有 boundaries + inferred
- **boundaries 也为空** → skill 本身挖得不够，报告显眼位置提示"访谈 D5 维度缺失，反例集仅能从 rules 推导，置信度降低"
- **hard rules 也为空** → skill 质量极低，E4 反例部分几乎无内容可测，`boundary_recognition_pct` 置 N/A，权重转嫁

## 陷阱：不要让反例"作弊"

反例的 `scenario` 字段**不能**包含以下内容（会泄漏给子 agent D）：

- "这是一个反例"
- "测试 R3 规则"
- "你应该拒绝"
- 任何直接指向 skill 内部 id 的表述

反例必须以**用户口吻**呈现，子 agent D 应该在不知道这是反例的情况下做出判断。
