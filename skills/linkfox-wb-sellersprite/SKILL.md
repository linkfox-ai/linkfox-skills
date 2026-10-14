---
name: linkfox-wb-sellersprite
display_name: LinkFox 卖家精灵选品
display_name_en: LinkFox SellerSprite Product Selection
description: 面向亚马逊选品与市场判断的卖家精灵数据分析能力，覆盖商品筛选、竞品对标、类目市场评估和 ASIN 流量关键词反查。
description_zh: 面向亚马逊卖家的卖家精灵数据分析能力：按关键词、ASIN、卖家、品牌或类目发现并筛选商品，评估细分类目市场规模与竞争结构，查看节点统计看板，并反查 ASIN 的自然与广告流量关键词。当用户需要亚马逊选品、竞品研究、市场机会筛选、类目质量判断或 ASIN 流量词分析时触发。支持实时近 30 天与可用历史月份数据；完整参数、响应字段和错误处理见 references/。
description_en: SellerSprite data analysis for Amazon product selection and market decisions. discover and filter products by keyword, ASIN, seller, brand, or category; evaluate category-market size and competitive structure; inspect node-level market statistics; and reverse-lookup an ASIN's organic and advertising traffic keywords. Use when the user needs Amazon product selection, competitor research, market opportunity screening, category quality assessment, or ASIN traffic-keyword analysis. Supports near-real-time 30-day data and available historical monthly snapshots. Full parameters, response fields, and error handling are in references/.
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


# LinkFox 卖家精灵选品（LinkFox SellerSprite Product Selection）

通过卖家精灵为亚马逊选品提供从商品发现、竞品对标到类目市场判断和流量结构分析的一体化数据支持。根据用户的对象和问题选择商品级、市场级、节点统计或 ASIN 流量分析路径，输出带时间口径、站点、关键指标、分页信息和数据成本字段的结构化结果。当前包含 5 个子模块和 5 个只读 API operation；每个子模块的完整细节归档在对应 reference 中。

## 能力边界

### 能力范围

- **商品搜索与选品筛选**：使用 `linkfox-sellersprite-product-search` 与 `sellersprite/productSearch`，按关键词、类目、价格、月销量、销售额、BSR、毛利率、评分、评论数、配送方式、卖家/品牌、徽章、上架时间、重量和变体等条件筛选商品；参数与字段见 `references/linkfox-sellersprite-product-search.md`。
- **竞品查询与对标**：使用 `linkfox-sellersprite-competitor-lookup` 与 `sellersprite/competitor-lookup`，通过 ASIN、关键词、卖家、品牌或类目查找竞品，比较月销量、销售额、BSR、价格、评分、配送、徽章和增长趋势，并可查看变体或历史快照；参数与字段见对应 reference。
- **细分类目市场筛选**：使用 `linkfox-sellersprite-market-research` 与 `sellersprite/market/research`，按类目节点或类目关键字筛选市场，评估规模、集中度、履约结构、新品、价格、评分、毛利、BSR、重量和体积等聚合指标。
- **节点市场统计看板**：使用 `linkfox-sellersprite-market-statistics` 与 `sellersprite/market/statistics`，针对指定节点输出市场总体、头部 Listing 前 N 名和新品口径统计。
- **ASIN 流量关键词反查**：使用 `linkfox-sellersprite-traffic-keyword` 与 `sellersprite/traffic/keyword`，按 ASIN 查看关键词、自然位、广告位、流量与转化类型、搜索量、购买量、PPC 竞价和流量分布。
- **时间与站点维度分析**：商品与竞品查询支持 `nearly` 近 30 天数据和已存在的 `yyyyMM` 月度快照；市场列表、市场统计和流量关键词支持各自 schema 允许的月份。应始终在结果中标明 marketplace 与数据月份，不把不同端点的时间口径混为一谈。

### 边界与限制

