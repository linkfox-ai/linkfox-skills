---
name: linkfox-junglescout-keyword-share-of-voice
description: Jungle Scout关键词市场份额（Share of Voice）分析，返回亚马逊搜索结果前3页的品牌声量占比（自然/广告/综合）、30天精确搜索量、PPC竞价中位数及TOP3 ASIN点击转化数据，覆盖10个站点。当用户提到品牌市场份额、品牌声量占比、搜索结果品牌分布、Share of Voice、SOV分析、品牌竞争格局、广告位占比、自然排名品牌占比、PPC竞价分析、品牌垄断分析、keyword share of voice, brand visibility, organic vs sponsored share, brand dominance, PPC bid analysis, search result brand distribution, competitive landscape, weighted SOV, top ASIN clicks conversions时触发此技能。即使用户未明确提及"Share of Voice"或"SOV"，只要其需求涉及分析某个亚马逊关键词搜索结果中各品牌的市场占有率或竞争格局，也应触发此技能。
---

# Jungle Scout — 关键词市场份额 Share of Voice

This skill queries Share of Voice (SOV) data for Amazon keywords via the Jungle Scout data source, returning brand visibility distribution across the first 3 pages of search results, along with search volume, PPC bid estimates, and top ASIN click/conversion metrics across 10 Amazon marketplaces.

## Core Concepts

Share of Voice measures **how much of the search results real estate a brand occupies** for a given keyword. Jungle Scout analyzes the first 3 pages of Amazon search results and calculates each brand's presence in three dimensions:

- **Organic SOV**: Brand visibility from organic (non-sponsored) search result positions
- **Sponsored SOV**: Brand visibility from sponsored/advertising placements
- **Combined SOV**: Overall brand visibility merging both organic and sponsored results

Each dimension has two calculation methods:

- **Basic SOV**: Simple product count ratio — number of a brand's products ÷ total products on the 3 pages
- **Weighted SOV**: Position-adjusted ratio that gives higher weight to top positions and factors like Amazon's Choice badge; this is the more meaningful metric for competitive analysis

The tool also returns:

- **30-day exact search volume**: Total estimated searches in the past 30 days
- **PPC bid median**: Median suggested bid for this keyword, useful for advertising cost estimation
- **TOP3 ASIN click & conversion data**: The top 3 ASINs by clicks, with click count, conversion count, and conversion rate

## Data Fields

### brands (Brand SOV Breakdown)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Brand Name | brand | Brand name as shown in search results | Anker |
| Organic Products | organicProducts | Number of organic listings in the first 3 pages | 5 |
| Sponsored Products | sponsoredProducts | Number of sponsored listings | 3 |
| Combined Products | combinedProducts | Total listings (organic + sponsored) | 8 |
| Organic Basic SOV | organicBasicSov | Organic simple ratio (0–1) | 0.083 |
| Organic Weighted SOV | organicWeightedSov | Organic position-weighted ratio (0–1) | 0.112 |
| Sponsored Basic SOV | sponsoredBasicSov | Sponsored simple ratio (0–1) | 0.15 |
| Sponsored Weighted SOV | sponsoredWeightedSov | Sponsored position-weighted ratio (0–1) | 0.18 |
| Combined Basic SOV | combinedBasicSov | Combined simple ratio (0–1) | 0.133 |
| Combined Weighted SOV | combinedWeightedSov | Combined position-weighted ratio (0–1) | 0.152 |
| Organic Avg Position | organicAveragePosition | Average ranking position in organic results | 12.4 |
| Sponsored Avg Position | sponsoredAveragePosition | Average ranking position in sponsored results | 5.0 |
| Combined Avg Position | combinedAveragePosition | Average ranking position across all results | 9.5 |
| Organic Avg Price | organicAveragePrice | Average price of organic products | 29.99 |
| Sponsored Avg Price | sponsoredAveragePrice | Average price of sponsored products | 25.99 |
| Combined Avg Price | combinedAveragePrice | Average price of all products | 28.49 |

### topAsins (TOP 3 ASIN Click & Conversion)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| ASIN | asin | Amazon Standard Identification Number | B09V3KXJPB |
| Product Name | name | Product title | Anker Portable Charger... |
| Brand | brand | Product brand | Anker |
| Clicks | clicks | Click count (30-day window) | 15200 |
| Conversions | conversions | Conversion count (30-day window) | 4560 |
| Conversion Rate | conversionRate | Conversion rate (0–1) | 0.30 |

### Top-Level Summary Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| ID | id | Resource identifier | — |
| Type | type | Fixed value | share_of_voice |
| 30-Day Search Volume | estimated30DaySearchVolume | Exact search volume over 30 days | 125000 |
| PPC Bid Median | exactSuggestedBidMedian | Median suggested PPC bid (USD) | 1.25 |
| Product Count | productCount | Total products in the first 3 pages | 60 |
| Updated At | updatedAt | Data freshness timestamp | 2026-04-10T00:00:00 |
| Top ASINs Start Date | topAsinsModelStartDate | Click/conversion data window start | 2026-03-11 |
| Top ASINs End Date | topAsinsModelEndDate | Click/conversion data window end | 2026-04-10 |
| Cost Token | costToken | Tokens consumed by this call | 1 |

