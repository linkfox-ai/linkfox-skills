---
name: linkfox-wb-sorftime
display_name: LinkFox Sorftime亚马逊选品
display_name_en: LinkFox Sorftime Amazon Product Research
description: Sorftime 亚马逊选品与竞品研究：搜索筛选多站点产品、回看历史快照、分析指定 ASIN 详情和趋势。当用户要找产品、筛选市场或研究 ASIN 时触发；广告投放、评论分析和知产检测不在范围。
description_zh: 面向亚马逊选品与竞品研究，通过 Linkfox MCP 使用 Sorftime 搜索和筛选多站点产品、回看历史月份快照，并按 ASIN 获取价格、销量、BSR、利润、FBA 费用及趋势数据。当用户要发现产品、分析类目/品牌/卖家、组合筛选或深入研究指定 ASIN 时触发；完整参数、响应字段和错误处理见 references。
description_en: Amazon product research powered by Sorftime through Linkfox MCP. Discover and filter products across marketplaces, inspect historical monthly snapshots, and analyze a specific ASIN's pricing, sales, BSR, profit, FBA fees, and time-series trends.
icon: icons/logo.png
version: 2.1.0
author: Linkfox
---

> [!IMPORTANT]
本 Skill 必须依赖 MCP “LinkFox”。如未安装该MCP，请明确通知用户：
> 请先安装 LinkFox 连接器：
> - 在 WorkBuddy 左侧找到 “专家·技能·连接器” → “连接器”；
> - 搜索关键词 “LinkFox”，并安装连接器 “LinkFox”（注意：是 linkfox，不是 linkfox-product-selection），按指引完成登录授权；
> - 返回 WorkBuddy 重试。


# LinkFox Sorftime亚马逊选品（LinkFox Sorftime Amazon Product Research）

面向亚马逊选品和竞品研究，提供从市场范围发现到单个 ASIN 深查的一体化数据工作流：先按站点、类目、品牌、卖家、ABA 关键词、价格、销量、评分、排名、履约方式和变体数量等条件找到产品，再对指定 ASIN 查看产品基本面、利润与 FBA 费用、价格/销量/BSR/Deal 历史。当前包含 2 个可路由子能力和 2 个精确 MCP endpoint。

## 能力边界

### 能力范围

- **多维产品发现与筛选**：使用子能力 `linkfox-sorftime-amazon-product-query` 的 `/sorftime/amazon/productQuery`，按单条件或 AND 组合条件搜索产品，适合类目、品牌、卖家、竞品、ABA 关键词、季节性产品、价格/销量/评分/排名/履约等筛选。参数与字段见 `references/linkfox-sorftime-amazon-product-query.md`。
- **历史月份快照**：在产品搜索请求中设置 `queryMonth`（`yyyy-MM`），回看 2024-01 起可用的历史产品数据，用于比较价格、销量、排名等市场快照；具体站点限制以接口响应为准。
- **指定 ASIN 详情与趋势**：使用子能力 `linkfox-sorftime-amazon-product-detail` 的 `/sorftime/amazon/productDetail`，适合查看标题、变体、卖家、评分、价格、利润、FBA 明细、官方月销量、BSR、Listing 特征、Deal 和时间序列趋势。参数与字段见 `references/linkfox-sorftime-amazon-product-detail.md`。
- **跨站点研究**：两个业务端点均支持 `us`、`gb`、`de`、`fr`、`in`、`ca`、`jp`、`es`、`it`、`mx`、`ae`、`au`、`br`、`sa`；未指定站点时使用 `us`，英国必须写 `gb`。
- **自动授权与计费引导**：WorkBuddy 自动注入授权；MCP/401/402/403 异常按 `references/onboarding.md` 分层处理，不索取凭证，不自动查询套餐、下单、支付或轮询。

### 边界与限制

