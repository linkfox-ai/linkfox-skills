# Shopee 提前结束优惠券接口说明

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

## 接口：提前结束优惠券（end_voucher）

提前结束指定优惠券活动。

> 官方：[end_voucher](https://open.shopee.com/documents/v2/v2.voucher.end_voucher?module=112&type=1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| path | string | 是 | 固定为 `api/v2/voucher/end_voucher`，必须带 `api/v2/voucher/` 前缀。 |
| method | string | 是 | 固定为 `POST`；外层请求始终为 POST。 |
| shopId | string | 与 merchantId 至少一个 | 推荐使用选定店铺 ID；允许同时提供两种标识。网关据此选择授权，并将其作为 `shop_id` 加入上游 query。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；网关据此选择授权，并将其作为 `merchant_id` 加入上游 query，不加入 body。 |
| queryString | string | 否 | 共享函数兼容不含 `?` 的查询串；本 POST 操作的 CLI 不构造或发送此字段。 |
| body | string | 是 | 上游请求体的字符串；按本操作的官方字段要求构造。 |
| contentType | string | 传 body 时 | 默认 `application/json`；共享函数在 body 非 null 时传给网关。 |

服务端根据选店标识解析令牌，无需客户端提供原始令牌。脚本不会自动将顶层保留键按原键名拼入上游查询或请求体；选店标识由网关按上述规则转发。

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 默认值 / 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一个 | 同上；数字输入兼容转成字符串发送。 |
| merchantId | string | 与 shopId 至少一个 | 同上；保留用户指定的选店标识。 |
| api | string | 仅通用入口必填 | `end_voucher`；独立脚本已固定此值。 |
| skipDepCheck | boolean | 否 | 默认 false，仅跳过本地安装检测。 |
| contentType | string | 否 | 默认 `application/json`。 |
| body | object / string | 与 requestBody 任选其一 | 优先于 requestBody；对象紧凑序列化，字符串原样传递。按提前结束操作的官方要求提供目标优惠券。 |
| requestBody | object / string | 未传 body 时使用 | 与 body 兼容，保持字符串原样传递。 |

本模块六个注册项均未登记 `body_fields`；runner 仅按注册项中的 `body_fields` 收集顶层业务字段，因此这些操作必须使用 `body` / `requestBody`。`shopId`、`merchantId`、`skipDepCheck` 等保留键不自动进入上游 body。完整优惠券配置字段、必填组合、枚举、默认值和数量限制须依据本页官方文档核对，并结合用户提供的完整 body 构造，不能将示例占位对象当成有效活动配置。

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
| api | string | 本次操作 `end_voucher`。 |
| developerProxy | object | 网关完整响应；保留错误，不丢弃原始 body。 |
| developerProxy.transportHttpStatus | integer / null | 业务封装记录的外层 LinkFox HTTP 状态；连接失败为 null。 |
| transportHttpStatus | integer / null | 顶层回显外层状态，便于与上游 `developerProxy.httpStatus` 区分。 |
| resolvedPath | string | 实际转发路径 `api/v2/voucher/end_voucher`。 |
| requestBody | 原输入 JSON 类型 / string / null | POST 时返回解析后的请求体；非 JSON 字符串保留原文，空字符串为 null。 |
| endVoucher | 解析后的 JSON 类型 / null | 网关正常响应且上游状态为 200 时解析 body；正文为空或不是合法 JSON 时为 null；其余状态不生成该字段。 |
| endVoucherResponse | 原上游类型 | 当 `endVoucher` 为 object 且其 `response` 非 null 时提取；不补造内部字段。 |

`endVoucher` 保留整个上游 JSON，`endVoucherResponse` 提取其中非 null 的 `response`。业务数据字段以官方文档及实际响应为准。

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
  -d '{"path":"api/v2/voucher/end_voucher","method":"POST","shopId":"67890","body":"<按官方定义填写完整请求体>","contentType":"application/json"}'
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
