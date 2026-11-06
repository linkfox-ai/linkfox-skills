# 店铺授权状态辅助 接口说明

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

## 接口：查询店铺授权状态（resolve_store_tokens）

此接口返回已绑定店铺的授权状态，不返回原始令牌；15 个 Returns 入口不主动调用它。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID；辅助函数将非空值转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；辅助函数允许两者同时传入。 |
| appType | string | 否 | 网关默认 erp，枚举 erp / ad；辅助函数仅透传 shopId / merchantId，使用网关默认 erp；直接调用网关时可指定。 |

辅助函数为 `scripts/_shopee_returns_common.py::resolve_store_tokens(params)`；没有独立 Returns CLI 操作名，不把该函数当作授权实现。依赖选店与授权由 `linkfox-shopee-store-auth` 完成，Returns 主流程由服务端按选店标识解析令牌。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务码，按基础规则判断。 |
| errmsg | string | 网关消息。 |
| authRecordId | Long | 授权主表 ID。 |
| shopId / merchantId | string | 店铺 / 商户 ID。 |
| shopIdList / merchantIdList | string | 店铺 / 商户 ID 列表的 JSON 字符串。 |
| appType | string | erp / ad。 |
| expireIn | Long | access_token 有效期（秒）。 |
| status | string | 授权状态 ACTIVE / EXPIRED。 |
| message | string | 说明。 |

#### 本地附加字段

辅助函数完整返回公共调用器的响应对象。HTTP 异常无法解析响应 JSON 时可能含本地生成的 `error` 和 `details`，连接失败时可能含 `error`；这些字段不是网关成功响应契约。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 无授权记录时应回到 `linkfox-shopee-store-auth` 核对授权；不在本技能内创建或刷新令牌。
- 授权状态查询不能替代店铺授权；正常响应不表示退货业务处理成功。

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
  "skillName": "linkfox-shopee-store-returns",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
