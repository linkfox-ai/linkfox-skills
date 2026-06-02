# Sponsored Display (SD) 实体查询 — 参数与字段参考

覆盖 SD v3 的 6 个 list 端点的查询参数与字段定义。通用约定、共用参数、错误码见 `../api.md`；写操作（create/update）通过 `scripts/sd/create_*.py` 与 `scripts/sd/update_*.py` 调用，payload 透传 Amazon 原生格式。

## 可用脚本

| 脚本 | 业务实体 | 返回 key |
|------|---------|---------|
| `sd/list_campaigns.py` | 广告活动 | `campaigns` |
| `sd/list_ad_groups.py` | 广告组 | `adGroups` |
| `sd/list_product_ads.py` | 商品广告 | `productAds` |
| `sd/list_targets.py` | 定向子句（商品/受众） | `targetingClauses` |
| `sd/list_negative_targets.py` | 否定定向子句 | `negativeTargetingClauses` |
| `sd/list_creatives.py` | 创意素材 | `creatives` |

> **注意**：Sponsored Display **没有 keywords**（仅商品 / 受众 / 品类定向）。按 id 单查、创建、删除、归档，以及 brandSafety / forecasts / budgetRules / optimizationRules / locations 等"非基础实体查询"接口本技能不覆盖。

## SD 接口形态

| 维度 | Sponsored Display v3 |
|------|----------------------|
| HTTP 方法 | `GET` |
| 参数位置 | querystring |
| 分页方式 | `startIndex` + `count`（偏移分页） |
| `stateFilter` 实参 | 逗号分隔小写串，如 `enabled,paused,archived` |
| id 类过滤实参 | 逗号分隔字符串，如 `"123,456"` |
| 扩展字段 | 通过路径区分：基础 `/sd/<entity>`，扩展 `/sd/<entity>/extended` |
| Content-Type | `application/json` |

所有过滤字段对外统一接受 `{"include":[...]}`、裸数组、单值字符串三种宽容形态；脚本会将其序列化为 Sponsored Display 端所需的 querystring 参数。

## 过滤器结构

### Object —— `{"include":[...]}`

适用：`campaignIdFilter` / `adGroupIdFilter` / `adIdFilter` / `targetIdFilter` / `portfolioIdFilter` / `creativeIdFilter` / `stateFilter`

```json
{"stateFilter":     {"include": ["ENABLED","PAUSED"]}}
{"campaignIdFilter":{"include": ["1122334455", "6677889900"]}}
```

兼容写法（自动归一）：
- 裸数组 `["ENABLED"]` → `{"include":["ENABLED"]}`
- 裸字符串 `"ENABLED"` → `{"include":["ENABLED"]}`

### Text —— `nameFilter`

Sponsored Display **仅支持精确匹配**，没有 `BROAD_MATCH`：

```json
{"nameFilter": {"queryTermMatchType":"EXACT_MATCH","include":["holiday"]}}
```

传 `BROAD_MATCH` 时脚本会在 stderr 输出一次提示，并按 `include[0]` 作 `name` 精确匹配。

### Client-side filter —— `asinFilter` / `skuFilter`（仅 productAds）

Sponsored Display 的 `/sd/productAds` 接口不支持按 ASIN / SKU 过滤；脚本会先按其他过滤条件拉取 productAds，再在本地按精确值匹配。建议同时传 `campaignIdFilter` 或 `adGroupIdFilter` 收窄上游拉取范围，否则 stderr 会输出性能提示。

```json
{"asinFilter":{"include":["B01ABCDEFG"]},
 "campaignIdFilter":{"include":["1122334455"]}}
```

## 其他入参

| 参数 | 类型 | 说明 |
|------|------|------|
| `fetchAll` | bool | 默认 `true`，关闭后只拉第一页 |
| `maxResults` | int | 1-100，默认 100；对应 Sponsored Display 端 `count`（每页大小） |
| `includeExtendedDataFields` | bool | 默认 `false`；`true` 时请求 `/sd/<entity>/extended` 路径；**`creatives` 没有 extended 路径，此入参无效** |
| `skipDepCheck` | bool | 跳过 ads-auth 依赖检查 |

## 枚举值

| 字段 | 值 | 适用 |
|------|----|------|
| `state` | `ENABLED` / `PAUSED` / `ARCHIVED`（脚本提交上游时自动转为 `enabled` / `paused` / `archived`） | 全部 6 个实体 |
| `expressionType` | `auto` / `manual` | targets |
| `creativeType` | （Sponsored Display 各 creative 类型，由上游返回原值） | creatives |

## 每个脚本的过滤器

