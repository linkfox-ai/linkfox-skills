---
name: linkfox-amazon-opportunity-search-by-metrics
description: 亚马逊反向选品：基于历史商业洞察报告沉淀的指标数据池，按 30+ 项商业维度（市场规模与增长、价格区间与档位份额、竞争密度与头部集中度、人群画像如年龄/性别/收入、评论卖点与痛点等）反向筛选亚马逊赛道与关键词。当用户提到反向选品、指标筛选、细分市场反查、蓝海赛道挖掘、低竞争赛道、新人友好赛道、品牌分散市场、痛点切入、卖点反查、定价档位机会、人群画像选品、Amazon niche reverse search, niche metrics filter, low-competition niche, blue ocean niche, demographic-based selection, pain-point niche, price tier opportunity, sweet spot pricing, brand fragmentation时触发此技能。即使用户未明确说"反向选品"，只要其需求是按商业维度筛选符合条件的亚马逊赛道，也应触发此技能。
---

# Amazon Opportunity Screener by Metrics

This skill guides you on how to reverse-search Amazon niches and keywords from a metrics pool aggregated from historical opportunity reports, helping sellers turn vague selection ideas (low competition, growing demand, blue ocean, pain-point opportunity, etc.) into concrete niche candidates.

## Core Concepts

This tool exposes a queryable pool of **niche-level metrics** (~37 fields per record) distilled from past Amazon opportunity reports. Instead of generating a fresh report (forward analysis), it lets you **reverse-filter** the existing pool by 30+ business dimensions and returns matching `(marketplace, keyword)` records ranked by collection time (most recent first).

Records are at the **niche / keyword** level, not ASIN level. Each record represents a niche snapshot — its market size, growth, competition, price tiers, demographics, top features, and review themes.

**Forward vs. reverse**: Use `linkfox-amazon-opportunity-report` when the user has a keyword and wants a comprehensive AI report. Use this skill when the user has business criteria (filters) and wants to discover which keywords / niches fit.

## Filter Dimensions

Filters are grouped into six business dimensions. All filter parameters are optional, but **at least one of `keyword` / `nicheName` or any metric filter must be provided** — fully empty calls are rejected.

| Dimension | Example Parameters | Typical User Intent |
|-----------|---------------------|---------------------|
| Market size & growth | `nicheRevenue360dMinUsdAtLeastGte`, `nichePeakSearchVolumeAtLeastGte`, `nicheSearchVolumeYoyChangePctAtLeastGte`, `nichePeakMonthGte/Lte` | "Big enough market", "fast-growing", "Q4 seasonal" |
| Competition density | `nicheBrandCountLte`, `nicheBrandCountYoyChangePctAtLeastLte`, `nicheTop5ProductClickSharePctAtLeastLte`, `featureTop5BrandSharePctAtLeastLte` | "Newcomer-friendly", "brands fragmented", "no oligopoly", "brands exiting" |
| Price & tier | `priceMinUsdGte`, `priceMaxUsdLte`, `priceSweetSpotMinUsdGte/Lte`, `priceEntryClickSharePctAtLeastGte`, `priceMidClickSharePctAtLeastLte`, `priceHighClickSharePctAtLeastGte` | "Affordable focus", "premium-friendly", "mid-tier blue ocean" |
| Demographics | `demoPrimaryAgeMinGte`, `demoPrimaryAgeMaxLte`, `demoGenderDominant`, `demoPrimaryIncomeTier`, `demoLifeStageTagsContains` | "Female-driven", "high-income", "parents", "fitness enthusiasts" |
| Product features | `featureNewAvgReviewCountAtLeastLte`, `featureEstablishedAvgReviewCountAtLeastLte`, `featureEmergingTrendTagsContains`, `featureUncommonFeatureTagsContains`, `searchTopCategory1Label` | "New-product entry barrier low", "emerging trend", "uncommon feature edge", "set/kit niches" |
| Review insights | `reviewPositiveTop1Topic`, `reviewPositiveTop1PctAtLeastGte/Lte`, `reviewNegativeTop1Topic`, `reviewNegativeTop1PctAtLeastGte/Lte`, `reviewNegativeTop2Topic`, `reviewStrategicInsightTagsContains` | "Pain-point niche", "comfort-driven sellers", "size-issue opportunity" |

See `references/api.md` for the full parameter list, types, value ranges, and response field map.

## Supported Marketplaces

Currently only **US** (United States) is supported. Always set `amazonDomain` to `US` (or omit). If a user requests other marketplaces, inform them this tool currently only covers the US market.

## 调用方式

- **API 端点**：`POST /amazon/opportunity/searchByMetrics`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/amazon_opportunity_screener.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-opportunity-search-by-metrics-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

## How to Build Queries

The user expresses business intent in natural language; you map it to **the smallest viable set of filters**. Principles:

1. **Convert intent into specific bounds**: "low competition" → `nicheBrandCountLte: 20`; "fast-growing" → `nicheSearchVolumeYoyChangePctAtLeastGte: 100` (≥100% YoY); "newcomer-friendly" → `featureNewAvgReviewCountAtLeastLte: 500`.
2. **Start narrow, then loosen**: First call usually with 2–4 strong filters and `limit=25`. If the result set is empty or too small, drop or widen the most aggressive filter rather than adding new ones.
3. **Pair complementary signals**: Brand-level + product-level concentration (`featureTop5BrandSharePctAtLeastLte` + `nicheTop5ProductClickSharePctAtLeastGte`) reveals "brands fragmented but products concentrated" — a brand-extension entry signal.
4. **Snake_case fragments for tag fields**: `featureEmergingTrendTagsContains`, `demoLifeStageTagsContains`, `reviewNegativeTop1Topic`, etc. accept snake_case word fragments and use LIKE matching. Pass a root word (`size`, `parent`, `cordless`) to cover normalized variants.
5. **Faithful to user intent**: Don't silently add filters the user didn't ask for. If they only said "growing", just filter on growth — don't also constrain price unless they mentioned it.

