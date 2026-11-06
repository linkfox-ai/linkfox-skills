# FBA 入仓：保留的 v0 查询与文档 接口说明

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



## 接口：获取旧版预处理说明（getPrepInstructions）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/inbound/v0/prepInstructions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [legacy-v0-script-usage.md](legacy-v0-script-usage.md)。

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
- 通常提供 sellerSKUList 或 asinList 至少一组，各最多 50；不静默替换标识。数组使用 v0 CSV 格式，不套用 v2024 MSKU 重复 key。


## 接口：获取箱唛标签（getLabels）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/inbound/v0/shipments/{shipmentId}/labels`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [legacy-v0-script-usage.md](legacy-v0-script-usage.md)。

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
- v2024 流程先从 getShipment 取得 shipmentConfirmationId 作为 v0 path 的 shipmentId，不直接使用 38 字符流程 ID。packageLabelsToPrint 与 listShipmentBoxes.boxId 一致，否则可能 IncorrectPackageIdentifier。Non-Partnered LTL 标签需 pageSize 与 pageStartIndex，pageSize 最大 1000；每个 pallet 返回四张相同标签。DownloadURL 约 15 秒有效，需要文件时立即下载本次 HTTPS URL，不接受任意 URL。


## 接口：获取提单（getBillOfLading）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/inbound/v0/shipments/{shipmentId}/billOfLading`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [legacy-v0-script-usage.md](legacy-v0-script-usage.md)。

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
- v2024 流程使用 getShipment.shipmentConfirmationId 作为 v0 path 的 shipmentId，不直接使用 38 字符流程 ID。DownloadURL 约 15 秒有效，需要文件时立即下载本次 HTTPS URL，不接受任意 URL。


## 接口：查询旧版货件（getShipments）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/inbound/v0/shipments`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [legacy-v0-script-usage.md](legacy-v0-script-usage.md)。

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
- v0 参数名按 Query 表映射为 PascalCase；SHIPMENT 使用状态或货件 ID 列表，DATE_RANGE 使用完整时间区间，NEXT_TOKEN 仅继续上一页，不混用其他模式字段。


## 接口：按旧版货件查询商品（getShipmentItemsByShipmentId）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/inbound/v0/shipments/{shipmentId}/items`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [legacy-v0-script-usage.md](legacy-v0-script-usage.md)。

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
- 使用原生 v0 shipmentId。marketplaceId 已废弃，不传；保留本次 ItemData 和 NextToken。


## 接口：查询旧版货件商品（getShipmentItems）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `fba/inbound/v0/shipments/{shipmentId}/items`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `GET`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [legacy-v0-script-usage.md](legacy-v0-script-usage.md)。

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
- v0 参数名按 Query 表映射为 PascalCase；DATE_RANGE 使用完整时间区间，NEXT_TOKEN 只继续上一页，不混入新日期筛选。

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
