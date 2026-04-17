---
name: linkfox-junglescout-keyword-by-keyword
description: Jungle Scout关键词拓展工具，根据种子关键词扩展出相关关键词列表，包含搜索量、趋势、PPC竞价、排名难度等数据，覆盖美国、英国、德国、日本等10个亚马逊站点。当用户提到关键词拓展、关键词挖掘、长尾词挖掘、相关关键词、关键词建议、拓词、PPC竞价研究、关键词竞争度、关键词发现、Jungle Scout关键词、keyword expansion, keyword discovery, keyword scout, related keywords, long-tail keywords, keyword suggestions, PPC bid research, keyword competition, seed keyword expansion, keyword mining时触发此技能。即使用户未明确提及"Jungle Scout"，只要其需求涉及从一个种子关键词出发找到更多相关关键词及其搜索量、竞争度等指标，也应触发此技能。
---

# Jungle Scout — 根据关键词扩展关键词信息 (Keyword by Keyword)

This skill expands a seed keyword into a list of related keywords with search volume, trends, PPC bids, ranking difficulty, and other competitive metrics via the Jungle Scout data source, covering 10 Amazon marketplaces.

## Core Concepts

Jungle Scout Keyword by Keyword 工具是亚马逊关键词研究的核心工具之一，从一个**种子关键词**出发，挖掘与之相关的大量关键词及其竞争指标。主要应用场景包括：

- **关键词拓展/发现**：输入核心词，获取数百个相关关键词，扩充 listing 关键词库
- **长尾词挖掘**：通过 `minWordCount` 筛选 3+ 词的长尾关键词，发现低竞争高转化机会
- **PPC 竞价研究**：查看精确/广泛匹配 PPC 出价和品牌广告出价，规划广告预算
- **竞争度评估**：通过 `easeOfRankingScore` 和 `organicProductCount` 判断关键词排名难度
- **趋势分析**：查看月度趋势和季度趋势百分比变化，识别增长型关键词

## Data Fields

### Output Fields (keywordInfoList)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| 关键词 | name | 关键词名称 | yoga mat thick |
| 站点 | country | 市场代码 | us |
| 精确搜索量 | monthlySearchVolumeExact | 月均精确匹配搜索量 | 45000 |
| 广泛搜索量 | monthlySearchVolumeBroad | 月均广泛匹配搜索量 | 120000 |
| 月度趋势 | monthlyTrend | 环比月度搜索量变化百分比 | 15.3 |
| 季度趋势 | quarterlyTrend | 环比季度搜索量变化百分比 | -5.2 |
| 主类目 | dominantCategory | 搜索结果中占比最高的品类 | Sports & Outdoors |
| 相关性评分 | relevancyScore | 与种子词的相关性评分 | 856 |
| 排名难度 | easeOfRankingScore | 排名容易度评分（越高越容易） | 3 |
| 自然商品数 | organicProductCount | 搜索结果中的自然排名商品数量 | 342 |
| 广告商品数 | sponsoredProductCount | 搜索结果中的广告商品数量 | 28 |
| PPC精确出价 | ppcBidExact | 精确匹配 PPC 建议出价（美元） | 1.25 |
| PPC广泛出价 | ppcBidBroad | 广泛匹配 PPC 建议出价（美元） | 0.89 |
| 品牌广告出价 | spBrandAdBid | Sponsored Brand 广告建议出价（美元） | 2.50 |
| 推荐促销 | recommendedPromotions | 推荐促销赠品数量 | 150 |
| 消耗Token | costToken | 本次调用消耗的 token 数 | 1 |

## Supported Marketplaces

10 Amazon marketplaces: `us` (default), `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp`. When the user does not specify a marketplace, use `us`.

