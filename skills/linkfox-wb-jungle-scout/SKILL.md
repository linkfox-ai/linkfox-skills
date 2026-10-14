---
name: linkfox-wb-jungle-scout
display_name: LinkFox Jungle Scout选品
display_name_en: LinkFox Jungle Scout Product Research
description: 面向亚马逊选品与竞品研究的 Jungle Scout 数据分析能力，按关键词、ASIN、产品筛选、市场份额、历史搜索量和销量估算提供可审计的市场洞察。
description_zh: 面向亚马逊选品决策，提供关键词拓展与反查、搜索量历史趋势、品牌声量与竞争格局、产品数据库筛选和 ASIN 日销量估算。覆盖 10 个 Amazon 站点，返回搜索量、趋势、竞价、排名、产品基本面、SOV、转化和销量时间序列等结构化数据；当用户需要发现产品机会、研究竞品流量、判断关键词竞争或验证销量趋势时触发。查询参数、响应字段、错误处理和 MCP 调用见 references/。
description_en: Amazon product-research capability powered by Jungle Scout data. It provides keyword expansion and reverse-ASIN research, historical search-volume trends, brand Share of Voice and competitive landscape, product-database filtering, and ASIN daily sales estimates across 10 Amazon marketplaces. Use it for product discovery, competitor traffic research, keyword competition assessment, market-gap analysis, or sales-trend validation. Full parameters, response fields, error handling, and MCP calls are in references/.
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


# LinkFox Jungle Scout选品（LinkFox Jungle Scout Product Research）

面向亚马逊选品研究、竞品拆解和市场验证，按用户的问题类型查询 Jungle Scout 数据并输出可复核的表格、趋势或竞争格局。本 WorkBuddy 能力覆盖 6 个子能力和 6 个 API operation。子能力标识必须按下方路由原样使用，完整参数与长字段说明见对应 reference。

## 能力边界

### 能力范围

- **产品机会筛选**：按站点、关键词或类目、价格、月销量、月收入、评论、评分、BSR、LQS、卖家类型、产品尺寸和上架时间筛选亚马逊商品；使用 `linkfox-junglescout-product-database` 和 `tool-jungle-scout/product-database/query`。
- **种子词拓展**：从一个关键词发现相关词、长尾词、搜索量、趋势、排名难度和 PPC 竞价；使用 `linkfox-junglescout-keyword-by-keyword` 和 `tool-jungle-scout/keywords/by-keyword`。
- **竞品 ASIN 反查**：输入最多 10 个 ASIN，查看其自然/广告/综合排名、关键词搜索量、相关度、竞争度和竞价；使用 `linkfox-junglescout-keyword-by-asin` 和 `tool-jungle-scout/keywords/by-asin`。
- **关键词需求趋势**：按周查看单个关键词在指定日期范围内的精确搜索量，判断季节性、增长、下降和波动；使用 `linkfox-junglescout-keyword-history` 和 `tool-jungle-scout/keywords/historical-search-volume`。
- **品牌竞争格局**：分析关键词搜索结果前 3 页的自然、广告和综合品牌 SOV，并查看 30 天搜索量、PPC 竞价中位数及 TOP ASIN 点击/转化；使用 `linkfox-junglescout-keyword-share-of-voice` 和 `tool-jungle-scout/keywords/share-of-voice`。
- **ASIN 销量趋势**：按日查询单个 ASIN 在历史日期区间内的预估销量和最近已知价格，支持总量、均值、峰谷和价格关系分析；使用 `linkfox-junglescout-sales-estimates` 和 `tool-jungle-scout/sales-estimates/query`。
- **站点覆盖**：统一支持 `us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`；未指定站点时使用 `us`。站点名称必须映射为接口代码，不要把本地货币或语言代码误当成站点。
- **审计与复核**：保留每次调用的 `toolName`、`arguments`、`costToken`、更新时间和错误信息；MCP 不自动提供旧脚本的响应落盘或摘要。

### 边界与限制

