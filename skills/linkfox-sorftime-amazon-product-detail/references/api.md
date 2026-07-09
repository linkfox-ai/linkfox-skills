# Sorftime 产品详情(含趋势) API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/amazon/productDetail`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 亚马逊标准识别号（ASIN），支持多个（最多10个），以英文逗号隔开。示例：`B0088PUEPK` 或 `B0088PUEPK,B00U26V4VQ` |
| marketplace | string | 是 | 亚马逊站点代码：us、gb、de、fr、in、ca、jp、es、it、mx、ae、au、br、sa |
| includeTrend | integer | 否 | 是否包含趋势数据。`1`：包含（默认）；`2`：不包含 |
| queryTrendStartDate | string | 否 | 趋势开始日期，格式 `yyyy-MM-dd`。默认仅返回近15天，查询天数>15天时扣费加倍 |
| queryTrendEndDate | string | 否 | 趋势截止日期，格式 `yyyy-MM-dd` |

## 响应结构

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

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 code 字段区分（code = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errcode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` 等业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
| 其他非200值 | 业务异常 | 参考 `msg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B00FLYWNYQ", "marketplace": "us"}'
```

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B00FLYWNYQ", "marketplace": "us", "includeTrend": 1, "queryTrendStartDate": "2025-01-01", "queryTrendEndDate": "2025-03-01"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-sorftime-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE - `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE - `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
