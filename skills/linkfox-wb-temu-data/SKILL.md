---
name: linkfox-wb-temu-data
display_name: LinkFox Temu选品
display_name_en: LinkFox Temu Product Research
description: Temu商品、店铺与类目数据查询能力，支持筛选、排行、选品和类目定位。
description_zh: 面向 Temu 选品与市场调研的统一数据查询能力：按关键词、商品或店铺标识、类目、价格、销量、评分、评论、上架时间和托管模式筛选商品与店铺，并检索可复用的类目 ID；支持分页、排序、结构化结果展示以及类目数据同步前置检查。当用户需要 Temu 商品选品、店铺研究、商品或店铺排行、类目 ID 定位、全托管/半托管筛选或 Temu 市场数据时触发。能力不提供订单、广告、供应链、评论原文或法律结论；完整参数与响应字段见 references/。
description_en: Unified Temu research data access for product selection and market analysis. Query and filter products and stores by keywords or IDs, categories, price, sales, ratings, reviews, listing dates, and fulfillment mode; locate reusable category IDs, handle pagination and sorting, and check category synchronization prerequisites. Use when users need Temu product research, store analysis, rankings, category lookup, or full-managed/semi-managed filtering. It does not provide orders, advertising, sourcing, review text, or legal conclusions. Full parameters and response fields are in references/.
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


# LinkFox Temu选品（LinkFox Temu Product Research）

面向 Temu 选品与市场调研的统一数据查询能力：帮助 Agent 从商品、店铺和类目三个维度定位市场机会，按可解释的筛选条件返回结构化列表、数量、排序结果和可复用的类目标识。适用于商品筛选、店铺表现研究、类目定位、全托管/半托管对比及后续条件联查。本能力覆盖 3 个子能力、4 个 operation：商品查询（linkfox-temu-product-query，1 个）、店铺查询（linkfox-temu-store-query，1 个）、类目检索与同步前置（linkfox-temu-category-search，2 个）。

## 能力边界

### ✅ 能力范围

- **Temu 商品筛选与排行**：使用 linkfox-temu-product-query，通过 ehunt/temu/productQuery 按关键词、商品 ID/店铺 ID、前台或后台类目、价格、评分、评论数、总/周/日销量、上架日期、上下架状态、全托管/半托管、半托管地区和标签筛选，并按价格、销量或评分排序。适合商品池发现、爆款初筛、价格带比较和选品候选整理。
- **Temu 店铺筛选与表现研究**：使用 linkfox-temu-store-query，通过 ehunt/temu/storeQuery 按店铺名称/ID、国家站点、后台类目、托管模式、总/周/月销量与销售额、评分、评论、粉丝、商品数和开店日期筛选，并支持店铺排行。
- **Temu 类目 ID 定位**：使用 linkfox-temu-category-search，通过 ehunt/temu/temuCategorySearch 在已同步的本地类目库中按中文名、英文名或类目 ID 子串检索，返回层级、父类目、是否有子类目以及可供商品/店铺查询使用的 id/categoryId。
- **类目数据同步前置检查**：通过 ehunt/temu/syncTemuCategory（无入参）同步分类树到本地库；当类目检索为空且用户确实需要查找类目时，先说明同步前置并调用该 operation，再重新检索。
- **跨维度联查**：先用类目检索得到类目 ID，再把 ID 放入商品查询的 categoryHome/categoryBackend 或店铺查询的 category；先用店铺结果取得 storeId，再回到商品查询的 searchKey 做店铺商品池定位。每一步的返回数量和计费均单独记录。
- **结构化结果与追溯**：查询端点返回 products、stores 或 categories 列表及 total、来源和渲染元数据；保留参数摘要、结果标识和积分字段用于追溯。

### ❌ 边界与限制

