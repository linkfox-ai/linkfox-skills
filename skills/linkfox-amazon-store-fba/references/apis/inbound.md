# Amazon FBA 入仓 v2024-03-20 接口说明

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



## 接口：列出入仓计划（listInboundPlans）

> 官方：[listInboundPlans](https://developer-docs.amazon.com/sp-api/reference/listinboundplans)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans"
}'
```


## 接口：创建入仓计划（createInboundPlan）

> 官方：[createInboundPlan](https://developer-docs.amazon.com/sp-api/reference/createinboundplan)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：获取入仓计划（getInboundPlan）

> 官方：[getInboundPlan](https://developer-docs.amazon.com/sp-api/reference/getinboundplan)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId"
}'
```


## 接口：列出计划箱件（listInboundPlanBoxes）

> 官方：[listInboundPlanBoxes](https://developer-docs.amazon.com/sp-api/reference/listinboundplanboxes)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/boxes"
}'
```


## 接口：取消入仓计划（cancelInboundPlan）

> 官方：[cancelInboundPlan](https://developer-docs.amazon.com/sp-api/reference/cancelinboundplan)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/cancellation",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出计划商品（listInboundPlanItems）

> 官方：[listInboundPlanItems](https://developer-docs.amazon.com/sp-api/reference/listinboundplanitems)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/items"
}'
```


## 接口：更新计划名称（updateInboundPlanName）