- **数据性质**：这是 Jungle Scout 的估算/抓取数据，不是亚马逊实时后台数据；关键词历史为 7 天粒度，销量估算为日粒度，SOV 是某一时间点的快照。不能据此承诺实际销量、收入或市场份额。
- **平台范围**：仅处理 Amazon 站点数据；不适用于 Shopee、TikTok Shop、独立站或其他平台，也不执行广告投放、商品上架、订单、库存、物流或供应链操作。
- **参数边界**：种子词拓展和 SOV 每次只接受一个关键词；ASIN 反查每次最多 10 个 ASIN；产品数据库必须指定 `marketplace`；销量估算必须指定 `marketplace`、`asin`、`startDate`、`endDate`；历史搜索量日期范围最长 366 天。
- **日期限制**：销量估算的 `endDate` 必须早于当前日期，不得查询今天或未来；历史搜索量的日期使用 `YYYY-MM-DD`，跨越超过 366 天时拆分请求，并在输出中注明分段。
- **数据内容边界**：不提供评论文本、Listing 全文、实时 BSR 历史、关键词 ABA 排名、实际利润核算或法律/财务结论；`feeBreakdown` 仅在产品数据库响应提供时展示，不能替代完整成本核算。
- **认证与计费**：WorkBuddy 自动注入授权，查询会消耗积分；同一任务相同 `toolName + arguments` 只调用一次。失败、空结果或参数错误时不得自动改词、换 ASIN、翻页或重复试探。
- **结果解释**：`SOV`、搜索量、销量、收入和排名均为数据指标；不得将“竞争低”“高转化”或“值得开发”表述为保证性结论，应说明依据、时间范围和不可用字段。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “帮我找一个品”“按价格、销量、评论筛选产品” | `linkfox-junglescout-product-database` | 已有具体 ASIN 且要看日销量，用 `linkfox-junglescout-sales-estimates`；要看关键词指标，用 `linkfox-junglescout-keyword-by-keyword` |
| “拓展这个种子词”“找长尾词/PPC 词” | `linkfox-junglescout-keyword-by-keyword` | 要看某个词随时间变化，用 `linkfox-junglescout-keyword-history`；已知竞品 ASIN 要反查，用 `linkfox-junglescout-keyword-by-asin` |
| “这个 ASIN 有哪些流量词”“比较几个竞品 ASIN 的关键词” | `linkfox-junglescout-keyword-by-asin` | 只给关键词、没有 ASIN 时用 `linkfox-junglescout-keyword-by-keyword` |
| “这个词过去几个月搜索量如何”“有没有季节性” | `linkfox-junglescout-keyword-history` | 只想找相关词用 `linkfox-junglescout-keyword-by-keyword`；要品牌占比用 `linkfox-junglescout-keyword-share-of-voice` |
| “这个关键词谁占据搜索结果”“广告位被谁占了” | `linkfox-junglescout-keyword-share-of-voice` | 要多关键词趋势比较时分别调用 history；要单品销量时用 sales estimates |
| “这个 ASIN 每天卖多少”“看最近 30 天销量” | `linkfox-junglescout-sales-estimates` | 要按市场条件发现多个产品用 product database；要 ASIN 关键词结构用 keyword-by-asin |

选择思路：先判断输入主体是“产品筛选、种子关键词、ASIN、单关键词时间序列、品牌竞争格局”中的哪一种，再判断用户要的是列表、趋势还是份额。相近需求不能用一个端点替代：搜索量历史不是种子词拓展，日销量也不是产品数据库的月销量。一个请求若同时需要多个层面，先完成主问题；追加端点会产生额外积分消耗，需先说明新增查询范围和成本风险，由用户决定是否继续。

## 业务需求路由速查

