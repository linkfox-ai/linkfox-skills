# Amazon 店铺 Feeds 接口说明

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



## 接口：创建 Feed 文档（createFeedDocument）

> 官方：[createFeedDocument](https://developer-docs.amazon.com/sp-api/reference/createfeeddocument)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `feeds/2021-06-30/documents`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 常见上游成功为 201。上传 URL 有时效；过期时重新创建文档。
- `403` 表示权限或 feedType 未授权；`1005` 须结合 errmsg 区分路径/方法白名单拒绝与授权失效，按“公共规则 → 网关错误响应”排查；`429` 应降低请求频率。
- 收到 `450` / `453` / `454` / `459` 时遵循 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil，453 停止全店 SP-API；不得换脚本绕过冷却。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "region": "NA",
  "sellerId": "A1EXAMPLE",
  "path": "feeds/2021-06-30/documents",
  "method": "POST",
  "body": "{\"contentType\":\"text/tab-separated-values; charset=UTF-8\"}",
  "contentType": "application/json"
}'
```


## 接口：获取 Feed 文档（getFeedDocument）

> 官方：[getFeedDocument](https://developer-docs.amazon.com/sp-api/reference/getfeeddocument)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `feeds/2021-06-30/documents/{feedDocumentId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 常见上游成功为 200。下载 URL 不经过网关，不把地址本身当成已下载的结果内容。
- `403` 表示权限或 feedType 未授权；`1005` 须结合 errmsg 区分路径/方法白名单拒绝与授权失效，按“公共规则 → 网关错误响应”排查；`429` 应降低请求频率。
- 收到 `450` / `453` / `454` / `459` 时遵循 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil，453 停止全店 SP-API；不得换脚本绕过冷却。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "region": "NA",
  "sellerId": "A1EXAMPLE",
  "path": "feeds/2021-06-30/documents/example-document-id",
  "method": "GET",
  "queryString": "enableContentEncodingUrlHeader=true"
}'
```


## 接口：提交 Feed（createFeed）

> 官方：[createFeed](https://developer-docs.amazon.com/sp-api/reference/createfeed)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `feeds/2021-06-30/feeds`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 常见上游成功为 202，表示任务被接受，不等于文件处理成功；写入结果不确定时先查询，不能直接重放。
- `403` 表示权限或 feedType 未授权；`1005` 须结合 errmsg 区分路径/方法白名单拒绝与授权失效，按“公共规则 → 网关错误响应”排查；`429` 应降低请求频率。
- 收到 `450` / `453` / `454` / `459` 时遵循 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil，453 停止全店 SP-API；不得换脚本绕过冷却。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "region": "NA",
  "sellerId": "A1EXAMPLE",
  "path": "feeds/2021-06-30/feeds",
  "method": "POST",
  "body": "{\"feedType\":\"POST_FLAT_FILE_INVLOADER_DATA\",\"marketplaceIds\":[\"ATVPDKIKX0DER\"],\"inputFeedDocumentId\":\"example-document-id\"}",
  "contentType": "application/json"
}'
```


## 接口：查询 Feed（getFeed）

> 官方：[getFeed](https://developer-docs.amazon.com/sp-api/reference/getfeed)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `feeds/2021-06-30/feeds/{feedId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 常见上游成功为 200。依据 processingStatus 展示进展；DONE 仍需读取结果文档判断逐条处理结果。不得自动无限轮询。
- `403` 表示权限或 feedType 未授权；`1005` 须结合 errmsg 区分路径/方法白名单拒绝与授权失效，按“公共规则 → 网关错误响应”排查；`429` 应降低请求频率。
- 收到 `450` / `453` / `454` / `459` 时遵循 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil，453 停止全店 SP-API；不得换脚本绕过冷却。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "region": "NA",
  "sellerId": "A1EXAMPLE",
  "path": "feeds/2021-06-30/feeds/example-feed-id",
  "method": "GET"
}'
```


## 接口：列出 Feed（getFeeds）

> 官方：[getFeeds](https://developer-docs.amazon.com/sp-api/reference/getfeeds)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `feeds/2021-06-30/feeds`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 常见上游成功为 200。返回空列表时展示当前检索范围，不自动翻页或扩大条件。getFeeds 有独立 usage plan，429 时降频。
- `403` 表示权限或 feedType 未授权；`1005` 须结合 errmsg 区分路径/方法白名单拒绝与授权失效，按“公共规则 → 网关错误响应”排查；`429` 应降低请求频率。
- 收到 `450` / `453` / `454` / `459` 时遵循 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil，453 停止全店 SP-API；不得换脚本绕过冷却。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "region": "NA",
  "sellerId": "A1EXAMPLE",
  "path": "feeds/2021-06-30/feeds",
  "method": "GET",
  "queryString": "feedTypes=POST_FLAT_FILE_INVLOADER_DATA&pageSize=10"
}'
```


