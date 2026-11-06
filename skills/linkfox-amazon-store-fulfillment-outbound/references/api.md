# Amazon 店铺多渠道出仓履约 接口说明

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

### 网关错误响应

接口成功对象与错误对象分别处理。统一错误模型仅包含以下字段；本地脚本补充字段见脚本参考。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 网关错误码；HTTP 200 仍可能包含业务错误。 |
| errmsg | string | 网关错误说明，保留原文。 |

参数异常可返回 HTTP 400、errcode=400；上游连接异常可返回 HTTP 200、errcode=1503。代理定位授权时，1002 表示缺少身份或店铺参数，1004 表示未找到当前成员绑定的授权，1005 也可能表示授权失效；路径白名单拒绝同样使用 1005，须结合 errmsg 区分。不得把本地 error、details、transportHttpStatus、outputError 或解析后的业务对象视为网关 DTO 字段。



## 接口：预览履约订单（getOrderPreview）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/previews`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：200。只有公共正常响应与此成功集合同时满足时才提供解析业务字段和成功缓存；不把错误 body 当作业务结果。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。
- 存在 constraints 时停止创建，展示受影响 SKU 与 Amazon 原因。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "POST",
  "path": "fulfillment/outbound/2026-07-04/previews",
  "body": "{\"destination\":{\"deliveryAddress\":{\"name\":\"示例收件人\",\"addressLine1\":\"1 Example St\",\"postalCode\":\"98101\",\"countryCode\":\"US\"}},\"lineItems\":[{\"product\":{\"productIdentifier\":{\"amazonSku\":\"SKU-1\"}},\"amount\":{\"value\":\"1\",\"unit\":\"EACHES\"}}]}",
  "contentType": "application/json"
}'
```


## 接口：获取配送报价（getOffers）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/offers`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：200。只有公共正常响应与此成功集合同时满足时才提供解析业务字段和成功缓存；不把错误 body 当作业务结果。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。
- 报价不能等同于下单；缺 SKU 的 item 在本地拒绝，避免无效请求。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "POST",
  "path": "fulfillment/outbound/2026-07-04/offers",
  "body": "{\"origin\":{\"countryCode\":\"US\"},\"items\":[{\"productIdentifier\":{\"amazonSku\":\"SKU-1\"}}]}",
  "contentType": "application/json"
}'
```


## 接口：创建履约订单（createOrder）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/orders`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：200 / 202。只有公共正常响应与此成功集合同时满足时才提供解析业务字段；写操作不缓存；不把错误 body 当作业务结果。
- 200 返回 order；202 至少返回 orderId 和 status，表示异步接受，使用原 orderId 查询，不自动轮询或另造幂等标识。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "POST",
  "path": "fulfillment/outbound/2026-07-04/orders",
  "body": "{\"orderId\":\"ORDER-1\",\"destination\":{\"deliveryAddress\":{\"name\":\"示例收件人\",\"addressLine1\":\"1 Example St\",\"postalCode\":\"98101\",\"countryCode\":\"US\"}},\"lineItems\":[{\"lineItemId\":\"LINE-1\",\"product\":{\"productIdentifier\":{\"amazonSku\":\"SKU-1\"}},\"amount\":{\"value\":\"1\",\"unit\":\"EACHES\"}}],\"fulfillmentConfiguration\":{\"action\":\"HOLD\"}}",
  "contentType": "application/json"
}'
```


## 接口：列出履约订单（listOrders）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/orders`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：200。只有公共正常响应与此成功集合同时满足时才提供解析业务字段和成功缓存；不把错误 body 当作业务结果。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "GET",
  "path": "fulfillment/outbound/2026-07-04/orders",
  "queryString": "shipments=INCLUDE"
}'
```


## 接口：查询履约订单（getOrder）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/orders/{orderId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：200。只有公共正常响应与此成功集合同时满足时才提供解析业务字段和成功缓存；不把错误 body 当作业务结果。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。
- 包裹跟踪已包含在订单 shipments 中，不在新版路径上虚构 getPackageTrackingDetails 等额外操作；POD 隐私按 SKILL.md 处理。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "GET",
  "path": "fulfillment/outbound/2026-07-04/orders/ORDER-1",
  "queryString": "shipments=INCLUDE",
  "fulfillmentServiceId": "tenant-1"
}'
```


