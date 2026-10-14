---
name: linkfox-wb-walmart-product-selection
display_name: LinkFox 沃尔玛选品
display_name_en: LinkFox Walmart Product Selection
description: 沃尔玛商品搜索、筛选和单品深度调研能力，用于发现、比较和评估可开发商品。
description_zh: 面向沃尔玛市场的商品选品与竞品调研能力：按关键词或类目检索当前商品列表，比较价格、评分、卖家、库存与配送信息，并按指定 Item ID 深查商品属性、Listing 质量、销量估算、历史价格和销量走势。当用户要做沃尔玛选品、竞品发现、价格对比、单品机会判断或趋势核查时触发；完整参数、响应字段与错误处理见 references/。
description_en: Walmart product selection and competitor-research capability for discovering and evaluating current listings, comparing price, ratings, sellers, stock and shipping, and deep-diving into a specified Item ID for product attributes, listing quality, estimated sales, historical prices and sales trends. Use it for Walmart product research, competitor discovery, price comparison, opportunity evaluation, or trend checks; full parameters, response fields, and error handling are in references/.
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


# LinkFox 沃尔玛选品（LinkFox Walmart Product Selection）

面向沃尔玛卖家、选品员和市场研究人员，完成从当前商品发现到单品深查的选品判断：先按关键词或类目获取 Walmart.com 当前 listing，再针对明确的数值 Item ID 查看商品属性、Listing 质量、销量估算以及可用的价格/销量历史。当前覆盖 **2 个子能力、2 个 API/operation**：`linkfox-walmart-search`（列表检索）和 `linkfox-wallysmarter-product-detail`（单品详情与趋势）。

## 能力边界

### ✅ 能力范围

- **沃尔玛商品发现与列表筛选**（`linkfox-walmart-search`）：通过 `walmart/search` 按 `keyword` 或 `categoryId` 浏览当前商品，使用价格区间、排序、facet、店铺、设备和 NextDay 等条件缩小候选集；返回标题、价格、评分、评价数、卖家、商品链接、广告/库存/配送和变体信息。
- **当前 listing 对比**（`linkfox-walmart-search`）：比较 `price`/`wasPrice`、`rating`/`reviews`、`sellerName`、`shippingPrice`、`freeShipping`、`twoDayShipping` 和 `outOfStock` 等字段，支持最多 100 页的分页查看；`best_seller` 只表示当前搜索排序，不等于历史销量数据。
- **沃尔玛单品深度调研**（`linkfox-wallysmarter-product-detail`）：以 Walmart 数值 Item ID 调用 `wallysmarter/productDetail`，读取品牌、售价、评分、评论量、销量估算、收入估算、卖家、WFS/Marketplace、部门、Listing/内容质量分、库存和商品时间戳。
- **单品价格与销量趋势**（`linkfox-wallysmarter-product-detail`）：`includeStats=true` 时读取 `stats.price` 与 `stats.sales` 的 UTC 日期序列，概括价格变化和销量变化；历史覆盖取决于 WallySmarter 的跟踪数据。
- **搜索到深查的选品链路**：从列表结果的数值 `usItemId` 或商品 URL 中取得 Item ID，再逐个调用单品端点核查候选；列表和详情是独立调用，需分别记录返回的 `costToken`。认证与积分异常规则见 `references/onboarding.md`。

### ❌ 边界与限制

