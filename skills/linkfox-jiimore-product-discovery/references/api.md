# 极目-亚马逊-产品挖掘 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/jiimore/productDiscovery`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 关键词（必填，并根据所选国家，翻译关键词为对应国家的语言） |

### 筛选参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| countryCode | string | 否 | 国家，使用国家简称。默认 `US`。可选值：`US`、`JP`、`DE` |
| priceMin | number | 否 | 最低商品价格 |
| priceMax | number | 否 | 最高商品价格 |
| totalReviewsMin | integer | 否 | 最低评论数 |
| totalReviewsMax | integer | 否 | 最高评论数 |
| customerRatingMin | number | 否 | 最低评分 |
| customerRatingMax | number | 否 | 最高评分 |
| clickConversionRateMin | number | 否 | 最低点击购买转化率，数值范围为0-1，0.1表示10% |
| clickConversionRateMax | number | 否 | 最高点击购买转化率，数值范围为0-1，0.1表示10% |
| clickConversionRateCompositeMin | number | 否 | 最低综合转化率，数值范围为0-1，0.1表示10% |
| clickConversionRateCompositeMax | number | 否 | 最高综合转化率，数值范围为0-1，0.1表示10% |
| clickCountT7Min | integer | 否 | 最低周点击量 |
| clickCountT7Max | integer | 否 | 最高周点击量 |
| clickCountT30Min | integer | 否 | 最低月点击量 |
| clickCountT30Max | integer | 否 | 最高月点击量 |
| clickCountGrowthT7Min | number | 否 | 最低周点击增长率，数值范围为0-1，0.1表示10% |
| clickCountGrowthT7Max | number | 否 | 最高周点击增长率，数值范围为0-1，0.1表示10% |
| clickCountGrowthT30Min | number | 否 | 最低月点击增长率，数值范围为0-1，0.1表示10% |
| clickCountGrowthT30Max | number | 否 | 最高月点击增长率，数值范围为0-1，0.1表示10% |
| salesVolumeT360Min | integer | 否 | 最低年销售量 |
| salesVolumeT360Max | integer | 否 | 最高年销售量 |
| grossProfitMarginMin | number | 否 | 最低毛利率 |
| grossProfitMarginMax | number | 否 | 最高毛利率 |
| fbaFeeMin | number | 否 | 最低FBA佣金 |
| fbaFeeMax | number | 否 | 最高FBA佣金 |
| launchDateMin | string | 否 | 最小上架时间，格式为：`yyyyMMdd000000` |
| launchDateMax | string | 否 | 最大上架时间，格式为：`yyyyMMdd000000` |
| nicheCountMin | integer | 否 | 最低细分市场数量 |
| nicheCountMax | integer | 否 | 最高细分市场数量 |
| sellerCountry | string | 否 | 卖家国家地区编码，选择多个的情况下用逗号隔开，如：`CN,US` |

### 排序与分页

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sortField | string | 否 | 排序字段。默认 `purchasedClicksT360`。可选值：`totalReviews`（总评论数）、`price`（价格）、`launchDate`（上架时间）、`clickCountT7`（7天点击量）、`clickCountT30`（30天点击量）、`clickCountT90`（90天点击量）、`clickConversionRate`（点击购买转化率）、`clickConversionRateComposite`（综合点击购买转化率）、`customerRating`（评分）、`purchasedClicksT360`（360天购买量）、`clickCountGrowthT7`（周点击增长率）、`clickCountGrowthT30`（月点击增长率）、`currentPrice`（当前价格）、`fbaFee`（FBA佣金）、`shippingFee`（FBA运费）、`gpm`（毛利率） |
| sortType | string | 否 | 排序方式。默认 `desc`。可选值：`desc`（降序）、`asc`（升序） |
| page | integer | 否 | 页码。默认 `1` |
| pageSize | integer | 否 | 每页数量（10-100）。默认 `50` |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总数 |
| sourceTool | string | 工具类型：`jiimore` |
| sourceType | string | 来源类型：`amazon` |
| type | string | 渲染的样式 |
| title | string | 标题 |
| costToken | integer | 消耗token |
| columns | array | 渲染的列 |
| products | array | 产品列表（详见下方） |

### 产品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 亚马逊商品ASIN |
| parentAsin | string | 亚马逊商品父ASIN |
| title | string | 产品标题 |
| brand | string | 品牌 |
| price | number | 价格 |
| imageUrl | string | 产品主图 |
| productImageUrls | array | 产品图片链接列表 |
| asinUrl | string | ASIN链接 |
| ratings | integer | 评论数 |
| availableDate | string | 上架时间（时间戳） |
| availableDateString | string | 上架日期（字符串） |
| categoryNames | array | 类目信息 |
| marketplaceId | string | 站点ID |
| clickCountT7 | integer | 周点击量 |
| clickCountT30 | integer | 月点击量 |
| clickCountT90 | integer | 季度点击量 |
| clickConversionRate | number | 点击购买转化率 |
| clickConversionRateComposite | number | 综合转化率 |
| grossProfitMargin | number | 毛利率 |
| fbaFee | number | 亚马逊佣金 |
| shippingFee | number | FBA运费 |
| sourceTool | string | 工具类型：`jiimore` |
| sourceType | string | 来源类型：`amazon` |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
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
curl -X POST https://tool-gateway.linkfox.com/jiimore/productDiscovery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "wireless charger",
    "countryCode": "US",
    "clickConversionRateMin": 0.1,
    "priceMin": 10,
    "priceMax": 50,
    "sortField": "clickConversionRate",
    "sortType": "desc",
    "page": 1,
    "pageSize": 20
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