- **自动授权边界**：业务调用不得传 `headers`、Authorization、API Key、token、JWT、手机号或其他凭证；授权由 WorkBuddy 注入。
- **查询与趋势的职责不同**：`productQuery` 用于跨产品发现、筛选和历史快照；`productDetail` 用于已知 ASIN 的详情与趋势。不要用 ASIN 相似查询代替指定 ASIN 详情，也不要用详情端点探索整个类目。
- **查询分页限制**：产品搜索每页最多 100 个产品，最多 200 页；只有用户明确需要更多结果时才增加 `page`，不要因为空结果或失败自动翻页试探。
- **详情批量与趋势成本**：详情一次最多查询 10 个 ASIN；默认趋势为近 15 天，指定超过 15 天的范围会加倍计费；仅需基本信息时用 `includeTrend: 2`。
- **历史快照限制**：`queryMonth` 使用 `yyyy-MM`；US、GB、DE 支持完整回看，其他站点通常只支持回看 Top 100，AU、BR、IN 不支持回看。若接口返回不同限制，以接口消息为准。
- **字段估算与单位**：销量/销售额为估算数据，`-1` 表示无法估算；搜索的价格筛选值使用货币最小单位（美元为美分），详情趋势中的价格和销售额也使用当地货币最小单位，当前详情价格/利润字段则按当地货币展示。
- **非结构化后处理限制**：返回结果不支持通过 `_dataQuery_executeDynamicQuery` 做二次分析；直接从本次 MCP 返回中按需抽取字段，不自动追加收费调用。
- **不适用范围**：不提供广告/PPC 投放策略、评论正文情感分析、商标/专利/版权检测、ABA 关键词搜索量与排名、店铺订单/库存/物流、注册申请、法律意见或侵权结论。
- **计费安全**：同一任务内相同 MCP `toolName + arguments` 只调用一次；失败、空结果或参数不匹配时不得自动改词、换 ASIN、翻页或改参数连续试探。继续调用前说明可能产生额外积分消耗，由用户决定。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找这个类目/品牌/卖家的热销产品” | `linkfox-sorftime-amazon-product-query`，分别使用 `queryType=2/3/4` | 若用户已给出具体 ASIN 且要趋势曲线，改用 `linkfox-sorftime-amazon-product-detail` |
| “找这个 ASIN 的竞品/相似产品” | `productQuery` 的 `queryMode=1, queryType=1` | 该查询返回相似产品，不代表目标 ASIN 本身；若要目标 ASIN 详情，用 `productDetail` |
| “按关键词、价格、销量、评分、BSR、FBA 等条件筛选” | `productQuery`；单条件用 `queryMode=1`，多个条件用 `queryMode=2`（AND） | 需要指定 ASIN 的利润明细或变体时，用 `productDetail` |
| “看某个月这个类目的产品/价格快照” | `productQuery` 加 `queryMonth` | AU、BR、IN 或超出站点回看范围时，先依据接口 `msg` 说明限制；要单品连续趋势则用 `productDetail` |
| “看这个 ASIN 的价格、销量、BSR、利润走势” | `linkfox-sorftime-amazon-product-detail`，默认趋势或指定日期范围 | 只要产品基本面、不需要趋势时设置 `includeTrend=2` 以减少响应和成本 |
| “对比多个 ASIN 的详情” | `productDetail`，逗号分隔 ASIN，最多 10 个 | 若用户还不知道候选 ASIN，先用 `productQuery` 发现产品 |

选择时先判断用户是否已有 ASIN：没有 ASIN 或需要跨产品筛选时走产品搜索；已有 ASIN 且问题涉及单品详情、费用或历史趋势时走产品详情。再根据是否需要多条件、历史月份、长趋势范围和批量 ASIN 调整参数，并在可能产生额外消耗时先提示。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 MCP `toolName` | 本地 helper |
|---|---|---|---|---|---|
| `linkfox-sorftime-amazon-product-query` | 多维亚马逊产品搜索、筛选、竞品/类目/品牌/卖家探索、历史月份快照 | `references/linkfox-sorftime-amazon-product-query.md` | `/sorftime/amazon/productQuery` | `sorftime/amazon/productQuery` | 无 |
| `linkfox-sorftime-amazon-product-detail` | 指定 ASIN 产品详情、利润/FBA 费用、变体、价格/销量/BSR/Deal 趋势 | `references/linkfox-sorftime-amazon-product-detail.md` | `/sorftime/amazon/productDetail` | `sorftime/amazon/productDetail` | 无 |

