# Shopee 选店授权状态查询 接口说明

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

## 接口：查询选店授权状态（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID，推荐；脚本转为字符串。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户 ID；两者同时传入时均保留，不擅自更换目标。 |
| appType | string | 否 | 网关默认 erp，可选 erp / ad；Shop 模块使用 erp。 |

业务辅助函数 `resolve_store_tokens(params)` 只提取 shopId、merchantId 并转为字符串；两者均缺失时退出 1。此辅助函数不映射 appType，使用网关默认 erp；不自动插入 9 个 Shop CLI 的调用链，不以其代替授权技能。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| 返回对象 | object | 原样返回网关 JSON；返回授权记录与状态，不返回原始令牌。 |
| authRecordId | Long | 授权记录 ID。 |
| shopId / merchantId | string | 授权记录中的店铺 / 商户 ID。 |
| shopIdList / merchantIdList | string | 店铺 / 商户 ID 列表的 JSON 字符串。 |
| appType | string | erp / ad。 |
| expireIn | Long | 授权记录中的有效期秒数，不是本次查询起的剩余有效期。 |
| status | string | ACTIVE / EXPIRED；授权记录状态，不能替代实际转发结果。 |
| message | string | 授权状态说明。 |
| errcode | integer / string / null（如返回） | 网关状态，按公共规则判断。 |
| errmsg | string（如返回） | 网关消息。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

本辅助函数保留授权状态字段，不承担授权或令牌获取流程；授权缺失或异常转交授权技能。

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
  "skillName": "linkfox-shopee-store-shop",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
