---
name: linkfox-wb-jiimore
display_name: LinkFox 亚马逊极目市场洞察
display_name_en: LinkFox Amazon Jiimore Market Intelligence
description: 面向亚马逊选品与市场研究的极目市场洞察能力，支持关键词、ASIN 和细分市场 ID 的市场分析、商品发掘、竞品挖掘与评论洞察。
description_zh: 面向亚马逊选品、竞品研究和市场评估的统一极目洞察能力。支持按关键词发现细分市场和商品、按 ASIN 分析所属市场与同细分竞品、按 nicheId 查询市场级深度指标，以及提取细分市场正负面评论主题。覆盖 US、JP、DE 站点，提供可分页筛选的需求、销量、搜索、转化、价格、品牌集中度、广告、新品、退货、毛利、评论和趋势数据；当用户需要上述市场情报、潜力商品、竞品列表、消费者痛点或市场机会判断时触发。
description_en: Unified Jiimore intelligence for Amazon product research, market evaluation, and competitor discovery. It supports keyword-based niche and product discovery, ASIN-based niche analysis and same-niche competitor mining, nicheId-level market deep dives, and positive/negative review-topic insights across the US, JP, and DE marketplaces. Use it when the user needs demand, sales, search, conversion, pricing, brand concentration, advertising, launches, returns, margin, review, or trend data for Amazon market decisions.
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


# LinkFox 亚马逊极目市场洞察（LinkFox Amazon Jiimore Market Intelligence）

面向亚马逊选品、竞品研究和市场评估，按用户提供的关键词、ASIN 或细分市场 ID 返回可核验的市场数据与结构化洞察。可用于发现高需求细分市场和潜力商品、分析某个商品所在的市场、挖掘同细分竞品、查看市场级消费者正负面主题，以及对指定 niche 做价格、竞争、广告、库存、新品和盈利指标的深度查看。当前覆盖 6 个子能力和 6 个只读 API operation，业务调用统一由 LinkFox MCP 完成。

## 能力边界

### 能力范围

- **关键词细分市场发现**：使用子能力 `linkfox-jiimore-get-niche-info-by-keyword` 调用 `POST /jiimore/getNicheInfoByKeyword`，按关键词返回多个 niche 的需求得分、搜索量、销量、转化、价格、品牌集中度、广告、新品、退货和 CPC 指标；适合从一个词探索市场空间。
- **ASIN 细分市场分析**：使用子能力 `linkfox-jiimore-get-niche-info-by-asin` 调用 `POST /jiimore/getNicheInfoByAsin`，根据一个 ASIN 返回其关联的 niche 及市场指标；适合已知商品后反查所属市场，固定数量返回，不提供分页和排序。
- **指定市场深度洞察**：使用子能力 `linkfox-jiimore-get-niche-info` 调用 `POST /jiimore/getNicheInfo`，根据单个 `nicheId` 返回市场概览、当前/90 天前/360 天前对比、价格、搜索转化、商品与品牌集中度、新品、缺货、评论、卖家成熟度、广告和盈利数据。
- **细分市场评论洞察**：使用子能力 `linkfox-jiimore-get-niche-review-from-keyword` 调用 `POST /jiimore/getNicheReviewFromKeyword`，按关键词返回正面/负面评论主题、提及比例和评论样例；适合提炼用户认可点和产品痛点。
- **关键词商品发掘**：使用子能力 `linkfox-jiimore-product-discovery` 调用 `POST /jiimore/productDiscovery`，按关键词筛选商品 ASIN、标题、价格、评分/评论、点击、转化、毛利、FBA 费用、上架时间、类目和主图；适合事实型商品机会扫描。
- **ASIN 同细分竞品挖掘**：使用子能力 `linkfox-jiimore-page-asins-by-asin` 调用 `POST /jiimore/pageAsinsByAsin`，围绕参考 ASIN 获取同 niche 商品并按点击、转化、销量、评论、评分、价格、FBA、毛利、上架时间和卖家国家筛选；适合竞品列表与 90 天趋势查看。
- **站点范围**：上述市场、商品和评论数据支持 `US`、`JP`、`DE`，未指定时默认 `US`；跨站点查询必须分别指定 `countryCode`。
- **数据处理**：API 中比例、份额、转化率、增长率、ACOS、退货率、缺货率等字段通常为 0-1 小数，展示时转换为百分比；完整请求参数、响应字段和错误码按路由表读取对应 reference。

### 边界与限制

