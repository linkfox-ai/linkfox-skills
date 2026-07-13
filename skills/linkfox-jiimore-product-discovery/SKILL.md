---
name: linkfox-jiimore-product-discovery
description: 基于极目数据的亚马逊商品发掘与潜力爆品挖掘。当用户提到产品挖掘、潜力爆品、高转化选品、点击增长分析、市场增长机会、关键词选品、FBA利润筛选、细分市场商品发掘、卖家来源筛选、product mining, potential bestsellers, high-conversion product selection, market growth opportunities, Jiimore data, FBA profitability screening, keyword-based product selection时触发此技能。即使用户未明确提及"极目"，只要其需求涉及基于转化率、点击量和利润指标的亚马逊关键词驱动选品，也应触发此技能。
---

# Jiimore Product Discovery

This skill guides you on how to discover and mine high-potential Amazon products using the Jiimore product discovery engine, helping Amazon sellers find potential bestsellers through keyword-based filtering with conversion, click growth, and profitability indicators.

## Core Concepts

Jiimore Product Discovery is a keyword-driven Amazon product mining tool. Given a search keyword, it returns a list of products matching specified performance criteria such as conversion rate, click growth rate, gross profit margin, pricing, reviews, and listing age. This makes it ideal for identifying emerging opportunities, validating product ideas, and competitive benchmarking.

**Keyword is required**: Every query must include a `keyword`. The keyword should be translated into the language of the target marketplace (e.g., Japanese for JP, German for DE).

**Rate values are decimals**: Conversion rates and growth rates are expressed as decimals between 0 and 1. For example, `0.1` means 10%, `0.25` means 25%. This is a common point of confusion when users specify percentages.

**Marketplace support**: Currently supports US (United States), JP (Japan), and DE (Germany). Default is **US**. Use US when the user doesn't specify a marketplace.

## Parameter Guide

### Required

| Parameter | Description | Example |
|-----------|-------------|---------|
| keyword | Search keyword (must be translated to the target marketplace language) | wireless charger |

### Filtering Parameters

| Parameter | Description | Value Format |
|-----------|-------------|--------------|
| priceMin / priceMax | Product price range | Number (e.g., 10.0, 50.0) |
| totalReviewsMin / totalReviewsMax | Review count range | Integer (e.g., 0, 500) |
| customerRatingMin / customerRatingMax | Customer rating range | Number (e.g., 4.0, 5.0) |
| clickConversionRateMin / clickConversionRateMax | Click-to-purchase conversion rate | Decimal 0-1 (0.1 = 10%) |
| clickConversionRateCompositeMin / clickConversionRateCompositeMax | Composite conversion rate | Decimal 0-1 (0.1 = 10%) |
| clickCountT7Min / clickCountT7Max | Weekly click count range | Integer |
| clickCountT30Min / clickCountT30Max | Monthly click count range | Integer |
| clickCountGrowthT7Min / clickCountGrowthT7Max | Weekly click growth rate | Decimal 0-1 (0.1 = 10%) |
| clickCountGrowthT30Min / clickCountGrowthT30Max | Monthly click growth rate | Decimal 0-1 (0.1 = 10%) |
| salesVolumeT360Min / salesVolumeT360Max | Annual sales volume range | Integer |
| grossProfitMarginMin / grossProfitMarginMax | Gross profit margin range | Number |
| fbaFeeMin / fbaFeeMax | FBA fee range | Number |
| launchDateMin / launchDateMax | Listing date range | String: yyyyMMdd000000 |
| nicheCountMin / nicheCountMax | Niche market count range | Integer |
| sellerCountry | Seller origin country code(s), comma-separated | CN,US |
| countryCode | Target marketplace (US, JP, DE) | US |

### Sorting & Pagination

| Parameter | Description | Default |
|-----------|-------------|---------|
| sortField | Sort by field (see options below) | purchasedClicksT360 |
| sortType | Sort direction: `desc` or `asc` | desc |
| page | Page number | 1 |
| pageSize | Results per page (10-100) | 50 |

**Available sort fields**: totalReviews, price, launchDate, clickCountT7, clickCountT30, clickCountT90, clickConversionRate, clickConversionRateComposite, customerRating, purchasedClicksT360, clickCountGrowthT7, clickCountGrowthT30, currentPrice, fbaFee, shippingFee, gpm

