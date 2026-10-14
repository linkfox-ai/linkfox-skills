# linkfox-junglescout-keyword-by-keyword

## 功能与适用范围

从一个种子关键词拓展相关关键词，返回精确/广泛搜索量、月度/季度趋势、相关性、排名难度、自然/广告商品数和 PPC 出价。适用于关键词库扩充、长尾词发现、PPC 竞价研究和竞争度初筛。

每次仅接受一个 `searchTerms`；它不提供关键词历史时间序列、ASIN 反查、商品数据库筛选或广告执行。

## MCP 调用

- 响应字段来源：`skills/linkfox-junglescout-keyword-by-keyword/references/api.md`。仅从该文件核对并恢复下方响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`tool-jungle-scout/keywords/by-keyword`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errorCode` / `code` 与消息字段。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

## 请求参数

### 必填

| 参数 | 类型 | 说明 |
|---|---|---|
| `marketplace` | string | `us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`；默认 `us` |
| `searchTerms` | string | 单个种子关键词，按用户原意传入 |

### 可选

| 参数 | 类型 | 说明 |
|---|---|---|
| `needCount` | int | 返回结果总数 |
| `sort` | string | 默认 `-monthly_search_volume_exact` |
| `minMonthlySearchVolumeExact` / `maxMonthlySearchVolumeExact` | int | 精确搜索量下限/上限 |
| `minMonthlySearchVolumeBroad` / `maxMonthlySearchVolumeBroad` | int | 广泛搜索量下限/上限 |
| `minWordCount` / `maxWordCount` | int | 关键词词数范围；长尾词通常设 `minWordCount: 3` |
| `minOrganicProductCount` / `maxOrganicProductCount` | int | 自然排名商品数范围 |

排序字段支持 `name`、`dominant_category`、`monthly_trend`、`quarterly_trend`、`monthly_search_volume_exact`、`monthly_search_volume_broad`、`recommended_promotions`、`sp_brand_ad_bid`、`ppc_bid_broad`、`ppc_bid_exact`、`ease_of_ranking_score`、`relevancy_score`、`organic_product_count` 及前缀 `-` 的降序形式。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| keywordInfoList | array | 关键词信息列表 |

### keywordInfoList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 关键词名称 |
| country | string | 市场代码 |
| monthlySearchVolumeExact | integer | 月均精确匹配搜索量 |
| monthlySearchVolumeBroad | integer | 月均广泛匹配搜索量 |
| monthlyTrend | number | 月度搜索量变化百分比 |
| quarterlyTrend | number | 季度搜索量变化百分比 |
| dominantCategory | string | 搜索结果中占比最高的品类 |
| relevancyScore | integer | 与种子词的相关性评分 |
| easeOfRankingScore | integer | 排名容易度评分（越高越容易排名） |
| organicProductCount | integer | 自然排名商品数量 |
| sponsoredProductCount | integer | 广告商品数量 |
| ppcBidExact | number | 精确匹配 PPC 建议出价（美元） |
| ppcBidBroad | number | 广泛匹配 PPC 建议出价（美元） |
| spBrandAdBid | number | Sponsored Brand 广告建议出价（美元） |
| recommendedPromotions | integer | 推荐促销赠品数量 |

## MCP 参数示例

```json
{
  "toolName": "tool-jungle-scout/keywords/by-keyword",
  "arguments": {
    "marketplace": "us",
    "searchTerms": "yoga mat",
    "needCount": 20
  }
}
```

## 错误与展示

HTTP 200 仍检查 `errcode`/`errorCode`；`200` 解析 `keywordInfoList`，`401` 或授权错误、`402` 或余额错误读取 `references/onboarding.md`，其他错误根据 `errmsg` 修正必填字段、站点、筛选范围或排序值。错误示例：`{"errcode":401,"errmsg":"authorized error"}`。

业务成功需检查 `errcode` / `errorCode` / `code`，不得只依据代理层成功判断。

表格默认列出关键词、精确/广泛搜索量、月/季度趋势、PPC 出价和排名难度；趋势正值标 `↑`、负值标 `↓`，并说明结果排序与数量。月均搜索量是估算，不要当作实时搜索量或成交量。

## 反馈 API

反馈使用 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，请求 JSON 为 `skillName: linkfox-wb-jungle-scout`、`sentiment: POSITIVE|NEUTRAL|NEGATIVE`、`category: BUG|COMPLAINT|SUGGESTION|OTHER`、`content`。反馈 API 与工具网关分离；记录用户意图、实际结果和不匹配/建议/表扬原因即可。




