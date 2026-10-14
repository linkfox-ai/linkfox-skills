---
name: linkfox-sif-keyword-summary
description: 在给定关键词下拆解所有竞品 ASIN 的流量来源——自然搜索、SP 广告、SB 品牌广告、SBV 视频广告、SP 推荐、AC/ER/TR 等推荐位，支持按 ASIN 过滤、指定日期区间及新进流量词等筛选。当用户提到关键词流量来源、该关键词下哪些竞品在抢流量、自然流量与付费流量占比、SP广告曝光、品牌广告占比、SP推荐位、推荐位广告/非广告拆分、搜索展示分析、Amazon's Choice或编辑推荐曝光、关键词竞争格局、ASIN流量构成、keyword traffic, traffic structure analysis, search share, ad share, traffic source distribution, SIF, traffic analysis, SP recommendation, recommend position breakdown时触发此技能。即使用户未明确提及"SIF"，只要其需求涉及在某关键词下分析竞品 ASIN 的流量来源分布，也应触发此技能。
---

# SIF Keyword Traffic Source Summary

## 能力边界

### 能力范围

- 针对单个 Amazon 关键词返回其下 ASIN 的自然搜索、SP、品牌、视频、AC、ER、TR 和推荐位广告/非广告流量来源及曝光结构。
- 支持 ASIN 过滤、单个 traffic condition、站点、最近 7 天或自定义日期区间、排序和分页；同时提供关键词级与商品级两套得分字段。

### 不适用范围

- 一次请求只能传一个关键词和一个 `condition`；多关键词或多流量条件比较必须分别调用。
- 不提供 ASIN 全关键词的完整汇总、长期排名趋势、销售估算、评论、Listing 优化或广告竞价/预算建议。

This skill guides you on how to query and analyze keyword traffic source data for Amazon products, helping sellers understand the traffic structure behind keywords — including organic search, Sponsored Products (SP) ads, brand ads, video ads, and various Amazon recommendation placements.

## Core Concepts

The SIF Keyword Summary tool returns, for one given keyword, the list of ASINs appearing under that keyword along with their per-keyword traffic exposure breakdown and their product-level cross-channel traffic mix. It answers: **Who is taking traffic under this keyword, and through which channels?**

**Traffic channels analyzed:**

- **Natural Search** — organic search result positions
- **SP Ads (Sponsored Products)** — paid product ad placements (regular slot)
- **Brand Ads (SB)** — top and bottom brand ad placements on the search results page
- **Video Ads (SBV)** — Sponsored Brands Video placements
- **SP Recommendation slots** — Trending now / Seen on social media / Customers frequently viewed / 4 stars and above
- **Amazon's Choice (AC)** — Amazon's Choice badge recommendations
- **Editorial Recommendations (ER)** — editorial/curated recommendation placements
- **Top Rated (TR)** — high-rating recommendation placements

**Two score families** (important — do not mix):

1. **Product-level** fields (no prefix, e.g. `naturalSearchExposureScore`): the ASIN's overall exposure across all keywords.
2. **Keyword-level** fields (`keyword…` prefix, e.g. `keywordNaturalExposureScore`): the ASIN's exposure on just this one queried keyword.

## Parameter Guide

### Required Parameter

| Parameter | Type | Description |
|-----------|------|-------------|
| searchKeyword | string | The search keyword to analyze. Translate to the target marketplace's language when applicable. Max 1000 characters. |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| country | string | US | Marketplace code (13 supported — see list below). |
| asins | string | (none) | Comma-separated ASIN filter; if omitted, returns all ASINs appearing under the keyword. Max 1000 chars. |
| condition | string | (none) | Filter by a specific traffic source. Only one value per request. See Condition Filters below. |
| last7d | boolean | true | Use the latest 7 days. When `false`, the API uses `startDate`/`endDate`. |
| startDate | string | — | `yyyy-MM-dd`. Takes effect when `last7d=false`; if omitted, the system's latest integral week is used. |
| endDate | string | — | `yyyy-MM-dd`, paired with `startDate`. |
| sortBy | string | (default) | Sort field. See sortBy section below. |
| pageNum | integer | 1 | Page number for pagination. |
| pageSize | integer | 100 | Results per page. Min 10, max 100. |
| desc | boolean | true | Sort in descending order. |

### Supported Marketplaces

