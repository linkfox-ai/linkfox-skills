# Amazon 店铺买家反馈洞察 接口说明

官方总览：[Customer Feedback API v2024-06-01](https://developer-docs.amazon.com/sp-api/docs/customer-feedback-api-v2024-06-01-use-case-guide)。

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



## 接口：商品评论主题（getItemReviewTopics）

> 官方参考：[getItemReviewTopics](https://developer-docs.amazon.com/sp-api/reference/getitemreviewtopics)。Customer Feedback 版本为 `2024-06-01`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `customerFeedback/2024-06-01/items/{asin}/reviews/topics`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 只有 Amazon 上游 `httpStatus` 为 200 才解析为本操作的业务结果，不能仅凭 LinkFox 外层 HTTP 成功判断 Amazon 成功。
- 上游 403 表示角色、授权或站点不支持，不归为余额不足；网关 1005 须结合 `errmsg` 判断：授权失效时通过 `linkfox-amazon-store-auth` 重新授权；路径或方法被拒绝时检查 `customerFeedback/2024-06-01/` 路径白名单与 GET 放行规则。
- 450 / 453 / 454 / 459 的触发阈值、冷却、禁止绕过与恢复规则见 [店铺保护与重试](spapi-protection.md)。453 期间停止该店铺全部 SP-API 调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"A1EXAMPLE","region":"NA","method":"GET","path":"customerFeedback/2024-06-01/items/B0EXAMPLE01/reviews/topics","queryString":"marketplaceId=ATVPDKIKX0DER&sortBy=MENTIONS"}'
```


## 接口：商品所属类目（getItemBrowseNode）

> 官方参考：[getItemBrowseNode](https://developer-docs.amazon.com/sp-api/reference/getitembrowsenode)。Customer Feedback 版本为 `2024-06-01`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `customerFeedback/2024-06-01/items/{asin}/browseNode`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 只有 Amazon 上游 `httpStatus` 为 200 才解析为本操作的业务结果，不能仅凭 LinkFox 外层 HTTP 成功判断 Amazon 成功。
- 上游 403 表示角色、授权或站点不支持，不归为余额不足；网关 1005 须结合 `errmsg` 判断：授权失效时通过 `linkfox-amazon-store-auth` 重新授权；路径或方法被拒绝时检查 `customerFeedback/2024-06-01/` 路径白名单与 GET 放行规则。
- 450 / 453 / 454 / 459 的触发阈值、冷却、禁止绕过与恢复规则见 [店铺保护与重试](spapi-protection.md)。453 期间停止该店铺全部 SP-API 调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"A1EXAMPLE","region":"NA","method":"GET","path":"customerFeedback/2024-06-01/items/B0EXAMPLE01/browseNode","queryString":"marketplaceId=ATVPDKIKX0DER"}'
```


## 接口：商品评论趋势（getItemReviewTrends）

> 官方参考：[getItemReviewTrends](https://developer-docs.amazon.com/sp-api/reference/getitemreviewtrends)。Customer Feedback 版本为 `2024-06-01`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `customerFeedback/2024-06-01/items/{asin}/reviews/trends`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 只有 Amazon 上游 `httpStatus` 为 200 才解析为本操作的业务结果，不能仅凭 LinkFox 外层 HTTP 成功判断 Amazon 成功。
- 上游 403 表示角色、授权或站点不支持，不归为余额不足；网关 1005 须结合 `errmsg` 判断：授权失效时通过 `linkfox-amazon-store-auth` 重新授权；路径或方法被拒绝时检查 `customerFeedback/2024-06-01/` 路径白名单与 GET 放行规则。
- 450 / 453 / 454 / 459 的触发阈值、冷却、禁止绕过与恢复规则见 [店铺保护与重试](spapi-protection.md)。453 期间停止该店铺全部 SP-API 调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"A1EXAMPLE","region":"NA","method":"GET","path":"customerFeedback/2024-06-01/items/B0EXAMPLE01/reviews/trends","queryString":"marketplaceId=ATVPDKIKX0DER"}'
```


## 接口：类目评论主题（getBrowseNodeReviewTopics）

> 官方参考：[getBrowseNodeReviewTopics](https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereviewtopics)。Customer Feedback 版本为 `2024-06-01`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/topics`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 只有 Amazon 上游 `httpStatus` 为 200 才解析为本操作的业务结果，不能仅凭 LinkFox 外层 HTTP 成功判断 Amazon 成功。
- 上游 403 表示角色、授权或站点不支持，不归为余额不足；网关 1005 须结合 `errmsg` 判断：授权失效时通过 `linkfox-amazon-store-auth` 重新授权；路径或方法被拒绝时检查 `customerFeedback/2024-06-01/` 路径白名单与 GET 放行规则。
- 450 / 453 / 454 / 459 的触发阈值、冷却、禁止绕过与恢复规则见 [店铺保护与重试](spapi-protection.md)。453 期间停止该店铺全部 SP-API 调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"A1EXAMPLE","region":"NA","method":"GET","path":"customerFeedback/2024-06-01/browseNodes/123456/reviews/topics","queryString":"marketplaceId=ATVPDKIKX0DER&sortBy=MENTIONS"}'
```


## 接口：类目评论趋势（getBrowseNodeReviewTrends）

> 官方参考：[getBrowseNodeReviewTrends](https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereviewtrends)。Customer Feedback 版本为 `2024-06-01`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/trends`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 只有 Amazon 上游 `httpStatus` 为 200 才解析为本操作的业务结果，不能仅凭 LinkFox 外层 HTTP 成功判断 Amazon 成功。
- 上游 403 表示角色、授权或站点不支持，不归为余额不足；网关 1005 须结合 `errmsg` 判断：授权失效时通过 `linkfox-amazon-store-auth` 重新授权；路径或方法被拒绝时检查 `customerFeedback/2024-06-01/` 路径白名单与 GET 放行规则。
- 450 / 453 / 454 / 459 的触发阈值、冷却、禁止绕过与恢复规则见 [店铺保护与重试](spapi-protection.md)。453 期间停止该店铺全部 SP-API 调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"A1EXAMPLE","region":"NA","method":"GET","path":"customerFeedback/2024-06-01/browseNodes/123456/reviews/trends","queryString":"marketplaceId=ATVPDKIKX0DER"}'
```


## 接口：类目退货主题（getBrowseNodeReturnTopics）

> 官方参考：[getBrowseNodeReturnTopics](https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereturntopics)。Customer Feedback 版本为 `2024-06-01`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/topics`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 只有 Amazon 上游 `httpStatus` 为 200 才解析为本操作的业务结果，不能仅凭 LinkFox 外层 HTTP 成功判断 Amazon 成功。
- 上游 403 表示角色、授权或站点不支持，不归为余额不足；网关 1005 须结合 `errmsg` 判断：授权失效时通过 `linkfox-amazon-store-auth` 重新授权；路径或方法被拒绝时检查 `customerFeedback/2024-06-01/` 路径白名单与 GET 放行规则。
- 450 / 453 / 454 / 459 的触发阈值、冷却、禁止绕过与恢复规则见 [店铺保护与重试](spapi-protection.md)。453 期间停止该店铺全部 SP-API 调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"A1EXAMPLE","region":"NA","method":"GET","path":"customerFeedback/2024-06-01/browseNodes/123456/returns/topics","queryString":"marketplaceId=ATVPDKIKX0DER&sortBy=MENTIONS"}'
```


## 接口：类目退货趋势（getBrowseNodeReturnTrends）

> 官方参考：[getBrowseNodeReturnTrends](https://developer-docs.amazon.com/sp-api/reference/getbrowsenodereturntrends)。Customer Feedback 版本为 `2024-06-01`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/trends`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 只有 Amazon 上游 `httpStatus` 为 200 才解析为本操作的业务结果，不能仅凭 LinkFox 外层 HTTP 成功判断 Amazon 成功。
- 上游 403 表示角色、授权或站点不支持，不归为余额不足；网关 1005 须结合 `errmsg` 判断：授权失效时通过 `linkfox-amazon-store-auth` 重新授权；路径或方法被拒绝时检查 `customerFeedback/2024-06-01/` 路径白名单与 GET 放行规则。
- 450 / 453 / 454 / 459 的触发阈值、冷却、禁止绕过与恢复规则见 [店铺保护与重试](spapi-protection.md)。453 期间停止该店铺全部 SP-API 调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"A1EXAMPLE","region":"NA","method":"GET","path":"customerFeedback/2024-06-01/browseNodes/123456/returns/trends","queryString":"marketplaceId=ATVPDKIKX0DER"}'
```


## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-customer-feedback",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
