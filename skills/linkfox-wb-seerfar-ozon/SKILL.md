---
name: linkfox-wb-seerfar-ozon
display_name: LinkFox Ozon选品
display_name_en: LinkFox Ozon Product Research
description: Ozon 市场、关键词、商品、店铺和类目数据选品分析能力，支持发现机会、筛选商品、反查流量词与深度评估。
description_zh: 面向 Ozon 选品与竞品研究的统一数据分析能力：可浏览市场热词、围绕种子词挖掘长尾词、按 SKU 反查自然词与广告词、分析店铺和类目、筛选商品报表并查看单品销量趋势、库存和排名。用户需要 Ozon 市场机会发现、关键词研究、商品筛选、店铺拆解、类目分析或单品评估时触发。结果来自 Seerfar 数据接口，完整参数、响应字段和错误码见 references/。
description_en: Unified Ozon product-research and competitive-analysis capability for discovering market opportunities, mining and reverse-looking-up keywords, screening products, analyzing shops and categories, and deep-diving into one SKU's sales trend, stock, ranking, brand, and seller data. Use when the user needs Ozon market, keyword, product, shop, category, or listing research. Results come from Seerfar data endpoints; full parameters, response fields, and error codes are documented in references/.
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


# LinkFox Ozon选品（LinkFox Ozon Product Research）

面向 Ozon 选品、关键词研究和竞品拆解，输出可核验的市场指标、商品列表、店铺/类目汇总以及单品趋势数据。能力覆盖 7 个子能力、7 个 API/operation，关联 `tool_key=seerfar_ozon`：`linkfox-seerfar-ozon-market-keyword-search`、`linkfox-seerfar-ozon-keyword-mining`、`linkfox-seerfar-ozon-keyword-back-search`、`linkfox-seerfar-ozon-shop-search`、`linkfox-seerfar-ozon-category-search`、`linkfox-seerfar-ozon-product-detail-search`、`linkfox-seerfar-ozon-product-report-search`。

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` allowlist | `seerfar/ozon/marketKeywordSearch`、`seerfar/ozon/keywordMining`、`seerfar/ozon/keywordBackSearch`、`seerfar/ozon/shopSearch`、`seerfar/ozon/categorySearch`、`seerfar/ozon/productDetailSearch`、`seerfar/ozon/productReportSearch` |
| 调用结构 | `{"toolName":"<精确 endpoint>","arguments":{...}}`；原请求体直接作为 `arguments` |

- `toolName` 必须从 allowlist 选择，精确匹配且区分大小写。
- WorkBuddy 自动注入 MCP Authorization；MCP 配置、文档和 `arguments` 中不得增加 `headers`、API Key、token、JWT、手机号或其他凭证。
- 禁止 curl、`urllib`、`requests`、`httpx` 或其他 HTTP 方式直连工具网关；MCP 或 `proxy_call` 缺失时停止，不得静默 fallback。
- 同一任务内相同 `toolName + arguments` 不得重复调用；收费调用失败、空结果或结果不理想时不得自动重试或改条件探测。
- 先检查 MCP 连接、schema 和 `isError`，再读取 text/structured content；text 为 JSON 字符串时只解析一次。随后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`，最后读取业务字段。
- 新 MCP 链路不提供旧脚本的 24 小时缓存、JSON 落盘或 stdout 摘要；仅保留非敏感调用摘要和状态用于结果追溯。

## 能力边界

### 能力范围

