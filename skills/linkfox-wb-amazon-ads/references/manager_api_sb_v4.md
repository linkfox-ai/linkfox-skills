# Sponsored Brands V4 API

来源：`skills/linkfox-amazon-ads-manager/references/api/sb-v4.md`。V4 是默认版本，支持 Legacy 与 Multi-Ad-Group Campaign。

## MCP 调用

使用 `LinkFox.proxy_call`，精确 `toolName=amazonAds/developerProxy`。直接传 developerProxy 路由对象，WorkBuddy 自动授权，禁止 headers、token 和 HTTP fallback。

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"sb/v4/campaigns/list","method":"POST","body":"{}","contentType":"application/vnd.sbcampaignresource.v4+json"}}
```

## 资源路径

| 资源 | Amazon 路径 | 说明 |
|---|---|---|
| Campaign | `sb/v4/campaigns[/list]` | V4 create/update/list |
| Ad Group | `sb/v4/adGroups[/list]` | V4 create/update/list |
| Ad | `sb/v4/ads[/list]`、`sb/v4/ads/{adType}` | create 时必须提供来源列出的 `adType` |
| Keyword | `sb/keywords` | Amazon 共享 targeting transport，不存在 `sb/v4/keywords` |
| Target | `sb/targets[/list]` | Amazon 共享 V3/V3.2 transport，不存在 `sb/v4/targets` |
| Creative Version | `sb/ads/creatives/...` | 独立 Creative Version |
| Budget Rule | `sb/budgetRules` | list/create/update |

Ad type：`autoCollection`、`manualCollection`、`brandVideo`、`video`、`productCollection`、`productCollectionExtended`、`storeSpotlight`。Creative type：`productCollection`、`productCollectionExtended`、`storeSpotlight`、`video`、`brandVideo`。

Campaign/Ad Group/Ad list 的分页字段包括来源明确提到的 `nextToken`，部分响应可能有 `totalCount`；请求和返回的准确嵌套来源未完整定义，不得推导。旧 caller 的 filter 映射、自动分页聚合和 `total` 不属于 MCP。

## 响应字段

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | Amazon 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 失败时的错误摘要 |
| `details` | string/object | 错误详情；内部结构来源未说明 |
