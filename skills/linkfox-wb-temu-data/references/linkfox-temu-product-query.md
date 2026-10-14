# linkfox-temu-product-query 子能力归档

以下内容保留该子能力的执行边界、调用规则、参数、响应字段、错误处理和认证引导，执行时以本档案及主 SKILL.md 的路由为准。

## 能力说明与执行规则

---
name: linkfox-temu-product-query
description: 按多维度筛选 Temu 商品（关键词/商品 ID/店铺 ID、前后台类目、价格、评分、评论、总/周/日销量、上架时间、全托管/半托管、半托管地区、标签等）。当用户提到 Temu 商品、Temu 选品、拼多多跨境、Temu 爆款、Temu 半托管、全托管商品、Temu product query、temu items 时触发。即使用户未提及工具名，只要在 Temu 上搜商品、看销量/评分/价格或筛品，也应触发此技能。
---

# Temu 商品查询

## 要点

- **分页**：`page` 从 1 起；`pageSize` 默认 20、最大 100（建议 ≤50）。
- **区间入参**：`*Begin` / `*End` 成对出现（价格、评分、评论、总/周/日销量、上架时间），组成上游区间。
- **类目**：`categoryHome` 前台类目 ID、`categoryBackend` 后台类目 ID；可先用 Temu 品类检索拿到 id。
- **托管模式**：`isLocal`（0=全托管，1=半托管）；半托管可用 `region` 限定地区（多个逗号分隔）。
- **上下架**：`soldOut`（0=上架，1=下架）。
- **标签**：`tags` / `customTags` 多个用逗号分隔。
- **排序**：`sortBy` 为「字段-方向」字符串，如 `order_week-0`（周销量降序，默认）、`price-0`、`order_total-0`、`rating-0`。

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

按动态规则计费：消耗积分 = 产品数量 × 1.8。按本页返回条数计费；翻到下一页，本质上是再发一次请求，再按下一页返回条数重新计算。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

## API 参考

# Temu 商品查询 API 参考

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`ehunt/temu/productQuery`
- **arguments**：直接使用下表请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；配置和 `arguments` 不得加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text JSON 只解析一次，最后检查下游 `errcode`、`code`、`errmsg`、`msg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；相同 `toolName + arguments` 不得重复收费调用，失败、空结果或返回不理想时不得自动重试。

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

来源未提供这些字段的类型，统一标为“来源未说明”；上游别名按来源保留。

| 字段路径 | 类型 | 上游别名 | 说明 |
|------|------|----------|------|
| products[].productId | 来源未说明 | `product_id` | 商品 ID |
| products[].productName | 来源未说明 | `product_name` | 商品名（英文） |
| products[].productNameCn | 来源未说明 | `product_name_cn` | 商品名（中文） |
| products[].logoUrl | 来源未说明 | `logo_url` | 主图 URL |
| products[].price | 来源未说明 | - | 价格 |
| products[].orderTotal | 来源未说明 | `order_total` | 总销量 |
| products[].orderWeek | 来源未说明 | `order_week` | 周销量 |
| products[].orderDay | 来源未说明 | `order_day` | 日销量 |
| products[].orderMonth | 来源未说明 | `order_month` | 月销量 |
| products[].rating | 来源未说明 | - | 评分 |
| products[].reviewNum | 来源未说明 | `review_num` | 评论数 |
| products[].publishTime | 来源未说明 | `publish_time` | 上架时间 |
| products[].soldOut | 来源未说明 | `sold_out` | 是否下架 |
| products[].isLocal | 来源未说明 | `is_local` | 是否半托管：0=全托管，1=半托管 |
| products[].localRegion | 来源未说明 | `local_region` | 半托管地区列表 |
| products[].localRegion[] | 来源未说明 | - | 半托管地区列表元素 |
| products[].storeId | 来源未说明 | `store_id` | 店铺 ID |
| products[].tags | 来源未说明 | - | 标签列表 |
| products[].tags[] | 来源未说明 | - | 标签列表元素 |
| products[].customTags | 来源未说明 | `custom_tags` | 自定义标签 |
| products[].categoryHome | 来源未说明 | `category_home` | 前台类目 |
| products[].categoryBackend | 来源未说明 | `category_backend` | 后台类目 |

| 字段路径 | 类型 | 说明 |
|------|------|------|
| columns[] | 来源未说明 | 渲染列元素；来源未说明内部字段 |

## MCP 调用示例

```json
{
  "toolName": "ehunt/temu/productQuery",
  "arguments": {
    "searchKey": "kitchen",
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
  "skillName": "linkfox-temu-product-query",
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