- **市场热词与市场画像**：按搜索热度、30 天增长、商品/竞品/卖家数、价格、销量、市场空间和转化集中度筛选市场关键词；使用 `linkfox-seerfar-ozon-market-keyword-search` 和 `seerfar/ozon/marketKeywordSearch`。
- **种子词拓展与长尾挖掘**：围绕一个俄语或其他用户提供的种子词发现相关词，并按相关度、标题密度、搜索量、竞争和加购转化筛选；使用 `linkfox-seerfar-ozon-keyword-mining` 和 `seerfar/ozon/keywordMining`。
- **SKU 关键词反查**：从最多 20 个商品 SKU 反查自然搜索词、广告搜索词及每个词的自然排名、广告排名、曝光和转化；使用 `linkfox-seerfar-ozon-keyword-back-search` 和 `seerfar/ozon/keywordBackSearch`。
- **店铺商品与卖家结构**：按卖家/店铺 ID 分页查看商品销量、价格、评分、配送方式、卖家类型及店铺汇总；使用 `linkfox-seerfar-ozon-shop-search` 和 `seerfar/ozon/shopSearch`。
- **类目容量与商品排行**：按类目 ID 获取类目总销量、总销售额、均价、评分、季节性和商品列表，可按历史月份及配送方式查看；使用 `linkfox-seerfar-ozon-category-search` 和 `seerfar/ozon/categorySearch`。
- **单品深度评估**：按单个 SKU 查看价格、评分、销量、销售额、库存、类目排名、每日销量趋势、品牌、卖家、配送方式和上架时长；使用 `linkfox-seerfar-ozon-product-detail-search` 和 `seerfar/ozon/productDetailSearch`。
- **商品报表筛选**：按销量、销售额及增长、转化、价格、评分、评论、毛利率、退货取消率、品牌、卖家、配送方式、上架时间和标签筛选商品；使用 `linkfox-seerfar-ozon-product-report-search` 和 `seerfar/ozon/productReportSearch`。
- **结果追溯**：新 MCP 链路不承诺旧脚本的摘要、缓存或落盘；按需展示必要字段，并记录非敏感调用摘要和状态。

### 边界与限制

- 所有查询由 WorkBuddy 自动授权，并按接口消耗积分；同一任务内相同 `toolName + arguments` 只调用一次。失败或空结果不得自动换词、改筛选条件、翻页或重试探测，继续调用前先提醒用户并由用户决定。
- 数据以 Ozon 为主；关键词类结果可能带 `platform=1` 的 Wildberries 行，接口没有平台入参选择器，需按返回的 `platform` 客户端区分。商品、店铺和类目查询不应据此推断为其他平台数据。
- `page` 是列表查询必需对象；店铺和类目 `pageSize` 最大为 20；市场关键词、关键词挖掘和反查的列表也应使用分页与排序。类目 ID、店铺 ID、SKU 必须使用 Seerfar 可识别的标识，不能用人类可读名称替代。
- 关键词市场搜索必须传 `page`；关键词挖掘必须传 `keyword` 与 `page`；关键词反查必须传 `skuIds`、`hasVariant` 与 `page`；店铺必须传 `id` 与 `page`；类目必须传 `categoryId` 与 `page`；单品详情必须传 `sku`；商品报表必须传 `page`。
- 关键词市场搜索用于全市场关键词浏览，可选 `searchDate` 和 `categories`；关键词挖掘用于围绕种子词拓展，不支持 `searchDate`、`categories`；关键词反查用于 SKU→关键词，不接受种子 `keyword`，历史时间使用 `historyDate`。
- 店铺/类目列表是分页视图，`total` 不等于完整店铺/类目规模时以 `hasNextPage` 继续判断；商品详情是单 SKU 查询，不能批量；商品报表的 `skus` 最多 10 个。
- 销量、销售额、库存、转化、毛利率、排名和趋势属于 Seerfar 数据或模型估计，不等同于 Ozon 官方后台数据；部分字段会因商品类型、平台卖家或上游数据缺失而不返回。
- 不提供 Ozon 账号操作、上架、订单、库存写入、广告投放、物流履约、供应链执行或其他平台运营动作；不保证选品成功，也不替用户做未经数据支持的收益或竞争结论。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “Ozon 热词有哪些”“按搜索量/卖家数找蓝海词” | `linkfox-seerfar-ozon-market-keyword-search` | 已有种子词并要相关词改用关键词挖掘；已有 SKU 并要流量词改用关键词反查 |
| “围绕这个俄语词找长尾词/相关词” | `linkfox-seerfar-ozon-keyword-mining` | 不提供种子、要看全市场词改用市场热词；要反查某商品排名词改用关键词反查 |
| “这个 SKU 排在哪些自然词/广告词下” | `linkfox-seerfar-ozon-keyword-back-search` | 要商品销量/库存/趋势改用单品详情；要按多个指标筛商品改用商品报表 |
| “这个店铺卖什么、爆品是什么、店铺总销量多少” | `linkfox-seerfar-ozon-shop-search` | 只有店铺名或商品名时先通过商品/列表结果取得 `sellerId`；要类目规模改用类目查询 |
| “这个 Ozon 类目有多大、类目热销商品/价格带是什么” | `linkfox-seerfar-ozon-category-search` | 只有类目名称时先解析 `categoryId`；要店铺维度改用店铺查询 |
| “查看一个 SKU 的详情、库存、排名或销量趋势” | `linkfox-seerfar-ozon-product-detail-search` | 要一次筛选多个商品或按指标排名改用商品报表；要该商品的关键词改用关键词反查 |
| “按销量、价格、评分、毛利率筛 Ozon 商品/找爆款” | `linkfox-seerfar-ozon-product-report-search` | 要单 SKU 的日趋势改用单品详情；要类目级汇总改用类目查询；要店铺全目录改用店铺查询 |

