# Shopify 店铺查询 API 参考

## 调用说明

- **网关路由**：`POST ehunt/shopify/storeQuery`（完整：`${LINKFOX_TOOL_GATEWAY}/ehunt/shopify/storeQuery`）。
- **MCP 展示名**：Shopify 店铺查询（确切工具名以当前环境下发的工具元数据为准）。
- **鉴权**：请求头 `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）。
- **说明**：参数与返回结构以当前网关返回为准；若上游返回 JSON 根级 `code` 字段，成功值（`200`）以实网为准。无数据时网关可能抛错。

## 请求参数（JSON）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string, maxLen=500 | 否 | 店铺名称或域名关键词 |
| country | string | 否 | 国家代码（如 US、CN） |
| year | integer | 否 | 店铺创建年份：1=最近 1 年，2=1~2 年，3=2~3 年，4=3 年以上 |
| productNumMin | integer，≥0 | 否 | 产品数区间（起始） |
| productNumMax | integer，≥0 | 否 | 产品数区间（结束） |
| advertiseCountMin | integer，≥0 | 否 | 广告数区间（起始） |
| advertiseCountMax | integer，≥0 | 否 | 广告数区间（结束） |
| monthlyVisitMin | integer，≥0 | 否 | 月访问量区间（起始） |
| monthlyVisitMax | integer，≥0 | 否 | 月访问量区间（结束） |
| monthOrderMin | integer，≥0 | 否 | 月订单量区间（起始） |
| monthOrderMax | integer，≥0 | 否 | 月订单量区间（结束） |
| sortBy | integer | 否 | 排序字段：0=产品数,1=类目数,2=月访问量,3=FB 粉丝,4=Ins 粉丝,5=广告数,6=相关度,7=月订单数（默认） |
| orderBy | string | 否 | 排序方向：`desc`（默认）/`asc` |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100 |

## 响应主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| storeNum | integer | 符合条件的店铺总数（上游 `store_num`） |
| stores | array | Shopify 店铺列表 |
| columns | array | 渲染的列 |
| title | string | 标题（`Shopify 店铺查询`） |
| sourceType | string | 来源类型：shopify |
| sourceTool | string | 工具类型：ehunt |
| type | string | 渲染的样式：tableListWorkbenches |

### `stores[]` 元素

| 字段 | 上游别名 | 说明 |
|------|----------|------|
| storeId | `store_id` | 店铺 ID |
| shopId | `shop_id` | Shopify shop ID |
| storeName | `store_name` | 店铺名称 |
| storeDomain | `store_domain` | 店铺域名 |
| storeLink | `store_link` | 店铺链接 |
| country | - | 国家 |
| createdTime | `created_time` | 创建时间 |
| productNum | `product_num` | 产品数 |
| categoryNum | `category_num` | 类目数 |
| categories | - | 类目列表（元素含 `id`、`name`） |
| monthlyVisit | `monthly_visit` | 月访问量（格式化） |
| monthOrderNum | `month_order_num` | 月订单量（格式化） |
| fbFollowers | `fb_followers` | Facebook 粉丝数 |
| insFollowers | `ins_followers` | Instagram 粉丝数 |
| advertiseCount | `advertise_count` | 广告数 |
| adLink | `ad_link` | 广告库链接 |
| email | - | 联系邮箱 |
| facebookUrl | `facebook_url` | Facebook 主页 |
| instagramUrl | `instagram_url` | Instagram 主页 |
| socialLinks | `social_links` | 社媒链接（Map） |
| globalRank | `global_rank` | 全球排名 |
| logo | - | 店铺 Logo URL |
| availableStatus | `available_status` | 是否活跃：1=活跃 |

## 脚本调试（可选）

仓库内提供 **`scripts/shopify_store_query.py`**（Python 3，仅标准库），向 LinkFox 工具网关 POST 与 MCP 入参一致的 JSON。

- **网关**：`https://tool-gateway.linkfox.com`（可用 `LINKFOX_TOOL_GATEWAY_BASE` 覆盖根 URL）
- **默认路径段**：`ehunt/shopify/storeQuery`（可用 `LINKFOX_EHUNT_SHOPIFY_STORE_QUERY_PATH` 覆盖，不含域名）
- **鉴权**：环境变量 `LINKFOXAGENT_API_KEY`（与其他 `linkfox-*` skill 相同；如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"
python scripts/shopify_store_query.py '{"searchKey": "fashion", "country": "US", "page": 1, "pageSize": 20}'
```

若返回 404，说明部署上该工具的 HTTP 路径与默认不一致，请用 `listEnabledTool` 或运维确认实际 path 后设置 `LINKFOX_EHUNT_SHOPIFY_STORE_QUERY_PATH`。

## Feedback API

> 与上方工具网关 API 独立，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-shopify-store-query",
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
