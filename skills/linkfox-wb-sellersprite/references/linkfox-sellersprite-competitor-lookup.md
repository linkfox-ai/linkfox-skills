---
name: linkfox-sellersprite-competitor-lookup
description: 利用卖家精灵数据反查ASIN或关键词，提供多站点亚马逊竞品的销量、排名、定价等核心指标分析。
---

# 卖家精灵-竞品查询（SellerSprite Competitor Lookup）

本业务能力用于查询和分析亚马逊竞品商品数据，帮助亚马逊卖家发现竞争商品、对标表现并提取可执行的竞争情报；完整参数与响应字段见本文后部的 API 参考章节。

## 能力边界

### ✅ 能力范围

- 通过 ASIN、关键词、卖家名称、品牌或类目查询亚马逊竞品，返回销量、销售额、BSR 排名、价格、评分、增长趋势等商品指标。
- 覆盖 12 个亚马逊站点：US、UK、DE、FR、JP、CA、IT、ES、MX、AU、TR、IN（默认 US）。
- 支持实时数据（近 30 天，`nearly`）与历史月度快照（`yyyyMM` 格式，如 `202501`），便于同比与季节性分析。
- 支持查询商品变体数据，并可按销量、销售额、BSR、价格、评分、增长率等多维排序。

### ❌ 边界与限制

- **结果上限**：每页返回 10-100 条（由 `size` 控制），更大结果集需翻页。
- **ASIN 上限**：单次最多查询 40 个 ASIN（`asinList`）。
- **历史快照**：仅支持已存在的月度快照，不支持未来日期。
- **关键词语言**：关键词应与目标站点语言一致（如美国用英语、德国用德语）以获得最佳结果；非对应语言需先翻译。
- **不在范围内**：ABA 搜索词数据与关键词排名（用 ABA 工具）；广告/PPC 广告管理；评论内容与情感分析；Listing 文案撰写或优化建议；供应商寻源或制造成本；账号健康与政策合规。

## 核心概念

卖家精灵竞品查询提供亚马逊商品数据，覆盖 12 个站点，可按 ASIN、关键词、卖家名称、品牌或类目查询，返回月销量、销售额、BSR 排名、价格、评分与增长趋势等指标。

**支持的站点**：US（美国）、UK（英国）、DE（德国）、FR（法国）、JP（日本）、CA（加拿大）、IT（意大利）、ES（西班牙）、MX（墨西哥）、AU（澳大利亚）、TR（土耳其）、IN（印度）。未指定站点时默认使用 **US**。

**数据快照**：支持实时数据（近 30 天）与历史月度快照。`nearly`（默认）查询当前数据，`yyyyMM` 格式（如 `202501`）查询历史快照。历史快照记录该月所有在售 Listing，便于同比与季节性对比。

