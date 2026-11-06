# Amazon 店铺订单查询与履约管理 接口说明

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



## 接口：搜索订单（searchOrders）

> 官方：[searchOrders](https://developer-docs.amazon.com/sp-api/reference/searchorders)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/2026-01-01/orders`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 读取操作上游 httpStatus 为 200 时解析业务对象；非 200 时保留 developerProxy 与错误 body，不认定为成功。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/2026-01-01/orders",
  "method": "GET",
  "queryString": "marketplaceIds=ATVPDKIKX0DER&lastUpdatedAfter=2026-05-01T00%3A00%3A00Z"
}'
```


## 接口：获取订单详情（getOrder）

> 官方：[getOrder](https://developer-docs.amazon.com/sp-api/reference/getorder-3)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/2026-01-01/orders/{orderId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 读取操作上游 httpStatus 为 200 时解析业务对象；非 200 时保留 developerProxy 与错误 body，不认定为成功。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/2026-01-01/orders/123-1234567-1234567",
  "method": "GET",
  "queryString": "includedData=FULFILLMENT&includedData=PACKAGES"
}'
```


## 接口：获取订单买家信息（getOrderBuyerInfo）

> 官方：[getOrderBuyerInfo](https://developer-docs.amazon.com/sp-api/reference/getorderbuyerinfo)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/v0/orders/{orderId}/buyerInfo`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 读取操作上游 httpStatus 为 200 时解析业务对象；非 200 时保留 developerProxy 与错误 body，不认定为成功。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 本 v0 接口标记为 deprecated；新集成优先采用 v2026-01-01 searchOrders / getOrder 与 includedData 补齐业务字段。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/v0/orders/123-1234567-1234567/buyerInfo",
  "method": "GET"
}'
```


## 接口：获取收货地址（getOrderAddress）

> 官方：[getOrderAddress](https://developer-docs.amazon.com/sp-api/reference/getorderaddress)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/v0/orders/{orderId}/address`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 读取操作上游 httpStatus 为 200 时解析业务对象；非 200 时保留 developerProxy 与错误 body，不认定为成功。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 本 v0 接口标记为 deprecated；新集成优先采用 v2026-01-01 searchOrders / getOrder 与 includedData 补齐业务字段。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/v0/orders/123-1234567-1234567/address",
  "method": "GET"
}'
```


## 接口：获取订单商品（getOrderItems）

> 官方：[getOrderItems](https://developer-docs.amazon.com/sp-api/reference/getorderitems)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/v0/orders/{orderId}/orderItems`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 读取操作上游 httpStatus 为 200 时解析业务对象；非 200 时保留 developerProxy 与错误 body，不认定为成功。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 本 v0 接口标记为 deprecated；新集成优先采用 v2026-01-01 searchOrders / getOrder 与 includedData 补齐业务字段。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/v0/orders/123-1234567-1234567/orderItems",
  "method": "GET"
}'
```


## 接口：获取订单商品买家信息（getOrderItemsBuyerInfo）

> 官方：[getOrderItemsBuyerInfo](https://developer-docs.amazon.com/sp-api/reference/getorderitemsbuyerinfo)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/v0/orders/{orderId}/orderItems/buyerInfo`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 读取操作上游 httpStatus 为 200 时解析业务对象；非 200 时保留 developerProxy 与错误 body，不认定为成功。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 本 v0 接口标记为 deprecated；新集成优先采用 v2026-01-01 searchOrders / getOrder 与 includedData 补齐业务字段。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/v0/orders/123-1234567-1234567/orderItems/buyerInfo",
  "method": "GET"
}'
```


## 接口：更新配送状态（updateShipmentStatus）

> 官方：[updateShipmentStatus](https://developer-docs.amazon.com/sp-api/reference/updateshipmentstatus)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/v0/orders/{orderId}/shipment`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本操作成功时可能为上游 HTTP 204 且没有 JSON body；按网关及上游状态解释结果，不要求出现业务 JSON。写入结果不确定时先查询订单状态，不直接重放。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/v0/orders/123-1234567-1234567/shipment",
  "method": "POST",
  "body": "{\"marketplaceId\": \"ATVPDKIKX0DER\", \"shipmentStatus\": \"ReadyForPickup\"}",
  "contentType": "application/json"
}'
```


## 接口：获取管制订单信息（getOrderRegulatedInfo）

> 官方：[getOrderRegulatedInfo](https://developer-docs.amazon.com/sp-api/reference/getorderregulatedinfo)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/v0/orders/{orderId}/regulatedInfo`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 读取操作上游 httpStatus 为 200 时解析业务对象；非 200 时保留 developerProxy 与错误 body，不认定为成功。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- Accept 等头若需特化，取决于网关是否支持透传；当前脚本不附加额外 Amazon 请求头。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/v0/orders/123-1234567-1234567/regulatedInfo",
  "method": "GET"
}'
```


## 接口：更新买家核验状态（updateVerificationStatus）

> 官方：[updateVerificationStatus](https://developer-docs.amazon.com/sp-api/reference/updateverificationstatus)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/v0/orders/{orderId}/regulatedInfo`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PATCH`；LinkFox 外层始终 POST。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本操作成功时可能为上游 HTTP 204 且没有 JSON body；按网关及上游状态解释结果，不要求出现业务 JSON。写入结果不确定时先查询订单状态，不直接重放。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

以下仅演示网关包装，嵌套对象须替换为满足 Amazon schema 的实际核验或包裹资料，不可按空对象提交。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/v0/orders/123-1234567-1234567/regulatedInfo",
  "method": "PATCH",
  "body": "{\"regulatedOrderVerificationStatus\": {}}",
  "contentType": "application/json"
}'
```


## 接口：确认发货（confirmShipment）

> 官方：[confirmShipment](https://developer-docs.amazon.com/sp-api/reference/confirmshipment)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `orders/v0/orders/{orderId}/shipmentConfirmation`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本操作成功时可能为上游 HTTP 204 且没有 JSON body；按网关及上游状态解释结果，不要求出现业务 JSON。写入结果不确定时先查询订单状态，不直接重放。
- errcode=1005 等拒绝转发时，需要后端检查 `orders/v0/...` 与 `orders/2026-01-01/...` 前缀白名单及本操作上游方法支持。
- Orders 及相关角色权限必须有效；部分读取需要 Restricted Data Token（RDT），本技能不实现 RDT，以 Amazon 数据保护政策为准。参考 [Tokens API](https://developer-docs.amazon.com/sp-api/reference/createrestricteddatatoken)。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。

### curl 示例

以下仅演示网关包装，嵌套对象须替换为满足 Amazon schema 的实际核验或包裹资料，不可按空对象提交。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "sellerId": "A1BCDEFGHIJK2",
  "region": "NA",
  "path": "orders/v0/orders/123-1234567-1234567/shipmentConfirmation",
  "method": "POST",
  "body": "{\"packageDetail\": {}}",
  "contentType": "application/json"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-orders",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