- 不支持除 `US`、`JP`、`DE` 之外的站点；不把站点名称或语言猜测成另一个国家，关键词应使用目标站点语言（US 英文、JP 日文、DE 德文）。
- 关键词市场发现、商品发掘和评论洞察必须提供 `keyword`；ASIN 市场分析与竞品挖掘必须提供 `asin`；指定市场深度洞察必须提供单个 `nicheId`。不能用商品标题替代 ASIN，也不能用关键词替代 niche ID。
- `getNicheInfoByAsin` 只按 `count` 返回关联 niche，不支持分页/排序；`getNicheInfo` 一次只查一个 niche；商品与竞品列表的 `pageSize` 最大为 100。
- 所有比例筛选值按 API 约定传 0-1，不得把用户说的 10% 直接传成 `10`；上架日期筛选必须使用 `yyyyMMdd000000`。
- 本能力不提供单个 ASIN 的 Listing 全量详情或原始评论，不提供 ABA 搜索词数据、广告投放/竞价管理、店铺运营、库存执行、供应商采购、物流规划、注册申请、法律意见或完整利润策略。
- 结果是数据服务返回的市场指标和评论聚合，不替代侵权/FTO、财务、法律或平台合规结论；缺失字段必须标明“接口未返回”，不得自行补算为事实。
- 同一会话同一参数组合默认只调用一次；失败、空结果或过滤过严时不得自动换词、换 ASIN、换站点、连续翻页或放宽条件试探。若用户要继续查询，先说明会产生额外积分消耗并由用户决定。

## 工具选择指南

当需求同时涉及“市场”“商品”“竞品”或“评论”时，先判断用户的定位锚点和输出对象，再按下表选择。默认推荐只表示最贴合当前问题的子能力，不能替用户擅自发起多个收费查询。

| 需求 / 用户说 | 默认推荐 | 何时换用其他 |
|---|---|---|
| “这个关键词有哪些细分市场”“评估关键词的需求、垄断、品牌集中度” | `linkfox-jiimore-get-niche-info-by-keyword` | 已有 ASIN 要反查所属市场时换 `linkfox-jiimore-get-niche-info-by-asin`；已有 `nicheId` 要全量指标时换 `linkfox-jiimore-get-niche-info` |
| “这个 ASIN 属于哪些 niche”“分析这个商品所在市场” | `linkfox-jiimore-get-niche-info-by-asin` | 要同 niche 商品列表换 `linkfox-jiimore-page-asins-by-asin`；要单一 niche 的历史对比与评论洞察时先取 `nicheId` 再用 `linkfox-jiimore-get-niche-info` |
| “查这个 nicheId 的完整市场数据”“看价格/缺货/品牌/新品趋势” | `linkfox-jiimore-get-niche-info` | 不知道 `nicheId` 时先用关键词或 ASIN 市场发现；想看商品行列表换商品发掘或竞品挖掘 |
| “客户喜欢什么”“这个品类的差评痛点”“评论主题/情感” | `linkfox-jiimore-get-niche-review-from-keyword` | 明确要求单个 ASIN 原始评论时本能力不适用；只看市场销量、价格或需求而不看评论时换市场数据能力 |
| “按关键词找潜力商品/爆品”“筛高转化、高增长、高毛利商品” | `linkfox-jiimore-product-discovery` | 要 niche 级竞争格局而不是商品行时换关键词细分市场发现；已有参考 ASIN 的同类商品时换 ASIN 竞品挖掘 |
| “找这个 ASIN 的同类竞品”“按转化、评论、毛利筛竞品” | `linkfox-jiimore-page-asins-by-asin` | 只想知道 ASIN 所属 niche 时换 ASIN 细分市场分析；没有参考 ASIN、从关键词找商品时换商品发掘 |
| “看高需求且低集中度市场” | `linkfox-jiimore-get-niche-info-by-keyword` | 若用户要在某个已知商品所在市场中比较，先换 ASIN 细分市场分析；若已知 niche ID，直接深度洞察 |
| “看市场机会并理解用户痛点” | 先让用户选择市场发现或评论洞察的优先方向 | 市场规模/竞争指标用关键词细分市场发现；体验与投诉主题用评论洞察；不要未经决定自动调用两次 |

### 选择思路

- 以 **关键词** 为入口：需要市场段指标选 `getNicheInfoByKeyword`，需要商品行选 `productDiscovery`，需要消费者主题选 `getNicheReviewFromKeyword`。
- 以 **ASIN** 为入口：需要所属 niche 选 `getNicheInfoByAsin`，需要同 niche 竞品列表选 `pageAsinsByAsin`。
- 以 **nicheId** 为入口：选 `getNicheInfo` 做深度市场画像；一次只传一个 ID，比较多个 ID 时必须逐次调用并提前说明费用。
- 只在用户明确需要更深层的第二类数据时继续调用；先使用已返回的 `nicheId`、ASIN、分页和趋势字段，避免重复查询。

