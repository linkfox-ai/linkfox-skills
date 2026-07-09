---
name: linkfox-jiimore-get-niche-review-from-keyword
description: 亚马逊细分市场评论分析与消费者情感洞察。当用户提到细分市场评论分析、消费者情感、用户痛点、客户反馈洞察、评论主题分析、好评差评拆解、细分市场舆情挖掘、产品评论情感分析、niche market reviews, consumer sentiment, customer pain points, review topic analysis, positive/negative reviews, opinion mining, Jiimore data时触发此技能。即使用户未明确提及"细分市场评论"，只要其需求涉及分析亚马逊细分市场中的消费者评论或理解细分市场层面的客户情感，也应触发此技能。
---

# Jiimore Niche Review from Keyword

This skill guides you on how to query and analyze Amazon niche market review data powered by Jiimore, helping Amazon sellers uncover consumer sentiment, pain points, and real demand signals from product reviews within niche markets.

## Core Concepts

Niche Review Analysis aggregates and categorizes customer reviews across products in an Amazon niche market. Given a keyword, the system identifies the relevant niche markets, extracts review topics, classifies them as positive or negative, and shows how frequently each topic is mentioned. This enables sellers to understand what customers love, what frustrates them, and where product improvement opportunities exist.

**Review types**: Each review entry is classified as either "positive" or "negative", reflecting the overall sentiment of that review topic.

**Mention percentage**: The `percentOfMentions` value (0-1 scale, representing 0%-100%) indicates how frequently a particular topic appears across all reviews in the niche. A higher percentage means more customers are talking about that topic.

## Supported Marketplaces

US (United States), JP (Japan), DE (Germany)

Default marketplace is **US**. Use US when the user does not specify a marketplace.

## 调用方式

- **API 端点**：`POST /jiimore/getNicheReviewFromKeyword`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/jiimore_get_niche_review.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-jiimore-get-niche-review-from-keyword-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Parameter Guide

### Required Parameter

| Parameter | Type | Description |
|-----------|------|-------------|
| keyword | string | The search keyword (max 1000 chars). Must be in the language of the target marketplace (English for US, German for DE, Japanese for JP) |

### Marketplace & Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| countryCode | string | US | Country code: US, JP, or DE |
| page | integer | 1 | Page number (starting from 1) |
| pageSize | integer | 50 | Results per page (10-100) |

### Sorting

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| sortField | string | unitsSoldT7 | Field to sort by (see Sortable Fields below) |
| sortType | string | desc | Sort direction: `desc` (descending) or `asc` (ascending) |

**Sortable Fields**:

| Field | Description |
|-------|-------------|
| unitsSoldT7 | Units sold (7-day) |
| searchVolumeT7 | Search volume (7-day) |
| searchVolumeGrowthT7 | Search volume growth (7-day) |
| clickConversionRateT7 | Click conversion rate (7-day) |
| searchConversionRateT7 | Search conversion rate (7-day) |
| clickCountT7 | Click count (7-day) |
| demand | Demand score |
| avgPrice | Average price |
| maximumPrice | Maximum price |
| minimumPrice | Minimum price |
| productCount | Product count |
| brandCount | Brand count |
| top5BrandsClickShare | Top 5 brands click share |
| top5ProductsClickShare | Top 5 products click share |
| clickCountT90 | Click count (90-day) |
| clickConversionRateT90 | Click conversion rate (90-day) |
| searchConversionRateT90 | Search conversion rate (90-day) |
| searchVolumeT90 | Search volume (90-day) |
| unitsSoldT90 | Units sold (90-day) |
| unitsSoldGrowthT90 | Units sold growth (90-day) |
| searchVolumeGrowthT90 | Search volume growth (90-day) |
| returnRateT360 | Return rate (360-day) |
| newProductsLaunchedT180 | New products launched (180-day) |
| successfulLaunchesT180 | Successful launches (180-day) |
| launchRateT180 | Launch success rate (180-day) |
| acos | ACOS |
| profitRate50 | Profit rate at 50% organic orders |

### Niche Filtering Parameters

All filter parameters follow a min/max range pattern. Values for percentage-based fields use a 0-1 scale (e.g., 0.05 = 5%).

**Product & Brand Metrics**:

| Parameter | Type | Description |
|-----------|------|-------------|
| productCountMin / productCountMax | integer | Product count range |
| brandCountMin / brandCountMax | integer | Brand count range |
| avgPriceMin / avgPriceMax | number | Average price range |

**Sales & Search Volume**:

| Parameter | Type | Description |
|-----------|------|-------------|
| unitsSoldT7Min / unitsSoldT7Max | integer | Units sold (7-day) range |
| searchVolumeT7Min / searchVolumeT7Max | integer | Search volume (7-day) range |
| clickCountT7Min / clickCountT7Max | integer | Click count (7-day) range |

**Conversion & Click Rates** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| clickConversionRateT7Min / clickConversionRateT7Max | number | Click conversion rate (7-day) range |

