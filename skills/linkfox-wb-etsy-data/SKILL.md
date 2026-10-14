---
name: linkfox-wb-etsy-data
display_name: LinkFox Etsy选品
display_name_en: LinkFox Etsy Product Research
description: 面向 Etsy 选品研究的商品、店铺、类目与 Listing 详情数据查询能力。
description_zh: 面向 Etsy 选品与竞品研究，按类目、关键词、价格、销量、收藏、评论、标签、店铺表现或 Listing 直链查询公开数据，输出可筛选的商品/店铺列表、类目 ID 或单品详情；当用户需要 Etsy 找品、筛品、找类目、筛店铺、拆解 Listing 时触发。仅提供当前公开或已同步数据，不负责店铺运营、订单或个体评论全文分析。完整参数见 references/。
description_en: Etsy product-research data lookup for category IDs, multi-filter product and shop discovery, and one-listing public detail extraction. Use when users need Etsy product sourcing, listing screening, category lookup, shop discovery, or competitor listing audits. Returns current public or synchronized data through structured JSON; it does not manage seller operations, orders, or individual review text. See references/ for complete parameters.
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


# LinkFox Etsy选品（LinkFox Etsy Product Research）

面向 Etsy 选品、竞品研究和市场筛查，按用户给出的类目关键词、商品筛选条件、店铺筛选条件或 Listing 直链，返回可继续分析的类目 ID、商品列表、店铺列表或单 Listing 公开详情。该能力覆盖 4 个子能力和 4 个 Etsy 数据查询 API operation；每个子能力的完整参数、响应字段和特殊规则见 `references/`。

## 能力边界

### ✅ 能力范围

- **Etsy 类目 ID 检索**：在已同步的 Etsy 类目库中按类目名称、`id` 或 `parentIds` 子串匹配，返回类目层级、名称、父类目和可用于筛选的 `id`；使用 `toolName=ehunt/etsy/etsyCategorySearch`。
- **Etsy 商品筛选与找品**：按关键词或商品 URL、价格、销量、收藏、评论、上架时间、发货国家、商品类型、Pick/Bestsell/Raving、状态和类目等条件筛选商品，并按上游排序字段分页返回；使用 `toolName=ehunt/etsy/productQuery`。
- **Etsy 店铺筛选与表现研究**：按店铺关键词/URL、销量、周销量、收藏、评论、开店时间、国家、主营类目、Raving、星标和状态筛选店铺，并返回店铺公开表现字段；使用 `toolName=ehunt/etsy/storeQuery`。
- **单个 Listing 详情审查**：对一个合法的 Etsy 商品直链提取标题、描述、价格区间、币种、图片、变体、数量、类目、发货地、预计送达、店铺资料和评论聚合信号；使用 `toolName=etsy/product/detail`。
- **结果审计与复用**：保留调用参数摘要、结果标识和积分字段用于追溯；同一任务内相同 `toolName + arguments` 不得重复调用。

### ❌ 边界与限制

- **类目数据依赖同步**：类目检索只查询已写入库的数据；库未由 `_ehunt_syncEtsyCategory` 同步时可能返回空结果，本能力不把空结果解释为 Etsy 没有该类目。
- **当前公开数据**：商品、店铺和 Listing 结果是查询时的公开或数据服务快照，不保证字段始终存在、准确或持续更新；不得据此承诺销量、收入、排名或未来趋势。
- **分页与费用**：商品和店铺按返回条数动态计费，翻页会产生新的请求和费用；失败、空结果或参数错误后不得自动换词、换链接、翻页或改参数连续试探。
- **排序编码不同**：商品查询 `sortBy` 为 `1~6` 且 `sortDesc` 使用 `1=降序、2=升序`；店铺查询 `sortBy` 为 `8~11` 且 `sortDesc` 使用 `1=降序、0=升序`，不得混用。
- **单 Listing 输入严格**：详情接口只接受 `etsy.com` 或其子域的 HTTPS `/listing/<数字ID>` 直链，最多一个 slug 段；一次只查一个 Listing，不接受搜索页、店铺页、非 Etsy 域名或缺少数字 ID 的链接。
- **反馈数据为聚合**：详情只提供评论数量、评分、标签和动态分项，不提供逐条买家评论、情感全文或评论下载；商品/店铺查询也不替代评论分析工具。
- **不提供卖家操作**：不负责 Listing 创建/编辑、店铺管理、订单、库存、广告、物流、采购、支付或 Etsy 账号操作，也不负责专利/商标/版权判断。
- **认证与运行条件**：WorkBuddy 自动注入 MCP Authorization；不得要求用户提供或配置凭证。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找 Etsy 类目 ID”“给商品筛选找 category” | `linkfox-etsy-category-search`：用类目关键词查名称、`id`、`parentIds` | 已知类目 ID 时直接把它传给商品/店铺查询；库未同步时先完成 `_ehunt_syncEtsyCategory` |
| “按关键词/价格/销量筛 Etsy 商品”“做 Etsy 选品池” | `linkfox-etsy-product-query`：多维筛选和分页列表 | 只有一个已知 Listing 直链且要标题、图片、变体、发货和评论聚合时换 `linkfox-etsy-product-detail` |
| “找高销量 Etsy 店铺”“筛店铺表现/国家/开店时间” | `linkfox-etsy-store-query`：店铺维度筛选和排序 | 需要店铺内具体商品时先用店铺结果中的 URL/名称继续业务查询；需要单商品完整页面时换详情查询 |
| “拆这个 Etsy Listing”“提取这个商品链接的图片和价格” | `linkfox-etsy-product-detail`：单 Listing 当前公开详情 | 需要关键词、多商品、价格/销量区间或榜单筛选时换 `linkfox-etsy-product-query`；不要用详情接口批量试探 |
| “先找类目，再按类目筛品” | 先 `linkfox-etsy-category-search`，再 `linkfox-etsy-product-query` | 若用户只需要类目名称/层级，不必追加商品查询；追加调用前说明商品接口按返回条数计费 |