| 子能力 | reference | 原 endpoint | 精确 `toolName` | 本地辅助 |
|---|---|---|---|---|
| `linkfox-junglescout-product-database` | `references/linkfox-junglescout-product-database.md` | `/tool-jungle-scout/product-database/query` | `tool-jungle-scout/product-database/query` | 无 |
| `linkfox-junglescout-keyword-by-keyword` | `references/linkfox-junglescout-keyword-by-keyword.md` | `/tool-jungle-scout/keywords/by-keyword` | `tool-jungle-scout/keywords/by-keyword` | 无 |
| `linkfox-junglescout-keyword-by-asin` | `references/linkfox-junglescout-keyword-by-asin.md` | `/tool-jungle-scout/keywords/by-asin` | `tool-jungle-scout/keywords/by-asin` | 无 |
| `linkfox-junglescout-keyword-history` | `references/linkfox-junglescout-keyword-history.md` | `/tool-jungle-scout/keywords/historical-search-volume` | `tool-jungle-scout/keywords/historical-search-volume` | 无 |
| `linkfox-junglescout-keyword-share-of-voice` | `references/linkfox-junglescout-keyword-share-of-voice.md` | `/tool-jungle-scout/keywords/share-of-voice` | `tool-jungle-scout/keywords/share-of-voice` | 无 |
| `linkfox-junglescout-sales-estimates` | `references/linkfox-junglescout-sales-estimates.md` | `/tool-jungle-scout/sales-estimates/query` | `tool-jungle-scout/sales-estimates/query` | 无 |

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName` 使用上表 endpoint 去掉前导 `/` 的精确值，区分大小写；`arguments` 直接使用对应 reference 的请求对象。
- 禁止额外包裹 `body`、`params`、`data` 或另一层 `arguments`。WorkBuddy 自动注入 Authorization；不得传 headers、API Key、token、JWT、手机号或其他凭证。
- 禁止通过 `urllib`、`requests`、`httpx`、旧查询脚本或其他方式直连工具网关；MCP 缺失时不得 HTTP fallback。
- 收费调用失败、空结果或不理想时不得自动改词、换 ASIN、翻页或重试；同一任务相同 `toolName + arguments` 只调用一次。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errorCode` / `code` 与 `errmsg` / `msg`。
- MCP 不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。结果追溯依靠调用参数和返回中的 `costToken`、更新时间与业务字段。
- 完整参数、响应、成本、错误与 Feedback 规则见对应 reference；认证错误分层见 `references/onboarding.md`。

```json
{"mcpServers":{"LinkFox":{"type":"streamableHttp","url":"https://mcp-tool-gateway.linkfox.com/mcp/any-tool"}}}
```

## 使用示例

以下示例使用接口真实字段。示例中的 `B0D1234567` 仅作为 10 位 ASIN 格式示例；执行前应替换为目标 ASIN。每次实际调用前说明积分消耗风险，失败或空结果不自动重试。

### 1. 产品机会筛选

`product-database/query`：

```json
{
  "marketplace": "us",
  "includeKeywords": "phone stand",
  "minPrice": 15,
  "maxPrice": 50,
  "minSales": 300,
  "maxReviews": 500,
  "minRating": 4.0,
  "sellerTypes": "fba",
  "productTiers": "standard",
  "sort": "-sales",
  "needCount": 20
}
```

重点读取 `productDatabaseList[]` 的 `title`、`brand`、`price`、`approximate30DayUnitsSold`、`approximate30DayRevenue`、`productRank`、`reviews`、`rating`、`listingQualityScore`、`numberOfSellers` 和 `feeBreakdown`。品类筛选时 `categories` 必须是目标站点的英文标准主分类名；关键词字段最多各 100 项、每项最长 50 字符。

### 2. 种子关键词拓展

`keywords/by-keyword`：

```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minWordCount": 3,
  "minMonthlySearchVolumeExact": 1000,
  "maxOrganicProductCount": 500,
  "sort": "-monthly_search_volume_exact",
  "needCount": 50
}
```

重点读取 `keywordInfoList[]` 的 `name`、精确/广泛搜索量、`monthlyTrend`、`quarterlyTrend`、`easeOfRankingScore`、`organicProductCount`、`ppcBidExact` 和 `ppcBidBroad`。`searchTerms` 只能是一个种子词；相关词扩展不是历史趋势查询。

### 3. ASIN 反查关键词

`keywords/by-asin`：

```json
{
  "marketplace": "us",
  "asins": ["B0D1234567", "B0D7654321"],
  "includeVariants": true,
  "minMonthlySearchVolumeExact": 5000,
  "needCount": 50,
  "sort": "-relevancy_score"
}
```

重点读取 `keywordInfoList[]` 的 `name`、`organicRank`、`sponsoredRank`、`overallRank`、`relevancyScore`、`easeOfRankingScore`、搜索量、PPC 出价和 `competitorOrganicRank`/`competitorSponsoredRank`。一次最多 10 个 ASIN，适合竞品流量词对比，不适合从文字种子词找新词。