**Market Concentration** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| top5BrandsClickShareMin / top5BrandsClickShareMax | number | Top 5 brands click share range |
| top5ProductsClickShareMin / top5ProductsClickShareMax | number | Top 5 products click share range |
| sponsoredProductsPercentageMin / sponsoredProductsPercentageMax | number | SP ad percentage range |

**Brand & Seller Age**:

| Parameter | Type | Description |
|-----------|------|-------------|
| avgBrandAgeMin / avgBrandAgeMax | number | Average brand age (current) |
| avgBrandAgeQoqMin / avgBrandAgeQoqMax | number | Average brand age (90-day) |
| avgBrandAgeYoyMin / avgBrandAgeYoyMax | number | Average brand age (360-day) |
| avgSellingPartnerAgeMin / avgSellingPartnerAgeMax | number | Average seller age (current) |
| avgSellingPartnerAgeQoqMin / avgSellingPartnerAgeQoqMax | number | Average seller age (90-day) |
| avgSellingPartnerAgeYoyMin / avgSellingPartnerAgeYoyMax | number | Average seller age (360-day) |

**New Product & Return Metrics** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| launchRateT180Min / launchRateT180Max | number | Launch success rate (180-day) range |
| newProductRateT180 | number | New product percentage (180-day) min |
| returnRateT360Min / returnRateT360Max | number | Return rate (360-day) range |

**Advertising**:

| Parameter | Type | Description |
|-----------|------|-------------|
| cpcMediumMin / cpcMediumMax | number | CPC (current) range |

## Usage Examples

**1. Basic niche review lookup for a keyword**
```
Analyze customer reviews in niche markets related to "yoga mat" on the US marketplace.
```
Parameters: `{"keyword": "yoga mat", "countryCode": "US"}`

**2. Find niche reviews with high search volume**
```
Show me niche market reviews for "wireless earbuds" where 7-day search volume is above 10000.
```
Parameters: `{"keyword": "wireless earbuds", "countryCode": "US", "searchVolumeT7Min": 10000}`

**3. Low competition niches with review insights**
```
Find review insights for "pet bed" niches where top 5 brands hold less than 30% click share.
```
Parameters: `{"keyword": "pet bed", "countryCode": "US", "top5BrandsClickShareMax": 0.3}`

**4. Japanese market niche reviews**
```
Analyze niche reviews for wireless earbuds on the Japan marketplace.
```
Parameters: `{"keyword": "wireless earbuds", "countryCode": "JP"}`

**5. Sorted by demand score**
```
Show niche reviews for "kitchen organizer" sorted by demand score in descending order.
```
Parameters: `{"keyword": "kitchen organizer", "sortField": "demand", "sortType": "desc"}`

**6. Filter by new product success rate**
```
Find niches for "phone case" where the 180-day new product launch success rate is above 20%.
```
Parameters: `{"keyword": "phone case", "launchRateT180Min": 0.2}`

**7. Low return rate niches**
```
Show review topics for "water bottle" niches with return rates below 5%.
```
Parameters: `{"keyword": "water bottle", "returnRateT360Max": 0.05}`

## Display Rules

1. **Present data clearly**: Show review topics in a well-organized table. Include the niche name, review type (positive/negative), topic, mention percentage, and a review example
2. **Percentage formatting**: Convert 0-1 scale values to percentages for display (e.g., 0.15 -> 15%)
3. **Sentiment separation**: When presenting results, group or clearly label positive vs. negative reviews so users can quickly identify opportunities and pain points
4. **Actionable insight framing**: While showing data objectively, highlight high-mention-percentage negative reviews as potential product improvement opportunities, and high-mention-percentage positive reviews as features to emphasize in listings
5. **Volume notice**: When results are large, show the most relevant data first and remind users about pagination options
6. **Error handling**: When a query fails, explain the reason and suggest adjusting the keyword or filter criteria
7. **Language reminder**: If a user provides a keyword in the wrong language for the target marketplace, remind them to use the marketplace's native language (English for US, German for DE, Japanese for JP)
## User Expression & Scenario Quick Reference

**Applicable** -- Consumer review and sentiment analysis within Amazon niche markets:

| User Says | Scenario |
|-----------|----------|
| "What do customers say about XX" | Niche review topic lookup |
| "Customer pain points for XX" | Negative review analysis |
| "What features do buyers love in XX" | Positive review analysis |
| "Review sentiment for XX niche" | Full sentiment breakdown |
| "Consumer demand insights for XX" | Demand signal extraction from reviews |
| "Common complaints about XX products" | Negative topic mining |
| "What makes XX products popular" | Positive topic mining |
| "Niche market review analysis" | General niche review exploration |

**Not applicable** -- Needs beyond niche review analysis:
- Individual ASIN review analysis (this tool works at the niche/market level)
- Keyword search volume trends without review context (use ABA data tools instead)
- Product listing optimization or copywriting
- Advertising strategy and PPC management
- Sales estimation or revenue forecasting

**Boundary judgment**: When users say "market research" or "product opportunity", if their intent focuses on understanding consumer sentiment, review topics, and pain points within a niche market, this skill applies. If they are asking about search volume trends, pricing strategy, or sales data without review context, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
