---
name: linkfox-sif-keyword-summary
description: 在给定关键词下拆解所有竞品 ASIN 的流量来源——自然搜索、SP 广告、SB 品牌广告、SBV 视频广告、SP 推荐、AC/ER/TR 等推荐位，支持按 ASIN 过滤、指定日期区间及新进流量词等筛选。当用户提到关键词流量来源、该关键词下哪些竞品在抢流量、自然流量与付费流量占比、SP广告曝光、品牌广告占比、SP推荐位、推荐位广告/非广告拆分、搜索展示分析、Amazon's Choice或编辑推荐曝光、关键词竞争格局、ASIN流量构成、keyword traffic, traffic structure analysis, search share, ad share, traffic source distribution, SIF, traffic analysis, SP recommendation, recommend position breakdown时触发此技能。即使用户未明确提及"SIF"，只要其需求涉及在某关键词下分析竞品 ASIN 的流量来源分布，也应触发此技能。
---

# SIF Keyword Traffic Source Summary

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

## 调用方式

- **API 端点**：`POST /sif/keywordSummary`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/sif_keyword_traffic.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-sif-keyword-summary-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

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

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