### 4. 关键词历史搜索量

`keywords/historical-search-volume`：

```json
{
  "marketplace": "us",
  "keyword": "christmas decorations",
  "startDate": "2025-09-01",
  "endDate": "2026-08-27"
}
```

重点读取 `historicalSearchVolumeList[]` 的 `estimateStartDate`、`estimateEndDate` 和 `estimatedExactSearchVolume`，以周为点绘制趋势并标出峰谷。日期跨度不能超过 366 天；该能力只返回精确搜索量，不返回 PPC 或关键词建议。

### 5. 关键词品牌 SOV

`keywords/share-of-voice`：

```json
{
  "marketplace": "de",
  "keyword": "kabellose kopfhörer"
}
```

重点读取 `shareOfVoice.brands[]` 的 `brand`、`organicWeightedSov`、`sponsoredWeightedSov`、`combinedWeightedSov`、平均位置和平均价格，以及 `topAsins[]` 的 `asin`、`clicks`、`conversions`、`conversionRate`。SOV 值是 0–1，展示时转为百分比；数据只覆盖搜索结果前 3 页且是快照，不能当作历史份额。

### 6. ASIN 日销量估算

`sales-estimates/query`：

```json
{
  "marketplace": "us",
  "asin": "B0D1234567",
  "startDate": "2026-08-01",
  "endDate": "2026-08-27"
}
```

重点读取 `salesEstimateList[].dailyEstimates[]` 的 `date`、`estimatedUnitsSold` 和 `lastKnownPrice`，汇总总销量、日均销量、峰谷日期，并在有充分数据时估算“销量 × 最近已知价格”的区间收入；该收入不是平台结算收入。每次只能查询一个 ASIN，`endDate` 必须早于当前日期，价格单位为 USD。

## 展示规则

1. **先说明查询上下文**：展示站点、关键词或 ASIN、日期范围、排序/筛选条件、数据更新时间和 `costToken`；若字段缺失、响应为空或数据非实时，明确标注。
2. **产品筛选用表格**：默认列出标题、品牌、价格、近 30 天预估销量、近 30 天预估收入、BSR、评论、评分和 LQS；用户问利润时再展开 `feeBreakdown`，并说明价格和费用口径。
3. **关键词列表按意图裁剪**：拓词侧重精确/广泛搜索量、趋势和排名难度；广告研究侧重 `ppcBidExact`、`ppcBidBroad`、`spBrandAdBid`；ASIN 反查侧重自然/广告排名、相关度和竞品对比。
4. **趋势使用时间序列**：历史搜索量和日销量优先用折线图或时间线，附精确数据表；标出峰值、谷值、趋势方向和日期，不把短期波动解释为确定性季节规律。
5. **SOV 用百分比和双层表格**：品牌表按 `combinedWeightedSov` 降序，突出前 5 个品牌；分别展示自然、广告、综合 SOV 和 TOP 3 ASIN 点击/转化，不把加权 SOV 与基础 SOV 混为一谈。
6. **机会判断保持客观**：低评论高销量、高 LQS、低 `easeOfRankingScore` 等只标记为候选信号；同时呈现数据时效、样本范围和可能缺失，不直接保证蓝海、利润或转化。
7. **不可用值不误读**：值为 `0`、`-1`、空字符串或缺失时标为 `N/A` 或省略，不能当作真实零值；价格、收入、销量估算与 PPC 竞价的货币/单位要写清楚。
8. **错误要可行动**：依据 `errcode`/`errorCode`/`errmsg` 说明原因。ASIN、站点、日期跨度、类目名、关键词单值和必填字段错误时给出具体修正；401/402 或余额提示转到认证积分章节，403 不归入认证/余额处理。
9. **数据来源与反馈**：说明结果来自 Jungle Scout 对应端点；用户反馈结果不准确、意图不匹配、抱怨、建议或表扬时，按对应 reference 的 Feedback API 规则记录，不中断当前结果交付。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`：MCP 缺失时停止并提示配置；MCP 连接 401 按 WorkBuddy 自动授权链路异常处理；代理成功后的下游 401、402、403 与其他业务错误分别处理。不得要求或接收用户手工提供 Authorization、API Key、token、JWT 或手机号，不得自动购买套餐、支付或轮询订单。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