## 业务需求路由速查

| 子能力 | reference | 精确 `toolName` | 风险 |
|---|---|---|---|
| 关键词细分市场发现 | `references/linkfox-jiimore-get-niche-info-by-keyword.md` | `jiimore/getNicheInfoByKeyword` | 收费只读 |
| ASIN 细分市场分析 | `references/linkfox-jiimore-get-niche-info-by-asin.md` | `jiimore/getNicheInfoByAsin` | 收费只读 |
| 指定 niche 深度洞察 | `references/linkfox-jiimore-get-niche-info.md` | `jiimore/getNicheInfo` | 收费只读 |
| 关键词评论洞察 | `references/linkfox-jiimore-get-niche-review-from-keyword.md` | `jiimore/getNicheReviewFromKeyword` | 收费只读 |
| 关键词商品发掘 | `references/linkfox-jiimore-product-discovery.md` | `jiimore/productDiscovery` | 收费只读 |
| ASIN 同细分竞品 | `references/linkfox-jiimore-page-asins-by-asin.md` | `jiimore/pageAsinsByAsin` | 收费只读 |

无本地辅助脚本；所有工具网关业务调用只使用 MCP。

## 调用方式

- MCP server：`LinkFox`
- URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- allowlist：`jiimore/getNicheInfoByKeyword`、`jiimore/getNicheInfoByAsin`、`jiimore/getNicheInfo`、`jiimore/getNicheReviewFromKeyword`、`jiimore/productDiscovery`、`jiimore/pageAsinsByAsin`。
- 调用结构：`{"toolName":"<精确 endpoint>","arguments":{<原请求参数>}}`。`toolName` 区分大小写，`arguments` 不加额外包装。
- WorkBuddy 自动注入 Authorization；配置和参数不得加入 headers、API Key、token、JWT、手机号或其他凭证。
- 禁止 curl、`urllib`、`requests`、`httpx` 等直连工具网关；MCP 或 `proxy_call` 缺失时停止，不得 HTTP fallback。
- 新链路不提供旧脚本的 24 小时缓存、自动落盘或 stdout 摘要。以当前任务内 `toolName + arguments` 去重，并保留查询参数摘要和必要结果 ID 追溯。
- 先检查 MCP/schema/`isError`，再读取代理内容；text JSON 只解析一次；最后检查下游业务错误字段。
- 完整参数、响应、错误和示例只从路由表对应 reference 读取。

## 使用示例

以下示例均为下游业务参数对象；放入对应 `proxy_call.arguments`。每次真正发起查询前都要告知用户可能产生积分消耗，并遵守去重、分页和失败不自动试探规则。

### 1. 按关键词发现细分市场

```json
{
  "keyword": "wireless earbuds",
  "countryCode": "US",
  "top5BrandsClickShareMax": 0.5,
  "brandCountMin": 20,
  "sortField": "demand",
  "sortType": "desc",
  "page": 1,
  "pageSize": 20
}
```

调用 `/jiimore/getNicheInfoByKeyword`。重点读取 `data[].nicheId`、`nicheTitle`/`translationZh`、`demand`、搜索量、销量、品牌份额和 `cpc`；比例按百分比展示。需要某一 niche 的历史和评论字段时，保留返回的 `nicheId` 再决定是否查询深度洞察。

### 2. 按 ASIN 反查所属细分市场

```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "count": 10,
  "top5BrandsClickShareMax": 0.5,
  "searchVolumeT7Min": 5000
}
```

调用 `/jiimore/getNicheInfoByAsin`。重点读取 `nicheInfoVoList` 中的 `nicheId`、标题、需求、搜索/销量、品牌集中度和 CPC。该接口没有分页/排序；`errcode=10000` 是无符合条件的 niche，应说明空结果并等待用户决定是否放宽筛选。

### 3. 查询指定 niche 的深度市场画像

```json
{
  "nicheId": "12345678",
  "countryCode": "US"
}
```

调用 `/jiimore/getNicheInfo`。按市场概览、价格/盈利、搜索转化、商品/品牌份额、新品上架、库存、评论、卖家成熟度、广告和趋势分组读取 `data[]`；并列展示当前、90 天前和 360 天前字段。一次只能查询一个 `nicheId`，比较多个 ID 前先提示将产生多次消耗。

### 4. 提取关键词对应的评论主题

```json
{
  "keyword": "yoga mat",
  "countryCode": "US",
  "searchVolumeT7Min": 5000,
  "top5BrandsClickShareMax": 0.5,
  "sortField": "demand",
  "sortType": "desc",
  "page": 1,
  "pageSize": 50
}
```