| 脚本 | 可用过滤器 |
|------|-----------|
| `list_campaigns.py` | `campaignIdFilter`、`stateFilter`、`nameFilter`、`portfolioIdFilter` |
| `list_ad_groups.py` | `adGroupIdFilter`、`campaignIdFilter`、`stateFilter`、`nameFilter` |
| `list_product_ads.py` | `adIdFilter`、`adGroupIdFilter`、`campaignIdFilter`、`stateFilter`、`asinFilter`（Client）、`skuFilter`（Client） |
| `list_targets.py` | `targetIdFilter`、`adGroupIdFilter`、`campaignIdFilter`、`stateFilter` |
| `list_negative_targets.py` | `adGroupIdFilter`、`campaignIdFilter`、`stateFilter` |
| `list_creatives.py` | `creativeIdFilter`、`adGroupIdFilter`（互斥，同时传时上游会按 400 / 422 返回） |

## 常见实体字段

| 实体 | 字段（节选；extended 路径返回更多） |
|------|---------|
| campaigns | `campaignId` / `name` / `state` / `tactic`（`T00020` / `T00030`）/ `costType`（`cpc` / `vcpm`）/ `budget` / `budgetType` / `startDate` / `endDate` / `portfolioId` |
| adGroups | `adGroupId` / `campaignId` / `name` / `state` / `defaultBid` / `bidOptimization` / `creativeType` |
| productAds | `adId` / `adGroupId` / `campaignId` / `state` / `asin` / `sku` / `landingPageURL` / `landingPageType` |
| targetingClauses | `targetId` / `adGroupId` / `campaignId` / `state` / `expressionType`（auto / manual）/ `expression`（type ∈ `asinSameAs` / `asinCategorySameAs` / `audience` / `views` / `purchases` ...） / `bid` |
| negativeTargetingClauses | `targetId` / `adGroupId` / `campaignId` / `state` / `expression`（与 targets 类似，type 仅限 `asinSameAs` / `asinBrandSameAs`） |
| creatives | `creativeId` / `adGroupId` / `name` / `creativeType` / `properties`（headline / brandLogoAssetID / video 等，按 creativeType 不同） / `moderationStatus` |

## 调用示例

```bash
# 列活跃 SD campaigns
python sd/list_campaigns.py '{"profileId":1111111111,"region":"NA",
  "stateFilter":{"include":["ENABLED"]},"maxResults":50}'

# 按 campaign 列 SD adGroups（含扩展字段，请求 /sd/adGroups/extended）
python sd/list_ad_groups.py '{"profileId":1111111111,"region":"NA",
  "campaignIdFilter":{"include":["1122334455"]},
  "includeExtendedDataFields":true}'

# 按 ASIN 反查 SD 投放（client-side 过滤，带 campaign 收窄）
python sd/list_product_ads.py '{"profileId":1111111111,"region":"NA",
  "asinFilter":{"include":["B01ABCDEFG"]},
  "campaignIdFilter":{"include":["1122334455"]}}'

# 列某 adGroup 下的定向子句
python sd/list_targets.py '{"profileId":1111111111,"region":"NA",
  "adGroupIdFilter":{"include":["5566778899"]}}'

# 列某 adGroup 下的否定定向
python sd/list_negative_targets.py '{"profileId":1111111111,"region":"NA",
  "adGroupIdFilter":{"include":["5566778899"]}}'

# 列某 adGroup 下的创意
python sd/list_creatives.py '{"profileId":1111111111,"region":"NA",
  "adGroupIdFilter":{"include":["5566778899"]}}'
```

## 与 SP / SB 的差异速查

供从 Sponsored Products / Sponsored Brands 迁移到 Sponsored Display 的开发者对照查阅。

| 维度 | SP v3 | SB v4 | SD v3 |
|------|-------|-------|-------|
| 路径前缀 | `sp/` | `sb/v4/` | `sd/`（+ `/extended` 子路径） |
| HTTP 方法 | POST list | POST list | GET |
| Content-Type | `application/vnd.sp<entity>.v3+json` | `application/vnd.sb<entity>resource.v4+json` | `application/json` |
| 实体数量 | 6 个 list | 3 个 list | 6 个 list（含 creatives；不含 keywords） |
| 分页 | `nextToken` | `nextToken` + `totalCount` | `startIndex` + `count`（偏移分页） |
| `stateFilter` 实参 | 大写 ENUM | 大写 ENUM | 接口端要求小写串，脚本会自动转换 |
| 扩展字段 | `includeExtendedDataFields:true` 标志 | `includeExtendedDataFields:true` 标志 | 路径切换 `/sd/<entity>/extended` |
| Client-side filter | `asinFilter` / `skuFilter`（productAds） | 暂无 | `asinFilter` / `skuFilter`（productAds） |


