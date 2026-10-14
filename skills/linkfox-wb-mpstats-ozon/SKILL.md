---
name: linkfox-wb-mpstats-ozon
display_name: LinkFox MPSTATS Ozon选品
display_name_en: LinkFox MPSTATS Ozon Product Intelligence
description: 面向 Ozon 俄罗斯站的商品发现、详情核验、趋势分析与品牌/类目/卖家选品洞察能力。
description_zh: 面向 Ozon 俄罗斯站的 MPSTATS 商品数据分析能力：按俄语关键词或 SKU 发现商品，查询单品详情与分日走势，并按品牌、类目路径或卖家 ID 筛选商品、比较销量价格库存评分和周转表现。当用户需要 Ozon 选品、竞品核验、爆款挖掘、店铺或品牌分析、类目机会扫描时触发；完整参数及 MCP 调用约定见 references/。
description_en: MPSTATS-powered Ozon Russia product intelligence for product discovery, SKU card verification, daily trend analysis, and brand-, category-, or seller-scoped selection research. Triggered for Ozon product sourcing, competitor checks, bestseller discovery, store or brand audits, and category opportunity scans. Full parameters and MCP call contracts are in references/.
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


# LinkFox MPSTATS Ozon选品（LinkFox MPSTATS Ozon Product Intelligence）

本能力用于把 Ozon 俄罗斯站的商品数据转化为可核验的选品与竞品研究结果：先按俄语关键词或 SKU 找到商品，再按 SKU、品牌、类目或卖家查看价格、销量、销售额、评分、库存、周转、排名和时间走势。它覆盖 6 个业务子能力，并通过 WorkBuddy 的 `LinkFox.proxy_call` 调用 6 个精确 endpoint toolName。子能力标识、参数和 toolName 在下方路由表及对应 reference 中逐项列出。

## 能力边界

### 能力范围

- **商品发现与身份解析**（`linkfox-mpstats-ozon-product-search`）：用俄语关键词或 Ozon SKU 列表检索商品，返回 `productId`、俄语标题、商品页、主图、品牌和卖家等身份字段，适合作为后续详情、趋势或维度分析的入口。
- **SKU 商品卡核验**（`linkfox-mpstats-ozon-product-detail`）：对已有 SKU 批量查询商品详情，单次最多 100 个，返回价格、折扣、Ozon Card 价、评分、评论数、库存、配送方案、统计期销量/销售额、上期对比、潜在销售额和缺货损失等字段；服务端逐 SKU 并发并对失败项自动重试一次，允许部分成功。
- **单 SKU 分日走势**（`linkfox-mpstats-ozon-product-trend`）：围绕一个 `productId` 查看指定日期窗口的每日价格、销量、库存、评分、评论数以及畅销/新品标记；`includeSearchStats` 可请求搜索可见性扩展，但以实际返回 schema 为准。
- **品牌维度商品洞察**（`linkfox-mpstats-ozon-brand-products`）：按 Ozon 前台展示的品牌名查询该品牌 SKU，支持数值筛选、排序、分页、货币换算和 FBO/FBS 口径切换，用于品牌商品结构、爆款和销售额占比观察。
- **类目维度商品洞察**（`linkfox-mpstats-ozon-category-products`）：按 Ozon 使用的俄语完整类目路径查询商品，支持销量、价格、评分、库存、周转、损失销售额等多条件筛选和类目内排名，用于类目爆款与细分机会扫描。
- **卖家维度商品洞察**（`linkfox-mpstats-ozon-seller-products`）：按数字型 `sellerId` 查询店铺 SKU，支持与品牌/类目维度相同的筛选、排序、分页、货币和 FBO/FBS 选项，用于店铺结构、卖家爆款和竞店对标。
- **统一研究链路**：发现结果中的 `productId`、`brand`、`brandId`、`sellerId` 和 `category` 可继续用于 SKU 详情、趋势或品牌/类目/卖家下钻；各查询结果中的 `costToken`、`costTime` 和日期字段用于审计调用成本与数据时点。

### 边界与限制

