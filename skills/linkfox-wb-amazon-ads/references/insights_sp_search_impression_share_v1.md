


## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`amazonAds/developerProxy`
- `arguments` 直接传共享代理业务对象，保留 `region`、`profileId`、`path`、`method`、`body`、`contentType`；不得额外包裹。
- WorkBuddy 自动注入 Authorization；禁止 `headers`、API Key、token 或 JWT。禁止 HTTP fallback。
- 同一任务相同 `toolName + arguments` 不重复调用。失败、空结果和未完成状态不自动重建报告。
- 先检查 MCP schema、`isError` 和代理错误；text JSON 只解析一次，再检查 `httpStatus` / `body` 及 Amazon 状态。

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"adsApi/v1/retrieve/reports","method":"POST","body":"{\"reportIds\":[\"REPORT_ID\"]}","contentType":"application/json"}}
```
# Sponsored Products Search Term Impression Share（Reporting API v1）参考

## 调用规范

- **请求地址**：LinkFox MCP，`toolName=amazonAds/developerProxy`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：WorkBuddy 自动注入 Authorization；禁止传入凭证。
- **请求内容类型**：通过 `arguments.contentType` 指定；不得传 `headers`
- **默认生产网关**：`LinkFox MCP`
- **Amazon 认证**：只传 `profileId`；后端选择 token。参数中禁止出现 access/refresh token
- **上游成熟度**：Amazon 官方当前把 Reporting API v1 标为 open beta；账号可能尚未开放，字段/限流可能调整，不应按 GA 稳定性承诺
- **生成时间**：异步报告通常约 2–10 分钟，Search Impression Share 偶尔可能更久；状态查询由用户明确触发，不自动轮询

入口：按本 reference 的 MCP 状态机调用。

## 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---:|---|---|
| `profileId` | integer/string | 是 | - | 正整数；来自 Ads 授权 Skill |
| `region` | string | 是 | - | `NA` / `EU` / `FE` |
| `startDate` | string | 创建模式是 | - | `YYYY-MM-DD` |
| `endDate` | string | 创建模式是 | - | `YYYY-MM-DD`；不得晚于今天 |
| `timeUnit` | string | 否 | `DAILY` | `DAILY` / `SUMMARY` |
| `advertiserAccountId` | string | 否 | 自动映射 | Ads v1 account ID；仅用于映射失败后的显式恢复 |
| `reportId` | string | 查询阶段是 | - | 创建响应返回的 ID；用于构造 retrieve 请求 |

本报告入口不接受 campaign/adGroup/target/keyword 等自定义维度，因为它们与 impression share/rank 的官方字段兼容规则冲突。

## 内部 Ads v1 调用链

所有调用均经 LinkFox MCP 的 `amazonAds/developerProxy` 转发。Ads v1 不发送 `Amazon-Advertising-API-Scope`；`profileId` 只用于后端选取授权记录/token。

### 1. 映射 advertiser account

`POST adsApi/v1/query/advertiserAccounts`

依次查询 `{}` 和 `{"isGlobalAccountFilter":{"include":[false]}}`，跟随 `nextToken`，从 `alternateIds` 匹配当前 profile，得到唯一 `advertiserAccountId`。

### 2. 创建 SP Search Term Impression Share 报告

`POST adsApi/v1/create/reports`

```json
{
  "accessRequestedAccounts": [{"advertiserAccountId": "ACCOUNT_ID"}],
  "reports": [{
    "format": "CSV",
    "periods": [{"datePeriod": {"startDate": "2026-08-01", "endDate": "2026-08-07"}}],
    "query": {
      "fields": [
        "date.value", "advertiserAccount.id", "adProduct.value",
        "searchTerm.value", "metric.impressionShare", "metric.impressionShareRank"
      ],
      "filter": {"on": {
        "field": "adProduct.value", "comparisonOperator": "EQUALS",
        "not": false, "values": ["SPONSORED_PRODUCTS"]
      }}
    }
  }]
}
```

`SUMMARY` 把 `date.value` 换成 `dateRange.value`。三个非时间维度是 impression share/rank 的官方必需字段，不能删；也不能追加 campaign/ad group/target。

### 3. 轮询并下载

`POST adsApi/v1/retrieve/reports`

```json
{"reportIds":["REPORT_ID"]}
```

按官方建议最多每分钟轮询。`COMPLETED` 后下载全部 `completedReportParts[].url`，支持 plain CSV 和 gzip-compressed CSV；预签名 URL 不输出。

## developerProxy 请求示例

```json
{
  "region": "NA",
  "path": "adsApi/v1/create/reports",
  "method": "POST",
  "profileId": 1234567890,
  "body": "{...Amazon JSON body...}",
  "contentType": "application/json"
}
```

## 异步响应处理

来源明确列出 `PENDING` / `PROCESSING` / `COMPLETED` / `FAILED`。前两者表示 Amazon 仍在生成；保存 `reportId`，等待用户后续明确请求后再调用 retrieve。完成响应可能有多个 `completedReportParts[]` 和预签名 `url`；不自动下载、生成本地文件清单、预览或缓存。空 CSV 是合法空报告，不自动扩大日期或更换账号重试。

## 错误处理

| 状态/错误 | 含义 | 建议 |
|---|---|---|
| 400 | 日期或字段组合非法 | 查看 `details.body`，不添加不兼容维度 |
| 401 | LinkFox key 或 Amazon token 失效 | LinkFox 401 走 onboarding；上游 401 刷新 Ads 授权 |
| 402 | LinkFox 余额/套餐问题 | 走 `references/onboarding.md` |
| 403 | Amazon Ads v1 权限不足 | 检查 Ads API 应用/授权账户权限 |
| 404 | reportId 不存在/不可访问 | 不自动重建 |
| 429 | 上游限流 | 降低轮询频率，不密集重试 |
| `FAILED` | Amazon 报告生成失败 | 透传失败详情 |

## 官方参考

- [Reporting API v1 overview](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/overview)
- [Reporting API v1 quickstart](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/quickstart)
- [Query advertiser accounts](https://advertising.amazon.com/API/docs/en-us/guides/account-management/query-advertiser-accounts)
- [Search term dimension](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/dimensions/targeting/search-term)
- [Search impression share metrics](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/metrics/impression-share/search)

## Feedback API

此端点与工具网关不同：`POST https://skill-api.linkfox.com/api/v1/public/feedback`。

```json
{"skillName":"linkfox-amazon-ads-sp-insights-report","sentiment":"NEUTRAL","category":"SUGGESTION","content":"..."}
```



## 响应字段表

来源：`skills/linkfox-amazon-ads-sp-insights-report/references/sp-search-impression-share-v1.md`。来源成功/未完成示例是旧 caller 合成输出，不纳入。Amazon 三阶段响应的完整父对象和属性来源未说明。

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | number | developerProxy 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 代理错误摘要 |
| `details` | string/object | 错误详情；来源未说明内部固定结构 |

来源只明确提及 `reportId`、`status`、`completedReportParts[]`、`url`，未完整定义它们在 `body` 内的父对象，故不推测字段路径。
