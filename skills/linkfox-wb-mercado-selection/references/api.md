# Mercado Libre Product Selection API 参考

## MCP 调用规范

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **原 endpoint**：`/mercado/productSelection`
- **精确 `toolName`**：`mercado/productSelection`（区分大小写，不带前导 `/`）
- **`arguments`**：直接使用原请求体 `{ "toolName": "<operation>", "arguments": { ... } }`。外层 MCP `toolName` 与内层 operation selector 同名但职责不同；不得把内层对象扁平化，也不得额外包裹 `body`、`params` 或 `data`。
- **认证**：WorkBuddy 自动注入授权上下文。禁止在 MCP 配置或参数中加入 `headers`、Authorization、API Key、token、JWT、手机号或任何上游凭证。
- **解析与错误**：先检查 MCP 连接、schema 和 `isError`，再读取 text/structured content；text JSON 只解析一次，之后判断下游 `errcode`/`errmsg` 与 `code`/`msg`。MCP 缺失或失败时禁止回退旧 HTTP 网关或脚本。
- **收费去重**：同一任务内相同外层 `toolName + arguments` 只调用一次。失败、空结果或结果不理想不得自动重试、换参数或翻页；追加调用前说明潜在消耗并取得用户同意。

## 请求参数

完整 `proxy_call` 参数为：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {
    "toolName": "categorySearch",
    "arguments": {
      "siteId": "MLM",
      "searchText": "Auriculares"
    }
  }
}
```

| 字段路径 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | MCP endpoint 固定为 `mercado/productSelection`。 |
| `arguments` | object | 是 | 原下游请求体。 |
| `arguments.toolName` | string | 是 | 24 个美客多 operation 之一，见下方「工具与必填字段」。 |
| `arguments.arguments` | object | 是 | 对应 operation 的业务参数对象；字段名必须与 `mercado-tool-reference.md` 完全一致。 |

内层 `arguments.arguments` 必须是 JSON 对象，不能是数组、字符串或数字。后端会移除 `uId`、`uid`、`memberId`，并裁剪空值。

## 工具与必填字段

以下必填字段来自后端 `LingdongToolDefinition` 契约（完整可选参数见 `mercado-tool-reference.md`）：

| 工具 | 是否收费 | 必填字段 | 用途 |
|---|---:|---|---|
| `itemInfo` | 是 | `siteId`, `itemId` | 查询商品基本信息 |
| `itemHistory` | 是 | `itemId` | 查询商品销量历史 |
| `itemSearch` | 是 | `siteId` | 商品搜索与筛选 |
| `catalogInfo` | 是 | `siteId`, `productId` | 查询官链/目录基本信息 |
| `catalogHistory` | 是 | `siteId`, `productId` | 查询官链/目录销量历史 |
| `catalogSearch` | 是 | `siteId` | 官链/目录搜索 |
| `keywordDateSearch` | 是 | `siteId`, `runDate` | 按天查询热搜词 |
| `keywordMonthSearch` | 是 | `siteId`, `runMonth` | 按月查询热搜词 |
| `keywordReverse` | 是 | `siteId`, `itemId` | 流量词反查 |
| `categorySearch` | 否 | `siteId`, `searchText` | 搜索类目 |
| `categorySmallSearch` | 否 | `siteId`, `searchText` | 搜索最小子类目 |
| `trendBrandTopBrand` | 是 | `siteId`, `categoryId` | 类目热门品牌排行 |
| `trendBrandTopItem` | 是 | `siteId`, `categoryId` | 类目热门商品排行 |
| `trendBrandTopSeller` | 是 | `siteId`, `categoryId` | 类目热门店铺排行 |
| `trendNewItems` | 是 | `siteId`, `categoryId` | 新品机会分析 |
| `trendPrice` | 是 | `siteId`, `categoryId` | 价格分布趋势 |
| `trendSale` | 是 | `siteId`, `categoryId` | 销量分布 |
| `trendSoldHis` | 是 | `siteId`, `categoryId` | 销售历史趋势 |
| `trendStatistical` | 是 | `siteId`, `categoryId` | 类目汇总统计 |
| `trendStoreInventoryType` | 是 | `siteId`, `categoryId` | 仓储类型分布 |
| `sellerSearch` | 是 | `siteId` | 店铺搜索 |
| `reviewSearch` | 否 | `itemId` | 查询商品评论 |
| `rateInfo` | 否 | `siteId` | 汇率查询 |
| `myUsage` | 否 | 无 | 查询套餐使用量 |

免费工具：`categorySearch`、`categorySmallSearch`、`reviewSearch`、`rateInfo`、`myUsage`。收费工具：除免费工具外的所有工具。当前后端策略是每次收费工具调用固定返回 `costToken = 16000`，不会因为结果为空而免扣。

## 站点 ID

| 站点 | 含义 |
|---|---|
| `MLM` | 墨西哥 |
| `MLB` | 巴西 |
| `MLA` | 阿根廷 |
| `MLC` | 智利 |
| `MCO` | 哥伦比亚，仅部分搜索和趋势工具支持 |

各工具的完整可选站点以 `mercado-tool-reference.md` 为准。

## 响应结构

响应字段来源：`skills/linkfox-mercado-product-selection/references/api.md`。下表按来源的响应示例及字段说明恢复；来源没有定义 `data` 内文本或动态 JSON 的统一子字段，因此不得臆造 operation 专属响应字段。

正常响应示例（以 `myUsage` 为例；多数工具以文本返回业务结果，`data` 常为字符串）：

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "type": "rawMcpToolResult",
  "toolName": "myUsage",
  "charged": false,
  "data": "=== 我的套餐及使用量 ===\n...",
  "rawResponse": {},
  "contentText": "\"=== 我的套餐及使用量 ===\\n...\"",
  "textParsedAsJson": true,
  "costToken": 0,
  "costTime": 308
}
```

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `code` | string | LinkFox 封装层状态；成功示例为 `"200"`。 |
| `msg` | string | LinkFox 封装层消息；成功示例为 `"ok"`。 |
| `errcode` | integer | 与 `code`/`msg` 并存的网关状态码；成功为 `200`，失败为非 200。 |
| `errmsg` | string | 网关状态消息；成功示例为 `"ok"`。 |
| `type` | string | 当前通常为 `rawMcpToolResult`。 |
| `toolName` | string | 实际执行的下游 operation 名。 |
| `charged` | boolean | 该 operation 是否收费。 |
| `data` | string / array / object | 从上游 MCP `content.text` 解包后的业务数据；多数 operation 返回格式化文本，仅当上游返回 JSON 数组/对象时解析为对应结构。来源未定义统一子字段。 |
| `rawResponse` | object | 上游 MCP `tools/call` 原始 result；来源记载当前返回空对象 `{}`，没有定义子字段。 |
| `contentText` | string | MCP text content 拼接后的原文。 |
| `textParsedAsJson` | boolean | `contentText` 是否成功解析为 JSON；JSON 字符串被解析后 `data` 仍可为字符串。 |
| `total` | integer / absent | 后端推断的记录数；仅在可推断时出现，文本类结果中省略而非 `null`。 |
| `costToken` | integer | 本次调用的 token 成本；来源记载收费 operation 为 16000，免费 operation 为 0。 |
| `costTime` | integer | 后端耗时，单位毫秒。 |

