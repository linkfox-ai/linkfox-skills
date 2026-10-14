---
name: linkfox-sif-asin-keywords
description: 使用SIF数据反查任意亚马逊ASIN的流量关键词，包括自然排名、广告排名、搜索量、流量占比、自然/付费得分、ABA TOP3点击集中度、点击转化率、搜索量同比涨跌及周/月时间窗。当用户提到ASIN关键词分析、ASIN反查、流量关键词研究、自然排名查询、广告排名查询、关键词位置追踪、SIF关键词数据、竞品关键词窥探、查看哪些关键词为产品带来流量、分析特定ASIN的关键词表现、按周/月/最近N天的关键词时间窗、ASIN reverse keyword lookup, traffic keywords, organic ranking, ad ranking, search volume, SIF keywords, competitor keyword reverse lookup, click concentration, click-to-purchase conversion, week-over-week search volume时触发此技能。即使用户未明确提及"SIF"，只要其需求涉及查找与特定亚马逊商品（ASIN）关联的关键词，也应触发此技能。
---

# SIF ASIN Keyword Analysis

## 能力边界

### 能力范围

- 针对单个 Amazon ASIN 反查带来流量的关键词，返回自然排名、SP 广告排名、搜索量、流量份额、曝光得分、点击集中度和点击购买转化率。
- 支持 13 个 Amazon 站点、关键词文本筛选、自然/广告/转化/新进等条件筛选、最近 7/30 天、指定月或指定周，以及排序和分页。

### 不适用范围

- 一次请求不能查询多个 ASIN；多 ASIN 比较必须分别调用。
- 不提供与具体 ASIN 无关的广泛关键词研究、销售/收入估算、评论或 Listing 文案、广告竞价/预算管理及长期历史趋势曲线。

This skill guides you on how to query and analyze traffic keywords for a specific Amazon ASIN, helping Amazon sellers understand which keywords drive traffic to a product and how that product ranks for each keyword.

## Core Concepts

SIF ASIN Keyword data reveals the keywords that bring traffic to a specific Amazon product (ASIN). For each keyword, you can see the product's organic search rank, SP ad rank, search volume, traffic share, display position types, and various performance markers. This is the go-to tool for reverse ASIN keyword lookup.

**Single-ASIN limitation**: This tool queries one ASIN at a time. If the user wants to compare multiple ASINs, you must make separate queries for each.

**Ranking logic**: A smaller rank value means a better (higher) position. Rank 1 means the product appears first in search results. When a user says "ranking improved", the numeric value decreased; "ranking dropped" means the value increased.

## Data Fields

