# linkfox-temu-store-query 子能力归档

以下内容保留该子能力的执行边界、调用规则、参数、响应字段、错误处理和认证引导，执行时以本档案及主 SKILL.md 的路由为准。

## 能力说明与执行规则

---
name: linkfox-temu-store-query
description: 按多维度筛选 Temu 店铺（店名/ID、国家站点、后台类目、全托管/半托管、总/周/月销量与销售额、评分、评论、粉丝、商品数、开店时间等）。当用户提到 Temu 店铺、Temu 店铺分析、Temu seller、Temu 店铺排行、Temu 半托管店铺、Temu 销售额、temu stores、Temu store query 时触发。即使用户未提及工具名，只要在 Temu 上找店铺、筛店铺数据或分析店铺表现，也应触发此技能。
---

# Temu 店铺查询

在具备 LinkFox「第三方数据服务」MCP 时，对应网关路由 **`ehunt/temu/storeQuery`** 调用（MCP 展示名：**Temu 店铺查询**，确切工具名以当前环境下发的工具元数据为准）。鉴权与上游路由由网关处理；若响应含根级 `code` 字段，是否成功以实网为准。

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100。
- **区间入参**：`*Min` / `*Max` 成对出现（总/周/月销量、总/周/月销售额、评分、评论、粉丝、商品数），组成上游区间。
- **站点**：`siteId` 国家站点 ID，多个逗号分隔（如 `211`=美国、`76`=英国）。
- **类目**：`category` 后台类目 ID，多个逗号分隔。
- **托管模式**：`isLocal`（0=全托管，1=半托管，字符串）。
- **开店时间**：`listedTimeBegin` / `listedTimeEnd`（YYYY-MM-DD）。
- **排序**：`sortBy` 为「字段-方向」字符串，如 `order_week_count-0`（周销量降序，默认）、`order_count-0`、`total_revenue-0`、`rating-0`。

## MCP 入口

本子能力仅通过 `LinkFox` 的 `proxy_call` 执行，精确 `toolName` 见下方【MCP 调用】。

## 参考

入参/出参表见本文件下方的“API 参考”。

## 解决认证和积分问题
发生以下异常情况时，采用 references/onboarding.md 引导解决问题：

### 异常情况
- **MCP 连接或下游响应 401/402**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

## 积分消耗规则

按动态规则计费：消耗积分 = 店铺数量 × 1.8。按本页返回条数计费；翻到下一页，本质上是再发一次请求，再按下一页返回条数重新计算。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

## API 参考

# Temu 店铺查询 API 参考

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`ehunt/temu/storeQuery`
- **arguments**：直接使用下表请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；配置和 `arguments` 不得加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text JSON 只解析一次，最后检查下游 `errcode`、`code`、`errmsg`、`msg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；相同 `toolName + arguments` 不得重复收费调用，失败、空结果或返回不理想时不得自动重试。

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

来源未提供这些字段的类型，统一标为“来源未说明”；上游别名按来源保留。

| 字段路径 | 类型 | 上游别名 | 说明 |
|------|------|----------|------|
| stores[].storeId | 来源未说明 | `store_id` | 店铺 ID |
| stores[].siteId | 来源未说明 | `site_id` | 国家站点 ID |
| stores[].storeName | 来源未说明 | `store_name` | 店铺名称 |
| stores[].logoUrl | 来源未说明 | `logo_url` | 店铺 Logo URL |
| stores[].orderTotal | 来源未说明 | `order_total` | 总销量 |
| stores[].orderWeek | 来源未说明 | `order_week` | 周销量 |
| stores[].orderMonth | 来源未说明 | `order_month` | 月销量 |
| stores[].totalRevenue | 来源未说明 | `total_revenue` | 总销售额 |
| stores[].weekRevenue | 来源未说明 | `week_revenue` | 周销售额 |
| stores[].monthRevenue | 来源未说明 | `month_revenue` | 月销售额 |
| stores[].rating | 来源未说明 | - | 评分 |
| stores[].listedTime | 来源未说明 | `listed_time` | 开店时间 |
| stores[].reviewNum | 来源未说明 | `review_num` | 评论数 |
| stores[].followerNum | 来源未说明 | `follower_num` | 粉丝数 |
| stores[].productNum | 来源未说明 | `product_num` | 商品数 |
| stores[].categoriesCn | 来源未说明 | `categories_cn` | 中文类目列表 |
| stores[].categoriesCn[] | 来源未说明 | - | 中文类目列表元素 |
| stores[].categories | 来源未说明 | - | 英文类目列表 |
| stores[].categories[] | 来源未说明 | - | 英文类目列表元素 |
| stores[].isLocal | 来源未说明 | `is_local` | 是否半托管：0=全托管，1=半托管 |

| 字段路径 | 类型 | 说明 |
|------|------|------|
| columns[] | 来源未说明 | 渲染列元素；来源未说明内部字段 |

## MCP 调用示例

```json
{
  "toolName": "ehunt/temu/storeQuery",
  "arguments": {
    "searchKey": "home",
    "siteId": "211",
    "page": 1,
    "pageSize": 20
  }
}
```

## Feedback API

> 与上方工具网关 API 独立，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-temu-store-query",
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

## 认证与积分引导

# 解决认证和积分问题

读取 `references/onboarding.md` 并分层处理 MCP 连接、代理层和下游业务错误。WorkBuddy 自动注入 Authorization；不得要求用户提供凭证。下游 402 引导访问 `https://agent.linkfox.com/`，不得自动选套餐、下单、支付或轮询；403 不归入认证或计费错误。