- **认证边界**：Authorization 由 WorkBuddy 自动注入；不得要求用户提供 Key、token、JWT 或手机号，也不得将凭证或 `headers` 放入 `arguments`。
- **数据时效**：搜索和商品属性是当前数据；历史价格/销量仅在详情请求开启统计且 WallySmarter 有跟踪覆盖时可用，不保证覆盖所有商品或全部历史日期。
- **输入边界**：列表搜索至少提供 `keyword` 或 `categoryId`；`keyword` 最大 1024 字符，`page` 为 1–100。详情一次只接受一个数值 `productId`/Item ID，不接受批量数组。
- **结果边界**：列表端点提供评分和评价数量，但不提供评论正文；详情的 `salesEstimate`/`revenue` 是估算值，不是卖家后台真实销量或收入。
- **输出边界**：详情返回混合结构化与非结构化数据，不支持通过 `@智能数据查询` 做二次分析；需要多个商品时必须逐个调用并注意额外消耗。
- **不在范围内**：Walmart 卖家账号、广告投放、订单或购买记录、评论文本情感分析、历史价格跟踪（列表端点）、实时库存/配送承诺、供应商采购、店铺级经营报表和法律/财务结论。
- **分析口径**：接口只提供客观数据。除非用户明确要求，不把排序、评分或估算销量直接表述为保证成功的开发建议；选品结论必须标注数据时间和估算性质。

## 工具选择指南

按用户目标先选择检索深度，再到【业务需求路由速查】定位端点、脚本和 reference。两个端点可串联，但不要用详情端点替代列表搜索，也不要用列表当前字段推导历史趋势。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “在 Walmart 搜索某个关键词/类目”“找一批候选产品” | `linkfox-walmart-search` | 已有明确数值 Item ID 且需要属性或趋势时换用 `linkfox-wallysmarter-product-detail` |
| “找便宜的/最畅销的/某价格带的商品”“比较 Walmart listing” | `linkfox-walmart-search`，使用 `minPrice`/`maxPrice`/`sort`/`page` | 需要单个商品的历史价格或销量时再对候选逐个做详情查询 |
| “查 Walmart 商品详情”“看品牌、卖家、WFS、Listing 分” | `linkfox-wallysmarter-product-detail` | 只有关键词、类目或模糊商品名时先用 `linkfox-walmart-search` 找到数值 Item ID |
| “这个商品最近价格/销量走势如何”“销量估算是多少” | `linkfox-wallysmarter-product-detail`，默认 `includeStats=true` | 只需当前属性且希望减少返回数据时设 `includeStats=false`；不要用搜索结果替代趋势 |
| “先找品，再判断哪些值得深查” | 先 `linkfox-walmart-search`，再对用户选定的 Item ID 调详情 | 用户只要列表或只给一个 Item ID 时只调用对应端点，避免无必要消耗 |
| “查实体店某店库存/移动端展示/NextDay 配送” | `linkfox-walmart-search`，使用 `storeId`/`device`/`nextDayEnabled` | 详情端点不提供实时配送或店铺级库存判断 |

### 工具选择思路

- 需求涉及**发现、过滤、排序、分页或多个商品横向比较**时，优先列表检索；需要更细的单品字段或历史序列时，再根据候选的数值 Item ID 进入详情。
- 需求涉及**一个明确商品的当前属性、销量估算、Listing 分或历史走势**时，直接使用详情；`includeStats=false` 适合只看属性，`true` 适合趋势判断。
- 搜索与详情返回字段、成本和时间窗不同。满足程度相同的情况下采用默认推荐，并在串联调用前告知用户会发生额外调用，由用户决定是否继续。

## 业务需求路由速查

下表覆盖本能力的全部业务子能力和 API/operation；完整参数、响应字段、错误码和 MCP 示例见对应 reference。

| 子能力 | 业务能力 | reference | 原 endpoint | 精确 `toolName` | 本地脚本 |
|---|---|---|---|---|---|
| `linkfox-walmart-search` | 沃尔玛商品列表搜索、筛选、排序与分页 | `references/linkfox-walmart-search.md` | `/walmart/search` | `walmart/search` | 无 |
| `linkfox-wallysmarter-product-detail` | 沃尔玛单品详情、销量估算、价格/销量历史 | `references/linkfox-wallysmarter-product-detail.md` | `/wallysmarter/productDetail` | `wallysmarter/productDetail` | 无 |

上表也是本 skill 的完整 `toolName` allowlist；名称区分大小写，禁止调用其他 endpoint。认证和积分异常规则归档于 `references/onboarding.md`。

## MCP 调用方式