调用 `/jiimore/getNicheReviewFromKeyword`。读取 `data[]` 的 `nicheName`、`reviewType`、`topic`、`percentOfMentions` 和 `reviewExample`，将正面与负面分组；高提及负面主题可标成“痛点”，高提及正面主题可标成“认可点”，但不能延伸成未经请求的经营建议。

### 5. 按关键词筛选潜力商品

```json
{
  "keyword": "wireless charger",
  "countryCode": "US",
  "clickConversionRateMin": 0.1,
  "grossProfitMarginMin": 0.3,
  "totalReviewsMax": 100,
  "sortField": "clickConversionRate",
  "sortType": "desc",
  "page": 1,
  "pageSize": 20
}
```

调用 `/jiimore/productDiscovery`。读取 `products[]` 的 ASIN、标题、价格、评分/评论、主图、点击量、转化率、毛利、FBA 费用和上架日期；提示 API 接收的比例是小数，展示时换算为百分比。商品列表有分页，不因结果少而自动放宽条件。

### 6. 按参考 ASIN 挖掘同细分竞品

```json
{
  "asin": "B0GC4RPX79",
  "countryCode": "US",
  "clickConversionRateCompositeMin": 0.15,
  "clickCountT30Min": 2000,
  "totalReviewsMax": 100,
  "sortField": "clickConversionRateComposite",
  "sortType": "desc",
  "page": 1,
  "pageSize": 50
}
```

调用 `/jiimore/pageAsinsByAsin`。读取 `data[]` 的 ASIN、标题、价格、评分、评论、转化率、点击/销量、毛利、`niches` 和 `trends`；如 `total` 超过当前页，先报告当前页与总页数，再由用户决定是否翻页。`trends` 可做 90 天点击、价格和评论方向摘要，不能替代单品详情。

## 展示规则

1. **先说明查询口径**：展示所用子能力、端点对应的业务口径、站点、关键词/ASIN/nicheId、筛选条件和查询时间与数据口径；不把不同口径的市场段、商品列表和评论主题混成一张表。
2. **结构化呈现**：市场段结果优先展示 `nicheId`、原始标题、中文标题（若有）、需求得分、搜索量、销量、商品数、品牌数和 TOP5 份额；商品结果优先展示 ASIN、标题、价格、评分/评论、点击、转化、毛利和主图链接。
3. **评论分组**：评论结果必须清楚区分正面与负面，展示主题、提及比例和样例；不得把细分市场评论聚合写成某个单独 ASIN 的原始评论。
4. **深度市场分组**：指定 niche 结果按概览、价格/盈利、搜索需求、竞争集中度、新品、库存、评论、卖家成熟度、广告和盈利展示；当前、90 天前、360 天前数据尽可能并列。
5. **百分比格式**：API 返回的 0-1 比例/份额/转化/增长/ACOS/退货/缺货字段，用户界面显示为百分比并保留原始字段含义；请求示例或参数说明明确提醒 API 仍接收 0-1。
6. **站点与语言**：显示 `countryCode`；关键词必须符合目标站点语言。若用户关键词语言与站点不匹配，先提示需翻译或让用户确认，不擅自把翻译后的词当作用户原词记录。
7. **分页与数量**：当 `total`、`pages` 或当前页小于总数时，标出当前页、页大小和总量，并建议是否继续；`getNicheInfoByAsin` 的 `count` 是返回数量，不要误称为分页。
8. **趋势与图片**：有 `trends` 时摘要说明 90 天指标的上升、下降或稳定方向；有 `referenceAsinImageUrl`、`imageUrl` 或 `imagesUrl` 时展示或提供链接，并注明这是接口返回的图片字段。
9. **错误处理**：按响应中的 `errcode`/`errorCode`、HTTP 状态和 `errmsg` 原样解释；`401` 按认证引导，`402` 按余额/积分引导，ASIN 市场接口 `10000` 按无匹配结果处理，其他错误给出与参数相关的修正建议。
10. **缺失与不确定性**：接口未返回的字段显示“未返回”，不以 0、空字符串或估算值替代；区分当前值、历史快照、样例和趋势推断，不把数据指标包装成保证性结论。
11. **客观表达**：默认只呈现数据和直接可见的趋势/主题，不输出未经请求的主观选品结论、法律意见、利润承诺或广告建议；用户明确要求解释时，仍需基于实际字段并注明推断边界。

## 解决认证和积分问题

读取 `references/onboarding.md`。MCP 连接 401、代理成功后的下游 401、下游 402、403 必须分层处理；不得要求用户配置 MCP Authorization 或把凭证放进 `arguments`。

## 积分消耗说明

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。
