# Lanjing Mercado Libre Product Selection API 参考

## 调用规范

本 Skill 只调用 LinkFox 后端生产网关，不直连蓝鲸 XP-MCP 上游服务。

- **网关**：由环境变量 `LINKFOX_TOOL_GATEWAY` 指定，缺省回退 `https://tool-gateway.linkfox.com`
- **请求地址**：`POST ${LINKFOX_TOOL_GATEWAY}/lingdong/call`
- **Content-Type**：`application/json`
- **User-Agent**：`LinkFox-Skill/2.0`
- **超时**：120s
- **认证方式**：Header `Authorization: <api_key>`，api_key 优先从环境变量 `LINKFOX_AGENT_API_KEY` 读取，回退 `LINKFOXAGENT_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

脚本还会透传 `SESSION_ID`、`MODE_ID`、`APP_NAME` 同名环境变量（缺省空串）。不要把蓝鲸上游 `secret-key`、`X-API-Key` 或后端内部环境变量交给 Skill；上游凭证由后端托管。

## 请求参数

请求体固定为：

```json
{
  "toolName": "categorySearch",
  "arguments": {
    "siteId": "MLM",
    "searchText": "Auriculares"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | 24 个蓝鲸美客多工具名之一，见下方「工具与必填字段」。 |
| `arguments` | object | 是 | 对应工具的参数对象。字段名必须与 `lanjing-mercado-tool-reference.md` 完全一致。 |

`arguments` 必须是 JSON 对象，不能是数组、字符串或数字。后端会移除 `uId`、`uid`、`memberId`，并裁剪空值。

## 工具与必填字段

以下必填字段来自后端 `LingdongToolDefinition` 契约（完整可选参数见 `lanjing-mercado-tool-reference.md`）：

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

各工具的完整可选站点以 `lanjing-mercado-tool-reference.md` 为准。

## 响应结构

正常响应示例（以 `myUsage` 为例；蓝鲸多数工具以文本返回业务结果，`data` 常为字符串）：

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

| 字段 | 说明 |
|---|---|
| `code`, `msg` | LinkFox 封装层状态，成功时 `code:"200"`、`msg:"ok"`。 |
| `errcode`, `errmsg` | 与 `code`/`msg` 并存的网关状态码；成功 `errcode:200`，失败为非 200（见「错误处理」）。 |
| `type` | 当前通常为 `rawMcpToolResult`。 |
| `toolName` | 实际调用的蓝鲸工具名。 |
| `charged` | 该工具是否收费。 |
| `data` | 从 MCP `content.text` 解包后的业务数据。蓝鲸多数工具以**文本**返回结果（类目列表、商品字段、套餐用量等都是格式化文本），因此 `data` 常常是字符串；仅当上游返回 JSON 数组/对象时才会被解析成对应结构。 |
| `rawResponse` | MCP `tools/call` 原始 result；当前网关返回为空对象 `{}`（原始 result 不透出给 Skill，需要原始文本时看 `contentText`/`data`）。 |
| `contentText` | MCP text content 拼接后的原文。 |
| `textParsedAsJson` | `contentText` 是否被成功解析为 JSON（文本被 JSON 字符串包裹时也为 true，此时 `data` 仍是字符串）。 |
| `total` | 后端推断的记录数；仅在可推断时出现（如列表类结果），文本类结果中**省略该字段**（不是 `null`）。 |
| `costToken` | 本次调用的 token 成本（收费工具 16000，免费工具 0）。 |
| `costTime` | 后端耗时，单位毫秒。 |

## 脚本用法

入口脚本以官方模板为唯一权威：整体复制模板 + 替换占位符，已内置网关、鉴权、120s 超时、24h 本地缓存、`--inline` 与自动落盘。请求体作为**单个 JSON 参数**传入（即完整的 `{"toolName":...,"arguments":{...}}`）：

```bash
# 免费工具：按名称搜墨西哥类目
python scripts/linkfox_lanjing_mercado_product_selection.py '{"toolName":"categorySearch","arguments":{"siteId":"MLM","searchText":"Auriculares"}}'

# 收费工具：真实 MLM 商品详情
python scripts/linkfox_lanjing_mercado_product_selection.py '{"toolName":"itemInfo","arguments":{"siteId":"MLM","itemId":"MLM4979447466"}}'

# 免费工具：套餐用量（无参数）
python scripts/linkfox_lanjing_mercado_product_selection.py '{"toolName":"myUsage","arguments":{}}'

# 强制全量打印到 stdout（同样落盘）
python scripts/linkfox_lanjing_mercado_product_selection.py '{"toolName":"myUsage","arguments":{}}' --inline
```

输出策略：响应体 ≤ 8 KB 时落盘后全量打印；> 8 KB 时落盘后只打印摘要（顶层字段、`total`/`costToken` 等计数、最大列表字段长度 + 前 3 条样本）。二次同参会走 24h 缓存，输出含 `Cache hit`。

## curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY}/lingdong/call" \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"categorySearch","arguments":{"siteId":"MLM","searchText":"Auriculares"}}'
```

## 错误处理

业务错误时 HTTP 仍为 200，响应体只剩 `errcode` / `errmsg`（不含 `code`/`data` 等封装字段）：

```json
{ "errcode": 1002, "errmsg": "参数校验失败，请检查输入。参数 siteId 不能为空，请补充后重试。" }
```

常见 `errcode`：

| errcode | 含义 | 处理 |
|---|---|---|
| `1002` | 参数校验失败（必填缺失 / arguments 非对象 / 不支持的 toolName 等） | 按「工具与必填字段」和 `lanjing-mercado-tool-reference.md` 补齐字段、核对 toolName 拼写，保持大小写。 |
| `500` | 上游 MCP 调用异常（如 `LingdongMcpClient$TransientMcpException`） | 多为瞬时（MCP 握手偶发 404），重试 1-2 次；仍失败记录脱敏请求/响应交后端确认。 |

> `lanjing-mercado-tool-reference.md` 附录 E 的 `-32000` 系列是上游 MCP 协议层错误码，网关会统一转成 `1002`/`500`，Skill 侧不会直接见到。

其他情况：

- HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- HTTP `403`：检查 `Authorization` 是否为 LinkFox 网关 Key，而不是蓝鲸上游 Key。
- `toolName` 不支持：网关返回 `errcode 1002`，`errmsg` 形如「参数校验失败，请检查输入。不支持的 toolName: <name>」（脚本不会退出，照常落盘该错误响应）。
- `data` 是文本：这不一定是失败，多数蓝鲸工具以文本返回业务结果。
- 查询为空（如 `查询不到商品信息`、`未查询到评论数据`）：封装层 `code:"200"` 属正常，是上游业务结果为空，不应报成系统异常；换一个真实 ID/关键词即可。

## Feedback API

此接口只用于 Skill 使用反馈，不是 Mercado 工具调用入口。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "linkfox-lanjing-mercado-product-selection",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "User expected itemSearch results to preserve the upstream field order when presenting a comparison table."
}
```

字段规则：

| 字段 | 说明 |
|---|---|
| `skillName` | 固定为 `linkfox-lanjing-mercado-product-selection`。 |
| `sentiment` | `POSITIVE`、`NEUTRAL`、`NEGATIVE` 三选一。 |
| `category` | `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 四选一。 |
| `content` | 简洁描述用户意图、实际行为、问题或表扬；不要包含 Key、隐私、完整大响应或敏感业务数据。 |
