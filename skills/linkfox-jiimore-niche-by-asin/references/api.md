# 极目-亚马逊-产品挖掘（ASIN） API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/jiimore/pageAsinsByAsin`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 参考 ASIN，用于查询与该 ASIN 同属细分市场（Niche）的竞品列表，最大长度1000字符 |

### 站点与分页

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| countryCode | string | 否 | US | 国家编码，可选值：`US`（美国）、`JP`（日本）、`DE`（德国） |
| page | integer | 否 | 1 | 页码（从1开始） |
| pageSize | integer | 否 | 50 | 每页返回数量（10-100） |
| sortField | string | 否 | purchasedClicksT360 | 排序字段（见下方排序选项） |
| sortType | string | 否 | desc | 排序方式：`desc`（降序）或 `asc`（升序） |

### 筛选参数（均为可选）

**价格与FBA**：

| 参数 | 类型 | 说明 |
|------|------|------|
| priceMin | number | 最低产品价格 |
| priceMax | number | 最高产品价格 |
| fbaFeeMin | number | 最低FBA佣金 |
| fbaFeeMax | number | 最高FBA佣金 |
| grossProfitMarginMin | number | 最低毛利率 |
| grossProfitMarginMax | number | 最高毛利率 |

**评论与评分**：

| 参数 | 类型 | 说明 |
|------|------|------|
| totalReviewsMin | integer | 最少评论数量 |
| totalReviewsMax | integer | 最多评论数量 |
| customerRatingMin | number | 最低评分，取值范围 0.0-5.0 |
| customerRatingMax | number | 最高评分，取值范围 0.0-5.0 |

**点击数据（7天）**：

| 参数 | 类型 | 说明 |
|------|------|------|
| clickCountT7Min | integer | 最低周点击量 |
| clickCountT7Max | integer | 最高周点击量 |
| clickCountGrowthT7Min | number | 最低周点击增长率，取值范围 0-1，例如 0.1 表示 10% |
| clickCountGrowthT7Max | number | 最高周点击增长率，取值范围 0-1，例如 0.1 表示 10% |
| clickConversionRateMin | number | 最低点击转化率，取值范围 0-1，例如 0.1 表示 10% |
| clickConversionRateMax | number | 最高点击转化率，取值范围 0-1，例如 0.1 表示 10% |

**点击数据（30天）**：

| 参数 | 类型 | 说明 |
|------|------|------|
| clickCountT30Min | integer | 最低月点击量 |
| clickCountT30Max | integer | 最高月点击量 |
| clickCountGrowthT30Min | number | 最低月点击增长率，取值范围 0-1，例如 0.1 表示 10% |
| clickCountGrowthT30Max | number | 最高月点击增长率，取值范围 0-1，例如 0.1 表示 10% |

**综合转化率**：

| 参数 | 类型 | 说明 |
|------|------|------|
| clickConversionRateCompositeMin | number | 最低综合点击转化率，取值范围 0-1，例如 0.1 表示 10% |
| clickConversionRateCompositeMax | number | 最高综合点击转化率，取值范围 0-1，例如 0.1 表示 10% |

**销量与上架时间**：

| 参数 | 类型 | 说明 |
|------|------|------|
| salesVolumeT360Min | integer | 最低年销量 |
| salesVolumeT360Max | integer | 最高年销量 |
| launchDateMin | string | 最早上架时间，格式为 yyyyMMdd000000 |
| launchDateMax | string | 最晚上架时间，格式为 yyyyMMdd000000 |

**细分市场与卖家**：

| 参数 | 类型 | 说明 |
|------|------|------|
| nicheCountMin | integer | 最少细分市场数量 |
| nicheCountMax | integer | 最多细分市场数量 |
| sellerCountry | string | 卖家国家的国家码，选择多个国家的用英文逗号隔开，如：CN,US |

### 排序选项