选择时先判断用户要的是类目元数据、商品集合、店铺集合还是单个 Listing 页面；再检查输入是关键词/筛选条件还是严格直链。多个能力都能满足时，优先选择请求更少、返回粒度与目标一致的默认推荐，并在可能产生额外积分消耗时让用户决定是否继续。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 精确 `toolName` | 本地脚本 |
|---|---|---|---|---|
| `linkfox-etsy-category-search` | `_ehunt_etsyCategorySearch`：按关键词检索已同步类目 | `references/linkfox-etsy-category-search.md` | `ehunt/etsy/etsyCategorySearch` | 无 |
| `linkfox-etsy-product-query` | `_ehunt_productQuery`：多维筛选 Etsy 商品 | `references/linkfox-etsy-product-query.md` | `ehunt/etsy/productQuery` | 无 |
| `linkfox-etsy-store-query` | `_ehunt_storeQuery`：多维筛选 Etsy 店铺 | `references/linkfox-etsy-store-query.md` | `ehunt/etsy/storeQuery` | 无 |
| `linkfox-etsy-product-detail` | Listing 详情：查询一个 Etsy 商品直链 | `references/linkfox-etsy-product-detail.md` | `etsy/product/detail` | 无 |

Feedback API 与工具网关分离，按 `references/linkfox-etsy-product-detail.md` 原有规则处理，不属于 `proxy_call` allowlist。

## MCP 调用方式