## MCP 示例

免费类目搜索：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {
    "toolName": "categorySearch",
    "arguments": {
      "siteId": "MLM",
      "searchText": "Auriculares"
    }
  }
}
```

收费商品详情：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {
    "toolName": "itemInfo",
    "arguments": {
      "siteId": "MLM",
      "itemId": "MLM4979447466"
    }
  }
}
```

免费套餐用量：

```json
{
  "toolName": "mercado/productSelection",
  "arguments": {
    "toolName": "myUsage",
    "arguments": {}
  }
}
```

每个示例只代表一次调用。收费 operation 的失败、空结果或不理想结果不得自动触发第二次调用。

## 错误处理

代理层成功时仍可能出现下游业务错误；此时下游响应可能只包含 `errcode` / `errmsg`，不含 `code`/`data` 等封装字段：

```json
{ "errcode": 1002, "errmsg": "参数校验失败，请检查输入。参数 siteId 不能为空，请补充后重试。" }
```

常见 `errcode`：

| errcode | 含义 | 处理 |
|---|---|---|
| `1002` | 参数校验失败（必填缺失 / arguments 非对象 / 不支持的 toolName 等） | 按「工具与必填字段」和 `mercado-tool-reference.md` 补齐字段、核对 toolName 拼写，保持大小写。 |
| `500` | 上游 MCP 调用异常（如 `LingdongMcpClient$TransientMcpException`） | 记录脱敏的 MCP `toolName`、arguments 与错误信息；收费调用不得自动重试。 |

> `mercado-tool-reference.md` 附录 E 的 `-32000` 系列是上游 MCP 协议层错误码，网关会统一转成 `1002`/`500`，Skill 侧不会直接见到。

其他情况：

- MCP 连接或下游 401/authorized error：按 `onboarding.md` 的 WorkBuddy 自动授权异常处理，不传凭证。
- 下游 402：按 `onboarding.md` 的积分不足流程处理。
- 下游 403：按权限问题处理，不归入 401/402。
- 内层 operation 不支持：下游返回 `errcode 1002`，`errmsg` 形如「参数校验失败，请检查输入。不支持的 toolName: <name>」。
- `data` 是文本：这不一定是失败，多数工具以文本返回业务结果。
- 查询为空（如 `查询不到商品信息`、`未查询到评论数据`）：封装层 `code:"200"` 属正常，是上游业务结果为空，不应报成系统异常；不得自动换 ID、关键词、分页或参数再次调用。

## Feedback API

此接口只用于 Skill 使用反馈，不是 Mercado 工具调用入口。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "linkfox-mercado-product-selection",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "User expected itemSearch results to preserve the upstream field order when presenting a comparison table."
}
```

字段规则：

| 字段 | 说明 |
|---|---|
| `skillName` | 固定为 `linkfox-mercado-product-selection`。 |
| `sentiment` | `POSITIVE`、`NEUTRAL`、`NEGATIVE` 三选一。 |
| `category` | `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 四选一。 |
| `content` | 简洁描述用户意图、实际行为、问题或表扬；不要包含 Key、隐私、完整大响应或敏感业务数据。 |
