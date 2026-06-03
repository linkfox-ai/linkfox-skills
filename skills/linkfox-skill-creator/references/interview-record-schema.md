# interview-record.md Schema v1

`references/interview-record.md` 是整个 skill 的**真值源**。评估器、迭代、跨人协作都以它为准。本文档定义它的严格结构。

## 文件总体形态

```markdown
---
<frontmatter：结构化字段>
---

<body：访谈原稿按轮次归档>

<进度标记注释>
```

## Frontmatter 完整定义

```yaml
---
# 元信息
schema_version: 1                              # 当前版本恒为 1
skill_name: linkfox-<name>                     # 目标 skill 的名字（与 SKILL.md 一致）
expert: <expert-identifier-or-unknown>         # 专家标识；MVP 可以是名字、邮箱前缀
created_at: 2026-04-27T10:30:00+08:00          # ISO-8601
contributors: []                               # v2 预留：多专家协作。MVP 保持空数组

# D1 业务情境
scenario:
  description: <一句话，skill 做什么>
  primary_user: <谁用这个能力——岗位/角色>
  typical_trigger_moment: <什么时刻触发>
  success_criteria:
    - <成功标志 1>
    - <成功标志 2>

# D2 输入形态
inputs:
  - type: url | asin | keyword | image | table | json | text | other
    example: <具体例子>
    notes: <说明性备注，如"必须是商品详情页链接">
  - ...

# D3 核心流程
process:
  - step: 1
    name: <步骤名，业务语言>
    inputs: [<输入字段 1>, <输入字段 2>]
    decisions: [<决策 1>, <决策 2>]
    outputs: [<输出字段 1>]
    execution_type: script | llm | delegate    # 三选一，详见 06-delegate-discovery.md
    # 当 execution_type=script：
    script: scripts/<name>.py
    # 当 execution_type=delegate：
    delegates_to: linkfox-<sub-skill-slug>
    delegate_inputs_mapping:
      <sub_skill_param>: <来自哪里（D2 输入字段 / 专家给的常量 / 上一步输出）>
    delegate_confirmed_at: <ISO-8601>
    delegate_expert_quote: |
      <专家确认采纳时的原话>
    # 通用：
    expert_verbatim: |
      <专家原话，一字不改>
    assumed_fields: []                         # 列出本步骤中你补的字段
  - step: 2
    ...

# D4 关键规则
rules:
  - id: R1
    text: <规则内容>
    type: hard | soft
    scope: [<适用步骤或字段>]
    counter_example: <反例描述；硬规则可为 null>
    expert_verbatim: |
      <原话>
    assumed_fields: []

# D5 边界与踩坑
boundaries:
  - id: B1
    scenario: <不适用场景>
    why_not_applicable: <原因>
    expert_verbatim: |
      <原话>

pitfalls:
  - id: P1
    scenario: <踩坑场景>
    why_wrong: <为什么是坑>
    expert_verbatim: |
      <原话>

# D6 输出偏好（可选）
output_preferences:
  format: <表格 | 清单 | 报告 | 其他>
  style: <简洁 | 详细 | 按风险级别分组 | 其他>

# D7 外部依赖（可选，仅用于"自己写脚本调平台 API"的情形）
external_dependencies:
  - service: <服务名>
    purpose: <用途>
    auth_type: <api_key | oauth | none>
    env_vars: [<需要的环境变量>]

# 委托依赖（从 D3 的 delegate 步骤汇总而来）
depends_on: []                                 # ["linkfox-sellersprite-product-search", ...]，去重

# 委托搜索日志（每次搜索/展示/确认都追加一条，详见 06-delegate-discovery.md）
delegate_search_log: []

# 质量与审查
quality: ready | partial | draft               # 见 04-stage-3-generate.md
privacy_review: <timestamp 或 no_sensitive_declared_at_<timestamp>>
---
```

## Body 部分

Frontmatter 之后是**访谈原稿归档**，按时间顺序记录每一轮对话：

```markdown
## 第 1 轮访谈（2026-04-27 10:30）

**主持人**：您平时什么时候会想起来用这个能力？

**专家**：一般是上架前最后一步，我会让实习生跑一遍，但他们经常漏...

**主持人**：我理解您是说，目前靠手工流程但容易出错，对吗？

**专家**：对。

## 第 2 轮访谈（2026-04-27 10:45）

...
```

**Body 的用途**：
- 阶段 2 的批量确认需要回引用原话
- 评估器 E1 忠实度检查需要对照原稿
- 后续迭代时，可以看当时对话背景

**Body 的约束**：
- 必须按"你 + 专家"交替记录
- 时间戳精度到分钟
- 隐私处理：body 中凡含敏感信息的段落，整段标红或打码；原始版本保留在本地 `verbatim_original` 字段（不上传）

## 进度标记注释

文件**末尾**必有一行：

```html
<!-- interview-progress: round=<n> dim_done=[<D1..D5>] status=<status> -->
```

可能的 status 值：

| status | 含义 |
|--------|------|
| `kickoff_done` | 阶段 0 完成 |
| `interview_ongoing` | 阶段 1 进行中 |
| `interview_complete` | 阶段 1 完成，dim_done 含 D1-D5 全部 |
| `ready_to_generate` | 阶段 2 通过，可生成 |
| `complete` | 阶段 3+4 完成 |
| `interrupted` | 专家中途暂停 |

## 字段级约束

### expert_verbatim

- 必须一字不改
- 多行用 YAML 竖线块：`|`
- 允许口语、方言、省略句；不允许整理归纳
- 若内容敏感被替换：原字段改为脱敏版本，新增 `verbatim_redacted: true` 和 `redaction_note: <说明>`

