# 卖家精灵-选产品 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/productSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

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

| 字段 | 类型 | 说明 |
|------|------|------|
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

### 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 亚马逊ASIN |
| title | string | 商品标题 |
| asinUrl | string | 亚马逊商品详情页URL |
| imageUrl | string | 商品图片URL |
| price | number | 当前价格 |
| averagePrice | number | 平均价格 |
| primePrice | number | Prime价格，-1表示没有 |
| currency | string | 币种 |
| monthlySalesUnits | integer | 月销量 |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| bsr | integer | BSR排名 |
| bsrGrowthRate | number | BSR增长率 |
| rating | number | 评分 |
| ratings | integer | 评分数 |
| ratingsRate | number | 留评率 |
| profit | number | 毛利率（%） |
| fba | number | FBA运费 |
| sellerNum | integer | 卖家数 |
| sellerId | string | BuyBox卖家ID |
| sellerName | string | BuyBox卖家名称 |
| sellerNation | string | BuyBox卖家国籍 |
| brand | string | 品牌 |
| brandUrl | string | 品牌页URL |
| fulfillment | string | 配送方式（AMZ / FBA / FBM） |
| availableDate | string | 上架时间（时间戳） |
| availableDateString | string | 上架日期（格式化字符串） |
| variationNum | integer | 变体数 |
| variant30DayUnits | integer | 子体月销量（件数） |
| variant30DayRevenue | number | 子体月销售额（金额） |
| variant30DayUpdatedAt | string | 子体数据更新时间 |
| weight | string | 重量 |
| packageWeight | string | 包装重量 |
| dimension | string | 尺寸 |
| packageDimensions | string | 包装尺寸 |
| dimensionsType | string | 尺寸类型 |
| packageDimensionType | string | 包装尺寸类型 |
| listingQualityScore | number | Listing质量得分 |
| deliveryPrice | number | 卖家运费，-1表示没有 |
| nodeLabelPath | string | 类目路径 |
| nodeIdPath | string | 节点ID路径 |
| nodeId | integer | 节点ID |
| dataSnapshotMonth | string | 数据查询月份 |
| badgeBestSeller | string | Best Seller标识（Y/N） |
| badgeAmazonChoice | string | Amazon's Choice标识（Y/N） |
| badgeNewRelease | string | New Release标识（Y/N） |
| badgeVideo | string | 视频介绍（Y/N） |
| badgeEbc | string | A+页面（Y/N） |
| badge | object | 标识汇总对象，包含：bestSeller、amazonChoice、newRelease、video、ebc |
| subcategories | array | 子类目列表，每项包含 code（类目code）、rank（排名）、label（名称） |
| sku | string | SKU |
| keyword | string | 对应筛选的关键词 |
| sourceType | string | 来源类型 |
| sourceTool | string | 来源工具标识 |

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
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/productSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "yoga mat",
    "marketplace": "US",
    "minUnits": 300,
    "minPrice": 10,
    "maxPrice": 50,
    "order": {"field": "total_units", "desc": "true"},
    "page": 1,
    "size": 20
  }'
```

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

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
