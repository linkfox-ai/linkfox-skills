---
name: linkfox-youying-shopee-product-search
description: 友鹰Shopee商品选品工具，支持Shopee全站点的商品查询与筛选，覆盖马来西亚、台湾、印尼、泰国、菲律宾、新加坡、越南、巴西、墨西哥、智利、哥伦比亚等11个站点。当用户提到Shopee选品、虾皮商品搜索、Shopee爆款、虾皮市场分析、Shopee品类选品、虾皮关键词选品、Shopee销量筛选、虾皮价格筛选、东南亚电商选品、Shopee product search, Shopee product selection, Shopee bestsellers, Shopee market analysis时触发此技能。即使用户未明确提及"友鹰"或"Shopee"，只要其需求涉及在虾皮平台上搜索商品或筛选Shopee商品数据，也应触发此技能。
---

# 友鹰-Shopee 商品选品

This skill guides you on how to query and filter Shopee product data across 11 marketplaces, helping cross-border sellers discover trending products and market opportunities on Shopee.

## Core Concepts

友鹰（YouYing）Shopee 商品选品工具提供 Shopee 全站商品的结构化查询能力。卖家可通过关键词、价格区间、销量、上架时间、店铺属性等多维度条件灵活组合筛选，发现爆款货源与市场机会。

**核心数据维度**：
- **销量数据**：前30天销售件数（sold）、估算前30天销售件数（estimateSold）、商品总销售件数（historicalSold）、前30天销售额（payment）
- **价格数据**：默认价（price）、最低价（minPrice）、最高价（maxPrice）
- **店铺数据**：店铺名称、是否官方店铺、虾皮优选、本地/海外、跨境/本土
- **商品属性**：评分、评分数、收藏数、浏览数、SKU 数量、上架时间、类目结构

## Data Fields

### Product Fields (Output)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| 商品ID | pid | 商品唯一标识 | 12345678 |
| 商品标题 | title | 商品名称 | Storage Box Organizer |
| 商品描述 | description | 商品详细描述 | ... |
| 商品主图 | imageUrl | 商品主图URL | https://... |
| 商品链接 | productUrl | Shopee商品页面链接 | https://... |
| 默认价 | price | 商品默认价格（当地货币） | 29.90 |
| 最低价 | minPrice | SKU最低价 | 19.90 |
| 最高价 | maxPrice | SKU最高价 | 39.90 |
| 前30天销售件数 | sold | 近30天实际销量 | 1500 |
| 估算前30天销量 | estimateSold | 估算的近30天销量 | 1200 |
| 总销售件数 | historicalSold | 商品累计总销量 | 50000 |
| 前30天销售额 | payment | 近30天销售金额（当地货币） | 45000 |
| 商品评分 | rating | 0-5分 | 4.8 |
| 评分数 | ratings | 收到的评分总数 | 320 |
| 收藏数 | favorite | 被收藏次数 | 2800 |
| 浏览数 | viewCount | 浏览次数 | 15000 |
| 库存 | stock | 当前库存数量 | 500 |
| SKU数量 | skuNumber | SKU变体数量 | 8 |
| 上架时间 | genTime | 商品首次上架日期 | 2025-06-01 |
| 类目结构 | categoryStructure | 所属类目层级路径 | Home & Living > Storage |
| 店铺名称 | shopName | 所属店铺名称 | BestHome Official |
| 店铺链接 | shopUrl | 店铺页面链接 | https://... |
| 是否官方店铺 | isOfficialShop | 1=是, 0=否 | 1 |
| 虾皮优选 | isShopeeVerified | 1=优选, 0=非优选 | 1 |
| 发货类型 | cbOption | 1=跨境, 0=本土 | 0 |
| 店铺所在地类型 | shippingIconType | 0=本地, 1=海外 | 0 |
| 商品状态 | status | 1=正常, 0=下架 | 1 |

## Supported Marketplaces

| 站点 | station 值 | 代码 |
|------|-----------|------|
| 马来西亚 | malaysia | MY |
| 台湾 | taiwan_china | Taiwan_CHN |
| 印度尼西亚 | indonesia | ID |
| 泰国 | thailand | TH |
| 菲律宾 | philippines | PH |
| 新加坡 | singapore | SG |
| 越南 | vietnam | VN |
| 巴西 | brazil | BR |
| 墨西哥 | mexico | MX |
| 智利 | chile | CL |
| 哥伦比亚 | columbia | CO |

