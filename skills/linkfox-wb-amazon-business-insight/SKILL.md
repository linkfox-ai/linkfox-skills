---
name: linkfox-wb-amazon-business-insight
display_name: LinkFox 亚马逊商业洞察
display_name_en: LinkFox Amazon Business Insight
description: 面向亚马逊卖家的商业洞察能力，支持搜索词分析、关键词市场报告、指标反向选品和政策资讯查询。
description_zh: 面向亚马逊卖家的统一 WorkBuddy 商业洞察能力：分析 ABA 搜索词热度、趋势、点击份额和转化份额，生成美国站单关键词市场机会报告，按市场规模、增长、竞争、价格、人群、产品特征和评论痛点反向筛选赛道，并查询亚马逊政策资讯列表与正文。支持站点和时间范围参数、CSV 下载链接和安全展示；不覆盖广告投放管理、Listing 优化、具体 ASIN 详情/评论拆解、销量估算或法律/经营最终结论。
description_en: A unified WorkBuddy business-insight capability for Amazon sellers. Analyze ABA search-term popularity, trends, click share, and conversion share; generate US keyword market-opportunity reports; screen niches by market size, growth, competition, price bands, audience attributes, product features, and review pain points; and query Amazon policy feed lists and full policy articles. It supports marketplace and date-range parameters, CSV download links, and safe result presentation; it does not cover ad campaign management, listing optimization, specific ASIN details or review analysis, sales estimation, or final legal/business decisions.
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


# LinkFox 亚马逊商业洞察（LinkFox Amazon Business Insight）

为亚马逊卖家提供从搜索需求、关键词市场判断、赛道机会筛选到平台政策跟踪的商业洞察：根据用户已有关键词、筛选标准或政策时间范围，选择对应查询路径，返回可核验的数据表、Markdown 报告或政策正文，并明确站点、时间快照、参数和积分消耗。当前覆盖 4 个子能力和 5 个只读 API operation；其中政策子能力包含列表与详情两个 operation。

## 能力边界

### 能力范围

- **ABA 搜索词洞察**（`linkfox-aba-intelligent-query`）：调用 `proxy_call`，`toolName=aba/intelligentQuery`，按 15 个站点的周粒度搜索词数据分析搜索热度排名、趋势、季节性、点击份额、转化份额及高点击低转化 ASIN；可按用户明确要求生成 CSV 下载链接。详细参数见 `references/linkfox-aba-intelligent-query.md`。
- **关键词市场机会报告**（`linkfox-amazon-opportunity-report-by-keyword`）：调用 `proxy_call`，`toolName=amazon/opportunity/reportByKeyword`，针对美国站单个关键词生成涵盖市场潜力、产品特征、用户评论、客户画像、搜索趋势和定价分析的 AI Markdown 报告。详细参数见 `references/linkfox-amazon-opportunity-report-by-keyword.md`。
- **指标反向选品**（`linkfox-amazon-opportunity-search-by-metrics`）：调用 `proxy_call`，`toolName=amazon/opportunity/searchByMetrics`，从赛道指标池按市场规模与增长、品牌/产品集中度、价格档位、年龄/性别/收入/生命阶段、产品特征及评论卖点痛点筛选关键词和赛道。详细参数见 `references/linkfox-amazon-opportunity-search-by-metrics.md`。
- **政策资讯与正文**（`linkfox-amazon-policy-feed`）：先用 `toolName=amazon/policyFeed` 按站点和时间分页查询亚马逊卖家政策资讯，再用 `toolName=amazon/policyFeedDetail` 根据列表中的 `id` 获取完整 Markdown 正文。详细参数见 `references/linkfox-amazon-policy-feed.md`。

### 边界与限制

