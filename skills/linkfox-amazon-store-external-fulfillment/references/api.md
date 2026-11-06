# Amazon 店铺外部履约管理 接口说明

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



## 接口：按 location 查询或发布库存（batchInventory）

> 官方：[batchInventory](https://developer-docs.amazon.com/sp-api/reference/batchinventory)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/inventory/2024-09-11/inventories`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。
- 批量库存常返回上游 `207 Multi-Status`，必须逐条查看 `responses[].status`，不能把整批都报告成功。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/inventory/2024-09-11/inventories",
    "method": "POST",
    "body": "{\"requests\":[{\"method\":\"POST\",\"uri\":\"/inventory/fetch?locationId=DEFAULT&skuId=SKU-1\"}]}",
    "contentType": "application/json"
}'
```

---


## 接口：查询货件列表（getShipments）

> 官方：[getShipments](https://developer-docs.amazon.com/sp-api/reference/getshipments-1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments",
    "method": "GET",
    "queryString": "status=ACCEPTED&locationId=ABCD"
}'
```

---


## 接口：查询单个货件（getShipment）

> 官方：[getShipment](https://developer-docs.amazon.com/sp-api/reference/getshipment-1)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1",
    "method": "GET"
}'
```

---


## 接口：确认或拒绝货件（processShipment）

> 官方：[processShipment](https://developer-docs.amazon.com/sp-api/reference/processshipment)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1",
    "method": "POST",
    "queryString": "operation=CONFIRM"
}'
```

---


## 接口：创建包裹（createPackages）

> 官方：[createPackages](https://developer-docs.amazon.com/sp-api/reference/createpackages)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1/packages",
    "method": "POST",
    "body": "{\"packages\":[]}",
    "contentType": "application/json"
}'
```

示例仅展示网关格式；包裹内容与状态须按实际渠道 schema 补齐，不能把占位或空内容当作可提交业务资料。

---


## 接口：更新包裹（updatePackage）

> 官方：[updatePackage](https://developer-docs.amazon.com/sp-api/reference/updatepackage)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
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

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1/packages/PACKAGE-1",
    "method": "PUT",
    "body": "{}",
    "contentType": "application/json"
}'
```

示例仅展示网关格式；包裹内容与状态须按实际渠道 schema 补齐，不能把占位或空内容当作可提交业务资料。

---


## 接口：更新包裹状态（updatePackageStatus）

> 官方：[updatePackageStatus](https://developer-docs.amazon.com/sp-api/reference/updatepackagestatus)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1/packages/PACKAGE-1",
    "method": "PATCH",
    "body": "{\"status\":\"<渠道允许的状态>\"}",
    "contentType": "application/json"
}'
```

示例仅展示网关格式；包裹内容与状态须按实际渠道 schema 补齐，不能把占位或空内容当作可提交业务资料。

---


## 接口：查询配送选项（retrieveShippingOptions）

> 官方：[retrieveShippingOptions](https://developer-docs.amazon.com/sp-api/reference/retrieveshippingoptions)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}/shippingOptions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1/shippingOptions",
    "method": "GET",
    "queryString": "packageId=PACKAGE-1"
}'
```

---


## 接口：生成发票（generateInvoice）

> 官方：[generateInvoice](https://developer-docs.amazon.com/sp-api/reference/generateinvoice)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1/invoice",
    "method": "POST"
}'
```

---


## 接口：读取发票（retrieveInvoice）

> 官方：[retrieveInvoice](https://developer-docs.amazon.com/sp-api/reference/retrieveinvoice)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1/invoice",
    "method": "GET"
}'
```

---


## 接口：生成或重新生成面单（generateShipLabels）

> 官方：[generateShipLabels](https://developer-docs.amazon.com/sp-api/reference/generateshiplabels)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/shipments/{shipmentId}/shipLabels`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `PUT`；LinkFox 外层始终 POST。 |
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

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/shipments/SHIPMENT-1/shipLabels",
    "method": "PUT",
    "queryString": "operation=GENERATE"
}'
```

---


## 接口：查询退货列表（listReturns）

> 官方：[listReturns](https://developer-docs.amazon.com/sp-api/reference/listreturns)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/returns`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/returns",
    "method": "GET",
    "queryString": "status=CREATED"
}'
```

---


## 接口：查询单个退货（getReturn）

> 官方：[getReturn](https://developer-docs.amazon.com/sp-api/reference/getreturn)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `externalFulfillment/2024-09-11/returns/{returnId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 网关正常后，再检查 Amazon `httpStatus`；脚本兼容本接口上游 `200 / 207 / 204` 成功状态（含 204 空正文）。网关 errcode 成功不代表上游成功；上游失败时保留完整错误，不标记 success。
- `1005` 须结合 `errmsg` 判断：路径或方法被拒绝时，由后端检查 `externalFulfillment/` 前缀与本操作方法是否放行；授权信息失效时，重新完成店铺授权。
- `403` 应检查角色、allowlist、签名与店铺授权，不当作充值问题；`409 / 422` 应检查货件当前状态及参数，避免状态机冲突；`429` 降速后继续须先征得用户同意。
- 收到 `450 / 453 / 454 / 459` 时遵循 [店铺保护与重试](spapi-protection.md)；453 期间停止该店铺全部 SP-API。写入结果不确定时先查状态，不直接重放。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "externalFulfillment/2024-09-11/returns/RETURN-1",
    "method": "GET"
}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-external-fulfillment",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
