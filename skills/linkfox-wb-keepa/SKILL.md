---
name: linkfox-wb-keepa
display_name: LinkFox Keepa选品
display_name_en: LinkFox Keepa Product Selection
description: 面向亚马逊 Keepa 商品数据的选品与竞品分析能力，支持多条件找品、ASIN 详情查询和商品历史趋势查看。
description_zh: 面向亚马逊商品发现、竞品核查和趋势判断的 Keepa 数据能力，支持按关键词、类目、价格、销量、BSR、评分、评论数、尺寸重量、配送方式等条件筛选商品，按 ASIN 获取结构化商品详情，并查看单个商品的价格、BSR、评分、卖家数和月销量历史。当用户需要 Keepa 选品、ASIN 查询、竞品对比、价格走势、排名趋势、销量趋势或商品历史数据时触发；输出结构化结果、趋势数据、商品链接和可追溯的原始响应。该能力不提供评论正文、关键词搜索量、广告数据、店铺级库存或实时搜索页快照。
description_en: Keepa-based Amazon product discovery and competitor-analysis capability for multi-criteria product screening, structured ASIN lookups, and single-product historical trend analysis. Use it when users need Keepa product selection, ASIN details, competitor comparison, price history, BSR trends, rating or seller-count changes, monthly sales history, or other Amazon product-level history. It returns structured product data, time-series results, product links, and traceable raw responses, but does not provide review text, keyword-volume analytics, advertising data, store-level inventory, or real-time Amazon SERP snapshots.
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


# LinkFox Keepa选品（LinkFox Keepa Product Selection）

本能力用于完成亚马逊商品发现、商品级竞品核查和历史趋势判断：可以先按多维条件筛选候选商品，再按 ASIN 获取结构化详情，或直接查看单个商品的价格、BSR、评分、卖家数和月销量变化。结果包含 Keepa 返回的商品字段、时间序列和商品链接，适合选品初筛、竞品比较和历史表现复盘。

本能力覆盖 3 个子能力，均通过 `LinkFox` 的 `proxy_call` 调用。子能力标识、完整参数、响应字段、错误码和 MCP 示例见 `references/`。

## 能力边界

### 能力范围

- **多条件商品发现**：通过 `proxy_call` 调用 `keepa/productSearch`，按 Amazon 站点、标题关键词、类目、价格、月销量、当前/平均/历史 BSR、评分、评论数、品牌、尺寸重量、配送方式、危险品、变体和缺货比例等条件筛选商品。适用于没有确定 ASIN 时的候选挖掘、低竞争筛选和结构化选品。
- **ASIN 商品详情**：通过 `proxy_call` 调用 `keepa/productRequest`，获取标题、品牌、材质、价格/币种、图片、上架日期、类目、销售排名、当前及近 12 个月月销量、评分、评论数、尺寸重量、配送、卖家数、FBA 费用和利润等结构化字段。适用于已知一个或多个 ASIN 的详情查询和横向比较；单次最多 5 个 ASIN。
- **单商品历史趋势**：通过 `proxy_call` 调用 `keepa/productSeries`，按 1—365 天查看单个 ASIN 的 Buy Box/新品/Deal/Prime/FBA/FBM/优惠券价格、主/子类 BSR、卖家数、评分、评分数和月销量时间序列。适用于价格追踪、排名趋势、促销变化和竞争强度复盘。
- **连续分析与可追溯输出**：可按“搜索候选 → 详情核查 → 必要时查看历史”的顺序使用上述子能力；每次记录精确 `toolName`、原始业务参数、调用时间、下游状态、`costToken` 和必要结果标识。不要假定 MCP 提供本地缓存或响应落盘。
- **多站点映射**：`domain=1/2/3/4/5/6/8/9/10/11/12` 分别对应美国、英国、德国、法国、日本、加拿大、意大利、西班牙、印度、墨西哥、巴西；`productSearch` 文档明确列出至 `11`，使用巴西站前先以对应 reference 的支持范围为准。未指定站点时默认使用美国站 `domain=1`。

### 边界与限制

