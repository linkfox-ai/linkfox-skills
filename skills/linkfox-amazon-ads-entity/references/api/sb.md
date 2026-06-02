# Sponsored Brands (SB) 实体查询 — 参数与字段参考

覆盖 SB v4 的 3 个 list 端点。通用约定、共用参数、错误码见 `../api.md`。

## 可用脚本

| 脚本 | 业务实体 | 返回 key |
|------|---------|---------|
| `sb/list_campaigns.py` | 广告活动 | `campaigns` |
| `sb/list_ad_groups.py` | 广告组 | `adGroups` |
| `sb/list_ads.py` | 广告创意 | `ads` |

> **注意**：SB v4 仅提供 campaigns/adGroups/ads 三个 list。SB 的 keywords/negativeKeywords/targets/negativeTargets 是 v3 REST 风格（`GET /sb/xxx/{id}` 按 id 单查 / `POST /sb/xxx` 创建），**Amazon 官方没有提供"list all"端点**，本 skill 也不提供。

## 响应额外字段

SB v4 响应除 `<entityKey>`、`nextToken` 之外，还会带 `totalCount`：

```json
{
  "campaigns": [ ... ],
  "totalCount": 42,
  "nextToken": "..."
}
```

本 skill 输出会自动汇总所有分页 items，`total` 字段是**最终**条数。

## 过滤器结构

SB v4 的 filter 体系与 SP v3 **基本一致**（复用 skill 的结构化规范）：

### Object —— `{"include":[...]}` / `{"exclude":[...]}`

适用：`campaignIdFilter` / `adGroupIdFilter` / `adIdFilter` / `portfolioIdFilter` / `stateFilter`

```json
{"stateFilter": {"include": ["ENABLED","PAUSED"]}}
{"campaignIdFilter": {"include": ["1122334455"]}}
```

### Text —— `{"queryTermMatchType":"...","include":[...]}`

适用：`nameFilter`（campaigns / adGroups）

```json
{"nameFilter": {"queryTermMatchType": "BROAD_MATCH", "include": ["holiday"]}}
```

`queryTermMatchType`: `BROAD_MATCH` / `EXACT_MATCH`。

### 其他入参

| 参数 | 类型 | 说明 |
|------|------|------|
| `includeExtendedDataFields` | boolean | 返回扩展字段（策略、时间戳等） |

## 枚举值

| 字段 | 值 | 适用 |
|------|----|------|
| `state` | `ENABLED` / `PAUSED` / `ARCHIVED` | 全部 3 个实体 |

## 每个脚本的过滤器

| 脚本 | 可用过滤器 |
|------|-----------|
| `list_campaigns.py` | `campaignIdFilter`、`stateFilter`、`nameFilter`、`portfolioIdFilter` |
| `list_ad_groups.py` | `adGroupIdFilter`、`campaignIdFilter`、`stateFilter`、`nameFilter` |
| `list_ads.py` | `adIdFilter`、`adGroupIdFilter`、`campaignIdFilter`、`stateFilter` |

## 常见实体字段

| 实体 | 字段 |
|------|------|
| campaigns | `campaignId` / `name` / `state` / `portfolioId` / `budget.{budget,budgetType}` / `brandEntityId` / `brandName` / `startDate` / `endDate` / `bidding` 等 |
| adGroups | `adGroupId` / `campaignId` / `name` / `state` / `bidOptimization` 等 |
| ads | `adId` / `adGroupId` / `campaignId` / `state` / `creativeType`（`PRODUCT_COLLECTION` / `VIDEO` / `BRAND_VIDEO` / `STORE_SPOTLIGHT` 等）/ 对应类型的创意字段 |

> SB v4 的 ads 列表返回各种创意类型的元数据；若需读取创意细节，Amazon 另提供 `/sb/ads/creatives/*` 端点（本 skill 暂未覆盖）。

## 调用示例

```bash
# 列活跃 SB campaigns
python sb/list_campaigns.py '{"profileId":1111111111,"region":"NA",
  "stateFilter":{"include":["ENABLED"]},"maxResults":50}'

# 按 campaign 列 adGroups（带名称模糊匹配）
python sb/list_ad_groups.py '{"profileId":1111111111,"region":"NA",
  "campaignIdFilter":{"include":["1122334455"]},
  "nameFilter":{"queryTermMatchType":"BROAD_MATCH","include":["spring"]}}'

# 列某 adGroup 下的 ads
python sb/list_ads.py '{"profileId":1111111111,"region":"NA",
  "adGroupIdFilter":{"include":["5566778899"]}}'
```

## 与 SP 的差异速查

| 维度 | SP v3 | SB v4 |
|------|-------|-------|
| 路径前缀 | `sp/` | `sb/v4/` |
| Content-Type | `application/vnd.sp<Entity>.v3+json`（Amazon 严格要求小写 vendor MIME） | `application/vnd.sb<entity>resource.v4+json`（全小写；响应 MIME） |
| 实体数量 | 6 个 list | 3 个 list（keywords/targets 等 v3 未提供 list） |
| 过滤器 | Object / Array / Scalar / Text / Client 5 类 | 主要 Object + Text；暂未见到 Array/Scalar 需求 |
| 响应分页 | `nextToken` | `nextToken` + `totalCount`（SB 特有） |
| 客户端过滤 | `asinFilter` / `skuFilter`（productAds） | 暂无 |