- **站点范围**：只覆盖 MPSTATS 的 Ozon 俄罗斯站数据，不覆盖 Wildberries 或其他俄罗斯/全球电商平台。
- **数据时点**：统计接口的 `endDate` 最晚为昨日（T-1），不能传今天或未来日期；缺省日期由接口按各 operation 的规则处理。
- **输入必须匹配维度**：搜索至少提供 `keyword` 或 `productIds`；详情必须提供 SKU 列表；趋势每次只能提供一个数字型 `productId`；品牌必须是精确的 Ozon 展示名；类目必须是俄语完整路径；卖家必须是数字字符串 `sellerId`。
- **搜索不是指标接口**：`productSearch` 是身份解析接口，固定返回约 10 个身份字段，不返回价格、销量、评分、库存、周转或排名；需要这些指标时必须转到详情或相应维度下钻。
- **容量限制**：商品详情单次最多 100 个 SKU；品牌、类目、卖家每页最多 100 行；商品搜索没有分页、排序和筛选参数，单次结果有上游约 36 条的硬上限；趋势单次只支持一个 SKU。
- **口径限制**：品牌/类目/卖家结果的 `revenueSharePercent` 是当前查询维度结果集内占比，不是全站占比；`position` 也对应当前查询维度。`includeFbs` 是整批或整次查询共享的口径开关，不能按单个 SKU 设置。
- **语言与名称**：关键词、类目路径和品牌名应优先使用 Ozon 实际使用的俄语或拉丁形式。英文/中文关键词应先转成俄语并标明转换；品牌不支持模糊匹配，拼写错误可能返回空结果。
- **时间序列缺口**：趋势点的 `hasData=false` 表示没有观测，不等于零销量；同样不要把缺失字段当成零。趋势接口当前 schema 不保证额外的独立搜索位次字段。
- **数据用途**：结果是市场数据与查询结果，不是采购承诺、销量保证或财务/经营结论；不包含评论文本、Listing 文案优化、广告投放、订单、物流、供应链和利润核算建议。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “在 Ozon 搜索某个商品/关键词”“我有一批 Ozon SKU，先告诉我商品名” | `linkfox-mpstats-ozon-product-search`；俄语关键词或 `productIds` 至少传一个 | 已经有 SKU 且要价格、销量、库存、评分时换 `linkfox-mpstats-ozon-product-detail`；已有品牌、类目或卖家维度时直接用对应下钻 |
| “查这些 SKU 的价格、销量、评分、库存”“批量看竞品商品卡” | `linkfox-mpstats-ozon-product-detail`；适合 1–100 个 SKU 的统计期汇总 | 只看一个 SKU 每日变化换 `linkfox-mpstats-ozon-product-trend`；要某品牌/类目/店铺下的商品集合换相应 `*-products` |
| “这个 Ozon SKU 最近销量/价格怎么变化”“看是否季节性或缺货” | `linkfox-mpstats-ozon-product-trend`；一个 SKU 一个日期窗口 | 只要一张当前统计期商品卡换 `product-detail`；多 SKU 或维度筛选不要循环替代为趋势接口 |
| “看 adidas/Xiaomi 在 Ozon 卖什么”“品牌爆款/品牌销售额结构” | `linkfox-mpstats-ozon-brand-products`；`brandName` 必须是展示名 | 不知道精确品牌拼写先用 `product-search`；要跨品牌类目比较换 `category-products`；要店铺商品换 `seller-products` |
| “找某个 Ozon 类目的爆款/蓝海 SKU”“筛销量、价格、周转” | `linkfox-mpstats-ozon-category-products`；需要俄语完整 `categoryPath` 和可选 `filters` | 不知道完整路径先从详情结果的 `category` 或搜索结果定位；只看一个品牌/店铺时换 `brand-products`/`seller-products` |
| “拆解某个 Ozon 卖家店铺”“看竞店 SKU、销售额和缺货损失” | `linkfox-mpstats-ozon-seller-products`；需要数字型 `sellerId` | 只有卖家名称先用 `product-search` 解析 `sellerId`；要类目或品牌集合换对应下钻 |