13 marketplaces: US (United States), UK (United Kingdom), DE (Germany), CA (Canada), JP (Japan), FR (France), ES (Spain), IT (Italy), MX (Mexico), AU (Australia), AE (United Arab Emirates), BR (Brazil), SA (Saudi Arabia).

Default marketplace is **US**. Codes outside this list will be rejected by the API pattern.

### Condition Filters

Each request can include at most **one** condition filter. Flag-style:

| Value | Meaning |
|-------|---------|
| nfPosition | Natural search traffic keywords |
| isSpAd | SP ad keywords |
| isVedioAd | Video ad keywords |
| isBrandAd | Brand ad keywords |
| isPPCAd | PPC ad keywords (all paid ad types) |
| isSearchRecommend | Search recommendation keywords |
| acAd | SP recommendation (Trending now / Customers frequently viewed / etc.) |

Period-count filters (`.total` full / `.in` new-in):

| Value | Meaning |
|-------|---------|
| totalPeriod.in | Newly-entered traffic keywords this period |
| nfKeywordCnt.total / nfKeywordCnt.in | Keywords with (new) organic exposure |
| adKeywordCnt.total / adKeywordCnt.in | Keywords with (new) ad exposure |
| allSpKeywordCnt.total / allSpKeywordCnt.in | (New) SP-ad keywords (regular + recommendation) |
| spKeywordCnt.total / spKeywordCnt.in | (New) SP regular keywords |
| recSpKeywordCnt.total / recSpKeywordCnt.in | (New) SP recommendation keywords |
| allSbKeywordCnt.total / allSbKeywordCnt.in | (New) SB-ad keywords |
| sbKeywordCnt.total / sbKeywordCnt.in | (New) SB regular keywords |
| sbvKeywordCnt.total / sbvKeywordCnt.in | (New) SBV keywords |

### sortBy

Leave empty for system default. Valid values:

`totalKeywordNum` (total keyword count), `naturalKeywordNum`, `brandKeywordNum`, `vedioKeywordNum`, `acKeywordNum`, `erKeywordNum`, `trKeywordNum`, `sumScore` (total exposure across all keywords), `totalNfScore`, `totalSpSocre` (note spelling), `totalBrandScore`, `totalVedioScore`, `totalAcScore`, `totalTrScore`, `totalErScore`.

## MCP 调用方式

- **MCP Server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **精确 toolName**：`sif/keywordSummary`
- **响应字段来源**：`skills/linkfox-sif-keyword-summary/references/api.md`；只从该文件的响应章节核对字段。
- **arguments**：直接使用本 reference 的请求参数对象，不包裹 `body`、`params` 或 `data`。
- **自动授权**：WorkBuddy 自动注入授权上下文；禁止传 `headers`、`Authorization`、API Key、token、JWT 或手机号。
- **响应处理**：text JSON 只解析一次；先处理 MCP/代理错误，再处理下游 `code`/`errcode` 与消息字段。
- **成本纪律**：相同 `toolName + arguments` 默认只调用一次；失败或空结果不得自动换关键词、站点、翻页或筛选条件。继续查询前先告知额外消耗并取得同意。
- **本地能力变化**：旧脚本的 24 小时缓存、自动落盘、会话索引和 stdout 摘要不属于 MCP 能力，迁移后不再承诺。

```json
{"toolName":"sif/keywordSummary","arguments":{"searchKeyword":"wireless charger","country":"US"}}
```

## 解决认证和积分问题
发生以下异常情况时，采用 onboarding.md 引导解决问题：

### 异常情况
- **MCP 不可用**：检查 `LinkFox` 配置并刷新会话，禁止回退旧 HTTP 网关。
- **401**：WorkBuddy 自动授权上下文异常；不在参数中补传凭证。
- **402 / 积分不足**：引导用户访问 `https://agent.linkfox.com/` 自助处理，不自动下单或支付。
- **403**：权限问题，与 401/402 分开处理。

## Usage Examples

**1. Basic keyword traffic overview**
Query the traffic source breakdown for a keyword in the US marketplace:
```
searchKeyword: "wireless charger", country: "US"
```

**2. Filter for organic search traffic only**
See only ASINs that appear in natural search results for a keyword:
```
searchKeyword: "wireless charger", country: "US", condition: "nfPosition"
```

**3. Analyze SP ad competition**
Find which ASINs are running SP ads for a keyword:
```
searchKeyword: "wireless charger", country: "US", condition: "isSpAd"
```

