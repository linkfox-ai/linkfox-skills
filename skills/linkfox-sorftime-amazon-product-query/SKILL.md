---
name: linkfox-sorftime-amazon-product-query
description: "基于Sorftime数据的亚马逊多维度产品搜索与筛选，涵盖14个站点，支持历史月份快照回看。当用户提到Sorftime产品搜索、亚马逊产品筛选、竞品调研、类目分析、品牌热销、卖家分析、季节性产品、历史快照回看、产品搜索、月销量月销额、ABA关键词找产品、价格范围筛选、新品发现、多条件组合筛选、product search, competitor research, category analysis, brand bestsellers, seller analysis, seasonal products, historical snapshot时触发此技能。即使用户未明确提及\"Sorftime\"，只要其需求涉及亚马逊产品搜索、筛选、对比或类目/品牌/卖家维度的产品探索，也应触发此技能。"
---

# Sorftime Product Search

This skill guides you on how to search and filter Amazon products via Sorftime across multiple dimensions, helping Amazon sellers discover products, analyze competitors, and explore market opportunities.

## Core Concepts

Sorftime Product Search supports multi-dimensional product retrieval with 16 query types, single or multi-condition AND combinations, and historical monthly snapshot lookback from January 2024. Data covers pricing, BSR rankings, monthly sales, FBA fees, and profit analysis.

**Key differentiator**: This tool is for searching and filtering across products. If you need detailed trend data (sales/price/BSR history) for a specific ASIN, use the Sorftime Product Detail skill instead.

## Data Fields

Response data covers the following categories (see `references/api.md` for complete field reference):

- **Basic info**: ASIN, title, brand, listing URL, images (main + list), parent ASIN, variation count, weight, size
- **Pricing & profit**: current price, sale price (after coupon), strikethrough price, coupon, FBA fees (with detail breakdown), platform fee, profit amount & rate
- **Sales**: monthly sales units, monthly revenue, daily sales, daily revenue (values of -1 = cannot estimate)
- **Rankings**: BSR rank, category, sub-category rankings
- **Ratings**: rating score, rating count
- **Listing info**: listing date, days online
- **Seller**: Buybox seller name/ID/country, FBA status, seller count
- **Listing features**: A+ content, video, brand store

## Supported Marketplaces

US (United States), GB (United Kingdom), DE (Germany), FR (France), IN (India), CA (Canada), JP (Japan), ES (Spain), IT (Italy), MX (Mexico), AE (United Arab Emirates), AU (Australia), BR (Brazil), SA (Saudi Arabia)

Default marketplace is **US**. Use `us` when the user doesn't specify a marketplace.

**Note**: Sorftime uses lowercase codes (e.g., `us`, `gb`, `de`), and UK is coded as `gb` (not `uk`).

## 调用方式

- **API 端点**：`POST /sorftime/amazon/productQuery`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sorftime_product_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sorftime-amazon-product-query-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。
## How to Build Queries

The key parameters are `marketplace` (required), `queryMode`, `queryType`, and `queryValue`. The query system has two modes and 16 filter types that can be combined flexibly.

### Principles for Building Queries

1. **Always specify the marketplace**: Use lowercase site codes, e.g., `us`, `de`, `jp`
2. **Choose the right query mode**: Use `queryMode=1` for a single filter; use `queryMode=2` to combine multiple filters with AND logic
3. **Match queryType with queryValue format**: Each queryType expects a specific format - see the table below. Mismatched formats will cause errors
4. **Mind price units**: Price filters (queryType=8) use smcurrency unit (cents for USD), so $19.99 = `1999`
5. **Use open ranges when appropriate**: Omit one end for open range - `,1000` means "up to 1000"; `100,` means "100 or more"
6. **Use queryMonth for historical comparison**: Format `yyyy-MM`; compare with a second call without queryMonth to see changes over time

### Query Types (queryType, for queryMode=1)

| queryType | Name | queryValue Format | Example |
|-----------|------|-------------------|---------|
| 1 | ASIN Similar | ASIN | `B0CVM8TXHP` |
| 2 | Category | NodeId | `3743561` |
| 3 | Brand | Brand name | `Anker` |
| 4 | Seller Name | Store name | `AnkerDirect` |
| 5 | Seller ID | SellerId | `A294P4X9EWVXLJ` |
| 6 | ABA Keyword | Keyword | `Power Bank` |
| 7 | Title/Attribute Match | Keywords | `10,000mAh 30W` |
| 8 | Price Range | `min,max` (in cents) | `1,1000` (=$0.01~$10) |
| 9 | Monthly Sales Range | `min,max` | `100,1000` |
| 10 | Seasonal Products | Month list | `1,2,3` (peak in Jan-Mar) |
| 11 | Listing Date Range | `start,end` (yyyy-MM-dd) | `2024-06-01,2024-12-01` |
| 12 | Rating Range | `min,max` | `3,5` |
| 13 | Review Count Range | `min,max` | `10,500` |
| 14 | Rank Range | `bsr_min,bsr_max;sub_min,sub_max` | `500,5000;1,100` |
| 15 | Fulfillment | `FBA` / `FBM` | `FBA,FBM` |
| 16 | Variation Count | `min,max` | `1,50` |