## 接口：更新履约订单（updateOrder）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/orders/{orderId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：202。只有公共正常响应与此成功集合同时满足时才提供解析业务字段；写操作不缓存；不把错误 body 当作业务结果。
- 202 仅表示请求已接受，不代表更新或取消完成；通过 getOrder 核实。取消无法保证停止已开始履约的部分。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "PUT",
  "path": "fulfillment/outbound/2026-07-04/orders/ORDER-1",
  "body": "{\"fulfillmentConfiguration\":{\"action\":\"SHIP\"}}",
  "contentType": "application/json"
}'
```


## 接口：取消履约订单（cancelOrder）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/orders/{orderId}/cancel`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：202。只有公共正常响应与此成功集合同时满足时才提供解析业务字段；写操作不缓存；不把错误 body 当作业务结果。
- 202 仅表示请求已接受，不代表更新或取消完成；通过 getOrder 核实。取消无法保证停止已开始履约的部分。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "PUT",
  "path": "fulfillment/outbound/2026-07-04/orders/ORDER-1/cancel"
}'
```


## 接口：模拟订单状态（updateOrderStatus）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/orders/{orderId}/status`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：204。只有公共正常响应与此成功集合同时满足时才提供解析业务字段；写操作不缓存；不把错误 body 当作业务结果。
- 204 可没有响应体；这不构成空结果错误，但仅代表沙箱模拟请求成功。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "PUT",
  "path": "fulfillment/outbound/2026-07-04/orders/ORDER-1/status",
  "body": "{\"status\":\"PROCESSING\"}",
  "contentType": "application/json"
}'
```


## 接口：模拟包裹状态（updatePackage）

官方基线：[Fulfillment Outbound v2026-07-04](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-v2026-07-04)；[OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-outbound-api-model/fulfillmentOutbound_2026-07-04.json)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fulfillment/outbound/2026-07-04/orders/{orderId}/packages/{packageId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |
| fulfillmentServiceId | string | 否 | 仅适用于 Fulfillment Outbound v2026-07-04；去空白后不超过 40 字符且不得包含 CR/LF；映射为上游 x-amzn-fulfillment-service-id 请求头。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：204。只有公共正常响应与此成功集合同时满足时才提供解析业务字段；写操作不缓存；不把错误 body 当作业务结果。
- 204 可没有响应体；这不构成空结果错误，但仅代表沙箱模拟请求成功。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "PUT",
  "path": "fulfillment/outbound/2026-07-04/orders/ORDER-1/packages/PACKAGE-1",
  "body": "{\"status\":\"IN_TRANSIT\"}",
  "contentType": "application/json"
}'
```


## 接口：查询发票头（getInvoiceHeaders）

本接口属于 Invoices API v2026-06-25；Outbound 概述角色列表关联此操作，但它不在 Outbound 模型的九个 operation 中。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `finances/invoices/2026-06-25/invoices`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Amazon 上游成功状态：200。只有公共正常响应与此成功集合同时满足时才提供解析业务字段和成功缓存；不把错误 body 当作业务结果。
- Amazon 400 / 403 / 404 / 413 / 415 时修正请求、授权或资源；429 / 500 / 503 或超时后不自动重放 POST/PUT，写入结果不确定时先查询原订单。
- 450 / 453 / 454 / 459 的触发阈值、冷却、停调范围和最多一次恢复重试见 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil；453 停止该店铺全部 SP-API。
- 仅发现发票头，不返回完整发票承诺；空页也可能带 nextToken，不自动翻页。

### curl 示例

固定操作脚本自动构造以下网关请求。写入示例仅用于核对契约，实际执行仍需明确确认；confirmWrite 是本地选项，不加入网关 body。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1SELLER",
  "region": "NA",
  "method": "GET",
  "path": "finances/invoices/2026-06-25/invoices",
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-fulfillment-outbound",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
