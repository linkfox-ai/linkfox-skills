# 沃尔玛商品列表搜索（linkfox-walmart-search）

## 功能说明

按关键词或类目检索 Walmart.com 当前商品 listing，支持价格区间、排序、分页、facet、门店、设备和 NextDay 条件。结果适合候选发现、当前价格/评分/卖家横向比较和库存/配送字段核验。至少提供 `keyword` 或 `categoryId` 一个；不提供评论正文、历史价格或历史销量。

## 能力边界

### ✅ 能力范围

- 关键词搜索、类目浏览和关键词+类目组合查询。
- `best_seller`、`best_match`、`price_low`、`price_high` 排序，价格上下限和 `page` 分页。
- 按 `storeId`、`device`、`facet`、`nextDayEnabled` 缩小当前结果。
- 返回商品标题、描述、价格、卖家、评分、评价数量、图片/商品页链接、赞助标记、库存、运费、配送和变体字段。

### ❌ 边界与限制

- 至少提供 `keyword` 或 `categoryId`；关键词最大 1024 字符，页码为 1–100。
- 这是当前 listing 查询，不是历史价格跟踪、真实卖家后台销量、店铺经营报表或市场规模测算。
- 只返回评分/评价数量，不返回评论正文，不支持评论情感分析。
- 不处理卖家账号、广告管理、订单、采购、物流履约或 Walmart Affiliate/API Key 管理。
- 结果只用于客观数据分析，不构成销售、投资或法律结论。

## MCP 调用

- **MCP server**：`LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`）。
- **唯一工具**：`proxy_call`。
- **原 endpoint**：`/walmart/search`。
- **精确 `toolName`**：`walmart/search`，区分大小写。
- **`arguments`**：直接使用下方请求参数对象，不增加 `body`、`params`、`data`、`headers` 或第二层 `arguments`。Authorization 由 WorkBuddy 自动注入，不得传 API Key、token、JWT、手机号或其他凭证。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理层错误；代理成功后读取 text/structured content。text 为 JSON 字符串时只解析一次，再读取下游 `errorCode`/`errcode`、`errmsg` 和业务字段。
- **计费**：每次业务调用都可能消耗积分，以响应 `costToken` 为准；MCP 外层对象不是下游业务响应，不得把代理状态当作业务成功。
- **禁止回退与去重**：不得使用 curl、`urllib`、`requests`、`httpx` 直连网关；MCP 缺失时停止。同一任务内相同 `toolName + arguments` 不得重复调用；失败、空结果或结果不理想时不得自动换词、翻页、扩大范围或重试收费调用。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keyword` | string | 否* | 搜索关键词，最多 1024 字符；与 `categoryId` 至少一个 |
| `categoryId` | string | 否* | 类目 ID；与 `keyword` 至少一个，`0` 表示所有部门 |
| `sort` | string | 否 | `price_low`、`price_high`、`best_seller`、`best_match` |
| `page` | integer | 否 | 页码，默认 1，范围 1–100 |
| `minPrice` | number | 否 | 最低价格 |
| `maxPrice` | number | 否 | 最高价格 |
| `spelling` | boolean | 否 | 是否启用拼写修正，默认 `true` |
| `softSort` | boolean | 否 | 是否按相关性排序，默认 `true`；`false` 禁用 |
| `storeId` | string | 否 | 指定 Walmart 门店 |
| `device` | string | 否 | `desktop`、`tablet` 或 `mobile`，默认 `desktop` |
| `facet` | string | 否 | `key:value` 过滤条件，多个条件用 `\|\|` 分隔 |
| `nextDayEnabled` | boolean | 否 | 仅显示 NextDay 配送结果，默认 `false` |
| `jsonRestrictor` | string | 否 | 限制返回的 JSON 字段 |

## 响应结构

成功响应字段仅依据 `skills/linkfox-walmart-search/references/api.md`：

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 记录数 |
| `products` | array | 产品列表（见下方产品对象） |
| `columns` | array | 渲染的列；来源未说明数组元素字段 |
| `type` | string | 渲染的样式 |
| `costToken` | integer | 消耗 token |

### `products[]` 产品对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `products[]` | object | 产品对象 |
| `products[].productId` | string | 产品 ID |
| `products[].usItemId` | string | US 商品 ID |
| `products[].title` | string | 标题 |
| `products[].description` | string | 描述 |
| `products[].price` | number | 价格 |
| `products[].wasPrice` | number | 原价（was_price） |
| `products[].currency` | string | 货币单位 |
| `products[].minPrice` | number | 最低价格 |
| `products[].pricePerUnitAmount` | string | 单价金额 |
| `products[].pricePerUnit` | string | 单价单位 |
| `products[].rating` | number | 评分 |
| `products[].reviews` | integer | 评价数 |
| `products[].sellerName` | string | 卖家名称 |
| `products[].sellerId` | string | 卖家 ID |
| `products[].imageUrl` | string | 缩略图 |
| `products[].productPageUrl` | string | 产品页面 URL |
| `products[].sponsored` | boolean | 是否是赞助商品 |
| `products[].outOfStock` | boolean | 是否缺货 |
| `products[].freeShipping` | boolean | 是否免运费 |
| `products[].twoDayShipping` | boolean | 是否支持两日配送 |
| `products[].freeShippingWithWalmartPlus` | boolean | Walmart Plus 会员免运费 |
| `products[].shippingPrice` | number | 运费 |
| `products[].multipleOptionsAvailable` | boolean | 是否有多个选项 |
| `products[].variantSwatches` | array | 变体样本列表 |
| `products[].variantSwatches[]` | object | 变体样本；来源未说明对象类型属性之外的约束 |
| `products[].variantSwatches[].name` | 来源未说明 | 变体名称 |
| `products[].variantSwatches[].imageUrl` | 来源未说明 | 变体图片 URL |
| `products[].variantSwatches[].productPageUrl` | 来源未说明 | 变体产品页面 URL |
| `products[].variantSwatches[].variantFieldId` | 来源未说明 | 变体字段 ID |
| `products[].sourceTool` | string | 来源工具 |
| `products[].sourceType` | string | 来源类型：`walmart` |

### 业务错误响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errorCode` | 来源未说明 | 正常 HTTP 200 响应的业务状态；`200` 表示成功，其他值表示业务错误 |
| `errcode` | integer | 未授权等错误响应中的业务码；来源示例为 `401` |
| `errmsg` | string | 错误原因；来源示例为 `authorized error` |

