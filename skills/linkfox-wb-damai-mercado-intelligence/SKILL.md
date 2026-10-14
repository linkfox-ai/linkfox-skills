---
name: linkfox-wb-damai-mercado-intelligence
display_name: LinkFox 大麦美客多选品
display_name_en: LinkFox Damai Mercado Libre Product Intelligence
description: 面向美客多跨境选品与市场调研的市场、商品、销量趋势、图片相似商品和评论洞察能力。
description_zh: 面向 Mercado Libre 美客多卖家与选品人员，查询墨西哥、巴西、阿根廷、智利和哥伦比亚市场的类目、行业规模、商品快照、销量趋势、图片相似商品及评论数据，支持从类目定位到商品核查的可审计分析；适用于市场调研、竞品筛选、商品趋势判断和评论研究，不适用于店铺或订单等官方卖家操作。完整参数与响应字段见 references/，本地图片上传辅助见 scripts/。
description_en: Market and product intelligence for Mercado Libre selection research across Mexico, Brazil, Argentina, Chile, and Colombia, covering categories, industry metrics, product snapshots, sales trends, image similarity, and reviews with auditable filters and coverage. It does not perform seller-account or order operations. Full parameters and response fields are in references/; the local image upload helper is in scripts/.
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


# LinkFox 大麦美客多选品（LinkFox Damai Mercado Libre Product Intelligence）

为美客多选品和市场调研提供从类目定位、市场规模观察、商品筛选，到销量趋势、图片相似商品和评论核查的一体化数据能力。Agent 应先根据用户问题选择 operation，再按市场、筛选条件和时间覆盖呈现可核验结果；不把数据推断为平台保证的销量、利润或法律结论。

当前包含 1 个子能力标识和 7 个 operation：`search_categories`、`industry_overview`、`search_product_snapshots`、`product_sales_trend`、`image_search_products`、`review_search`、`get_my_quota_status`。七个 operation 均放在 `/damai/call` 的原请求体中；MCP 外层精确 `toolName` 为 `damai/call`。本地图片另通过 `oss/file/presignedPut` 获取预签名 URL，再由本地 helper 上传。

## 能力边界

### ✅ 能力范围

