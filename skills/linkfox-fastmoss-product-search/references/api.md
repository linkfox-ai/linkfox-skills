# FastMoss-TikTok商品搜索 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/fastmoss/productSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词（商品标题模糊匹配） |
| region | string | 否 | 市场区域代码。可选值：US（美国）、GB（英国）、MX（墨西哥）、ES（西班牙）、DE（德国）、IT（意大利）、FR（法国）、ID（印度尼西亚）、VN（越南）、MY（马来西亚）、TH（泰国）、PH（菲律宾）、BR（巴西）、JP（日本）、SG（新加坡） |
| category | string | 否 | 英文类目名称，系统自动匹配TikTok类目ID。非英文需先翻译为英文 |
| shopType | integer | 否 | 店铺类型：1=本地店铺，2=跨境店铺 |
| isTopSelling | boolean | 否 | 仅筛选热销商品 |
| isNewListed | boolean | 否 | 仅筛选新上架商品 |
| isSshop | boolean | 否 | 仅筛选TikTok全托管（S-shop）商品 |
| isFreeShipping | boolean | 否 | 仅筛选包邮商品 |
| isLocalWarehouse | boolean | 否 | 仅筛选本地仓发货商品 |
| unitsSoldRange | object | 否 | 销量范围筛选，格式：`{"min": 100, "max": 5000}` |
| commissionRateRange | object | 否 | 佣金率范围筛选，格式：`{"min": 0.05, "max": 0.20}`（小数，0.10=10%） |
| creatorCountRange | object | 否 | 带货达人数范围筛选，格式：`{"min": 10, "max": 500}` |
| orderField | string | 否 | 排序字段：day7_units_sold（7天销量）、day7_gmv（7天GMV）、commission_rate（佣金率）、total_units_sold（总销量）、total_gmv（总GMV）、creator_count（达人数）。默认降序排列 |
| page | integer | 否 | 页码，默认 1 |
| pageSize | integer | 否 | 每页条数，最大 10，默认 10 |

## 响应结构

### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 符合条件的总记录数 |
| products | array | 商品信息列表（详见下方） |
| columns | array | 渲染列定义 |
| type | string | 渲染样式类型 |
| costToken | integer | 消耗 token 数 |

### 商品对象字段（products 数组）

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 商品标题 |
| productId | string | 商品唯一标识ID |
| region | string | 市场区域代码 |
| price | number | 商品价格 |
| minPrice | number | 最低价格 |
| maxPrice | number | 最高价格 |
| currency | string | 货币代码 |
| totalSaleCnt | integer | 累计总销量 |
| totalSale1dCnt | integer | 1天销量 |
| totalSale7dCnt | integer | 7天销量 |
| totalSale28dCnt | integer | 28天销量 |
| totalSale90dCnt | integer | 90天销量 |
| totalSaleGmvAmt | number | 累计总GMV |
| totalSaleGmv7dAmt | number | 7天GMV |
| totalSaleGmv28dAmt | number | 28天GMV |
| totalVideoCnt | integer | 带货视频数 |
| totalLiveCnt | integer | 直播带货数 |
| totalIflCnt | integer | 带货达人数 |
| productCommissionRate | number | 商品佣金比例（小数，0.10=10%） |
| productRating | number | 商品评分 |
| reviewCount | integer | 评论数量 |
| skuCount | integer | SKU数量 |
| shopName | string | 店铺名称 |
| shopSellerId | string | 卖家ID |
| shopTotalUnitsSold | integer | 店铺总销量 |
| isCrossBorder | integer | 是否跨境：1=跨境，0=本地 |
| isSShopText | string | 是否全托管店铺（是/否） |
| freeShippingText | string | 是否包邮（是/否） |
| availableDate | string | 上架时间 |
| categoryName | string | 商品品类名称 |
| salesTrendFlagText | string | 销售趋势标记 |
| tiktokUrl | string | TikTok商品链接 |
| fastmossUrl | string | FastMoss商品详情链接 |
| imageUrl | string | 商品图片URL |

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
curl -X POST https://tool-gateway.linkfox.com/fastmoss/productSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "phone case",
    "region": "US",
    "orderField": "day7_units_sold",
    "pageSize": 10
  }'
```

带范围筛选的示例：

```bash
curl -X POST https://tool-gateway.linkfox.com/fastmoss/productSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "beauty",
    "region": "US",
    "commissionRateRange": {"min": 0.10},
    "creatorCountRange": {"min": 50},
    "orderField": "commission_rate",
    "pageSize": 10
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-fastmoss-product-search",
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
