# linkfox-shopee-store-auth

## MCP 调用

| 子能力 | MCP server | 唯一工具 | `toolName` | `arguments` |
|---|---|---|---|---|
| 生成授权 URL | `LinkFox` | `proxy_call` | `shopee/authorizeUrl` | 本节请求参数对象 |
| 列已授权店铺 | `LinkFox` | `proxy_call` | `shopee/authorizedStores` | `{}` |
| 查询授权状态 | `LinkFox` | `proxy_call` | `shopee/storeTokens` | 本节请求参数对象 |

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；禁止在 MCP 配置或 `arguments` 中传 `headers`、API Key、token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 HTTP fallback。相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。返回 text 为 JSON 字符串时只解析一次，并依次处理 MCP、代理和下游业务错误。

## 请求参数与响应字段

### `shopee/authorizeUrl`

| 请求字段 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `shopName` | string | 否 | - | 店铺展示名 |
| `region` | string | 否 | `cn` | `cn` / `global` / `br` |
| `appType` | string | 否 | `erp` | `erp` / `ad` |

```json
{"toolName":"shopee/authorizeUrl","arguments":{"shopName":"Example Shop","region":"cn","appType":"erp"}}
```

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `sourceType` | string | 来源示例中的来源类型 |
| `authorizeUrl` | string | 来源示例中的授权 URL，约 1 小时有效 |

### `shopee/authorizedStores`

```json
{"toolName":"shopee/authorizedStores","arguments":{}}
```

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | number | 店铺授权记录数 |
| `stores` | array | 授权记录数组 |
| `stores[].authRecordId` | number | 授权记录 ID |
| `stores[].shopId` | string | 店铺 ID |
| `stores[].merchantId` | string | 商户 ID |
| `stores[].shopIdList` | string | 店铺 ID 列表的 JSON 字符串 |
| `stores[].merchantIdList` | string | 商户 ID 列表的 JSON 字符串 |
| `stores[].shopName` | string | 店铺展示名 |
| `stores[].region` | string | 授权区域 |
| `stores[].appType` | string | `erp` / `ad`；历史空值按 `erp` |

### `shopee/storeTokens`

| 请求字段 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `shopId` | string | 与 `merchantId` 二选一 | - | 店铺 ID |
| `merchantId` | string | 与 `shopId` 二选一 | - | 商户 ID |
| `appType` | string | 否 | `erp` | `erp` / `ad` |

```json
{"toolName":"shopee/storeTokens","arguments":{"shopId":"67890","appType":"ad"}}
```

| 响应字段路径 | 类型 | 说明 |
|---|---|---|
| `authRecordId` | number | 授权记录 ID |
| `shopId` | string | 店铺 ID |
| `merchantId` | string | 商户 ID |
| `appType` | string | 应用类型 |
| `tokenType` | string | 来源状态示例中的 token 类型元数据，不是原始 token |
| `expireIn` | number | access token 剩余有效秒数，通常 14400 |
| `status` | string | 授权状态 |

响应字段来源：`skills/linkfox-shopee-store-auth/references/api.md`。上表覆盖来源三个公开接口示例的全部顶层、父数组及嵌套字段；没有补猜来源未给出的可空性或约束。

## 授权业务规则

- ERP 与 AD 是独立授权；广告 operation 必须具备 `appType=ad`，其他店铺 operation 使用 ERP。
- 判断授权须匹配 `shopId`/`merchantId + appType`；`storeTokens` 只检查状态，不返回原始 access/refresh token，也不触发刷新。
- 授权 URL 约 1 小时有效，不复用旧 URL。授权属于外部用户操作，获取 URL 后等待用户完成，再查询授权记录；不得自动轮询。
- `api/v2/ads/**` 由服务端选择 AD，其余 `api/v2/**` 选择 ERP；调用 `shopee/developerProxy` 时禁止传 `appType` 或 access token。

## 错误码

| `errcode` | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 读取结果 |
| `1002` | 参数错误、`appType` 非法或未登录 | 修正参数，不重试相同请求 |
| `1003` | 授权服务异常或网络失败 | 授权时重新获取 URL；不自动重试 |
| `1004` | 找不到目标应用授权 | 按 ERP/AD 能力重新授权 |
| `1005` | Token 失效或转发路径未白名单 | 重新授权或核对 `api/v2` path |

## 算力消耗

来源 skill 明确说明这三个授权管理操作不消耗算力。仍需遵守相同 `toolName + arguments` 不重复调用以及授权状态不自动轮询的规则。

## Feedback API

Feedback API 与工具网关分离，不迁移为 `proxy_call`。仅在功能与描述不符、结果偏离意图、用户表达反馈或发现改进点时，按原 Feedback 契约向 `https://skill-api.linkfox.com/api/v1/public/feedback` 报告，不中断当前流程。
