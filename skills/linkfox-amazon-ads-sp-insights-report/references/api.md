# Amazon Ads SP 洞察报告 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

### 网关错误响应

成功对象与错误对象分别判断。错误对象字段如下；本地调用器记录的传输状态与解析结果见脚本参考。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 网关错误码，HTTP 200 仍可能包含业务错误。 |
| errmsg | string | 错误说明，保留原文。 |

参数异常可返回 HTTP 400、errcode=400；上游连接异常可返回 HTTP 200、errcode=1503。1002用于缺参数、区域或路径不合法，1004用于授权记录不存在或不属于当前成员；1005可能是授权失效，也可能是路径或方法未放行，结合errmsg判断。受保护状态遵循账号保护规则，不连续试探。

代理通过profileId校验当前成员绑定并选择授权令牌。Ads v1的adsApi/v1/路径不发送Amazon-Advertising-API-Scope；其他可用路径以profileId作为该请求头。ClientId由上游代理注入。广告profile的查询与刷新使用授权技能的/amazonAds/profiles接口。

## 接口：查询 advertiser accounts

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `adsApi/v1/query/advertiserAccounts`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 同时查询 global 与 non-global 并跟随分页，按 profile 别名匹配，去重后必须恰好一个账号；零个或多个均停止，禁止默认第一个。
- 显式提供 `advertiserAccountId` 时跳过账号查询，仅用于映射失败后的恢复。

共用的业务错误及冷却处理见本文「错误与广告账号保护」。业务调用使用报告入口完成编排，直接调用本节接口不会自动完成整份报告。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "path": "adsApi/v1/query/advertiserAccounts",
  "method": "POST",
  "profileId": 1234567890,
  "body": "{}",
  "contentType": "application/json"
}'
```


## 接口：创建洞察报告

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `adsApi/v1/create/reports`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 创建成功必须取得非空 `reportId`；仅 HTTP 或网关成功不足以判为报告完成。
- Audience 保留币种依赖；Search Impression Share 保留三个非时间维度且不得附加不兼容维度，详见两类专用参考。
- 失败不自动换日期、账号或字段重建；结果不确定时先查询已有任务。

共用的业务错误及冷却处理见本文「错误与广告账号保护」。业务调用使用报告入口完成编排，直接调用本节接口不会自动完成整份报告。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "path": "adsApi/v1/create/reports",
  "method": "POST",
  "profileId": 1234567890,
  "body": "{\"accessRequestedAccounts\":[{\"advertiserAccountId\":\"ACCOUNT_ID\"}],\"reports\":[{\"format\":\"CSV\",\"periods\":[{\"datePeriod\":{\"startDate\":\"2026-08-01\",\"endDate\":\"2026-08-07\"}}],\"query\":{\"fields\":[\"date.value\",\"advertiserAccount.id\",\"adProduct.value\",\"searchTerm.value\",\"metric.impressionShare\",\"metric.impressionShareRank\"],\"filter\":{\"on\":{\"field\":\"adProduct.value\",\"comparisonOperator\":\"EQUALS\",\"not\":false,\"values\":[\"SPONSORED_PRODUCTS\"]}}}}]}",
  "contentType": "application/json"
}'
```


## 接口：查询洞察报告状态

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `adsApi/v1/retrieve/reports`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 查询响应须找到报告任务；完成状态后下载全部 plain CSV / gzip CSV 分片，任何分片失败清理本次已写分片，不返回部分成功。
- 客户端窗口结束返回本地 `STILL_PROCESSING`，不等于 Amazon FAILED；确认继续后按 `resumeHint.params` 和 `--no-cache` 续跑原 `reportId`。
- 成功且 `totalRows=0` 是合法空结果，不自动扩大日期、切换账号或重建；成功、失败及未完成的本地结构见下表。

共用的业务错误及冷却处理见本文「错误与广告账号保护」。业务调用使用报告入口完成编排，直接调用本节接口不会自动完成整份报告。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "path": "adsApi/v1/retrieve/reports",
  "method": "POST",
  "profileId": 1234567890,
  "body": "{\"reportIds\":[\"REPORT_ID\"]}",
  "contentType": "application/json"
}'
```

## 业务入口与运行约定

入口参数、调用示例与落盘约定见 [脚本使用](script-usage.md#业务入口与运行约定)。

## 本地工作流响应结构

本地加工输出见 [脚本结果](script-usage.md#本地工作流响应结构)。

## 错误与广告账号保护

| 状态 / 错误 | 含义 | 处理 |
|---|---|---|
| `Missing or invalid parameter` | profile、region 或创建日期缺失/非法 | 按专用参考补齐后再调。 |
| `Unsupported parameter(s)` | 非固定报告参数或维度 | 删除不支持参数，不绕过脚本。 |
| 400 | 日期、字段组合或 body 非法 | 看 `details.body`，修正一次后再调。 |
| 401 | LinkFox Key 或 Amazon Token 失效 | LinkFox 401 走 [onboarding](onboarding.md)；上游 401 由 Ads Auth 刷新。 |
| 402 | 余额、套餐或额度问题 | 走 [onboarding](onboarding.md)。 |
| 403 | Amazon v1 权限未开放 | 检查 Ads 应用、账号和授权权限，不用 v3 伪造。 |
| 404 | 任务不存在或不可访问 | 核对原 reportId、账号和区域，不自动重建。 |
| 429 | Amazon 限流 | 尊重 Retry-After，保持每分钟级轮询并降低频率，不密集重试。 |
| `FAILED` 及其他失败状态 | 报告生成失败 | 透传脱敏详情，不自动更换参数。 |
| `STILL_PROCESSING` | 客户端等待窗口耗尽 | 向用户确认后续跑原 reportId。 |
| `totalRows=0` | 成功空报告 | 合法空结果，不连续试探。 |
| exit 42 | Ads Auth 依赖缺失或检查失败 | 先安装/加载认证技能，不获取或传原始 Amazon 凭证。 |


同一广告账号/profile 连续收到 Amazon Ads API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大广告账号风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 广告账号/profile+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查 profileId、region、实体/报告 ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 广告账号/profile 全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该广告账号调用，检查 Ads 授权、应用权限、profile 归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 广告账号/profile+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属 profile/区域、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 广告账号/profile+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该广告账号/profile 全部 Ads API。
- 保留已有 `reportId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明广告账号保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊广告账号安全，检测到 Amazon Ads API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或积分限制。”不要只说“LinkFox 限流”或“服务器繁忙”。


## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-ads-sp-insights-report",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
