# `_ehunt_productQuery` API 参考

## 调用说明

- **工具名**：`_ehunt_productQuery`（LinkFox MCP，`serverName`：第三方数据服务）。
- **MCP 展示名**：Etsy商品查询。
- **说明**：参数与返回结构以当前网关返回为准；若上游返回 JSON 根级 `code` 字段，成功值以实网为准。

## 请求参数（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| beginFavorites | integer，≥0 | 否 | 收藏数（起始），与结束值共同组成上游 favorites |
| beginFavoritesWeekly | integer，≥0 | 否 | 周新增收藏数（起始），与结束值共同组成上游 favorites_weekly |
| beginPrice | number，≥0 | 否 | 价格（起始），与结束价共同组成上游 price（如 20~100）；仅填一侧时上游为 起始~ 或 ~结束 |
| beginReviews | integer，≥0 | 否 | 评论数（起始），与结束值共同组成上游 reviews |
| beginReviewsWeekly | integer，≥0 | 否 | 周新增评论数（起始），与结束值共同组成上游 reviews_weekly |
| beginSales | integer，≥0 | 否 | 总销量（起始），与结束值共同组成上游 sales |
| beginSalesWeekly | integer，≥0 | 否 | 周销量（起始），与结束值共同组成上游 sales_weekly（如 1~100） |
| category | string, maxLen=1000 | 否 | 商品分类 ID（单品类），详见 EHunt 商品分类接口 |
| country | string, maxLen=1000 | 否 | 发货国家 |
| currencyCode | string, default=USD, maxLen=1000 | 否 | 货币代码 |
| endFavorites | integer，≥0 | 否 | 收藏数（结束） |
| endFavoritesWeekly | integer，≥0 | 否 | 周新增收藏数（结束） |
| endPrice | number，≥0 | 否 | 价格（结束），与起始价共同组成上游 price |
| endReviews | integer，≥0 | 否 | 评论数（结束） |
| endReviewsWeekly | integer，≥0 | 否 | 周新增评论数（结束） |
| endSales | integer，≥0 | 否 | 总销量（结束） |
| endSalesWeekly | integer，≥0 | 否 | 周销量（结束） |
| isBestsell | integer | 否 | 是否畅销商品 |
| isPick | integer | 否 | 是否 Pick 商品 |
| isRaving | integer | 否 | 是否 Raving 商品 |
| listedTime | string, pattern | 否 | 上架时间不早于该日期（YYYY-MM-DD） |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100，建议不超过 50 |
| productType | string，须符合 schema 正则 | 否 | 商品类型，多个逗号分隔：1=手工 2=复古 3=数字 4=定制 9=其他 |
| searchKey | string, maxLen=500 | 否 | 搜索关键词或 Etsy 商品 URL |
| sortBy | integer (1~6) | 否 | 排序字段（对应上游 sort_by，取值 1~6） |
| sortDesc | integer | 否 | 排序方向（对应上游 `desc`）。schema 示例：降序 `1`、升序 `2`（与店铺查询的 `sortDesc` 编码不同） |
| status | integer | 否 | 商品状态（示例：1 上架，0 下架） |

## 响应主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数（本页返回条数，便于与列表长度对齐） |
| sourceTool | string | 工具类型：ehunt |
| sourceType | string | 来源类型：etsy |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token（按本页返回条数估算） |
| productNum | integer | 符合条件的商品总数（上游 product_num） |
| title | string | 标题 |
| type | string | 渲染的样式 |
| products | array | Etsy 商品列表 |

### `products[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| category | string | 类目名称 |
| favorites | integer | 收藏数 |
| favoritesWeekly | integer | 周新增收藏数 |
| imageUrl | string | 主图 URL |
| isBestsell | integer | 是否畅销：1=是 |
| isPick | integer | 是否 Pick：1=是 |
| isRaving | integer | 是否 Raving：1=是 |
| price | number | 价格 |
| productUrl | string | 商品链接 |
| releaseTime | string | 上架/发布时间 |
| reviews | integer | 评论数 |
| reviewsWeekly | integer | 周新增评论数 |
| salesTotal | integer | 总销量 |
| salesWeekly | integer | 周销量 |
| shipsFrom | string | 发货国家 |
| status | integer | 商品状态：1=上架，0=下架 |
| storeName | string | 店铺名称 |
| tags | string | 标签 |
| title | string | 商品标题 |

## 脚本调试（可选）

仓库内提供 **`scripts/ehunt_etsy_product_query.py`**（Python 3，仅标准库）。

- **默认路径段**：`ehunt/etsy/productQuery`（可用 `LINKFOX_EHUNT_PRODUCT_QUERY_PATH` 覆盖）
- **网关**：`https://tool-gateway.linkfox.com`（可用 `LINKFOX_TOOL_GATEWAY_BASE` 覆盖）；**鉴权**：`LINKFOXAGENT_API_KEY`（申请见 https://skill.linkfox.com/linkfoxskills/guide.htm ）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/ehunt_etsy_product_query.py '{"searchKey": "poster", "currencyCode": "USD", "page": 1, "pageSize": 20}'
```