**4. SP recommendation slots**
Find ASINs surfacing in SP recommendation slots (Trending now, Customers frequently viewed, etc.):
```
searchKeyword: "wireless charger", country: "US", condition: "acAd"
```

**5. Keyword analysis for a non-US marketplace**
Analyze traffic sources in the Japan marketplace (use the local language keyword):
```
searchKeyword: "ワイヤレス充電器", country: "JP"
```

**6. Focus on specific competitor ASINs**
Limit results to a small set of competing ASINs:
```
searchKeyword: "wireless charger", country: "US", asins: "B01NBNDC1T,B09VLJJPL6"
```

**7. Custom date range**
```
searchKeyword: "wireless charger", country: "US", last7d: false, startDate: "2026-04-05", endDate: "2026-04-11"
```

**8. Rank ASINs by their overall SP exposure**
```
searchKeyword: "wireless charger", country: "US", sortBy: "totalSpSocre", desc: true
```

**9. Newly-entered traffic keywords this period**
```
searchKeyword: "wireless charger", country: "US", condition: "totalPeriod.in"
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables. Group data by traffic channel exposure ratios for easy comparison.
2. **Distinguish product-level vs keyword-level scores**: Do not mix `naturalSearchExposureScore` (product-wide) with `keywordNaturalExposureScore` (this keyword only). Label columns so users know which scope they are reading.
3. **Highlight key ratios**: When displaying results, emphasize the natural search exposure ratio vs. paid ad exposure ratio to help users quickly assess the organic-to-paid balance.
4. **Translate field names**: Present field names in user-friendly language rather than raw API field names (e.g., "Natural Search Exposure Ratio" instead of "naturalSearchExposureRatio").
5. **Volume notice**: When results are large (high total count), show core data and remind users they can paginate to see more results.
6. **Period annotation**: When comparing exposure/counts, label the resolved window — default `last7d`; or `startDate ~ endDate` if a custom range was set. Also surface `dataPeriodStartDate` on each row.
7. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query parameters (e.g., checking keyword spelling or marketplace code).
8. **Percentage formatting**: Display exposure ratios as percentages (e.g., 0.45 as "45%") for readability.
9. **Traffic source summary**: When presenting a single ASIN's data, provide a brief traffic composition summary (e.g., "This product gets 60% of its exposure from organic search, 25% from SP ads, and 15% from brand ads"); prefer keyword-level fields when the user asks specifically about this keyword.

## Important Limitations

- **Single condition filter**: Only one `condition` value can be used per request. To compare multiple traffic sources, make separate requests.
- **Marketplace coverage**: 13 marketplaces only — IN / NL / SE / PL / TR / SG are no longer available.
- **Keyword language**: The `searchKeyword` should be in the language of the target marketplace for best results.
- **Result cap**: Each page returns at most 100 records.
- **Scope**: This endpoint focuses on per-keyword ASIN traffic; it does not return whole-ASIN metadata, cross-channel keyword counts, or variant aggregation. Use the ASIN traffic-source tool for those.

## User Expression & Scenario Quick Reference

**Applicable** — Traffic source and competition structure analysis for Amazon keywords:

| User Says | Scenario |
|-----------|----------|
| "Where does the traffic come from for this keyword" | Traffic source breakdown |
| "How much organic vs paid traffic" | Organic/paid ratio analysis |
| "Who's running SP ads for this keyword" | SP ad competition analysis (`condition=isSpAd`) |
| "Which products are in SP recommendation slots" | SP recommendation lookup (`condition=acAd`) |
| "Which products have Amazon's Choice" | AC badge analysis (via `amazonsChoiceExposureScore`) |
| "Is this keyword dominated by ads" | Ad saturation assessment |
| "Show me the brand ad competition" | Brand ad landscape analysis |
| "Traffic structure for my competitor's keyword" | Competitive traffic analysis |
| "Which products get editorial recommendations" | ER placement analysis |
| "Compare these 2 ASINs on this keyword" | ASIN filter via `asins="B0A,B0B"` |
| "For the week of March 8, traffic under this keyword" | Custom `startDate`/`endDate` window |
| "Newly-entered traffic keywords this period" | New-in filter (`condition=totalPeriod.in`) |

**Not applicable** — Needs beyond keyword traffic source analysis:
- Historical keyword ranking trends beyond current + custom window (use ABA data tools)
- Advertising bid/budget optimization
- Product reviews or listing content
- Sales volume estimation
- Full keyword search volume curve over time
- Whole-ASIN traffic structure across all keywords (use the SIF ASIN traffic-source tool)

## 积分消耗规则

消耗 9 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `linkfox-sif-keyword-summary.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*