- **数据形态**：本能力提供筛选/检索结果和聚合字段，不等同于商品详情页、店铺详情页或评论原文；不能据此补齐未返回的 SKU、变体、物流、利润、供应商、广告或订单信息。
- **类目前置**：类目检索依赖已同步的本地类目库；同步未完成、类目已删除或关键词不匹配时可能返回空结果。不得把空结果推断为 Temu 不存在该类目。
- **筛选语义**：商品与店铺的区间字段应按成对的 Begin/End 或 Min/Max 传入；站点 ID、类目 ID、标签和地区的多值格式为逗号分隔。不得擅自把自然语言条件转换成未定义的字段。
- **分页与实时性**：page 从 1 开始，单页上限依端点而不同；每翻一页都是新请求。数据以数据服务返回为准，不能承诺平台后台实时、完整或永久一致。
- **认证与计费**：WorkBuddy 自动注入 MCP Authorization；商品和店铺查询按本页返回数量动态消耗积分，类目本地检索不消耗积分，但同步和 MCP 可用性仍受环境限制。重复、翻页、改参数或重试前先提示可能增加消耗。
- **不适用场景**：不处理 Temu 下单、订单/库存/物流、广告投放、店铺运营、Listing 文案优化、评论情感分析、供应链采购、图片找同款、商标/专利/版权判断或其他非 Temu 数据查询任务。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| 找 Temu 商品、按关键词筛商品、看价格/销量/评分或做商品选品 | linkfox-temu-product-query | 需要研究卖家整体经营规模、粉丝或店铺商品数时换用 linkfox-temu-store-query |
| 找 Temu 店铺、按站点/类目/销量/销售额筛店铺 | linkfox-temu-store-query | 需要查看具体商品池或按商品标签、日销量筛选时换用 linkfox-temu-product-query |
| 找到商品或店铺查询所需的类目 ID | linkfox-temu-category-search | 若本地没有结果，先用同一子能力的 ehunt/temu/syncTemuCategory，再重新检索 |
| 只知道类目中文名/英文名/ID 的一部分 | linkfox-temu-category-search | 不要直接把名称当作商品/店铺接口的 category ID；先定位 id/categoryId |
| 按前台类目筛商品 | linkfox-temu-product-query 的 categoryHome | 已知后台类目或需要店铺类目筛选时，分别使用 categoryBackend 或店铺查询的 category |
| 按后台类目筛店铺 | linkfox-temu-store-query 的 category | 需要按商品前台类目筛选时换用商品查询的 categoryHome |
| 研究全托管与半托管商品 | 商品查询的 isLocal，并在半托管时加 region | 研究店铺经营模式或店铺周/月销售额时换用店铺查询的 isLocal |
| 需要大范围结果 | 先设置明确条件，优先 pageSize 不超过 50 | 不要为了“全量”盲目翻页；先确认成本和用户是否需要更多页 |

选择思路：先判断用户要观察的实体是商品、店铺还是类目；需要类目 ID 时先查类目。商品和店铺都能表达“销量高/评分高”时，按用户要评估单品机会还是卖家整体经营来选择。优先采用筛选条件更贴合、请求页数更少的路径；同等满足时使用上表默认推荐。涉及翻页、同步或重复查询时，先说明数据范围和积分影响，再继续。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 精确 `toolName` | 本地脚本 |
|---|---|---|---|---|
| linkfox-temu-product-query | Temu 商品多维筛选、排序与分页 | references/linkfox-temu-product-query.md | `ehunt/temu/productQuery` | 无 |
| linkfox-temu-store-query | Temu 店铺多维筛选、排序与分页 | references/linkfox-temu-store-query.md | `ehunt/temu/storeQuery` | 无 |
| linkfox-temu-category-search | 已同步本地库中的 Temu 类目关键词/ID 检索 | references/linkfox-temu-category-search.md | `ehunt/temu/temuCategorySearch` | 无 |
| linkfox-temu-category-search | Temu 类目树同步前置 operation | references/linkfox-temu-category-search.md | `ehunt/temu/syncTemuCategory` | 无 |

## MCP 调用方式

