# Shopify 商品查询 API 参考

## 调用说明

- **网关路由**：`POST ehunt/shopify/productQuery`（完整：`${LINKFOX_TOOL_GATEWAY}/ehunt/shopify/productQuery`）。
- **MCP 展示名**：Shopify 商品查询（确切工具名以当前环境下发的工具元数据为准）。
- **鉴权**：请求头 `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）。
- **说明**：参数与返回结构以当前网关返回为准；若上游返回 JSON 根级 `code` 字段，成功值（`200`）以实网为准。无数据时网关可能抛错。

## 请求参数（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string, maxLen=500 | 否 | 关键词或 Shopify 商品/店铺 URL |
| priceMin | number，≥0 | 否 | 价格区间（起始，USD），与 priceMax 组成上游 `price` |
| priceMax | number，≥0 | 否 | 价格区间（结束，USD） |
| salesWeeklyMin | integer，≥0 | 否 | 周销量区间（起始） |
| salesWeeklyMax | integer，≥0 | 否 | 周销量区间（结束） |
| publishedTimeBegin | string (YYYY-MM-DD) | 否 | 上架日期区间起始 |
| publishedTimeEnd | string (YYYY-MM-DD) | 否 | 上架日期区间结束 |
| facebookAd | integer | 否 | 是否有 Facebook 广告：1=有 |
| competitionMin | integer，≥0 | 否 | 竞争度（在售店铺数量）区间起始 |
| competitionMax | integer，≥0 | 否 | 竞争度（在售店铺数量）区间结束 |
| hasSupplier | integer | 否 | 是否有货源：1=有，0=无 |
| showDeleted | integer | 否 | 是否显示已下架商品：1=是，0=否 |
| country | string | 否 | 发货国家（两位国家代码，如 US） |
| sortBy | integer | 否 | 排序字段（默认 14=周销量降序，另含价格/广告数/竞争度/销售额等取值，见下方枚举） |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100，建议不超过 50 |

### `sortBy` 取值

上游排序枚举，默认 `14`（周销量降序）。常见取值含价格、上架时间、广告数、竞争度、周销量、周销售额、销售额增长率等的升/降序组合；具体编码以当前网关工具 schema 注释为准，未知时使用默认值即可。

## 响应主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| productNum | integer | 符合条件的商品总数（上游 `product_num`） |
| products | array | Shopify 商品列表 |
| columns | array | 渲染的列 |
| title | string | 标题（`Shopify 商品查询`） |
| sourceType | string | 来源类型：shopify |
| sourceTool | string | 工具类型：ehunt |
| type | string | 渲染的样式：tableListWorkbenches |

### `products[]` 元素

| 字段 | 上游别名 | 说明 |
|------|----------|------|
| productId | `product_id` | 商品 ID |
| title | - | 商品标题 |
| productLink | `product_link` | 商品链接 |
| previewImageUrl | `preview_image_url` | 主图 URL |
| country | - | 发货国家 |
| minPrice | `min_price` | 最低价 |
| maxPrice | `max_price` | 最高价 |
| storeId | `store_id` | 店铺 ID |
| shopId | `shop_id` | Shopify shop ID |
| storeLink | `store_link` | 店铺链接 |
| storeRank | `store_rank` | 店铺等级 |
| competitorCount | `competitor_count` | 竞争度（在售店铺数量） |
| facebookAdCount | `facebook_ad_count` | Facebook 广告数 |
| weekOrderCount | `week_order_count` | 周销量（字符串） |
| weekRevenueCount | `week_revenue_count` | 周销售额 |
| weekRevenueGrowth | `week_revenue_growth` | 周销售额增长率（%） |
| shelfTime | `shelf_time` | 上架时间 |
| isDeleted | `is_deleted` | 是否下架：0=上架，1=下架 |
| isFavourite | `is_favourite` | 是否已收藏 |

## 脚本调试（可选）

仓库内提供 **`scripts/shopify_product_query.py`**（Python 3，仅标准库），向 LinkFox 工具网关 POST 与 MCP 入参一致的 JSON。

- **网关**：`https://tool-gateway.linkfox.com`（可用 `LINKFOX_TOOL_GATEWAY_BASE` 覆盖根 URL）
- **默认路径段**：`ehunt/shopify/productQuery`（可用 `LINKFOX_EHUNT_SHOPIFY_PRODUCT_QUERY_PATH` 覆盖，不含域名）
- **鉴权**：环境变量 `LINKFOXAGENT_API_KEY`（与其他 `linkfox-*` skill 相同；如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/shopify_product_query.py '{"searchKey": "phone case", "country": "US", "page": 1, "pageSize": 20}'
```

若返回 404，说明部署上该工具的 HTTP 路径与默认不一致，请用 `listEnabledTool` 或运维确认实际 path 后设置 `LINKFOX_EHUNT_SHOPIFY_PRODUCT_QUERY_PATH`。

## Feedback API

> 与上方工具网关 API 独立，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-shopify-product-query",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: 使用本 skill YAML frontmatter 中的 `name`
- `sentiment`: `POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`: `BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content`: 简述用户意图、实际结果与问题或好评原因