- **类目定位**（`linkfox-damai-mercado-market-intelligence` / `search_categories`）：按目标站点本地语言搜索候选类目，返回类目 ID、当地名称与路径、层级、叶子标记，以及可用的近 30 天订单、GMV、价格、商品和商家指标；`search_categories` 免费，适合在行业分析前解析类目。
- **行业概览**（`industry_overview`）：基于 `category_id` 与市场代码读取行业月度订单、均价、GMV趋势和类目摘要，适合判断类目规模与时间变化；这是收费 operation。
- **商品快照筛选**（`search_product_snapshots`）：按本地语言关键词、类目、商品 ID、商品 URL、店铺 ID 或店铺名称筛选商品，并按价格、近 30 天/历史销量、评分、评论数、上架日期、卖家类型、履约等条件排序分页；返回商品、卖家、类目、销量、评价、库存、履约和属性聚合等字段；这是收费 operation。
- **单品销量趋势**（`product_sales_trend`）：按商品 ID读取月度和 ISO 周订单序列、请求区间、实际覆盖天数与覆盖提示；这是收费 operation。
- **图片相似商品**（`image_search_products`）：用公开图片 URL或图片 Base64在指定市场检索相似美客多商品，返回商品 ID及服务状态；本地图片先通过 `oss/file/presignedPut` 获取预签名 URL，再用 `scripts/upload_image.py` 上传并取得公开 URL；这是收费 operation。
- **评论查询**（`review_search`）：按商品 ID分页获取评论原文、评分、标题/商品名、日期、买家字段及上游提供的本地化文本；这是收费 operation。
- **配额与连接诊断**（`get_my_quota_status`）：读取当前托管上游账号的套餐、额度和积分计费状态，仅用于判断是否可以继续收费查询；免费，向用户展示时必须隐藏账号编码等内部标识。
- **会话审计与结果读取**：记录精确 endpoint `toolName`、原始下游请求体、调用时间、收费状态和必要结果标识。不要假定 MCP 提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。
- **市场覆盖**：`MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚；省略 `market_code` 时按 `MLM` 处理。类目词和商品关键词应使用所选市场的本地语言。

### ❌ 边界与限制

- **网关边界**：市场数据只通过 `proxy_call` 调用 `damai/call`，不得直接访问大麦上游，也不得向用户索取或转发上游 `X-API-Key`。
- **输入约束**：`search_product_snapshots` 至少需要 `keyword`、`category_id`、`sku_id`、`product_url`、`shop_id`、`shop_query` 之一；`image_search_products` 至少需要 `image_url` 或 `image_base64`；不得传 `uId`、`uid`、`memberId`、未记录的 camelCase 别名或未知字段。
- **范围约束**：`product_sales_trend.days` 只能为 1–731；商品搜索和评论的 `limit` 最大 100；日期使用 `YYYYMMDD` 或 `YYYY-MM-DD`；排序字段只能用 API 记录的枚举。
- **数据边界**：数据可能延迟、不完整或没有匹配记录；`data_available=false`、空列表和覆盖不足是有效业务结果，不自动改词、换市场、换邮编、翻页或替换图片。
- **计费边界**：`search_categories` 与 `get_my_quota_status` 免费；其余 5 个 operation 每次成功调用收取 12 LinkFox 积分（￥0.12），并可能消耗上游套餐次数或上游积分。收费请求超时、5xx、限流或结果为空时，不自动重放或连续试探。
- **图片边界**：图片 URL必须可公开访问；不要向用户展示预签名 URL 的查询参数、完整 Base64、API Key或提供方账号标识。图片搜索只返回相似商品 ID，读取完整商品记录需要另一次可能收费的商品查询。
- **业务边界**：不执行店铺授权、Listing 发布、库存更新、订单履约、退款、广告投放或其他 Mercado Libre 官方卖家 API；不提供平台保证的预测销量、利润、竞争结论或其他未经响应字段支持的推断。
- **认证边界**：WorkBuddy 自动注入授权，禁止添加或索取 headers、API Key、JWT、手机号及认证 token。MCP/代理层和下游业务层错误必须分开处理；HTTP 403 属于权限/路由问题，不当作充值问题处理。

## 工具选择指南

按“用户要回答的业务问题”选择 operation；需要多个维度时先确定最小必要调用集合，并在发起收费调用前告知预计调用次数和积分消耗。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “找墨西哥手机类目”“给我美客多类目 ID” | `search_categories` | 已有明确 `category_id` 且要看规模/趋势时改用 `industry_overview`；不要直接猜类目 ID |
| “这个类目的市场规模/GMV/订单趋势” | `industry_overview` | 需要先从名称找 ID 时先免费调用 `search_categories`；需要商品明细时改用 `search_product_snapshots` |
| “筛选月销高的商品”“按关键词找竞品”“查这个 SKU 的商品信息” | `search_product_snapshots` | 只要时间序列用 `product_sales_trend`；只研究买家反馈用 `review_search`；如果只有图片先用 `image_search_products` |
| “这个商品最近销量怎么走” | `product_sales_trend` | 还需要价格、卖家、库存、评分等当前快照时改用 `search_product_snapshots` |
| “用图片找美客多同款/相似款” | `image_search_products` | 只有本地图片时先调用 `oss/file/presignedPut`，再用 `scripts/upload_image.py` 执行预签名 PUT；拿到商品 ID 后若要销量或评论，再由用户决定是否调用收费 operation |
| “分析这个商品的评论/差评” | `review_search` | 需要先确认商品信息或补充筛选字段时用 `search_product_snapshots`；不要用销量趋势代替评论查询 |
| “查看套餐、额度、是否还能继续查” | `get_my_quota_status` | 仅在收费 operation 返回套餐/积分异常时调用一次辅助诊断；不要把内部账号字段直接展示给用户 |

### 工具选择思路

- 先区分“发现类目”“观察类目市场”“筛商品”“看单品趋势”“找图片相似商品”“读评论”“查额度”这七类意图，再校验所需输入是否齐全。
- 默认优先使用能直接回答问题且字段最少的 operation：类目名称先免费解析，已知商品 ID 时不必先做关键词搜索；只有用户需要额外维度时才追加调用。
- `search_product_snapshots` 与 `product_sales_trend` 都涉及销量，但前者是商品快照与筛选排序，后者是单个商品的时间序列；`image_search_products` 只发现 ID，不替代商品详情查询。
- 多个收费 operation 都有可能满足需求时，说明每个调用的用途、输入、预期出参和积分成本，让用户决定是否继续；不因空结果自动扩大条件。
- 任何收费调用前检查本任务是否已使用相同 `toolName + arguments`；不得重复调用。用户要求刷新时先提醒可能产生新的积分和上游额度消耗。

## 业务需求路由速查

按【工具选择指南】确定 operation 后，读取 reference 的完整参数和响应说明，再通过 `proxy_call` 调用。

### Endpoint allowlist

| 用途 | 原 endpoint | 精确 `toolName` | reference | 本地辅助 |
|---|---|---|---|---|
| 七个市场数据 operation 的共享代理 | `/damai/call` | `damai/call` | `references/linkfox-damai-mercado-market-intelligence.md` | 无 |
| 本地图片上传前获取预签名 URL | `/oss/file/presignedPut` | `oss/file/presignedPut` | `references/linkfox-damai-mercado-market-intelligence.md` | `scripts/upload_image.py` 仅执行预签名 PUT |

### Operation 路由

| operation | 业务能力 | 成本 |
|---|---|---|
| `search_categories` | 搜索候选类目 | 免费 |
| `industry_overview` | 类目行业概览 | 收费 |
| `search_product_snapshots` | 商品快照搜索与筛选 | 收费 |
| `product_sales_trend` | 商品销量趋势 | 收费 |
| `image_search_products` | 图片相似商品搜索 | 收费 |
| `review_search` | 商品评论查询 | 收费 |
| `get_my_quota_status` | 上游套餐与额度状态 | 免费 |

## 调用方式

- 固定 MCP Server：`LinkFox`，URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`，唯一工具为 `proxy_call`。
- 市场数据的 MCP 外层固定为 `{"toolName":"damai/call","arguments":{"toolName":"<operation>","arguments":{...}}}`。内层是原共享 endpoint 请求体，不得扁平化或丢失。
- `toolName` 精确匹配上方 allowlist，区分大小写且不得带前导 `/`。七个 operation 不是 MCP 外层 `toolName`。
- WorkBuddy 自动注入授权。禁止添加 `headers`、Authorization、API Key、上游 `X-API-Key`、JWT、手机号或认证 token，也不要向用户索取。
- 禁止使用 `curl`、`urllib`、`requests`、`httpx` 或其他方式直连旧工具网关；MCP 缺失或失败时不得回退 HTTP。
- `proxy_call` 的 text 若为 JSON 字符串只解析一次。先检查 MCP/schema/`isError`，再检查下游 `code`、`errcode`、`error`、`errmsg` 或 `msg`。
- 同一任务内相同 MCP 外层 `toolName + arguments` 不得重复调用；收费 operation 失败、空结果、429/5xx 或超时不自动重试、改参或翻页。
- 本地图片先用 `proxy_call` 调用 `oss/file/presignedPut`，参数为 `contentType`、`fileExtension`；再把返回的预签名 URL 通过标准输入交给 `python scripts/upload_image.py <本地图片路径>`。helper 只执行 OSS PUT，不访问 LinkFox 网关。
- `search_categories`、`get_my_quota_status` 免费，其余五项成功调用每次 12 LinkFox 积分（￥0.12），并可能消耗上游额度。完整参数、响应字段、错误码和图片流程见 reference。