- **MCP server**：`LinkFox`，类型 `streamableHttp`，URL 为 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`。
- **唯一工具**：`proxy_call`。调用结构固定为 `{"toolName":"<精确 endpoint>","arguments":{...}}`；`arguments` 直接使用对应 reference 的请求参数对象，不额外包裹 `body`、`params`、`data` 或第二层 `arguments`。
- **自动授权**：Authorization 由 WorkBuddy 自动注入。MCP 配置、文档和 `arguments` 均不得加入 `headers`、API Key、token、JWT、手机号或其他凭证。
- **禁止直连**：不得使用 curl、`urllib`、`requests`、`httpx` 或其他方式访问工具网关；MCP 或 `proxy_call` 缺失时停止，不得静默回退 HTTP。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理层状态；代理成功后读取 text/structured content。text 为 JSON 字符串时只解析一次，再检查下游 `errorCode`、`errcode`、`code`、`errmsg` 或 `msg`。
- **调用纪律**：同一任务中相同 `toolName + arguments` 不得重复调用。失败、空结果或结果不理想时不得自动换关键词、换商品、翻页、重试或改猜另一个 `toolName`；需要额外收费调用时先说明积分消耗并取得用户决定。
- **行为变化**：MCP 链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。需要追溯时在当前会话记录准确的 `toolName`、`arguments`、调用时间和返回的 `costToken`，不得声称已有本地缓存或结果文件。

## 使用示例

以下示例使用真实参数形状。结果中的 `costToken`、`costTime` 和历史覆盖范围以实际响应为准；串联多个示例意味着多次调用，应先让用户决定是否继续。

### 商品发现与列表快筛

**1. 关键词搜索并按畅销排序**

```json
{"toolName":"walmart/search","arguments":{"keyword":"wireless earbuds","sort":"best_seller","page":1}}
```

从 `products[]` 读取 `title`、`price`、`currency`、`rating`、`reviews`、`sellerName`、`usItemId`、`productPageUrl`、`outOfStock` 和 `sponsored`；同时展示 `total` 与 `costToken`。`best_seller` 是当前结果排序，不能当作历史销量证明。

**2. 价格带和分页筛选**

```json
{"toolName":"walmart/search","arguments":{"keyword":"laptop stand","minPrice":10,"maxPrice":50,"sort":"price_low","page":1}}
```

用 `wasPrice` 判断是否存在划线价，用 `shippingPrice`、`freeShipping` 和 `twoDayShipping` 补充到手条件；结果较多时依据 `total` 建议用户继续指定 `page`，页码范围为 1–100。

**3. 类目或门店场景**

```json
{"toolName":"walmart/search","arguments":{"categoryId":"976759_976787","page":2,"device":"desktop","nextDayEnabled":true}}
```

`keyword` 和 `categoryId` 至少一个必填；需要店铺限定时增加 `storeId`，需要特定展示端时使用 `desktop`、`tablet` 或 `mobile`。facet 使用 `key:value||key:value` 格式，具体字段不要凭空扩展。

### 单品深查与趋势

**4. 查询单个 Item ID 的详情和历史**

```json
{"toolName":"wallysmarter/productDetail","arguments":{"productId":5177343351,"includeStats":true}}
```

读取 `products[0]` 的 `title`、`price`、`wasPrice`、`brand`、`rating`、`reviews`、`salesEstimate`、`revenue`、`sellerName`、`fulfillmentType`、`listingScore`、`contentScore`、`outOfStock` 和 `stats`。`stats.price`/`stats.sales` 是 UTC 日期升序序列，应分别概括价格和销量变化，并注明是估算/历史数据；历史数据是否存在取决于跟踪覆盖。

**5. 只看当前属性**

```json
{"toolName":"wallysmarter/productDetail","arguments":{"productId":5169493923,"includeStats":false}}
```

此模式适合只核验当前商品属性、卖家、配送和 Listing 分。响应中的 `stats` 应按 `null` 或不可用字段展示，不要据此推断趋势；详情一次只能查一个数值 Item ID。

### 搜索到深查

**6. 对候选做定向复核**

先用列表请求筛出候选，再从结果的数值 `usItemId` 或 Walmart 商品 URL `/ip/<数字>` 取得详情请求的 `productId`：

```json
{"toolName":"walmart/search","arguments":{"keyword":"water bottle","minPrice":15,"maxPrice":40,"sort":"best_match","page":1}}
```

随后对用户选定的单个候选调用示例 4 或 5，并把列表当前字段与详情字段分列展示。不要把搜索结果中的字母数字 `productId` 误当成详情所需的数值 Item ID；每增加一个详情候选都可能增加调用和积分消耗。

## 展示规则

1. **先呈现数据，再做分析**：列表用表格展示标题、价格、评分/评价数、卖家和商品链接；详情按当前属性、配送/库存、Listing 分和历史统计分组。除非用户明确要求，不添加主观购买或开发结论。
2. **统一价格口径**：列表展示 `price` 和可用的 `wasPrice`，同时保留 `currency`；详情按美元展示当前价、划线价和最低价，并在字段为空时标为 N/A，不臆造折扣。
3. **给评分上下文**：始终把 `rating` 与 `reviews` 放在一起；评分高但评价数很少时客观标注样本量，不把评分当作销量或质量保证。
4. **明确库存和配送**：列表的 `outOfStock=true` 要醒目标注缺货，详情用 `outOfStock=1` 表示缺货；详情同时展示 `fulfillmentType` 的 `WFS` 或 `MARKETPLACE`。列表的免费配送、两日配送和运费按返回字段展示。
5. **标识广告和变体**：`sponsored=true` 或详情 `sponsored=1` 标注为赞助/广告商品；`multipleOptionsAvailable` 和 `variantSwatches` 存在时注明有变体，不把单个变体价格代表整个商品。
6. **解释排序和分页**：说明 `best_seller`、`best_match`、`price_low`、`price_high` 的当前排序语义；当 `total` 较大时告知总量和 `page` 范围，不自动翻页。
7. **解释趋势和分数**：只有 `includeStats=true` 且 `stats` 有数据时才总结价格/销量趋势；`listingScore` 和 `contentScore` 应说明为 Listing/内容质量分，通常分数越高表示质量越好，不视为平台排名或销售保证。
8. **区分估算与事实**：`salesEstimate`、`revenue` 和趋势序列标注为 WallySmarter 估算/历史数据；报告 `sourceTool`、`sourceType`、`updatedAt` 或查询时间，方便审计数据时点。
9. **处理不可用字段**：`null`、空字符串、`0`/`-1` 若按接口语义表示不可用，不展示为真实数值，统一写 N/A；同时指出哪些字段因 `includeStats=false` 或数据覆盖不足而不可用。
10. **错误处理可行动**：按响应的 `errorCode`/`errcode`/`code` 与 `errmsg`/`msg` 原样说明失败原因，并给出对应修正建议：缺少关键词/类目、页码越界、Item ID 非数值、不可访问的配置或参数不受支持时分别修正，不盲目重试。
11. **反馈处理**：若用户明确表扬、不满、指出结果与意图不符或发现功能问题，按对应 reference 中的 Feedback API 规则异步上报 `POSITIVE`/`NEUTRAL`/`NEGATIVE`；反馈不应中断当前数据展示，也不要把 API Key、手机号或支付信息写入反馈内容。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md` 并严格区分层级：

- MCP 或 `proxy_call` 缺失：停止业务调用，提供 MCP 配置并提示重启或重载客户端，不得 HTTP fallback。
- MCP 连接 401：按 WorkBuddy 自动授权链路异常处理，提示重新登录、重载连接或联系 WorkBuddy 管理员；不得要求用户手工填写 Authorization。
- 代理成功但下游 JSON 为 401：按自动授权或下游业务认证失败处理，不得把 Key、token、JWT、手机号或 `headers` 放入 `arguments`。
- 下游 JSON 为 402 或积分不足：引导用户访问 `https://agent.linkfox.com/`，不得自动选套餐、下单、支付、轮询或重试收费调用。
- 403 和其他错误：按业务 reference 原文处理，不得错误归类为 401/402。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
