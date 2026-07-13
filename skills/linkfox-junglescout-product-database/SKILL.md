---
name: linkfox-junglescout-product-database
description: Jungle Scout产品数据库多条件筛选，支持按品类、价格、销量、收入、评论、评分、重量、BSR排名、LQS、卖家类型等维度筛选亚马逊商品，覆盖10个站点。当用户提到亚马逊选品、产品数据库筛选、BSR排名筛选、品类选品、高评分低竞争选品、FBA选品、亚马逊商品搜索、产品筛选、Amazon product database, product research, product filtering, BSR rank filter, category product search, niche product finder, FBA product search, Amazon product discovery, low competition products, Jungle Scout product database时触发此技能。即使用户未明确提及"Jungle Scout"或"产品数据库"，只要其需求涉及按多条件筛选亚马逊商品或发现潜力产品，也应触发此技能。
---

# Jungle Scout — 产品数据库查询

This skill queries the Jungle Scout Product Database via the LinkFox tool gateway, enabling multi-condition filtering of Amazon products across 10 marketplaces. Sellers can discover products by category, price range, sales volume, revenue, reviews, rating, BSR rank, Listing Quality Score (LQS), seller type, and more.

## Core Concepts

Jungle Scout 产品数据库是亚马逊商品级别的多维筛选工具，帮助卖家从海量商品中快速锁定目标产品：

- **品类选品**：按亚马逊主分类筛选特定品类下的商品
- **销量/收入筛选**：通过月销量和月收入范围圈定市场规模合适的产品
- **竞争度评估**：通过评论数、评分、卖家数量判断竞争激烈程度
- **Listing 质量评估**：LQS（Listing Quality Score，1-10分）帮助发现优化空间大的产品
- **产品类型过滤**：区分 FBA/FBM/AMZ 卖家类型、标准尺寸/超大尺寸
- **新品发现**：通过上架日期筛选近期上架的新品

**Internal paging**: The API handles pagination automatically; you specify `needCount` to control how many results you want, and the backend fetches them across pages internally.

## Data Fields

### Key Output Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| 商品标题 | title | 产品标题 | Yoga Mat Non Slip... |
| 品牌 | brand | 品牌名称 | Liforme |
| 主分类 | category | 亚马逊主分类 | Sports & Outdoors |
| 分类路径 | breadcrumbPath | 完整分类层级 | Sports & Outdoors > Exercise & Fitness |
| 价格 | price | 当前售价 (USD) | 29.99 |
| 月销量 | approximate30DayUnitsSold | 近30天预估销量 | 1200 |
| 月收入 | approximate30DayRevenue | 近30天预估收入 (USD) | 35988.00 |
| BSR排名 | productRank | Best Sellers Rank | 3456 |
| 评论数 | reviews | 累计评论数 | 850 |
| 评分 | rating | 平均评分 (1.0-5.0) | 4.5 |
| LQS | listingQualityScore | Listing质量评分 (1-10) | 8 |
| 卖家数量 | numberOfSellers | 在售卖家数 | 3 |
| 卖家类型 | sellerType | 卖家类型 (amz/fba/fbm) | fba |
| 首次上架日期 | dateFirstAvailable | 产品首次上架日期 | 2024-06-15 |
| 重量 | weightValue / weightUnit | 产品重量 | 2.5 lbs |
| 尺寸 | lengthValue / widthValue / heightValue / dimensionsUnit | 产品尺寸 | 24×8×8 inches |
| 父ASIN | parentAsin | 父体ASIN | B0XXXXXXXX |
| Buy Box持有者 | buyBoxOwner | Buy Box 当前持有卖家 | BrandName |
| 费用明细 | feeBreakdown | FBA费用、推荐费、总费用等 | {fbaFee: 5.40, ...} |
| 子分类排名 | subcategoryRanks | 子分类BSR排名列表 | [{subcategory: "Yoga Mats", rank: 12}] |
| 消耗Token | costToken | 本次调用消耗的 token 数 | 5 |

## Supported Marketplaces

us (United States), uk (United Kingdom), de (Germany), in (India), ca (Canada), fr (France), it (Italy), es (Spain), mx (Mexico), jp (Japan)

Default marketplace is **us**. Use us when the user doesn't specify a marketplace.

## 调用方式

- **API 端点**：`POST /tool-jungle-scout/product-database/query`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/junglescout_product_database.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-junglescout-product-database-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

Only `marketplace` is **required**. All other parameters are optional filters — combine them to narrow results.

### Principles for Building API Calls

