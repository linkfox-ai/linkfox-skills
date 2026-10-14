# Amazon Ads Manager API 总览

来源响应契约：`skills/linkfox-amazon-ads-manager/references/api.md` 及 `references/api/{sp,sd,sb-v3,sb-v4}.md`。来源中的旧脚本输出、分页聚合和本地过滤不是 `amazonAds/developerProxy` 的下游响应，本 reference 不保留这些行为。

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`amazonAds/developerProxy`
- `arguments` 直接传 `region`、`profileId`、`path`、`method`、可选 `body` / `contentType`，不得额外包裹。
- WorkBuddy 自动注入 Authorization；禁止传入 `headers`、API Key、token 或 JWT，禁止 HTTP fallback。
- 相同 `toolName + arguments` 不重复调用。写操作必须先获得用户对具体对象和动作的明确确认，结果不明确时不得自动重放。

```json
{"toolName":"amazonAds/developerProxy","arguments":{"region":"NA","profileId":1234567890,"path":"sp/campaigns/list","method":"POST","body":"{}","contentType":"application/vnd.spCampaign.v3+json"}}
```

## 产品 reference

| 广告产品 | 业务 reference | 说明 |
|---|---|---|
| Sponsored Products v3 | `manager_api_sp.md` | Campaign、Ad Group、Keyword、Target、Product Ad、Negative Target |
| Sponsored Brands V3/V4 | `manager_api_sb.md`、`manager_api_sb_v3.md`、`manager_api_sb_v4.md`、`manager_api_sb_coexistence.md` | Legacy 与 Multi-Ad-Group 路径必须显式选择 |
| Sponsored Display v3 | `manager_api_sd.md` | Campaign、Ad Group、Target、Negative Target、Product Ad、Budget Rule |

Sponsored Television 和 Amazon DSP 不在范围内。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `region` | string | 是 | `NA` / `EU` / `FE` |
| `profileId` | number | 是 | 来自 Ads 授权结果 |
| `path` | string | 是 | 对应产品 reference 中的 Amazon Ads 相对路径，不带前导 `/` |
| `method` | string | 是 | 路径规定的 `GET` / `POST` / `PUT` |
| `body` | string | 依操作 | Amazon 原生 JSON 请求体序列化后的字符串；无请求体时传空字符串 |
| `contentType` | string | 依操作 | 对应资源版本的 Amazon media type 或 `application/json` |

旧脚本的自动分页、依赖检查、客户端过滤和参数转换项不得放进 `proxy_call.arguments`。分页 token、过滤器和资源 payload 必须按具体 Amazon 路径的原生请求结构传递；来源没有给出完整结构时标记“来源未说明”，不得推导。

## 响应字段

`proxy_call` 的 text content 为下游 JSON 字符串时只解析一次。来源没有给出 `developerProxy` 对各 Amazon 资源响应体的完整固定 schema，因此只记录来源明确的代理包装；`body` 内部按本次 Amazon 响应原样处理，不从旧 caller 输出推导字段。

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | 下游 Amazon HTTP 状态；来源明确出现 |
| `body` | string/object | Amazon 原始响应体；完整嵌套属性来源未说明 |
| `error` | string | 代理错误摘要；失败时可能出现 |
| `details` | string/object | 错误详情；来源未说明固定内部结构 |

实体字段表只表示来源明确列出的 Amazon 业务字段，不承诺完整 schema，也不代表 `developerProxy` 会额外生成实体数组、`total`、`pagesFetched` 或 `truncated`。

## 错误处理

| 状态 | 处理 |
|---|---|
| MCP `isError=true`、连接或 schema 错误 | 展示 MCP 错误并停止，不改走 HTTP |
| 400 | 核对 path、method、media type、过滤器或 payload，不自动换参数重试 |
| 401 | 按 `onboarding.md` 区分 WorkBuddy 授权和 Amazon Ads 授权 |
| 402 | 按 `onboarding.md` 处理积分或余额不足 |
| 403 | 核对 profile 权限及资源版本 |
| 404 | 核对资源路径和 ID，不猜测替代路径 |
| 409/422 | 展示业务冲突或校验详情；写操作不自动重放 |
| 429 | 尊重返回的限流信息，取得用户同意后再发起新的收费调用 |

## Feedback API

Feedback 与业务 MCP 分离：`POST https://skill-api.linkfox.com/api/v1/public/feedback`。

- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content` 不得包含凭证、完整广告 payload 或其他敏感信息。
