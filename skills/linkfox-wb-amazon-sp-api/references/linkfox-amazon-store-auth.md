# Amazon 店铺授权与管理

## MCP 调用与响应

WorkBuddy 自动注入 Authorization；禁止传 `headers`、API Key、token、JWT、手机号或其他凭证。五个 `toolName` 均精确匹配且区分大小写。失败不自动重试，相同 `toolName + arguments` 不重复调用；错误按 MCP、代理、下游业务三层处理，text JSON 只解析一次。

### `spApi/authorizeUrl`

请求：`region`（NA/EU/FE，必填）、`sellerName`（非空，必填）。

```json
{"toolName":"spApi/authorizeUrl","arguments":{"region":"NA","sellerName":"My Store"}}
```

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `authorizeUrl` | string | Amazon 授权链接 |

### `spApi/authorizedStores`

```json
{"toolName":"spApi/authorizedStores","arguments":{}}
```

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `stores` | array | 授权店铺数组 |
| `stores[].sellerName` | string | 店铺展示名 |
| `stores[].sellerId` | string | Seller ID |
| `stores[].region` | string | NA/EU/FE |
| `total` | number | 授权记录数 |

### `spApi/refreshToken`

请求：`sellerId` 必填，`region` 可选。

```json
{"toolName":"spApi/refreshToken","arguments":{"sellerId":"A1234567890","region":"NA"}}
```

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `authRecordId` | number | 授权记录 ID |
| `success` | boolean | 刷新是否成功 |
| `message` | string | 状态消息 |

### `spApi/storeTokens`

请求：`sellerId`、`region` 均必填。只检查授权状态，不返回或提供下游 raw token。

```json
{"toolName":"spApi/storeTokens","arguments":{"sellerId":"A1234567890","region":"NA"}}
```

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `sellerId` | string | Seller ID |
| `region` | string | 区域 |
| `authRecordId` | number | 授权记录 ID |
| `status` | string | 授权状态 |
| `tokenExpiresAt` | number | 来源定义的到期元数据 |
| `message` | string | 状态消息 |

### `spApi/cancelAuthorization`

这是高风险写操作。调用前确认 `sellerId + region`；只解除 LinkFox 本地绑定，Amazon Seller Central 侧需卖家手动 Disable authorization。

```json
{"toolName":"spApi/cancelAuthorization","arguments":{"sellerId":"A1234567890","region":"NA"}}
```

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `success` | boolean | 本地解绑是否成功 |
| `sellerId` | string | Seller ID |
| `region` | string | 区域 |
| `authRecordId` | number | 授权记录 ID |
| `bindUserId` | number | 绑定用户 ID |
| `localAuthorizationRevoked` | boolean | 本地授权是否撤销 |
| `amazonRevoked` | boolean | Amazon 侧是否撤销；来源示例为 false |
| `remainingBindings` | number | 剩余绑定数；为 0 时本地主记录标记 REVOKED |
| `message` | string | 状态消息 |

响应字段来源：`skills/linkfox-amazon-store-auth/references/api.md`。以上覆盖五个成功响应 JSON 的父数组和全部嵌套字段。错误响应字段为 `errcode`（number）与 `errmsg`（string）；来源未说明的可空性不补猜。

## 错误与成本

`200` 成功；`1002` 缺参数或认证失败；`1003` 第三方服务失败；`1004` 授权不存在或不属于当前用户；`1005` 授权取消或失效。授权 URL 获取后等待用户操作，不自动轮询。来源说明授权能力不消耗算力。

## Feedback API

Feedback 与工具网关分离，不迁移为 `proxy_call`；按原契约向 `https://skill-api.linkfox.com/api/v1/public/feedback` 报告，不中断用户流程。