- WorkBuddy 自动注入 MCP Authorization；接口结果中的 `costToken`、错误信息和数据时间应随结果呈现。未授权、积分不足和余额问题按【解决认证和积分问题】处理。
- ABA 是约 3 年历史的周粒度搜索词数据，不是日实时数据；关键词报告是生成时点快照；指标反向选品是历史报告指标池快照；政策资讯可能比 Amazon 原页面稍有延迟。
- 关键词报告、指标反向选品目前仅支持美国站；ABA 支持 API 列出的 15 个站点；政策资讯支持 API 列出的站点，但站点筛选只对部分资讯类型生效。不得把不支持的站点静默改写成美国站。
- 关键词报告返回 Markdown，不适合直接进行结构化二次聚合；指标反向选品返回赛道/关键词级数据，不是 ASIN 级数据；ABA 不替代广告、评论或销量估算工具；政策详情必须使用列表返回的有效 `id`。
- 不适用范围包括广告竞价与 PPC 策略、Listing 文案优化、具体 ASIN 商品详情或销量估算、单个 ASIN 评论拆解、实时店铺搜索、账户内个性化通知，以及把商业洞察结果当作法律或平台最终裁定。
- 同一会话同一参数组合默认只调用一次。失败或空结果不得自动换关键词、翻页、改站点或连续试探；需要扩大范围或再次调用时，先说明可能产生额外积分并让用户决定。

## 工具选择指南

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “这个关键词的市场机会怎么样”“给我完整选品/商业洞察报告” | `linkfox-amazon-opportunity-report-by-keyword` | 只要搜索排名和点击/转化份额时换 ABA；想按条件发现多个赛道时换指标反向选品 |
| “过去几周关键词热度如何”“找上升词、季节词、蓝海词”“导出搜索词数据” | `linkfox-aba-intelligent-query` | 需要六维市场叙事报告时换关键词报告；需要跨赛道按价格/竞争/人群条件筛选时换指标反向选品 |
| “找低竞争/高增长/痛点/中档价格机会”“按人群或评论指标找赛道” | `linkfox-amazon-opportunity-search-by-metrics` | 已经确定一个关键词并要完整市场解释时换关键词报告；要搜索词周趋势或 ASIN 点击转化明细时换 ABA |
| “最近亚马逊有什么政策变化”“查美国站近一周政策公告” | `linkfox-amazon-policy-feed` 的 `policyFeed` operation | 已经有列表记录 `id` 并要全文时直接用 `policyFeedDetail`；若要商品、关键词或销售数据，换商业数据路径 |
| “查看这条政策的全文”并提供了列表中的 32 位 `id` | `linkfox-amazon-policy-feed` 的 `policyFeedDetail` operation | 没有有效 `id` 或 ID 无效时先调用 `policyFeed`，不能猜测详情 ID |
| 同时需要市场机会和政策核验 | 先执行用户明确优先的一个路径，再展示结果并说明下一次调用的目的与积分成本 | 用户只要一类结果时不要并行调用其他路径；需要搜索词数据、赛道指标和完整报告时按目标逐层选择 |

选择时先判断用户拥有的是“关键词/搜索行为”“筛选标准”还是“政策时间或记录 ID”，再用满足目标的最小参数集合。报告与指标筛选的结果粒度、ABA 的周粒度以及政策列表/详情的串联关系不同；在多个路径都可用时，向用户推荐默认项并让用户决定是否继续扩大查询。

## 业务需求路由速查

| 子能力 | 业务能力 | reference | 精确 `toolName` | 本地脚本 |
|---|---|---|---|---|
| `linkfox-aba-intelligent-query` | ABA 搜索词智能查询、趋势与点击/转化份额分析 | `references/linkfox-aba-intelligent-query.md` | `aba/intelligentQuery` | 无 |
| `linkfox-amazon-opportunity-report-by-keyword` | 单关键词六维市场机会报告 | `references/linkfox-amazon-opportunity-report-by-keyword.md` | `amazon/opportunity/reportByKeyword` | 无 |
| `linkfox-amazon-opportunity-search-by-metrics` | 按商业指标反向筛选关键词/赛道 | `references/linkfox-amazon-opportunity-search-by-metrics.md` | `amazon/opportunity/searchByMetrics` | 无 |
| `linkfox-amazon-policy-feed` | 政策法规资讯列表、站点/时间筛选与分页 | `references/linkfox-amazon-policy-feed.md` | `amazon/policyFeed` | 无 |
| `linkfox-amazon-policy-feed` | 单条政策资讯全文 | `references/linkfox-amazon-policy-feed.md` | `amazon/policyFeedDetail` | 无 |

公共认证引导见 `references/onboarding.md`。

## MCP 调用方式