## 使用示例

以下示例均使用真实记录的字段名。市场代码必须与用户目标站点一致，关键词使用当地语言；收费示例在执行前要提示调用次数和积分。

### 1. 免费解析类目

```json
{"toolName":"damai/call","arguments":{"toolName":"search_categories","arguments":{"market_code":"MLM","query":"celulares","limit":10}}}
```

主要出参：`data` 中的类目记录或 `request_overview`、`record_count`、`records[]`，记录可能包含类目 ID、当地化路径、层级、叶子标记、近 30 天订单/GMV、均价、商品数和店铺数。该 operation 免费；找到目标类目后再决定是否调用行业概览。

### 2. 查询类目行业规模与趋势

```json
{"toolName":"damai/call","arguments":{"toolName":"industry_overview","arguments":{"market_code":"MLM","category_id":"MLM1055"}}}
```

主要出参：`data_available`、`market_code`、`taxonomy_code`、`industry_summary`，以及月销量、月均价、月 GMV、商品数、活跃商品数、平均日销量和近 30 天交易额。`monthly_order_growth_rate` 可能是 number、array 或 null，应按响应原样解释；这是收费 operation，空数据也可能消耗额度。

### 3. 按类目筛选商品机会

```json
{"toolName":"damai/call","arguments":{"toolName":"search_product_snapshots","arguments":{"market_code":"MLM","category_id":"MLM1055","sort_by":"sales_30d","sort_order":"desc","page":1,"limit":20,"sales_30d_min":100,"shop_type":"local"}}}
```