- **MCP server**：`LinkFox`
- **URL**：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- **唯一工具**：`proxy_call`
- **调用结构**：`{"toolName":"<allowlist 中的精确值>","arguments":{...}}`。原请求对象直接作为 `arguments`，不增加 `body`、`params`、`data` 或另一层 `arguments`；无参同步也必须传 `{}`。
- **allowlist**：`ehunt/temu/productQuery`、`ehunt/temu/storeQuery`、`ehunt/temu/temuCategorySearch`、`ehunt/temu/syncTemuCategory`。精确匹配并区分大小写，不得使用展示名代替。
- **认证**：WorkBuddy 自动注入 Authorization。配置、文档和 `arguments` 不得加入 headers、API Key、token、JWT、手机号或其他凭证。
- **禁止直连**：不得使用 curl、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 或 `proxy_call` 缺失时停止，不得 HTTP fallback。
- **响应处理**：先检查 MCP 连接、schema 和 `isError`，再读取 text/structured content；text 为 JSON 字符串时只解析一次，最后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`。
- **输出与去重**：新链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。失败、空结果或返回不理想时不得自动重试；相同 `toolName + arguments` 不得重复调用，保留参数摘要、结果标识和积分字段追溯。
- **读数据建议**：确认 total/productNum/storeNum 或 categories 数量后按字段读取，不要为了查看单个字段把大响应全部放入上下文。展示时保留原始数值、单位、日期和空值含义。
- **完整参数位置**：商品、店铺、类目检索和同步的参数、响应、分页、排序、错误行为及示例见对应 reference；认证与积分引导见 references/onboarding.md。未在 reference 中定义的字段不得编造。

## 使用示例

### 商品选品筛选

使用商品查询筛选价格、评分、周销量和托管模式，适合建立候选商品池：

~~~json
{"searchKey":"kitchen organizer","categoryBackend":"123456","priceBegin":5,"priceEnd":30,"ratingBegin":4,"ratingEnd":5,"salesWeeklyBegin":100,"soldOut":0,"isLocal":0,"sortBy":"order_week-0","page":1,"pageSize":20}
~~~

关键出参：读取 productNum 了解符合条件的总数，从 products[] 查看 productId、productName/productNameCn、logoUrl、price、orderTotal/orderWeek/orderDay/orderMonth、rating、reviewNum、publishTime、soldOut、isLocal、localRegion、storeId、tags、customTags 和类目字段。商品查询按本页返回数量动态计费（每个产品 1.8 积分）；若需要下一页必须先提示会再次消耗。categoryBackend 应使用已确认的类目 ID，半托管筛选可增加 region。

### 店铺表现筛选

使用店铺查询按美国站、半托管、周销量和评分筛选店铺：

~~~json
{"siteId":"211","isLocal":"1","orderWeekMin":100,"orderWeekMax":5000,"ratingMin":4,"ratingMax":5,"productNumMin":10,"sortBy":"order_week_count-0","page":1,"pageSize":20}
~~~

关键出参：读取 storeNum 了解符合条件的店铺总数，从 stores[] 查看 storeId、siteId、storeName、logoUrl、orderTotal/orderWeek/orderMonth、totalRevenue/weekRevenue/monthRevenue、rating、listedTime、reviewNum、followerNum、productNum、categoriesCn/categories 和 isLocal。店铺查询按本页返回店铺数量动态计费（每个店铺 1.8 积分）；金额字段按 API 约定以 USD 为单位，分页或换条件都会产生新的请求。

### 类目 ID 定位与同步

先检索已同步的本地类目库：

~~~json
{"keyword":"kitchen","page":1,"pageSize":50}
~~~

关键出参：categories[] 中的 id、categoryId、parentId、level、categoryName、categoryNameEn、isDeleted、hasChildren；把确认后的 id/categoryId 用于后续商品的 categoryHome/categoryBackend 或店铺的 category。类目本地检索不消耗积分，pageSize 最大 200。若结果为空且用户需要继续找类目，先调用无入参的同步 operation：

~~~json
{}
~~~

同步成功通常返回 result=success 和 totalRows；同步会改变本地类目数据状态，应在同步后重新执行检索，而不是把空结果直接当作结论。同步操作本身是否可用以当前 WorkBuddy 工具元数据为准。

### MCP 调用

业务调用只使用 `proxy_call`；完整参数示例见对应 reference。商品与店铺的查询成本、类目库状态、认证和错误处理按上方规则执行。

## 展示规则

1. **先给结果类型和范围**：明确展示的是商品、店铺或类目列表，标注查询条件、页码/pageSize、返回条数 total，以及 productNum/storeNum（若响应提供）；不要把本页返回条数写成全库总量。
2. **保留来源元数据**：如返回 title、sourceType、sourceTool、type，应保留或说明其含义；Temu 数据通常标记 sourceType=temu、sourceTool=ehunt，type 可能为 tableListWorkbenches。不得把这些字段改写成未经返回的第三方来源。
3. **解释商品字段**：商品结果优先展示 productId、中文/英文名称、主图、价格、总/周/日/月销量、评分、评论数、上架时间、上下架状态、托管模式、地区、店铺 ID、标签和类目；soldOut=0 表示上架，soldOut=1 表示下架；isLocal=0 表示全托管，isLocal=1 表示半托管。
4. **解释店铺字段**：店铺结果优先展示 storeId、站点、店名、Logo、总/周/月销量、总/周/月销售额、评分、开店时间、评论、粉丝、商品数、类目和托管模式；销售额按返回字段约定展示 USD，不自行换汇或四舍五入成未声明的金额。
5. **解释类目字段**：类目结果展示 id/categoryId、parentId、level、中英文名称、isDeleted、hasChildren；isDeleted=1 时标注已删除，不推荐直接用于后续筛选；hasChildren=true 时提示仍可继续按类目树细分。
6. **处理空值与同步状态**：空数组、缺失字段、未同步、本地库无匹配和上游无数据要明确标注；类目空结果先检查同步状态。不要用估算、常识或其他平台数据填补空值。
7. **处理错误与成本**：如响应根级 code、errcode、errmsg、msg，只按实际返回展示并给出下一步修正建议；不把 401/402/403 混淆。展示商品/店铺结果时同时注明按页计费规则，以及继续翻页/重试可能增加积分。
8. **保证可追溯**：保留 `toolName`、参数摘要、结果标识和积分字段；新 MCP 链路不承诺缓存或响应落盘，用户要求具体字段时从当前响应读取，不凭摘要臆测。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`，并分层判断 MCP 连接、代理层与下游业务响应。WorkBuddy 自动注入 Authorization，不得要求用户手工填写凭证或将凭证放入 `arguments`。

- MCP 或 `proxy_call` 缺失：停止业务调用，提供 MCP 配置并提示重启或重载 WorkBuddy；Skill 不能自行安装或热加载 MCP。
- MCP 连接 401：提示重新登录、重载连接，仍失败则联系 WorkBuddy 管理员。
- 代理成功但下游 JSON 为 401：报告自动授权或下游业务认证失败，不得索取 Key。
- 下游 JSON 为 402 或积分不足：引导访问 `https://agent.linkfox.com/`，不得自动选套餐、下单、支付或轮询。
- 403 与其他错误：按业务 reference 原样处理，不得错误归类为 401/402，也不得自动重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