选择时先判断用户要查的实体是**关键词、SKU、店铺还是类目**，再判断是发现/筛选、反查还是深度详情；同时检查必填 ID、时间窗口、排序字段和列表上限。多个选择都能满足时，说明各自的出入参、数据粒度与额外调用成本，让用户决定是否继续。

## 业务需求路由速查

| 子能力 | 业务能力 | reference / API reference | `toolName` | 本地辅助 |
|---|---|---|---|---|
| `linkfox-seerfar-ozon-market-keyword-search` | 全市场热词筛选与关键词市场画像 | `references/linkfox-seerfar-ozon-market-keyword-search.md` / `references/linkfox-seerfar-ozon-market-keyword-search-api.md` | `seerfar/ozon/marketKeywordSearch` | 无 |
| `linkfox-seerfar-ozon-keyword-mining` | 围绕种子词挖掘相关词与长尾词 | `references/linkfox-seerfar-ozon-keyword-mining.md` / `references/linkfox-seerfar-ozon-keyword-mining-api.md` | `seerfar/ozon/keywordMining` | 无 |
| `linkfox-seerfar-ozon-keyword-back-search` | 按 SKU 反查自然词、广告词和排名指标 | `references/linkfox-seerfar-ozon-keyword-back-search.md` / `references/linkfox-seerfar-ozon-keyword-back-search-api.md` | `seerfar/ozon/keywordBackSearch` | 无 |
| `linkfox-seerfar-ozon-shop-search` | 店铺商品目录、卖家类型与店铺汇总 | `references/linkfox-seerfar-ozon-shop-search.md` / `references/linkfox-seerfar-ozon-shop-search-api.md` | `seerfar/ozon/shopSearch` | 无 |
| `linkfox-seerfar-ozon-category-search` | 类目容量、季节性与类目商品排行 | `references/linkfox-seerfar-ozon-category-search.md` / `references/linkfox-seerfar-ozon-category-search-api.md` | `seerfar/ozon/categorySearch` | 无 |
| `linkfox-seerfar-ozon-product-detail-search` | 单 SKU 详情、销量趋势、库存与排名 | `references/linkfox-seerfar-ozon-product-detail-search.md` / `references/linkfox-seerfar-ozon-product-detail-search-api.md` | `seerfar/ozon/productDetailSearch` | 无 |
| `linkfox-seerfar-ozon-product-report-search` | 多指标商品报表筛选与商品级排名 | `references/linkfox-seerfar-ozon-product-report-search.md` / `references/linkfox-seerfar-ozon-product-report-search-api.md` | `seerfar/ozon/productReportSearch` | 无 |

每个 reference 文件都包含对应能力说明、边界、参数和使用规则；同名 `-api.md` 文件保留完整请求参数、响应字段、错误码、MCP 与响应示例。

## 调用方式

1. 按【业务需求路由速查】选择一个 reference 和对应的精确 `toolName`。
2. 从 reference 请求参数表构造 `arguments`，原请求对象直接传入，不增加传输层字段。
3. 使用 `proxy_call` 调用一次；相同参数不重复收费调用，失败后不猜测其他 `toolName`。
4. 按 MCP 外层、代理内容、下游业务错误、业务字段的顺序解析。完整 schema、错误码、响应示例及独立 Feedback API 见同名 `-api.md`。

