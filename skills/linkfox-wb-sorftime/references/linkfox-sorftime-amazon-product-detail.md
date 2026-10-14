# `linkfox-sorftime-amazon-product-detail`

## 功能与适用场景

按一个或多个 Amazon ASIN 查询 Sorftime 产品详情和历史趋势，支持 14 个站点。适用于查看指定产品的基本信息、变体、价格与利润、FBA 费用、销量、BSR、评分、卖家、Listing 特征、Deal，以及日/月销量、销售额、价格和排名历史。

此子能力面向已知 ASIN 的单品研究；产品跨类目、品牌、卖家或条件筛选请改用 `linkfox-sorftime-amazon-product-query`。

## 能力范围与限制

- 支持 US、GB、DE、FR、IN、CA、JP、ES、IT、MX、AE、AU、BR、SA，代码全部小写；英国代码为 `gb`，默认站点为 `us`。
- `asin` 和 `marketplace` 必填；一次最多 10 个 ASIN，使用英文逗号分隔。
- `includeTrend=1` 包含趋势，默认只返回近 15 天；`includeTrend=2` 不包含趋势，适合只取基本详情并减少成本。
- 设置 `queryTrendStartDate`、`queryTrendEndDate` 可查询指定范围，格式为 `yyyy-MM-dd`；超过 15 天的范围计费加倍。需要趋势时两个日期应一起核对。
- 销量和销售额是估算数据，非标准类目或 Amazon Renewed 等场景可能为 `-1`，表示无法估算。
- 当前详情价格、FBA 费用和利润字段按当地货币返回；趋势价格和销售额使用当地货币最小单位，例如美元为美分。
- 同一任务内相同 MCP `toolName + arguments` 不得重复调用；失败或空结果不得自动换 ASIN、改日期或重复请求。
- 不负责跨产品搜索、ABA 关键词排名/搜索量、广告投放、评论正文分析、专利/商标检查或法律结论。

## MCP 调用规范

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 原 endpoint：`/sorftime/amazon/productDetail`
- 精确 `toolName`：`sorftime/amazon/productDetail`，区分大小写且不带前导 `/`。
- `arguments`：直接使用本 reference 的请求参数对象，不额外包裹 `body`、`params`、`data` 或另一层 `arguments`。
- WorkBuddy 自动注入授权上下文；禁止传 `headers`、Authorization、API Key、token、JWT、手机号或其他凭证。
- 先检查 MCP 连接、工具、schema 和 `isError`，再读取 text/structured content；text JSON 只解析一次。之后检查下游 `errcode`/`errmsg`、`code`/`msg`，最后读取结果与成本字段。
- 同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或不理想结果不得自动改参、翻页或重试收费请求；追加调用前说明潜在消耗并取得用户同意。MCP 不可用时禁止 HTTP fallback。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `asin` | string | 是 | ASIN，可传单个或最多 10 个，以英文逗号分隔，如 `B0088PUEPK`。 |
| `marketplace` | string | 是 | `us`、`gb`、`de`、`fr`、`in`、`ca`、`jp`、`es`、`it`、`mx`、`ae`、`au`、`br`、`sa`。 |
| `includeTrend` | integer | 否 | `1` 包含趋势（默认），`2` 不包含趋势。 |
| `queryTrendStartDate` | string | 否 | 趋势开始日期，`yyyy-MM-dd`。默认仅近 15 天；超过 15 天计费加倍。 |
| `queryTrendEndDate` | string | 否 | 趋势截止日期，`yyyy-MM-dd`。 |

## 响应结构

响应字段来源：`skills/linkfox-sorftime-amazon-product-detail/references/api.md`。

### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 响应码（200表示成功） |
| msg | string | 响应消息 |
| total | integer | 结果总数 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗Token数量 |
| requestConsumed | integer | 消耗的请求数 |
| sourceType | string | 来源类型：sorftime |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| products | array | 产品详情列表（详见下方） |

### 商品对象字段（products 数组元素）

