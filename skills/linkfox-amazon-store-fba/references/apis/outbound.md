# Amazon FBA MCF 履约 v2020-07-01 接口说明

认证引导见 [onboarding.md](../onboarding.md)，通用运行约定见 [api.md](../api.md)。

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



## 接口：预览旧版 MCF 履约（getFulfillmentPreview）

> 官方：[getFulfillmentPreview](https://developer-docs.amazon.com/sp-api/reference/getfulfillmentpreview)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/fulfillmentOrders/preview`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "POST",
  "path": "fba/outbound/2020-07-01/fulfillmentOrders/preview",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：查询旧版 MCF 配送报价（deliveryOffers）

> 官方：[deliveryOffers](https://developer-docs.amazon.com/sp-api/reference/deliveryoffers)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/deliveryOffers`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "POST",
  "path": "fba/outbound/2020-07-01/deliveryOffers",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出旧版 MCF 履约订单（listAllFulfillmentOrders）

> 官方：[listAllFulfillmentOrders](https://developer-docs.amazon.com/sp-api/reference/listallfulfillmentorders)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/fulfillmentOrders`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "GET",
  "path": "fba/outbound/2020-07-01/fulfillmentOrders"
}'
```


## 接口：创建旧版 MCF 履约订单（createFulfillmentOrder）

> 官方：[createFulfillmentOrder](https://developer-docs.amazon.com/sp-api/reference/createfulfillmentorder)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/fulfillmentOrders`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "POST",
  "path": "fba/outbound/2020-07-01/fulfillmentOrders",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：获取旧版 MCF 包裹跟踪（getPackageTrackingDetails）

> 官方：[getPackageTrackingDetails](https://developer-docs.amazon.com/sp-api/reference/getpackagetrackingdetails)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/tracking`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "GET",
  "path": "fba/outbound/2020-07-01/tracking",
  "queryString": "packageNumber=123"
}'
```


## 接口：列出旧版 MCF 退货原因（listReturnReasonCodes）

> 官方：[listReturnReasonCodes](https://developer-docs.amazon.com/sp-api/reference/listreturnreasoncodes)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/returnReasonCodes`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "GET",
  "path": "fba/outbound/2020-07-01/returnReasonCodes"
}'
```


## 接口：创建旧版 MCF 退货（createFulfillmentReturn）

> 官方：[createFulfillmentReturn](https://developer-docs.amazon.com/sp-api/reference/createfulfillmentreturn)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/return`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "PUT",
  "path": "fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE_sellerFulfillmentOrderId/return",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：获取旧版 MCF 履约订单（getFulfillmentOrder）

> 官方：[getFulfillmentOrder](https://developer-docs.amazon.com/sp-api/reference/getfulfillmentorder)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "GET",
  "path": "fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE_sellerFulfillmentOrderId"
}'
```


## 接口：更新旧版 MCF 履约订单（updateFulfillmentOrder）

> 官方：[updateFulfillmentOrder](https://developer-docs.amazon.com/sp-api/reference/updatefulfillmentorder)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "PUT",
  "path": "fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE_sellerFulfillmentOrderId",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：取消旧版 MCF 履约订单（cancelFulfillmentOrder）

> 官方：[cancelFulfillmentOrder](https://developer-docs.amazon.com/sp-api/reference/cancelfulfillmentorder)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/cancel`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "PUT",
  "path": "fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE_sellerFulfillmentOrderId/cancel",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：提交旧版 MCF 订单状态更新（submitFulfillmentOrderStatusUpdate）

> 官方：[submitFulfillmentOrderStatusUpdate](https://developer-docs.amazon.com/sp-api/reference/submitfulfillmentorderstatusupdate)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/status`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "PUT",
  "path": "fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE_sellerFulfillmentOrderId/status",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：获取旧版 MCF 功能（getFeatures）

> 官方：[getFeatures](https://developer-docs.amazon.com/sp-api/reference/getfeatures)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/features`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "GET",
  "path": "fba/outbound/2020-07-01/features",
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}'
```


## 接口：获取旧版 MCF 功能库存（getFeatureInventory）

> 官方：[getFeatureInventory](https://developer-docs.amazon.com/sp-api/reference/getfeatureinventory)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/features/inventory/{featureName}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "GET",
  "path": "fba/outbound/2020-07-01/features/inventory/EXAMPLE_featureName",
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}'
```


## 接口：获取旧版 MCF 功能 SKU（getFeatureSKU）

> 官方：[getFeatureSKU](https://developer-docs.amazon.com/sp-api/reference/getfeaturesku)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/outbound/2020-07-01/features/inventory/{featureName}/{sellerSku}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [outbound-script-usage.md](outbound-script-usage.md)。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先判断 LinkFox 外层与网关状态，再判断 Amazon 上游 httpStatus。上游 2xx 才解析业务 body；202 可能只是被接受，204 可无 body，不能据此宣称后续业务流程完成。
- errcode=1005 时先结合 errmsg 区分：路径未放行时联系后端确认 fba/、inbound/fba/ 白名单；授权失效时重新完成店铺授权。403 检查 Amazon Fulfillment 等角色、授权与区域。
- 遇 429 降速并先征得用户同意；450 / 453 / 454 / 459 按 [店铺保护与重试](../spapi-protection.md) 处理，453 期间停止该店铺全部 SP-API，不重放结果不确定的写入。

### curl 示例

以下为请求形状示意；将 EXAMPLE 标识和业务 body 占位文本替换为真实有效输入后再使用。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1EXAMPLE",
  "region": "NA",
  "method": "GET",
  "path": "fba/outbound/2020-07-01/features/inventory/EXAMPLE_featureName/EXAMPLE_sellerSku",
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-fba",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
