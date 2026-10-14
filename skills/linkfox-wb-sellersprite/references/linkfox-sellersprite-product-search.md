---
name: linkfox-sellersprite-product-search
description: 利用卖家精灵多维度筛选亚马逊商品，支持销量、排名、毛利等条件，助力精准选品。
---

# 卖家精灵-商品搜索（SellerSprite Product Search）

本业务能力通过卖家精灵商品数据库搜索、筛选和分析亚马逊商品数据，帮助亚马逊卖家做出数据驱动的选品决策；完整参数与响应字段见本文后部的 API 参考章节。

## 能力边界

### ✅ 能力范围

- 基于卖家精灵商品数据库，按价格、月销量、月销售额、BSR 排名、毛利率、评分、评分数、配送方式、标签（Best Seller / Amazon's Choice / New Release）、卖家国籍、品牌、上架时间等多维条件筛选亚马逊商品。
- 支持近 30 天实时数据（`dataSnapshotMonth: "nearly"`）与历史月度快照（`yyyyMM`），可做同期对比与季节性分析。
- 覆盖站点：US、UK、DE、FR、JP、CA、IT、ES、MX、IN（仅限该枚举集合）。

### ❌ 边界与限制

- **单页上限**：`size` 最大 100 条。
- **历史快照**：仅支持已存在的历史月度快照，不支持未来日期。
- **重量单位**：使用任意重量筛选时必须同时传 `weightUnit`。
- **子类目 BSR**：子类目 BSR 排名筛选仅在 `filterSubNode` 为 `true` 时生效。
- **上架时间枚举**：`listedWithinLastMonths` 仅允许 `1`、`3`、`6`、`12`、`24`。
- **子体近 30 日销量**：`minAmzUnit` / `maxAmzUnit` 仅在近 30 日类查询（通常 `dataSnapshotMonth: "nearly"`）时支持，历史 `yyyyMM` 快照不可用。
- **不在范围内**：ABA 搜索词/关键词分析（用 ABA 工具）；广告/PPC 数据；评论文本分析；Listing 文案撰写与优化；供应商采购与制造成本；物流与库存规划。

## 核心概念

卖家精灵商品搜索提供丰富的亚马逊商品筛选维度，支持近 30 天实时数据与月度历史快照，可做同期对比与季节性分析。

**BSR（Best Sellers Rank）**：BSR 数值越小代表在所属类目销量越好，BSR 为 1 即该类目销量第一。用户说「BSR 上升」指数值减小（排名变好），「BSR 下降」指数值增大。

**数据快照**：`dataSnapshotMonth` 控制查询时段。`nearly`（默认）取近 30 天实时数据；传 `yyyyMM`（如 `202412`）查历史月度快照，适合季节性分析与同比对比。