### Per-keyword record (each element of `data`)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Keyword | keyword | The search keyword driving traffic | wireless charger |
| Keyword Translation | translateKeyword | Localized keyword translation for the marketplace | 无线充电器 |
| ASIN | asin | The product ASIN being queried | B0XXXXXXXX |
| Organic Rank | productNaturalRank | Product's position in organic search results | 5 |
| Organic Rank (Display) | naturalRankDisplay | Organic rank as display text | 5 |
| Ad Rank | productAdRank | Product's position in SP ad results | 3 |
| Ad Rank (Display) | adRankDisplay | Ad rank as display text | 3 |
| Weekly Search Volume | weeklySearchVolume | Estimated weekly searches for this keyword | 125000 |
| Keyword Popularity Rank | keywordPopularityRank | Keyword's search volume rank among all keywords (lower = more popular) | 203 |
| Total Search Result Products | totalSearchResultProductCount | Total products shown under this keyword (organic + ads + recommendations) | 1280 |
| Traffic Share | trafficShare | Share of traffic this keyword contributes to the ASIN (1 = 100%) | 0.05 |
| Natural Traffic Share | naturalTrafficShare | Organic exposure score / total score | 0.62 |
| Paid Traffic Share | paidTrafficShare | Paid-ad exposure score / total score (SP + SB + SBV + recAd) | 0.31 |
| Natural Traffic Score | naturalTrafficScore | Organic search exposure score for this ASIN on this keyword (0 = none) | 4.2 |
| SP Ads Score | sponsoredProductsScore | Sponsored Products regular-slot score (excludes SP recommendation slots) | 2.1 |
| Brand Ad (SB) Score | brandAdScore | Sponsored Brands total score (standard + video) | 0.8 |
| Video Ad (SBV) Score | videoAdScore | Sponsored Brands Video score | 0.3 |
| SP Recommendation Score | sponsoredRecommendationScore | Combined score across SP recommendation slots (Trending now, Seen on social media, Customers frequently viewed, 4 stars and above, etc.) | 1.4 |
| SP Recommendation Breakdown | sponsoredRecommendationBreakdown | Array of `{title, score, scoreRatio}` per SP recommendation slot | [{"title":"Trending now","score":0.8,"scoreRatio":0.57}] |
| ABA TOP3 Click Concentration | clickConcentrationShare | Whether clicks under this keyword concentrate on the top ASINs (NOT a conversion rate) | 0.42 |
| Click-to-Purchase Conversion | clickToPurchaseConversionRate | `purchaseQty / clickQty` at the keyword level | 0.037 |
| Display Position Types | displayPositionTypes | Where the product appears: natural, ac, sp, top, bottom, er, vedio, tr, trfob | ["natural", "sp"] |
| Traffic Characteristic Markers | trafficCharacteristicMarkers | Traffic feature tags: isMainKw, isAccurateKw, isAccurateAboveKw, isAccurateTailKw | ["isMainKw"] |
| Conversion Performance Markers | conversionPerformanceMarkers | Conversion tags: isPurchaseKw, isQualityKw, isStableKw, isLossKw, isInvalidKw | ["isPurchaseKw"] |
| Last Organic Rank Time | lastNaturalRankTime | When the product last had a valid organic rank for this keyword | 2026-04-20 |
| Last Ad Rank Time | lastAdRankTime | When the product last had a valid SP ad rank for this keyword | 2026-04-20 |
| Period End Date | periodEndDate | End date of the current (weekly) period = start-week + 7 days | 2026-04-27 |
| Update Time | updateTime | When the keyword data was last updated | 2026-04-21 |

### Top-level response fields (alongside `data`)

| Field | API Name | Description |
|-------|----------|-------------|
| Is Parent ASIN | isParentAsin | Whether the queried ASIN is a parent (variation hub) |
| Has Variants | hasVaiants | Whether the ASIN has variants |
| Latest ABA Week | abaCreateDateWeek | Latest ABA weekly data reference date |

## Supported Marketplaces

13 marketplaces: US (United States), UK (United Kingdom), DE (Germany), CA (Canada), JP (Japan), FR (France), ES (Spain), IT (Italy), MX (Mexico), AU (Australia), AE (United Arab Emirates), BR (Brazil), SA (Saudi Arabia).

Default marketplace is **US**. Use US when the user does not specify a marketplace. Codes outside this list will be rejected by the API pattern.

## MCP 调用方式

- **MCP Server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **精确 toolName**：`sif/asinKeywords`
- **响应字段来源**：`skills/linkfox-sif-asin-keywords/references/api.md`；只从该文件的响应章节核对字段。
- **arguments**：直接使用本 reference 的请求参数对象，不包裹 `body`、`params` 或 `data`。
- **自动授权**：WorkBuddy 自动注入授权上下文；禁止传 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- **响应处理**：text JSON 只解析一次；先处理 MCP/代理错误，再处理下游 `code`/`errcode` 与消息字段。
- **成本纪律**：相同 `toolName + arguments` 默认只调用一次；失败或空结果不得自动换关键词、站点、翻页或筛选条件。继续查询前先告知额外消耗并取得同意。
- **本地能力变化**：旧脚本的 24 小时缓存、自动落盘、会话索引和 stdout 摘要不属于 MCP 能力，迁移后不再承诺。

```json
{"toolName":"sif/asinKeywords","arguments":{"asin":"B0XXXXXXXX","country":"US"}}
```

## 解决认证和积分问题
发生以下异常情况时，采用 onboarding.md 引导解决问题：

### 异常情况
- **MCP 不可用**：检查 `LinkFox` 配置并刷新会话，禁止回退旧 HTTP 网关。
- **401**：WorkBuddy 自动授权上下文异常；不在参数中补传凭证。
- **402 / 积分不足**：引导用户访问 `https://agent.linkfox.com/` 自助处理，不自动下单或支付。
- **403**：权限问题，与 401/402 分开处理。

## Parameter Guide

### Required Parameter

- **asin** (string, required): The Amazon ASIN to look up. Only one ASIN per request.