趋势数组均采用交错格式：偶数下标为日期（yyyyMMdd），奇数下标为对应值。

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string | 商品标题 |
| brand | string | 品牌 |
| asinUrl | string | 商品链接，亚马逊Listing详情页URL |
| imageUrl | string | 主图URL |
| productImageUrls | array | 主图列表（所有商品图片URL） |
| ebcPhoto | array | A+图片列表 |
| storeName | string | 店铺名称 |
| description | string | 五点描述 |
| productBadge | array | 产品标志，如Amazon Choice、Best Seller、New Release等 |
| lastUpdate | string | 更新时间，ASIN数据最近采集时间（格式yyyy-MM-dd） |
| offSale | boolean | 是否下架。true=不可售，false=可售 |
| productType | string | 分类，亚马逊产品类目节点名称 |
| weight | string | 重量，单位g |
| size | array | 尺寸，外包装[最长边,第二长边,最短边]，单位cm |
| parentAsin | string | 父ASIN，有子体时为父级ASIN，无子体时为null |
| variationNum | integer | 变体数 |
| variationASIN | array | 子体ASIN列表，无子体时为空 |
| attribute | array | 产品属性，有子体时表示子体属性。每项包含 asin（子体ASIN）、name（属性名）、value（属性值） |
| price | number | 销售价，扣除Coupon后的实际售价，单位为当地货币(如美元) |
| coupon | integer | Coupon政策。值>=0为抵扣金额(如500=$5)，值<0为折扣百分比(如-10=10%折扣) |
| platformFee | number | 平台佣金，单位为当地货币(如美元) |
| fbaFees | number | FBA费用，单位为当地货币(如美元) |
| fbaDetail | array | FBA明细。首项为配送费，后续为月份:仓储费，如[475,"1-9:5","10-12:15"] |
| shipCost | number | FBM配送费，单位为当地货币(如美元) |
| shipsFrom | string | 发货方 |
| profitAmount | number | 利润，到手价-FBA费-佣金，单位为当地货币(如美元) |
| profitRate | number | 利润率，例25.83表示25.83% |
| monthlySalesUnits | integer | 官方月销量，亚马逊公布的ASIN月销量，取近7个自然日最新值，无则为0 |
| salesRank | integer | BSR排名，大类排名 |
| category | array | 大类，[大类名称, NodeId] |
| bsrCategory | array | 小类排名列表，每项包含 nodeId（节点ID）、name（类目名称）、rank（排名）、date（日期，格式yyyyMMdd） |
| availableDate | string | 上架时间，格式yyyy-MM-dd |
| onlineDays | integer | 上架天数 |
| rating | number | 当前评分（0.0-5.0，如4.70） |
| ratings | integer | 评分数量 |
| fiveStarRatings | number | 5星占比，例57.7表示57.7% |
| fourStarRatings | number | 4星占比 |
| threeStarRatings | number | 3星占比 |
| twoStarRatings | number | 2星占比 |
| oneStarRatings | number | 1星占比 |
| buyboxSeller | string | Buybox卖家名称 |
| buyBoxSellerId | string | Buybox卖家ID |
| buyboxSellerAddress | string | 卖家所在地，Buybox卖家国籍(二字码如CN、US)，亚马逊自营时为null |
| isFBA | boolean | 是否FBA，Buybox卖家是否使用FBA物流 |
| sellerNum | integer | 卖家数 |
| aPlus | boolean | 有A+ |
| hasVideo | boolean | 有视频 |
| hasBrandStore | boolean | 有品牌店 |
| feature | object | 产品特性星级，亚马逊为此产品统计的特性及每个特性的星级，如{"Battery life":4.0} |
| productInfo | object | 产品信息，Listing中部Product Information结构化数据 |
| property | object | 属性列表，含变体属性及Bullet Points上方说明 |
| brandPromotion | string | 品牌促销 |
| dealType | string | Deal标签 |
| extraSavings | array | 关联促销，如[{Asin:xxx, Text:"Save 5%..."}] |
| rankTrend | array | BSR趋势，大类排名变化历史，交错格式[日期,排名,...] |
| bsrRankTrend | array | 小类排名趋势，JSON格式[{NodeId:xxx, Rank:[日期,排名,...]}] |
| listingSalesVolumeOfDailyTrend | array | 日销量趋势，值为-1表示无法预估 |
| listingSalesOfDailyTrend | array | 日销售额趋势，单位为当地货币最小单位(如美分)，值为-1表示无法预估 |
| listingSalesVolumeOfMonthTrend | array | 月销量趋势(近30日)，值为-1表示无法预估 |
| listingSalesOfMonthTrend | array | 月销售额趋势，单位为当地货币最小单位(如美分) |
| priceTrend | array | 售价趋势，未扣Coupon，单位为当地货币最小单位，-1表示该日无可用价格 |
| listPriceTrend | array | 原价趋势（划线价历史），单位为当地货币最小单位，-1表示该日无可用价格 |
| dealTrend | array | Deal趋势，值1=有Deal，0=无Deal |
### products 内嵌数组/对象字段