- **MCP server**：`LinkFox`
- **URL**：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- **唯一工具**：`proxy_call`
- **调用结构**：`{"toolName":"<allowlist 中的精确值>","arguments":{...}}`。`arguments` 直接使用 reference 定义的请求参数对象，不增加 `body`、`params`、`data` 或另一层 `arguments`。
- **allowlist**：`aba/intelligentQuery`、`amazon/opportunity/reportByKeyword`、`amazon/opportunity/searchByMetrics`、`amazon/policyFeed`、`amazon/policyFeedDetail`。精确匹配并区分大小写，不得使用展示名或改写命名。
- **认证**：WorkBuddy 自动注入 Authorization。MCP 配置、文档和 `arguments` 不得加入 headers、API Key、token、JWT、手机号或其他凭证。
- **禁止直连**：不得使用 curl、`urllib`、`requests`、`httpx` 或其他方式直连工具网关；MCP 或 `proxy_call` 缺失时停止，不得 HTTP fallback。
- **响应处理**：先检查 MCP 连接、schema 和 `isError`，再读取 text/structured content；text 为 JSON 字符串时只解析一次，最后检查下游 `errcode`、`errorCode`、`code`、`errmsg` 或 `msg`。
- **调用去重**：收费调用失败、空结果或返回不理想时不得自动重试；同一任务内相同 `toolName + arguments` 不得重复调用。新链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要，保留参数摘要、结果标识和积分字段用于追溯。
- **读数据建议**：报告接口优先展示 `stdout` Markdown；ABA 查看 `tables`/`downloadUrl`；指标筛选查看 `data` 与过滤条件；政策列表查看 `data[].id` 后再读取详情。不要把大 JSON 全量复制进上下文。
- **参数完整位置**：ABA 的 `analysisDescription`、`region`、`createDownloadUrl` 及 15 个站点见其 reference；关键词报告必须提供 `site=US` 与 `keyword`；指标筛选的完整市场、竞争、价格、人群、产品和评论字段见其 reference，至少提供 `keyword`/`nicheName`/一个指标且 `limit` 为 1-200；政策列表的 `site`、时间、`page`、`pageSize` 与详情的 `id` 见其 reference。
- **调用顺序**：政策全文必须先列表后详情；指标筛选先以 2-4 个强条件小范围检索，空结果时只放宽最激进条件；ABA 查询要在自然语言描述中写清站点、时间、数值边界、比较基准和去重方式；关键词报告不把其他站点伪装成 US。

## 使用示例

以下示例只展示关键参数。每次真实调用都会返回 `costToken` 或等价的消耗字段；需要追加查询、放大 `limit`、翻页、生成下载或读取详情时，先向用户说明可能产生额外消耗并由用户决定。

### 1. ABA 搜索词趋势与下载

```json
{
  "analysisDescription": "筛选美国站，关键词包含 charger，过去12周搜索频率排名和点击/转化份额；相同搜索词相同ASIN保留最新记录",
  "region": "US",
  "createDownloadUrl": true
}
```

以 `toolName=aba/intelligentQuery` 调用 `proxy_call`。重点出参是 `tables`、`total`、`downloadUrl`、`downloadNote`、`costToken`；排名值越小代表热度越高。只在用户明确要求导出时将 `createDownloadUrl` 设为 `true`，下载链接最多包含 10,000 条记录，数据仍是周粒度。

### 2. 单关键词六维市场机会报告

```json
{
  "site": "US",
  "keyword": "hair mousse travel size"
}
```

以 `toolName=amazon/opportunity/reportByKeyword` 调用 `proxy_call`。成功时读取 `stdout` Markdown，关注市场潜力、产品特征、用户评论、客户画像、搜索趋势和定价分析，并同时呈现 `costTime`/`costToken`。当前仅支持 `site=US`；报告是快照和非结构化文本，不适合直接送入结构化聚合流程。

### 3. 按指标反向筛选赛道

```json
{
  "nicheBrandCountLte": 20,
  "nicheSearchVolumeYoyChangePctAtLeastGte": 100,
  "featureNewAvgReviewCountAtLeastLte": 500,
  "limit": 25,
  "amazonDomain": "US"
}
```

以 `toolName=amazon/opportunity/searchByMetrics` 调用 `proxy_call`。重点出参是 `data` 中的关键词/赛道、市场规模、峰值搜索量、同比变化、品牌数、价格档位、人群、特征和评论标签，以及 `code`、`msg`、`costToken`。这是历史赛道指标池筛选，不是 ASIN 搜索；至少一个关键词、赛道名或指标过滤字段必须存在，最多用 `limit=200` 扩大结果。

