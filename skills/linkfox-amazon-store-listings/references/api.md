# Amazon 店铺刊登与商品类型管理 接口说明

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



## 接口：获取单条刊登（getListingsItem）

> 官方：[getListingsItem](https://developer-docs.amazon.com/sp-api/reference/getlistingsitem)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `listings/2021-08-01/items/{sellerId}/{sku}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析为业务成功；根据上游状态和 body 中的错误说明处理。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。

- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)。453 涉及店铺全部 SP-API；该规则统一维护，避免各操作的冷却时间和处理要求不一致。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2/My-Seller-SKU-001",
    "method": "GET",
    "sellerId": "A1BCDEFGHIJK2",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&includedData=summaries,attributes"
  }'
```


## 接口：搜索刊登列表（searchListingsItems）

> 官方：[searchListingsItems](https://developer-docs.amazon.com/sp-api/reference/searchlistingsitems)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `listings/2021-08-01/items/{sellerId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析为业务成功；根据上游状态和 body 中的错误说明处理。
- 成功响应通常含 items、numberOfResults、pagination 等；下一页令牌以实际 body 为准，传回 pageToken。成功空列表表示本次未匹配到刊登，不等于系统错误。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。

- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)。453 涉及店铺全部 SP-API；该规则统一维护，避免各操作的冷却时间和处理要求不一致。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2",
    "method": "GET",
    "sellerId": "A1BCDEFGHIJK2",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&pageSize=10&sortBy=lastUpdatedDate&sortOrder=DESC&includedData=summaries"
  }'
```


## 接口：部分更新刊登（patchListingsItem）

> 官方：[patchListingsItem](https://developer-docs.amazon.com/sp-api/reference/patchlistingsitem)

仅支持对 **顶层** listing 属性做 JSON Patch；嵌套属性 patch 行为以 Amazon 文档为准。**Vendor** 场景下 **`delete`** 可能返回 **400**（官方说明）。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `listings/2021-08-01/items/{sellerId}/{sku}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析为业务成功；根据上游状态和 body 中的错误说明处理。
- 写请求返回 200 仅表示已理解请求；须解析 body 中的 status、issues 等确认是否接受，不能直接宣布商品已可销售。结果不确定时先查询刊登状态，不直接重放写请求。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。

- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)。453 涉及店铺全部 SP-API；该规则统一维护，避免各操作的冷却时间和处理要求不一致。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2/My-Seller-SKU-001",
    "method": "PATCH",
    "sellerId": "A1BCDEFGHIJK2",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&includedData=issues",
    "contentType": "application/json",
    "body": "{\"productType\":\"LUGGAGE\",\"patches\":[{\"op\":\"replace\",\"path\":\"/attributes/item_name\",\"value\":[{\"value\":\"Example\",\"marketplace_id\":\"ATVPDKIKX0DER\"}]}]}"
  }'
```


## 接口：创建或全量更新刊登（putListingsItem）

> 官方：[putListingsItem](https://developer-docs.amazon.com/sp-api/reference/putlistingsitem)

**创建**新刊登或对现有刊登做**全量**更新（非部分 patch）；请求体为完整 **`attributes`** 对象，须符合该 **productType** 的 JSON Schema。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `listings/2021-08-01/items/{sellerId}/{sku}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析为业务成功；根据上游状态和 body 中的错误说明处理。
- 写请求返回 200 仅表示已理解请求；须解析 body 中的 status、issues 等确认是否接受，不能直接宣布商品已可销售。结果不确定时先查询刊登状态，不直接重放写请求。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。

- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)。453 涉及店铺全部 SP-API；该规则统一维护，避免各操作的冷却时间和处理要求不一致。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2/My-Seller-SKU-001",
    "method": "PUT",
    "sellerId": "A1BCDEFGHIJK2",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&includedData=issues",
    "contentType": "application/json",
    "body": "{\"productType\":\"LUGGAGE\",\"requirements\":\"LISTING\",\"attributes\":{\"item_name\":[{\"value\":\"Example Title\",\"marketplace_id\":\"ATVPDKIKX0DER\"}]}}"
  }'
```


## 接口：删除刊登（deleteListingsItem）

> 官方：[deleteListingsItem](https://developer-docs.amazon.com/sp-api/reference/deletelistingsitem)

删除指定 **marketplace** 下该 **sellerId + sku** 的刊登项；**无请求体**。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `listings/2021-08-01/items/{sellerId}/{sku}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
| method | string | 是 | 本操作上游方法为 `DELETE`；LinkFox 外层始终 POST。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析为业务成功；根据上游状态和 body 中的错误说明处理。
- 写请求返回 200 仅表示已理解请求；须解析 body 中的 status、issues 等确认是否接受，不能直接宣布商品已可销售。结果不确定时先查询刊登状态，不直接重放写请求。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。

- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)。453 涉及店铺全部 SP-API；该规则统一维护，避免各操作的冷却时间和处理要求不一致。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/items/A1BCDEFGHIJK2/My-Seller-SKU-001",
    "method": "DELETE",
    "sellerId": "A1BCDEFGHIJK2",
    "queryString": "marketplaceIds=ATVPDKIKX0DER"
  }'
```


## 接口：查询刊登限制（getListingsRestrictions）

> 官方：[getListingsRestrictions](https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions)

返回目录 **ASIN** 在指定 **sellerId** 与 **marketplaceIds** 下的刊登限制。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `listings/2021-08-01/restrictions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析为业务成功；根据上游状态和 body 中的错误说明处理。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 本接口针对 ASIN 的刊登限制；不能将没有返回限制直接解释为已经完成上架。

- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)。453 涉及店铺全部 SP-API；该规则统一维护，避免各操作的冷却时间和处理要求不一致。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "path": "listings/2021-08-01/restrictions",
    "method": "GET",
    "sellerId": "A1BCDEFGHIJK2",
    "queryString": "asin=B08N5WRWNW&sellerId=A1BCDEFGHIJK2&marketplaceIds=ATVPDKIKX0DER"
  }'
```


## 接口：搜索商品类型（searchDefinitionsProductTypes）

> 官方：[searchDefinitionsProductTypes](https://developer-docs.amazon.com/sp-api/reference/searchdefinitionsproducttypes)

搜索可用的 **product type** 定义列表。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `definitions/2020-09-01/productTypes`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析为业务成功；根据上游状态和 body 中的错误说明处理。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。

- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)。453 涉及店铺全部 SP-API；该规则统一维护，避免各操作的冷却时间和处理要求不一致。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "path": "definitions/2020-09-01/productTypes",
    "method": "GET",
    "sellerId": "A1BCDEFGHIJK2",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&keywords=luggage,suitcase"
  }'
```


## 接口：获取商品类型定义（getDefinitionsProductType）

> 官方：[getDefinitionsProductType](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype)

按 **productType** 名称拉取 JSON Schema 定义。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `definitions/2020-09-01/productTypes/{productType}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游 `httpStatus` 不为 200 时不解析为业务成功；根据上游状态和 body 中的错误说明处理。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。

- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)。453 涉及店铺全部 SP-API；该规则统一维护，避免各操作的冷却时间和处理要求不一致。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "path": "definitions/2020-09-01/productTypes/LUGGAGE",
    "method": "GET",
    "sellerId": "A1BCDEFGHIJK2",
    "queryString": "marketplaceIds=ATVPDKIKX0DER&requirements=LISTING&productTypeVersion=LATEST"
  }'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-listings",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