`station` 为**必填**参数，可传站点名（如 `malaysia`）或代码（如 `MY`）。当用户未指定站点时，需要**询问用户**想查询哪个站点。

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/youying_shopee_search.py` directly to run queries.

## How to Build Queries

根据用户需求，将自然语言转换为 API 参数组合。核心原则是**精确映射用户的筛选条件到对应参数**。

### Principles for Building API Calls

1. **必填站点**：每次调用必须指定 `station`。用户说"马来""马来西亚"→ `malaysia`；"台湾"→ `taiwan_china`；"印尼"→ `indonesia` 等
2. **关键词搜索**：`keyword` 为标题关键词，搭配 `keywordType` 控制匹配模式（1=整句匹配，2=多词AND，3=多词OR）
3. **数值范围**：大多数筛选条件使用 Start/End 或 Min/Max 成对参数，按需设置单侧或双侧
4. **排序**：`orderBy` 指定排序字段，`orderByType` 指定升/降序（默认 DESC 降序）
5. **分页**：`page` 从 1 开始，`pageSize` 范围 1-1000，默认 1000
6. **排除逻辑**：`notExistKeyword` 可排除包含特定词的商品，`notExistShopIdList` 可排除特定店铺

### Common Query Scenarios

**1. 关键词选品 — 按销量筛选热销商品**
```
station: malaysia
keyword: Storage Box
keywordType: 2
soldMin: 100
orderBy: sold
orderByType: DESC
pageSize: 100
```

**2. 新品发现 — 近期上架且有一定销量的商品**
```
station: thailand
keyword: Phone Case
listingDateFrom: 2025-06-01
soldMin: 50
orderBy: gen_time
orderByType: DESC
```

**3. 高潜力商品 — 低价高销量**
```
station: indonesia
keyword: LED Light
priceMax: 50000
soldMin: 500
orderBy: payment
orderByType: DESC
```

**4. 跨境卖家商品筛选**
```
station: malaysia
keyword: Wireless Earbuds
cbOption: 1
soldMin: 200
orderBy: sold
orderByType: DESC
```

**5. 品类选品 — 按类目 + 销售额筛选**
```
station: vietnam
pL1Id: 11036379
paymentStart: 10000000
orderBy: payment
orderByType: DESC
pageSize: 200
```

**6. 竞品店铺分析 — 查看特定店铺的商品**
```
station: malaysia
shopIdList: 123456789
orderBy: sold
orderByType: DESC
```

**7. 优选商品筛选 — 虾皮优选 + 高评分**
```
station: philippines
keyword: Beauty
isShopeeVerified: 1
ratingMin: 4.5
soldMin: 100
orderBy: rating
orderByType: DESC
```

**8. 大卖排除 — 发现中小卖家机会**
```
station: taiwan_china
keyword: 收纳盒
notExistShopIdList: 111111,222222,333333
soldMin: 50
soldMax: 500
orderBy: sold
orderByType: DESC
```

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Currency notice**: Different marketplaces use different currencies (MYR, TWD, IDR, THB, PHP, SGD, VND, BRL, MXN, CLP, COP). Always remind users of the currency context when showing price/payment data
3. **Volume notice**: When results are large, show core data (title, price, sold, payment, rating) and remind users they can view more via pagination
4. **Key metrics highlight**: Prioritize showing `sold` (前30天销量), `payment` (前30天销售额), `price`, `rating` as these are the most decision-relevant metrics
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting query criteria
6. **Image display**: When `imageUrl` is available, include product images to help users make visual assessments

## Important Limitations

- **Result cap**: `pageSize` maximum is 1000 records per request
- **Required field**: `station` is always required — if missing, ask the user which marketplace to query
- **Price currency**: Prices are in local currency of the selected marketplace, not USD
- **Data freshness**: Data depends on 友鹰's crawling schedule, see `lastModiTime` for last update time

## User Expression & Scenario Quick Reference

**Applicable** - Shopee product search and filtering:

| User Says | Scenario |
|-----------|----------|
| "虾皮上什么好卖" "Shopee爆款" | Hot-selling product discovery |
| "帮我在Shopee上搜xx商品" | Keyword product search |
| "马来站最近上架的新品" | New product discovery by listing date |
| "销量过千的商品有哪些" | Volume-based product filtering |
| "东南亚哪些品类有机会" | Category-level opportunity scan |
| "帮我看看这个店铺的商品" | Competitor shop analysis |
| "跨境商品和本土商品对比" | Cross-border vs local comparison |
| "Shopee优选商品筛选" | Shopee Verified product filtering |
| "低价高销量的商品" | Price-volume opportunity mining |

**Not applicable** - Needs beyond Shopee product search:
- Amazon, TikTok, eBay, 1688 等其他平台的商品搜索
- Shopee 广告投放策略
- Shopee 店铺运营建议
- Shopee 物流/仓储方案
- 已有本地 Shopee 数据文件的处理

**Boundary judgment**: When users say "东南亚选品", "虾皮市场分析", or "跨境电商选品", if it boils down to searching and filtering products on Shopee by various criteria, this skill applies. If they're asking about logistics planning, advertising strategy, or store operations, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
