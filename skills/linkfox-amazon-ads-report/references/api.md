# Amazon Ads 报告 接口说明

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

## 接口：创建广告报告

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `reporting/reports`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
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

- 创建使用上游 2xx 且 body 中存在 reportId；不能仅凭网关成功认定报告已生成。
- 上游 HTTP 425 且 detail 含 `The Request is a duplicate of : <uuid>` 时，自动提取原任务转入查询；无法解析则停止，不重复创建。
- 报告类型、列、分组、筛选和日期限制以 [类型目录](report-types/index.md) 链接的逐类型文档为单一真相源。默认构参与日期约束见 [运行规则](report-runtime.md)。

| 状态 / 退出码 | 含义 | 处理 |
|---|---|---|
| 上游 400 | 日期跨度超限、类型或参数非法 | 依据 detail 对照类型文档修正；超限按日期限制分段。 |
| 上游 401 | Ads 授权失效或服务端令牌异常 | 停止自动重试，检查授权，必要时重新授权；按 onboarding.md 的指引处理。 |
| 上游 402 | 算力或余额不足 | 按 onboarding.md 的指引处理。 |
| 上游 403 | 未关联广告账户或权限不足 | 核对 Ads 授权、profile 归属、region、经理账户与广告账户关联。 |
| 上游 404 | 任务不存在或过期 | 核对任务与归属；确需重建时遵守调用和保护规则，不自动重建。 |
| 上游 422 | columns / groupBy 不适配 | 对照类型文档基础指标、分组和 frontmatter 修正。 |
| 上游 429 | profile 限流，约 30 req/min/profile | 降频，建议间隔 30 秒；有保护码或 retryAfter/blockedUntil 时优先遵循保护规则。 |
| 450 / 453 / 454 / 459 | 网关账号保护 | 立即停调，按 [账号保护规则](report-runtime.md#账号保护与重试) 的阈值、冷却及修正后最多一次重试执行。453 期间停该 profile 全部 Ads API。 |
| exit 42 | 认证技能缺失 | 安装 linkfox-amazon-ads-auth，不绕过依赖取 token。 |
| exit 1 | 输入、网关、上游、下载或生成失败 | 如实展示保存的错误和 stderr，保留已有任务，不盲目重试。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "reporting/reports",
  "method": "POST",
  "contentType": "application/vnd.createasyncreportrequest.v3+json",
  "body": "{\"name\":\"SP 活动报告\",\"startDate\":\"2026-04-27\",\"endDate\":\"2026-05-03\",\"configuration\":{\"adProduct\":\"SPONSORED_PRODUCTS\",\"groupBy\":[\"campaign\"],\"columns\":[\"date\",\"campaignId\",\"campaignName\",\"impressions\",\"clicks\",\"cost\"],\"reportTypeId\":\"spCampaigns\",\"timeUnit\":\"DAILY\",\"format\":\"GZIP_JSON\"}}"
}'
```


## 接口：查询广告报告

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `reporting/reports/{reportId}`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`GET`；外层LinkFox请求始终POST。 |
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

- 上游非 2xx 不解析为查询成功；只有完成状态并有 url 才进入下载。生成失败须显示 failureReason。
- 等待耗尽输出 STILL_PROCESSING 并退出 2；这不是失败。保留任务，询问用户后用 resumeHint.params 恢复，不重新创建。
- 状态轮询不使用响应缓存，下载及临时访问服务规则见 [运行规则](report-runtime.md)。

| 状态 / 退出码 | 含义 | 处理 |
|---|---|---|
| 上游 400 | 日期跨度超限、类型或参数非法 | 依据 detail 对照类型文档修正；超限按日期限制分段。 |
| 上游 401 | Ads 授权失效或服务端令牌异常 | 停止自动重试，检查授权，必要时重新授权；按 onboarding.md 的指引处理。 |
| 上游 402 | 算力或余额不足 | 按 onboarding.md 的指引处理。 |
| 上游 403 | 未关联广告账户或权限不足 | 核对 Ads 授权、profile 归属、region、经理账户与广告账户关联。 |
| 上游 404 | 任务不存在或过期 | 核对任务与归属；确需重建时遵守调用和保护规则，不自动重建。 |
| 上游 422 | columns / groupBy 不适配 | 对照类型文档基础指标、分组和 frontmatter 修正。 |
| 上游 429 | profile 限流，约 30 req/min/profile | 降频，建议间隔 30 秒；有保护码或 retryAfter/blockedUntil 时优先遵循保护规则。 |
| 450 / 453 / 454 / 459 | 网关账号保护 | 立即停调，按 [账号保护规则](report-runtime.md#账号保护与重试) 的阈值、冷却及修正后最多一次重试执行。453 期间停该 profile 全部 Ads API。 |
| exit 42 | 认证技能缺失 | 安装 linkfox-amazon-ads-auth，不绕过依赖取 token。 |
| exit 1 | 输入、网关、上游、下载或生成失败 | 如实展示保存的错误和 stderr，保留已有任务，不盲目重试。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "reporting/reports/7df1ef5d-45ba-40cc-b607-ff2148cf4f5e",
  "method": "GET",
  "contentType": "application/json"
}'
```

---


## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-ads-report",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
