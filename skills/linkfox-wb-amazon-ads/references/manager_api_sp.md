# Sponsored Products v3 实体管理

来源：`skills/linkfox-amazon-ads-manager/references/api/sp.md`。来源列出的旧脚本过滤、自动分页、本地 ASIN/SKU 过滤及合成输出不属于 `developerProxy`。

## MCP 调用

统一使用 `LinkFox.proxy_call`，精确 `toolName=amazonAds/developerProxy`。`arguments` 直接传 `region`、`profileId`、`path`、`method`、可选 `body` / `contentType`。WorkBuddy 自动授权；禁止 headers、token 和 HTTP fallback。写操作先确认，同参数不重复调用。

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"sp/campaigns/list","method":"POST","body":"{}","contentType":"application/vnd.spCampaign.v3+json"}}
```

## 资源路径

| 实体 | list 路径 | 来源明确的常见字段 |
|---|---|---|
| Campaign | `sp/campaigns/list` | `campaignId`、`name`、`state`、`targetingType`、`budget`、`startDate`、`endDate`、`dynamicBidding`、`portfolioId` |
| Ad Group | `sp/adGroups/list` | `adGroupId`、`campaignId`、`name`、`state`、`defaultBid` |
| Keyword | `sp/keywords/list` | `keywordId`、`adGroupId`、`campaignId`、`keywordText`、`matchType`、`state`、`bid` |
| Negative Keyword | `sp/negativeKeywords/list` | 与 Keyword 相同；`matchType` 为 `NEGATIVE_EXACT` / `NEGATIVE_PHRASE` |
| Product Ad | `sp/productAds/list` | `adId`、`adGroupId`、`campaignId`、`asin`、`sku`、`state` |
| Target | `sp/targets/list` | `targetId`、`adGroupId`、`campaignId`、`state`、`expression`、`expressionType`、`bid` |

create/update/archive 的准确路径、method、media type 和 Amazon 原生 payload 以来源相应操作为准。来源没有提供完整请求或响应 schema 时不得猜测。`asinFilter` / `skuFilter` 是旧脚本的本地过滤能力，不得传给 `developerProxy`；需要筛选时使用 Amazon 路径真实支持的过滤器或在返回后由 Agent 显式筛选。

## 响应字段

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | Amazon 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 失败时的错误摘要 |
| `details` | string/object | 错误详情；内部结构来源未说明 |

上表不承诺旧 caller 的实体 key、`total`、`pagesFetched`、`truncated`、`serverTotalBeforeClientFilter` 或 `clientSideFilters`。