- **MCP server**：`LinkFox`
- **URL**：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- **唯一工具**：`proxy_call`
- **调用结构**：`{"toolName":"<allowlist 中的精确值>","arguments":{...}}`。原请求参数对象直接作为 `arguments`，不增加 `body`、`params`、`data` 或另一层 `arguments`。
- **allowlist**：`ehunt/etsy/etsyCategorySearch`、`ehunt/etsy/productQuery`、`ehunt/etsy/storeQuery`、`etsy/product/detail`。精确匹配并区分大小写，不得以旧 operation 展示名代替。
- **认证**：WorkBuddy 自动注入 Authorization。配置、文档和 `arguments` 不得加入 headers、API Key、token、JWT、手机号或其他凭证。
- **禁止直连**：不得使用 curl、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 或 `proxy_call` 缺失时停止，不得 HTTP fallback。
- **响应处理**：先检查 MCP 连接、schema 和 `isError`，再读取 text/structured content；text 为 JSON 字符串时只解析一次，最后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`。
- **输出与去重**：新链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。失败、空结果或返回不理想时不得自动重试；相同 `toolName + arguments` 不得重复调用，保留参数摘要、结果标识和积分字段追溯。
- **读数据建议**：按 reference 定向读取完整标题、图片、描述或列表字段，避免把整份大响应放入上下文。空数组、`null`、空字符串和源端不可用字段要按原样记录。
- **完整参数位置**：请求参数、范围编码、响应字段和错误处理见 4 个业务 reference；Feedback API 规则见 `references/linkfox-etsy-product-detail.md`；认证/计费引导见 `references/onboarding.md`。
- **调用成本控制**：类目检索本地库查询不消耗积分；商品和店铺按本页返回数量动态计算，公式为返回商品/店铺数 × 1.8；详情接口会消耗积分，实际以响应 `costToken` 为准。任何追加查询、翻页或改参数前先向用户说明可能的额外费用。

## 使用示例

### 类目定位层

```json
{"keyword":"jewelry","page":1,"pageSize":50}
```

以 `toolName=ehunt/etsy/etsyCategorySearch` 调用 `proxy_call`。重点读取 `categories[]` 的 `id`、`name`、`categoryLevel`、`parentId`、`parentIds`，将选中的 `id` 原样传给后续商品/店铺筛选。类目库需要先同步，查询本身不计积分。

### 商品找品层

```json
{"searchKey":"poster","currencyCode":"USD","beginPrice":20,"endPrice":100,"beginSales":100,"productType":"1,4","sortBy":1,"sortDesc":1,"page":1,"pageSize":20}
```

以 `toolName=ehunt/etsy/productQuery` 调用 `proxy_call`。重点读取 `products[]` 的 `title`、`productUrl`、`price`、`salesTotal`、`salesWeekly`、`favorites`、`reviews`、`tags`、`category`、`shipsFrom` 和 `isPick/isBestsell/isRaving`，同时保留 `productNum`、`total`、`costToken`。本页返回 20 条时按动态规则约消耗 36 积分；下一页另计，继续前须告知用户。

### 店铺筛选层

```json
{"searchKey":"ceramic","country":"US","beginSalesWeekly":10,"endSalesWeekly":1000,"isRaving":1,"sortBy":9,"sortDesc":1,"page":1,"pageSize":20}
```

以 `toolName=ehunt/etsy/storeQuery` 调用 `proxy_call`。重点读取 `stores[]` 的 `storeName`、`storeUrl`、`salesTotal`、`salesWeekly`、`reviews`、`favorites`、`productCount`、`rating`、`startAt`、`country` 和 `category`，同时展示 `storeNum`、`total`、`costToken`。本页返回 20 条时按动态规则约消耗 36 积分；店铺升序应使用 `sortDesc: 0`，不能套用商品查询的 `2`。

### 单 Listing 详情层

```json
{"productUrl":"https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt"}
```

以 `toolName=etsy/product/detail` 调用 `proxy_call`。该请求必须是 Etsy Listing HTTPS 直链且只查一个商品；重点读取 `data[0]` 的 `productId`、`title`、`price/lowPrice/highPrice`、`currency`、`image/images`、`variants`、`maxQuantity`、`category`、`countryShippingFrom`、`deliveryDaysMin/Max`、`shopName/shopUrl/shopSales`、`reviews/star/shopReviews`、`highlightsTags/reviewsTags/reviewsScores`。响应可能缺少公开页面字段，不能把缺失值静默修复为推断值；当前详情不提供历史价格或逐条评论。

## 展示规则

1. **先给结论粒度**：类目结果先展示匹配数量和可复用 `id`；商品/店铺结果先展示筛选条件、页码、返回数和主要排序；详情结果先展示标题、Listing ID、店铺、类目、价格区间和币种。
2. **标注数据来源与时间**：列表结果标注 Etsy 数据服务 `ehunt`/`etsy`，类目结果标注“已同步 Etsy 类目库”，详情标注为“当前公开 Listing 快照”，并保留查询时间和响应中的 `costToken`。
3. **列表字段按用途呈现**：商品优先呈现标题、链接、价格、销量、周销量、收藏、评论、标签、发货地和店铺；店铺优先呈现名称、链接、销量、周销量、评论、收藏、商品数、评分、开店时间、国家和类目；不要把 `productNum/storeNum` 误称为本页返回条数。
4. **详情媒体适度展开**：主图可内联展示，默认只说明剩余图片数量；有变体和最大数量时再展示；长描述和完整图片数组先摘要，新 MCP 链路不承诺本地落盘。
5. **保留不可用状态**：`null`、空字符串、空数组或疑似误识别的店铺字段按“不可用/提取不确定”标注；不把 `0`、`-1`、缺失字段或空评分改成正常业务值，也不自行换链接补抓。
6. **区分聚合与逐条数据**：详情中的 Listing 评论、店铺评论、`highlightsTags`、`reviewsTags`、`reviewsScores` 是聚合信号，不能表述为逐条评论、情感结论或用户画像。
7. **错误要可行动**：按 `errcode`/`errmsg` 或 HTTP 状态说明失败原因，并给出对应修正建议：类目库未同步、URL 不合法、页面类型错误、参数越界、国家/类型编码错误、401/402、超时或上游异常；失败时不自动连续重试。
8. **客观表达与边界提示**：不把销量、相似度、评分或标签直接包装成保证性结论；不提供店铺收入、未来趋势、侵权法律结论、运营承诺或个体评论分析。需要追加查询时先说明新增费用，由用户决定。
9. **反馈上报**：若用户明确表达结果与意图不符、缺字段、赞扬、不满或改进建议，按 `references/linkfox-etsy-product-detail.md` 中的 Feedback API 规则上报，不中断当前结果展示；反馈端点与 Etsy 数据端点分开，失败不影响主查询结果。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`，并分层判断 MCP 连接、代理层与下游业务响应。WorkBuddy 自动注入 Authorization，不得要求用户手工填写凭证或将凭证放入 `arguments`。

- MCP 或 `proxy_call` 缺失：停止业务调用，提供 MCP 配置并提示重启或重载 WorkBuddy；Skill 不能自行安装或热加载 MCP。
- MCP 连接 401：提示重新登录、重载连接，仍失败则联系 WorkBuddy 管理员。
- 代理成功但下游 JSON 为 401：报告自动授权或下游业务认证失败，不得索取 Key。
- 下游 JSON 为 402 或积分不足：引导访问 `https://agent.linkfox.com/`，不得自动选套餐、下单、支付或轮询。
- 403 与其他错误：按业务 reference 原样处理，不得错误归类为 401/402，也不得自动重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