- **认证必需**：WorkBuddy 自动注入 MCP Authorization；MCP 401 与代理成功后的下游 401 分层处理，禁止要求用户提供凭证。
- **调用与数据成本**：调用会消耗积分；同一任务中相同 `toolName + arguments` 只调用一次。失败或空结果不得自动更换关键词、翻页、改站点或连续试探参数；继续查询前应先说明额外消耗并由用户决定。
- **站点差异**：竞品查询支持 US、UK、DE、FR、JP、CA、IT、ES、MX、AU、TR、IN；商品搜索仅支持 US、UK、DE、FR、JP、CA、IT、ES、MX、IN；市场列表、市场统计和流量关键词支持 US、JP、UK、DE、FR、IT、ES、CA、IN。未指定且端点允许时默认 US。
- **输入要求**：市场统计必须提供 `marketplace` 与合法 `nodeIdPath`；流量关键词必须提供 `marketplace` 与单个 `asin`；市场列表至少需要 `marketplace`；商品搜索和竞品查询的可选筛选字段应按对应 schema 传入。`asinList` 单次最多 40 个，分页上限和返回数量以对应端点为准。
- **比例与枚举**：市场列表中的 GoodsCrn、BrandCrn、SellerCrn、EbcProportion、FbaProportion、FbmProportion、AmazonSelfProportion 的 `min*`/`max*` 必须传 0～1 小数；商品搜索使用重量筛选时必须同时提供 `weightUnit`，子类目 BSR 筛选需 `filterSubNode=true`，上架月份只允许 1、3、6、12、24。
- **历史限制**：只可查询数据源已有的历史月份，不能查询未来；市场类端点通常最多支持当前月往前约 24 个月，流量关键词历史查询必须使用 `yyyyMM`。`minAmzUnit`/`maxAmzUnit` 只适用于近 30 天风格的数据。
- **不适用范围**：不提供 ABA 搜索词历史分析、独立的关键词拓展或全市场搜索量研究、不管理 PPC 广告活动、不读取评论正文或做评论情感分析、不撰写 Listing、不提供供应商与制造成本、物流库存、订单、账号健康、平台政策合规或其他平台数据。
- **分析边界**：销量、销售额、毛利率、BSR、流量和竞争指标是数据源估算或快照，不等同于财务、广告归因或法律结论；跨端点比较必须先核对站点、时间、聚合层级和字段单位。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “帮我按价格、销量、毛利率筛选商品”“找新品机会/低竞争商品” | `linkfox-sellersprite-product-search` | 如果用户要从某关键词、ASIN、卖家或品牌定位竞品，用 `linkfox-sellersprite-competitor-lookup`；如果要按类目整体筛市场，用 `linkfox-sellersprite-market-research` |
| “找这个关键词/ASIN/品牌/卖家的竞品”“做竞品对标” | `linkfox-sellersprite-competitor-lookup` | 如果问题是商品库多条件筛选而非竞品反查，用 `linkfox-sellersprite-product-search`；如果问题是整个类目市场结构，用市场类能力 |
| “筛选值得进入的细分类目/市场”“看市场集中度、新品比例” | `linkfox-sellersprite-market-research` | 如果已知一个节点、只要快速看总体和头部/新品指标，用 `linkfox-sellersprite-market-statistics`；如果要落到具体商品明细，用 `linkfox-sellersprite-product-search` |
| “看某个类目的市场质量/头部 Listing/新品统计” | `linkfox-sellersprite-market-statistics` | 如果还没有合法节点路径且需要筛选多个候选市场，用 `linkfox-sellersprite-market-research`；如果要逐商品列表，用 `linkfox-sellersprite-product-search` |
| “反查这个 ASIN 的流量词/自然词/广告词”“看转化优质词” | `linkfox-sellersprite-traffic-keyword` | 只有在问题转为商品筛选或竞品发现时才切换到商品搜索/竞品查询；它不替代无 ASIN 的关键词研究 |
| “这个市场能不能做”但同时需要商品与类目两层证据 | 先用 `linkfox-sellersprite-market-research` 或 `linkfox-sellersprite-market-statistics` 判断市场层级，再由用户决定是否调用商品搜索或竞品查询 | 不要默认连续调用多个端点；应说明每一步新增的数据范围与积分消耗，由用户决定 |

选择时优先判断分析对象：具体商品/商品集合使用商品级端点，关键词或卖家维度的竞品发现使用竞品查询，类目候选筛选使用市场列表，单节点概览使用市场统计，单个 ASIN 的词和排名使用流量关键词。多个路径都可行时，比较出入参、结果层级、时间口径和调用成本，向用户推荐默认路径并让用户决定是否继续。

## 业务需求路由速查

| 子能力 | reference | 精确 `toolName` | 风险 |
|---|---|---|---|
| 竞品查询与历史对标 | `references/linkfox-sellersprite-competitor-lookup.md` | `sellersprite/competitor-lookup` | 收费只读 |
| 商品搜索与多条件筛选 | `references/linkfox-sellersprite-product-search.md` | `sellersprite/productSearch` | 收费只读 |
| 类目市场列表筛选 | `references/linkfox-sellersprite-market-research.md` | `sellersprite/market/research` | 收费只读 |
| 节点市场统计 | `references/linkfox-sellersprite-market-statistics.md` | `sellersprite/market/statistics` | 收费只读 |
| ASIN 流量关键词反查 | `references/linkfox-sellersprite-traffic-keyword.md` | `sellersprite/traffic/keyword` | 收费只读 |

