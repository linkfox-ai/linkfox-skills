# 09 评估报告 schema

报告文件路径：`{skill_dir}/.eval/report-{YYYYMMDD-HHmm}.md`。

每次评估产生一份新的报告，**不覆盖**历史。最新报告供 `linkfoxskill skill eval-report` 展示。

## 结构

报告 = YAML frontmatter（机读） + markdown 详情（人读）。

## Schema v1 – YAML frontmatter

```yaml
---
schema_version: 1
skill_name: linkfox-amazon-listing-infringement-check
skill_path: /abs/path/to/skill
evaluator_version: 1.0.0
model: claude-opus-4-7
created_at: 2026-04-27T15:30:00+08:00
elapsed_ms: 142000
dimensions_evaluated: [e1, e2, e3, e4]   # 或部分，如 [e3] / [e3, e2]
from_cache:                              # 若 --only 部分重跑，这里列沿用的维度
  e3: .eval/report-20260425-1000.md
trace_file: .eval/trace-20260427-1530.md
isolation: strict                        # strict / soft / violated

# ----- E3 契约 -----
contract:
  passed: true
  checks_total: 10
  checks_passed: 10
  issues: []
  # 或：
  # passed: false
  # issues:
  #   - check_id: C1
  #     check_name: "frontmatter 合法"
  #     severity: error
  #     file: SKILL.md
  #     line: 3
  #     message: "description 字段少于 50 字"

# ----- E2 可读性 -----
readability:
  score: 80              # 0-100，通过项数 × 10
  pass_count: 8
  threshold: 60
  passed_gate: true
  checks:
    - id: 1
      name: "何时触发三问准确"
      passed: true
      note: "..."
    - id: 2
      name: "先读哪个文件明确"
      passed: true
      note: "..."
    # ... 10 项
  agent_b_answers:
    when: "..."
    first_file: "..."
    pitfall: "..."
  agent_b_execution_graph: |
    ...

# ----- E1 忠实度 -----
fidelity:
  score: 78
  process_analysis:
    total: 5
    match: [ { skill_id: step_1, interview_id: step_1 } ]
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
    total: 6
    match: [R1, R2, R3]
    drift: []
    over_generalized: []
    missing:
      - interview_id: R4
        interview_text: "title 出现 'FDA Registered' 必须标违规"
    hallucinated:
      - skill_id: R_extra
        skill_text: "title 不能超过 80 字"
        evidence: rules-and-boundaries.md:L45
        note: "interview-record 中找不到对应条目；可能是 Creator 误加，或专家口头补充未更新记录"

# ----- E4 行为 -----
behavior:
  score: 72
  coverage_pct: 85
  rule_compliance_pct: 80
  boundary_recognition_pct: 67
  script_used_pct: 100
  order_correctness_pct: 100
  synthetic_task:
    description: "..."
    coverage_map:
      - branch: "step_2: title 含品牌关键词"
        expected: true
        triggered: true
  counter_examples:
    - id: CE-1
      source: pitfall
      scenario: "..."
      expected_behavior: "触发 R4"
      actual: "skill 未识别，按正常流程"
      handled: false
  violations:
    - rule_id: R3
      step_id: step_4
      scenario: synthetic_main
      evidence: |
        trace:step step_4 的 ACTION 未触发品牌检查
      severity: high
  scripts_used:
    - script: scripts/check-brand-keywords.py
      invoked: true
      step_id: step_2
      invocation_source: trace_and_bash     # trace 自报 + Bash 日志双证
    - script: scripts/validate-title-length.py
      invoked: false
      bypass_reason: "step_3 是 LLM 自己数的字数，未调脚本"

# ----- 汇总 -----
summary:
  overall_score: 76
  publish_advice: warn    # block / warn / ok / excellent
  strengths:
    - "流程忠实度较高（fidelity=78）"
    - "所有被调用的脚本都真正执行（script_used_pct=100）"
  blocking_issues: []     # 若有 E3 fail 或 E2 fail，这里列
  recommended_fixes:
    - priority: high
      dimension: e1
      label: over_generalized
      target: "SKILL.md 步骤 3「品牌扫描」"
      fix: "改为'按品牌库精确匹配关键词'，与 interview-record process[2].expert_verbatim 对齐"
    - priority: high
      dimension: e1
      label: missing
      target: "rules-and-boundaries.md 缺 R4 '虚假 FDA 声明'"
      fix: "补充 R4 条目，文字引用 interview-record rules[3].expert_verbatim"
    - priority: high
      dimension: e1
      label: hallucinated
      target: "rules-and-boundaries.md 的 R_extra 'title ≤ 80 字'"
      fix: "interview-record 中无此规则；请专家确认后删除，或专家确认保留时补访谈记录"
    - priority: medium
      dimension: e4
      label: boundary_missed
      target: "反例 CE-1 (FDA Registered) 未被识别"
      fix: "在 rules-and-boundaries.md 的踩坑章节，把 FDA Registered 虚假声明的识别要点再写具体"
    - priority: low
      dimension: e4
      label: script_bypass
      target: "scripts/validate-title-length.py 在 step_3 未调用"
      fix: "在 SKILL.md 或 workflow.md 明确「step_3 必须调 scripts/validate-title-length.py，不要自己数字数」"
---

# 评估报告详情

（markdown 正文，下面详细叙述每个维度的具体 evidence）
```

