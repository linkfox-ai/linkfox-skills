# 查询店铺授权状态 接口说明

[模块导航](../api.md)。`_shopee_logistics_common.resolve_store_tokens(params)` 提供的兼容操作；仅查询既有授权状态，不返回原始令牌，不实现授权或刷新逻辑；常规 46 个物流脚本不额外调用。

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

## 接口：查询店铺授权状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID；helper 将值转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 已授权商户 ID；同时传入时两个标识均保留。 |
| appType | string | 否 | 网关默认 `erp`，允许 `erp` / `ad`；物流使用 `erp`。兼容 helper 仅转发 shopId / merchantId，使用网关默认值；其他应用类型须直接调用网关。 |

环境变量与输出、无缓存约定见 [脚本运行约定](../api.md#脚本运行约定)。未提供任一标识时 helper 在本地退出 1。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按公共规则判断。 |
| errmsg | string | 网关消息。 |
| error | string | HTTP 或连接错误的兼容说明（如有）。 |
| details | string | HTTP 错误原始响应详情（如有）。 |
| authRecordId | integer（Long） | 授权主表 ID。 |
| shopId | string | 店铺 ID。 |
| merchantId | string | 商户 ID。 |
| shopIdList | string | 店铺 ID 列表的 JSON 字符串。 |
| merchantIdList | string | 商户 ID 列表的 JSON 字符串。 |
| appType | string | 应用类型：`erp` / `ad`。 |
| expireIn | integer（Long） | access_token 有效期，单位为秒；不据此推算剩余有效期。 |
| status | string | 授权记录状态：`ACTIVE` / `EXPIRED`；不替代实际物流请求结果。 |
| message | string | 授权状态说明。 |

响应不包含原始 access_token / refresh_token；helper 原样返回网关 JSON。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 无授权记录交由 `linkfox-shopee-store-auth` 处理；不得从查询授权状态扩展为重新授权。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-logistics",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