无本地辅助脚本；全部工具网关业务调用只使用 MCP。

## 调用方式

- MCP server：`LinkFox`
- URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- allowlist：`sellersprite/competitor-lookup`、`sellersprite/productSearch`、`sellersprite/market/research`、`sellersprite/market/statistics`、`sellersprite/traffic/keyword`。
- 调用结构：`{"toolName":"<精确 endpoint>","arguments":{<原请求参数>}}`；`toolName` 区分大小写，`arguments` 不额外包装。
- WorkBuddy 自动注入 Authorization；配置与参数不得加入 headers、API Key、token、JWT、手机号或其他凭证。
- 禁止 curl、`urllib`、`requests`、`httpx` 等直连工具网关；MCP 缺失时停止，不得 HTTP fallback。
- 新链路不提供旧脚本的 24 小时缓存、自动落盘或 stdout 摘要。同一任务以 `toolName + arguments` 去重，保留查询参数摘要和必要结果标识追溯。
- 先检查 MCP/schema/`isError`，再读代理内容；text JSON 只解析一次；最后检查下游业务错误字段。
- 完整参数、响应、枚举、错误与成本以对应 reference 为准。

## 使用示例

以下示例均为接近可执行的 JSON 请求；`B0XXXXXXXXX` 需替换为真实 ASIN，类目 `nodeIdPath` 需替换为数据源认可的节点路径。调用前应确认站点、时间口径和积分消耗。

### 1. 关键词竞品发现（竞品查询）


```json
{
  "marketplace": "US",
  "keyword": "wireless earbuds",
  "matchType": 1,
  "dataSnapshotMonth": "nearly",
  "order": {"field": "total_units", "desc": "true"},
  "page": 1,
  "size": 20
}
```

重点出参是 `products[]`（`asin`、`title`、`price`、`monthlySalesUnits`、`monthlySalesRevenue`、`bsr`、`rating`、`ratings`、`profit`、`fulfillment`、`badge*`）和 `total`、`costToken`。关键词应使用目标站点语言；`size` 为 10～100，最多一次查询 40 个 ASIN，历史月份只能使用已有快照。

### 2. 多条件商品选品（商品搜索）


```json
{
  "marketplace": "US",
  "keyword": "desk organizer",
  "matchType": 1,
  "minUnits": 300,
  "minPrice": 15,
  "maxPrice": 50,
  "minProfit": 40,
  "sellerNation": "CN",
  "fulfillment": "FBA",
  "listedWithinLastMonths": 6,
  "order": {"field": "profit", "desc": "true"},
  "page": 1,
  "size": 20
}
```

重点出参是 `products[]` 商品明细、`total`、`dataSnapshotMonth`、`nodeLabel` 和 `costToken`。`profit` 是按数据源估算的百分比，不是承诺利润；若加重量条件必须传 `weightUnit`，`minAmzUnit`/`maxAmzUnit` 不适用于历史月度快照。

### 3. 细分类目市场筛选（市场列表）


```json
{
  "marketplace": "US",
  "month": "nearly",
  "minAvgRevenue": 10000,
  "minAvgUnits": 500,
  "maxGoodsCrn": 0.4,
  "maxSellerCrn": 0.5,
  "minNewProportion": 10,
  "orderField": "total_amount",
  "orderDesc": true,
  "page": 1,
  "size": 50
}
```

重点出参是 `data[]`（节点路径、`totalProducts`、`sellers`、`brands`、`avgUnits`、`avgRevenue`、`avgPrice`、`avgRating`、`avgProfit`、比例和 `top10Images`）以及 `total`、`costToken`。示例中的集中度参数使用 0～1 小数；返回字段中带 `(%)` 的比例以响应口径为准，`size` 最大 200，历史月份通常限于近 24 个月。

### 4. 单节点市场质量看板（市场统计）


```json
{
  "marketplace": "US",
  "nodeIdPath": "172282:281407",
  "month": "nearly",
  "topN": 10,
  "newProduct": 6
}
```

重点出参是 `data[]` 中的总体指标（`totalProducts`、`sellers`、`brands`、`avgUnits`、`avgRevenue`、`avgPrice`、`avgRating`、`avgBsr`）、头部指标（`hl*`）和新品指标（`new*`），并报告 `topN`、`newProduct`、marketplace、月份和 `costToken`。`marketplace` 与 `nodeIdPath` 为必填；节点路径非法或未提供时不能据此推断市场结果。

