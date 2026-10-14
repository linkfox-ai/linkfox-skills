# linkfox-junglescout-product-database

## 功能与适用范围

在 Amazon 产品数据库中按多条件筛选商品，条件包括关键词/ASIN、类目、价格、月销量、月收入、评论、评分、重量、BSR、LQS、卖家数量、卖家类型、尺寸层级、可购买状态和更新时间。适用于产品发现、细分市场初筛、低评论高销量信号和 Listing 优化机会识别。

它不提供商品详情页全文、评论文本、关键词历史趋势、广告执行或非 Amazon 平台数据；`approximate30Day*` 是估算值。

## MCP 调用

- 响应字段来源：`skills/linkfox-junglescout-product-database/references/api.md`。仅从该文件核对并恢复下方响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`tool-jungle-scout/product-database/query`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errorCode` / `code` 与消息字段。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

## 请求参数

`marketplace` 是唯一必填字段，取 `us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`，默认 `us`。

| 分组 | 参数 | 说明 |
|---|---|---|
| 关键词 | `includeKeywords`、`excludeKeywords` | 逗号分隔标题/ASIN包含或排除词；各最多 100 项，每项最长 50 字符 |
| 类目 | `categories` | 逗号分隔的目标站点标准主分类名；必须与站点分类文本匹配 |
| 价格/销量/收入 | `minPrice`、`maxPrice`、`minSales`、`maxSales`、`minRevenue`、`maxRevenue` | 数值上下限，可只给一端 |
| 评论/评分 | `minReviews`、`maxReviews`、`minRating`、`maxRating` | 评分范围 1.0–5.0 |
| 重量/排名/LQS | `minWeight`、`maxWeight`、`minRank`、`maxRank`、`minLqs`、`maxLqs` | 重量单位磅；LQS 范围 1–10 |
| 卖家/产品 | `minSellers`、`maxSellers`、`minNet`、`maxNet`、`sellerTypes`、`productTiers` | `sellerTypes` 为 `amz`/`fba`/`fbm`；`productTiers` 为 `oversize`/`standard` |
| 排除项 | `excludeTopBrands`、`excludeUnavailableProducts` | boolean |
| 日期/结果 | `minUpdatedAt`、`maxUpdatedAt`、`needCount`、`sort` | 日期 `YYYY-MM-DD`；`needCount` 为结果总数 |

`sort` 支持 `name`、`-name`、`category`、`-category`、`revenue`、`-revenue`、`sales`、`-sales`、`price`、`-price`、`rank`、`-rank`、`reviews`、`-reviews`、`lqs`、`-lqs`、`sellers`、`-sellers`；默认 `name`，前缀 `-` 表示降序。

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

### `productDatabaseList[].feeBreakdown` 对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `productDatabaseList[].feeBreakdown.fbaFee` | 来源未说明 | FBA 费用 |
| `productDatabaseList[].feeBreakdown.referralFee` | 来源未说明 | 推荐费 |
| `productDatabaseList[].feeBreakdown.variableClosingFee` | 来源未说明 | 可变结算费 |
| `productDatabaseList[].feeBreakdown.totalFees` | 来源未说明 | 总费用 |

### `productDatabaseList[].subcategoryRanks[]` 对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `productDatabaseList[].subcategoryRanks[].subcategory` | 来源未说明 | 来源未说明 |
| `productDatabaseList[].subcategoryRanks[].rank` | 来源未说明 | 来源未说明 |
| `productDatabaseList[].subcategoryRanks[].id` | 来源未说明 | 来源未说明 |

## MCP 参数示例

```json
{
  "toolName": "tool-jungle-scout/product-database/query",
  "arguments": {
    "marketplace": "us",
    "includeKeywords": "yoga mat",
    "minSales": 300,
    "maxPrice": 50,
    "minRating": 4,
    "sort": "-sales",
    "needCount": 20
  }
}
```

## 错误与展示

HTTP 200 后检查 `errcode`/`errorCode`；`200` 解析 `productDatabaseList`，`401`/授权错误和 `402`/余额错误读取 `references/onboarding.md`，其他错误根据 `errmsg` 修正类目、筛选范围或 `needCount`。错误示例：`{"errcode":401,"errmsg":"authorized error"}`。

业务成功需检查 `errcode` / `errorCode` / `code`，不得只依据代理层成功判断。

表格默认列标题、品牌、价格、月销量、月收入、BSR、评论、评分和 LQS；注明排序和返回数量。低评论高销量、高 LQS 只能标为候选信号。缺失、`0`、`-1` 或不可用字段按 N/A 处理，商品图展示时才使用 `imageUrl`。

## 反馈 API

反馈地址为 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，字段使用 `skillName: linkfox-wb-jungle-scout`、`sentiment`、`category` 和描述用户意图/实际结果的 `content`。`sentiment` 取 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 取 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。




