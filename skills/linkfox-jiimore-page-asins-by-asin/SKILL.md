---
name: linkfox-jiimore-page-asins-by-asin
description: 按ASIN查找亚马逊同细分市场（Niche）竞品，支持点击转化率、综合转化率、点击量、销量、评论、评分、价格、毛利率等多维度筛选潜力竞品。当用户提到同细分竞品、ASIN竞品挖掘、Niche竞品分析、同类商品对标、ASIN对标分析、细分市场竞品列表、高转化竞品筛选、极目产品挖掘、niche competitor by ASIN, ASIN competitor analysis, same niche products, similar products discovery, conversion rate comparison, potential competitor screening, Jiimore ASIN mining时触发此技能。即使用户未明确提及"细分市场"或"Niche"，只要其需求涉及根据某个ASIN挖掘同细分下的竞品列表或筛选潜力竞品，也应触发此技能。
---

# Jiimore Niche Competitor by ASIN

This skill guides you on how to query and filter Amazon competing products in the same niche segments as a reference ASIN, helping Amazon sellers discover potential competitors and evaluate opportunities using metrics such as click conversion rate, composite conversion rate, click volume, sales volume, reviews, price, FBA fees, and gross profit margin.

## Core Concepts

Given a reference ASIN, the tool **mines competing ASINs that share the same niche segments** on Amazon and returns a paginated list with rich metrics: click conversion rate, composite conversion rate, click counts (7-day/30-day/90-day), sales volume, pricing, FBA fees, gross profit margin, customer rating, and 90-day trend data. Data is available for **US**, **JP**, and **DE** marketplaces only.

**ASIN is required**: Every query must include a reference `asin`. The tool finds products that share the same niche segments as this ASIN and returns them with detailed metrics.

**Percentage fields**: Several parameters use a 0-1 decimal range representing 0%-100%. When displaying these values to users, convert them to percentages (e.g., 0.15 -> 15%).

**Date format**: Launch date parameters use the format `yyyyMMdd000000` (e.g., `20240101000000` for January 1, 2024).

## Parameter Guide

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| asin | string | Reference ASIN to find competing products for (max 1000 chars) |

### Marketplace & Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| countryCode | string | US | Country code: US, JP, DE |
| page | integer | 1 | Page number (starts from 1) |
| pageSize | integer | 50 | Results per page (10-100) |
| sortField | string | purchasedClicksT360 | Field to sort by (see Sorting Options below) |
| sortType | string | desc | Sort direction: `desc` or `asc` |

### Filter Parameters (all optional, min/max ranges)

**Price & FBA**:
| Parameter | Type | Description |
|-----------|------|-------------|
| priceMin / priceMax | number | Product price range |
| fbaFeeMin / fbaFeeMax | number | FBA commission range |
| grossProfitMarginMin / grossProfitMarginMax | number | Gross profit margin range |

**Reviews & Ratings**:
| Parameter | Type | Description |
|-----------|------|-------------|
| totalReviewsMin / totalReviewsMax | integer | Total review count range |
| customerRatingMin / customerRatingMax | number | Customer rating range (0.0-5.0) |

**Click Data (7-day)**:
| Parameter | Type | Description |
|-----------|------|-------------|
| clickCountT7Min / clickCountT7Max | integer | Weekly click count range |
| clickCountGrowthT7Min / clickCountGrowthT7Max | number | Weekly click growth rate (0-1) |
| clickConversionRateMin / clickConversionRateMax | number | Click conversion rate (0-1) |

**Click Data (30-day)**:
| Parameter | Type | Description |
|-----------|------|-------------|
| clickCountT30Min / clickCountT30Max | integer | Monthly click count range |
| clickCountGrowthT30Min / clickCountGrowthT30Max | number | Monthly click growth rate (0-1) |

**Composite Conversion**:
| Parameter | Type | Description |
|-----------|------|-------------|
| clickConversionRateCompositeMin / clickConversionRateCompositeMax | number | Composite click conversion rate (0-1) |

**Sales & Launch Date**:
| Parameter | Type | Description |
|-----------|------|-------------|
| salesVolumeT360Min / salesVolumeT360Max | integer | 360-day sales volume range |
| launchDateMin / launchDateMax | string | Launch date range (format: yyyyMMdd000000) |

**Niche & Seller**:
| Parameter | Type | Description |
|-----------|------|-------------|
| nicheCountMin / nicheCountMax | integer | Number of niches the product belongs to |
| sellerCountry | string | Seller country code(s), comma-separated (e.g., "CN,US") |

### Sorting Options

| Value | Meaning |
|-------|---------|
| purchasedClicksT360 | 360-day purchased clicks (default) |
| totalReviews | Total reviews |
| price | Price |
| launchDate | Launch date |
| clickCountT30 | 30-day click count |
| clickCountT90 | 90-day click count |
| clickCountT7 | 7-day click count |
| clickConversionRate | Click conversion rate |
| clickConversionRateComposite | Composite click conversion rate |
| customerRating | Customer rating |
| clickCountGrowthT7 | Weekly click growth rate |
| clickCountGrowthT30 | Monthly click growth rate |
| currentPrice | Current price |
| fbaFee | FBA commission |
| shippingFee | FBA shipping fee |
| gpm | Gross profit margin |