## 使用示例

以下示例均为真实 `arguments` 形状。执行前确认必要 ID 和积分预算；每个响应都可能包含 `costToken`。

### 1. 全市场热词与蓝海筛选

```json
{
  "page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]},
  "searchVolume": {"min": 10000},
  "sellers": {"max": 50}
}
```

使用 `toolName=seerfar/ozon/marketKeywordSearch` 调用 `proxy_call`。重点读取 `data[].query/queryCn`、`searchVolume`、`count30GrowthRate`、`productCount`、`sellers`、`avgPrice`、`marketSpace` 和 `products[]`；`platform=0/1` 分别标注 Ozon/Wildberries。该接口必须有 `page`，不能用人类可读类目名代替 `categories`。

### 2. 围绕种子词挖掘长尾词

```json
{
  "keyword": "телефон",
  "page": {"page": 1, "pageSize": 20, "orders": [{"field": "relevancy", "direction": "DESC"}]},
  "matchType": 1,
  "includeKeywords": ["женские"],
  "excludeKeywords": ["ремень"],
  "searchVolume": {"min": 1000},
  "sellers": {"max": 50}
}
```

使用 `toolName=seerfar/ozon/keywordMining` 调用 `proxy_call`。读取 `query/queryCn`、`relevancy`、`titleDensity`、`wordCount` 和市场指标；该接口必须有 `keyword` 与 `page`，不支持 `searchDate`、`categories`，不能当作全市场热词浏览接口。

### 3. 反查 SKU 的自然词或广告词

```json
{
  "skuIds": [4380710124],
  "hasVariant": 1,
  "type": ["0"],
  "naturalRank": {"max": 10},
  "page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
}
```

使用 `toolName=seerfar/ozon/keywordBackSearch` 调用 `proxy_call`。读取 `query/queryCn`、搜索市场指标以及 `dimension.type`、`dimension.naturalRank`、`dimension.exposure`、`dimension.conversion`；`type:["0"]` 为自然词，`type:["1"]` 为广告词。`skuIds` 最多 20 个，`skuIds`、`hasVariant`、`page` 均必填。

### 4. 店铺商品结构与爆品

```json
{
  "id": 1362816,
  "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}
}
```

使用 `toolName=seerfar/ozon/shopSearch` 调用 `proxy_call`。先展示店铺级 `totalSales`、`totalRevenue`、`productCount`、`dailySales`、`rating` 与配送分布，再展示商品的 `sku`、`price`、`sales`、`reviewRating`、`sellerType`、`fulfillment`。`pageSize` 最大为 20；负店铺 ID 可能代表 Ozon 自营，`returnCancellationRate` 缺失时显示 `-`。

### 5. 类目容量与历史月份

```json
{
  "categoryId": "15621032_15621049_115951147",
  "date": "2026-02",
  "fulfillment": "FBO",
  "page": {"page": 1, "pageSize": 20, "orders": [{"field": "revenue", "direction": "DESC"}]}
}
```

使用 `toolName=seerfar/ozon/categorySearch` 调用 `proxy_call`。先读取 `categoryInfo`、`totalSales`、`totalRevenue`、`avgPrice`、`rating`、`seasonalityAmplitude`、`seasonalityCoef` 与日期范围，再列商品字段；`fulfillment` 必须是单个字符串，不是数组，`categoryId` 必须是 Seerfar 层级 ID。

### 6. 单 SKU 详情与销量趋势

```json
{
  "sku": "175924376",
  "dateRange": "past_90_days"
}
```

使用 `toolName=seerfar/ozon/productDetailSearch` 调用 `proxy_call`。读取 `title`、`sku`、`price`、`reviewRating`、`totalSales`、`dailySales`、`totalRevenue`、`stock`、`categoryRanks`、`salesTrendVOList`、`sellerName`、`brandName` 和 `fulfillment`；趋势按峰值、方向和窗口概括，完整日序列按当前 MCP 响应读取。该接口每次只查一个 SKU，销量/销售额是所选窗口的模型估计。

