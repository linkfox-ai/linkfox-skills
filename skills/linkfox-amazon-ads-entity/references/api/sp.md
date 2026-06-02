# Sponsored Products (SP) 实体查询 — 参数与字段参考

覆盖 6 个 SP v3 list 端点。通用约定、共用参数、错误码见 `../api.md`。

## 可用脚本

| 脚本 | 业务实体 | 返回 key |
|------|---------|---------|
| `sp/list_campaigns.py` | 广告活动 | `campaigns` |
| `sp/list_ad_groups.py` | 广告组 | `adGroups` |
| `sp/list_keywords.py` | 关键词 | `keywords` |
| `sp/list_negative_keywords.py` | 否定关键词 | `negativeKeywords` |
| `sp/list_product_ads.py` | 商品广告 | `productAds` |
| `sp/list_targets.py` | 商品定向 | `targetingClauses`（不是 `targets`）|

## 过滤器结构（5 类）

### 1. Object —— `{"include":[...]}` / `{"exclude":[...]}`

适用：`campaignIdFilter` / `adGroupIdFilter` / `keywordIdFilter` / `targetIdFilter` / `adIdFilter` / `negativeKeywordIdFilter` / `portfolioIdFilter` / `stateFilter` / `expressionTypeFilter`

```json
{"stateFilter": {"include": ["ENABLED","PAUSED"]}}
{"campaignIdFilter": {"include": ["1122334455"]}}
{"expressionTypeFilter": {"include": ["AUTO"]}}
```

### 2. Array —— 裸数组 `["EXACT","BROAD"]`

适用：`matchTypeFilter`（keywords / negativeKeywords）

```json
{"matchTypeFilter": ["EXACT","PHRASE"]}
```

兼容：传 `{"include":["EXACT"]}` 本 skill 自动解包。

### 3. Scalar —— 裸字符串 `"AUTO"`

适用：`campaignTargetingTypeFilter`（adGroups）

```json
{"campaignTargetingTypeFilter": "AUTO"}
```

### 4. Text —— `{"queryTermMatchType":"...","include":[...]}`

适用：`nameFilter`（campaigns / adGroups）、`keywordTextFilter`（keywords / negativeKeywords）

```json
{"nameFilter": {"queryTermMatchType": "BROAD_MATCH", "include": ["holiday"]}}
```

`queryTermMatchType`: `BROAD_MATCH` / `EXACT_MATCH`。

### 5. Client —— 本 skill 在本地过滤

适用：`asinFilter` / `skuFilter`（productAds）

```json
{"asinFilter": {"include": ["B01ABCDEFG"]}}
{"asinFilter": ["B01ABCDEFG"]}
{"asinFilter": "B01ABCDEFG"}
```

Amazon 原生 list 接口对这两个字段不生效，本 skill 拉取后本地精确匹配。建议同时传 `campaignIdFilter` / `adGroupIdFilter` / `adIdFilter` 收窄拉取量；否则触发全量拉取 + stderr 性能提示。

输出会多出：`serverTotalBeforeClientFilter` / `clientSideFilters`。

## 枚举值

| 字段 | 值 | 适用 |
|------|----|------|
| `state` | `ENABLED` / `PAUSED` / `ARCHIVED` | 全部 6 个实体 |
| `matchType` | `BROAD` / `PHRASE` / `EXACT` | keywords |
| `matchType` | `NEGATIVE_EXACT` / `NEGATIVE_PHRASE` | negativeKeywords |
| `expressionType` | `AUTO` / `MANUAL` | targets |
| `campaignTargetingType` | `AUTO` / `MANUAL` | adGroups |
| `queryTermMatchType` | `BROAD_MATCH` / `EXACT_MATCH` | nameFilter / keywordTextFilter |

## 每个脚本的过滤器

| 脚本 | 可用过滤器 |
|------|-----------|
| `list_campaigns.py` | `campaignIdFilter`、`stateFilter`、`nameFilter`、`portfolioIdFilter` |
| `list_ad_groups.py` | `adGroupIdFilter`、`campaignIdFilter`、`stateFilter`、`nameFilter`、`campaignTargetingTypeFilter` |
| `list_keywords.py` | `keywordIdFilter`、`adGroupIdFilter`、`campaignIdFilter`、`stateFilter`、`matchTypeFilter`、`keywordTextFilter` |
| `list_negative_keywords.py` | `negativeKeywordIdFilter`、`adGroupIdFilter`、`campaignIdFilter`、`stateFilter`、`matchTypeFilter`、`keywordTextFilter` |
| `list_product_ads.py` | `adIdFilter`、`adGroupIdFilter`、`campaignIdFilter`、`stateFilter`、`asinFilter`（Client）、`skuFilter`（Client） |
| `list_targets.py` | `targetIdFilter`、`adGroupIdFilter`、`campaignIdFilter`、`stateFilter`、`expressionTypeFilter` |

## 常见实体字段

| 实体 | 字段 |
|------|------|
| campaigns | `campaignId` / `name` / `state` / `targetingType` / `budget.{budget,budgetType}` / `startDate` / `endDate` / `dynamicBidding.strategy` / `portfolioId` |
| adGroups | `adGroupId` / `campaignId` / `name` / `state` / `defaultBid` |
| keywords | `keywordId` / `adGroupId` / `campaignId` / `keywordText` / `matchType` / `state` / `bid` |
| negativeKeywords | 同 keywords，`matchType` ∈ `NEGATIVE_EXACT` / `NEGATIVE_PHRASE` |
| productAds | `adId` / `adGroupId` / `campaignId` / `asin` / `sku` / `state` |
| targetingClauses | `targetId` / `adGroupId` / `campaignId` / `state` / `expression` / `expressionType` / `bid` |

## 调用示例

```bash
# 列活跃 campaigns
python sp/list_campaigns.py '{"profileId":1111111111,"region":"NA",
  "stateFilter":{"include":["ENABLED"]},"maxResults":50}'

# 按 campaign 列 AUTO 广告组
python sp/list_ad_groups.py '{"profileId":1111111111,"region":"NA",
  "campaignIdFilter":{"include":["1122334455"]},
  "campaignTargetingTypeFilter":"AUTO"}'

# EXACT 关键词
python sp/list_keywords.py '{"profileId":1111111111,"region":"NA",
  "adGroupIdFilter":{"include":["5566778899"]},
  "matchTypeFilter":["EXACT"]}'

# 按 ASIN 反查（client-side，带 campaign 收窄）
python sp/list_product_ads.py '{"profileId":1111111111,"region":"NA",
  "asinFilter":{"include":["B01ABCDEFG"]},
  "campaignIdFilter":{"include":["1122334455"]}}'

# AUTO 定向目标
python sp/list_targets.py '{"profileId":1111111111,"region":"NA",
  "adGroupIdFilter":{"include":["5566778899"]},
  "expressionTypeFilter":{"include":["AUTO"]}}'
```