**类目层级**：亚马逊类目名称支持以英文冒号（`:`）分隔的多级路径，如 `Electronics:Computers & Accessories:Monitors`。需将用户提供的类目描述转换为冒号分隔格式。

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/competitor-lookup`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/competitor-lookup",
  "arguments": {
    "marketplace": "US",
    "keyword": "wireless earbuds",
    "page": 1,
    "size": 20
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 使用示例

**1. 按 ASIN 查询竞品**
```json
{
  "marketplace": "US",
  "asinList": "B072MQ5BRX,B08N5WRWNW"
}
```
用途：按 ASIN 分析特定竞争商品。

**2. 按关键词搜索竞品**
```json
{
  "marketplace": "US",
  "keyword": "wireless earbuds",
  "matchType": 1,
  "order": {"field": "total_units", "desc": "true"},
  "size": 20
}
```
用途：发现某关键词下销量最高的商品，按月销量排序。

**3. 按品牌和类目筛选**
```json
{
  "marketplace": "US",
  "brand": "Anker",
  "nodeLabel": "Electronics:Headphones",
  "order": {"field": "total_amount", "desc": "true"}
}
```
用途：分析某品牌在指定类目下的商品矩阵。

**4. 按卖家名称查找**
```json
{
  "marketplace": "DE",
  "sellerName": "Anker Direct",
  "order": {"field": "bsr_rank", "desc": "false"}
}
```
用途：查看某卖家所有商品并按 BSR 排序。

**5. 历史快照对比**
```json
{
  "marketplace": "US",
  "keyword": "space heater",
  "dataSnapshotMonth": "202412",
  "order": {"field": "total_units", "desc": "true"},
  "size": 20
}
```
用途：利用历史数据快照分析季节性商品表现。

**6. 展示商品变体**
```json
{
  "marketplace": "JP",
  "asinList": "B0XXXXXXXXX",
  "showVariation": "Y"
}
```
用途：查看某商品系列所有变体级数据。

## 展示规则

1. **清晰呈现数据**：以格式化表格展示查询结果，包含 ASIN、标题、价格、月销量、BSR、评分、品牌等关键指标。除非用户要求，否则不做主观商业建议。
2. **关键词语言**：按关键词搜索时，始终将关键词翻译为目标站点语言（如 US/UK 用英语、DE 用德语、JP 用日语）；若用户提供的关键词语言不符，提醒用户并告知译文。
3. **BSR 说明**：展示 BSR 数据时，提醒用户 BSR 值越低表示销量表现越强。
4. **增长指标**：展示增长率时，明确正值代表改善还是下滑（BSR 增长数为正表示 BSR 上升，即排名变差）。
5. **分页提示**：当总结果数超出当前页大小时，告知用户总数并询问是否继续翻页。
6. **标识高亮**：当商品带有标识（Best Seller、Amazon's Choice、A+ 内容、视频）时，在结果中突出显示，因为它们是重要的竞争信号。
7. **错误处理**：查询失败时，依据 `message` 字段说明原因，并建议调整查询参数。
8. **快照引导**：当用户想做季节性或趋势分析时，主动建议使用历史快照（如去年同期）进行对比。

## 用户表达与场景速查

**适用** —— 亚马逊竞品商品数据查询：

| 用户说 | 场景 |
|--------|------|
| "查一下这个 ASIN 的竞品" | 基于 ASIN 的竞品查询 |
| "wireless earbuds 销量最高的有哪些" | 基于关键词的商品发现 |
| "这个卖家在卖什么" | 卖家商品矩阵分析 |
| "看看 Electronics 类目下的商品" | 基于类目的浏览 |
| "这几个 ASIN 的月销量" | 指定商品的销量估算 |
| "最近哪些新品涨得快" | 增长趋势发现 |
| "对比不同品牌的商品" | 品牌对标 |
| "去年 12 月这个细分市场怎么样" | 历史快照分析 |
| "高评分的畅销品" | 多指标筛选 |
| "这个类目里 FBA 和 FBM 的情况" | 配送方式分析 |

不适用场景见上方【能力边界】。

## 解决认证和积分问题

MCP/`proxy_call` 缺失、MCP 401、下游 401、下游 402 与 403 按 `onboarding.md` 分层处理。WorkBuddy 自动注入 Authorization；不得索要手工凭证或把凭证放入 `arguments`。

## MCP 调用规范

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`sellersprite/competitor-lookup`（区分大小写）
- `arguments` 直接使用本 reference 请求参数对象，不额外包裹 `body`、`params` 或 `data`，不传 headers、API Key、token、JWT 或手机号。

```json
{
  "toolName": "sellersprite/competitor-lookup",
  "arguments": {
    "marketplace": "US",
    "keyword": "wireless earbuds",
    "page": 1,
    "size": 20
  }
}
```

先检查 MCP/schema/`isError`；代理成功后读取 text/structured content，text JSON 只解析一次；再检查下游 `errcode`、`errorCode`、`errmsg`/`message`。禁止 HTTP fallback。收费调用失败、空结果或不理想时不自动重试；同一任务内相同 `toolName + arguments` 不重复调用。

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 否 | 亚马逊站点代码，默认 `US`。可选值：US、UK、DE、FR、JP、CA、IT、ES、MX、AU、TR、IN |
| keyword | string | 否 | 搜索关键词。请尽量翻译为对应国家的语言，比如美国用英语关键词，德国用德语关键词等 |
| asinList | string | 否 | ASIN，多个ASIN使用英文逗号分隔，最多40个。格式：`^[A-Z0-9]+(,[A-Z0-9]+){0,39}$` |
| sellerName | string | 否 | 卖家名称筛选 |
| brand | string | 否 | 品牌名称筛选 |
| nodeLabel | string | 否 | 亚马逊类目名称，支持多层级类目名称，层级之间用英文冒号 `:` 分割，例如 `Electronics:Headphones` |
| nodeIdPath | string | 否 | 亚马逊类目ID路径 |
| matchType | integer | 否 | 匹配方式。1 = 词组匹配（默认），2 = 模糊匹配，3 = 精准匹配 |
| showVariation | string | 否 | 是否查询变体。`Y` = 是，`N` = 否（默认） |
| dataSnapshotMonth | string | 否 | 亚马逊商品数据快照年月。默认 `nearly`（查询最近30天实时数据）。使用 `yyyyMM` 格式查询历史快照（如 `202412` 表示2024年12月）。仅支持已存在的历史快照，不支持未来日期。建议季节性分析时查询去年同期快照进行对比 |
| page | integer | 否 | 页码，从1开始（默认1） |
| size | integer | 否 | 每页条数，返回10-100条数据（默认50） |
| order | object | 否 | 排序配置（见下方说明） |

### 排序对象（order）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| field | string | 是 | 排序字段。可选值：`total_units`（月销量）、`total_amount`（月销售额）、`bsr_rank`（BSR排名）、`price`（价格）、`rating`（评分）、`reviews`（评分数）、`profit`（毛利率）、`reviews_rate`（留评率）、`available_date`（上架时间）、`questions`（Q&A数）、`total_units_growth`（月销量增长率）、`total_amount_growth`（月销售额增长率）、`reviews_increasement`（月新增评分数）、`bsr_rank_cv`（近7天BSR增长数）、`bsr_rank_cr`（近7天BSR增长率）、`amz_unit`（子体销量）。默认：`total_units` |
| desc | string | 是 | 排序方向。`true` = 降序，`false` = 升序。默认：`true` |

## 响应结构

### 顶层字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 匹配结果总数 |
| sourceType | string | 来源类型（如 `amazon`） |
| message | string | 执行消息或错误描述 |
| type | string | 渲染样式 |
| nodeLabel | string | 类目名称回显 |
| columns | array | 渲染的列定义 |
| products | array | 竞品列表（见下方说明） |
| costToken | integer | 消耗token |

### `products[]` 元素

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[] | object | 产品数组元素（来源对象字段表） |
| products[].asin | string | 商品ASIN |
| products[].title | string | 商品标题 |
| products[].price | number | 当前价格 |
| products[].primePrice | number | Prime价格 |
| products[].averagePrice | number | 平均价格 |
| products[].currency | string | 币种 |
| products[].monthlySalesUnits | integer | 月销量（件数） |
| products[].monthlySalesRevenue | number | 月销售额 |
| products[].monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| products[].bsr | integer | BSR排名 |
| products[].bsrGrowthRate | number | BSR增长率 |
| products[].bsrGrowthCount | integer | BSR增长数 |
| products[].rating | number | 评分 |
| products[].ratings | integer | 评分数 |
| products[].ratingsGrowth | integer | 月新增评分数 |
| products[].ratingsRate | number | 留评率 |
| products[].brand | string | 品牌 |
| products[].brandUrl | string | 品牌URL |
| products[].sellerName | string | BuyBox卖家名称 |
| products[].sellerId | string | BuyBox卖家ID |
| products[].sellerNation | string | BuyBox卖家国籍 |
| products[].sellerNum | integer | 卖家数 |
| products[].fulfillment | string | 配送方式：AMZ、FBA、FBM |
| products[].availableDate | string | 上架时间（日期格式） |
| products[].availableDateString | string | 上架日期（字符串格式） |
| products[].profit | number | 毛利率 |
| products[].fba | number | FBA运费 |
| products[].deliveryPrice | number | 卖家运费 |
| products[].imageUrl | string | 商品图片URL |
| products[].parent | string | 父体ASIN |
| products[].variationNum | integer | 变体数 |
| products[].variant30DayUnits | integer | 子体月销量（件数） |
| products[].variant30DayRevenue | number | 子体月销售额 |
| products[].variant30DayUpdatedAt | string | 子体数据更新时间（时间戳） |
| products[].amzUnitDateString | string | 子体销量更新日期 |
| products[].listingQualityScore | number | Listing质量得分 |
| products[].nodeLabelPath | string | 类目路径 |
| products[].nodeIdPath | string | 节点ID路径 |
| products[].nodeId | integer | 节点ID |
| products[].dimension | string | 商品尺寸 |
| products[].dimensionsType | string | 尺寸类型 |
| products[].weight | string | 商品重量 |
| products[].packageDimensions | string | 包装尺寸 |
| products[].packageDimensionType | string | 包装尺寸类型 |
| products[].packageWeight | string | 包装重量 |
| products[].sku | string | SKU |
| products[].keyword | string | 匹配的关键词（如通过关键词搜索，则显示对应关键词） |
| products[].dataSnapshotMonth | string | 数据查询月份 |
| products[].sourceTool | string | 来源工具 |
| products[].sourceType | string | 来源类型 |
| products[].badgeBestSeller | string | Best Seller标识（Y/N） |
| products[].badgeAmazonChoice | string | Amazon's Choice标识（Y/N） |
| products[].badgeNewRelease | string | New Release标识（Y/N） |
| products[].badgeEbc | string | A+页面（Y/N） |
| products[].badgeVideo | string | 视频介绍（Y/N） |
| products[].badge | object | 标识详情对象，包含：`bestSeller`、`amazonChoice`、`newRelease`、`ebc`、`video`（均为 Y/N 字符串） |
| products[].subcategories | array | 子类目排名，每项包含 `code`（类目code）、`rank`（排名）、`label`（名称） |

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

## MCP 调用示例

使用本 reference 的完整 `proxy_call` 示例；其他筛选组合仍直接放入 `arguments`。

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