> 官方：[updateInboundPlanName](https://developer-docs.amazon.com/sp-api/reference/updateinboundplanname)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/name",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出装箱组箱件（listPackingGroupBoxes）

> 官方：[listPackingGroupBoxes](https://developer-docs.amazon.com/sp-api/reference/listpackinggroupboxes)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/packingGroups/EXAMPLE_packingGroupId/boxes"
}'
```


## 接口：列出装箱组商品（listPackingGroupItems）

> 官方：[listPackingGroupItems](https://developer-docs.amazon.com/sp-api/reference/listpackinggroupitems)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/packingGroups/EXAMPLE_packingGroupId/items"
}'
```


## 接口：设置装箱信息（setPackingInformation）

> 官方：[setPackingInformation](https://developer-docs.amazon.com/sp-api/reference/setpackinginformation)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/packingInformation",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出装箱选项（listPackingOptions）

> 官方：[listPackingOptions](https://developer-docs.amazon.com/sp-api/reference/listpackingoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/packingOptions"
}'
```


## 接口：生成装箱选项（generatePackingOptions）

> 官方：[generatePackingOptions](https://developer-docs.amazon.com/sp-api/reference/generatepackingoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/packingOptions",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：确认装箱选项（confirmPackingOption）

> 官方：[confirmPackingOption](https://developer-docs.amazon.com/sp-api/reference/confirmpackingoption)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/packingOptions/EXAMPLE_packingOptionId/confirmation",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出计划托盘（listInboundPlanPallets）

> 官方：[listInboundPlanPallets](https://developer-docs.amazon.com/sp-api/reference/listinboundplanpallets)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/pallets"
}'
```


## 接口：列出放置选项（listPlacementOptions）

> 官方：[listPlacementOptions](https://developer-docs.amazon.com/sp-api/reference/listplacementoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/placementOptions"
}'
```


## 接口：生成放置选项（generatePlacementOptions）

> 官方：[generatePlacementOptions](https://developer-docs.amazon.com/sp-api/reference/generateplacementoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/placementOptions",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：确认放置选项（confirmPlacementOption）

> 官方：[confirmPlacementOption](https://developer-docs.amazon.com/sp-api/reference/confirmplacementoption)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/placementOptions/EXAMPLE_placementOptionId/confirmation",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：获取现行入仓货件（getShipment）

> 官方：[getShipment](https://developer-docs.amazon.com/sp-api/reference/getshipment)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId"
}'
```


## 接口：列出货件箱件（listShipmentBoxes）

> 官方：[listShipmentBoxes](https://developer-docs.amazon.com/sp-api/reference/listshipmentboxes)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/boxes"
}'
```


## 接口：列出货件内容更新预览（listShipmentContentUpdatePreviews）

> 官方：[listShipmentContentUpdatePreviews](https://developer-docs.amazon.com/sp-api/reference/listshipmentcontentupdatepreviews)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/contentUpdatePreviews"
}'
```


## 接口：生成货件内容更新预览（generateShipmentContentUpdatePreviews）

> 官方：[generateShipmentContentUpdatePreviews](https://developer-docs.amazon.com/sp-api/reference/generateshipmentcontentupdatepreviews)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/contentUpdatePreviews",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：获取货件内容更新预览（getShipmentContentUpdatePreview）

> 官方：[getShipmentContentUpdatePreview](https://developer-docs.amazon.com/sp-api/reference/getshipmentcontentupdatepreview)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/contentUpdatePreviews/EXAMPLE_contentUpdatePreviewId"
}'
```


## 接口：确认货件内容更新预览（confirmShipmentContentUpdatePreview）

> 官方：[confirmShipmentContentUpdatePreview](https://developer-docs.amazon.com/sp-api/reference/confirmshipmentcontentupdatepreview)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/contentUpdatePreviews/EXAMPLE_contentUpdatePreviewId/confirmation",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：获取交货单文档（getDeliveryChallanDocument）

> 官方：[getDeliveryChallanDocument](https://developer-docs.amazon.com/sp-api/reference/getdeliverychallandocument)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/deliveryChallanDocument"
}'
```


## 接口：列出送达窗口选项（listDeliveryWindowOptions）

> 官方：[listDeliveryWindowOptions](https://developer-docs.amazon.com/sp-api/reference/listdeliverywindowoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/deliveryWindowOptions"
}'
```


## 接口：生成送达窗口选项（generateDeliveryWindowOptions）

> 官方：[generateDeliveryWindowOptions](https://developer-docs.amazon.com/sp-api/reference/generatedeliverywindowoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/deliveryWindowOptions",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：确认送达窗口选项（confirmDeliveryWindowOptions）

> 官方：[confirmDeliveryWindowOptions](https://developer-docs.amazon.com/sp-api/reference/confirmdeliverywindowoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/deliveryWindowOptions/EXAMPLE_deliveryWindowOptionId/confirmation",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出现行货件商品（listShipmentItems）

> 官方：[listShipmentItems](https://developer-docs.amazon.com/sp-api/reference/listshipmentitems)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/items"
}'
```


## 接口：更新货件名称（updateShipmentName）

> 官方：[updateShipmentName](https://developer-docs.amazon.com/sp-api/reference/updateshipmentname)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/name",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出货件托盘（listShipmentPallets）

> 官方：[listShipmentPallets](https://developer-docs.amazon.com/sp-api/reference/listshipmentpallets)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/pallets"
}'
```


## 接口：取消自配送预约（cancelSelfShipAppointment）

> 官方：[cancelSelfShipAppointment](https://developer-docs.amazon.com/sp-api/reference/cancelselfshipappointment)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/selfShipAppointmentCancellation",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：获取自配送预约时段（getSelfShipAppointmentSlots）

> 官方：[getSelfShipAppointmentSlots](https://developer-docs.amazon.com/sp-api/reference/getselfshipappointmentslots)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/selfShipAppointmentSlots"
}'
```


## 接口：生成自配送预约时段（generateSelfShipAppointmentSlots）

> 官方：[generateSelfShipAppointmentSlots](https://developer-docs.amazon.com/sp-api/reference/generateselfshipappointmentslots)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/selfShipAppointmentSlots",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：安排自配送预约（scheduleSelfShipAppointment）

> 官方：[scheduleSelfShipAppointment](https://developer-docs.amazon.com/sp-api/reference/scheduleselfshipappointment)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/selfShipAppointmentSlots/EXAMPLE_slotId/schedule",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：更新货件发货地址（updateShipmentSourceAddress）

> 官方：[updateShipmentSourceAddress](https://developer-docs.amazon.com/sp-api/reference/updateshipmentsourceaddress)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/sourceAddress",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：更新货件跟踪信息（updateShipmentTrackingDetails）

> 官方：[updateShipmentTrackingDetails](https://developer-docs.amazon.com/sp-api/reference/updateshipmenttrackingdetails)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/shipments/EXAMPLE_shipmentId/trackingDetails",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出运输选项（listTransportationOptions）

> 官方：[listTransportationOptions](https://developer-docs.amazon.com/sp-api/reference/listtransportationoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/transportationOptions"
}'
```


## 接口：生成运输选项（generateTransportationOptions）

> 官方：[generateTransportationOptions](https://developer-docs.amazon.com/sp-api/reference/generatetransportationoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/transportationOptions",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：确认运输选项（confirmTransportationOptions）

> 官方：[confirmTransportationOptions](https://developer-docs.amazon.com/sp-api/reference/confirmtransportationoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/inboundPlans/EXAMPLE_inboundPlanId/transportationOptions/confirmation",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出商品合规信息（listItemComplianceDetails）

> 官方：[listItemComplianceDetails](https://developer-docs.amazon.com/sp-api/reference/listitemcompliancedetails)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/items/compliance`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/items/compliance",
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}'
```


## 接口：更新商品合规信息（updateItemComplianceDetails）

> 官方：[updateItemComplianceDetails](https://developer-docs.amazon.com/sp-api/reference/updateitemcompliancedetails)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/items/compliance`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/items/compliance",
  "queryString": "marketplaceId=ATVPDKIKX0DER",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：创建站点商品标签（createMarketplaceItemLabels）

> 官方：[createMarketplaceItemLabels](https://developer-docs.amazon.com/sp-api/reference/createmarketplaceitemlabels)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/items/labels`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/items/labels",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：列出商品预处理信息（listPrepDetails）

> 官方：[listPrepDetails](https://developer-docs.amazon.com/sp-api/reference/listprepdetails)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/items/prepDetails`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/items/prepDetails",
  "queryString": "marketplaceId=ATVPDKIKX0DER&mskus=EXAMPLE_SKU"
}'
```


## 接口：设置商品预处理信息（setPrepDetails）

> 官方：[setPrepDetails](https://developer-docs.amazon.com/sp-api/reference/setprepdetails)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/items/prepDetails`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/items/prepDetails",
  "body": "<按本接口官方模型填入完整 JSON 字符串>",
  "contentType": "application/json"
}'
```


## 接口：查询入仓异步操作状态（getInboundOperationStatus）

> 官方：[getInboundOperationStatus](https://developer-docs.amazon.com/sp-api/reference/getinboundoperationstatus)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `inbound/fba/2024-03-20/operations/{operationId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-script-usage.md](inbound-script-usage.md)。

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
- 按入仓状态机调用；409/422 检查状态与参数。generate* 等异步操作返回标识后通过 getInboundOperationStatus 查询，不擅自高频轮询，先征得用户同意。
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
  "path": "inbound/fba/2024-03-20/operations/EXAMPLE_operationId"
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