### Common Scenarios

**1. Niche reverse-lookup by keyword**
```json
{"keyword": "whoop band", "limit": 25}
```

**2. Newcomer-friendly low-competition niches**
```json
{"nicheBrandCountLte": 20, "featureNewAvgReviewCountAtLeastLte": 500, "limit": 25}
```

**3. High-growth blue ocean (≥100% YoY, brands not yet flooding in)**
```json
{"nicheSearchVolumeYoyChangePctAtLeastGte": 100, "nicheBrandCountYoyChangePctAtLeastLte": 30, "limit": 25}
```

**4. Mid-tier price gap (low-price dominates, mid-tier scarce)**
```json
{"priceEntryClickSharePctAtLeastGte": 70, "priceMidClickSharePctAtLeastLte": 5, "limit": 25}
```

**5. Pain-point entry — strong size complaints**
```json
{"reviewNegativeTop1Topic": "size", "reviewNegativeTop1PctAtLeastGte": 70, "limit": 25}
```

**6. Premium-friendly female-driven niches**
```json
{"demoGenderDominant": "female", "demoPrimaryIncomeTier": "high", "priceHighClickSharePctAtLeastGte": 25, "limit": 25}
```

**7. Q4 seasonal niches with ≥100k peak search**
```json
{"nichePeakMonthGte": 11, "nichePeakMonthLte": 12, "nichePeakSearchVolumeAtLeastGte": 100000, "limit": 25}
```

**8. Track niches around a known competitor brand**
```json
{"featureTopBrandsContains": "WHOOP", "limit": 50}
```

## Display Rules

1. **Present data only**: Render the returned niches as a clean comparison table — niche name / keyword, market size, growth, brand count, price range, key tags. No subjective business advice.
2. **Surface the active filters**: Echo the filter set you used so the user can adjust ("当前筛选：品牌数 ≤ 20 且搜索量同比 ≥ 100%").
3. **Time-snapshot reminder**: Records reflect data at collection time and are not continuously updated. Mention this when results look stale or contradict a user's external knowledge.
4. **Empty / few-result handling**: If `data` is empty or very short, suggest widening the most aggressive filter rather than re-asking the user from scratch.
5. **Error handling**: When a query fails, explain the reason based on the `msg` field (most often the "fully empty parameters" guard) and suggest adding at least one filter.
6. **No secondary aggregation**: The results power frontend rendering and are not stored, so they cannot be fed into `@智能数据查询` (intelligent data query) for further aggregation. If users ask for grouped statistics across niches, do the calculation locally or pull a wider `limit` first.

## Important Limitations

- **US only**: Currently only supports the United States marketplace (`amazonDomain` = `US`).
- **No pagination**: There is no `page` parameter. Increase `limit` (max 200) to widen the candidate pool; results are sorted by collection time (newest first).
- **At least one filter required**: Calls with no `keyword` / `nicheName` and no metric filter are rejected.
- **Snapshot data**: Records are aggregated from historical opportunity reports; new reports refresh the pool over time, but individual records are not real-time.
- **Niche-level granularity**: The output is niche / keyword level, not ASIN level. To dig into specific products inside a niche, hand off to `linkfox-amazon-search`, `linkfox-keepa-product-search`, etc.

## User Expression & Scenario Quick Reference

**Applicable** — Niche-level reverse selection on the US Amazon market:

| User Says | Scenario |
|-----------|----------|
| "Low-competition niches", "newcomer-friendly", "brand-light" | Brand-density filter |
| "Brands are exiting", "old players retreating" | Negative brand-count YoY |
| "Fast-growing niche", "trending up", "≥100% YoY" | Search-volume YoY filter |
| "Mid-tier blue ocean", "low-price dominates but mid is scarce" | Price-tier share gap |
| "Premium-friendly", "high-income consumers" | Income tier + high-tier share |
| "Female / male / mixed market" | Gender dominance filter |
| "Parents / students / retirees / fitness enthusiasts" | Life-stage tag |
| "Strong size / quality / durability pain point" | Negative review topic + share |
| "Comfort-driven", "value-driven sellers" | Positive review topic + share |
| "Track all niches around brand X" | `featureTopBrandsContains` |
| "Q4 seasonal niches", "Prime Day window" | Peak month + peak volume |

**Not applicable** — Use other tools instead:
- Need a comprehensive AI report on one keyword → `linkfox-amazon-opportunity-report`
- ASIN-level competitor research, sales estimation → SellerSprite / Keepa / Sorftime tools
- Real-time keyword ranking, search-term mining → ABA / SIF tools
- Marketplaces other than US → not yet supported by this tool
- Want to run group-by aggregation over niches via `@智能数据查询` → unsupported (data is not warehoused)

**Boundary judgment**: When users describe selection criteria in business language and want matching candidate niches, this skill applies. When they hand you a specific keyword and want the full multi-dimensional analysis, use `linkfox-amazon-opportunity-report`. When they want to drill into ASINs / sellers within a niche, hand off to product-search tools.

## 积分消耗规则

按动态规则计费：消耗积分 = 1.5 × (N ≤ 25 ? 5 : 5 + ceil((N - 25) / 5))。N 是接口实际返回的数据条数；即使 N = 0，只要接口成功也按 15000 计费。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.



---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
