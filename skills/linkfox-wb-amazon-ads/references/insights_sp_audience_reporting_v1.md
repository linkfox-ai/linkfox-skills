


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
# Sponsored Products Audience（Reporting API v1）参考

## 调用规范

- **请求地址**：LinkFox MCP，`toolName=amazonAds/developerProxy`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：WorkBuddy 自动注入 Authorization；禁止传入凭证。
- **请求内容类型**：通过 `arguments.contentType` 指定；不得传 `headers`
- **默认生产网关**：`LinkFox MCP`
- **Amazon 认证**：只传 `profileId`；后端按 profile 选择 access token。参数中禁止出现 access token、refresh token 或 LWA 密钥
- **上游成熟度**：Amazon 官方当前把 Reporting API v1 标为 open beta；账号可能尚未开放，字段/限流可能调整，不应按 GA 稳定性承诺
- **生成时间**：异步报告通常约 2–10 分钟，偶尔可能更久；状态查询由用户明确触发，不自动轮询

入口：按本 reference 的 MCP 状态机调用。

## 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---:|---|---|
| `profileId` | integer/string | 是 | - | 正整数；来自 Ads 授权 Skill |
| `region` | string | 是 | - | `NA` / `EU` / `FE` |
| `startDate` | string | 创建模式是 | - | `YYYY-MM-DD` |
| `endDate` | string | 创建模式是 | - | `YYYY-MM-DD`；不得晚于今天 |
| `timeUnit` | string | 否 | `DAILY` | `DAILY` / `SUMMARY` |
| `detailLevel` | string | 否 | `ACCOUNT` | `ACCOUNT` / `CAMPAIGN` / `AD_GROUP` |
| `advertiserAccountId` | string | 否 | 自动映射 | Ads v1 account ID；仅用于映射失败后的显式恢复 |
| `reportId` | string | 查询阶段是 | - | 创建响应返回的 ID；用于构造 retrieve 请求 |

## 内部 Ads v1 调用链

三步均通过同一个 LinkFox `developerProxy` 转发；v1 请求不发送 `Amazon-Advertising-API-Scope`，`profileId` 只用于服务端选取授权记录/token。

### 1. 映射 advertiser account

`POST adsApi/v1/query/advertiserAccounts`

Agent 先查询 global accounts，再按需要用下面的 non-global filter 查询；若响应明确给出 `nextToken`，由用户决定是否继续查询下一页：

```json
{"isGlobalAccountFilter":{"include":[false]}}
```

从 `alternateIds` 中匹配当前 `profileId`，得到唯一 `advertiserAccountId`。若显式传入 `advertiserAccountId`，跳过本步。

### 2. 创建 SP Audience 报告

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
        "audienceSegment.id", "audienceSegment.name", "audienceSegment.type",
        "audienceSegment.classCode", "audienceSegment.source",
        "audienceSegmentCountry.code", "budgetCurrency.value",
        "metric.impressions", "metric.clicks",
        "metric.totalCost", "metric.purchases", "metric.sales", "metric.roas"
      ],
      "filter": {"on": {
        "field": "adProduct.value", "comparisonOperator": "EQUALS",
        "not": false, "values": ["SPONSORED_PRODUCTS"]
      }}
    }
  }]
}
```

`SUMMARY` 把 `date.value` 换成 `dateRange.value`。`CAMPAIGN` 增加 `campaign.id/name`；`AD_GROUP` 再增加 `adGroup.id/name`。`budgetCurrency.value` 是 `metric.totalCost` 与 `metric.sales` 的官方必需依赖，不能删除。

### 3. 轮询并下载

`POST adsApi/v1/retrieve/reports`

```json
{"reportIds":["REPORT_ID"]}
```

状态：`PENDING` / `PROCESSING` / `COMPLETED` / `FAILED`。完成响应中的 `completedReportParts[]` 可能包含多个 `url`，资源可能是 plain CSV 或 gzip-compressed CSV。

## developerProxy 请求示例

每一步都构造独立的 developerProxy 请求：

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

来源明确列出 `PENDING` / `PROCESSING` / `COMPLETED` / `FAILED`。前两者表示 Amazon 仍在生成；保存 `reportId`，等待用户后续明确请求后再调用 retrieve。完成响应可能有多个 `completedReportParts[]` 和预签名 `url`；不自动下载、生成本地文件清单、预览或缓存。

## 错误处理

| 状态/错误 | 含义 | 建议 |
|---|---|---|
| 400 | 日期、字段组合或 body 非法 | 查看 `details.body`，修正一次后再调 |
| 401 | LinkFox key 或 Amazon token 失效 | LinkFox 401 走 onboarding；上游 401 刷新 Ads 授权 |
| 402 | LinkFox 余额/套餐问题 | 走 `references/onboarding.md` |
| 403 | Amazon Ads v1 权限不足 | 检查 Ads API 应用/授权账户权限 |
| 404 | reportId 不存在/不可访问 | 不自动重建；向用户说明 |
| 429 | 上游限流 | 尊重 Retry-After/降低轮询频率，不密集重试 |
| `FAILED` | Amazon 报告生成失败 | 透传失败详情 |

## 官方参考

- [Reporting API v1 overview](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/overview)
- [Reporting API v1 quickstart](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/quickstart)
- [Query advertiser accounts](https://advertising.amazon.com/API/docs/en-us/guides/account-management/query-advertiser-accounts)
- [Audience segment dimension](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/dimensions/audience/audience-segment)
- [Costs metrics: total cost](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/metrics/costs-and-fees/costs#total-cost)
- [Purchase metrics: sales and ROAS](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/metrics/amazon-retail-conversions/purchases#sales)

## Feedback API

此端点与工具网关不同：`POST https://skill-api.linkfox.com/api/v1/public/feedback`。

```json
{"skillName":"linkfox-amazon-ads-sp-insights-report","sentiment":"NEUTRAL","category":"SUGGESTION","content":"..."}
```



## 响应字段表

来源：`skills/linkfox-amazon-ads-sp-insights-report/references/sp-audience-reporting-v1.md`。来源成功/未完成示例是旧 caller 合成输出，不纳入。Amazon 三阶段响应的完整父对象和属性来源未说明。

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | number | developerProxy 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 代理错误摘要 |
| `details` | string/object | 错误详情；来源未说明内部固定结构 |

来源只明确提及 `reportId`、`status`、`completedReportParts[]`、`url`，未完整定义它们在 `body` 内的父对象，故不推测字段路径。