## Markdown 正文部分

frontmatter 后的 markdown 内容按 4 个维度分段，每段展示该维度的具体证据。不必冗余 frontmatter 内容，只展开"重要的 fail/扣分项 + evidence 片段"：

```markdown
# {skill_name} 评估报告

评估时间：2026-04-27 15:30
评估器版本：1.0.0
综合得分：76 / 100（advice: warn）

## 契约（E3）✓ 通过

10/10 全部通过。

## 可读性（E2）✓ 通过 80 分

- #3 最易出错点命中 D5：**未通过**
  - 子 agent B 给出答案："可能理解错业务"
  - 该答案未命中 rules-and-boundaries.md 的任何具体踩坑
  - 修复建议：SKILL.md "何时不用"段加一句关键踩坑的指向

## 忠实度（E1）78 分

### process 分析

- step_3 **over_generalized**
  - skill 写作："品牌扫描"（SKILL.md:L27）
  - interview-record 原话："按品牌库精确匹配关键词"
  - 影响：执行 agent 可能误以为是语义判断

### rules 分析

- R4 **missing**（interview-record 有但 skill 缺）
  - interview-record 原话："title 出现 'FDA Registered' 必须标违规"
- R_extra **hallucinated**
  - skill 写作："title 不能超过 80 字"（rules-and-boundaries.md:L45）
  - interview-record 中无对应
  - 可能原因：Creator 误加 / 专家口头补充未更新

## 行为（E4）72 分

### 合成任务轨迹

…（节选 trace 关键片段）…

### 反例测试

- CE-1（pitfall：FDA Registered）**未处理**
  - 预期：触发 R4 虚假声明识别
  - 实际：按正常流程输出，未识别
- CE-2（boundary：Shopify 平台）**正确处理**

### 脚本调用

- scripts/check-brand-keywords.py ✓ 调用
- scripts/validate-title-length.py ✗ **未调用**（LLM 自己数字数）

## 综合建议

1. 补 R4 到 rules-and-boundaries.md
2. 删除 / 补齐 R_extra
3. 明确 step_3 必须调脚本而非 LLM 自算

（priority 顺序见 frontmatter recommended_fixes）
```

## advice 阈值判定

主评估 agent 在汇总阶段，按下表机械计算 `publish_advice`：

| 条件 | advice |
|------|--------|
| `contract.passed == false` 或 `readability.passed_gate == false` | `block` |
| `overall_score < 75` | `warn` |
| `75 ≤ overall_score < 90` | `ok` |
| `overall_score >= 90` | `excellent` |

## isolation 字段

- `strict`：所有子 agent 均通过 Agent 工具 spawn，未发现越界
- `soft`：某些角色降级为主 agent 代办（工具不可用），overall 的置信度应打折
- `violated`：某子 agent 被确认越界读了禁止文件，该维度作废并权重转嫁

## dimensions_evaluated

- 全量评估：`[e1, e2, e3, e4]`
- 部分重跑：只列本次跑的；沿用上份的在 `from_cache` 字典里列出
- E3 fail 终止：`[e3]`
- E2 fail 终止：`[e3, e2]`

## schema 升级规则

- 本文档是 v1
- 未来新增字段：必须保持 v1 字段不变，新字段追加
- 删除字段：触发 schema_version bump 到 v2，旧报告不兼容，CLI eval-report 需按版本分支解析

## 报告保留策略

- `.eval/` 下报告不自动清理，用户负责
- `linkfoxskill skill eval-report` 默认读 `report-*.md` 中最新（按文件名字典序）
- 报告是纯文本，可以 git track（但 `.gitignore` 默认忽略 `.eval/`，用户若要留档需手动 unignore）
