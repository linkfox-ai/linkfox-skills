# Shopee 已授权状态查询兼容接口说明

[模块导航](../api.md) · [技能入口](../../SKILL.md) · [认证与算力引导](../onboarding.md)

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

## 接口：查询已授权店铺状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `shopId` | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐使用；两者均提供时，兼容函数均转发。 |
| `merchantId` | string | 与 shopId 至少一个 | 已授权商户 ID；本模块不属于可省略选店的 Public 接口。 |
| `appType` | string | 否 | 网关默认 erp，枚举 erp / ad；订单使用 erp。兼容函数只转发 shopId / merchantId，使用网关默认值；指定 appType 时需直接调用接口。 |

`_shopee_orders_common.resolve_store_tokens(params)` 提供已授权状态兼容查询。它仅查询已授权记录，不返回原始令牌，也不发起授权。当前 22 个订单 CLI 不调用此函数，直接按 shopId / merchantId 选店。安装与重新授权交给 `linkfox-shopee-store-auth`，本技能不实现授权或令牌刷新。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码，遵循公共规则。 |
| errmsg | string | 网关消息或错误原因。 |
| authRecordId | Long | 授权主表 ID。 |
| shopId | string | 店铺 ID。 |
| merchantId | string | 商户 ID。 |
| shopIdList | string | 店铺 ID 列表的 JSON 字符串。 |
| merchantIdList | string | 商户 ID 列表的 JSON 字符串。 |
| appType | string | 应用类型：erp / ad。 |
| expireIn | Long | access_token 有效期，单位秒；不据此推算当前剩余有效期。 |
| status | string | ACTIVE / EXPIRED；服务端按授权记录是否含 token 标记，不等同于刚完成上游有效性校验。 |
| message | string | 授权状态说明。 |

以上为网关定义的响应字段；兼容函数原样保留实际响应。接口不返回 accessToken 或 refreshToken。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 选店标识缺失时本地退出，不发送请求。无授权记录时返回授权技能处理，不自动刷新 token。
- 兼容函数通过公共 run 执行并强制 --no-cache，不自动串联订单操作。运行约定见 [模块运行约定](../api.md#运行约定)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "shopId": "67890"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-orders",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
