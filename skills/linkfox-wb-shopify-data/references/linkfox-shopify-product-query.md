# Shopify 商品查询 reference

## 能力说明与边界

按关键词或 Shopify 商品/店铺 URL、价格、周销量、上架时间、Facebook 广告、竞争度、货源、下架状态、发货国家和排序筛选商品。

- `page` 从 1 起；`pageSize` 默认 20、最大 100，建议不超过 50。
- `*Min` / `*Max` 组成区间，只填一侧时由上游解释为开放区间。
- `sortBy` 默认 `14`（周销量降序）；其他编码未知时不得猜测。
- `facebookAd`、`hasSupplier`、`showDeleted` 为整数开关；`country` 使用两位国家代码。
- 返回当前市场快照，不提供后台操作、历史趋势或销量保证；失败或空结果不得自动改词、翻页或改变参数。

### 计费

动态计费为“本页返回商品数 × 1.8 积分”。翻页会重新计费，实际以响应中的消耗和当前计费规则为准；高频或大页查询先由用户决定。

## MCP 调用

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- `toolName`：`ehunt/shopify/productQuery`
- `arguments`：直接使用下述请求对象，不增加包装层。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 禁止 HTTP fallback。同一任务内相同 `toolName + arguments` 只调用一次；收费调用失败、空结果或不理想时不得自动重试。
- 先检查 MCP 层，再检查代理层；代理结果中的 text 是 JSON 字符串时只解析一次，最后检查下游业务状态。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `searchKey` | string, maxLen=500 | 否 | 关键词或 Shopify 商品/店铺 URL |
| `priceMin` | number，≥0 | 否 | 价格区间起始，USD；与 `priceMax` 组成上游 `price` |
| `priceMax` | number，≥0 | 否 | 价格区间结束，USD |
| `salesWeeklyMin` | integer，≥0 | 否 | 周销量区间起始 |
| `salesWeeklyMax` | integer，≥0 | 否 | 周销量区间结束 |
| `publishedTimeBegin` | string (`YYYY-MM-DD`) | 否 | 上架日期区间起始 |
| `publishedTimeEnd` | string (`YYYY-MM-DD`) | 否 | 上架日期区间结束 |
| `facebookAd` | integer | 否 | 是否有 Facebook 广告：`1=有` |
| `competitionMin` | integer，≥0 | 否 | 竞争度（在售店铺数量）区间起始 |
| `competitionMax` | integer，≥0 | 否 | 竞争度区间结束 |
| `hasSupplier` | integer | 否 | 是否有货源：`1=有`、`0=无` |
| `showDeleted` | integer | 否 | 是否显示已下架商品：`1=是`、`0=否` |
| `country` | string | 否 | 发货国家，两位国家代码如 `US` |
| `sortBy` | integer | 否 | 默认 `14=周销量降序`；其他价格、广告数、竞争度、销售额编码以工具 schema 为准 |
| `page` | integer，≥1，默认 1 | 否 | 页码，从 1 开始 |
| `pageSize` | integer，1~100，默认 20 | 否 | 每页条数，最大 100，建议不超过 50 |

上游排序还包含价格、上架时间、广告数、竞争度、周销量、周销售额和增长率的升降序组合；来源未列出具体编码，未知时使用默认 14。

## 完整 MCP 示例

```json
{
  "toolName": "ehunt/shopify/productQuery",
  "arguments": {
    "searchKey": "phone case",
    "country": "US",
    "sortBy": 14,
    "page": 1,
    "pageSize": 20
  }
}
```

## 响应字段

字段定义仅来自 `skills/linkfox-shopify-product-query/references/api.md` 的响应部分。来源未给 `products[]` 字段类型列，除明确说明为字符串的字段外均标记为“来源未说明”。

| 字段路径 | 类型 | 上游别名 | 说明 |
|---|---|---|---|
| `total` | integer | — | 本页返回条数 |
| `productNum` | integer | `product_num` | 符合条件的商品总数（上游 `product_num`） |
| `products` | array | — | Shopify 商品列表 |
| `products[]` | object | — | Shopify 商品列表元素；来源以元素字段表定义为对象 |
| `columns` | array | — | 渲染的列 |
| `columns[]` | 来源未说明 | — | 渲染列元素；来源未说明元素结构 |
| `title` | string | — | 标题（`Shopify 商品查询`） |
| `sourceType` | string | — | 来源类型：shopify |
| `sourceTool` | string | — | 工具类型：ehunt |
| `type` | string | — | 渲染的样式：tableListWorkbenches |
| `products[].productId` | 来源未说明 | `product_id` | 商品 ID |
| `products[].title` | 来源未说明 | - | 商品标题 |
| `products[].productLink` | 来源未说明 | `product_link` | 商品链接 |
| `products[].previewImageUrl` | 来源未说明 | `preview_image_url` | 主图 URL |
| `products[].country` | 来源未说明 | - | 发货国家 |
| `products[].minPrice` | 来源未说明 | `min_price` | 最低价 |
| `products[].maxPrice` | 来源未说明 | `max_price` | 最高价 |
| `products[].storeId` | 来源未说明 | `store_id` | 店铺 ID |
| `products[].shopId` | 来源未说明 | `shop_id` | Shopify shop ID |
| `products[].storeLink` | 来源未说明 | `store_link` | 店铺链接 |
| `products[].storeRank` | 来源未说明 | `store_rank` | 店铺等级 |
| `products[].competitorCount` | 来源未说明 | `competitor_count` | 竞争度（在售店铺数量） |
| `products[].facebookAdCount` | 来源未说明 | `facebook_ad_count` | Facebook 广告数 |
| `products[].weekOrderCount` | string | `week_order_count` | 周销量（字符串） |
| `products[].weekRevenueCount` | 来源未说明 | `week_revenue_count` | 周销售额 |
| `products[].weekRevenueGrowth` | 来源未说明 | `week_revenue_growth` | 周销售额增长率（%） |
| `products[].shelfTime` | 来源未说明 | `shelf_time` | 上架时间 |
| `products[].isDeleted` | 来源未说明 | `is_deleted` | 是否下架：0=上架，1=下架 |
| `products[].isFavourite` | 来源未说明 | `is_favourite` | 是否已收藏 |

## 错误与展示

下游根级 `code=200` 可表示成功，具体以实际响应为准；错误时读取业务状态和消息。401、402、403 分别按 `onboarding.md` 的授权、计费和权限规则处理。无数据或其他异常时停止，不自动重试。

展示查询条件、本页条数、`productNum`、分页和消耗；商品优先展示标题、链接、主图、国家、价格、周销量/销售额、竞争度、广告数、上架时间和下架状态。格式化值按原样保留，缺失字段标记 N/A。

## Feedback API

反馈接口与商品查询 MCP 独立：`POST https://skill-api.linkfox.com/api/v1/public/feedback`。使用统一 `skillName=linkfox-wb-shopify-data`；`sentiment` 为 `POSITIVE`/`NEUTRAL`/`NEGATIVE`，`category` 为 `BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`，`content` 简述意图、结果和原因。反馈不得中断当前流程或包含敏感信息。