两个业务子能力分别只有上述 1 个 API operation；`productQuery` 的 16 种 `queryType` 是同一端点的参数分支，不应当当作 16 个端点处理。

## MCP 调用方式

- MCP server：`LinkFox`；唯一工具：`proxy_call`。
- 允许的精确 `toolName`：`sorftime/amazon/productQuery`、`sorftime/amazon/productDetail`。两者均为原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- 原请求对象直接放入 `proxy_call.arguments`，不得额外包裹 `body`、`params`、`data` 或另一层 `arguments`。
- WorkBuddy 自动注入授权上下文；MCP 配置和参数中禁止增加 `headers`、Authorization、API Key、token、JWT、手机号或其他凭证。
- 先检查 MCP 连接、工具、schema 与 `isError`，再读取 text/structured content；text JSON 只解析一次。之后检查下游 `errcode`/`errmsg`、`code`/`msg`，最后读取结果、分页与成本字段。
- 同一任务内相同 `toolName + arguments` 只调用一次。收费调用失败、空结果或不理想时不自动换词、换 ASIN、翻页、改日期或重试；追加调用前说明潜在消耗并取得用户同意。
- MCP 不可用时禁止回退旧 HTTP 网关、Python 查询脚本或其他工具。
- 旧脚本的 24 小时缓存、自动响应落盘、会话元数据和 stdout 摘要已移除；不要声称 MCP 自动提供这些能力。记录实际 `toolName`、参数摘要、站点、页码/时间范围、查询时间和成本字段便于复核。
- 完整参数、响应和错误分别见两份业务 reference；认证与积分异常见 `references/onboarding.md`。

## 使用示例

以下示例均为对应端点的 JSON Body。未指定站点时可默认 `us`，但实际请求仍应显式传入 `marketplace`。

### 产品搜索：单条件类目探索

```json
{
  "toolName": "sorftime/amazon/productQuery",
  "arguments": {
    "marketplace": "us",
    "queryMode": 1,
    "queryType": 2,
    "queryValue": "3743561",
    "page": 1
  }
}
```

`queryType=2` 的值是类目 NodeId；重点出参是 `products`、`total`、`page`、`pageCount`、`costToken`。每页最多 100 个产品，展示时说明当前页和总页数；如需下一页必须由用户明确要求。

### 产品搜索：多条件选品筛选

```json
{
  "toolName": "sorftime/amazon/productQuery",
  "arguments": {
    "marketplace": "us",
    "queryMode": 2,
    "queryValue": "[{\"QueryType\":8,\"Content\":\",2000\"},{\"QueryType\":9,\"Content\":\"500,\"},{\"QueryType\":12,\"Content\":\"4,5\"},{\"QueryType\":15,\"Content\":\"FBA\"}]",
    "page": 1
  }
}
```

这里分别表示价格不高于 2000 美分、月销量至少 500、评分 4–5、FBA；`QueryType` 与 `Content` 必须使用 API 规定的大小写和格式。重点出参是价格、销量/销售额、利润率、BSR、评分、卖家与履约字段；估算字段为 `-1` 时展示为不可估算。

### 产品搜索：历史月份快照

```json
{
  "toolName": "sorftime/amazon/productQuery",
  "arguments": {
    "marketplace": "de",
    "queryMode": 1,
    "queryType": 3,
    "queryValue": "Anker",
    "queryMonth": "2024-11",
    "page": 1
  }
}
```

`queryMonth` 只能使用 `yyyy-MM`。适合把历史结果与不带 `queryMonth` 的当前请求对照；必须先确认站点支持回看，历史快照可能有 Top 100 限制。

### 产品详情：基本面与利润

