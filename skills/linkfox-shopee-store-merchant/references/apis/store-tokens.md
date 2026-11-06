# 查询已授权店铺或商户状态 接口说明

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

## 接口：查询已授权店铺或商户状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 已授权店铺标识。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户标识。 |
| appType | string | 否 | 授权应用类型，枚举 `erp` / `ad`，默认 `erp`；Merchant 使用 `erp`。 |

接口返回当前用户已绑定的授权状态，不返回原始令牌。共享脚本 `resolve_store_tokens(params)` 只提取 `shopId`、`merchantId` 并转换为字符串，不传 `appType`，因此使用网关默认值 `erp`；不提供独立 CLI、不自动参与六项 Merchant 查询。授权与令牌管理仍由认证技能负责，不能借此创建授权。兼容环境变量、无缓存与输出约定见 [模块运行约定](../api.md#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态码，按公共规则判断。 |
| errmsg | string | 网关错误或说明。 |
| authRecordId | integer (Long) | 授权主表 ID。 |
| shopId | string | 店铺 ID。 |
| merchantId | string | 商户 ID。 |
| shopIdList | string | 店铺 ID 列表的 JSON 字符串。 |
| merchantIdList | string | 商户 ID 列表的 JSON 字符串。 |
| appType | string | 授权应用类型：`erp` / `ad`。 |
| expireIn | integer (Long) | access_token 有效期，单位秒；不是绝对到期时间。 |
| status | string | 授权状态：`ACTIVE` / `EXPIRED`。 |
| message | string | 授权状态说明。 |

辅助函数原样返回完整网关 JSON，不提取令牌。

#### 辅助函数落盘兼容

| 字段 | 类型 | 说明 |
|---|---|---|
| response | array / string / number / boolean / null | 仅网关返回非对象 JSON 时，落盘文件用此字段包裹原始响应，避免公共输出器因非对象响应崩溃；Python 返回值仍为原始 JSON。对象响应直接完整落盘，不增加此包裹。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

未取得有效授权记录时，交由 `linkfox-shopee-store-auth` 处理；不自动重试、创建或刷新授权。不得把任何令牌展示为用户报告内容。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"merchantId":"12345"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-merchant",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
