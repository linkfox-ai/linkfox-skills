


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
# Amazon Ads SP 洞察报告 API 参考

本 Skill 统一封装 Sponsored Products Audience 与 Search Term Impression Share/Rank 两类 Reporting API v1 beta 报告。

## 调用规范

- **请求地址**：LinkFox MCP，`toolName=amazonAds/developerProxy`
- **请求方式**：POST JSON
- **认证方式**：WorkBuddy 自动注入 Authorization；禁止传入凭证。
- **请求内容类型**：通过 `arguments.contentType` 指定；不得传 `headers`
- **默认网关**：`LinkFox MCP`
- **Amazon Token**：只传 `profileId`；后端选择并刷新 Token。禁止在参数中传入任何 Amazon 凭证
- **成熟度**：Reporting API v1 当前为 Amazon open beta
- **生成时间**：异步报告通常约 2–10 分钟，偶尔可能更久；每次状态查询由用户明确触发，不自动轮询

## 入口与参数

| 报告 | 入口 | 专用参考 |
|---|---|---|
| Sponsored Products Audience | `proxy_call` | `sp-audience-reporting-v1.md` |
| Sponsored Products Search Term Impression Share/Rank | `proxy_call` | `sp-search-impression-share-v1.md` |

共同业务输入为 `profileId`、`region`、`startDate`、`endDate`、`timeUnit`、`advertiserAccountId`。Audience 额外使用 `detailLevel`；Search Impression Share 不接受自定义维度或字段。旧 caller 的轮询控制项不得作为 `developerProxy` 业务参数；查询状态时直接构造 retrieve 请求并复用 `reportId`。

## 内部调用链

三个路径都通过同一 LinkFox `developerProxy` 转发：

1. `POST adsApi/v1/query/advertiserAccounts`：把 `profileId` 映射到唯一 `advertiserAccountId`。
2. `POST adsApi/v1/create/reports`：创建固定官方字段组合的 CSV 报告。
3. `POST adsApi/v1/retrieve/reports`：按 `reportId` 查询状态；完成响应可能包含 `completedReportParts[]` 资源。

Ads v1 请求不发送 `Amazon-Advertising-API-Scope`；`profileId` 仅供后端选择当前用户已授权的 Token。

## developerProxy 请求示例



三个阶段分别构造 `developerProxy` 调用。保留创建返回的 `reportId`；`PENDING` / `PROCESSING` 不是失败，等待用户后续明确请求后再查询同一报告。不得自动下载、落盘或生成本地预览。

## 错误

| 状态/错误 | 含义 | 处理 |
|---|---|---|
| 400 | 日期、字段组合或请求体非法 | 查看 `details`，修正一次后再调 |
| 401 | LinkFox Key 或 Amazon Token 失效 | LinkFox 401 走 onboarding；Amazon 401 刷新 Ads 授权 |
| 402 | LinkFox 套餐或余额问题 | 走 `references/onboarding.md` |
| 403 | v1 权限未开放 | 检查 Amazon Ads 应用和授权账号权限 |
| 404 | reportId 不存在或不可访问 | 不自动重建 |
| 429 | Amazon 限流 | 降低轮询频率，不密集重试 |
| `FAILED` | 报告生成失败 | 透传失败详情 |

## Feedback API

`POST https://skill-api.linkfox.com/api/v1/public/feedback`

```json
{"skillName":"linkfox-amazon-ads-sp-insights-report","sentiment":"NEUTRAL","category":"SUGGESTION","content":"..."}
```



## 响应字段表

来源：`skills/linkfox-amazon-ads-sp-insights-report/references/api.md`。其中成功/未完成示例属于旧 caller 合成输出，不纳入下游响应。来源未给出 advertiser-account、create、retrieve 三个 Amazon 响应体的完整固定嵌套。

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | number | developerProxy 下游 HTTP 状态 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 代理错误摘要 |
| `details` | string/object | 错误详情；来源未说明内部固定结构 |

来源明确提及的 Amazon 业务字段包括 `reportId`、`status`、`completedReportParts[]` 和分片 `url`，但未完整定义它们在 `body` 中的父对象和属性，故不将推测路径写入响应表。
