# Jungle Scout 产品数据库查询 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：产品数据库查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/tool-jungle-scout/product-database/query`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码，唯一必填参数。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`。用户未指定站点时由调用方填入 `us`，不能省略；其余字段均为可选筛选条件 |

#### 关键词筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| includeKeywords | string | 否 | 标题/ASIN包含关键词，逗号分隔，最多100项，每项最长50字符 |
| excludeKeywords | string | 否 | 标题/ASIN排除关键词，逗号分隔，最多100项，每项最长50字符 |

#### 品类筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| categories | string | 否 | 主分类名称，多个分类逗号分隔，须与对应站点的标准分类名完全匹配。美国站使用英文标准名称，例如 Appliances, Arts Crafts & Sewing, Automotive, Baby, Beauty & Personal Care, Books, CDs & Vinyl, Cell Phones & Accessories, Clothing Shoes & Jewelry, Collectibles & Fine Art, Computers, Digital Music, Electronics, Garden & Outdoor, Grocery & Gourmet Food, Handmade, Health Household & Baby Care, Home & Kitchen, Industrial & Scientific, Kindle Store, Kitchen & Dining, Movies & TV, Musical Instruments, Office Products, Pet Supplies, Sports & Outdoors, Tools & Home Improvement, Toys & Games, Video Games 等。其他站点（uk, de, fr, it, es, mx, jp, ca, in）有对应的本地分类名 |

#### 价格 / 销量 / 收入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minPrice | number | 否 | 最低价格 |
| maxPrice | number | 否 | 最高价格 |
| minSales | integer | 否 | 最低月销量 |
| maxSales | integer | 否 | 最高月销量 |
| minRevenue | number | 否 | 最低月收入 |
| maxRevenue | number | 否 | 最高月收入 |

#### 评论 / 评分

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minReviews | integer | 否 | 最低评论数 |
| maxReviews | integer | 否 | 最高评论数 |
| minRating | number | 否 | 最低评分（1.0-5.0） |
| maxRating | number | 否 | 最高评分（1.0-5.0） |

#### 重量 / 尺寸 / BSR

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minWeight | number | 否 | 最低重量（磅） |
| maxWeight | number | 否 | 最高重量（磅） |
| minRank | integer | 否 | 最低BSR排名 |
| maxRank | integer | 否 | 最高BSR排名 |
| minLqs | integer | 否 | 最低LQS评分（1-10） |
| maxLqs | integer | 否 | 最高LQS评分（1-10） |

#### 卖家 / 产品类型

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

#### 日期 / 分页 / 排序

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minUpdatedAt | string | 否 | 数据更新起始日期（YYYY-MM-DD） |
| maxUpdatedAt | string | 否 | 数据更新截止日期（YYYY-MM-DD） |
| needCount | integer | 否 | 需要返回的结果总数，后端自动跨页抓取；不设时使用服务默认数量，具体默认数量和每页条数不作预设，不自行添加分页参数 |
| sort | string | 否 | 排序字段。可选值：`name`, `-name`, `category`, `-category`, `revenue`, `-revenue`, `sales`, `-sales`, `price`, `-price`, `rank`, `-rank`, `reviews`, `-reviews`, `lqs`, `-lqs`, `sellers`, `-sellers`。前缀 `-` 表示降序。默认：`name` |

#### 站点映射

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

#### 参数约定与使用限制

- 各组 `min` / `max` 可以组合使用，也可以只传一端，例如 `minSales=300` 表示月销量至少 300。
- `minUpdatedAt` / `maxUpdatedAt` 表示数据更新时间，不是首次上架日期。新品需结合响应的 `dateFirstAvailable` 与 `dateFirstAvailableIsEstimated` 核对。
- 数据由 Jungle Scout 定期更新，并非实时数据。

#### 脚本兼容约定

业务入口为 `scripts/junglescout_product_database.py`，全部 LinkFox 商品查询由公共调用器 `scripts/call_api.py` 的 `run` 执行，业务入口不另建缓存层或 HTTP transport。

| 参数 / 约定 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 位置参数 | JSON | 是 | 以 JSON 位置参数传入上方请求参数 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应 |
| --no-cache | CLI flag | 否 | 跳过缓存读取和写入；不添加时使用 24 小时缓存 |
| 缓存键与位置 | 本地约定 | — | 对 `ensure_ascii=False, sort_keys=True` 的 JSON 计算 SHA-256，取前 16 位；保存到 `<cwd>/linkfox/.cache/linkfox-junglescout-product-database/linkfox-junglescout-product-database-<键>.json` |
| _cache.hit | boolean | 否 | 命中缓存时在返回响应中标记为 true；超过 24 小时或损坏的缓存不复用 |
| 输出目录检查 | 本地约定 | — | 在请求前检查当前目录下实际会话数据目录及元数据可写，不回退家目录或临时目录；拒绝解析到当前目录之外的输出路径 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| productDatabaseList | array | 产品数据列表 |

#### productDatabaseList 数组中每个对象

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

#### 费用明细与子分类排名

以下嵌套字段列出名称和含义，子字段类型以实际响应为准；按实际响应保留，不推断额外结构。

| 字段 | 类型 | 说明 |
|------|------|------|
| feeBreakdown.fbaFee | 未规定 | FBA 费用 |
| feeBreakdown.referralFee | 未规定 | 推荐费 |
| feeBreakdown.variableClosingFee | 未规定 | 可变结算费 |
| feeBreakdown.totalFees | 未规定 | 总费用 |
| subcategoryRanks[].subcategory | 未规定 | 子分类名称 |
| subcategoryRanks[].rank | 未规定 | 子分类 BSR 排名 |
| subcategoryRanks[].id | 未规定 | 子分类标识 |

#### 状态与消息字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码；示例为 401，按公共规则判断。 |
| errmsg | string | 网关消息或具体错误原因，例如 `authorized error`。 |
| errorCode | 未规定 | 响应中的业务状态字段；如实际返回则按返回值保留并结合消息说明，成功判断仍遵守公共规则。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应后读取 `productDatabaseList`；空列表表示本次未取得匹配商品，不能虚构候选或自动变更条件连续试探。
- 未列出额外的接口专属业务错误码。根据实际错误消息核对站点、分类或筛选条件；后续查询遵守 SKILL.md 的成本约束。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/tool-jungle-scout/product-database/query" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
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

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-junglescout-product-database",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