## Supported Marketplaces

us (United States), uk (United Kingdom), de (Germany), in (India), ca (Canada), fr (France), it (Italy), es (Spain), mx (Mexico), jp (Japan)

Default marketplace is **us**. Use us when the user doesn't specify a marketplace.

## 调用方式

- **API 端点**：`POST /tool-jungle-scout/keywords/share-of-voice`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/junglescout_keyword_sov.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-junglescout-keyword-share-of-voice-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

Only two parameters are needed: `marketplace` and `keyword`.

### Principles for Building API Calls

1. **Marketplace mapping**: "美国站" → `us`, "日本站" → `jp`, "德国站" → `de`; default to `us` when unspecified
2. **Keyword**: Pass the user's keyword as-is (lowercase English preferred)
3. **One keyword per call**: Each request analyzes one keyword; for multi-keyword comparison, make separate calls

### Common Query Scenarios

**1. Brand dominance check — Who owns this keyword?**
```json
{
  "marketplace": "us",
  "keyword": "portable charger"
}
```
Focus on `combinedWeightedSov` to see which brands dominate the search results page.

**2. PPC competitive analysis — Is this keyword worth bidding on?**
```json
{
  "marketplace": "us",
  "keyword": "wireless earbuds"
}
```
Compare `exactSuggestedBidMedian` with the keyword's search volume to gauge cost-efficiency. Check `sponsoredWeightedSov` to see how heavily competitors invest in ads.

**3. Conversion efficiency of top ASINs**
```json
{
  "marketplace": "de",
  "keyword": "kopfhörer kabellos"
}
```
Examine the `topAsins` array to find whether the top-clicked products convert well. High clicks + low conversion rate may indicate opportunity.

**4. Identify market gaps — Are there underserved positions?**
```json
{
  "marketplace": "jp",
  "keyword": "ヨガマット"
}
```
If no single brand has a `combinedWeightedSov` above 0.15, the keyword is fragmented and may be easier to enter. Combine with search volume to assess market size.

**5. Compare organic vs sponsored presence**
```json
{
  "marketplace": "uk",
  "keyword": "running shoes"
}
```
A brand with high `sponsoredWeightedSov` but low `organicWeightedSov` relies heavily on ads; this can inform competitive strategy.

## Display Rules

1. **Brand table**: Show the brands table sorted by `combinedWeightedSov` descending; highlight the **top 5 brands** for quick comprehension
2. **SOV as percentage**: Display SOV values as percentages (multiply by 100), e.g., 0.152 → 15.2%
3. **Context header**: Before the table, show the keyword's 30-day search volume (`estimated30DaySearchVolume`) and PPC bid median (`exactSuggestedBidMedian`) as context
4. **Top ASINs section**: Show the TOP 3 ASIN table separately with click count, conversion count, and conversion rate
5. **Competitive summary**: After the data, provide a brief competitive landscape summary: whether the keyword is dominated by a few brands or fragmented, and note any large gaps between organic and sponsored presence
6. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters

## Important Limitations

- **Coverage**: Only the first 3 pages of Amazon search results are analyzed (typically ~48–60 products)
- **Single keyword**: One keyword per API call; multi-keyword comparison requires separate calls
- **SOV is a snapshot**: Data reflects a point-in-time crawl, not a historical trend
- **No historical SOV**: This tool does not provide SOV changes over time; use the keyword history tool for volume trends

## User Expression & Scenario Quick Reference

**Applicable** — Brand market share and competitive analysis on Amazon search results:

| User Says | Scenario |
|-----------|----------|
| "这个词谁占的份额最大" | Brand dominance analysis |
| "这个关键词竞争激不激烈" | Competitive landscape assessment |
| "广告位都被谁占了" | Sponsored SOV analysis |
| "有没有品牌垄断这个词" | Monopoly detection |
| "这个词的PPC出价大概多少" | PPC bid estimation |
| "搜索结果里哪些品牌排前面" | Brand visibility ranking |
| "这个词的转化率高不高" | Top ASIN conversion analysis |

**Not applicable** — Beyond keyword Share of Voice scope:
- Historical search volume trends (use keyword history tool)
- Keyword suggestions / keyword mining (use ABA or keyword explorer tools)
- Product-level sales estimation or review analysis
- Listing optimization or copywriting advice
- Non-Amazon platform data

**Boundary judgment**: When users say "竞争分析", "品牌分析", or "市场格局", if the intent is to understand which brands occupy the search results page for a specific keyword (share of voice / brand distribution), this skill applies. If they want product-level sales data, profit margins, or historical trends, it does not apply.

## 积分消耗规则

消耗 63.75 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