- **输入与批量**：`productRequest` 的 `asin` 支持逗号分隔的 1—5 个 ASIN，字符串最长 300 字符；`productSeries` 一次只能传一个 ASIN，最多 365 天；`productSearch` 每页最少 50、最多 100 条，`perPage` 不能用来请求小于 50 的页面。
- **搜索条件限制**：`productSearch` 的关键词最多 50 个、最多 1000 字符；每类根/子类目最多 50 个；排序最多 3 条；历史 BSR 月份 `srAvgMonth` 只能使用最近 36 个月内的 `YYYYMM`。价格筛选字段使用最小货币单位，不能把展示价格的小数值直接当作筛选值。
- **历史数据限制**：`history=1` 会显著增加响应体和 Keepa token 消耗；`productSeries` 的采样点按 Keepa 实际捕获变化返回，不保证固定每日一个点。需要多 ASIN 历史曲线时必须逐个调用，不能把多个 ASIN 放入同一 `productSeries` 请求。
- **数据内容边界**：商品详情和搜索结果不返回商品评论正文或评论情感；本能力不提供关键词搜索量/ABA、广告投放与竞价、实时 Amazon 前台 SERP、店铺级销售/库存、Listing 文案优化、供应链履约或法律结论。
- **数据解释**：BSR 数值越小表示排名越好；价格必须结合响应中的 `currency` 展示；字段为 `0`、`-1`、空字符串或缺失时按不可用处理，不得解释为零销量、零费用或已确认属性。
- **认证与消耗**：WorkBuddy 自动注入授权，不要求或接收用户提供 API Key、token 或认证 headers。调用可能消耗积分；失败或空结果不得自动换关键词、翻页、换 ASIN、扩大范围或改参数连续试探；继续调用前应说明额外消耗，由用户决定。
- **非法律/预测结论**：历史价格、BSR、销量和评分只能作为数据观察，不能直接等同于未来销量预测、利润保证、市场容量结论或法律意见。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找月销量高、BSR 低、价格在某区间的产品”“按类目/关键词筛选新品” | `linkfox-keepa-product-search` | 已经有明确 ASIN 时改用 `linkfox-keepa-product-request`；只要历史曲线时改用 `linkfox-keepa-product-series` |
| “查这个 ASIN 的标题、价格、月销量、尺寸、FBA 费用” | `linkfox-keepa-product-request` | 需要价格/排名随时间变化时用 `linkfox-keepa-product-series`；没有 ASIN 而要发现商品时用 `linkfox-keepa-product-search` |
| “比较这几个 ASIN 的当前表现” | `linkfox-keepa-product-request`，一次最多 5 个 ASIN | 要分别比较历史曲线时按 ASIN 逐个调用 `linkfox-keepa-product-series`，并提前说明会产生多次消耗 |
| “看这个 ASIN 的价格历史、BSR 趋势、卖家数或评分变化” | `linkfox-keepa-product-series` | 只需当前详情或近 12 个月月销字段时用 `linkfox-keepa-product-request` 并设置 `history=1` |
| “先找候选，再看候选详情” | 先 `linkfox-keepa-product-search`，再按用户选定 ASIN 调 `linkfox-keepa-product-request` | 需要历史曲线时再单独调用 `linkfox-keepa-product-series`；不要在用户未决定时自动深查全部结果 |
| “要找实际 Amazon 搜索页上出现的商品/关键词排位” | 不适用本能力 | 使用 Amazon 前台搜索能力；Keepa 搜索是数据库条件筛选，不是实时 SERP 模拟 |

选择时先判断用户是否已有 ASIN，再判断要的是“候选列表”“当前结构化字段”还是“随时间变化的曲线”。同时核对站点、批量限制、`history`/`show*` 选项和预计积分消耗；相近需求同时满足时默认推荐上表工具，并把切换原因和额外调用成本讲清楚，由用户决定是否继续。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | `toolName` |
|---|---|---|---|
| `linkfox-keepa-product-request` | 按 ASIN 获取商品详情、当前指标和可选近 12 个月月销 | `references/linkfox-keepa-product-request.md` | `keepa/productRequest` |
| `linkfox-keepa-product-series` | 按单个 ASIN 获取价格、BSR、评分、卖家数和月销量历史 | `references/linkfox-keepa-product-series.md` | `keepa/productSeries` |
| `linkfox-keepa-product-search` | 按关键词、类目、销量、BSR、价格等条件搜索商品 | `references/linkfox-keepa-product-search.md` | `keepa/productSearch` |