| 值 | 说明 |
|------|------|
| purchasedClicksT360 | 360天购买点击（默认） |
| totalReviews | 评论数量 |
| price | 价格 |
| launchDate | 上架时间 |
| clickCountT30 | 30天点击量 |
| clickCountT90 | 90天点击量 |
| clickCountT7 | 7天点击量 |
| clickConversionRate | 点击转化率(原7天点击转化率) |
| clickConversionRateComposite | 综合点击转化率 |
| customerRating | 评分 |
| clickCountGrowthT7 | 周点击增长率 |
| clickCountGrowthT30 | 月点击增长率 |
| currentPrice | 当前价格 |
| fbaFee | FBA佣金 |
| shippingFee | FBA运费 |
| gpm | 毛利率 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总记录数 |
| pages | integer | 总页数 |
| page | integer | 当前页 |
| pageSize | integer | 每页大小 |
| data | array | ASIN 产品列表（见下方产品对象字段） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 产品对象字段（`data` 数组内）

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 亚马逊产品ASIN |
| parentAsin | string | 亚马逊产品父ASIN |
| title | string | 产品标题 |
| brand | string | 品牌 |
| price | number | 价格 |
| currentPrice | number | 当前价格 |
| currency | string | 币种 |
| customerRating | number | 评分 |
| totalReviews | integer | 评论数 |
| launchDate | string | 上架时间 |
| link | string | ASIN链接 |
| imagesUrl | string | 产品主图 |
| sellerName | string | 卖家名称 |
| sellerId | string | 卖家ID |
| fbaFee | number | FBA佣金 |
| shippingFee | number | FBA运费 |
| gpm | number | 毛利率 |
| clickConversionRate | number | 点击转化率(原7天点击转化率) |
| clickConversionRateComposite | number | 综合点击转化率 |
| clickConversionRateType | string | 转化率计算类型 |
| clickConversionRateCompositeType | string | 综合转化率计算类型 |
| clickCountT7 | integer | 7天点击量 |
| clickCountT30 | integer | 30天点击量 |
| clickCountT90 | integer | 90天点击量 |
| clickCountGrowthT7 | number | 周点击增长率 |
| clickCountGrowthT30 | number | 月点击增长率 |
| purchasedClicksT360 | integer | 360天购买点击 |
| salesVolumeT360 | integer | 年销量 |
| nicheCount | integer | 所属细分市场数 |
| sameNicheTitle | string | 同细分市场（Niche）标题 |
| involvedNum | integer | 涉及的关键词数量 |
| involvedFrequency | integer | 涉及的关键词频次 |
| categoryNames | array | 类目信息 |
| hasMetric | boolean | 标识是否有指标 |
| searchValueType | string | 搜索类型: exact(精准匹配), sameNiche(与参考 ASIN 同属细分市场), category(类目) |
| niches | array | top3细分市场，包含: nicheId, nicheTitle, demand(市场评分), image, marketplaceId |
| bestSellersRanking | array | 畅销榜排名，包含: rank(排名), category(类目名称) |
| trends | array | 90天趋势数据，包含: day(日期), clickCountT7(周点击量), reviewCount(评论数), reviewRating(评分), bestSellerRanking(BSR排名), averagePriceT7(周平均价格), totalOfferDepthT7(7天新增offer) |
| lastUpdateTime | string | 最后更新时间 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
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
curl -X POST https://tool-gateway.linkfox.com/jiimore/pageAsinsByAsin \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B0GC4RPX79",
    "countryCode": "US",
    "sortField": "purchasedClicksT360",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
```

### 带筛选条件的查询示例

```bash
curl -X POST https://tool-gateway.linkfox.com/jiimore/pageAsinsByAsin \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B0GC4RPX79",
    "countryCode": "US",
    "clickConversionRateCompositeMin": 0.15,
    "clickCountT30Min": 2000,
    "totalReviewsMax": 100,
    "sortField": "clickConversionRateComposite",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
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