## 调用方式

- **API 端点**：`POST /jiimore/productDiscovery`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/jiimore_product_discovery.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-jiimore-product-discovery-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## Usage Examples

**1. Find high-conversion wireless chargers in the US market**
```json
{
  "keyword": "wireless charger",
  "countryCode": "US",
  "clickConversionRateMin": 0.1,
  "sortField": "clickConversionRate",
  "sortType": "desc"
}
```

**2. Discover fast-growing new products (listed within the last 6 months, weekly click growth > 20%)**
```json
{
  "keyword": "desk lamp",
  "countryCode": "US",
  "launchDateMin": "20250901000000",
  "clickCountGrowthT7Min": 0.2,
  "sortField": "clickCountGrowthT7",
  "sortType": "desc"
}
```

**3. Find underpriced high-margin products with low competition (few reviews)**
```json
{
  "keyword": "phone stand",
  "countryCode": "US",
  "priceMin": 10,
  "priceMax": 30,
  "totalReviewsMax": 100,
  "grossProfitMarginMin": 0.3,
  "sortField": "gpm",
  "sortType": "desc"
}
```

**4. Mine products from Chinese sellers with strong monthly click growth in the German market**
```json
{
  "keyword": "Handyhuelle",
  "countryCode": "DE",
  "sellerCountry": "CN",
  "clickCountGrowthT30Min": 0.15,
  "sortField": "clickCountGrowthT30",
  "sortType": "desc"
}
```

**5. Find high-rated products with strong annual sales in the Japanese market**
```json
{
  "keyword": "ワイヤレスイヤホン",
  "countryCode": "JP",
  "customerRatingMin": 4.0,
  "salesVolumeT360Min": 1000,
  "sortField": "purchasedClicksT360",
  "sortType": "desc"
}
```

**6. Identify niche opportunities with high composite conversion and multiple niche markets**
```json
{
  "keyword": "yoga mat",
  "countryCode": "US",
  "clickConversionRateCompositeMin": 0.15,
  "nicheCountMin": 3,
  "sortField": "clickConversionRateComposite",
  "sortType": "desc"
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables, including product title, ASIN, price, ratings, conversion rates, click counts, and growth rates
2. **Rate formatting**: Always display rate values as percentages for readability (e.g., show 0.12 as 12%). Remind users that the API accepts decimals (0-1)
3. **Image display**: When product image URLs are available, display the main product image alongside the data
4. **Pagination awareness**: When results span multiple pages, inform the user of the total count and current page, and offer to fetch additional pages
5. **Keyword translation reminder**: Remind users that keywords must be in the target marketplace language (English for US, Japanese for JP, German for DE)
6. **Error handling**: When a query fails, explain the reason based on the response and suggest adjusting query criteria
7. **No subjective advice**: Present factual product data without making subjective business recommendations
## Important Limitations

- **Keyword is mandatory**: Every query requires a keyword; browsing without a keyword is not supported
- **Three marketplaces only**: Currently limited to US, JP, and DE
- **Page size cap**: Maximum 100 results per page
- **Rate values**: All rate/percentage parameters must be passed as decimals (0-1), not percentages
- **Launch date format**: Must follow the `yyyyMMdd000000` format exactly (e.g., `20250101000000`)

## User Expression & Scenario Quick Reference

**Applicable** -- Product discovery and mining tasks:

| User Says | Scenario |
|-----------|----------|
| "Find hot products for keyword X" | Keyword-based product discovery |
| "High conversion products", "best sellers" | High-conversion product screening |
| "Fast growing products", "trending items" | Click growth-based discovery |
| "New products with high potential" | New listing + growth filtering |
| "Products with good margins", "profitable items" | Gross profit margin screening |
| "Low competition products", "few reviews" | Low-review opportunity mining |
| "Products from Chinese sellers" | Seller origin filtering |
| "Niche market opportunities" | Niche count-based discovery |

**Not applicable** -- Needs beyond product discovery:

- ABA search term data and keyword analysis (use ABA Data Explorer)
- Advertising / PPC campaign management
- Product reviews and listing optimization
- Inventory management and supply chain
- Comprehensive market reports with profit/pricing strategy

## 积分消耗规则

消耗 9 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