### Optional Parameters

- **country** (string, default `US`): Marketplace code. See Supported Marketplaces above.
- **keyword** (string): Filter results to keywords containing this text. Translate the keyword into the language of the target marketplace when possible.
- **timePieceType** (string, default `latelyDay`): Time window type — `latelyDay` (most recent N days), `month` (specific month), `week` (specific week).
- **timePieceValue** (string, default `7`): Value paired with `timePieceType`.
  - When `timePieceType=latelyDay` → only `7` or `30` are supported
  - When `timePieceType=month` → `YYYY-MM` (e.g. `2026-04`)
  - When `timePieceType=week` → the week's start date `YYYY-MM-DD` (e.g. `2026-04-13`)
- **conditions** (string): Comma-separated condition filters. Flag-style filters:
  - `nfPosition` -- organic traffic keywords
  - `isSpAd` -- SP ad keywords
  - `isBrandAd` -- brand ad keywords
  - `isVedioAd` -- video ad keywords
  - `isAC` -- Amazon's Choice keywords
  - `isAccurateKw` -- precise traffic keywords
  - `isAccurateTailKw` -- precise long-tail keywords
  - `isPurchaseKw` -- purchase-converting keywords
  - `isQualityKw` -- high-quality conversion keywords
  - `isStableKw` -- stable conversion keywords
  - `isLossKw` -- conversion-loss keywords
  - `isInvalidKw` -- invalid-exposure keywords
  - `isMultiVariantKw` -- keywords ranking organically across multiple variants
  - `isSearchVolUpKw` -- keywords whose search volume increased year-over-year
  - `isSearchVolDownKw` -- keywords whose search volume decreased year-over-year

  Period-count filters (all / new-in):
  - `totalPeriod.in` -- newly-entered traffic keywords this period
  - `nfKeywordCnt.total` / `nfKeywordCnt.in` -- keywords with (new) organic exposure
  - `adKeywordCnt.total` / `adKeywordCnt.in` -- keywords with (new) ad exposure
  - `allSpKeywordCnt.total` / `allSpKeywordCnt.in` -- (new) SP-ad keywords (regular + recommendation)
  - `spKeywordCnt.total` / `spKeywordCnt.in` -- (new) SP regular keywords
  - `recSpKeywordCnt.total` / `recSpKeywordCnt.in` -- (new) SP recommendation keywords
  - `allSbKeywordCnt.total` / `allSbKeywordCnt.in` -- (new) SB-ad keywords
  - `sbKeywordCnt.total` / `sbKeywordCnt.in` -- (new) SB regular keywords
  - `sbvKeywordCnt.total` / `sbvKeywordCnt.in` -- (new) SBV keywords
- **sortBy** (string): Sort field. Options: `lastRank` (organic rank), `adLastRank` (ad rank), `updateTime` (update time), `searchesRank` (search popularity rank), `estSearchesNum` (monthly search volume).
- **desc** (boolean, default `true`): Sort in descending order. Set to `false` for ascending.
- **pageNum** (integer, default `1`): Page number for pagination.
- **pageSize** (integer, default `100`, range 10-100): Number of results per page.

### Building Effective Queries

1. **Always specify the marketplace**: Set `country` to one of the 13 supported codes.
2. **Pick the right time window**: The default is the latest 7 days. Pass `timePieceType=month` + `timePieceValue=YYYY-MM` for a specific month, or `timePieceType=week` + `timePieceValue=YYYY-MM-DD` for a specific ABA week.
3. **Use keyword filtering**: When the user is interested in specific keywords, pass the `keyword` parameter to narrow results.
4. **Apply condition filters**: Use `conditions` to focus on specific keyword types (e.g., only organic keywords, only purchase-converting keywords, or newly-entered SP keywords via `spKeywordCnt.in`).
5. **Choose appropriate sorting**: Sort by `estSearchesNum` for highest search volume keywords, or by `lastRank` for best-ranking keywords.
6. **Handle pagination**: The API returns at most 100 results per page. Use `pageNum` to retrieve additional pages if the total exceeds 100.

## Usage Examples

**1. Find all traffic keywords for an ASIN on the US marketplace**
```
asin: "B0XXXXXXXX", country: "US"
```

**2. Find organic traffic keywords only**
```
asin: "B0XXXXXXXX", country: "US", conditions: "nfPosition"
```

