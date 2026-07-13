---
name: linkfox-ebay-search
description: 在多个eBay国际站点上搜索和浏览商品listing。当用户提到eBay商品搜索、eBay listing查询、eBay价格对比、eBay市场浏览、eBay已售商品、eBay拍卖搜索、eBay选品调研、eBay search, eBay products, eBay pricing, eBay competitors, sold items, eBay auctions, eBay market analysis时触发此技能。即使用户未明确提及"eBay"，只要其需求涉及在eBay上搜索商品、对比eBay价格、查找已成交listing或分析eBay市场数据，也应触发此技能。
---

# eBay Product Search

This skill guides you on how to search and retrieve eBay product listing data, helping e-commerce sellers and buyers find products, compare prices, and analyze market trends across eBay's global marketplaces.

## Core Concepts

eBay Product Search provides access to eBay's front-end product listing data. It supports keyword-based search with rich filtering options including price range, item condition, buying format, sort order, seller location, and more. Results include product details such as title, price, shipping info, seller rating, sold quantity, and item condition.

**Marketplace logic**: The `ebayDomain` parameter controls which regional eBay site is searched. The default is `ebay.com` (US). When a user refers to a country or region, map it to the corresponding eBay domain (e.g., UK -> `ebay.co.uk`, Germany -> `ebay.de`).

**Buying format**: eBay supports multiple buying formats -- `Auction` for bid-based listings, `BIN` (Buy It Now) for fixed-price listings, and `BO` (Best Offer) for negotiable listings.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| keyword | string | No | Search keyword, up to 1024 characters | - |
| ebayDomain | string | No | eBay marketplace domain | ebay.com |
| page | integer | No | Page number for pagination | 1 |
| pageSize | integer | No | Results per page: 25, 50, 100, or 200 | 50 |
| orderBy | string | No | Sort order (see Sort Options below) | 12 (Best Match) |
| priceMin | number | No | Minimum price filter | - |
| priceMax | number | No | Maximum price filter | - |
| itemCondition | string | No | Item condition code(s), pipe-separated (e.g., `1000\|3000`) | - |
| buyingFormat | string | No | Buying format: Auction, BIN, or BO | - |
| showOnly | string | No | Display filters, comma-separated (e.g., `Sold,Complete`) | - |
| location | integer | No | Seller location country code | - |
| prefLoc | string | No | Preferred location scope: 1=Domestic, 2=Regional, 3=Worldwide | - |
| zipCode | string | No | ZIP/postal code for regional delivery filtering | - |
| categoryId | integer | No | eBay category ID | - |
| noCache | boolean | No | Bypass cache for fresh results | false |

### Sort Options

| Code | Meaning |
|------|---------|
| 12 | Best Match (default) |
| 1 | Time: ending soonest |
| 10 | Time: newly listed |
| 15 | Price + Shipping: lowest first |
| 16 | Price + Shipping: highest first |
| 2 | Price: lowest first |
| 3 | Price: highest first |
| 7 | Distance: nearest first |
| 18 | Condition: new first |
| 19 | Condition: used first |

### Item Condition Codes

| Code | Condition |
|------|-----------|
| 1000 | New |
| 1500 | New other (see details) |
| 1750 | New with defects |
| 2000 | Certified Refurbished |
| 2010 | Excellent - Refurbished |
| 2020 | Very Good - Refurbished |
| 2030 | Good - Refurbished |
| 2500 | Seller refurbished / Remanufactured |
| 2750 | Like New |
| 3000 | Used / Pre-owned |
| 7000 | For parts or not working |

### showOnly Filter Values

| Value | Meaning |
|-------|---------|
| Complete | Completed listings |
| Sold | Sold listings only |
| FR | Free returns |
| RPA | Returns accepted |
| AS | Authorized seller |
| Savings | Deals & savings |
| SaleItems | Sale items |
| Lots | Lots |
| FS | Free shipping |
| LPickup | Local pickup |

### Supported eBay Domains

