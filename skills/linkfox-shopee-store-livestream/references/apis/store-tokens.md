# Shopee 兼容令牌查询接口说明

[返回模块索引](../api.md) · [兼容函数](../../scripts/_shopee_livestream_common.py)

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

## 接口：获取店铺令牌（storeTokens）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/storeTokens`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 店铺 ID；兼容函数将标识转为字符串。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；同时提供时两个值均保留。 |
| appType | string | 否 | 网关默认 `erp`，可选 `erp` / `ad`；兼容函数不透传此字段，使用网关默认值。 |

`resolve_store_tokens(params)` 为 Python 内部兼容入口，没有独立 CLI；只筛选 shopId 与 merchantId，不自动做本地依赖检测。普通直播入口不调用此函数，使用店铺标识由服务端解析令牌。认证环境、无缓存与落盘行为见[脚本运行约定](../api.md#脚本运行约定)。

### 响应结构

| 字段 / 返回值 | 类型 | 说明 |
|---|---|---|
| 函数内存返回值 | object / JSON 值 | 原始接口响应；令牌字段路径及嵌套 schema 按实际返回读取，不固定推断。 |
| errcode | integer / string / null | 响应存在时按基础规则判断。 |
| errmsg | string | 响应存在时用于说明业务原因。 |
| error / details | string | 本地调用器在连接或 HTTP 异常时生成的消息、保留的原始正文（存在时），不属于网关业务字段。 |
| redacted | boolean | 仅持久化副本字段，固定 true；不写入原始令牌正文。 |
| transportHttpStatus | integer / null | 仅持久化副本字段，记录外层 HTTP 状态，连接失败为 null。 |

持久化副本仅包含 redacted 与 transportHttpStatus；原始响应只在内存返回，不打印到标准输出或写入响应缓存。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本接口供 Python 内部兼容调用；结果缺失或失败时不继续依赖令牌执行写入。
- 不以脱敏落盘标记推断接口成功，应检查内存中的原始响应和实际状态。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/storeTokens" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"shopId":"<已授权店铺 ID>"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-livestream",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