**3. Find keywords containing "charger" sorted by search volume (ascending)**
```
asin: "B0XXXXXXXX", country: "US", keyword: "charger", sortBy: "estSearchesNum", desc: false
```

**4. Find high-converting keywords**
```
asin: "B0XXXXXXXX", country: "US", conditions: "isPurchaseKw,isQualityKw"
```

**5. Find SP ad keywords on the Japan marketplace**
```
asin: "B0XXXXXXXX", country: "JP", conditions: "isSpAd", sortBy: "adLastRank", desc: false
```

**6. Find precise long-tail keywords with stable conversion**
```
asin: "B0XXXXXXXX", country: "US", conditions: "isAccurateTailKw,isStableKw"
```

**7. Find newly-entered SP traffic keywords in April 2026**
```
asin: "B0XXXXXXXX", country: "US", timePieceType: "month", timePieceValue: "2026-04", conditions: "spKeywordCnt.in"
```

**8. Find keywords whose search volume is trending up**
```
asin: "B0XXXXXXXX", country: "US", conditions: "isSearchVolUpKw", sortBy: "estSearchesNum", desc: true
```

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice.
2. **Ranking clarification**: When showing ranking data, remind users that lower numeric values mean better (higher) positions.
3. **Share formatting**: Display `trafficShare`, `naturalTrafficShare`, `paidTrafficShare`, and `clickConcentrationShare` as percentages (multiply by 100). For example, 0.05 should be shown as 5%.
4. **Click concentration wording**: `clickConcentrationShare` measures how concentrated clicks are on top ASINs under the keyword — it is NOT a conversion rate. Label it clearly so users don't confuse it with `clickToPurchaseConversionRate`.
5. **Period disclosure**: When showing counts sourced from `*.in`/`*.total` filters or comparing numbers, annotate the period range — default is last 7 days; if `timePieceType=month` or `week` is set, surface the resolved period (`periodEndDate` / `abaCreateDateWeek`).
6. **Marker translation**: Translate marker arrays into human-readable labels. For example, `["isMainKw", "isAccurateKw"]` should display as "Main Traffic, Precise Traffic".
7. **Display position translation**: Translate position type arrays into readable labels: natural = Organic, ac = Amazon's Choice, sp = SP Ad, top = Top Brand Ad, bottom = Bottom Brand Ad, er = Editorial Recommendation, vedio = Video Ad, tr = Top Rated, trfob = Top Rated Frequently Bought.
8. **Pagination notice**: When results have more pages, inform the user of the total count and suggest fetching additional pages.
9. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query parameters.
10. **Multi-ASIN requests**: If the user asks about multiple ASINs, make separate API calls for each and present the results together.
## Important Limitations

- **Single ASIN per request**: Only one ASIN can be queried at a time.
- **Page size cap**: Maximum 100 results per page.
- **Time window granularity**: `timePieceType=latelyDay` only supports `timePieceValue=7` or `30`; arbitrary N-day windows are not supported.
- **Marketplace coverage**: 13 marketplaces only — IN / NL / SE / PL / TR / SG are no longer available.
- **Keyword language**: The `keyword` filter should ideally be in the language of the target marketplace.

## User Expression & Scenario Quick Reference

**Applicable** -- Keyword analysis for specific Amazon products:

| User Says | Scenario |
|-----------|----------|
| "What keywords does this ASIN rank for" | Reverse ASIN keyword lookup |
| "Show me the traffic keywords for B0XXX" | Traffic keyword analysis |
| "What's the organic rank for this product" | Organic ranking check |
| "Which keywords is this product advertising on" | Ad keyword analysis |
| "Find high-converting keywords for this ASIN" | Conversion keyword mining |
| "What are the main traffic sources for this product" | Main traffic keyword identification |
| "Show me keywords with lost conversions" | Conversion loss diagnosis |
| "Which keywords have Amazon's Choice badge" | AC keyword discovery |
| "Compare keyword rankings for my ASIN" | Keyword position analysis |
| "Which new SP keywords did this ASIN get last month" | New-in period keyword discovery (`spKeywordCnt.in` + month window) |
| "Keywords whose search volume is trending up YoY" | Search-volume trend filter (`isSearchVolUpKw`) |
| "Is click concentration high on this keyword" | ABA TOP3 click concentration read |
| "Keyword click-to-purchase conversion" | Per-keyword conversion check |