选择时先判断用户的主维度：没有 ID 就做发现，已有 SKU 且问汇总指标就做详情，问“随时间如何变化”才做趋势；已有品牌名、完整类目路径或卖家 ID 时直接使用对应下钻。多个候选都能满足时，优先选择能直接回答问题且请求条数最少的 operation，并把 FBO/FBS、日期窗口、分页和货币作为统一参数确认。每次真实请求都可能消耗积分，扩大 SKU、分页或改参数前应先告知用户。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | `toolName` | 本地 helper |
|---|---|---|---|---|
| `linkfox-mpstats-ozon-product-search` | 俄语关键词 / SKU 商品搜索与身份解析 | `references/linkfox-mpstats-ozon-product-search.md` | `mpstats/ozon/productSearch` | 无 |
| `linkfox-mpstats-ozon-product-detail` | 1–100 个 SKU 商品卡与统计期汇总 | `references/linkfox-mpstats-ozon-product-detail.md` | `mpstats/ozon/productDetail` | 无 |
| `linkfox-mpstats-ozon-product-trend` | 单 SKU 分日价格、销量、库存与表现走势 | `references/linkfox-mpstats-ozon-product-trend.md` | `mpstats/ozon/productTrend` | 无 |
| `linkfox-mpstats-ozon-brand-products` | 品牌下 SKU 筛选、排序、分页与指标分析 | `references/linkfox-mpstats-ozon-brand-products.md` | `mpstats/ozon/brandProducts` | 无 |
| `linkfox-mpstats-ozon-category-products` | 俄语类目路径下 SKU 筛选与排名分析 | `references/linkfox-mpstats-ozon-category-products.md` | `mpstats/ozon/categoryProducts` | 无 |
| `linkfox-mpstats-ozon-seller-products` | 卖家店铺 SKU 筛选、排序与结构分析 | `references/linkfox-mpstats-ozon-seller-products.md` | `mpstats/ozon/sellerProducts` | 无 |

## MCP 调用方式

- **MCP Server**：`LinkFox`；统一工具为 `proxy_call`。
- **参数结构**：`proxy_call` 的 `toolName` 必须使用路由表中的精确值，大小写敏感且不带前导 `/`；业务参数直接放在 `arguments`，不要再包一层 `body`、`params` 或 `data`。
- **授权**：WorkBuddy 自动注入授权上下文。禁止在 `arguments` 中传 `headers`、`Authorization`、API Key、token、JWT 或手机号，也不读取本地环境变量补充认证。
- **响应处理**：`proxy_call` 的结果若是 JSON 字符串，只解析一次；解析后按 reference 的响应字段表处理。先区分 MCP 传输/配置错误，再处理下游业务 `code`/`errcode` 与 `msg`/`errmsg`。
- **失败纪律**：禁止回退旧 HTTP 网关、旧 Python 脚本或其他未声明工具。失败、空结果或部分成功不得自动换关键词、翻页、换品牌拼写或连续改日期探测，也不得为“确认结果”重复发起计费调用。确需重试、扩大 page/列表或切换 `includeFbs` 时，先向用户说明可能产生的额外积分消耗并取得同意。
- **完整参数位置**：每个 operation 的必填条件、所有可选参数、完整响应字段、错误码和 Feedback API 见 `references/<子能力标识>.md`；认证或计费异常的统一引导见 `references/onboarding.md`。
- **迁移后的本地能力**：本 skill 不保留本地 helper。旧脚本提供的 24 小时参数缓存、自动 JSON 落盘、会话索引和 stdout 摘要不属于 MCP 返回能力；需要留存或摘要时，应由当前 WorkBuddy 会话显式处理，不能宣称 MCP 已自动完成。

## 使用示例

以下参数均来自对应 operation。示例中的日期不能晚于昨日；俄语标题和品牌默认保留原文，展示时可按用户需要翻译。

### 1. 关键词发现与 SKU 反查

```json
{"keyword":"кроссовки","startDate":"2025-03-01","endDate":"2025-03-31"}
```

