---
name: linkfox-junglescout-keyword-by-asin
description: Jungle Scout根据ASIN反查关键词，输入最多10个ASIN获取其在亚马逊搜索结果中出现的所有关键词及搜索量、竞争度、PPC竞价等数据，覆盖10个站点。当用户提到ASIN反查关键词、反查词、ASIN关键词挖掘、竞品关键词、ASIN流量词、反向ASIN查询、ASIN搜索词、关键词拓展、ASIN词库、竞品流量分析、reverse ASIN lookup, keyword by ASIN, ASIN keyword mining, competitor keywords, ASIN traffic keywords, reverse keyword lookup, ASIN search terms, keyword expansion时触发此技能。即使用户未明确提及"Jungle Scout"或"反查"，只要其需求涉及通过ASIN查找相关关键词或分析竞品关键词，也应触发此技能。
---

# Jungle Scout — 根据 ASIN 反查关键词

This skill queries keywords associated with given ASINs via the Jungle Scout data source, returning keyword search volume, competition metrics, PPC bids, ranking positions, and relevancy scores across 10 Amazon marketplaces. It supports up to 10 ASINs per call.

## Core Concepts

Jungle Scout ASIN 反查关键词工具通过输入竞品或目标 ASIN，获取这些 ASIN 在亚马逊搜索结果中出现的所有关键词及详细指标。卖家可以利用此工具进行：

- **竞品关键词分析**：查看竞品在哪些关键词下获得自然/广告排名
- **关键词拓展**：从已知 ASIN 反向挖掘高潜力关键词
- **广告投放参考**：获取关键词的 PPC 出价（精确/广泛匹配）和 SP 品牌广告出价
- **竞争格局评估**：通过 Ease of Ranking Score 和竞品排名数据判断关键词竞争难度
- **流量结构解析**：了解 ASIN 的流量来自哪些关键词，各关键词的搜索量和排名如何

**数据维度**：每条记录代表一个关键词，包含搜索量、趋势、排名、竞价、竞争度等完整指标。

## Data Fields

### Output Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| 关键词 | name | 搜索关键词 | yoga mat |
| 站点 | country | 市场代码 | us |
| 精确搜索量 | monthlySearchVolumeExact | 月精确匹配搜索量 | 85420 |
| 广泛搜索量 | monthlySearchVolumeBroad | 月广泛匹配搜索量 | 125000 |
| 月趋势 | monthlyTrend | 月环比趋势（%） | 15.5 |
| 季度趋势 | quarterlyTrend | 季度趋势（%） | 8.2 |
| 主类目 | dominantCategory | 关键词主要类目 | Sports & Outdoors |
| 相关度 | relevancyScore | 关键词与 ASIN 的相关度（0-100） | 92 |
| 排名难度 | easeOfRankingScore | 排名容易程度（0-100，越高越容易） | 45 |
| 自然排名 | organicRank | ASIN 的自然搜索排名 | 5 |
| 广告排名 | sponsoredRank | ASIN 的广告排名 | 3 |
| 综合排名 | overallRank | 综合排名位置 | 4 |
| 自然结果数 | organicProductCount | 自然搜索结果中的商品总数 | 2000 |
| 广告结果数 | sponsoredProductCount | 广告位商品总数 | 48 |
| PPC精确出价 | ppcBidExact | 精确匹配 PPC 建议出价（USD） | 1.25 |
| PPC广泛出价 | ppcBidBroad | 广泛匹配 PPC 建议出价（USD） | 0.95 |
| SP品牌广告出价 | spBrandAdBid | SP 品牌广告建议出价（USD） | 2.10 |
| 推荐促销数 | recommendedPromotions | 推荐促销量 | 5 |
| 主力ASIN | primaryAsin | 该关键词下排名最高的 ASIN | B0XXXXXXXX |
| 自然相对位置 | relativeOrganicPosition | 查询 ASIN 的自然排名相对位置 | 0.12 |
| 广告相对位置 | relativeSponsoredPosition | 查询 ASIN 的广告排名相对位置 | 0.08 |
| 自然排名ASIN数 | organicRankingAsinsCount | 有自然排名的查询 ASIN 数量 | 3 |
| 广告排名ASIN数 | sponsoredRankingAsinsCount | 有广告排名的查询 ASIN 数量 | 2 |
| 竞品平均自然排名 | avgCompetitorOrganicRank | 查询 ASIN 的平均自然排名 | 12.5 |
| 竞品平均广告排名 | avgCompetitorSponsoredRank | 查询 ASIN 的平均广告排名 | 8.3 |
| 变体最低自然排名 | variationLowestOrganicRank | 变体中最佳自然排名 | 3 |
| 变体最低广告排名 | variationLowestSponsoredRank | 变体中最佳广告排名 | 2 |
| 竞品自然排名详情 | competitorOrganicRank | 各 ASIN 的自然排名数组 | [{asin, organicRank}] |
| 竞品广告排名详情 | competitorSponsoredRank | 各 ASIN 的广告排名数组 | [{asin, sponsoredRank}] |
| 更新时间 | updatedAt | 数据最后更新时间 | 2026-04-10 |
| 消耗Token | costToken | 本次调用消耗的 token 数 | 10 |

## Supported Marketplaces