### 4. 按评论痛点与价格档位找机会

```json
{
  "reviewNegativeTop1Topic": "size",
  "reviewNegativeTop1PctAtLeastGte": 70,
  "priceMidClickSharePctAtLeastLte": 5,
  "priceEntryClickSharePctAtLeastGte": 70,
  "limit": 25
}
```

同样以 `toolName=amazon/opportunity/searchByMetrics` 调用 `proxy_call`。展示时回显实际过滤条件，并将空或少量结果解释为当前条件下未找到足够记录；如需放宽条件，先提示新调用会产生额外消耗。标签筛选值使用 API 规定的 snake_case 片段，枚举值不能自行翻译或改写。

### 5. 查询政策列表并读取全文

列表请求：

```json
{
  "site": "US",
  "publishedAtGte": "2026-08-01 00:00:00",
  "publishedAtLte": "2026-08-28 23:59:59",
  "page": 1,
  "pageSize": 20
}
```

以 `toolName=amazon/policyFeed` 调用 `proxy_call`，从返回 `data[].id` 选择记录后再请求详情：

```json
{
  "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
}
```

以 `toolName=amazon/policyFeedDetail` 调用 `proxy_call`。列表关注 `title`、`summaryZh`、`publishedAt`、`originalUrl` 和 `id`；详情原样呈现 `stdout` Markdown，并附标题和摘要。列表默认近 7 天、`pageSize` 最大 100，详情 ID 必须来自列表；Amazon 原文链接是权威来源。

## 展示规则

1. **先说明范围**：在结果开头标注所用子能力、端点、站点、时间范围或筛选条件，并说明 ABA 周粒度、报告/指标快照或政策资讯延迟等适用限制。
2. **客观呈现**：ABA 与指标结果使用清晰表格展示；关键词报告原样呈现 `stdout` Markdown；政策列表展示标题、`summaryZh`、发布时间和原文链接，详情原样渲染 `stdout`。不额外加入未经数据支持的商业建议、政策预测或法律结论。
3. **解释关键字段**：展示 ABA 排名时明确“数值越小，搜索热度越高”；展示指标筛选时回显活动过滤器、结果粒度和采集快照；展示报告时说明六维内容是生成时点参考。
4. **处理大结果**：优先展示核心字段和最多 3 条代表性记录；ABA 响应包含 `downloadUrl` 时给出下载地址，用户明确要求下载时才生成该链接。新 MCP 链路不承诺本地落盘。
5. **标注来源与链接**：标明数据来自 ABA 搜索词、关键词市场报告、指标池或 Amazon 政策资讯；政策 `originalUrl` 使用可点击链接，详情内容与原文存在差异时以 Amazon 原文为准。
6. **处理不可用字段**：空值、缺失值以及接口明确表示不可用的字段标记为 N/A 或省略，不把缺失字段推断成零，不把赛道级指标写成 ASIN 级事实。
7. **处理错误**：依据响应中的 `errcode`/`errorCode`/`code`、`errmsg`/`msg` 和 HTTP 状态说明原因并给出具体修正建议：参数全空或范围/枚举非法则调整参数，详情 ID 无效则重新查列表，401/402 则进入认证与积分引导，403 说明无权限并停止重试。
8. **避免无依据扩展**：失败或空结果不自动换词、改站点、翻页、放宽过滤或重复请求；若用户选择继续，明确新的参数和预期输出后再调用。

## 解决认证和积分问题

发生异常时读取 `references/onboarding.md`，并分层判断 MCP 连接、代理层与下游业务响应。WorkBuddy 自动注入 Authorization，不得要求用户手工填写凭证或将凭证放入 `arguments`。

- MCP 或 `proxy_call` 缺失：停止业务调用，提供 MCP 配置并提示重启或重载 WorkBuddy；Skill 不能自行安装或热加载 MCP。
- MCP 连接 401：提示重新登录、重载连接，仍失败则联系 WorkBuddy 管理员。
- 代理成功但下游 JSON 为 401：报告自动授权或下游业务认证失败，不得索取 Key。
- 下游 JSON 为 402 或积分不足：引导访问 `https://agent.linkfox.com/`，不得自动选套餐、下单、支付或轮询。
- 403 与其他错误：按业务 reference 原样处理，不得错误归类为 401/402，也不得自动重试。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