### 7. 多指标商品报表筛选

```json
{
  "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]},
  "monthlySales": {"min": 5000},
  "price": {"max": 500},
  "convToCartPdp": {"min": 1},
  "returnCancellationRate": {"max": 10},
  "fulfillment": ["FBO"]
}
```

使用 `toolName=seerfar/ozon/productReportSearch` 调用 `proxy_call`。读取 `sku/title/price/sales/revenue/reviewRating/reviewCount/brandName/sellerName/fulfillment` 及增长、转化、毛利和退货指标；`data` 与 `products` 是同一组商品，别把别名字段重复计数。`skus` 若使用，单次最多 10 个。

## 展示规则

1. **客观呈现**：用表格或分区清楚展示原始指标、查询条件、时间窗口、`total`、`costToken` 和接口状态；不要把数据直接包装成保证收益或确定性选品结论。
2. **标注粒度与来源**：明确当前结果是关键词、商品、店铺或类目粒度，并标注对应端点/Seerfar 数据来源；连续查询时逐项标明来源与时间窗口。
3. **保留俄语与平台信息**：关键词优先展示 `query` 原文并在有值时附 `queryCn`；关键词结果同时展示 `platform`（0=Ozon，1=Wildberries）。反查同时展示 `dimension.type`（0=自然，1=广告）及排名/曝光/转化。
4. **货币和单位**：`price`、`revenue`、`totalRevenue` 等按接口标注俄罗斯卢布 `₽`；销量为件，评分按 0–5，比例/增长率带 `%` 或明确 0–1 比例，重量为 g、体积为 L。
5. **避免别名重复**：商品报表中 `productId=sku`、`monthlySalesUnits=sales`、`monthlySalesRevenue=revenue`、`rating=reviewRating`、`brand=brandName`、`productPageUrl=productUrl`；类目/店铺也优先选一套原始字段展示。
6. **汇总与分页**：店铺/类目先展示全局汇总，再展示当前页商品；`hasNextPage=true` 时提示可通过 `page.page` 继续，且 `pageSize` 不超过 20。大结果只展示必要行和计数，不要把完整数组直接塞入上下文。
7. **时间和趋势**：市场关键词 `searchDate`、反查 `historyDate`、类目 `date`、详情 `dateRange` 的语义不同，展示时写明真实数据窗口；单品 `salesTrendVOList` 概括峰值和方向，`sales:0` 表示无销量而非缺失。
8. **缺失值与空结果**：schema 定义但响应缺失的字段显示 `-` 或 `N/A`；店铺/类目/详情的 `total=0` 空结果应提示 ID 可能错误，不要误报系统故障。店铺 `sellerType` 是本土/跨境标识，而类目顶层 `sellerType` 是配送方式计数映射，不能混淆。
9. **接口错误**：当 `code` 不是 `"200"` 或 `errcode` 不是 `200` 时，透传 `msg/errmsg` 的原因并给出针对性修正；参数错误检查必填字段、ID、日期格式和枚举值，`1002` 检查页大小，`1003` 等限流错误等待后再由用户决定是否重试。
10. **认证、费用和免责声明**：401/402 或余额相关提示按下节处理；展示 `costToken`，在用户频繁翻页或多 SKU/多条件查询前提醒费用；Seerfar 指标是数据分析参考，不等于 Ozon 官方后台或商业保证。

## 解决认证和积分问题

- MCP 或 `proxy_call` 缺失：停止业务调用，按 `references/onboarding.md` 配置并重载客户端，不使用 HTTP fallback。
- MCP 连接 401：提示重新登录 WorkBuddy、重载连接或联系管理员；不得要求用户填写 Authorization。
- 代理成功后的下游 401：按 WorkBuddy 自动授权或下游业务认证失败处理，不在 `arguments` 中传凭证。
- 下游 402 或积分不足：引导用户访问 <https://agent.linkfox.com/>；不自动选套餐、下单、支付或轮询。
- `403` 和其他错误按对应 API reference 处理，不归错类。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