us (United States), uk (United Kingdom), de (Germany), in (India), ca (Canada), fr (France), it (Italy), es (Spain), mx (Mexico), jp (Japan)

Default marketplace is **us**. Use us when the user doesn't specify a marketplace.

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/junglescout_keyword_by_asin.py` directly to run queries.

## How to Build Queries

Required parameters: `marketplace` and `asins`. All other parameters are optional filters for narrowing results.

### Principles for Building API Calls

1. **站点映射**：用户说"美国站"→ `us`，"日本站"→ `jp`，"德国站"→ `de`；未指定时默认 `us`
2. **ASIN 格式**：标准 10 位亚马逊 ASIN（以 B0 开头），以数组传入，最多 10 个
3. **搜索量筛选**：用户说"搜索量大于1万"→ `minMonthlySearchVolumeExact: 10000`；"搜索量1000到5000"→ `min: 1000, max: 5000`
4. **排序选择**：默认按精确搜索量降序（`-monthly_search_volume_exact`）；用户要求"按相关度排序"→ `sort: -relevancy_score`
5. **结果数量**：用户说"给我前50个"→ `needCount: 50`；未指定时可根据场景适当设置（如 30-100）
6. **变体包含**：用户关注变体流量时设 `includeVariants: true`

### Common Query Scenarios

**1. 查看竞品 ASIN 的核心流量词**
```json
{
  "marketplace": "us",
  "asins": ["B0XXXXXXXX"],
  "needCount": 50,
  "sort": "-monthly_search_volume_exact"
}
```

**2. 多个 ASIN 的共同关键词（竞品对比）**
```json
{
  "marketplace": "us",
  "asins": ["B0XXXXXXXX", "B0YYYYYYYY", "B0ZZZZZZZZ"],
  "needCount": 100,
  "sort": "-relevancy_score"
}
```

**3. 筛选高搜索量低竞争关键词**
```json
{
  "marketplace": "us",
  "asins": ["B0XXXXXXXX"],
  "minMonthlySearchVolumeExact": 5000,
  "maxOrganicProductCount": 500,
  "needCount": 50,
  "sort": "-ease_of_ranking_score"
}
```

**4. 查找长尾关键词（多词组合）**
```json
{
  "marketplace": "us",
  "asins": ["B0XXXXXXXX"],
  "minWordCount": 3,
  "minMonthlySearchVolumeExact": 500,
  "needCount": 80,
  "sort": "-monthly_search_volume_exact"
}
```

**5. 日本站竞品广告关键词分析**
```json
{
  "marketplace": "jp",
  "asins": ["B0XXXXXXXX"],
  "needCount": 50,
  "sort": "-ppc_bid_exact"
}
```

**6. 包含变体的全量关键词挖掘**
```json
{
  "marketplace": "de",
  "asins": ["B0XXXXXXXX"],
  "includeVariants": true,
  "needCount": 200,
  "sort": "-monthly_search_volume_exact"
}
```

## Display Rules

1. **表格展示为主**：以表格形式展示关键词列表，核心列包括：关键词、精确搜索量、自然排名、广告排名、相关度、PPC 出价
2. **按需精简列**：根据用户意图选择展示列。竞品分析侧重排名和搜索量；广告分析侧重 PPC 出价和广告排名
3. **排名高亮**：对自然排名前 10 和广告排名前 5 的关键词做标注，帮助用户快速识别核心流量词
4. **趋势标注**：月/季度趋势为正时标注增长，为负时标注下降
5. **竞品对比**：当输入多个 ASIN 时，展示各 ASIN 在关键词下的排名对比
6. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters

## Important Limitations

- **ASIN 数量上限**：单次查询最多 10 个 ASIN
- **数据时效性**：数据定期更新，`updatedAt` 字段标注最后更新时间
- **搜索量类型**：同时提供精确匹配和广泛匹配两种搜索量
- **必填参数**：`marketplace` 和 `asins` 缺一不可
- **排名数据**：排名为该 ASIN 在对应关键词搜索结果中的位置，非实时数据

## User Expression & Scenario Quick Reference

**Applicable** - 通过 ASIN 反查和拓展关键词：

| User Says | Scenario |
|-----------|----------|
| "这个ASIN有哪些流量词" | 单个 ASIN 关键词反查 |
| "竞品用了哪些关键词" | 竞品关键词分析 |
| "帮我对比这几个ASIN的关键词" | 多 ASIN 关键词对比 |
| "这个产品搜什么词能搜到" | ASIN 反向搜索词查询 |
| "找一些搜索量大竞争小的词" | 高搜索量低竞争关键词筛选 |
| "这个ASIN的广告词有哪些" | ASIN 广告关键词分析 |
| "帮我拓展一下关键词" | 基于 ASIN 的关键词拓展 |

**Not applicable** - 超出 ASIN 反查关键词范围：
- 关键词搜索量历史趋势（需要关键词历史搜索量工具）
- ABA 搜索词排名（需要 ABA 工具）
- 商品销量估算、listing 优化建议
- 关键词广告投放执行（仅提供竞价参考数据）
- 非亚马逊平台的关键词数据

**Boundary judgment**: When users say "关键词", "流量词", or "搜索词", if they provide specific ASINs and want to know what keywords those ASINs rank for, this skill applies. If they want to search keywords by text or check historical search volume trends, other skills are more suitable.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