1. **站点映射**：用户说"美国站"→ `us`，"日本站"→ `jp`，"德国站"→ `de`；未指定时默认 `us`
2. **关键词**：`includeKeywords` 支持逗号分隔多个词（标题或ASIN），如 `yoga mat,fitness`；`excludeKeywords` 排除含特定词的商品
3. **品类匹配**：`categories` 必须使用对应站点的英文标准分类名，如美国站 `Sports & Outdoors`、`Home & Kitchen` 等；多个品类逗号分隔
4. **数值范围**：min/max 成对使用，可只传一端；如只设 `minSales=300` 表示月销量≥300
5. **排序**：`sort` 字段名前加 `-` 表示降序，如 `-sales` 按销量从高到低；默认按 `name` 升序
6. **结果数量**：`needCount` 控制返回结果总数，不设则返回默认数量

### Common Query Scenarios

**1. 关键词搜索 + 按销量筛选**
```json
{
  "marketplace": "us",
  "includeKeywords": "yoga mat",
  "minSales": 300,
  "maxSales": 5000,
  "sort": "-sales",
  "needCount": 50
}
```

**2. 品类 + 价格区间筛选**
```json
{
  "marketplace": "us",
  "categories": "Home & Kitchen",
  "minPrice": 15,
  "maxPrice": 50,
  "minSales": 100,
  "sort": "-revenue",
  "needCount": 50
}
```

**3. 高评分低竞争选品（评论少但评分高）**
```json
{
  "marketplace": "us",
  "categories": "Beauty & Personal Care",
  "minRating": 4.0,
  "maxReviews": 200,
  "minSales": 100,
  "sort": "-sales",
  "needCount": 50
}
```

**4. 仅 FBA 产品筛选**
```json
{
  "marketplace": "us",
  "includeKeywords": "phone stand",
  "sellerTypes": "fba",
  "productTiers": "standard",
  "minSales": 200,
  "sort": "-sales",
  "needCount": 50
}
```

**5. 排除头部品牌 + 发现蓝海机会**
```json
{
  "marketplace": "us",
  "categories": "Sports & Outdoors",
  "excludeTopBrands": true,
  "minSales": 300,
  "maxReviews": 500,
  "minRating": 4.0,
  "sort": "-sales",
  "needCount": 50
}
```

**6. 按上架日期发现新品**
```json
{
  "marketplace": "us",
  "categories": "Electronics",
  "minUpdatedAt": "2026-01-01",
  "minSales": 50,
  "sort": "-sales",
  "needCount": 50
}
```

## Display Rules

1. **Table format**: Present results in a structured table with key columns: title, brand, price, monthly sales, monthly revenue, BSR rank, reviews, rating, LQS
2. **Sorting note**: Remind the user what sorting was applied and how many results were returned
3. **Highlight insights**: Mark products with notably low reviews but high sales (potential opportunity), or high LQS scores
4. **Fee breakdown**: When users ask about profitability, include feeBreakdown details (FBA fee, referral fee, total fees)
5. **Image links**: Include `imageUrl` when displaying individual product details
6. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters

## Important Limitations

- **marketplace 必填**：每次查询必须指定站点
- **品类名需匹配**：`categories` 值必须与对应站点的标准主分类名完全一致
- **关键词限制**：`includeKeywords` / `excludeKeywords` 最多各100项，每项最长50字符
- **数据时效**：数据来源于 Jungle Scout 定期更新，非实时数据
- **评分范围**：`minRating` / `maxRating` 取值 1.0-5.0
- **重量单位**：`minWeight` / `maxWeight` 以磅（pounds）为单位

## User Expression & Scenario Quick Reference

**Applicable** - Amazon product multi-condition filtering and discovery:

| User Says | Scenario |
|-----------|----------|
| "帮我找月销量500以上的瑜伽垫" | 关键词 + 销量筛选 |
| "美国站厨房品类30美金以下有什么好产品" | 品类 + 价格筛选 |
| "评论少但评分高的蓝海产品" | 高评分低竞争选品 |
| "找FBA标准尺寸的手机支架" | 卖家类型 + 产品尺寸筛选 |
| "排除大品牌的运动品类机会" | 排除头部品牌 |
| "最近新上架的电子产品有哪些卖得好" | 新品发现 |
| "BSR排名1万以内的家居产品" | BSR排名筛选 |
| "LQS低于5分的高销量产品" | Listing优化机会 |

**Not applicable** - Beyond product database filtering:
- 关键词搜索量/趋势分析（需要关键词历史搜索量工具）
- ABA搜索词排名（需要ABA工具）
- 商品详情页/Listing内容分析
- 广告/PPC投放策略
- 非亚马逊平台商品数据

**Boundary judgment**: When users say "选品", "找产品", or "市场调研", if their need is to filter products by specific criteria (price, sales, category, reviews, etc.) from Amazon's product catalog, this skill applies. If they need keyword-level search volume data, advertising insights, or non-Amazon platform data, it does not apply.

## 积分消耗规则

按动态规则计费：消耗积分 = 实际查询页数 × 63.75。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