## 调用方式

- **API 端点**：`POST /jiimore/pageAsinsByAsin`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/jiimore_page_asins_by_asin.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-jiimore-page-asins-by-asin-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## Usage Examples

**1. Basic competitor lookup by ASIN**
Find competing products for a reference ASIN in the US market:
```json
{
  "asin": "B0GC4RPX79",
  "countryCode": "US",
  "sortField": "purchasedClicksT360",
  "sortType": "desc"
}
```

**2. High-conversion competitors**
Find competitors with composite conversion rate above 15%:
```json
{
  "asin": "B0GC4RPX79",
  "countryCode": "US",
  "clickConversionRateCompositeMin": 0.15,
  "sortField": "clickConversionRateComposite",
  "sortType": "desc"
}
```

**3. New product opportunities**
Find recently launched competitors (within 3 months) with high click growth:
```json
{
  "asin": "B0GC4RPX79",
  "countryCode": "US",
  "launchDateMin": "20240101000000",
  "clickCountGrowthT7Min": 0.1,
  "sortField": "clickCountGrowthT7",
  "sortType": "desc"
}
```

**4. Price-range filtered competitors**
Find competitors priced between $20 and $50 with good gross margins:
```json
{
  "asin": "B0GC4RPX79",
  "countryCode": "US",
  "priceMin": 20,
  "priceMax": 50,
  "grossProfitMarginMin": 0.3,
  "sortField": "gpm",
  "sortType": "desc"
}
```

**5. High-click low-review competitors (potential weak spots)**
Find competitors with monthly clicks above 2000 but fewer than 100 reviews:
```json
{
  "asin": "B0GC4RPX79",
  "countryCode": "US",
  "clickCountT30Min": 2000,
  "totalReviewsMax": 100,
  "sortField": "clickCountT30",
  "sortType": "desc"
}
```

**6. Japanese market competitor analysis**
Explore competitors in the Japanese market sorted by rating:
```json
{
  "asin": "B0GC4RPX79",
  "countryCode": "JP",
  "sortField": "customerRating",
  "sortType": "desc"
}
```

**7. Chinese sellers in the same niche**
Filter competitors by seller country (China) with high sales volume:
```json
{
  "asin": "B0GC4RPX79",
  "countryCode": "US",
  "sellerCountry": "CN",
  "salesVolumeT360Min": 1000,
  "sortField": "purchasedClicksT360",
  "sortType": "desc"
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables. Convert decimal ratios to percentages for readability (e.g., 0.25 -> 25%).
2. **Highlight key metrics**: Always surface the ASIN, product title, price, customer rating, click conversion rate (composite), click counts, total reviews, and gross profit margin as primary columns.
3. **Show niche context**: When the `niches` field is present, display the top niche titles and demand scores to give context about which market segments the product competes in.
4. **Trends visualization**: When `trends` data is available, summarize the 90-day trend direction (rising/falling/stable) for key metrics like clicks and pricing.
5. **Pagination guidance**: When `total` exceeds the current page size, inform the user of the total count and suggest fetching additional pages if needed.
6. **Error handling**: When a query fails, explain the reason based on the response message and suggest adjusting filter criteria (e.g., broadening ranges or checking the ASIN).
7. **No subjective advice**: Present data objectively without adding unsolicited business recommendations. Only provide interpretation when explicitly requested by the user.

## Important Limitations

- **Supported marketplaces**: Only US, JP, and DE are available. Other marketplace codes will be rejected.
- **ASIN required**: Every query must include a reference ASIN. The API will not return results without one.
- **Result cap**: Maximum 100 results per page.
- **Percentage values**: All rate/share parameters use 0-1 range, not 0-100. Ensure correct values when constructing filters.
- **Date format**: Launch date parameters must use `yyyyMMdd000000` format.

## User Expression & Scenario Quick Reference

**Applicable** -- Finding competing products based on a reference ASIN:

| User Says | Scenario |
|-----------|----------|
| "Find competitors for ASIN B0GC4RPX79" | Direct competitor lookup |
| "What products compete with this ASIN" | Same-niche competitor exploration |
| "Show me similar products in the same niche" | Niche competitor discovery |
| "High-conversion competitors for my product" | Conversion-based competitor filtering |
| "New products competing in my niche" | New entrant identification |
| "Which Chinese sellers compete with this ASIN" | Seller-origin based filtering |
| "Find low-review high-click products like mine" | Opportunity gap analysis |
| "Competitor pricing analysis for ASIN XX" | Price-focused competitor analysis |

**Not applicable** -- Needs beyond ASIN-based same-niche competitor discovery:

- Keyword-level niche market analysis (use Jiimore Niche Info by Keyword instead)
- Individual ASIN revenue or profit estimation
- ABA search term data / keyword research
- Advertising campaign management or bid optimization
- Product review analysis or listing optimization
- Supplier sourcing or logistics planning

**Boundary judgment**: When users say "competitor analysis" or "similar products," if their intent focuses on finding products that compete in the same niche as a specific ASIN, this skill applies. If they want keyword-level market segment data, direct them to Jiimore Niche Info by Keyword. If they need detailed product data for a single ASIN, direct them to Amazon Product Detail.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