**关键词匹配方式**：
- **词组匹配**（默认，`matchType=1`）：商品标题须包含该关键词词组。
- **模糊匹配**（`matchType=2`）：更宽泛的相关词匹配。
- **精准匹配**（`matchType=3`）：严格整串匹配。

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/productSearch`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/productSearch",
  "arguments": {
    "marketplace": "US",
    "keyword": "desk organizer",
    "page": 1,
    "size": 20
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 使用示例

**1. 某细分品类的高销量商品**
> "在美国站找月销量超过 500 的瑜伽垫，按月销量降序"
```json
{
  "keyword": "yoga mat",
  "marketplace": "US",
  "minUnits": 500,
  "order": {"field": "total_units", "desc": "true"}
}
```

**2. 低竞争新品机会发现**
> "找美国站近 6 个月上架、评分数少于 50、月销售额超 $5,000 的桌面收纳商品"
```json
{
  "keyword": "desk organizer",
  "marketplace": "US",
  "listedWithinLastMonths": 6,
  "maxRatings": 50,
  "minRevenue": 5000,
  "order": {"field": "total_units", "desc": "true"}
}
```

**3. 产品改良机会挖掘**
> "找评分 3.8-4.3（改良甜点区）、月销量超 300 的手机壳"
```json
{
  "keyword": "phone case",
  "marketplace": "US",
  "minRating": 3.8,
  "maxRating": 4.3,
  "minUnits": 300,
  "order": {"field": "total_units", "desc": "true"}
}
```

**4. 高毛利商品筛选**
> "找毛利率 40% 以上、价格 $15-$50、月销量不少于 100 的商品"
```json
{
  "marketplace": "US",
  "minProfit": 40,
  "minPrice": 15,
  "maxPrice": 50,
  "minUnits": 100,
  "order": {"field": "profit", "desc": "true"}
}
```

**5. 季节性同比对比**
> "查去年 12 月圣诞灯快照数据，与当前对比做季节性规划"
```json
{
  "keyword": "christmas lights",
  "marketplace": "US",
  "dataSnapshotMonth": "202412",
  "minUnits": 200,
  "order": {"field": "total_units", "desc": "true"}
}
```

**6. 中国卖家竞争格局**
> "找某类目下中国卖家的高销量 FBA 商品"
```json
{
  "keyword": "bluetooth speaker",
  "marketplace": "US",
  "sellerNation": "CN",
  "fulfillment": "FBA",
  "minUnits": 200,
  "order": {"field": "total_units", "desc": "true"}
}
```

**7. Best Seller 徽章商品**
> "找带 Best Seller 徽章、销量表现好的水杯商品"
```json
{
  "keyword": "water bottle",
  "marketplace": "US",
  "badgeBestSeller": "Y",
  "order": {"field": "total_units", "desc": "true"}
}
```

**8. 按销量增长率找高增长商品**
> "找月销量增长率超 50% 的升降桌"
```json
{
  "keyword": "standing desk",
  "marketplace": "US",
  "minUnitsGrowthRate": 50,
  "order": {"field": "total_units_growth", "desc": "true"}
}
```

## 展示规则

1. **清晰呈现数据**：以结构化表格展示，优先列：ASIN、标题、价格、月销量、月销售额、BSR 排名、评分、评分数、毛利率、配送方式。
2. **BSR 说明**：展示 BSR 时提示用户数值越小排名越好。
3. **毛利率说明**：毛利率为百分比，提示这是基于价格减去 FBA 费用与预估成本的估算值。
4. **分页提示**：总数超出当前页时，告知总数并建议调整 `page`/`size` 查看更多。
5. **快照标注**：展示历史快照数据时明确标注数据时段（如「数据来自 2024 年 12 月快照」），避免与实时数据混淆。
6. **错误处理**：查询失败时依据 `message` 字段说明原因并建议调整查询条件。
7. **重量单位确认**：用户使用重量筛选未指定单位时，先确认单位（g、kg、oz、lb）再查询。
8. **关键词翻译**：用户提供的关键词语言与目标站点不一致时，翻译为对应语言并告知译文。

## 用户表达与场景速查

**适用** —— 亚马逊商品级数据查询：

| 用户说 | 场景 |
|--------|------|
| "找 XX 类目高销量的商品" | 细分品类商品搜索 |
| "低竞争商品"、"新品机会" | 蓝海选品发现 |
| "哪些商品毛利高" | 盈利能力筛选 |
| "销量增长的商品"、"趋势商品" | 增长趋势探测 |
| "中国卖家卖得好的商品" | 竞争格局分析 |
| "最近上架表现好的商品" | 新品跟踪 |
| "差评多但销量好的商品" | 产品改良机会 |
| "和去年同期对比这个类目" | 季节性/同比分析 |
| "$30 以下、销量 1000+ 的 FBA 商品" | 多条件商品筛选 |
| "XX 类目的 Best Seller" | 徽章商品发现 |

不适用场景见上方【能力边界】。

## 解决认证和积分问题

MCP/`proxy_call` 缺失、MCP 401、下游 401、下游 402 与 403 按 `onboarding.md` 分层处理。WorkBuddy 自动注入 Authorization；不得索要手工凭证或把凭证放入 `arguments`。

## MCP 调用规范

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/productSearch`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/productSearch",
  "arguments": {
    "marketplace": "US",
    "keyword": "desk organizer",
    "page": 1,
    "size": 20
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「卖家精灵-选产品」入参 schema 一致（同步日期 2026-04-30）。

### 会话 / 网关（可选）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chatId | string | 否 | 对话 id，`maxLength` 1000 |
| uid | string | 否 | 用户 id，`maxLength` 1000 |
| requestId | string | 否 | 推送 id，`maxLength` 1000 |
| teamId | string | 否 | 团队 id，`maxLength` 1000 |

### 搜索与关键词

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词；请尽量翻译为对应国家的语言，比如美国用英语关键词，德国用德语关键词等；`maxLength` 10240 |
| matchType | integer | 否 | 匹配方式：1=词组匹配（默认），2=模糊匹配，3=精准匹配 |
| excludeKeywords | string | 否 | 排除关键词；`maxLength` 10240 |
| marketplace | string | 否 | 市场站点代码，默认 `US`。**仅允许** `US`、`UK`、`DE`、`FR`、`JP`、`CA`、`IT`、`ES`、`MX`、`IN`（须符合该枚举，不含 AU、TR 等未列出站点） |

### 类目筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nodeLabel | string | 否 | 亚马逊类目名称；`maxLength` 1000 |
| nodeIdPath | string | 否 | 亚马逊类目节点 ID；`maxLength` 1000 |
| filterSubNode | boolean | 否 | 是否筛选子类目节点；仅在 nodeLabel 或 nodeIdPath 有值时生效；传 JSON 布尔值 `true` / `false` |

### 数据快照

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dataSnapshotMonth | string | 否 | 商品数据快照年月，格式 `yyyyMM`（如 `202412` 表示2024年12月的数据快照），或 `nearly` 表示最近30天实时数据。默认值：`nearly`。用于历史分析和同期对比，仅支持已存在的历史快照，不支持未来日期；`maxLength` 1000 |

### 价格与利润

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minPrice | number | 否 | 最低价格（>= 0） |
| maxPrice | number | 否 | 最高价格（>= 0） |
| minProfit | number | 否 | 最小毛利率，单位 %（1-100） |
| maxProfit | number | 否 | 最大毛利率，单位 %（1-100） |
| minRevenue | number | 否 | 最低月销售额（>= 0） |
| maxRevenue | number | 否 | 最高月销售额（>= 0） |
| minFba | number | 否 | 最低FBA运费（>= 0） |
| maxFba | number | 否 | 最高FBA运费（>= 0） |

### 销量与BSR

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minUnits | integer | 否 | 最低月销量（>= 0） |
| maxUnits | integer | 否 | 最高月销量（>= 0） |
| minAmzUnit | integer | 否 | 最低子体近 30 日销量（**仅** `dataSnapshotMonth` 为「近 30 日」类查询时支持）；`minimum` 0 |
| maxAmzUnit | integer | 否 | 最高子体近 30 日销量（**仅**近 30 日查询支持）；`minimum` 0 |
| minUnitsGrowthRate | number | 否 | 月销量最低增长率，单位 % |
| maxUnitsGrowthRate | number | 否 | 月销量最高增长率，单位 % |
| minBsr | integer | 否 | 大类BSR最低排名 |
| maxBsr | integer | 否 | 大类BSR最高排名 |
| minBsrGrowthRate | number | 否 | BSR最低增长率，单位 % |
| maxBsrGrowthRate | number | 否 | BSR最高增长率，单位 % |
| minBsrGrowthCount | integer | 否 | BSR最低增长数 |
| maxBsrGrowthCount | integer | 否 | 大类BSR最高增长数 |
| minSubNodeBsrRank | integer | 否 | 子类目BSR最低排名（需 filterSubNode = true） |
| maxSubNodeBsrRank | integer | 否 | 子类目BSR最大排名（需 filterSubNode = true） |

### 评分与评论

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minRating | number | 否 | 最低评分值（0-5） |
| maxRating | number | 否 | 最高评分值（0-5），3.8-4.3为产品改良机会区间 |
| minRatings | integer | 否 | 最低评分数（0-10000） |
| maxRatings | integer | 否 | 最高评分数（0-10000） |
| minRatingsGrowthCount | integer | 否 | 最低月新增评分数（>= 0） |
| maxRatingsGrowthCount | integer | 否 | 最高月新增评分数（>= 0） |
| minListingQualityScore | number | 否 | 最低 Listing 页面质量分（>= 0） |
| maxListingQualityScore | number | 否 | 最高 Listing 页面质量分（>= 0） |

### 商品属性

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minVariations | integer | 否 | 最低变体数 |
| maxVariations | integer | 否 | 最高变体数 |
| minWeights | number | 否 | 最小重量（>= 0） |
| maxWeights | number | 否 | 最大重量（>= 0） |
| weightUnit | string | 否 | 重量单位：g、kg、oz、lb。如果参数中包含重量筛选，则必须指定此字段 |
| dimensionType | string | 否 | 包装尺寸类型（各站点代码不同，见下方说明） |
| minSellers | integer | 否 | 最小卖家数量 |
| maxSellers | integer | 否 | 最大卖家数量 |

### 标识与配送

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| badgeBestSeller | string | 否 | Best Seller 标识筛选：`Y`、`N` 或留空（全部） |
| badgeAmazonsChoice | string | 否 | Amazon's Choice 标识筛选：`Y`、`N` 或留空（全部） |
| badgeNewRelease | string | 否 | New Release 标识筛选：`Y`、`N` 或留空（全部） |
| fulfillment | string | 否 | 配送方式：单选 `AMZ` / `FBA` / `FBM`，或多选如 `AMZ,FBA`、`FBA,FBM`、`AMZ,FBA,FBM` 等；多条件用英文逗号；留空表示不限制 |
| showVariation | string | 否 | 是否查询变体：`Y` 或 `N`，默认 `N` |
| hideUnlistedProduct | boolean | 否 | 是否隐藏已下架商品，默认 `true` |
| listedWithinLastMonths | integer | 否 | 上架时间范围（月），**仅**允许：`1`、`3`、`6`、`12`、`24`（与枚举含义一致，勿传其他整数） |

### 卖家与品牌

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerNation | string | 否 | 卖家所属地代码（如 US、CN、HK），多条件用逗号隔开，默认不限制 |
| includeSellers | string | 否 | 包含卖家；`maxLength` 10240 |
| excludeSellers | string | 否 | 排除卖家；`maxLength` 10240 |
| includeBrands | string | 否 | 包含品牌；`maxLength` 10240 |
| excludeBrands | string | 否 | 排除品牌；`maxLength` 10240 |

### 排序与分页

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| order | object | 否 | 排序配置；若传入，建议同时提供 `field` 与 `desc`（子 schema 中二者为 required） |
| order.field | string | 否 | 排序字段：`total_units`（月销量）、`total_amount`（月销售额）、`bsr_rank`、`price`、`rating`、`reviews`、`profit`、`reviews_rate`、`available_date`、`questions`、`total_units_growth`、`total_amount_growth`、`reviews_increasement`、`bsr_rank_cv`、`bsr_rank_cr`、`amz_unit`（子体销量）。默认 `total_units`。传空字符串 `""` 表示不按上述业务字段排序（查询全部排序语义由服务端处理） |
| order.desc | string | 否 | `"true"` 降序，`"false"` 升序；默认 `"true"`；`maxLength` 1000 |
| page | integer | 否 | 页码，从1开始，默认 1 |
| size | integer | 否 | 每页条数（10-100），默认 20 |

## 响应结构

### 顶层字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 匹配商品总数 |
| products | array | 商品列表（详见下方商品对象字段） |
| columns | array | 渲染的列定义 |
| keyword | string | 搜索使用的关键词（如有） |
| nodeIdPath | string | 搜索的类目节点 |
| nodeLabel | string | 亚马逊类目名称 |
| dataSnapshotMonth | string | 数据查询月份 |
| sourceType | string | 来源类型（如 "amazon"） |
| type | string | 渲染样式 |
| message | string | 附加消息或错误信息 |
| costToken | integer | 消耗token |

### `products[]` 元素

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[] | object | 产品数组元素（来源对象字段表） |
| products[].asin | string | 亚马逊ASIN |
| products[].title | string | 商品标题 |
| products[].asinUrl | string | 亚马逊商品详情页URL |
| products[].imageUrl | string | 商品图片URL |
| products[].price | number | 当前价格 |
| products[].averagePrice | number | 平均价格 |
| products[].primePrice | number | Prime价格，-1表示没有 |
| products[].currency | string | 币种 |
| products[].monthlySalesUnits | integer | 月销量 |
| products[].monthlySalesRevenue | number | 月销售额 |
| products[].monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| products[].bsr | integer | BSR排名 |
| products[].bsrGrowthRate | number | BSR增长率 |
| products[].rating | number | 评分 |
| products[].ratings | integer | 评分数 |
| products[].ratingsRate | number | 留评率 |
| products[].profit | number | 毛利率（%） |
| products[].fba | number | FBA运费 |
| products[].sellerNum | integer | 卖家数 |
| products[].sellerId | string | BuyBox卖家ID |
| products[].sellerName | string | BuyBox卖家名称 |
| products[].sellerNation | string | BuyBox卖家国籍 |
| products[].brand | string | 品牌 |
| products[].brandUrl | string | 品牌页URL |
| products[].fulfillment | string | 配送方式（AMZ / FBA / FBM） |
| products[].availableDate | string | 上架时间（时间戳） |
| products[].availableDateString | string | 上架日期（格式化字符串） |
| products[].variationNum | integer | 变体数 |
| products[].variant30DayUnits | integer | 子体月销量（件数） |
| products[].variant30DayRevenue | number | 子体月销售额（金额） |
| products[].variant30DayUpdatedAt | string | 子体数据更新时间 |
| products[].weight | string | 重量 |
| products[].packageWeight | string | 包装重量 |
| products[].dimension | string | 尺寸 |
| products[].packageDimensions | string | 包装尺寸 |
| products[].dimensionsType | string | 尺寸类型 |
| products[].packageDimensionType | string | 包装尺寸类型 |
| products[].listingQualityScore | number | Listing质量得分 |
| products[].deliveryPrice | number | 卖家运费，-1表示没有 |
| products[].nodeLabelPath | string | 类目路径 |
| products[].nodeIdPath | string | 节点ID路径 |
| products[].nodeId | integer | 节点ID |
| products[].dataSnapshotMonth | string | 数据查询月份 |
| products[].badgeBestSeller | string | Best Seller标识（Y/N） |
| products[].badgeAmazonChoice | string | Amazon's Choice标识（Y/N） |
| products[].badgeNewRelease | string | New Release标识（Y/N） |
| products[].badgeVideo | string | 视频介绍（Y/N） |
| products[].badgeEbc | string | A+页面（Y/N） |
| products[].badge | object | 标识汇总对象，包含：bestSeller、amazonChoice、newRelease、video、ebc |
| products[].subcategories | array | 子类目列表，每项包含 code（类目code）、rank（排名）、label（名称） |
| products[].sku | string | SKU |
| products[].keyword | string | 对应筛选的关键词 |
| products[].sourceType | string | 来源类型 |
| products[].sourceTool | string | 来源工具标识 |

### 来源明确列出的嵌套字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].badge.bestSeller | 来源未说明 | Best Seller 标识（Y/N） |
| products[].badge.amazonChoice | 来源未说明 | Amazon's Choice 标识（Y/N） |
| products[].badge.newRelease | 来源未说明 | New Release 标识（Y/N） |
| products[].badge.ebc | 来源未说明 | A+ 页面标识（Y/N） |
| products[].badge.video | 来源未说明 | 视频介绍标识（Y/N） |
| products[].subcategories[] | object | 单个子类目排名 |
| products[].subcategories[].code | 来源未说明 | 类目 code |
| products[].subcategories[].rank | 来源未说明 | 排名 |
| products[].subcategories[].label | 来源未说明 | 名称 |

## 各站点包装尺寸类型代码

### 美国站（US）

| 代码 | 说明 |
|------|------|
| SS | 小号标准尺寸 |
| LS | 大号标准尺寸 |
| SO | 小号大件 |
| MO | 中号大件 |
| LO / LB | 大号大件 |
| SP | 特殊大件 |
| O | 其他尺寸 |
| ELO | 超大尺寸：0至50磅 |
| EL5O | 超大尺寸：50到70磅（不含50磅） |
| EL7O | 超大尺寸：70至150磅（不含70磅） |
| EL15O | 超大尺寸：150磅以上（不含150磅） |

### 日本站（JP）

| 代码 | 说明 |
|------|------|
| SM | 小号 |
| ST | 标准 |
| OV | 大件 |
| SS | 超大尺寸 |
| O | 其他尺寸 |

### 加拿大站（CA）

| 代码 | 说明 |
|------|------|
| EN | 信封装 |
| ST | 标准 |
| SO | 小号大件 |
| MO | 中号大件 |
| LO | 大号大件 |
| SP | 特殊大件 |
| O | 其他尺寸 |

### 英国 / 法国 / 德国 / 意大利 / 西班牙站（UK / FR / DE / IT / ES）

| 代码 | 说明 |
|------|------|
| SL | 小号信封 |
| NL | 标准信封 |
| LL | 大号信封 |
| ELL | 超大号信封 |
| SM | 小包裹 |
| SD | 标准包裹 |
| SB | 小号大件 |
| NB | 标准大件 |
| LB | 大号大件 |
| SPO | 特殊大件 |
| O | 其他尺寸 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` 等业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## MCP 调用示例

使用本 reference 的完整 `proxy_call` 示例；其他筛选组合仍直接放入 `arguments`。

## 响应示例（简略）

```json
{
  "total": 1523,
  "sourceType": "amazon",
  "dataSnapshotMonth": "nearly",
  "keyword": "yoga mat",
  "nodeLabel": "",
  "products": [
    {
      "asin": "B07XXXXXXX",
      "title": "Premium Yoga Mat - Non Slip, Eco Friendly...",
      "price": 29.99,
      "monthlySalesUnits": 12500,
      "monthlySalesRevenue": 374875.0,
      "bsr": 156,
      "rating": 4.6,
      "ratings": 35420,
      "profit": 42.5,
      "fulfillment": "FBA",
      "brand": "ExampleBrand",
      "sellerNation": "CN",
      "availableDateString": "2021-03-15",
      "badgeBestSeller": "Y",
      "badgeAmazonChoice": "N"
    }
  ],
  "message": "",
  "costToken": 1
}
```
