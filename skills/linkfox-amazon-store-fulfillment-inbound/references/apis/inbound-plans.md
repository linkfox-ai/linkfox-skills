# FBA 入仓：入库计划 接口说明

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



## 接口：列出入库计划（listInboundPlans）

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

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-plans-script-usage.md](inbound-plans-script-usage.md)。

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

- 本操作预期上游 `httpStatus`：200；其他状态保留错误，不解析为业务成功。
- Amazon 400/403/404/409/413/415/422：先修正输入或工作流状态，再由用户决定是否调用；429/500/503 或超时造成结果不确定时先查询状态或只读恢复，不自动重放 POST/PUT。现有网关仅在识别 token 过期时刷新并透明重试一次。
- 450/453/454/459 遵循 [店铺保护与重试](../spapi-protection.md)；453 期间停止该店铺全部 SP-API 调用。
- 展示本页计划及分页范围；已有计划时先只读恢复，不重复创建。


## 接口：创建入库计划（createInboundPlan）

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

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-plans-script-usage.md](inbound-plans-script-usage.md)。

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

- 本操作预期上游 `httpStatus`：202；其他状态保留错误，不解析为业务成功。
- 201/202 仅表示发起成功；查 getInboundOperationStatus，IN_PROGRESS 停止推进，FAILED 展示 operationProblems 并停止下游写入，仅 SUCCESS 继续。
- Amazon 400/403/404/409/413/415/422：先修正输入或工作流状态，再由用户决定是否调用；429/500/503 或超时造成结果不确定时先查询状态或只读恢复，不自动重放 POST/PUT。现有网关仅在识别 token 过期时刷新并透明重试一次。
- 450/453/454/459 遵循 [店铺保护与重试](../spapi-protection.md)；453 期间停止该店铺全部 SP-API 调用。
- 保留 inboundPlanId 和异步 operationId，分别用于后续计划操作与状态查询。创建后修改单个货件发货地址使用 updateShipmentSourceAddress。


## 接口：获取入库计划（getInboundPlan）

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

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-plans-script-usage.md](inbound-plans-script-usage.md)。

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

- 本操作预期上游 `httpStatus`：200；其他状态保留错误，不解析为业务成功。
- Amazon 400/403/404/409/413/415/422：先修正输入或工作流状态，再由用户决定是否调用；429/500/503 或超时造成结果不确定时先查询状态或只读恢复，不自动重放 POST/PUT。现有网关仅在识别 token 过期时刷新并透明重试一次。
- 450/453/454/459 遵循 [店铺保护与重试](../spapi-protection.md)；453 期间停止该店铺全部 SP-API 调用。
- 按当前计划阶段读取装箱、分仓与货件摘要，恢复进度；不因部分字段尚未返回而重复创建计划。


### curl 示例

```bash
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  --header "Content-Type: application/json" \
  --header "User-Agent: LinkFox-Skill/2.0" \
  --data '{"sellerId":"A1SELLER","region":"NA","method":"GET","path":"inbound/fba/2024-03-20/inboundPlans/wf12345678-1234-1234-1234-123456789012"}'
```


## 接口：列出计划箱信息（listInboundPlanBoxes）

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

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-plans-script-usage.md](inbound-plans-script-usage.md)。

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

- 本操作预期上游 `httpStatus`：200；其他状态保留错误，不解析为业务成功。
- Amazon 400/403/404/409/413/415/422：先修正输入或工作流状态，再由用户决定是否调用；429/500/503 或超时造成结果不确定时先查询状态或只读恢复，不自动重放 POST/PUT。现有网关仅在识别 token 过期时刷新并透明重试一次。
- 450/453/454/459 遵循 [店铺保护与重试](../spapi-protection.md)；453 期间停止该店铺全部 SP-API 调用。
- 只展示实际返回的箱信息；空结果应结合装箱阶段解释。


## 接口：取消入库计划（cancelInboundPlan）

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

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-plans-script-usage.md](inbound-plans-script-usage.md)。

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

- 本操作预期上游 `httpStatus`：202；其他状态保留错误，不解析为业务成功。
- 201/202 仅表示发起成功；查 getInboundOperationStatus，IN_PROGRESS 停止推进，FAILED 展示 operationProblems 并停止下游写入，仅 SUCCESS 继续。
- Amazon 400/403/404/409/413/415/422：先修正输入或工作流状态，再由用户决定是否调用；429/500/503 或超时造成结果不确定时先查询状态或只读恢复，不自动重放 POST/PUT。现有网关仅在识别 token 过期时刷新并透明重试一次。
- 450/453/454/459 遵循 [店铺保护与重试](../spapi-protection.md)；453 期间停止该店铺全部 SP-API 调用。
- 执行前展示计划 ID、状态及关联货件并取得明确确认。取消会影响关联货件；已确认运输的运费撤销窗口为 SPD 24 小时、LTL/FTL 1 小时，超时仍可能收费。完成后查询异步状态或计划是否 VOIDED。


## 接口：列出计划商品（listInboundPlanItems）

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

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-plans-script-usage.md](inbound-plans-script-usage.md)。

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

- 本操作预期上游 `httpStatus`：200；其他状态保留错误，不解析为业务成功。
- Amazon 400/403/404/409/413/415/422：先修正输入或工作流状态，再由用户决定是否调用；429/500/503 或超时造成结果不确定时先查询状态或只读恢复，不自动重放 POST/PUT。现有网关仅在识别 token 过期时刷新并透明重试一次。
- 450/453/454/459 遵循 [店铺保护与重试](../spapi-protection.md)；453 期间停止该店铺全部 SP-API 调用。
- package grouping 在确认分仓前可能使用 packingGroupId，确认后使用 shipmentId；保留实际标识，不混用。


## 接口：修改计划名称（updateInboundPlanName）

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

操作所需的脚本输入、路径、查询串与正文构造见 [inbound-plans-script-usage.md](inbound-plans-script-usage.md)。

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

- 本操作预期上游 `httpStatus`：204；其他状态保留错误，不解析为业务成功。
- 204 空 body 是成功，结果字段为 null，不当作 JSON 解析失败。
- Amazon 400/403/404/409/413/415/422：先修正输入或工作流状态，再由用户决定是否调用；429/500/503 或超时造成结果不确定时先查询状态或只读恢复，不自动重放 POST/PUT。现有网关仅在识别 token 过期时刷新并透明重试一次。
- 450/453/454/459 遵循 [店铺保护与重试](../spapi-protection.md)；453 期间停止该店铺全部 SP-API 调用。
- 只修改指定计划名称，不改变其装箱、分仓或运输选择。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-fulfillment-inbound",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
