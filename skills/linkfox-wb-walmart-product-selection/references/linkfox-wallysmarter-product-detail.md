# WallySmarter 沃尔玛商品详情（linkfox-wallysmarter-product-detail）

## 功能说明

通过单个 Walmart 数值 Item ID 查询商品详情，返回当前属性、价格、品牌、评分、卖家、配送方式、Listing/内容质量分、销量/收入估算，以及可选的历史价格和销量序列。它适合对搜索阶段选出的单品做深度核查；不用于关键词搜索或同时批量查询多个商品。

## 能力边界

### ✅ 能力范围

- 通过商品页 `https://www.walmart.com/ip/<productId>` 中的数值 ID 查询一个商品。
- 返回标题、描述、当前价、划线价、最低价、品牌、评分、评价数、卖家、部门和商品链接/图片。
- 返回 `salesEstimate`、`revenue`、`fulfillmentType`（`MARKETPLACE`/`WFS`）、`listingScore`、`contentScore`、库存、广告、品牌和变体标记。
- `includeStats=true`（默认）时读取 `stats.price` 与 `stats.sales` 的按天 UTC 历史序列。

### ❌ 边界与限制

- 只接受单个数值 `productId`/Item ID；批量查询必须逐个调用。
- 历史数据取决于 WallySmarter 的跟踪覆盖；没有统计数据时不能推导趋势。
- `salesEstimate` 与 `revenue` 是估算值，不是卖家后台真实经营数据。
- 返回混合结构化和非结构化数据，不兼容 `@智能数据查询` 二次分析。
- 不处理关键词/类目搜索、评论正文分析、卖家账号或广告经营指标、订单、店铺级市场规模、实时库存/配送承诺。
- 查询结果是数据参考，不构成销售、投资、法律或 FTO 结论。

## MCP 调用

- **MCP server**：`LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`）。
- **唯一工具**：`proxy_call`。
- **原 endpoint**：`/wallysmarter/productDetail`。
- **精确 `toolName`**：`wallysmarter/productDetail`，区分大小写。
- **`arguments`**：直接使用下方请求参数对象，不增加 `body`、`params`、`data`、`headers` 或第二层 `arguments`。Authorization 由 WorkBuddy 自动注入，不得传 API Key、token、JWT、手机号或其他凭证。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理层错误；代理成功后读取 text/structured content。text 为 JSON 字符串时只解析一次，再读取下游 `code`/`errcode`、`msg`/`errmsg` 和业务字段。
- **计费**：每次业务调用都可能消耗积分，以响应 `costToken` 为准；MCP 外层对象不是下游业务响应，不得把代理状态当作业务成功。
- **禁止回退与去重**：不得使用 curl、`urllib`、`requests`、`httpx` 直连网关；MCP 缺失时停止。同一任务内相同 `toolName + arguments` 不得重复调用；失败、空结果或结果不理想时不得自动换 ID、连续调用或重试收费调用。

## 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `productId` | integer | 是 | — | Walmart 数值 Item ID，来自商品 URL 的数字部分 |
| `includeStats` | boolean | 否 | `true` | 是否返回历史价格和历史销量 |

## 响应结构

成功响应字段仅依据 `skills/linkfox-wallysmarter-product-detail/references/api.md`：

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `code` | string | 返回码（`"200"` 表示成功） |
| `msg` | string | 消息（成功时为 `"ok"`，失败时为错误描述） |
| `total` | integer | 返回的商品数量（本接口通常为 1） |
| `products` | array | 商品列表（见下方商品对象） |
| `columns` | array | 列定义，描述 `products` 中各字段的元信息 |
| `type` | string | 响应渲染类型，固定值 `"productWorkbenches"` |
| `costTime` | integer | 接口耗时（毫秒） |
| `costToken` | integer | 消耗 Token 数量 |

### `columns[]` 列定义

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `columns[]` | object | 列定义元素 |
| `columns[].field` | 来源未说明 | 字段标识；来源仅明确列定义含此属性 |
| `columns[].title` | 来源未说明 | 列标题；来源仅明确列定义含此属性 |
| `columns[].cellType` | 来源未说明 | 单元格类型；来源仅明确列定义含此属性 |

