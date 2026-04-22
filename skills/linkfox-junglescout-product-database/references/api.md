# Jungle Scout 产品数据库查询 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/tool-jungle-scout/product-database/query`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp` |

### 关键词筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| includeKeywords | string | 否 | 标题/ASIN包含关键词，逗号分隔，最多100项，每项最长50字符 |
| excludeKeywords | string | 否 | 标题/ASIN排除关键词，逗号分隔，最多100项，每项最长50字符 |

### 品类筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| categories | string | 否 | 主分类名称，逗号分隔，需匹配对应站点的标准分类名。美国站示例：Appliances, Arts Crafts & Sewing, Automotive, Baby, Beauty & Personal Care, Books, CDs & Vinyl, Cell Phones & Accessories, Clothing Shoes & Jewelry, Collectibles & Fine Art, Computers, Digital Music, Electronics, Garden & Outdoor, Grocery & Gourmet Food, Handmade, Health Household & Baby Care, Home & Kitchen, Industrial & Scientific, Kindle Store, Kitchen & Dining, Movies & TV, Musical Instruments, Office Products, Pet Supplies, Sports & Outdoors, Tools & Home Improvement, Toys & Games, Video Games 等。其他站点（uk, de, fr, it, es, mx, jp, ca, in）有对应的本地分类名 |

### 价格 / 销量 / 收入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minPrice | number | 否 | 最低价格 |
| maxPrice | number | 否 | 最高价格 |
| minSales | integer | 否 | 最低月销量 |
| maxSales | integer | 否 | 最高月销量 |
| minRevenue | number | 否 | 最低月收入 |
| maxRevenue | number | 否 | 最高月收入 |

### 评论 / 评分

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minReviews | integer | 否 | 最低评论数 |
| maxReviews | integer | 否 | 最高评论数 |
| minRating | number | 否 | 最低评分（1.0-5.0） |
| maxRating | number | 否 | 最高评分（1.0-5.0） |

### 重量 / 尺寸 / BSR

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minWeight | number | 否 | 最低重量（磅） |
| maxWeight | number | 否 | 最高重量（磅） |
| minRank | integer | 否 | 最低BSR排名 |
| maxRank | integer | 否 | 最高BSR排名 |
| minLqs | integer | 否 | 最低LQS评分（1-10） |
| maxLqs | integer | 否 | 最高LQS评分（1-10） |

### 卖家 / 产品类型

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minSellers | integer | 否 | 最少卖家数 |
| maxSellers | integer | 否 | 最多卖家数 |
| minNet | number | 否 | 最低净利润 |
| maxNet | number | 否 | 最高净利润 |
| sellerTypes | string | 否 | 卖家类型，逗号分隔。可选值：`amz`（亚马逊自营）、`fba`、`fbm` |
| productTiers | string | 否 | 产品尺寸层级，逗号分隔。可选值：`oversize`、`standard` |
| excludeTopBrands | boolean | 否 | 是否排除头部品牌 |
| excludeUnavailableProducts | boolean | 否 | 是否排除不可购买的商品 |

### 日期 / 分页 / 排序

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minUpdatedAt | string | 否 | 数据更新起始日期（YYYY-MM-DD） |
| maxUpdatedAt | string | 否 | 数据更新截止日期（YYYY-MM-DD） |
| needCount | integer | 否 | 需要返回的结果总数，API内部自动分页 |
| sort | string | 否 | 排序字段。可选值：`name`, `-name`, `category`, `-category`, `revenue`, `-revenue`, `sales`, `-sales`, `price`, `-price`, `rank`, `-rank`, `reviews`, `-reviews`, `lqs`, `-lqs`, `sellers`, `-sellers`。前缀 `-` 表示降序。默认：`name` |

### 站点映射

| 站点 | marketplace 值 |
|------|---------------|
| 美国 | us |
| 英国 | uk |
| 德国 | de |
| 印度 | in |
| 加拿大 | ca |
| 法国 | fr |
| 意大利 | it |
| 西班牙 | es |
| 墨西哥 | mx |
| 日本 | jp |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| productDatabaseList | array | 产品数据列表 |

### productDatabaseList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 产品唯一标识 |
| title | string | 产品标题 |
| brand | string | 品牌名称 |
| category | string | 主分类 |
| breadcrumbPath | string | 完整分类路径 |
| price | number | 当前售价 (USD) |
| approximate30DayUnitsSold | integer | 近30天预估销量 |
| approximate30DayRevenue | number | 近30天预估收入 (USD) |
| productRank | integer | BSR排名 |
| reviews | integer | 评论总数 |
| rating | number | 平均评分 (1.0-5.0) |
| listingQualityScore | integer | Listing质量评分 (LQS, 1-10) |
| numberOfSellers | integer | 在售卖家数 |
| sellerType | string | 卖家类型 (amz/fba/fbm) |
| imageUrl | string | 商品主图URL |
| dateFirstAvailable | string | 首次上架日期 |
| weightValue | number | 产品重量 |
| weightUnit | string | 重量单位 |
| lengthValue | number | 长度 |
| widthValue | number | 宽度 |
| heightValue | number | 高度 |
| dimensionsUnit | string | 尺寸单位 |
| parentAsin | string | 父体ASIN |
| isParent | boolean | 是否为父体 |
| isVariant | boolean | 是否为变体 |
| isStandalone | boolean | 是否为独立产品 |
| isAvailable | boolean | 是否可购买 |
| buyBoxOwner | string | Buy Box 持有卖家名 |
| buyBoxOwnerSellerId | string | Buy Box 持有卖家ID |
| updatedAt | string | 数据更新时间 |
| feeBreakdown | object | 费用明细：`fbaFee`（FBA费用）、`referralFee`（推荐费）、`variableClosingFee`（可变结算费）、`totalFees`（总费用） |
| subcategoryRanks | array | 子分类BSR排名列表，每项含 `subcategory`、`rank`、`id` |
| type | string | 资源类型 |
| variants | array | 变体列表 |
| upcList | array | UPC码列表 |
| eanList | array | EAN码列表 |
| isbnList | array | ISBN码列表 |
| gtinList | array | GTIN码列表 |
| dateFirstAvailableIsEstimated | boolean | 上架日期是否为估算值 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `productDatabaseList` |
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
curl -X POST https://tool-gateway.linkfox.com/tool-jungle-scout/product-database/query \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "marketplace": "us",
    "includeKeywords": "yoga mat",
    "minSales": 300,
    "maxPrice": 50,
    "minRating": 4.0,
    "sort": "-sales",
    "needCount": 20
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-junglescout-product-database",
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
