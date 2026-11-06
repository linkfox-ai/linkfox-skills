# Shopee 查询优惠券详情接口说明

[模块导航与运行约定](../api.md)

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

## 接口：查询优惠券详情（get_voucher）

按 voucher_id 查看优惠券详情。

> 官方：[get_voucher](https://open.shopee.com/documents/v2/v2.voucher.get_voucher?module=112&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| path | string | 是 | 固定为 `api/v2/voucher/get_voucher`，必须带 `api/v2/voucher/` 前缀。 |
| method | string | 是 | 固定为 `GET`；外层请求始终为 POST。 |
| shopId | string | 与 merchantId 至少一个 | 推荐使用选定店铺 ID；允许同时提供两种标识。网关据此选择授权，并将其作为 `shop_id` 加入上游 query。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；网关据此选择授权，并将其作为 `merchant_id` 加入上游 query，不加入 body。 |
| queryString | string | 按上游要求 | 不含 `?` 的 URL 编码查询串；脚本仅在构造结果非空时发送。 |
| body | string | 否 | 共享函数兼容的上游请求体字符串；本 GET 操作的 CLI 不发送。 |
| contentType | string | 否 | 仅共享函数传 body 时使用，默认 `application/json`；本 GET 操作的 CLI 不发送。 |

服务端根据选店标识解析令牌，无需客户端提供原始令牌。脚本不会自动将顶层保留键按原键名拼入上游查询或请求体；选店标识由网关按上述规则转发。

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 同上；数字输入兼容转成字符串发送。 |
| merchantId | string | 与 shopId 至少一个 | 同上；保留用户指定的选店标识。 |
| api | string | 仅通用入口必填 | `get_voucher`；独立脚本已固定此值。 |
| skipDepCheck | boolean | 否 | 默认 false，仅跳过本地安装检测。 |
| contentType | string | 否 | 兼容保留键，默认 `application/json`；本 GET 操作不发送上游请求体，因此不传给网关。 |
| 上游业务字段 | string / number / boolean | 按官方要求 | 放 JSON 顶层；非 null 标量逐项 URL 编码，boolean 转为小写；null、object、array 被忽略。 |
| voucher_id | 按上游定义 | 按上游要求 | 优惠券标识；按上游定义核对类型、默认值和范围，脚本按标量查询字段处理。 |

`shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType` 是保留键，不进入查询串。注册表 `LIST_QUERY_FIELDS` 为空，查询不执行列表归一化。完整上游查询 schema、分页字段、状态枚举和限额按本页官方文档及实际返回核对，不臆造。

脚本 CLI、依赖退出码、无缓存、认证兼容与输出路径见 [运行约定](../api.md#脚本运行约定)。

### 响应结构

#### 网关响应与传输错误字段

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | 以实际响应为准 | 网关状态码若返回，按公共规则处理；不与脚本封装字段混为一谈。 |
| errmsg | 以实际响应为准 | 网关消息若返回，保留原因。 |
| httpStatus | integer（脚本兼容数字字符串） | Shopee 上游 HTTP 状态，与外层 LinkFox HTTP 状态不同。 |
| body | string | Shopee 原始响应正文；脚本按 JSON 解析。 |
| 其他原始字段 | 以实际响应为准 | 完整保留实际返回的其他字段，不假定额外字段的结构或类型。 |
| error | string | 传输失败时的错误说明；HTTP 错误有可解析 JSON 时保留其原始字段。 |
| details | string | HTTP 错误正文无法解析为 JSON 时保留的原文。 |
| rawResponse | 原响应 JSON 类型 | 仅网关返回非 object JSON 时由兼容封装保留。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 本次操作 `get_voucher`。 |
| developerProxy | object | 网关完整响应；保留错误，不丢弃原始 body。 |
| developerProxy.transportHttpStatus | integer / null | 业务封装记录的外层 LinkFox HTTP 状态；连接失败为 null。 |
| transportHttpStatus | integer / null | 顶层回显外层状态，便于与上游 `developerProxy.httpStatus` 区分。 |
| resolvedPath | string | 实际转发路径 `api/v2/voucher/get_voucher`。 |
| queryString | string | 仅非空 GET 查询时返回，不含 `?`。 |
| getVoucher | 解析后的 JSON 类型 / null | 网关正常响应且上游状态为 200 时解析 body；正文为空或不是合法 JSON 时为 null；其余状态不生成该字段。 |
| getVoucherResponse | 原上游类型 | 当 `getVoucher` 为 object 且其 `response` 非 null 时提取；不补造内部字段。 |

`getVoucher` 保留整个上游 JSON，`getVoucherResponse` 提取其中非 null 的 `response`。业务数据字段以官方文档及实际响应为准。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先核对外层状态和网关状态，再核对 `developerProxy.httpStatus`；上游状态为 200 才解析优惠券响应。
- 解析出 JSON 不代表活动操作成功；仍须根据上游正文的错误说明和实际结果解释，不自动重放写入。
- 上游 body 为空或解析失败时保留原始 `developerProxy.body`，不补造优惠券结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path":"api/v2/voucher/get_voucher","method":"GET","shopId":"67890","queryString":"voucher_id=12345"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-voucher",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
