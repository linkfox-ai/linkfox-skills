# `_ehunt_storeQuery` API 参考

## 调用说明

- **工具名**：`_ehunt_storeQuery`（LinkFox MCP，`serverName`：第三方数据服务）。
- **MCP 展示名**：Etsy店铺查询。
- **说明**：参数与返回结构以当前网关返回为准；若上游返回 JSON 根级 `code` 字段，成功值以实网为准。

## 请求参数（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| beginFavorites | integer，≥0 | 否 | 店铺收藏数（起始），与结束值组成上游 favorites |
| beginFavoritesWeekly | integer，≥0 | 否 | 店铺周新增收藏（起始），与结束值组成上游 favorites_weekly |
| beginReviews | integer，≥0 | 否 | 店铺评论数（起始），与结束值组成上游 reviews |
| beginReviewsWeekly | integer，≥0 | 否 | 店铺周新增评论（起始），与结束值组成上游 reviews_weekly |
| beginSales | integer，≥0 | 否 | 店铺总销量（起始），与结束值组成上游 sales |
| beginSalesWeekly | integer，≥0 | 否 | 店铺周销量（起始），与结束值组成上游 sales_weekly，如 10,100 |
| beginStoreOpenedAt | string, pattern | 否 | 店铺开店时间区间起始（YYYY-MM-DD），与结束日期组成上游 start_at，如 2020-01-01~2023-01-01 |
| category | string, maxLen=1000 | 否 | 店铺主营分类 |
| country | string, maxLen=1000 | 否 | 店铺所在国家 |
| endFavorites | integer，≥0 | 否 | 店铺收藏数（结束） |
| endFavoritesWeekly | integer，≥0 | 否 | 店铺周新增收藏（结束） |
| endReviews | integer，≥0 | 否 | 店铺评论数（结束） |
| endReviewsWeekly | integer，≥0 | 否 | 店铺周新增评论（结束） |
| endSales | integer，≥0 | 否 | 店铺总销量（结束） |
| endSalesWeekly | integer，≥0 | 否 | 店铺周销量（结束） |
| endStoreOpenedAt | string, pattern | 否 | 店铺开店时间区间结束（YYYY-MM-DD） |
| isRaving | integer | 否 | 是否 Raving 店铺：1=是 |
| isStar | integer | 否 | 是否星标店铺：1=是 |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100 |
| searchKey | string, maxLen=500 | 否 | 搜索关键词或店铺名称、店铺 URL |
| sortBy | integer (8~11) | 否 | 排序字段 sort_by：8=总销量，9=周销量，10=评论数，11=收藏数 |
| sortDesc | integer | 否 | 排序方向（对应上游 desc）：1=降序，0=升序 |
| status | integer | 否 | 店铺状态：1=活跃，0=非活跃 |

## 响应主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数（本页返回条数） |
| sourceTool | string | 工具类型：ehunt |
| sourceType | string | 来源类型：etsy |
| stores | array | 店铺列表 |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token（按本页返回条数估算） |
| storeNum | integer | 符合条件的店铺总数（上游 store_num） |
| title | string | 标题 |
| type | string | 渲染的样式 |

### `stores[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| category | array | 主营类目列表 |
| country | array | 国家/地区列表 |
| favorites | integer | 收藏数 |
| favoritesWeekly | integer | 周新增收藏数 |
| isRaving | integer | 是否 Raving：1=是 |
| isStar | integer | 是否星标：1=是 |
| logoUrl | string | 店铺头像 URL |
| productCount | integer | 店铺商品数量 |
| rating | number | 评分 |
| reviews | integer | 评论数 |
| reviewsWeekly | integer | 周新增评论数 |
| salesTotal | integer | 总销量 |
| salesWeekly | integer | 周销量 |
| shopWebsite | string | 店铺官网/外链 |
| startAt | string | 开店日期 |
| status | integer | 店铺状态：1=活跃，0=非活跃 |
| storeId | string | 店铺 ID |
| storeName | string | 店铺名称 |
| storeUrl | string | 店铺链接 |

## 脚本调试（可选）

仓库内提供 **`scripts/ehunt_etsy_store_query.py`**（Python 3，仅标准库），向 LinkFox 工具网关 POST 与 MCP 入参一致的 JSON。

- **网关**：`https://tool-gateway.linkfox.com`（可用 `LINKFOX_TOOL_GATEWAY_BASE` 覆盖根 URL）
- **默认路径段**：`ehunt/etsy/storeQuery`（可用 `LINKFOX_EHUNT_STORE_QUERY_PATH` 覆盖，不含域名）
- **鉴权**：环境变量 `LINKFOXAGENT_API_KEY`（与其他 `linkfox-*` skill 相同；申请见 https://skill.linkfox.com/linkfoxskills/guide.htm ）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/ehunt_etsy_store_query.py '{"searchKey": "ceramic", "country": "US", "page": 1, "pageSize": 20}'
```

若返回 404，说明部署上该工具的 HTTP 路径与默认不一致，请用 `listEnabledTool` 或运维确认实际 path 后设置 `LINKFOX_EHUNT_STORE_QUERY_PATH`。