---

# API 参考（完整归档）

# SIF-关键词流量来源 API 参考

## MCP 调用规范

- **MCP Server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **精确 toolName**：`sif/keywordSummary`
- **arguments**：下方请求参数对象直接作为 `arguments`，不传认证字段，不额外包裹。
- **解析与失败**：text JSON 只解析一次；区分 MCP/代理错误与下游业务错误；禁止 HTTP fallback 和自动重复计费调用。

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKeyword | string | 是 | 搜索关键词，尽量翻译成对应国家站点的语言。最大长度 1000 字符 |
| country | string | 否 | 国家站点，默认 `US`。可选值（共 13 个）：`US`、`UK`、`DE`、`CA`、`JP`、`FR`、`ES`、`IT`、`MX`、`AU`、`AE`、`BR`、`SA` |
| asins | string | 否 | ASIN 过滤列表，多个用英文逗号分隔；不传则返回该关键词下所有 ASIN。最大长度 1000 字符 |
| condition | string | 否 | 条件筛选，每次只能传一个。<br>**标志类**：`nfPosition`（自然流量词）、`isSpAd`（SP广告词）、`isVedioAd`（视频广告词）、`isBrandAd`（品牌广告词）、`isPPCAd`（PPC广告词）、`isSearchRecommend`（搜索推荐词）、`acAd`（SP 推荐）<br>**周期计数类**：`totalPeriod.in`（新进全部流量词）、`nfKeywordCnt.total` / `.in`、`adKeywordCnt.total` / `.in`、`allSpKeywordCnt.total` / `.in`、`spKeywordCnt.total` / `.in`、`recSpKeywordCnt.total` / `.in`、`allSbKeywordCnt.total` / `.in`、`sbKeywordCnt.total` / `.in`、`sbvKeywordCnt.total` / `.in` |
| last7d | boolean | 否 | 是否取最近 7 天数据，默认 `true`。传 `false` 时使用 `startDate`/`endDate` 区间 |
| startDate | string | 否 | 开始日期 `yyyy-MM-dd`（`last7d=false` 时生效；不填取系统最新整周） |
| endDate | string | 否 | 结束日期 `yyyy-MM-dd`（与 `startDate` 配套） |
| sortBy | string | 否 | 排序字段。可选值：`totalKeywordNum`（全部流量词）、`naturalKeywordNum`（自然流量词）、`brandKeywordNum`（品牌广告词）、`vedioKeywordNum`（视频广告词）、`acKeywordNum`（AC推荐词）、`erKeywordNum`（ER推荐词）、`trKeywordNum`（TR推荐词）、`sumScore`（所有关键词曝光总得分）、`totalNfScore`、`totalSpSocre`（注意拼写）、`totalBrandScore`、`totalVedioScore`、`totalAcScore`、`totalTrScore`、`totalErScore` |
| pageNum | integer | 否 | 页码，默认 `1` |
| pageSize | integer | 否 | 每页数量，最小 10，最大 100，默认 `100` |
| desc | boolean | 否 | 是否降序，默认 `true` |


## 响应结构

### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | SIF 业务返回码，`"1"` 表示成功 |
| msg | string | 消息 |
| total | integer | 本次实际返回的数据数量 |
| data | array | 返回数据，商品关键词流量数据对象数组 |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| title | string | 标题 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |

> 本接口不返回 `isParentAsin`、`variantsNum`、`noKeywordVariantsNum`；如需这些字段请使用 `sif/asinSummary` 接口。

### 数据项字段（`data` 数组中的每个对象）

