# Sponsored Display v3 实体管理

来源：`skills/linkfox-amazon-ads-manager/references/api/sd.md`。来源列出的旧脚本宽容入参、参数提示、本地过滤和分页聚合均不属于 `developerProxy`。

## MCP 调用

统一使用 `LinkFox.proxy_call`，精确 `toolName=amazonAds/developerProxy`。`arguments` 直接传 `region`、`profileId`、`path`、`method`、可选 `body` / `contentType`。WorkBuddy 自动授权；禁止 headers、token 和 HTTP fallback。写操作先确认，同参数不重复调用。

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"sd/campaigns","method":"GET","body":"","contentType":"application/json"}}
```

## 资源路径

| 实体 | 基础路径 | 来源明确的常见字段 |
|---|---|---|
| Campaign | `sd/campaigns` | `campaignId`、`name`、`state`、`tactic`、`costType`、`budget`、`budgetType`、`startDate`、`endDate`、`portfolioId` |
| Ad Group | `sd/adGroups` | `adGroupId`、`campaignId`、`name`、`state`、`defaultBid`、`bidOptimization`、`creativeType` |
| Product Ad | `sd/productAds` | `adId`、`adGroupId`、`campaignId`、`state`、`asin`、`sku`、`landingPageURL`、`landingPageType` |
| Target | `sd/targets` | `targetId`、`adGroupId`、`campaignId`、`state`、`expressionType`、`expression`、`bid` |
| Negative Target | `sd/negativeTargets` | `targetId`、`adGroupId`、`campaignId`、`state`、`expression` |
| Creative | `sd/creatives` | `creativeId`、`adGroupId`、`name`、`creativeType`、`properties`、`moderationStatus` |

SD list 使用 GET/query string 和 `startIndex` + `count`；扩展字段由对应 `/extended` 路径提供，Creative 没有 extended 路径。状态值按 Amazon 端要求使用小写串。SD 没有 keyword 资源。

旧脚本的自动分页、扩展路径切换、依赖检查、宽容 `include` 形态、BROAD 到 EXACT 转换以及 ASIN/SKU 本地过滤不得传入。只使用具体 Amazon 路径原生支持的 query 参数。

## 响应字段

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | Amazon 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 失败时的错误摘要 |
| `details` | string/object | 错误详情；内部结构来源未说明 |

不承诺旧 caller 的实体 key、分页聚合、本地过滤摘要或参数转换结果。