**Important**: queryType=1 (ASIN Similar) finds products similar to the given ASIN, not the ASIN itself. To query a single product's detail, use the Sorftime Product Detail skill.

### Historical Snapshots (queryMonth)

Set `queryMonth` (format `yyyy-MM`) to query a past month's product data snapshot. This lets users compare historical prices, rankings, and sales with current data.

- Supported range: January 2024 to present (~2 years)
- US, GB, DE support full "unlimited" lookback mode
- Other sites support Top 100 products only in lookback
- AU, BR, IN do **not** support lookback

### Query Examples for Common Scenarios

**1. Fititors of a given ASIN**
```
queryMode: 1, queryType: 1, queryValue: B0CVM8TXHP, marketplace: us
```

**2. Browse a category's top products**
```
queryMode: 1, queryType: 2, queryValue: 3743561, marketplace: us
```

**3. Analyze a brand's product portfolio**
```
queryMode: 1, queryType: 3, queryValue: Anker, marketplace: us
```

**4. Search by ABA keyword**
```
queryMode: 1, queryType: 6, queryValue: Power Bank, marketplace: us
```

**5. Discover seasonal products (Q4 peak)**
```
queryMode: 1, queryType: 10, queryValue: 10,11,12, marketplace: us
```

**6. Compare historical vs current data**
```
queryMonth: 2024-11, queryMode: 1, queryType: 2, queryValue: 3743561, marketplace: us
-> Compare with current data (no queryMonth) to see price/sales changes
```

**7. Multi-condition: new FBA products with good sales**
```
queryMode: 2
queryValue: [{"QueryType":11,"Content":"2024-06-01,"},{"QueryType":9,"Content":"300,"},{"QueryType":15,"Content":"FBA"}]
marketplace: us
```

**8. Find low-price high-sales products**
```
queryMode: 2
queryValue: [{"QueryType":8,"Content":",2000"},{"QueryType":9,"Content":"500,"}]
marketplace: us
```

**9. Check a seller's product portfolio**
```
queryMode: 1, queryType: 4, queryValue: AnkerDirect, marketplace: us
```

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Ranking clarification**: When showing ranking data, remind users that lower values mean better rankings
3. **Pagination notice**: Search results return max 100 products per page, up to 200 pages. If results are large, show highlights and remind users to paginate
4. **Sales estimation caveat**: Values of `-1` in sales/revenue fields mean "cannot estimate" - explain this to the user rather than showing -1 directly
5. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query criteria

## Important Limitations

- **Pagination**: Max 100 products per page, max 200 pages
- **Historisupported
- **Non-structured data**: Results do not support secondary analysis via `_dataQuery_executeDynamicQuery`
- **Sales estimation**: Products in non-standard categories may return -1 for sales fields
- **ABA keyword search** (queryType=6): Currently only supports ABA keywords, not arbitrary search terms

## User Expression & Scenario Quick Reference

**Applicable** - Product search and filtering on Amazon:

| User Says | Scenario |
|-----------|--------|
| "找一下这个类目下卖得好的产品" | Category exploration |
| "Anker品牌有哪些热销产品" | Brand analysis |
| "这个ASIN的竞品有哪些" | Competitor discovery |
| "帮我找一些季节性产品" | Seasonal product discovery |
| "新品中月销量超过500的有哪些" | Filtered product discovery |
| "去年双十一这个类目的价格快照" | Historical snapshot comparison |
| "这个卖家还卖了什么产品" | Seller portfolio |
| "帮我筛选利润率高于30%的FBA产品" | Profit-focused filtering |
| "月销量1000以上，评分4星以上的产品" | Multi-condition filtering |
| "标题包含wireless charger的产品" | Title keyword search |

**Not applicable** - Needs beyond product search:
- Detailed trend/history data for a specific ASIN (use Sorftime Product Detail)
- ABA search term ranking data (use ABA Data Explorer)
- Advertising / PPC strategy
- Product reviews content analysis
- Patent or trademark checks

**Boundary judgment**: When users say "competitor analysis" or "market research", if they need to discover and compare products across dimensions (category, brand, price range, etc.), this skill applies. If they need historical trend curves for a specific ASIN, use the Prt Detail skill. If they need keyword search volume data, use ABA Data Explorer.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