以 `toolName="mpstats/ozon/productSearch"` 调用 `proxy_call`。出参重点看 `products[].productId/title/brand/sellerId/sellerName/productPageUrl/imageUrl`、`total` 和 `costToken`。`keyword` 和 `productIds` 至少有一个；搜索无分页且单次约 36 条上限，不要把它当销量接口。

```json
{"productIds":[1786874757,151623766,142257239]}
```

这是同一 operation 的批量 SKU 身份解析。若下一步需要业务指标，把返回的 `productId` 传给商品详情，而不是从搜索结果推断价格或销量。

### 2. SKU 商品卡与周期对比

```json
{
  "productIds":[1786874757,151623766,142257239],
  "startDate":"2025-03-01",
  "endDate":"2025-03-31",
  "includeFbs":true
}
```

以 `toolName="mpstats/ozon/productDetail"` 调用 `proxy_call`。出参看 `products[]` 的 `price/monthlySalesUnits/monthlySalesRevenue/rating/reviewCount/balance/deliveryScheme`，需要缺货影响时再看 `revenuePotential/lostProfit/lostProfitPercent`，并将 `previousSalesUnits/previousRevenue` 与当期并列。批量超过 100 必须分批，`failedCount > 0` 时列出 `failures` 中的 SKU，不能静默丢弃。

### 3. 单 SKU 分日趋势

```json
{
  "productId":1786874757,
  "startDate":"2025-03-01",
  "endDate":"2025-03-31",
  "includeFbs":true,
  "includeSearchStats":true
}
```

以 `toolName="mpstats/ozon/productTrend"` 调用 `proxy_call`。出参是顶层 `data[]`，逐日读取 `date/hasData/price/sales/balance/rating/comments/isBestseller/isNew`；`hasData=false` 是缺失观测，不应改写为零销量。当前 schema 未声明额外搜索字段时，应明确说明搜索位次不可用。每日销售额不在出参中，若用户要求只能用 `sales * price` 作估算并标注估算。

### 4. 品牌商品筛选

```json
{
  "brandName":"adidas",
  "filters":[
    {"field":"rating","op":"GTE","value":4.5},
    {"field":"final_price","op":"BETWEEN","value":1000,"value2":5000}
  ],
  "sortField":"revenue",
  "sortDirection":"desc",
  "pageSize":50,
  "currency":"USD",
  "includeFbs":true
}
```

以 `toolName="mpstats/ozon/brandProducts"` 调用 `proxy_call`。过滤条件按 AND 处理，`BETWEEN` 必须提供 `value2`；出参看 `products[]` 的 39 字段商品卡以及品牌维度 `position/revenueSharePercent`。换算后要在表头标出 USD，精确品牌名不支持模糊匹配。

### 5. 类目机会扫描

```json
{
  "categoryPath":"Одежда/Женская одежда/Футболки и топы женские",
  "filters":[
    {"field":"sales","op":"GTE","value":50},
    {"field":"turnover_days","op":"LTE","value":30}
  ],
  "sortField":"revenue",
  "sortDirection":"desc",
  "page":1,
  "pageSize":100
}
```

以 `toolName="mpstats/ozon/categoryProducts"` 调用 `proxy_call`。`categoryPath` 必须是 Ozon 俄语完整路径；结果中的 `total` 用于判断是否还有下一页，类目维度的 `position`/`revenueSharePercent` 不应解释为全站排名/占比。未知路径先从商品详情或搜索结果中的 `category` 获取。

### 6. 卖家店铺拆解

```json
{
  "sellerId":"3628678",
  "sortField":"lost_profit",
  "sortDirection":"desc",
  "filters":[{"field":"sales","op":"GTE","value":30}],
  "pageSize":100,
  "currency":"RUB"
}
```

以 `toolName="mpstats/ozon/sellerProducts"` 调用 `proxy_call`。`sellerId` 必须是数字字符串；出参重点看 `productId/title/brand/monthlySalesUnits/monthlySalesRevenue/balance/turnoverDays/lostProfit/position`。只有卖家名称时先解析数字 `sellerId`，不要把名称直接传给卖家端点。

