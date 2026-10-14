# Amazon Ads 授权 API

来源响应契约：`skills/linkfox-amazon-ads-auth/references/api.md`，由以下五个精确 endpoint 与原调用脚本确认。

## MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- WorkBuddy 自动注入 Authorization；禁止传 `headers`、API Key、token、JWT 或手机号。
- `arguments` 直接使用各操作的请求对象；无参数也传 `{}`。
- 禁止 HTTP fallback。同一任务内相同 `toolName + arguments` 不重复调用；失败或空结果不自动重试。
- 先检查 MCP/代理错误；代理成功后，text JSON 只解析一次，再检查下游 `errcode` / `errmsg`。

## ID 关系

一次 OAuth 授权记录 `authRecordId` 可对应多个 marketplace `profileId`；`accountInfoId` 是跨 marketplace 的广告主 entity 标识。业务管理和报告使用 `profileId + region`。

## 1. 生成授权 URL

- `toolName`：`amazonAds/authorizeUrl`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `region` | string | 是 | `NA` / `EU` / `FE` |
| `accountName` | string | 是 | 非空账户显示名 |

```json
{"toolName":"amazonAds/authorizeUrl","arguments":{"region":"NA","accountName":"我的美国广告账号"}}
```

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `authorizeUrl` | string | Amazon LWA 授权 URL |
| `sourceType` | string | 来源类型；示例为 `amazon_ads` |

OAuth 回调由系统内部处理，不是公开接口。

## 2. 列已授权账号

- `toolName`：`amazonAds/authorizedStores`
- 请求参数：无，`arguments` 必须为 `{}`。

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | number | 账号×marketplace 记录数 |
| `stores` | array | 已授权记录数组 |
| `stores[].profileId` | number | marketplace profile ID |
| `stores[].accountInfoId` | string | 广告主 entity ID |
| `stores[].accountInfoName` | string | 广告主名称 |
| `stores[].accountType` | string | `seller` / `vendor` / `agency` |
| `stores[].countryCode` | string | 国家代码 |
| `stores[].marketplaceStringId` | string | marketplace 字符串 ID |
| `stores[].region` | string | `NA` / `EU` / `FE` |
| `stores[].authRecordId` | number | 授权记录 ID |
| `stores[].accountName` | string | 授权时设置的账户显示名 |

## 3. 列 profile

- `toolName`：`amazonAds/profiles`

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `refresh` | boolean | 否 | `false` | `true` 时穿透上游刷新；`false` 读快照 |

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | number | profile 数量 |
| `refreshed` | boolean | 是否执行上游刷新 |
| `profiles` | array | profile 数组 |
| `profiles[].profileId` | number | profile ID |
| `profiles[].region` | string | 区域 |
| `profiles[].countryCode` | string | 国家代码 |
| `profiles[].currencyCode` | string | 币种代码 |
| `profiles[].dailyBudget` | string | 日预算 |
| `profiles[].timezone` | string | 时区 |
| `profiles[].accountInfoId` | string | 广告主 entity ID |
| `profiles[].accountInfoType` | string | 广告主类型 |
| `profiles[].accountInfoName` | string | 广告主名称 |
| `profiles[].marketplaceStringId` | string | marketplace 字符串 ID |
| `profiles[].authRecordId` | number | 授权记录 ID |

## 4. 刷新令牌

- `toolName`：`amazonAds/refreshToken`
- `authRecordId` 与 `profileId` 二选一。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `authRecordId` | number | 条件必填 | 授权记录 ID |
| `profileId` | number | 条件必填 | 系统反查所属授权 |

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `authRecordId` | number | 授权记录 ID |
| `accessToken` | string | 敏感凭证；不得向用户展示或用于业务 arguments |
| `refreshToken` | string | 敏感凭证；不得向用户展示或用于业务 arguments |
| `tokenType` | string | token 类型 |
| `expiresIn` | string | 有效期秒数 |
| `message` | string | 刷新结果消息 |

## 5. 查询令牌状态

- `toolName`：`amazonAds/storeTokens`
- `authRecordId` 与 `profileId` 二选一；本操作不刷新，只读数据库。

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `authRecordId` | number | 授权记录 ID |
| `accessToken` | string | 敏感凭证；不得展示 |
| `refreshToken` | string | 敏感凭证；不得展示 |
| `tokenType` | string | token 类型 |
| `expiresIn` | string | 有效期秒数 |

## 错误响应

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | number | 业务错误码 |
| `errmsg` | string | 业务错误消息 |

| errcode | 含义 | 处理 |
|---|---|---|
| 200 | 成功 | 读取对应响应表 |
| 401 | 授权失败 | 按 `onboarding.md` 分层处理 |
| 402 | 积分不足 | 访问 `https://agent.linkfox.com/`，不自动购买 |
| 1002 | 缺参数或认证失败 | 核对必填参数；不得要求手工 MCP Authorization |
| 1003 | Amazon Ads 上游失败 | 透传，不自动重试 |
| 1004 | 授权记录不存在或不属于当前用户 | 核对 ID |
| 1005 | profile 权限校验失败 | 核对 profile 归属 |

## Feedback API

Feedback 使用独立的 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，不通过 `proxy_call`；仅在用户明确要求时调用。
