# 01 E1 忠实度评估

回答一个问题：**skill 里写的东西，是不是专家真说过的？**

## 5 种标签

对 skill 中的每一条流程步骤（process.step）和每一条规则（rules.rule）打一个标签：

| 标签 | 含义 | 扣分 |
|------|------|------|
| `match` | skill 里的这条，跟 interview-record 里专家原话对得上（可能改了用词但意图明确一致） | 0 |
| `drift` | 意图一致但细节或用词发生了变化，可能影响执行理解 | 5 |
| `over_generalized` | skill 把专家说的具体规则泛化了（如把"品牌库精确匹配"写成"品牌扫描"） | 10 |
| `missing` | 专家说过但 skill 里完全没有 | 15 |
| `hallucinated` | skill 里有但 interview-record 里找不到出处 | 15 |

## 评分公式

```
fidelity_score = max(0, 100 - (drift×5 + over_generalized×10 + missing×15 + hallucinated×15))
```

累加扣分取上限 100、下限 0。

## 执行步骤

### 步骤 1：spawn 子 agent A 做盲读提取

用 Agent 工具 spawn 一个子 agent，description 简短，prompt 包含以下要素：

```
你只能读以下三个文件：
  {skill_dir}/SKILL.md
  {skill_dir}/references/workflow.md
  {skill_dir}/references/rules-and-boundaries.md

不得读：
  {skill_dir}/references/interview-record.md
  {skill_dir}/.eval/ 下任何文件

请输出两个列表，结构化 JSON：

{
  "process": [
    { "id": "step_1", "name": "...", "description": "...", "deterministic": true|false }
  ],
  "rules": [
    { "id": "R1", "text": "...", "type": "hard|soft" }
  ]
}
```

期望子 agent 返回结构化 JSON。若返回自然语言，主 agent 自行做最佳努力结构化。

### 步骤 2：读 interview-record.md（主 agent）

子 agent 返回后，主 agent 打开 `{skill_dir}/references/interview-record.md`，解析其 frontmatter YAML（schema v1），提取：

- `process[]` — 专家原始流程列表
- `rules[]` — 专家原始规则列表

### 步骤 3：结构化比对

对 process 和 rules 分别做匹配：

**process 比对**：

1. 先按 `id` 直接匹配（如果 id 命名规范一致）
2. 若 id 不一致，按 `name` 模糊匹配（去空格、去标点、小写）
3. 若都不一致，按语义内容匹配（description + inputs + outputs 组合相似度）

匹配到之后打标签：
- `name + description + deterministic` 都对上 → `match`
- 意图一致但表述明显改了（如把"品牌库匹配"变成"品牌识别"）→ `drift`
- 原话是"精确匹配品牌库"，skill 写成"语义判断是否蹭品牌" → `over_generalized`
- interview-record 有但 skill 里找不到对应 step → `missing`
- skill 里有但 interview-record 里找不到任何对应项 → `hallucinated`

**rules 比对**（同样方法）：
- 按 `id` / `text` 依次匹配
- hard 规则比 soft 规则更严格（hard 被泛化或丢失尤其严重，需在报告 recommended_fixes 里重点标出）

### 步骤 4：hallucinated 特殊处理

若发现 `hallucinated`，主评估 agent 附加一个提示：

> 标 hallucinated 的条目可能是专家口头补充但未更新到 interview-record.md。建议请专家确认：
> - 是 Creator 误加 → Creator 应删除
> - 是专家后补但忘了记 → 专家确认后应补充 interview-record.md

这个提示写入报告的 `recommended_fixes`，不直接决定删留。

## 输出结构

```yaml
fidelity:
  score: 78
  process_analysis:
    match:
      - id: step_1
        skill_id: step_1
        interview_id: step_1
      - id: step_2
        skill_id: step_2
        interview_id: step_2
    drift: []
    over_generalized:
      - skill_id: step_3
        interview_id: step_3
        skill_text: "品牌扫描"
        interview_text: "按品牌库精确匹配关键词"
        evidence: SKILL.md:L27
    missing: []
    hallucinated: []
  rules_analysis:
    match: [R1, R2]
    drift: []
    over_generalized: []
    missing:
      - interview_id: R4
        interview_text: "title 出现 'FDA Registered' 必须标违规"
    hallucinated:
      - skill_id: R_extra
        skill_text: "title 不能超过 80 字"
        evidence: rules-and-boundaries.md:L45
```

## 边界情况

| 情况 | 处理 |
|------|------|
| interview-record.md 不存在 | E3 应该已经 fail（C3 check）——不会走到 E1 |
| interview-record schema 非 v1 | E3 fail |
| process 或 rules 在 interview 中为空 | 主 agent 在 E1 报告里标"访谈不完整：process 为空，建议请专家补充后重评" |
| 子 agent A 返回格式混乱 | 主 agent 尝试解析；仍失败则降级为主 agent 自己读 SKILL.md/workflow.md/rules-and-boundaries.md 并做对照，报告中 `isolation` 字段标 `degraded` |
| 子 agent A 声称读不到文件 | 检查路径正确性；若确因工具原因隔离失败，降级为 soft 隔离（主 agent 自读），报告 `isolation: soft` |

## 反向检查

做完比对后，主 agent 自检：
- 总条目数（process + rules）是否合理（< 3 条说明子 agent 盲读效果差，应重试）
- `match` 比例 > 80% 时，重点核查是否真的都 match（有时是"口头 match 但细节有 drift 没发现"）
- `missing` 列出来之后，对照 interview-record 全文再扫一遍，避免漏掉

## 与 E4 的联动

E1 标的 `over_generalized` 或 `missing` 的规则，在 E4 行为测试时应优先覆盖：如果该规则也没被子 agent C/D 的轨迹触发，说明这条规则不仅被 skill 忽略、在执行时也被忽略了——是双重缺陷，报告中合并展示。