## 展示规则

1. **按查询目的呈现列**：搜索结果先展示 `productId`、俄语 `title`、`brand`、`sellerName`、`sellerId`，并把商品页和主图作为辅助列；不得为搜索结果补写价格、销量、评分或库存。
2. **商品卡使用紧凑表格**：详情优先展示 `productId`、`title`、`price`、`monthlySalesUnits`、`monthlySalesRevenue`、`rating`、`reviewCount`、`balance`、`deliveryScheme`、`firstDate`；用户问缺货影响时才展开潜在销售额和损失销售额。
3. **保留时间口径**：详情中的 `previous*` 是等长上一周期，只有同时给出当前值和上期值时才称为环比/周期变化；趋势按日期逐行或 sparkline 友好格式展示，不能用汇总数字代替每日形状。
4. **正确解释缺失与异常**：趋势 `hasData=false` 与 `sales=0, hasData=true` 分开标记；搜索统计没有实际字段时说明不可用；响应中的 `failures`、空列表和缺失字段要如实展示，不得静默丢弃或用估算值冒充原始值。
5. **标明币种与维度**：Ozon 默认金额口径为 RUB，展示价格/销售额时注明 `currency`；品牌、类目、卖家结果的 `revenueSharePercent` 标注“当前查询维度结果集内占比”，`position` 标注具体维度。使用 USD/EUR/CNY 时说明已按请求货币换算及是否传入自定义 `currencyRate`。
6. **标明配送与库存口径**：展示 `deliveryScheme` 或 `isFbs`；混合 FBO/FBS 结果要提醒口径，`includeFbs` 适用于整次请求。`salesPerDayWithStock`/`dailySalesRevenueWithStock` 只代表有货日，不要和全窗口的日均值混用。
7. **分页与上限透明**：品牌、类目、卖家结果报告 `total`、当前页和 `pageSize`；搜索达到上游上限时建议收窄关键词、SKU 或日期，而不是虚构下一页；详情失败项列出 SKU 与错误信息。
8. **保留原文并可应请求翻译**：默认保留俄语商品标题、品牌、类目路径和卖家名；向中文/英文用户提供翻译时同时保留原文，避免改变用于再次查询的值。
9. **来源、时间和成本可审计**：展示或导出时保留 `sourceType/sourceTool`（若响应提供）、查询日期窗口、`costTime` 和 `costToken`；以本次 MCP 实际响应为准，不声称已由脚本自动落盘或缓存。
10. **客观呈现**：只描述 MPSTATS 返回的市场数据、筛选条件和可观察现象，不把排名、销量或损失销售额直接升级为“必然爆款”“一定值得采购”等经营结论。
11. **错误给出修正建议**：按 `code/errcode` 与 `msg/errmsg` 原样解释；针对缺少必填参数、俄语关键词、完整类目路径、精确品牌名、数字卖家 ID、日期越过昨日、页大小/详情批量超限，给出对应的输入修正方向。

## 解决认证和积分问题

发生以下异常时读取 `references/onboarding.md`。WorkBuddy 自动处理调用授权；不要索取、展示或猜测 API Key、token、JWT、手机号或支付状态。

### 异常情况

- **MCP 工具不存在或不可用**：这是 WorkBuddy/MCP 配置或加载问题，提示检查 `LinkFox` 是否已配置并刷新会话，不要改走旧 HTTP 网关。
- **401 / authorized error**：这是 WorkBuddy 自动授权上下文异常；提示刷新会话或检查连接，不要在参数中补传任何凭证。
- **402 / 积分或余额不足**：响应为 HTTP 402、`errcode=402`，或消息包含“积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值”等含义时，读取套餐并由用户决定是否购买，不要自动下单。
- **其他业务错误**：403 是无权限，不归入 auth/billing；输入错误、空结果和日期/批量限制按各 reference 的错误码修正，不要用 onboarding 代替业务排错。

积分不足时引导用户访问 `https://agent.linkfox.com/` 自助处理；不自动读取套餐、下单、支付或轮询订单。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