**Not applicable** -- Needs beyond single-ASIN keyword lookup:
- Broad keyword research not tied to a specific ASIN (use ABA data tools instead)
- Product reviews, listing copywriting
- Sales estimation, revenue analysis
- Advertising campaign management (bids, budgets)
- Category-wide keyword trends without a specific ASIN

## 积分消耗规则

消耗 9 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `linkfox-sif-asin-keywords.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*



---

# API 参考（完整归档）

# SIF-ASIN的关键词 API 参考

## MCP 调用规范

- **MCP Server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **精确 toolName**：`sif/asinKeywords`
- **arguments**：下方请求参数对象直接作为 `arguments`，不传认证字段，不额外包裹。
- **解析与失败**：text JSON 只解析一次；区分 MCP/代理错误与下游业务错误；禁止 HTTP fallback 和自动重复计费调用。

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | ASIN码，最大长度1000字符。本工具一次只能查询一个ASIN |
| country | string | 否 | 国家站点，默认 `US`。可选值（共 13 个）：`US`、`UK`、`DE`、`CA`、`JP`、`FR`、`ES`、`IT`、`MX`、`AU`、`AE`、`BR`、`SA` |
| keyword | string | 否 | 关键词，最大长度1000。尽量翻译成对应国家站点的语言 |
| timePieceType | string | 否 | 时间片段类型，默认 `latelyDay`。可选值：`latelyDay`（最近N天）、`month`（某月）、`week`（某周） |
| timePieceValue | string | 否 | 时间片段值，默认 `7`，最大长度1000。`latelyDay` 时仅支持 `7` 或 `30`；`month` 时为 `YYYY-MM`（如 `2026-04`）；`week` 时为周开始日期 `YYYY-MM-DD`（如 `2026-04-13`） |
| conditions | string | 否 | 条件筛选，多个以英文逗号隔开。可选值：<br>**标志类**：`nfPosition`（自然流量词）、`isSpAd`（SP广告词）、`isBrandAd`（品牌广告词）、`isVedioAd`（视频广告词）、`isAC`（AC推荐词）、`isAccurateKw`（精准流量词）、`isAccurateTailKw`（精准长尾词）、`isPurchaseKw`（出单词）、`isQualityKw`（转化优质词）、`isStableKw`（转化平稳词）、`isLossKw`（转化流失词）、`isInvalidKw`（无效曝光词）、`isMultiVariantKw`（多变体自然位词）、`isSearchVolUpKw`（搜索量同比增长词）、`isSearchVolDownKw`（搜索量同比下降词）<br>**周期计数类（`.total` 全量 / `.in` 新进）**：`totalPeriod.in`、`nfKeywordCnt.total`、`nfKeywordCnt.in`、`adKeywordCnt.total`、`adKeywordCnt.in`、`allSpKeywordCnt.total`、`allSpKeywordCnt.in`、`spKeywordCnt.total`、`spKeywordCnt.in`、`recSpKeywordCnt.total`、`recSpKeywordCnt.in`、`allSbKeywordCnt.total`、`allSbKeywordCnt.in`、`sbKeywordCnt.total`、`sbKeywordCnt.in`、`sbvKeywordCnt.total`、`sbvKeywordCnt.in` |
| sortBy | string | 否 | 排序字段。可选值：`lastRank`（自然排名）、`adLastRank`（广告排名）、`updateTime`（关键词抓取时间）、`searchesRank`（搜索排名）、`estSearchesNum`（月搜索量）。空字符串为默认系统排序 |
| desc | boolean | 否 | 是否降序，默认 `true` |
| pageNum | integer | 否 | 页码，默认 `1` |
| pageSize | integer | 否 | 每页数量，最小10，最大100，默认 `100` |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | SIF 业务返回码，`"1"` 表示成功 |
| msg | string | 消息 |
| total | integer | 本次实际返回的数据数量 |
| data | array | 返回数据数组（详见下方） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| title | string | 标题 |
| isParentAsin | boolean | 是否是父体（pasin） |
| hasVaiants | boolean | 是否有变体 |
| abaCreateDateWeek | string | 最新周 ABA 数据对应的周时间 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |

### data 数组元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| keyword | string | 关键词 |
| translateKeyword | string | 关键词翻译，站点本地化译文 |
| asin | string | 商品ASIN |
| productNaturalRank | integer | 商品自然搜索排名。该商品在此关键词下的自然搜索结果中的位置排名，如1表示排在搜索结果第1位（首位） |
| naturalRankDisplay | string | 自然排名显示文本。自然搜索排名的字符串表示形式 |
| productAdRank | integer | 商品SP广告排名。该商品在此关键词下的Sponsored Products广告位中的排名位置，如3表示排在广告位第3位 |
| adRankDisplay | string | 广告排名显示文本。SP广告排名的字符串表示形式 |
| weeklySearchVolume | integer | 周搜索量。该关键词在亚马逊平台每周的预估搜索次数 |
| keywordPopularityRank | integer | 关键词搜索热度排名。该关键词的月搜索量在亚马逊所有关键词中的排名，数值越小表示搜索量越大 |
| totalSearchResultProductCount | integer | 该关键词下搜索结果商品总数（在售产品数） |
| trafficShare | number | 流量占比。该关键词为商品带来的流量占所有关键词总流量的比例，其中1表示100% |
| naturalTrafficShare | number | 自然流量得分占比。自然搜索流量得分 / 总得分 |
| paidTrafficShare | number | 付费广告流量得分占比。广告流量得分 / 总得分；广告合计 = sp + sb + sbv + recAd |
| naturalTrafficScore | number | 自然流量得分。该关键词为该 ASIN 带来的自然搜索曝光得分，0 = 无自然流量曝光 |
| sponsoredProductsScore | number | SP 广告常规得分。Sponsored Products 常规位的流量得分（不含 SP 推荐位） |
| brandAdScore | number | SB 品牌广告得分。Sponsored Brands 品牌广告的流量得分（常规 + 视频，总和） |
| videoAdScore | number | SBV 视频广告得分。Sponsored Brands Video 视频广告的流量得分 |
| sponsoredRecommendationScore | number | SP 推荐位得分。Trending now / Seen on social media / Customers frequently viewed / 4 stars and above 等合计得分 |
| sponsoredRecommendationBreakdown | array | SP 推荐位得分明细。每项 `{title, score, scoreRatio}` |
| clickConcentrationShare | number | ABA TOP3 点击集中度。衡量点击是否集中在头部 ASIN；注意**不是转化率** |
| clickToPurchaseConversionRate | number | 点击到购买的转化率（purchaseQty / clickQty） |
| displayPositionTypes | array | 商品展示位置类型数组。可能包含以下值：natural=自然搜索结果位；ac=Amazon's Choice推荐位；sp=Sponsored Products赞助商品广告位；top=页面顶部品牌广告位；bottom=页面底部品牌广告位；er=Editorial Recommendations编辑推荐位；vedio=视频广告位；tr=Top Rated高评分推荐位；trfob=Top Rated Frequently Bought高频购买推荐位 |
| trafficCharacteristicMarkers | array | 关键词流量特征标记数组。可能包含以下值：isMainKw=主要流量词；isAccurateKw=精准流量词；isAccurateAboveKw=精准大词；isAccurateTailKw=精准长尾词 |
| conversionPerformanceMarkers | array | 转化效果标记数组。可能包含以下值：isPurchaseKw=出单词；isQualityKw=转化优质词；isStableKw=转化平稳词；isLossKw=转化流失词；isInvalidKw=无效曝光词 |
| lastNaturalRankTime | string | 最近有效自然排名的时间 |
| lastAdRankTime | string | 最近有效SP广告排名的时间 |
| periodEndDate | string | 本周期（周粒度）结束日期 = 开始周 + 7 天（站点时间） |
| updateTime | string | 关键词数据更新时间 |

## 错误码

接口包含两层状态码：网关调用状态通过 `errcode` 字段区分，`errcode = 200` 表示网关调用成功；SIF 业务成功通过响应体中的 `code` 字段区分，`code = "1"` 表示成功。当遇到未授权等网关错误时，HTTP 状态码和 `errcode` 为对应的错误码。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## MCP 示例

```json
{"toolName":"sif/asinKeywords","arguments":{"asin":"B0XXXXXXXX","country":"US","keyword":"charger","conditions":"nfPosition,isPurchaseKw","pageSize":50}}
```

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise



---
