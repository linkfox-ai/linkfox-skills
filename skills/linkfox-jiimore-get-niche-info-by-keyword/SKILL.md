---
name: linkfox-jiimore-get-niche-info-by-keyword
description: 按关键词深度分析亚马逊细分市场，涵盖垄断程度、品牌集中度、新品成功率和市场机会评分。当用户提到细分市场分析、关键词市场调研、垄断评估、品牌集中度分析、新品成功率、市场需求评分、竞争格局、亚马逊子市场探索、niche market analysis, keyword market, monopoly level, brand concentration, new product success rate, market opportunity score, competitive landscape, Jiimore data时触发此技能。即使用户未明确提及"细分市场"，只要其需求涉及评估某个关键词维度的亚马逊市场竞争格局、品牌密度或机会潜力，也应触发此技能。
---

# Jiimore Niche Info by Keyword

This skill guides you on how to query and analyze Amazon niche market data by keyword, helping Amazon sellers evaluate market segments for competitive intensity, brand maturity, pricing structure, and entry opportunity.

## 调用方式

- **API 端点**：`POST /jiimore/getNicheInfoByKeyword`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/jiimore_get_niche_info_by_keyword.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-jiimore-get-niche-info-by-keyword-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## Core Concepts

A **niche** (sub-market segment) is a grouping of products that share a common keyword theme on Amazon. This tool returns rich analytical dimensions for each niche, including search volume, sales volume, click-through rates, brand count, top-brand concentration, new product launch success rates, CPC estimates, and a composite demand score. Data is available for **US**, **JP**, and **DE** marketplaces.

**Keyword is required**: Every query must include a `keyword`. The keyword should be provided in the language of the target marketplace (e.g., English for US, Japanese for JP, German for DE). When the user provides a keyword in a different language, translate it to the marketplace language before calling the API.

**Percentage fields**: Several parameters and response fields use a 0-1 decimal range representing 0%-100%. When displaying these values to users, convert them to percentages (e.g., 0.35 -> 35%).

**Demand score**: The `demand` field is a composite opportunity score assigned to each niche. A higher value indicates greater market demand potential.

## Parameter Guide

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| keyword | string | Search keyword (max 1000 chars). Translate to the target marketplace language. |

### Marketplace & Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| countryCode | string | US | Country code: US, JP, DE |
| page | integer | 1 | Page number (starts from 1) |
| pageSize | integer | 50 | Results per page (10-100) |
| sortField | string | unitsSoldT7 | Field to sort by (see Sorting Options below) |
| sortType | string | desc | Sort direction: `desc` or `asc` |

### Filter Parameters (all optional, min/max ranges)

**Product & Pricing**:
| Parameter | Type | Description |
|-----------|------|-------------|
| productCountMin / productCountMax | integer | Product count range |
| avgPriceMin / avgPriceMax | number | Average price range |

**Search & Sales (7-day)**:
| Parameter | Type | Description |
|-----------|------|-------------|
| searchVolumeT7Min / searchVolumeT7Max | integer | Weekly search volume range |
| unitsSoldT7Min / unitsSoldT7Max | integer | Weekly units sold range |
| clickCountT7Min / clickCountT7Max | integer | Weekly click count range |
| clickConversionRateT7Min / clickConversionRateT7Max | number | Weekly click conversion rate (0-1) |

**Brand Metrics**:
| Parameter | Type | Description |
|-----------|------|-------------|
| brandCountMin / brandCountMax | integer | Number of brands in niche |
| top5BrandsClickShareMin / top5BrandsClickShareMax | number | Top 5 brands click share (0-1) |
| avgBrandAgeMin / avgBrandAgeMax | number | Average brand age (current) |
| avgBrandAgeQoqMin / avgBrandAgeQoqMax | number | Average brand age (90-day) |
| avgBrandAgeYoyMin / avgBrandAgeYoyMax | number | Average brand age (360-day) |

**Seller Metrics**:
| Parameter | Type | Description |
|-----------|------|-------------|
| avgSellingPartnerAgeMin / avgSellingPartnerAgeMax | number | Average seller age (current) |
| avgSellingPartnerAgeQoqMin / avgSellingPartnerAgeQoqMax | number | Average seller age (90-day) |
| avgSellingPartnerAgeYoyMin / avgSellingPartnerAgeYoyMax | number | Average seller age (360-day) |

**Competition & Advertising**:
| Parameter | Type | Description |
|-----------|------|-------------|
| top5ProductsClickShareMin / top5ProductsClickShareMax | number | Top 5 products click share (0-1) |
| sponsoredProductsPercentageMin / sponsoredProductsPercentageMax | number | SP ad percentage (0-1) |
| cpcMediumMin / cpcMediumMax | number | CPC median value range |

**New Product & Returns**:
| Parameter | Type | Description |
|-----------|------|-------------|
| launchRateT180Min / launchRateT180Max | number | 180-day new product success rate (0-1) |
| newProductRateT180 | number | 180-day new product ratio minimum (0-1) |
| returnRateT360Min / returnRateT360Max | number | 360-day return rate (0-1) |

### Sorting Options