### `products[]` 商品对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `products[]` | object | 商品对象 |
| `products[].usItemId` | integer | 商品内部 ID，即请求中的 `productId` |
| `products[].productId` | string | Walmart 商品唯一标识；字母数字混合，例如 `"6YBM50F6ZXAE"` |
| `products[].title` | string | 商品名称 |
| `products[].description` | string | 商品描述 |
| `products[].price` | number | 当前售价（美元） |
| `products[].wasPrice` | number | 划线价（美元），无折扣时可能为 null |
| `products[].minPrice` | number | 最低价格（美元） |
| `products[].brand` | string | 品牌名称 |
| `products[].rating` | number | 商品评分，范围 0.0–5.0 |
| `products[].reviews` | integer | 评论数量（条） |
| `products[].salesEstimate` | integer | 销量估算（件，近期周期内） |
| `products[].revenue` | number | 收入估算（美元） |
| `products[].sellerName` | string | 卖家名称 |
| `products[].fulfillmentType` | string | 配送类型：`"MARKETPLACE"`（第三方卖家自配送）或 `"WFS"`（Walmart Fulfillment Services） |
| `products[].productPageUrl` | string | 商品页面 URL |
| `products[].imageUrl` | string | 商品图片 URL（缩略图） |
| `products[].departmentName` | string | 所属部门名称，例如 `"Cell Phones"` |
| `products[].departmentId` | integer | 所属部门 ID |
| `products[].listingScore` | integer | Listing 质量评分 |
| `products[].contentScore` | integer | 内容质量分 |
| `products[].outOfStock` | integer | 是否缺货：`0`=有货，`1`=缺货 |
| `products[].sponsored` | integer | 是否广告商品：`0`=否，`1`=是 |
| `products[].isBranded` | integer | 是否品牌商品：`0`=否，`1`=是 |
| `products[].multipleOptionsAvailable` | integer | 是否有变体：`0`=否，`1`=是 |
| `products[].createdAt` | string | WallySmarter 首次收录时间；格式 `yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'` |
| `products[].updatedAt` | string | 最近一次数据更新时间；格式同 `createdAt` |
| `products[].stats` | object/null | 历史统计数据；仅当 `includeStats=true` 时返回，否则为 null |
| `products[].sourceTool` | string | 来源工具标识 |
| `products[].sourceType` | string | 商品来源平台，固定值 `"walmart"` |

### `products[].stats` 对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `products[].stats.price` | array | 历史售价时间序列；按日期升序、UTC 时区 |
| `products[].stats.price[]` | object | 单条日期-售价映射；对象只包含一个键值对 |
| `products[].stats.price[].<yyyy-MM-dd>` | number | key 为 UTC 日期，value 为当日售价（美元） |
| `products[].stats.sales` | array | 历史销量时间序列；按日期升序、UTC 时区 |
| `products[].stats.sales[]` | object | 单条日期-销量映射；对象只包含一个键值对 |
| `products[].stats.sales[].<yyyy-MM-dd>` | number | key 为 UTC 日期，value 为当日销量（件） |

消费端遍历数组时，取每个对象的唯一键作为日期、唯一值作为数值；不要把缺失日期插值为真实销量或价格。

### 业务错误响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 错误业务码；来源示例为 `401` |
| `errmsg` | string | 错误原因；来源示例为 `authorized error` |

## 错误码

正常 HTTP 响应通常为 200，业务结果由响应体 `code` 区分；未授权时 HTTP 状态可能为 401。

| 状态/码 | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 解析 `products`、`stats`、`costToken` 等字段 |
| `401` | 认证失败 | 读取 `references/onboarding.md`，按 WorkBuddy 自动授权链路处理 |
| `402` | 计费不足 | 读取 `references/onboarding.md`，引导用户访问 `https://agent.linkfox.com/`；不得自动购买或重试 |
| 其他非 200 业务值 | 业务异常 | 结合 `msg`/`errmsg` 说明原因 |

错误响应可能类似：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

## 使用示例

只查当前属性和趋势：

```json
{"toolName":"wallysmarter/productDetail","arguments":{"productId":5177343351,"includeStats":true}}
```

只查商品属性：

```json
{"toolName":"wallysmarter/productDetail","arguments":{"productId":5169493923,"includeStats":false}}
```

商品 ID 可从 `https://www.walmart.com/ip/<数字>` 取得。若 ID 来自列表响应，优先使用数值 `usItemId` 或商品页数字；列表中的字母数字 `productId` 不一定是本端点所需的数值参数。

## 展示规则

1. 以结构化分组展示当前属性、价格、卖家/配送、评分、质量分和历史统计；当前价与可用 `wasPrice` 一起显示并带 `$`。
2. `rating` 必须和 `reviews` 一起展示；`salesEstimate`、`revenue` 和历史序列明确标注为估算或历史数据。
3. `outOfStock=1` 要醒目标注缺货；展示 `fulfillmentType`，区分 `WFS` 与 `MARKETPLACE`；`sponsored=1` 标注广告。
4. 只有 `stats` 非空时才总结趋势；按 UTC 日期解释 `stats.price` 和 `stats.sales`，说明可用时间窗和数据覆盖限制。
5. 解释 `listingScore`/`contentScore` 是 Listing/内容质量分，通常分数越高表示质量越好，不将其当作销量或平台排名保证。
6. `null`、空值及接口语义中的不可用值标为 N/A；`includeStats=false` 时不要声称已经检查过历史趋势。
7. 展示 `productPageUrl`、`sourceTool`、`sourceType` 和 `updatedAt`/查询时间；不可用来源字段要明确说明。
8. 失败时按 `code`/`errcode` 和 `msg`/`errmsg` 解释，并建议检查数值 Item ID、Key、余额或统计覆盖；不要自动批量重试。

## Feedback API

这是独立于商品详情网关的反馈端点：

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- `Content-Type: application/json`

```json
{
  "skillName": "linkfox-wallysmarter-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

`sentiment` 必须为 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 必须为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。内容应记录用户意图、实际结果及问题/称赞点，不包含 API Key、验证码或支付信息。

## 认证引导

自动授权、计费和 WorkBuddy 渠道约束统一见 `references/onboarding.md`；403 表示无权限，不应按 401/402 自动购买套餐处理。
