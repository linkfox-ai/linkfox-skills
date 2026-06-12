# EchoTik-TikTok商品搜索 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/echotik/listProduct`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 商品关键词（请翻译为当地语言）。最大长度 1000 |
| region | string | 否 | 区域，默认 `US`。可选值：US（美国）、ID（印度尼西亚）、TH（泰国）、PH（菲律宾）、MY（马来西亚）、VN（越南）、GB（英国）、MX（墨西哥）、SG（新加坡）、SA（沙特阿拉伯）、BR（巴西）、ES（西班牙）、JP（日本）、DE（德国）、IT（意大利）、FR（法国） |
| categoryKeywordCN | string | 否 | 商品分类（请输入中文）。最大长度 1000 |
| minTotalSaleCnt | integer | 否 | 总销量（最小值） |
| maxTotalSaleCnt | integer | 否 | 总销量（最大值） |
| minTotalSale30dCnt | integer | 否 | 30天销量（最小值） |
| maxTotalSale30dCnt | integer | 否 | 30天销量（最大值） |
| minTotalSaleGmvAmt | string | 否 | 商品交易总额（最小值）。最大长度 1000 |
| maxTotalSaleGmvAmt | string | 否 | 商品交易总额（最大值）。最大长度 1000 |
| minTotalSaleGmv30dAmt | string | 否 | 商品交易总额（30天）（最小值）。最大长度 1000 |
| maxTotalSaleGmv30dAmt | string | 否 | 商品交易总额（30天）（最大值）。最大长度 1000 |
| minSpuAvgPrice | number | 否 | SPU平均价格（最小值） |
| maxSpuAvgPrice | number | 否 | SPU平均价格（最大值） |
| minProductRating | number | 否 | 商品评分（最小值） |
| maxProductRating | number | 否 | 商品评分（最大值） |
| minReviewCount | integer | 否 | 商品评价数（最小值） |
| maxReviewCount | integer | 否 | 商品评价数（最大值） |
| minProductCommissionRate | number | 否 | 商品佣金比例（最小值），输入值为百分比时自动转成小数，例如：5%->0.05 |
| maxProductCommissionRate | number | 否 | 商品佣金比例（最大值），输入值为百分比时自动转成小数，例如：5%->0.05 |
| minTotalIflCnt | integer | 否 | 带货达人数（最小值） |
| maxTotalIflCnt | integer | 否 | 带货达人数（最大值） |
| minTotalVideoCnt | integer | 否 | 带货视频数（最小值） |
| maxTotalVideoCnt | integer | 否 | 带货视频数（最大值） |
| minTotalViewsCnt | integer | 否 | 带货播放数（最小值） |
| maxTotalViewsCnt | integer | 否 | 带货播放数（最大值） |
| minFirstCrawlDt | integer | 否 | 商品上架时间（最小值），格式 YYYYMMDD（例如：20200101 代表 2020-01-01） |
| maxFirstCrawlDt | integer | 否 | 商品上架时间（最大值），格式 YYYYMMDD |
| saleDays | integer | 否 | 商品上架销售天数，单位是天 |
| productSortField | integer | 否 | 排序字段：1=总销量、2=商品交易总额、3=SPU平均价格、4=7天销量、5=30天销量、6=7天商品交易额、7=30天商品交易额。默认 `1` |
| sortType | integer | 否 | 排序方式：0=升序（asc）、1=降序（desc）。默认 `1` |
| pageNum | integer | 否 | 分页页码。默认 `1` |
| pageSize | integer | 否 | 每页条数。默认 `50` |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| products | array | 产品信息列表（详见下方） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 产品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 商品唯一标识ID |
| productName | string | 商品名称 |
| title | string | 商品名称 |
| imageUrl | string | 商品图片URL |
| coverUrl | string | 封面图URL列表 |
| productImageUrls | array | 商品图片URL列表 |
| categoryName | string | 商品品类名称 |
| categoryIds | array | 商品品类ID列表 |
| region | string | 区域代码 |
| currency | string | 货币 |
| price | number | 商品价格 |
| minPrice | number | 最低价格 |
| maxPrice | number | 最高价格 |
| spuAvgPrice | number | SPU平均价格 |
| productRating | number | 商品评分 |
| reviewCount | integer | 评论数量 |
| ratings | integer | 评论数 |
| productCommissionRate | number | 商品佣金比例 |
| totalSaleCnt | integer | 总销量 |
| totalSale1dCnt | integer | 1天内总销量 |
| totalSale7dCnt | integer | 7天内总销量 |
| totalSale15dCnt | integer | 15天内总销量 |
| totalSale30dCnt | integer | 30天内总销量 |
| totalSale60dCnt | integer | 60天内总销量 |
| totalSale90dCnt | integer | 90天内总销量 |
| monthlySalesUnits | integer | 月销量 |
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv1dAmt | number | 1天内总销售额 |
| totalSaleGmv7dAmt | number | 7天内总销售额 |
| totalSaleGmv15dAmt | number | 15天内总销售额 |
| totalSaleGmv30dAmt | number | 30天内总销售额 |
| totalSaleGmv60dAmt | number | 60天内总销售额 |
| totalSaleGmv90dAmt | number | 90天内总销售额 |
| firstCrawlDt | integer | 上架日期 |
| availableDate | string | 上架时间(时间戳) |
| discount | string | 折扣信息 |
| freeShippingText | string | 是否包邮 |
| offMarkText | string | 是否有优惠标记 |
| salesFlagText | string | 带货方式 |
| salesTrendFlagText | string | 销售趋势标记 |
| isSShopText | string | 是否S店 |
| salePropsInfo | array | 销售属性信息（商品规格） |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |
| asin | string | 产品ID |

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
curl -X POST https://tool-gateway.linkfox.com/echotik/listProduct \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "phone case",
    "region": "US",
    "minTotalSale30dCnt": 1000,
    "productSortField": 5,
    "sortType": 1,
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