## 错误码

正常 HTTP 响应通常为 200，业务结果由响应体 `errorCode` 区分；未授权时 HTTP 和业务码可能为 401。

| 状态/码 | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 解析 `total`、`products`、`costToken` 等字段 |
| `401` | 认证失败 | 读取 `references/onboarding.md`，按 WorkBuddy 自动授权链路处理 |
| `402` | 计费不足 | 读取 `references/onboarding.md`，引导用户访问 `https://agent.linkfox.com/`；不得自动购买或重试 |
| 其他非 200 业务值 | 业务异常 | 结合 `errmsg` 调整参数或向用户说明 |

## 使用示例

```json
{"toolName":"walmart/search","arguments":{"keyword":"wireless earbuds","sort":"best_seller","page":1}}
```

```json
{"toolName":"walmart/search","arguments":{"keyword":"laptop stand","minPrice":10,"maxPrice":50,"sort":"price_low"}}
```

```json
{"toolName":"walmart/search","arguments":{"categoryId":"976759_976787","page":2,"device":"mobile"}}
```

## 展示与反馈规则

1. 以表格展示标题、当前价、划线价、评分/评价数、卖家、库存、赞助标记和 `productPageUrl`；价格始终带 `currency` 对应的货币符号。
2. 评分必须和评价数一起展示；缺货商品要醒目标注，赞助商品不得与自然排序商品混为一谈。
3. `total` 较大时说明总量并提示使用 `page`，不要未经用户同意自动翻页。
4. 失败时按 `errorCode`/`errcode`/`errmsg` 给出可执行的修正建议；不可用字段标为 N/A。
5. 若用户反馈功能不符、结果不符意图、表扬或提出建议，按下列 Feedback API 规则提交，不中断当前任务。

## Feedback API

这是独立于商品网关的反馈端点，不要把它当作商品查询端点：

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- Header：`Content-Type: application/json`
- Body：

```json
{
  "skillName": "linkfox-walmart-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

`sentiment` 取 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 取 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。`content` 应说明用户意图/反馈、实际结果和问题或称赞点，且不得写入 API Key、验证码或支付信息。

## 认证引导

自动授权、计费和 WorkBuddy 渠道约束统一见 `references/onboarding.md`；不要把 403 无权限错误当作 401/402 处理。