## 调用方式

- 固定 MCP Server：`LinkFox`，URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`，唯一工具为 `proxy_call`。
- 外层参数固定为 `{"toolName":"<精确值>","arguments":{...}}`。`arguments` 直接放原接口请求体，不增加 `body`、`data`、`params` 或第二层 `arguments`。
- `toolName` 必须精确使用路由表中的 3 个值，区分大小写且不得带前导 `/`；不得猜测或调用 allowlist 外的 endpoint。
- WorkBuddy 自动注入授权。参数中禁止添加 `headers`、`Authorization`、API Key、token、JWT、手机号或其他凭证，也不要向用户索取。
- 禁止使用 `curl`、`urllib`、`requests`、`httpx` 或其他方式直连旧工具网关；MCP 缺失或失败时不得静默回退 HTTP。
- 先检查 MCP 连接、工具 schema 和 `isError`；代理成功后读取 text/structured content。text 是 JSON 字符串时只解析一次，再检查下游 `errorCode`、`errcode`、`code`、`errmsg` 或 `msg`。
- 单次失败、空结果或结果不理想都不自动重试、改参、翻页或换 ASIN；同一任务内相同 `toolName + arguments` 不得重复调用。再次调用可能重复扣费，须先说明原因并由用户决定。
- 完整参数、响应字段、错误码和 MCP 示例见对应 `references/linkfox-keepa-*.md`；授权异常见 `references/onboarding.md`。Feedback API 是独立公开通道，不通过 `proxy_call`，也不是业务 endpoint。

## 使用示例

以下示例均为 `proxy_call` 的完整参数。真实调用前确认目标站点、输入限制和积分消耗；不要因结果为空自动扩大范围或连续翻页。

### 1. 多条件筛选候选商品

调用 `LinkFox.proxy_call`：

```json
{
  "toolName": "keepa/productSearch",
  "arguments": {
    "domain": "1",
    "categoriesIncludeNames": ["Home & Kitchen"],
    "keyword": "wireless charger -car",
    "monthlySoldGte": 300,
    "currentBuyBoxShippingGte": 1500,
    "currentBuyBoxShippingLte": 5000,
    "currentRatingGte": 4.0,
    "currentCountReviewsLte": 500,
    "buyBoxIsFBA": true,
    "isHazMat": false,
    "perPage": 50,
    "sort": [{"fieldName": "monthlySold", "sortDirection": "desc"}]
  }
}
```

读取 `products[]` 的 ASIN、标题、品牌、价格/币种、`salesRank`、`monthlySalesUnits`、评分、评论数、配送、卖家数和链接，并报告 `total`、`currentPage`、`perPage`、`costToken`。价格筛选字段使用最小货币单位；BSR 越低越好；`perPage` 最多 100，若需要下一页先说明额外调用成本。

### 2. 查询一个或多个 ASIN 的商品详情

调用 `LinkFox.proxy_call`：

```json
{
  "toolName": "keepa/productRequest",
  "arguments": {
    "asin": "B0088PUEPK,B00U26V4VQ,B07M68S376",
    "domain": "3",
    "history": 1
  }
}
```

读取 `products[]` 的标题、品牌、价格、币种、图片、上架日期、类目、当前/30/90/180 天销售排名、当前和近 12 个月月销量、评分、评论数、尺寸、重量、配送、FBA 费用和利润。批量最多 5 个 ASIN，建议先给汇总表，再按需展开单个商品；`history=1` 会增加响应大小和 token 消耗。

### 3. 查看单个 ASIN 的历史趋势

调用 `LinkFox.proxy_call`：

```json
{
  "toolName": "keepa/productSeries",
  "arguments": {
    "asin": "B0DFRJ7WSX",
    "domain": "1",
    "days": 90,
    "showPrice": 1,
    "showPriceDeal": 1,
    "showPriceFba": 1,
    "showPriceFbm": 1,
    "showBsrMain": 1,
    "showSellerCount": 1
  }
}
```

读取 `buyboxPrice`、`price`、`priceDeal`、`priceFba`、`priceFbm`、`bsrMain`、`bsrSub`、`sellerCount`、`rating`、`ratingCount` 和 `monthlySold` 的 `time/value` 数据；BSR 类目序列还要读取 `categoryName` 与 `points`。一次只能查一个 ASIN，`days` 最大 365，采样时间不规则；历史曲线较多时先给趋势摘要和关键拐点。

### 4. 搜索后定向核查

先使用示例 1 获取候选，再由用户指定不超过 5 个 ASIN，使用示例 2 查询详情；只有用户还需要价格或排名曲线时，再对单个 ASIN 使用示例 3。三步会分别计费，不能把搜索结果自动全部深查，也不能把多 ASIN 历史请求合并到 `productSeries`。

## 展示规则

1. **按结果类型呈现**：商品搜索使用表格展示 ASIN、标题、品牌、价格/币种、BSR、月销量、评分、评论数、配送和卖家数；ASIN 详情按 ASIN 分块或先给批量汇总表；历史结果按指标和时间序列展示，并给出趋势摘要。
2. **标注数据来源与时间范围**：明确数据来自 Keepa 对应端点和子能力，详情/搜索标注 `lastUpdate` 或调用快照，历史曲线标注 `domain`、`days` 和数据时间范围，不把不同站点的价格和排名混在一起。
3. **解释 BSR**：展示 `salesRank`、`salesRank30/90/180` 或 `bsrMain/bsrSub` 时明确说明数值越小表示销售排名越好；趋势中“数值下降”代表排名改善，“数值上升”代表排名变差。
4. **规范价格与单位**：价格始终带货币符号或 `currency`；搜索请求的 `currentNew*`、`currentBuyBoxShipping*` 按最小货币单位构造，展示时换算为站点常用格式；尺寸标注毫米并可补充厘米/英寸，重量标注克。
5. **处理历史与缺失字段**：时序时间戳转换为可读日期；长序列总结起止值、整体趋势和显著波动；`0`、`-1`、空字符串或缺失字段按 N/A/不可用展示或省略，不当作真实的零值。
6. **控制列表和图片展示**：搜索结果报告 `total`/`totalCount`、页码和每页条数；大批量详情先展示摘要；有 `imageUrl` 或 `productImageUrls` 时提供可点击图片链接，默认不主动渲染整组图片，除非用户要求。
7. **客观表达分析性质**：竞品比较和趋势判断只基于返回数据；除非用户明确要求，不推导销售保证、利润保证或法律结论。`fbaFees`、`profit` 等字段按原始响应展示，不自行补算未返回的成本。
8. **错误处理与修正建议**：查询失败时展示 `errcode`/`errorCode`/`errmsg` 或 HTTP 状态，针对 ASIN 格式、站点 `domain`、价格单位、日期、分页、图片链接（如有）和参数范围给出修正建议；空结果不自动扩大条件或重试。

## 认证与积分异常

WorkBuddy 自动处理 MCP 授权，禁止要求用户提供 API Key、token、JWT、手机号或认证 headers。遇到异常时先区分错误层级，完整规则见 `references/onboarding.md`。

- **MCP 工具缺失或未连接**：停止业务调用，提示用户检查或重新加载 `LinkFox` 并重启 WorkBuddy；不得改走旧 HTTP 网关。
- **MCP 连接或代理层 401**：提示用户重新登录 WorkBuddy、重载 MCP 连接；仍失败时联系 WorkBuddy 管理员，不得手工填写 Authorization。
- **代理成功但下游业务 401**：按 WorkBuddy 自动授权或下游认证异常报告，不得把 Key 放入 `arguments`。
- **下游业务 402 或积分不足**：引导用户访问 `https://agent.linkfox.com/` 检查积分或套餐；不得自动选套餐、下单、支付、轮询或重试。
- **下游业务 403 和其他错误**：按对应业务 reference 的实际错误处理，不归类为 401 或 402。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