| 站点 | marketplace 值 | 说明 |
|------|---------------|------|
| 美国 | us | Amazon.com |
| 英国 | uk | Amazon.co.uk |
| 德国 | de | Amazon.de |
| 印度 | in | Amazon.in |
| 加拿大 | ca | Amazon.ca |
| 法国 | fr | Amazon.fr |
| 意大利 | it | Amazon.it |
| 西班牙 | es | Amazon.es |
| 墨西哥 | mx | Amazon.com.mx |
| 日本 | jp | Amazon.co.jp |

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/junglescout_keyword_by_keyword.py` directly to run queries.

## How to Build Queries

必填参数：`marketplace`、`searchTerms`（单个种子关键词字符串）。

### Principles for Building API Calls

1. **站点映射**：用户说"美国站"→ `us`，"日本站"→ `jp`，"德国站"→ `de`；未指定时默认 `us`
2. **种子关键词**：原样传入用户提供的关键词（英文小写为佳），仅支持单个关键词
3. **结果数量**：默认返回数量有限，若用户需要更多结果，设置 `needCount`
4. **排序选择**：默认按精确搜索量降序 (`-monthly_search_volume_exact`)，根据用户意图切换排序字段
5. **筛选过滤**：充分利用 `min/max` 参数缩小结果范围，避免返回无关低质量关键词

### Common Query Scenarios

**1. 扩展种子关键词 — 获取相关关键词列表**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat"
}
```

**2. 挖掘长尾关键词（3+ 词）**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minWordCount": 3,
  "needCount": 50
}
```

**3. 低竞争关键词发现**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "maxOrganicProductCount": 200,
  "minMonthlySearchVolumeExact": 1000,
  "sort": "-ease_of_ranking_score"
}
```

**4. 高搜索量关键词筛选**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minMonthlySearchVolumeExact": 10000,
  "sort": "-monthly_search_volume_exact",
  "needCount": 30
}
```

**5. PPC 竞价研究 — 按广泛出价排序**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minMonthlySearchVolumeExact": 500,
  "sort": "ppc_bid_broad",
  "needCount": 30
}
```

**6. 德国站广泛搜索量关键词**
```json
{
  "marketplace": "de",
  "searchTerms": "yogamatte",
  "minMonthlySearchVolumeBroad": 5000,
  "sort": "-monthly_search_volume_broad"
}
```

## Display Rules

1. **表格优先**：以表格展示关键词列表，核心列包括：关键词、精确搜索量、广泛搜索量、月度趋势、PPC精确出价、排名难度
2. **按需裁剪列**：根据用户意图决定展示列——PPC研究场景侧重出价列，拓词场景侧重搜索量和趋势
3. **趋势标注**：月度趋势和季度趋势为正值标注上升↑，负值标注下降↓
4. **排名难度解读**：`easeOfRankingScore` 1-3 为困难，4-6 为中等，7-10 为容易
5. **数据洞察**：在表格后提供简要总结，如高搜索量词集中在哪个类目、长尾词的竞争优势等
6. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters

## Important Limitations

- **单次单关键词**：`searchTerms` 仅接受一个种子关键词，多关键词需拆分多次调用
- **数据周期**：搜索量为月均估算值，非实时数据
- **站点限制**：仅覆盖 10 个亚马逊站点，不含澳大利亚、荷兰等
- **排序字段固定**：仅支持预定义的排序字段，不支持自定义组合排序

## User Expression & Scenario Quick Reference

**Applicable** — 关键词拓展与竞争分析：

| User Says | Scenario |
|-----------|----------|
| "帮我拓展这个关键词" | 种子词扩展 |
| "这个词有哪些相关关键词" | 相关词挖掘 |
| "找一些长尾词" | 长尾关键词筛选（minWordCount ≥ 3） |
| "竞争度低的词有哪些" | 低竞争关键词（排名难度 + 商品数量筛选） |
| "这个词的PPC出价多少" | PPC 竞价数据查询 |
| "搜索量大的相关词" | 高搜索量关键词筛选 |
| "德国站有什么相关词" | 非美国站关键词拓展 |
| "帮我做关键词调研" | 综合关键词研究 |

**Not applicable** — 超出关键词拓展范围：
- 关键词历史搜索量趋势（需要 keyword-history 工具）
- ABA 搜索词排名（需要 ABA 工具）
- 商品搜索或 listing 分析
- 非亚马逊平台的关键词数据
- ASIN 反查关键词

**Boundary judgment**: When users say "关键词", "拓词", or "关键词研究", if they want to expand a seed keyword into a list of related keywords with metrics, this skill applies. If they want to see a single keyword's historical search volume trend over time, use the keyword-history skill instead.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