> 两类得分：无前缀字段（如 `naturalSearchExposureScore`）为该 ASIN 在所有关键词上的商品级整体指标；`keyword*` 前缀字段（如 `keywordNaturalExposureScore`）为该 ASIN 仅在本次查询的关键词上的指标。

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN 编码 |
| productTitle | string | 商品标题 |
| productImageUrl | string | 商品主图 URL |
| productPrice | number | 商品售价 |
| customerRatingCount | integer | 客户评分总数 |
| productStarRating | number | 商品星级（0–5 星） |
| productRatingScore | number | 商品评分数值 |
| productUpdateTime | string | 产品更新时间（`yyyy-MM-dd HH:mm:ss`） |
| dataPeriodStartDate | string | 数据周期起始日期（`yyyy-MM-dd`） |
| totalExposureScore | number | 总曝光分数 |
| totalExposureRatio | number | 总流量份额 |
| naturalSearchExposureScore | number | 自然搜索曝光总分 |
| naturalSearchExposureRatio | number | 自然搜索曝光占比 |
| sponsoredProductsExposureScore | number | SP 广告曝光总分 |
| sponsoredProductsExposureRatio | number | SP 广告曝光占比 |
| brandAdExposureScore | number | 品牌广告曝光总分 |
| brandAdExposureRatio | number | 品牌广告曝光占比 |
| videoAdExposureScore | number | 视频广告曝光总分 |
| videoAdExposureRatio | number | 视频广告曝光占比 |
| amazonsChoiceExposureScore | number | AC 曝光总分 |
| amazonsChoiceExposureRatio | number | AC 曝光占比 |
| editorialRecommendationsExposureScore | number | ER 曝光总分 |
| editorialRecommendationsExposureRatio | number | ER 曝光占比 |
| topRatedExposureScore | number | TR 曝光总分 |
| topRatedExposureRatio | number | TR 曝光占比 |
| recommendPositionExposureScore | number | 推荐位曝光总分 |
| recommendAdExposureScore | number | 推荐位广告曝光分数 |
| recommendAdExposureRatio | number | 推荐位广告流量份额 |
| recommendNonadExposureScore | number | 推荐位非广告曝光分数 |
| recommendNonadExposureRatio | number | 推荐位非广告流量份额 |
| comprehensiveNaturalExposureScore | number | 综合自然流量得分（自然搜索 + 推荐位非广告） |
| comprehensiveNaturalExposureRatio | number | 综合自然流量份额 |
| keywordTotalExposureScore | number | 关键词总得分 |
| keywordNaturalExposureScore | number | 关键词自然得分 |
| keywordSponsoredProductsExposureScore | number | 关键词 SP 广告得分 |
| keywordBrandAdExposureScore | number | 关键词品牌广告得分 |
| keywordVideoAdExposureScore | number | 关键词视频广告得分 |
| keywordAmazonsChoiceExposureScore | number | 关键词 AC 得分 |
| keywordRecommendExposureScore | number | 关键词推荐位得分 |
| keywordRecommendAdExposureScore | number | 关键词推荐位广告得分 |
| keywordRecommendNonadExposureScore | number | 关键词推荐位非广告得分 |
| keywordComprehensiveNaturalExposureScore | number | 关键词综合自然得分（自然 + 推荐位非广告） |
| ppcTrafficSources | array | PPC 付费广告流量来源标记。包含：SP 广告、头部品牌广告、底部品牌广告、视频广告 |
| naturalSearchTrafficSources | array | 自然搜索流量来源标记 |
| amazonRecommendationSources | array | 亚马逊推荐流量来源标记。包含：Best Seller、AC、ER、TR、TRFOB 等 |
| promotionalDealSources | array | 促销活动流量来源标记。包含：Coupon、Limited Time Deal、Lowest Price in 30 Days 等 |

> 本接口不返回以下字段：`productCategory`、`productFeatures`、`isVariantProduct`、`isMonitored`、`monitoringStartTime`，以及 per-ASIN 的 `totalTrafficKeywordCount`、`naturalSearchKeywordCount`、`sponsoredProductsKeywordCount`、`brandAdKeywordCount`、`topBrandAdKeywordCount`、`bottomBrandAdKeywordCount`、`videoAdKeywordCount`、`amazonsChoiceKeywordCount`、`editorialRecommendationsKeywordCount`、`topRatedKeywordCount`、`frequentlyBoughtKeywordCount`。如需这些字段，请使用 `sif/asinSummary` 接口。

## 错误码

接口包含两层状态码：网关调用状态通过 `errcode` 字段区分，`errcode = 200` 表示网关调用成功；SIF 业务成功通过响应体中的 `code` 字段区分，`code = "1"` 表示成功。当遇到未授权等网关错误时，HTTP 状态码和 `errcode` 为对应的错误码。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
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
{"toolName":"sif/keywordSummary","arguments":{"searchKeyword":"wireless charger","country":"US","condition":"isSpAd","sortBy":"totalSpSocre","desc":true}}
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