以下层级均由来源字段说明明确给出；来源未说明具体类型时不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `products[].productImageUrls[]` | 来源未说明 | 单张商品图片 URL。 |
| `products[].ebcPhoto[]` | 来源未说明 | 单张 A+ 图片。 |
| `products[].productBadge[]` | 来源未说明 | 单个产品标志，如 Amazon Choice、Best Seller、New Release。 |
| `products[].size[0]` | 来源未说明 | 外包装最长边，单位 cm。 |
| `products[].size[1]` | 来源未说明 | 外包装第二长边，单位 cm。 |
| `products[].size[2]` | 来源未说明 | 外包装最短边，单位 cm。 |
| `products[].variationASIN[]` | 来源未说明 | 单个子体 ASIN。 |
| `products[].attribute[]` | object | 单个子体属性项。 |
| `products[].attribute[].asin` | 来源未说明 | 子体 ASIN。 |
| `products[].attribute[].name` | 来源未说明 | 属性名。 |
| `products[].attribute[].value` | 来源未说明 | 属性值。 |
| `products[].fbaDetail[0]` | 来源未说明 | FBA 配送费。 |
| `products[].fbaDetail[1...]` | 来源未说明 | 月份与仓储费，来源示例为 `"1-9:5"`、`"10-12:15"`。 |
| `products[].category[0]` | 来源未说明 | 大类名称。 |
| `products[].category[1]` | 来源未说明 | 大类 NodeId。 |
| `products[].bsrCategory[]` | object | 单个小类排名项。 |
| `products[].bsrCategory[].nodeId` | 来源未说明 | 节点 ID。 |
| `products[].bsrCategory[].name` | 来源未说明 | 类目名称。 |
| `products[].bsrCategory[].rank` | 来源未说明 | 排名。 |
| `products[].bsrCategory[].date` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].feature.<特性名>` | number | 产品特性名对应的星级；来源示例为 `{"Battery life":4.0}`。 |
| `products[].extraSavings[]` | object | 单个关联促销项。 |
| `products[].extraSavings[].Asin` | 来源未说明 | 关联促销 ASIN。 |
| `products[].extraSavings[].Text` | 来源未说明 | 关联促销文字，来源示例为 `"Save 5%..."`。 |
| `products[].rankTrend[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].rankTrend[奇数下标]` | 来源未说明 | 对应大类 BSR 排名。 |
| `products[].bsrRankTrend[]` | object | 单个小类排名趋势项。 |
| `products[].bsrRankTrend[].NodeId` | 来源未说明 | 小类节点 ID。 |
| `products[].bsrRankTrend[].Rank` | array | 日期、排名交错数组。 |
| `products[].bsrRankTrend[].Rank[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].bsrRankTrend[].Rank[奇数下标]` | 来源未说明 | 对应小类排名。 |
| `products[].listingSalesVolumeOfDailyTrend[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].listingSalesVolumeOfDailyTrend[奇数下标]` | 来源未说明 | 对应日销量；`-1` 表示无法预估。 |
| `products[].listingSalesOfDailyTrend[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].listingSalesOfDailyTrend[奇数下标]` | 来源未说明 | 对应日销售额，单位为当地货币最小单位；`-1` 表示无法预估。 |
| `products[].listingSalesVolumeOfMonthTrend[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].listingSalesVolumeOfMonthTrend[奇数下标]` | 来源未说明 | 对应近 30 日月销量；`-1` 表示无法预估。 |
| `products[].listingSalesOfMonthTrend[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].listingSalesOfMonthTrend[奇数下标]` | 来源未说明 | 对应月销售额，单位为当地货币最小单位。 |
| `products[].priceTrend[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].priceTrend[奇数下标]` | 来源未说明 | 对应未扣 Coupon 售价，单位为当地货币最小单位；`-1` 表示无可用价格。 |
| `products[].listPriceTrend[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].listPriceTrend[奇数下标]` | 来源未说明 | 对应划线原价，单位为当地货币最小单位；`-1` 表示无可用价格。 |
| `products[].dealTrend[偶数下标]` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |
| `products[].dealTrend[奇数下标]` | 来源未说明 | 对应 Deal 状态，`1` 有 Deal、`0` 无 Deal。 |

来源没有说明 `columns[]`、`productInfo` 或 `property` 的内部字段，也没有进一步说明部分图片/标志数组元素类型，因此不能补猜。

## 错误码与处理

| errcode | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 解析 `products` 和成本字段。 |
| `401` | 认证失败 | 读取 `references/onboarding.md`，按 WorkBuddy 自动授权异常处理，不传凭证。 |
| `402` | 余额不足 | 读取 `references/onboarding.md`，引导用户自助处理，不自动查询套餐或支付。 |
| 其他非 200 | 业务或参数异常 | 根据 `msg` 修正 ASIN、站点、日期或趋势参数；不自动改参重试。 |

错误示例：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

## MCP 请求示例

```json
{"toolName":"sorftime/amazon/productDetail","arguments":{"asin":"B00FLYWNYQ","marketplace":"us","includeTrend":2}}
```

```json
{"toolName":"sorftime/amazon/productDetail","arguments":{"asin":"B00FLYWNYQ","marketplace":"us","includeTrend":1,"queryTrendStartDate":"2025-01-01","queryTrendEndDate":"2025-03-01"}}
```

每个示例只表示一次调用。超过 15 天的趋势范围计费加倍，日期范围或 ASIN 变化不得自动触发新请求。

## 反馈 API

当实际行为与本能力描述不符、结果不符合意图、用户表达满意/不满或提出改进建议时，按需调用独立反馈端点，不影响当前结果交付：

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- `Content-Type: application/json`
- `skillName` 使用当前 WorkBuddy 能力名 `linkfox-wb-sorftime`。
- `sentiment` 取 `POSITIVE`（表扬）、`NEUTRAL`（无情绪建议）或 `NEGATIVE`（投诉/错误）。
- `category` 取 `BUG`、`COMPLAINT`、`SUGGESTION` 或 `OTHER`。
- `content` 说明用户意图/反馈、实际表现以及问题或表扬原因。
