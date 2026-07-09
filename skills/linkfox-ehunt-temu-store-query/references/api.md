# EHunt Temu 店铺查询 API 参考

## 调用说明

- **网关路由**：`POST ehunt/temu/storeQuery`（完整：`${LINKFOX_TOOL_GATEWAY}/ehunt/temu/storeQuery`）。
- **MCP 展示名**：Temu 店铺查询（确切工具名以当前环境下发的工具元数据为准）。
- **鉴权**：请求头 `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取。
- **说明**：参数与返回结构以当前网关返回为准；若上游返回 JSON 根级 `code` 字段，成功值（`200`）以实网为准。无数据时网关可能抛错。

## 请求参数（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string, maxLen=500 | 否 | 店铺名称或 ID 关键词 |
| siteId | string | 否 | 国家站点 ID，多个逗号分隔（如 211=美国，76=英国） |
| category | string | 否 | 后台类目 ID，多个逗号分隔 |
| isLocal | string | 否 | 是否半托管：0=全托管，1=半托管 |
| orderTotalMin | integer，≥0 | 否 | 总销量区间（起始） |
| orderTotalMax | integer，≥0 | 否 | 总销量区间（结束） |
| orderWeekMin | integer，≥0 | 否 | 周销量区间（起始） |
| orderWeekMax | integer，≥0 | 否 | 周销量区间（结束） |
| orderMonthMin | integer，≥0 | 否 | 月销量区间（起始） |
| orderMonthMax | integer，≥0 | 否 | 月销量区间（结束） |
| totalRevenueMin | number，≥0 | 否 | 总销售额区间（USD，起始） |
| totalRevenueMax | number，≥0 | 否 | 总销售额区间（USD，结束） |
| weekRevenueMin | number，≥0 | 否 | 周销售额区间（USD，起始） |
| weekRevenueMax | number，≥0 | 否 | 周销售额区间（USD，结束） |
| monthRevenueMin | number，≥0 | 否 | 月销售额区间（USD，起始） |
| monthRevenueMax | number，≥0 | 否 | 月销售额区间（USD，结束） |
| ratingMin | number (0~5) | 否 | 评分区间（起始） |
| ratingMax | number (0~5) | 否 | 评分区间（结束） |
| reviewNumMin | integer，≥0 | 否 | 评论数区间（起始） |
| reviewNumMax | integer，≥0 | 否 | 评论数区间（结束） |
| followerNumMin | integer，≥0 | 否 | 粉丝数区间（起始） |
| followerNumMax | integer，≥0 | 否 | 粉丝数区间（结束） |
| productNumMin | integer，≥0 | 否 | 商品数区间（起始） |
| productNumMax | integer，≥0 | 否 | 商品数区间（结束） |
| listedTimeBegin | string (YYYY-MM-DD) | 否 | 开店日期区间（起始） |
| listedTimeEnd | string (YYYY-MM-DD) | 否 | 开店日期区间（结束） |
| sortBy | string | 否 | 排序字段+方向：`order_week_count-0`（周销量降序，默认）、`order_count-0`、`total_revenue-0`、`rating-0` |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100 |

## 响应主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| storeNum | integer | 符合条件的店铺总数（上游 `store_num`） |
| stores | array | Temu 店铺列表 |
| columns | array | 渲染的列 |
| title | string | 标题（`Temu 店铺查询`） |
| sourceType | string | 来源类型：temu |
| sourceTool | string | 工具类型：ehunt |
| type | string | 渲染的样式：tableListWorkbenches |

### `stores[]` 元素

| 字段 | 上游别名 | 说明 |
|------|----------|------|
| storeId | `store_id` | 店铺 ID |
| siteId | `site_id` | 国家站点 ID |
| storeName | `store_name` | 店铺名称 |
| logoUrl | `logo_url` | 店铺 Logo URL |
| orderTotal | `order_total` | 总销量 |
| orderWeek | `order_week` | 周销量 |
| orderMonth | `order_month` | 月销量 |
| totalRevenue | `total_revenue` | 总销售额 |
| weekRevenue | `week_revenue` | 周销售额 |
| monthRevenue | `month_revenue` | 月销售额 |
| rating | - | 评分 |
| listedTime | `listed_time` | 开店时间 |
| reviewNum | `review_num` | 评论数 |
| followerNum | `follower_num` | 粉丝数 |
| productNum | `product_num` | 商品数 |
| categoriesCn | `categories_cn` | 中文类目列表 |
| categories | - | 英文类目列表 |
| isLocal | `is_local` | 是否半托管：0=全托管，1=半托管 |

## 脚本调试（可选）

仓库内提供 **`scripts/ehunt_temu_store_query.py`**（Python 3，仅标准库），向 LinkFox 工具网关 POST 与 MCP 入参一致的 JSON。

- **网关**：`https://tool-gateway.linkfox.com`（可用 `LINKFOX_TOOL_GATEWAY_BASE` 覆盖根 URL）
- **默认路径段**：`ehunt/temu/storeQuery`（可用 `LINKFOX_EHUNT_TEMU_STORE_QUERY_PATH` 覆盖，不含域名）
- **鉴权**：环境变量 `LINKFOXAGENT_API_KEY`（与其他 `linkfox-*` skill 相同；申请见 https://skill.linkfox.com/linkfoxskills/guide.htm ）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/ehunt_temu_store_query.py '{"searchKey": "home", "siteId": "211", "page": 1, "pageSize": 20}'
```

若返回 404，说明部署上该工具的 HTTP 路径与默认不一致，请用 `listEnabledTool` 或运维确认实际 path 后设置 `LINKFOX_EHUNT_TEMU_STORE_QUERY_PATH`。

## Feedback API

> 与上方工具网关 API 独立，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-ehunt-temu-store-query",
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