主要出参：`request_overview`、`record_count`、`matched_count`、`records[]`、`features`、`notices`。优先读取商品 ID/标题、价格和币种、近 30/60/90 天及累计销量、评分/评论数、卖家、类目路径、上架日期、履约和库存；没有提供的字段不可补造。`limit` 不超过 100，分页或改筛选会产生额外收费调用。

### 4. 查看单品销量趋势

```json
{"toolName":"damai/call","arguments":{"toolName":"product_sales_trend","arguments":{"market_code":"MLM","sku_id":"MLM1602785195","days":90}}}
```

主要出参：`product_code`、`range_start_date`、`range_end_date`、`requested_day_count`、`data_available`、`data_coverage`、`aggregation_period`、`monthly_order_series`、`weekly_order_series`、`notices`。必须区分请求的 90 天与实际覆盖天数，覆盖不足时明确提示；`days` 只能为 1–731。

### 5. 图片找相似商品

```json
{"toolName":"damai/call","arguments":{"toolName":"image_search_products","arguments":{"market_code":"MLM","image_url":"https://example.com/product.jpg","page":1,"limit":20}}}
```

主要出参：`request_overview`、`provider_status`、`display_message`、`record_count`、`product_code`、`provider_payload`；图片搜索结果通常只提供商品 ID，若要价格、销量或评论需另行调用相应 operation。图片 URL必须公开可访问；本地图片先按预签名 MCP 与本地 helper 两阶段流程处理，不要把 `image_base64` 或预签名查询参数写入用户可见消息。该 operation 收费。

### 6. 查询商品评论

```json
{"toolName":"damai/call","arguments":{"toolName":"review_search","arguments":{"market_code":"MLB","sku_id":"MLB123456789","page":1,"limit":20}}}
```

主要出参：`market_code`、`product_code`、`page_number`、`page_size`、`matched_count`、`reviews[]`；评论字段按上游实际提供，可能包括 ID、评分、标题/商品名、原文、本地化文本、时间和买家名。保留原文语言并标注翻译是否来自上游；`limit` 最大 100。评论为空不代表商品无评价，也不触发自动翻页。

### 7. 查询额度状态

```json
{"toolName":"damai/call","arguments":{"toolName":"get_my_quota_status","arguments":{}}}
```