| Domain | Country |
|--------|---------|
| ebay.com | United States (default) |
| ebay.co.uk | United Kingdom |
| ebay.de | Germany |
| ebay.fr | France |
| ebay.it | Italy |
| ebay.es | Spain |
| ebay.ca | Canada |
| ebay.com.au | Australia |
| ebay.nl | Netherlands |
| ebay.at | Austria |
| ebay.ch | Switzerland |
| ebay.pl | Poland |
| ebay.ie | Ireland |
| ebay.com.hk | Hong Kong |
| ebay.com.my | Malaysia |
| ebay.com.sg | Singapore |

## 调用方式

- **API 端点**：`POST /ebay/search`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/ebay_search.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ebay-search-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

**1. Basic Keyword Search**
Search for "wireless earbuds" on the US eBay marketplace:
```json
{"keyword": "wireless earbuds"}
```

**2. Search Sold Listings for Price Research**
Find sold listings for "iPhone 15 Pro" to gauge market value:
```json
{"keyword": "iPhone 15 Pro", "showOnly": "Sold,Complete", "orderBy": "10"}
```

**3. Search on a Specific Marketplace with Price Range**
Find new laptops priced between $500 and $1000 on eBay UK:
```json
{"keyword": "laptop", "ebayDomain": "ebay.co.uk", "priceMin": 500, "priceMax": 1000, "itemCondition": "1000"}
```

**4. Auction Items Ending Soon**
Find active auctions for "vintage watch" ending soonest:
```json
{"keyword": "vintage watch", "buyingFormat": "Auction", "orderBy": "1"}
```

**5. Find the Cheapest New Items**
Find the cheapest new "USB-C cable" with free shipping:
```json
{"keyword": "USB-C cable", "itemCondition": "1000", "orderBy": "15", "showOnly": "FS"}
```

**6. Paginated Results**
Get page 3 of results with 100 items per page for "running shoes":
```json
{"keyword": "running shoes", "page": 3, "pageSize": 100}
```

**7. Category-Specific Search**
Search within a specific eBay category:
```json
{"keyword": "mechanical keyboard", "categoryId": 33963}
```

**8. Location-Filtered Search**
Find products located in Germany on the German eBay site:
```json
{"keyword": "Kopfhoerer", "ebayDomain": "ebay.de", "location": 77}
```

## Display Rules

1. **Present data clearly**: Show search results in well-formatted tables including key fields such as title, price, condition, seller info, and shipping
2. **Price formatting**: Always display prices with their currency symbol. When showing price ranges (minPrice to maxPrice), format as a range
3. **Sold/completed data**: When showing sold items, highlight the sold price and quantity to help users with pricing research
4. **Seller trust indicators**: When available, show seller feedback percentage and review count to help users evaluate seller reliability
5. **Pagination notice**: When total results exceed the current page, inform the user of the total count and suggest pagination to see more
6. **Sponsored items**: Clearly mark sponsored listings so users can distinguish organic results from promoted ones
7. **Error handling**: When a query fails, explain the issue and suggest adjusting search parameters
8. **Link presentation**: Provide product links so users can view full details on eBay
## Important Limitations

- **No historical data**: This tool returns current live listings only, not historical pricing trends
- **Result cap**: Maximum 200 results per page
- **Rate limiting**: Excessive requests may be throttled; use `noCache: true` sparingly
- **Currency**: Prices are returned in the local currency of the eBay domain being searched

## User Expression & Scenario Quick Reference

**Applicable** -- Product search and listing data on eBay:

| User Says | Scenario |
|-----------|----------|
| "Search eBay for XX" | Basic product search |
| "How much does XX sell for on eBay" | Sold listing price research |
| "Find cheapest XX on eBay" | Price comparison / lowest price |
| "eBay auctions for XX" | Auction listing search |
| "What's selling on eBay UK/Germany" | Regional marketplace browsing |
| "New XX under $50 on eBay" | Filtered search by condition and price |
| "eBay sold prices for XX" | Completed/sold listing analysis |
| "Find refurbished XX on eBay" | Condition-specific search |

**Not applicable** -- Needs beyond eBay product listings:
- eBay seller account management or store analytics
- eBay listing creation or editing
- eBay order tracking or purchase history
- Cross-platform price comparison (eBay vs Amazon vs others)
- eBay advertising or promoted listing management

## 积分消耗规则

消耗 15 积分。

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
