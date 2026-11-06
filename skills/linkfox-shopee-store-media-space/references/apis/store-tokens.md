# 店铺授权状态辅助接口说明

公共规则与运行约定见 [模块总览](../api.md)。

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

## 接口：查询店铺授权状态（storeTokens，辅助函数）

对应函数：`scripts/_shopee_media_space_common.py` 的 `resolve_store_tokens`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID；存在时转字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；存在时转字符串。 |
| appType | string | 否 | 默认 erp；可选 erp / ad。resolve_store_tokens 不转发此字段，辅助函数查询默认的 erp 授权。 |

调用 resolve_store_tokens(params) 时，shopId 与 merchantId 可同时传；均为空时本地退出 1。本函数只透传这两个标识，无独立 CLI，不自行执行依赖检查；仅供已完成外部授权的调用方通过函数查询授权状态。当前六个媒体操作不调用本函数，不要为上传增加一次授权状态查询。业务封装调用 call_api.run 时始终禁用响应缓存，运行约定见 [模块总览](../api.md)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息。 |
| authRecordId | integer (Long) | 授权记录 ID。 |
| shopId | string | 店铺 ID。 |
| merchantId | string | 商户 ID。 |
| shopIdList | string | 店铺 ID 列表的 JSON 字符串。 |
| merchantIdList | string | 商户 ID 列表的 JSON 字符串。 |
| appType | string | erp / ad。 |
| expireIn | integer (Long) | access_token 有效期，单位秒。 |
| status | string | ACTIVE / EXPIRED；授权状态，不代表媒体上传成功。 |
| message | string | 授权状态说明。网关不返回原始 token。 |

#### 本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 连接或 HTTP 错误描述，如有。 |
| details | string | 非 JSON HTTP 错误原文，如有。 |
| transportHttpStatus | integer / null | 封装附加的外层 HTTP 状态。 |
| rawResponse | any | 网关响应非对象时保留原始值。 |

辅助函数完整透传网关响应并附加本地诊断字段，不解析或补造其他嵌套结构。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 1004 表示没有授权记录，交给认证技能处理；不要在本技能中创建授权或刷新 token。
- 函数仅返回网关原始结果，不把“拿到返回对象”解释为授权或上传成功。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "shopId": "67890"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-media-space",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