### assumed_fields

- 数组形式
- 每项是**字段的 YAML 路径**，例如 `inputs[0].example` 或 `process[2].decisions`
- 阶段 2 确认后，确认的字段从数组中移除

### execution_type（D3 特有，每个 step 必填）

三选一：

| 值 | 含义 | 必须伴随的字段 |
|----|------|-------------|
| `script` | 规则可形式化，写脚本实现 | `script: scripts/<name>.py` |
| `llm` | 经验判断，靠下游 agent 的语言理解处理 | 无（脚本字段不存在） |
| `delegate` | 调用一个已有的 skill 完成 | `delegates_to` + `delegate_inputs_mapping` + `delegate_confirmed_at` + `delegate_expert_quote` |

选择规则（详见 `06-delegate-discovery.md`）：

1. 该步骤是否涉及专业第三方能力？→ 是，则必须先搜索现有 skill
2. 搜到候选并经**专家明确确认** → `delegate`
3. 搜不到或专家拒绝 → 退到 `script`（规则可形式化）或 `llm`（经验判断）

专家明确拒绝判定某一步 → 标 `execution_type: unknown`，阶段 3 默认按 `llm` 处理。

### delegates_to（D3 delegate 步骤特有）

- 必须是一个合法的 skill slug（`linkfox-xxx` 形式）
- 必须在 `delegate_search_log` 中能找到对应的 `expert_choice` 记录
- 必须同时出现在顶层 `depends_on` 数组中
- 专家只说了"用那个工具"但没点具体候选 → 不允许填；继续追问直到明确

### depends_on（顶层字段）

- 从 D3 所有 `execution_type: delegate` 步骤的 `delegates_to` 去重汇总
- 不允许手工加未在 process 中出现的 slug
- 评估器 E3 会检查这里每一条在本地或云端可解析

### refused

- 任何字段可附带 `refused: true` 表示专家拒答
- 整维被拒 → 该维的顶层字段（如 `rules`、`boundaries`）置为空数组 + 加备注 `refused_by_expert: true`

## 与评估器（04 号文档）的契约

评估器在 E1（忠实度）维度会：
1. 读 frontmatter 的结构化字段
2. 对比 SKILL.md / references/workflow.md / references/rules-and-boundaries.md 中的每一条
3. 判定"生成内容是否 ⊆ interview-record 中的 `expert_verbatim` + 显式 decisions + `delegate_expert_quote`"
4. 任何超出 interview-record 的内容 → 标 `hallucinated`
5. `depends_on` 每一条必须能在 `delegate_search_log` 中找到 `expert_choice` 证据

**因此**：
- Creator **禁止**在生成文件时加入 interview-record 中没有的规则、步骤、边界
- Creator **禁止**在 `depends_on` 中加入未经专家确认的 skill
- 若 Creator 确实需要合理扩充（如从"价格过高"推断出"超过类目均价 200%"），必须：
  - 扩充内容归档到 `assumed_fields` 且阶段 2 确认
  - 或者追加一轮访谈把这条补进 `rules` 字段

## Schema 演进

MVP 恒用 v1。未来若需要 v2（比如引入多专家协作的 contributors 字段全量结构），：
- 新 schema_version = 2
- 写独立的迁移工具（`interview-record-migrator`）
- 不做 v1/v2 混合模式——要么全 v1 要么全 v2

## 完整示例（短小版）

```markdown
---
schema_version: 1
skill_name: linkfox-amazon-listing-infringement-check
expert: alice
created_at: 2026-04-27T10:30:00+08:00
contributors: []

scenario:
  description: 上架新品前做最终合规自查，防止 listing 上线后被投诉侵权下架
  primary_user: Amazon 运营
  typical_trigger_moment: 完成 listing 初稿，提交审核前最后一步
  success_criteria:
    - 发现明显的品牌侵权点
    - 给出修改建议

inputs:
  - type: url
    example: https://www.amazon.com/dp/B0XXXXXX
    notes: 必须是商品详情页链接

process:
  - step: 1
    name: 解析商品页
    inputs: [product_url]
    decisions: [抽取 title, brand, description]
    outputs: [structured_fields]
    execution_type: script
    script: scripts/parse-amazon-listing.py
    expert_verbatim: |
      进到商品页，把标题、品牌、描述这几个地方复制出来
    assumed_fields: []
  - step: 2
    name: 品牌字段合规判定
    inputs: [brand]
    decisions: [brand 含 generic 标红]
    outputs: [brand_risk_level]
    execution_type: script
    script: scripts/check-brand-compliance.py
    expert_verbatim: |
      brand 如果写 generic brand 那肯定不行
    assumed_fields: []

rules:
  - id: R1
    text: brand 字段含 generic 直接标红
    type: hard
    scope: [step_2]
    counter_example: null
    expert_verbatim: |
      generic brand 直接不合规

boundaries:
  - id: B1
    scenario: 商品链接已下架
    why_not_applicable: 无法提取字段
    expert_verbatim: |
      链接都挂了你让我查个啥

pitfalls:
  - id: P1
    scenario: 以为 unbranded 就安全
    why_wrong: 描述措辞可能一样有问题
    expert_verbatim: |
      很多新人以为 brand 写 unbranded 就没事

depends_on: []
delegate_search_log: []

quality: ready
privacy_review: no_sensitive_declared_at_2026-04-27T11:00:00+08:00
---

## 第 1 轮访谈（2026-04-27 10:30）

**主持人**：您平时什么时候会用这个能力？

**专家**：上架前最后一步，我会让实习生跑一遍...

<!-- interview-progress: round=3 dim_done=[D1,D2,D3,D4,D5] status=complete -->
```