## 接口：取消 Feed（cancelFeed）

> 官方：[cancelFeed](https://developer-docs.amazon.com/sp-api/reference/cancelfeed)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `feeds/2021-06-30/feeds/{feedId}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 上游成功可为 204，body 可能为空；脚本保留网关响应，不添加解析业务对象。取消是否生效以上游实际返回与后续查询为准，失败不反复提交。
- `403` 表示权限或 feedType 未授权；`1005` 须结合 errmsg 区分路径/方法白名单拒绝与授权失效，按“公共规则 → 网关错误响应”排查；`429` 应降低请求频率。
- 收到 `450` / `453` / `454` / `459` 时遵循 [店铺保护与重试](spapi-protection.md)。优先 retryAfter / blockedUntil，453 停止全店 SP-API；不得换脚本绕过冷却。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "region": "NA",
  "sellerId": "A1EXAMPLE",
  "path": "feeds/2021-06-30/feeds/example-feed-id",
  "method": "DELETE"
}'
```


## 非 LinkFox 操作：上传 Feed 文档内容

### 调用规范

`scripts/upload_feed_document.py` 对 createFeedDocument 返回的 URL 直接 HTTP PUT，超时 300 秒，不经 developerProxy，不发送 LinkFox API Key 或店铺令牌。下载 getFeedDocument 返回的 URL 也另行直接 HTTP GET。

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| uploadUrl | string | 是 | createFeedDocument 返回的预签名 url。 |
| contentType | string | 是 | 须与创建文档时的 MIME 完全一致。 |
| filePath | string | 三选一 | 本地文件路径，支持展开 ~，必须为存在的文件。 |
| content | string | 三选一 | 原始字符串，按 UTF-8 编码；允许空字符串。 |
| contentBase64 | string | 三选一 | Base64 编码内容。 |
| --inline | CLI flag | 否 | 强制完整打印并仍保存响应。 |

JSON 入参必须为对象；格式错误或非对象输入会在请求前以 exit 1 退出并输出错误说明。上传前检查当前目录下实际会话 data 目录可写；不可写时直接报错，不发起 PUT，不回退到其他目录。

应只提供一种内容来源；多项同时存在时，脚本依次优先使用 filePath > contentBase64 > content。上传 URL 有时效，过期需重新创建文档；上传失败检查 URL 与 Content-Type，不归为 SP-API 网关失败。文件 schema 与 feedType 应匹配，以 Amazon 要求为准。脚本不自动重试或自动提交 Feed。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| uploadUrl | string | 实际上传地址。 |
| bytesUploaded | integer | 本次尝试发送的字节数；失败时不代表已上传成功。 |
| httpStatus | integer | 直接 PUT 的 HTTP 状态；连接失败时缺失。 |
| success | boolean | PUT 返回 2xx 时为 true，否则 false。 |
| error | string | HTTP 或连接错误时输出。 |
| details | string | HTTP 错误响应前 2000 字符，如有。 |

### 响应码规则

上传失败时脚本 exit 1，成功时 exit 0。结果使用同一会话落盘和摘要方式，不读取或写入上传缓存。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-feeds",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
