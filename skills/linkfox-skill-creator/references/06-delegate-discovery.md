# 委托候选的搜索与专家确认（D3 内置子流程）

当专家描述某个 D3 步骤时，若这一步**涉及专业第三方能力**（选品 / 竞品 / ABA / 关键词 / 评论 / 侵权检测 / 专利查询 / 物流 / 类目分析等），你必须先搜索现有 skill 是否能承担这一步，再决定写脚本还是委托。

搜索与确认完成后，该步骤的 `execution_type` 会落到三种之一：

- `script` — 没有现成 skill，规则可形式化，自己写脚本
- `llm` — 没有现成 skill，靠经验判断
- `delegate` — 有匹配的 skill，且**专家明确确认**采用

## 为什么要这么做

Agent 真正执行这个 skill 时，下游只会严格按 workflow.md 里写的"调用 `linkfox-xxx`"去触发 Skill 工具。如果我们从零写脚本抓数据，等于把专家多年信任的专业工具（卖家精灵、Keepa、Jiimore 等）的能力重新劣质实现一遍——结果不准，还浪费了账号和付费资源。

所以 **delegate 优先于 script/llm**；没有候选或专家不采纳，才退到自写。

## 触发条件（满足任一都要搜）

- 步骤提到具体平台：卖家精灵、SellerSprite、Keepa、ABA、Helium10、Jiimore、Ruiguan、Zhihuiya、Google Trends、Echotik、TSearch、DLD 等
- 步骤动词 ∈ {查 / 筛 / 采 / 找 / 评估 / 对比 / 挖掘 / 分析} + 领域对象 ∈ {商品 / 关键词 / 评论 / 竞品 / 品牌 / 类目 / 广告 / 专利 / 商标}
- 专家原话含"一般我用 XX 工具看……"
- 你判断是 deterministic，但标准库（requests / json / re）不足以快速形成稳定实现

## 搜索兜底链

按顺序执行。命中任一层 → 进入"展示给专家"；三层都未命中 → 进入"未命中处理"。

### 第一层：电商专业库

```bash
linkfoxskill search <关键词>
```

等价于全局 `/e-commerce-find-skills` 的搜索能力。关键词取"核心动作 + 对象"：`卖家精灵 选品`、`ABA 关键词流量`、`Keepa 历史价格`、`Jiimore 细分品类` 等。

### 第二层：通用库

电商库无果时，退到 `/find-skills` 的通用搜索路径。扩展关键词（去掉平台限定）再搜一次。

### 第三层：询问专家

两层都为空时，用业务语言告诉专家，给三个选项：

> "这一步您说要[按条件查 100 个竞品]。我在我们这边现成的小助手里没找到能直接做这件事的。您希望：
>
> - (a) 我自己写一段程序来做
> - (b) 交给我每次根据上下文临场判断
> - (c) 您心里有别的来源 / 品牌工具，告诉我名字，我再去找一次"

专家选 (a) → 该步 `execution_type: script`；选 (b) → `execution_type: llm`；选 (c) → 按其给出的关键词再搜一次。

## 展示候选给专家（业务语言）

搜到候选后（≥ 1 个），用下面格式读给专家。**不暴露 slug**，你在内存里保留"业务名 ↔ slug"对照表。

> "这一步我找到 {N} 个现成能做的小助手：
>
> 1. **{业务名}**：{description 的前 1-2 句业务改写}。背后是 {vendor}。{付费说明}
> 2. ……
>
> 您平时用这类工具吗？这几个里有您想用的吗？"

**业务名**：skill 名去掉 `linkfox-` 前缀再改写为自然中文，如 `linkfox-sellersprite-product-search` → "卖家精灵选品"。

**付费说明**：
- 若 skill frontmatter 声明了 `vendor` / `paid` 字段 → 直接转述
- 若未声明 → "这个可能涉及账号或付费，具体价格/权限需要您自己确认"

## 专家确认规则（硬约束）

1. **只搜到 1 个候选也必须过专家**。不允许"候选唯一 → 自动采纳"
2. **默认值是"不用"**。专家必须明确说"用 / 就用这个 / 可以 / 选第 N 个"才算采纳
3. **专家犹豫 / 反问 / 说"再看看"** → 不算采纳。记 `delegate_search.pending`，继续访谈，等专家后续明确；若最终仍未确认，按"未采纳"落到 script/llm
4. **专家拒绝所有候选** → 回退到 script 或 llm，记 `delegate_search.expert_rejected` + 简短原因（如"专家说卖家精灵最近数据不准"）
5. **不替专家做专业判断**。不说"我建议您用 X"；只说"有这些候选，您选哪个"

## 采纳后写回 interview-record

被专家确认的候选，在该 step 下记录：

```yaml
- step: 2
  name: 按条件查询竞品
  execution_type: delegate
  delegates_to: linkfox-sellersprite-product-search
  delegate_inputs_mapping:
    keyword: <来自 D2 的类目关键词>
    marketplace: US
    minUnits: 500
  delegate_confirmed_at: 2026-04-27T10:42:15+08:00
  delegate_expert_quote: |
    就用卖家精灵那个，我平时都用它看竞品
  expert_verbatim: |
    第二步按某些条件查 100 个竞品，销量要 500 以上
  assumed_fields: []
```

同时在文件**顶层 frontmatter** 的 `depends_on` 数组中追加该 slug（去重）。

## 搜索日志归档（评估器友好）

每次搜索行为——无论命中、未命中、专家拒绝——都追加一条到顶层 `delegate_search_log`：

```yaml
delegate_search_log:
  - step: 2
    timestamp: 2026-04-27T10:40:00+08:00
    layer: ecommerce              # ecommerce | general | expert_ask
    queries: ["卖家精灵 选品", "amazon 竞品 筛选"]
    candidates_found:
      - slug: linkfox-sellersprite-product-search
        business_name: 卖家精灵选品
      - slug: linkfox-sellersprite-competitor
        business_name: 卖家精灵竞品对比
    expert_choice: linkfox-sellersprite-product-search
    # 或 expert_choice: null + expert_rejected: true + reason: "数据不准"
    # 或 expert_choice: null + not_found: true
```

Evaluator E1 忠实度可以直接核对"生成物里 `depends_on` 每一条在日志里都能找到专家确认原话"。

## 与 D7 外部依赖的分工

| 情形 | 走哪条路 | 字段 |
|------|---------|------|
| 有现成 skill，专家采纳 | delegate | `delegates_to` + 顶层 `depends_on` |
| 无现成 skill，但要调外部平台 API | script（D7 路径）| `script` + `external_dependencies` |
| 无现成 skill，也不调外部 API | script 或 llm | 常规二分 |

**delegate 优先**。只有候选确实不存在或专家拒绝时，才退到 D7 的"自己封装"。

## 硬禁忌

- 不允许搜到一条就默认写进 `depends_on` 不问专家
- 不允许把 slug 读给专家（专家听不懂、也不该记）
- 不允许专家说"随便"时强制采纳某个（"随便"等同未采纳）
- 不允许跳过搜索直接写脚本。每个"涉及专业工具"的步骤都要走这条链，哪怕最终不用
- 不允许把明显是经验判断的步骤硬塞成委托（如"判断标题是否通顺" / "预估这个品能不能打爆"——这些是 llm 的活，没有 skill 能替）
- 不允许在 `delegates_to` 里填专家没说过的 slug（哪怕你觉得"应该用那个更好"）
