# EHunt Temu 商品查询 API 参考

## 调用说明

- **网关路由**：`POST ehunt/temu/productQuery`（完整：`https://tool-gateway.linkfox.com/ehunt/temu/productQuery`）。
- **MCP 展示名**：Temu 商品查询（确切工具名以当前环境下发的工具元数据为准）。
- **鉴权**：请求头 `Authorization: <LINKFOXAGENT_API_KEY>`。
- **说明**：参数与返回结构以当前网关返回为准；若上游返回 JSON 根级 `code` 字段，成功值（`200`）以实网为准。无数据时网关可能抛错。

## 请求参数（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string, maxLen=500 | 否 | 关键词或商品 ID / 店铺 ID |
| categoryHome | string | 否 | 前台类目 ID |
| categoryBackend | string | 否 | 后台类目 ID |
| priceBegin | number，≥0 | 否 | 价格区间起始（USD），组成上游 `price` |
| priceEnd | number，≥0 | 否 | 价格区间结束（USD） |
| ratingBegin | number (0~5) | 否 | 评分区间起始，组成上游 `rating` |
| ratingEnd | number (0~5) | 否 | 评分区间结束 |
| reviewsBegin | integer，≥0 | 否 | 评论数区间起始，组成 `reviews` |
| reviewsEnd | integer，≥0 | 否 | 评论数区间结束 |
| salesTotalBegin | integer，≥0 | 否 | 总销量区间起始，组成 `sales_total` |
| salesTotalEnd | integer，≥0 | 否 | 总销量区间结束 |
| salesWeeklyBegin | integer，≥0 | 否 | 周销量区间起始，组成 `sales_weekly` |
| salesWeeklyEnd | integer，≥0 | 否 | 周销量区间结束 |
| salesDailyBegin | integer，≥0 | 否 | 日销量区间起始，组成 `sales_daily` |
| salesDailyEnd | integer，≥0 | 否 | 日销量区间结束 |
| publishTimeBegin | string (YYYY-MM-DD) | 否 | 上架日期区间起始，组成 `publish_time` |
| publishTimeEnd | string (YYYY-MM-DD) | 否 | 上架日期区间结束 |
| soldOut | integer | 否 | 是否下架：0=上架，1=下架 |
| isLocal | integer | 否 | 是否半托管：0=全托管，1=半托管 |
| region | string | 否 | 半托管地区，多个逗号分隔 |
| tags | string | 否 | 商品标签，多个逗号分隔 |
| customTags | string | 否 | 自定义标签，多个逗号分隔 |
| sortBy | string | 否 | 排序字段+方向：`order_week-0`（周销量降序，默认）、`price-0`、`order_total-0`、`rating-0` 等 |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100，建议不超过 50 |

## 响应主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| productNum | integer | 符合条件的商品总数（上游 `product_num`） |
| products | array | Temu 商品列表 |
| columns | array | 渲染的列 |
| title | string | 标题（`Temu 商品查询`） |
| sourceType | string | 来源类型：temu |
| sourceTool | string | 工具类型：ehunt |
| type | string | 渲染的样式：tableListWorkbenches |

### `products[]` 元素

| 字段 | 上游别名 | 说明 |
|------|----------|------|
| productId | `product_id` | 商品 ID |
| productName | `product_name` | 商品名（英文） |
| productNameCn | `product_name_cn` | 商品名（中文） |
| logoUrl | `logo_url` | 主图 URL |
| price | - | 价格 |
| orderTotal | `order_total` | 总销量 |
| orderWeek | `order_week` | 周销量 |
| orderDay | `order_day` | 日销量 |
| orderMonth | `order_month` | 月销量 |
| rating | - | 评分 |
| reviewNum | `review_num` | 评论数 |
| publishTime | `publish_time` | 上架时间 |
| soldOut | `sold_out` | 是否下架 |
| isLocal | `is_local` | 是否半托管：0=全托管，1=半托管 |
| localRegion | `local_region` | 半托管地区列表 |
| storeId | `store_id` | 店铺 ID |
| tags | - | 标签列表 |
| customTags | `custom_tags` | 自定义标签 |
| categoryHome | `category_home` | 前台类目 |
| categoryBackend | `category_backend` | 后台类目 |

## 脚本调试（可选）

仓库内提供 **`scripts/ehunt_temu_product_query.py`**（Python 3，仅标准库），向 LinkFox 工具网关 POST 与 MCP 入参一致的 JSON。

- **网关**：`https://tool-gateway.linkfox.com`（可用 `LINKFOX_TOOL_GATEWAY_BASE` 覆盖根 URL）
- **默认路径段**：`ehunt/temu/productQuery`（可用 `LINKFOX_EHUNT_TEMU_PRODUCT_QUERY_PATH` 覆盖，不含域名）
- **鉴权**：环境变量 `LINKFOXAGENT_API_KEY`（与其他 `linkfox-*` skill 相同；申请见 https://skill.linkfox.com/linkfoxskills/guide.htm ）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/ehunt_temu_product_query.py '{"searchKey": "kitchen", "page": 1, "pageSize": 20}'
```

若返回 404，说明部署上该工具的 HTTP 路径与默认不一致，请用 `listEnabledTool` 或运维确认实际 path 后设置 `LINKFOX_EHUNT_TEMU_PRODUCT_QUERY_PATH`。

## Feedback API

> 与上方工具网关 API 独立，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-ehunt-temu-product-query",
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
