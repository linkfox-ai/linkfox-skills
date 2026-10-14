# TikTok 视频号授权 API

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`tiktokVideo/authorizeUrl`、`tiktokVideo/authorizedAccounts`、`tiktokVideo/accountTokens`、`tiktokVideo/refreshToken`
- `arguments` 直接使用各节请求对象；无参数时传 `{}`。不传 headers 或任何凭证。

先检查 MCP/`isError`，再将 text JSON 解析一次并读取下游字段。相同 `toolName + arguments` 不重复调用；失败、空响应或非理想结果不自动重试，不作 HTTP fallback。

## 1. 生成授权 URL

`toolName`：`tiktokVideo/authorizeUrl`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| displayName | string | 否 | 来源未说明 | 视频号展示名称，可选，最长 256 |
| region | string | 否 | `global` | `global` 或 `us` |

```json
{"toolName":"tiktokVideo/authorizeUrl","arguments":{"displayName":"My Channel","region":"global"}}
```

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| authorizeUrl | string | 用户在浏览器中打开的授权链接（有效期约 1 小时） |

每次重新获取授权 URL 都是新调用；用户在浏览器完成 OAuth 后再列出账号。

## 2. 列出授权账号

`toolName`：`tiktokVideo/authorizedAccounts`；请求参数：无。

```json
{"toolName":"tiktokVideo/authorizedAccounts","arguments":{}}
```

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| accounts | array | 已授权账号数组（来源示例和子字段表确认） |
| accounts[] | object | 单个已授权账号（来源示例确认） |
| accounts[].openId | string | 创作者 open_id |
| accounts[].displayName | string | 展示名称 |
| accounts[].region | string | 授权 region（global / us） |
| accounts[].userType | integer | 用户类型（如 1=创作者） |
| accounts[].grantedScopes | string | 已授权 scope 列表 JSON 字符串 |
| total | integer | 账号总数（来源示例确认；说明来源未说明） |

## 3. 查询账号令牌状态

`toolName`：`tiktokVideo/accountTokens`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| openId | string | 是 | 创作者 open_id，最长 128 |

```json
{"toolName":"tiktokVideo/accountTokens","arguments":{"openId":"<creator_open_id>"}}
```

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| authRecordId | integer | 授权主表 ID |
| openId | string | 创作者 open_id |
| accessToken | string | access_token（来源如此定义；不得展示或放入后续 `arguments`） |
| refreshToken | string | refresh_token（不得展示或放入后续 `arguments`） |
| accessTokenExpireIn | integer | access_token 过期 Unix 时间戳 |
| refreshTokenExpireIn | integer | refresh_token 过期 Unix 时间戳 |
| userType | integer | 用户类型 |
| grantedScopes | string | 已授权 scope 列表 JSON |

此能力仅用于必要的授权诊断/过期时间检查；输出必须掩码。

## 4. 刷新令牌

`toolName`：`tiktokVideo/refreshToken`。这是授权写操作，调用前确认 `openId`；失败不自动重试。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| openId | string | 是 | 创作者 open_id |

```json
{"toolName":"tiktokVideo/refreshToken","arguments":{"openId":"<creator_open_id>"}}
```

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| authRecordId | integer | 授权记录 ID |
| accessToken | string | 新的 access_token（不得展示或转传） |
| refreshToken | string | 新的 refresh_token（不得展示或转传） |
| accessTokenExpireIn | integer | access_token 过期 Unix 时间戳 |
| refreshTokenExpireIn | integer | refresh_token 过期 Unix 时间戳 |
| message | string | 说明信息 |

refresh token 过期后重新生成授权 URL。

## 错误与成本

MCP/认证/积分按 `onboarding.md` 分层。`1002` 为参数校验/登录上下文错误；`1003` 为上游服务或网络异常；`1004` 为授权记录不存在、不属于当前用户或缺少 refresh token；`1005` 仅适用于共享代理白名单。授权链接、账号查询、令牌查询和刷新分别计为独立调用；不自动重复。

## Feedback API（不迁移到 MCP）

用户明确反馈时可独立 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，字段为 `skillName`（`linkfox-tiktok-video-auth`）、`sentiment`、`category` 和 `content`。它不是 tool-gateway endpoint，不使用 `proxy_call`；失败不影响主流程且不自动重试。

## 响应字段来源

以上四组表仅据 `skills/linkfox-tiktok-video-auth/references/api.md` 的对应 Response 表与 JSON 示例恢复；示例补出的父数组、元素对象和 `total` 的说明标为来源未说明。
