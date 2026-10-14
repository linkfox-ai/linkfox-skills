# linkfox-junglescout-keyword-by-asin

## 功能与适用范围

根据一个或多个亚马逊 ASIN 反查其出现的关键词，返回关键词搜索量、月/季度趋势、自然与广告排名、相关度、排名难度、PPC 出价和竞品排名详情。适用于竞品流量词挖掘、多个 ASIN 关键词对比、广告关键词参考和关键词拓展起点。

每次最多查询 10 个 ASIN；一次调用只能针对一个 Amazon 站点。它不提供种子词拓展、历史搜索量时间序列、实时排名、商品销量或广告投放执行。

## MCP 调用

- 响应字段来源：`skills/linkfox-junglescout-keyword-by-asin/references/api.md`。仅从该文件核对并恢复下方响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`tool-jungle-scout/keywords/by-asin`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errorCode` / `code` 与消息字段。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

## 请求参数

### 必填参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `marketplace` | string | `us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`；未指定时使用 `us` |
| `asins` | array<string> | ASIN 数组，最多 10 个；应使用标准 10 位 ASIN |

### 可选参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `needCount` | int | 返回总数，后端自动分页 |
| `includeVariants` | boolean | 是否包含变体商品的关键词 |
| `sort` | string | 排序字段；默认 `-monthly_search_volume_exact` |
| `minMonthlySearchVolumeExact` / `maxMonthlySearchVolumeExact` | int | 精确搜索量范围，1–999999 |
| `minMonthlySearchVolumeBroad` / `maxMonthlySearchVolumeBroad` | int | 广泛搜索量范围，1–999999 |
| `minWordCount` / `maxWordCount` | int | 关键词单词数范围，1–99999 |
| `minOrganicProductCount` / `maxOrganicProductCount` | int | 自然搜索结果数范围，1–99999 |

`sort` 可使用 `name`、`dominant_category`、`monthly_trend`、`quarterly_trend`、`monthly_search_volume_exact`、`monthly_search_volume_broad`、`recommended_promotions`、`sp_brand_ad_bid`、`ppc_bid_broad`、`ppc_bid_exact`、`ease_of_ranking_score`、`relevancy_score`、`organic_product_count` 及各自的 `-` 降序形式。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| keywordInfoList | array | 关键词信息列表 |

### keywordInfoList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 关键词 |
| country | string | 市场代码 |
| monthlySearchVolumeExact | integer | 月精确匹配搜索量 |
| monthlySearchVolumeBroad | integer | 月广泛匹配搜索量 |
| monthlyTrend | float | 月环比趋势（%） |
| quarterlyTrend | float | 季度趋势（%） |
| dominantCategory | string | 主要类目 |
| relevancyScore | integer | 关键词与 ASIN 的相关度（0-100） |
| easeOfRankingScore | integer | 排名容易程度（0-100，越高越容易排名） |
| organicRank | integer | ASIN 的自然搜索排名 |
| sponsoredRank | integer | ASIN 的广告排名 |
| overallRank | integer | 综合排名位置 |
| organicProductCount | integer | 自然搜索结果中的商品总数 |
| sponsoredProductCount | integer | 广告位商品总数 |
| ppcBidExact | float | 精确匹配 PPC 建议出价（USD） |
| ppcBidBroad | float | 广泛匹配 PPC 建议出价（USD） |
| spBrandAdBid | float | SP 品牌广告建议出价（USD） |
| recommendedPromotions | integer | 推荐促销量 |
| primaryAsin | string | 该关键词下排名最高的 ASIN |
| relativeOrganicPosition | float | 查询 ASIN 的自然排名相对位置 |
| relativeSponsoredPosition | float | 查询 ASIN 的广告排名相对位置 |
| organicRankingAsinsCount | integer | 有自然排名的查询 ASIN 数量 |
| sponsoredRankingAsinsCount | integer | 有广告排名的查询 ASIN 数量 |
| avgCompetitorOrganicRank | float | 查询 ASIN 的平均自然排名 |
| avgCompetitorSponsoredRank | float | 查询 ASIN 的平均广告排名 |
| variationLowestOrganicRank | integer | 变体中最佳自然排名 |
| variationLowestSponsoredRank | integer | 变体中最佳广告排名 |
| competitorOrganicRank | array | 各 ASIN 的自然排名，元素为 `{asin, organicRank}` |
| competitorSponsoredRank | array | 各 ASIN 的广告排名，元素为 `{asin, sponsoredRank}` |
| updatedAt | string | 数据最后更新时间 |

### `keywordInfoList[].competitorOrganicRank[]` 对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `keywordInfoList[].competitorOrganicRank[].asin` | string | ASIN；类型由来源响应示例确认 |
| `keywordInfoList[].competitorOrganicRank[].organicRank` | integer | 自然搜索排名；类型由来源响应示例确认 |

### `keywordInfoList[].competitorSponsoredRank[]` 对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `keywordInfoList[].competitorSponsoredRank[].asin` | string | ASIN；类型由来源响应示例确认 |
| `keywordInfoList[].competitorSponsoredRank[].sponsoredRank` | integer | 广告排名；类型由来源响应示例确认 |

## MCP 参数示例

```json
{
  "toolName": "tool-jungle-scout/keywords/by-asin",
  "arguments": {
    "marketplace": "us",
    "asins": [
      "B0D1234567"
    ],
    "needCount": 50
  }
}
```

## 错误与展示

正常响应 HTTP 200 时仍需检查业务 `errcode`/`errorCode`。`200` 解析 `keywordInfoList`；`401` 或 `authorized error` 转到 `references/onboarding.md`；`402` 或余额不足转到 onboarding；其他值读取 `errmsg`，检查 ASIN 数量/格式、站点代码、范围和排序字段。错误示例：`{"errcode":401,"errmsg":"authorized error"}`。

业务成功需检查 `errcode` / `errorCode` / `code`，不得只依据代理层成功判断。

表格至少展示关键词、精确搜索量、自然排名、广告排名、相关度和 PPC 出价；自然排名前 10、广告排名前 5 可高亮，正/负趋势分别标记上升/下降。多个 ASIN 时按 ASIN 展示排名对比，不把 `0` 或 `-1` 当成真实值。

## 反馈 API

若用户指出结果不准确、能力不匹配、报错、提出建议或表达满意，按反馈 API 记录，不中断当前任务：`POST https://skill-api.linkfox.com/api/v1/public/feedback`，JSON 字段为 `skillName`（使用 `linkfox-wb-jungle-scout`）、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和 `content`（记录意图、实际结果及问题/表扬原因）。该地址与工具网关分离，不要混用。