### 5. ASIN 流量词反查（流量关键词）


```json
{
  "marketplace": "US",
  "asin": "B0XXXXXXXXX",
  "month": "202507",
  "trafficKeywordTypes": "primary,precise",
  "conversionKeywordTypes": "excellent,stable",
  "page": 1,
  "size": 100,
  "orderField": "rankPosition",
  "orderDesc": false
}
```

重点出参是 `data[]`（`keyword`、`trafficKeywordType`、`conversionKeywordType`、`badges`、`rankPosition`、`adPosition`、`searches`、`purchases`、`purchaseRate`、`trafficPercentage`、`naturalRatio`、`adRatio`、`bid`、`latest*Ads`）以及 `summaryList`、`total`、`costToken`。流量关键词历史查询必须传 `yyyyMM`；每页最多 100 条、最多查询 2000 条，不能把该接口当成无 ASIN 的全站关键词研究。

### 6. ASIN、节点与历史快照的替代请求

竞品查询也可直接按 ASIN 或卖家筛选，例如：

```json
{
  "marketplace": "DE",
  "asinList": "B072MQ5BRX,B08N5WRWNW",
  "showVariation": "Y",
  "dataSnapshotMonth": "202412",
  "order": {"field": "bsr_rank", "desc": "false"},
  "size": 20
}
```

市场列表可用 `departmentKeyword` 或 `nodeIdPath` 限定类目；商品搜索可用 `nodeLabel`、`nodeIdPath`、`includeBrands`/`excludeBrands`、`badgeBestSeller` 等字段；流量关键词可用 `badges`、`keyword`、`orderField` 等字段。具体枚举和边界必须以对应 reference 为准，改变月份、分页或筛选条件都可能形成新的计费请求。

## 展示规则

1. **先呈现查询口径**：在结果开头标明业务能力、端点、marketplace、查询月份（`nearly` 表示最近 30 天；历史查询写出 `yyyyMM`）、页码/总数，以及用户实际传入的关键筛选条件。
2. **客观呈现**：商品或竞品结果优先用表格展示 ASIN、标题、价格/币种、月销量、月销售额、BSR、评分、评分数、毛利率、配送方式和品牌；市场结果优先展示节点、商品/卖家/品牌数量、平均销量/销售额、集中度、新品占比；流量结果优先展示关键词、自然位、广告位、流量类型、转化类型、搜索量和流量占比。
3. **标明数据来源与层级**：说明数据来自卖家精灵的商品搜索、竞品查询、市场列表、市场统计或流量关键词端点；区分商品级 `products[]`、市场级 `data[]` 和关键词级 `data[]`，不要把聚合指标写成单个商品的事实。
4. **解释关键指标**：BSR 数值越低通常代表类目销售表现越强；BSR 增长为正不等于变好，应结合接口字段说明排名方向；`profit` 是估算毛利率；市场集中度和结构占比按入参/响应单位分别解释，避免把 0～1 小数直接展示成 0.4% 而应说明为 40%。
5. **突出可读信号**：对 Best Seller、Amazon's Choice、New Release、A+、视频等徽章做清晰标记；对自然位、广告位、自然/广告流量占比和转化类型分栏；对 `topN` 与 `newProduct` 明确说明头部和新品统计口径。
6. **处理不可用字段**：值为 `0`、`-1`、空字符串或缺失时标记为 N/A 或省略，不把占位值当作真实价格、费用、排名、销量或比例；保留原始数值单位和币种。
7. **分页与时间提示**：当 `total` 大于当前页返回数量时，说明总结果数和当前页，并等待用户决定是否翻页；历史快照和近 30 天结果不得混排，跨月或跨端点比较须写明时间窗。
8. **错误与修正建议**：按 `errcode`/`errorCode`、`errmsg`/`message` 和 HTTP 状态说明失败原因；参数问题给出具体修正（ASIN、站点、节点路径、月份、枚举、分页、重量单位或集中度刻度），401/402 与余额问题转到 onboarding，不要静默重试。
9. **不越界解读**：除非用户明确要求，不输出主观商业结论；即使用户要求建议，也要把推断与原始数据分开，并提醒 SellerSprite 估算数据不构成财务、广告归因或法律意见。

## 解决认证和积分问题

读取 `references/onboarding.md`。MCP/`proxy_call` 缺失、MCP 连接 401、代理成功后的下游 401、下游 402 和 403 必须分层处理；不得要求用户配置 MCP Authorization 或把凭证放进 `arguments`。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
