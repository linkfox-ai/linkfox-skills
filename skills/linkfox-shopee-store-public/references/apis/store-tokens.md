# 查询店铺授权状态兼容辅助调用 接口说明

本文 scripts/ 路径以技能目录为基准；公共规则中的 onboarding.md 指 [认证与算力引导](../onboarding.md)。

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

这是共享模块提供的授权状态辅助函数，六个 Public 操作不自动调用它；日常授权与状态查询优先使用 `linkfox-shopee-store-auth`，此处不实现授权流程，也不返回原始 access/refresh token。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 网关选店；辅助函数将非空值转换为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 网关选商户；允许与 shopId 同时提供。 |
| appType | string | 否 | 网关可选 `erp` / `ad`，默认 `erp`；仅直接调用网关时可指定，兼容辅助函数不转发此字段，使用网关默认值。 |

辅助函数为 `scripts/_shopee_public_common.py` 中的 `resolve_store_tokens(params)`，无独立 CLI。其余 params 字段不转发。调用使用公共 `call_api.run`，始终 `--no-cache`，不读取或保存响应缓存；认证环境变量、网关地址兼容、会话请求头及当前目录落盘规则与 Public 操作相同，详见 [公共脚本运行约定](../api.md#脚本运行约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| 完整响应对象 | object | 辅助函数返回完整网关 JSON；只含授权状态和有效期等信息，不返回原始 token。 |
| authRecordId | integer（Long） | 授权主表 ID。 |
| shopId / merchantId | string | 店铺或商户标识。 |
| shopIdList / merchantIdList | string | 店铺或商户 ID 列表的 JSON 字符串。 |
| appType | string | `erp` / `ad`。 |
| expireIn | integer（Long） | access_token 有效期，单位为秒。 |
| status | string | `ACTIVE` / `EXPIRED`。 |
| message | string | 授权状态说明。 |
| errcode | integer / string / null（如返回） | 按公共规则判断。 |
| errmsg | string（如返回） | 网关说明。 |
| error | string（错误时） | 公共调用器的连接或 HTTP 错误说明。 |
| details | string（如返回） | 非 JSON HTTP 错误的原始文本。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 缺少两种目标标识时在本地终止，不发送请求；不自动刷新、重新授权或重试。
- 六个 Public 流程不会为了本调用增加一次隐式请求。

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
  "skillName": "linkfox-shopee-store-public",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