```json
{
  "toolName": "sorftime/amazon/productDetail",
  "arguments": {
    "asin": "B00FLYWNYQ",
    "marketplace": "us",
    "includeTrend": 2
  }
}
```

`includeTrend=2` 只取基本详情，适合检查价格、Coupon、平台佣金、FBA 明细、利润率、评分、卖家、变体、A+ 和在售状态；重点出参在 `products[]`，另有 `total`、`costToken`、`requestConsumed`。

### 产品详情：指定历史范围与批量 ASIN

```json
{
  "toolName": "sorftime/amazon/productDetail",
  "arguments": {
    "asin": "B00FLYWNYQ,B0088PUEPK,B0CVM8TXHP",
    "marketplace": "us",
    "includeTrend": 1,
    "queryTrendStartDate": "2025-01-01",
    "queryTrendEndDate": "2025-03-31"
  }
}
```

一次最多 10 个 ASIN。`products[].rankTrend`、`listingSalesVolumeOfDailyTrend`、`priceTrend` 等数组按日期和值交错排列，`bsrRankTrend` 是按子类节点分组的对象数组；超过默认 15 天会加倍计费，执行前必须提醒用户。

## 展示规则

1. **客观呈现数据**：使用表格或按产品分组展示 Sorftime 返回的字段，说明查询站点、查询时间、端点和分页/历史月份，不把数据直接包装成保证性选品结论。
2. **区分研究层级**：产品搜索结果突出 `asin`、标题、价格、销量、销售额、利润率、BSR、评分、卖家和 FBA；产品详情结果再补充变体、FBA 明细、Buy Box、A+、视频、品牌店、促销和趋势。
3. **排名说明**：展示 BSR 或小类排名时注明数值越低排名越好；同时标注大类/小类名称，避免把不同节点的排名直接横比。
4. **货币单位转换**：搜索价格筛选和详情趋势中的价格/销售额使用当地货币最小单位，展示给用户时换算为当地标准货币并保留原始单位说明；详情当前 `price`、`profitAmount`、`fbaFees` 等字段按接口说明使用当地货币。
5. **不可估算与缺失字段**：销量或销售额为 `-1` 时标为“无法估算”，不要展示成真实的负销量；`0`、`null`、空数组或缺失字段应标注 N/A 或省略，并解释其含义。
6. **分页与趋势可读性**：搜索最多每页 100 条、最多 200 页，展示当前 `page/pageCount`；趋势不要倾倒原始数组，整理为日期、数值、价格/销售额或 Deal 状态的可读表格，注明趋势范围。
7. **在售与促销状态**：详情中的 `offSale=true` 明确显示为当前不可售；`dealTrend` 中 `1` 表示当天有 Deal、`0` 表示没有，不能把历史 Deal 当作当前促销承诺。
8. **错误与修正建议**：业务失败时展示 `code`/`errcode` 与 `msg`/`errmsg` 的可理解说明，并针对 ASIN 格式、站点代码、日期、queryType/queryValue 格式、页码或额度给出修正建议；不自动连续试探。
9. **数据来源与反馈**：明确标注数据来源为 Sorftime。若用户对结果表示满意、不满、提出建议或报告错误，按相应 reference 的 Feedback API 规则上报，不打断当前结果交付。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`：

- MCP 或 `proxy_call` 缺失：停止业务调用，提示检查 `LinkFox` 配置并重新登录或重载连接；禁止 HTTP fallback。
- MCP 连接 401：按 WorkBuddy 自动授权链路异常处理，提示重新登录、重载连接或联系管理员；不得要求手工 Authorization。
- 代理成功但下游 `errcode=401`：按自动授权或下游认证失败处理，不把 Key/token 放入 `arguments`。
- 下游 `errcode=402` 或积分不足：引导用户访问 `https://agent.linkfox.com/` 自助处理；不得自动查询套餐、下单、支付或轮询。
- 403：按权限错误处理，不归入认证或计费问题。

处理完成后是否重新调用由用户决定；收费查询不得自动重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