| Value | Meaning |
|-------|---------|
| unitsSoldT7 | Weekly units sold |
| searchVolumeT7 | Weekly search volume |
| demand | Demand score |
| avgPrice | Average price |
| maximumPrice | Maximum price |
| minimumPrice | Minimum price |
| productCount | Product count |
| searchConversionRateT7 | Weekly search conversion rate |
| clickConversionRateT7 | Weekly click conversion rate |
| searchVolumeGrowthT7 | Search volume growth rate |
| clickCountT7 | Weekly click count |
| clickCountT90 | 90-day click count |
| brandCount | Brand count |
| top5BrandsClickShare | Top 5 brands click share |
| top5ProductsClickShare | Top 5 products click share |
| newProductsLaunchedT180 | 180-day new products launched |
| successfulLaunchesT180 | 180-day successful launches |
| launchRateT180 | 180-day launch success rate |
| returnRateT360 | Annual return rate |
| clickConversionRateT90 | 90-day click conversion rate |
| searchConversionRateT90 | 90-day search conversion rate |
| searchVolumeT90 | 90-day search volume |
| unitsSoldT90 | 90-day units sold |
| unitsSoldGrowthT90 | 90-day sales growth rate |
| searchVolumeGrowthT90 | 90-day search volume growth rate |
| acos | Advertising cost of sales |
| profitRate50 | Profit margin at 50% organic sales |

## Usage Examples

**1. Basic niche exploration by keyword**
Query niches related to "wireless earbuds" in the US market, sorted by weekly sales volume:
```json
{
  "keyword": "wireless earbuds",
  "countryCode": "US",
  "sortField": "unitsSoldT7",
  "sortType": "desc"
}
```

**2. Low-competition niche discovery**
Find niches for "yoga mat" where the top 5 brands hold less than 50% click share and brand count exceeds 20:
```json
{
  "keyword": "yoga mat",
  "countryCode": "US",
  "top5BrandsClickShareMax": 0.5,
  "brandCountMin": 20,
  "sortField": "demand",
  "sortType": "desc"
}
```

**3. High-demand, high-conversion niches**
Find niches for "phone case" with weekly search volume above 10000 and click conversion rate above 10%:
```json
{
  "keyword": "phone case",
  "countryCode": "US",
  "searchVolumeT7Min": 10000,
  "clickConversionRateT7Min": 0.1,
  "sortField": "searchVolumeT7",
  "sortType": "desc"
}
```

**4. New product opportunity analysis**
Find niches for "LED light" with high new product success rate (above 20%) and low return rate (below 5%):
```json
{
  "keyword": "LED light",
  "countryCode": "US",
  "launchRateT180Min": 0.2,
  "returnRateT360Max": 0.05,
  "sortField": "launchRateT180",
  "sortType": "desc"
}
```

**5. Japanese market niche research**
Explore niches related to headphones in Japan, sorted by demand score:
```json
{
  "keyword": "\u30d8\u30c3\u30c9\u30db\u30f3",
  "countryCode": "JP",
  "sortField": "demand",
  "sortType": "desc"
}
```

**6. Price-range-specific niche analysis**
Find niches for "backpack" with average price between $20 and $50 and low advertising saturation:
```json
{
  "keyword": "backpack",
  "countryCode": "US",
  "avgPriceMin": 20,
  "avgPriceMax": 50,
  "sponsoredProductsPercentageMax": 0.3,
  "sortField": "unitsSoldT7",
  "sortType": "desc"
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables. Convert decimal ratios to percentages for readability (e.g., 0.25 -> 25%).
2. **Highlight key metrics**: Always surface the niche title, demand score, weekly search volume, weekly sales, brand count, and top 5 brands click share as primary columns.
3. **Translate niche titles**: When the `translationZh` field is present and the user prefers Chinese, show it alongside the original `nicheTitle`.
4. **Pagination guidance**: When `total` exceeds the current page size, inform the user of the total count and suggest fetching additional pages if needed.
5. **Error handling**: When a query fails, explain the reason based on the response message and suggest adjusting filter criteria (e.g., broadening ranges or checking the keyword).
6. **CPC display**: When CPC data is present, show all three tiers (low, medium, high) to give a complete advertising cost picture.
7. **No subjective advice**: Present data objectively without adding unsolicited business recommendations. Only provide interpretation when explicitly requested by the user.
## Important Limitations

- **Supported marketplaces**: Only US, JP, and DE are available. Other marketplace codes will be rejected.
- **Keyword required**: Every query must include a keyword. The API will not return results without one.
- **Result cap**: Maximum 100 results per page.
- **Percentage values**: All rate/share parameters use 0-1 range, not 0-100. Ensure correct values when constructing filters.

## User Expression & Scenario Quick Reference

**Applicable** -- Niche-level market segment analysis by keyword:

| User Says | Scenario |
|-----------|----------|
| "Is there opportunity in the XX market" | Niche opportunity assessment |
| "How competitive is XX keyword" | Monopoly / brand concentration |
| "Find low-competition niches for XX" | Blue ocean niche discovery |
| "What's the new product success rate for XX" | New entrant viability |
| "Show me niche data for XX" | General niche exploration |
| "Which XX niches have high demand" | Demand-driven niche ranking |
| "What's the CPC / ad cost for XX niches" | Advertising cost analysis |
| "Find niches with high conversion for XX" | Conversion-optimized segments |
| "Brand concentration in XX market" | Brand dominance assessment |

**Not applicable** -- Needs beyond niche-level segment data:
- Individual ASIN performance or sales estimation
- Search term ranking trends (use ABA data tools instead)
- Advertising campaign management or bid optimization
- Product review analysis or listing optimization
- Supplier sourcing or logistics planning

**Boundary judgment**: When users say "market research" or "product opportunity", if their intent focuses on evaluating the competitive landscape and demand potential of keyword-level market segments, this skill applies. If they need ASIN-level data, search term ranking trends, or comprehensive business strategy, direct them to the appropriate tool.

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