主要出参可能包括 `credit_balance`、`credit_policy`、`plan_code`、`plan_name`、`quota_limit`、`used_quota`、`quota_ends_at`、`available_points`、`points_mode`，兼容版本也可能返回 `request_allowance`、`requests_consumed`、`requests_available` 等。该 operation 免费，仅用于连接或成本诊断；隐藏 `customer_account_code`、`customer_code` 等内部账号标识。

## 展示规则

1. **按请求上下文呈现**：每次结果都标注市场代码、用户筛选条件、时间覆盖、记录数、币种和分页信息；省略的字段不推断为零。
2. **类目结果**：展示完整当地化路径、类目 ID、层级和是否为终端/叶子类目；同时区分近 30 天指标与静态数量。
3. **行业结果**：优先展示 `data_available` 和 `industry_summary`，将月订单、均价、GMV和增长字段按响应真实类型呈现；数据不可用或覆盖不足时明确说明。
4. **商品结果**：优先展示商品 ID/标题、价格和币种、近 30 天订单、累计订单、评分/评论数、卖家、类目、上架日期、履约和库存；对 `null`、缺失、`0` 或 `-1` 等不可用值标注 N/A 或省略，不能当作实际业务数值。
5. **趋势结果**：同时显示请求天数、实际起止日期、覆盖天数/比例和月度或 ISO 周聚合方式；`notices` 中的覆盖不完整提示必须保留。
6. **图片结果**：明确说明这是相似商品 ID/提供方状态结果，不把相似性当作同款、销量或质量结论；获取完整商品记录需要另一次可能收费的调用。
7. **评论结果**：保留评论原文语言，只有在响应提供翻译字段时展示翻译，并区分原文与本地化文本；不要用少量评论概括全部用户。
8. **来源与审计**：说明数据来自大麦美客多市场洞察接口，并记录查询时间、市场、参数摘要和收费状态；不展示 `rawResponse`、API Key、Base64、预签名 URL 或提供方账号标识。
9. **客观边界**：只呈现响应支持的数据，不编造需求、利润、市场份额、竞争强度或预测；结果可延迟或不完整时，使用“数据不可用/当前覆盖不足/未返回匹配记录”等客观措辞。
10. **错误处理**：同时检查 HTTP 状态、`code`/`errcode`、`error`/`errmsg` 和业务 `data`，不能只看脚本退出码。`1002` 修正参数后再执行；401/402 走 onboarding；403 联系后端检查路由或托管 Key；1005 联系管理员；429/5xx、1003 或超时不自动重试收费操作；成功但无数据按筛选条件如实展示。
11. **反馈**：当行为、文档或展示与用户意图不符，或用户表达满意/不满时，按 reference 中的 Feedback API 发送必要的脱敏反馈；不得包含凭证、隐私、Base64 或完整大响应。

## 认证与积分异常

WorkBuddy 自动处理 MCP 授权，禁止要求用户提供 API Key、上游 Key、token、JWT、手机号或认证 headers。遇到异常时先区分错误层级，完整规则见 `references/onboarding.md`。

- **MCP 或 `proxy_call` 缺失**：停止业务调用，提示用户检查或重新加载 `LinkFox` 并重启 WorkBuddy；不得改走旧 HTTP 网关。
- **MCP 连接或代理层 401**：提示用户重新登录 WorkBuddy、重载 MCP 连接；仍失败时联系 WorkBuddy 管理员，不得手工填写 Authorization。
- **代理成功但下游业务 401**：按 WorkBuddy 自动授权或下游认证异常报告，不得把 Key 放入 `arguments`。
- **下游业务 402 或积分不足**：引导用户访问 `https://agent.linkfox.com/` 检查积分或套餐；不得自动选套餐、下单、支付、轮询或重试。
- **下游业务 403、`1005`**：按权限、路由或托管上游认证异常处理，不属于充值流程，绝不要求用户提供上游 `X-API-Key`。
- **上游额度诊断**：必要时仅调用一次免费的 `get_my_quota_status`；MCP 外层仍使用 `damai/call`，不得展示内部账号编码。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
