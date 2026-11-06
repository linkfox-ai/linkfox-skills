# Amazon 店铺 A+ 内容管理 接口说明

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



### 高级 A+ 与品牌故事文档

创建、更新及 ASIN 校验都将完整文档放进上游请求体的 `contentDocument`。脚本接收该对象并将外层请求体序列化到 `developerProxy.body`；直接调用网关时也应传 JSON 字符串。文档类型、模块字段和可用样例见 [高级 A+ 与品牌故事模块参考](modules.md)。

列表按 `contentMetadataRecords[].contentMetadata.badgeSet` 识别 `PREMIUM`，回读用 `CONTENTS` 和 `METADATA`。发布记录中的 `EBC` 不能区分标准与高级 A+；品牌故事以回读文档的 `contentType: BrandStory` 确认。若外层网关成功、内层 `httpStatus` 为 `403`，保留上游错误并核对当前店铺的 A+ 访问权限。

### Media 上游响应与状态

`createMedia` 和 `getMedia` 的成功响应都由 `Media`、`MediaInfo` 和基础 A+ 警告字段组成。下表描述的是解码后的上游 JSON，网关仍将原文放在 `body` 字符串中。具名脚本解码字段分别为 `createMediaResponse`、`getMediaResponse`。媒体 ID、状态、配对和问题字段按实际响应保留；输出可能含临时访问地址，不要对外分享。 [官方模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/aplus-content-api-model/aplusContent_2020-11-01.json)

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| mediaId | string | 是 | 当前媒体 ID，后续回读和视频组件引用此值。 |
| mediaType | string | 是 | `IMAGE` 或 `VIDEO`。 |
| title | string | 是 | 图片标题或文件名；视频顶层标题来自原始文件名，视频配对标题见 relatedMedia。 |
| descriptions | array<object> | 否 | 视频各语言的无障碍描述，图片没有此字段。 |
| descriptions[].locale | string | 是 | 描述对应的语言。 |
| descriptions[].value | string | 是 | 无障碍描述正文。 |
| status | array<string> | 是 | 官方模型要求至少一项且唯一；生产实测在多个配对阶段不一致时顶层可能返回空数组。脚本保留空数组并给出本地 resultWarnings，表示汇总状态未知，应分别检查 relatedMedia 状态，不能据此判为 AVAILABLE。处理阶段与后续责任方可同时出现。 |
| mediaUrl | string | 否 | 临时 CDN 访问地址；任何处理阶段均可能返回，不能据此判断媒体可展示。 |
| issues | array<object> | 否 | 当前媒体的问题，字段见下方 Issue 表。 |
| relatedMedia | array<object> | 否 | 媒体配对列表；独立图片可为空。 |
| relatedMedia[].associationType | string | 是 | 当前为 `VIDEO_PAIRING`。 |
| relatedMedia[].title | string | 是 | 视频与缩略图配对的标题。 |
| relatedMedia[].status | array<string> | 是 | 配对自身的处理阶段及责任方，至少一项且唯一。 |
| relatedMedia[].issues | array<object> | 否 | 配对自身的问题，结构同 Issue 表。 |
| relatedMedia[].media | object | 是 | 关联媒体的 `MediaInfo`，包含上表 mediaId、mediaType、title、descriptions、status、mediaUrl、issues，必填性相同；不再嵌套 relatedMedia。 |
| warnings | array<object> | 否 | 基础 A+ 警告列表，须结合当前结果解释。 |
| warnings[].code | string | 是 | 警告代码。 |
| warnings[].message | string | 是 | 警告说明。 |
| warnings[].details | string | 否 | 额外诊断信息。 |

| Issue 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| code | string | 是 | 问题代码。 |
| message | string | 是 | 问题说明。 |
| severity | string | 是 | `ERROR` 阻止发布，`WARNING` 需要审查，`INFO` 为附加信息。 |
| propertyNames | array<string> | 否 | 涉及的属性名。 |
| categories | array<string> | 是 | 问题类别，常见 `PROCESSING_ISSUE`、`CONTENT_POLICY`、`METADATA_VALIDATION`；保留实际值。 |

上游失败时，`body` 可能包含以下 SP-API 错误对象或非 JSON 错误原文。保留诊断，不将它作为 Media 成功对象解析。

| 字段 | 类型 | 说明 |
|---|---|---|
| errors | array<object> | 一个或多个上游错误。 |
| errors[].code | string | 上游错误代码。 |
| errors[].message | string | 上游错误说明。 |
| errors[].details | string | 可选的具体约束或权限线索。 |

| status 值 | 含义与后续处理 |
|---|---|
| PENDING_PROCESSING | 转码、校验处理中，稍后回读。 |
| PENDING_REVIEW | 等待内容审核，稍后回读。 |
| UNABLE_TO_PROCESS | 文件处理失败，结合 issues 检查编码、时长、损坏等原因。 |
| NOT_APPROVED | 内容合规审核未通过，结合 issues 处理。 |
| AVAILABLE | 可用于 A+ 展示；使用前同时核对视频和选定配对的状态及 ERROR 问题。 |
| PENDING_AMAZON | 下一步由 Amazon 处理，可与处理阶段并存。 |
| PENDING_SELLING_PARTNER | 下一步需要卖家处理，按 issues 提供线索。 |

媒体注册成功和媒体可展示是两个阶段。`get_media.py` 单次查询，不自动轮询。需等待时按用户任务设定总时限、次数和间隔，到上限后输出媒体 ID、当前状态和续查入口；不因等待超过一轮便重复注册媒体。 [媒体处理流程](https://developer-docs.amazon/sp-api/docs/create-edit-retrieve-aplus-media)

## 接口：搜索 A+ 文档（searchContentDocuments）

> 官方：[searchContentDocuments](https://developer-docs.amazon.com/sp-api/reference/searchcontentdocuments)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentDocuments`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。
- 列表以元数据为主，完整内容需 getContentDocument；保留当前页数据，不因空结果自动翻页。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentDocuments",
    "method": "GET",
    "queryString": "marketplaceId=ATVPDKIKX0DER"
}'
```


## 接口：创建 A+ 文档（createContentDocument）

> 官方：[createContentDocument](https://developer-docs.amazon.com/sp-api/reference/createcontentdocument)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentDocuments`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。

- 下方 curl 中空文档仅示意转发与 JSON 字符串编码，不是可发布的 A+ 模板；实际执行必须替换成符合官方模型的文档。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentDocuments",
    "method": "POST",
    "queryString": "marketplaceId=ATVPDKIKX0DER",
    "body": "{\"contentDocument\": {}}",
    "contentType": "application/json"
}'
```


## 接口：获取 A+ 文档（getContentDocument）

> 官方：[getContentDocument](https://developer-docs.amazon.com/sp-api/reference/getcontentdocument)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。


### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentDocuments/YOUR_KEY",
    "method": "GET",
    "queryString": "marketplaceId=ATVPDKIKX0DER&includedDataSet=CONTENTS,METADATA"
}'
```


## 接口：更新 A+ 文档（updateContentDocument）

> 官方：[updateContentDocument](https://developer-docs.amazon.com/sp-api/reference/updatecontentdocument)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。

- 下方 curl 中空文档仅示意转发与 JSON 字符串编码，不是可发布的 A+ 模板；实际执行必须替换成符合官方模型的文档。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentDocuments/YOUR_KEY",
    "method": "POST",
    "queryString": "marketplaceId=ATVPDKIKX0DER",
    "body": "{\"contentDocument\": {}}",
    "contentType": "application/json"
}'
```


## 接口：列出关联 ASIN（listContentDocumentAsinRelations）

> 官方：[listContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/listcontentdocumentasinrelations)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。


### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentDocuments/YOUR_KEY/asins",
    "method": "GET",
    "queryString": "marketplaceId=ATVPDKIKX0DER"
}'
```


## 接口：全量替换关联 ASIN（postContentDocumentAsinRelations）

> 官方：[postContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentasinrelations)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。
- `asinSet` 是全量替换，不是追加；从集合移除 ASIN 会暂停该 ASIN 的相关内容展示。先核对原集合和最终集合。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentDocuments/YOUR_KEY/asins",
    "method": "POST",
    "queryString": "marketplaceId=ATVPDKIKX0DER",
    "body": "{\"asinSet\": [\"B0XXXXXXXX\"]}",
    "contentType": "application/json"
}'
```


## 接口：校验文档与 ASIN（validateContentDocumentAsinRelations）

> 官方：[validateContentDocumentAsinRelations](https://developer-docs.amazon.com/sp-api/reference/validatecontentdocumentasinrelations)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentAsinValidations`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。

- 下方 curl 中空文档仅示意转发与 JSON 字符串编码，不是可发布的 A+ 模板；实际执行必须替换成符合官方模型的文档。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentAsinValidations",
    "method": "POST",
    "queryString": "marketplaceId=ATVPDKIKX0DER",
    "body": "{\"contentDocument\": {}}",
    "contentType": "application/json"
}'
```


## 接口：查询发布记录（searchContentPublishRecords）

> 官方：[searchContentPublishRecords](https://developer-docs.amazon.com/sp-api/reference/searchcontentpublishrecords)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentPublishRecords`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。


### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentPublishRecords",
    "method": "GET",
    "queryString": "marketplaceId=ATVPDKIKX0DER&asin=B0XXXXXXXX"
}'
```


## 接口：提交审核与发布（postContentDocumentApprovalSubmission）

> 官方：[postContentDocumentApprovalSubmission](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentapprovalsubmission)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/approvalSubmissions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。
- 官方无必填 body，脚本不传 developerProxy.body；提交供审核、批准与发布，不将提交接受解释为已审核通过。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentDocuments/YOUR_KEY/approvalSubmissions",
    "method": "POST",
    "queryString": "marketplaceId=ATVPDKIKX0DER",
    "contentType": "application/json"
}'
```


## 接口：暂停前台展示（postContentDocumentSuspendSubmission）

> 官方：[postContentDocumentSuspendSubmission](https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentsuspendsubmission)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/suspendSubmissions`；相对资源路径，占位段分别做百分号编码，最长 2048 字符。 |
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

- 上游 `httpStatus` 为 200 时解析业务 JSON；其他状态按上游 body 解释，不能因外层成功认定操作成功。应用权限不足导致的 403 不归入账户充值流程。
- 1005 须结合 errmsg 区分授权失效与路径未放行；提示路径未放行时，核对本操作前缀及 sp-api.developer-proxy.allowed-path-prefixes 配置。
- 收到 450 / 453 / 454 / 459 时遵循 [店铺保护与重试](spapi-protection.md)，453 期间停止该店铺全部 SP-API；写入结果不确定时先查状态，不直接重放。
- 请求暂停详情页可见 A+，不删除文档本体或 ASIN 关联；脚本不传 developerProxy.body。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "NA",
    "sellerId": "A1BCDEFGHIJK2",
    "path": "aplus/2020-11-01/contentDocuments/YOUR_KEY/suspendSubmissions",
    "method": "POST",
    "queryString": "marketplaceId=ATVPDKIKX0DER",
    "contentType": "application/json"
}'
```

## 接口：注册图片或视频媒体（createMedia）

> 官方：[createMedia](https://developer-docs.amazon/sp-api/reference/createmedia)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`。
- 应用及开发者档案都需具有 `Product Listing` role、卖家授权和 Media API 访问权限。路径前缀为 `aplus`。A+ 文档读取成功不能替代本操作权限验证。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 当前成员已授权的 Seller ID，最长 64 字符。 |
| region | string | 是 | `NA` / `EU` / `FE`，须与授权记录匹配。 |
| path | string | 是 | `aplus/2020-11-01/media`，相对路径，最长 2048 字符。 |
| method | string | 是 | 上游方法 `POST`；LinkFox 外层仍为 POST。 |
| contentType | string | 否 | 上游正文 MIME，脚本设置 `application/json`，最长 128 字符。 |
| body | string | 是 | 将下表 `CreateMediaRequest` 序列化成 JSON 字符串，最长 1,048,576 字符。 |
| queryString | string | 否 | 本操作不需要站点或其他查询参数；脚本不传。 |

#### 上游 CreateMediaRequest

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| mediaType | string | 是 | `IMAGE` 或 `VIDEO`。 |
| uploadDestinationId | string | 二选一 | 已完成文件上传的 Uploads ID，按上一步原值传入，与 mediaId 互斥。 |
| mediaId | string | 二选一 | 复用已有媒体时使用，与 uploadDestinationId 互斥。 |
| title | string | 否 | 独立图片标题，默认文件名；视频顶层标题来自文件名。 |
| descriptions | array<object> | VIDEO 必填 | 至少一项，语言不重复且受 Amazon 支持。IMAGE 不接受此字段。 |
| descriptions[].locale | string | 是 | 语言，例如 `en-US`。 |
| descriptions[].value | string | 是 | 对应语言的无障碍说明。 |
| relatedMedia | array<object> | VIDEO 必填 | 恰好一条图片配对；IMAGE 忽略此字段。 |
| relatedMedia[].associationType | string | 是 | `VIDEO_PAIRING`。 |
| relatedMedia[].title | string | 是 | 配对标题，至少三个词，不能全部大写。 |
| relatedMedia[].media | object | 是 | 缩略图媒体引用。 |
| relatedMedia[].media.mediaType | string | 是 | `IMAGE`。 |
| relatedMedia[].media.uploadDestinationId | string | 二选一 | 新上传缩略图的原始 Uploads ID，与该对象中的 mediaId 互斥。 |
| relatedMedia[].media.mediaId | string | 二选一 | 已注册的缩略图 ID，与该对象中的 uploadDestinationId 互斥。 |
| relatedMedia[].media.title | string | 否 | 新图片的可选标题，默认文件名。 |

Media API 请求不带 `marketplaceId`。Uploads 申请阶段仍按 Uploads API 要求指定站点。素材必须先成功上传，资源路径统一为 `aplus/2020-11-01/contentDocuments`。脚本输入及正文构造见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | 上游状态，创建成功为 201，相同元数据的幂等复用为 200。 |
| contentType | string | 上游响应 Content-Type。 |
| body | string | 上游原文，解码后的字段见公共规则的“Media 上游响应与状态”。 |
| xAmznRequestId | string | 上游请求标识，可为空。 |
| retryAfter | string | 上游重试提示，可为空；不表示允许自动重放。 |
| xAmznRateLimitLimit | string | 上游实际配额，可为空。 |

### 响应码规则

#### 业务规则

- 网关正常且上游为 200 或 201 时解析媒体 JSON。具名脚本还核对媒体 ID、请求类型及 title、status 的基础结构；复用媒体时返回 ID 须与请求一致。缺失或不匹配时保留 resultValidationError 诊断并非零退出。保留返回的媒体和配对 ID，再依据 status 判断后续阶段。
- 400 时检查 ID 二选一、恰好一条缩略图配对、配对标题、描述语言及已上传的文件。403 时核对卖家授权、Product Listing role 与应用 Media API 准入，保留上游原始错误，不归入充值流程。
- 409 表示相同素材已有不同元数据，先回读已有媒体；如确需改标题或描述，按 Amazon 的 `updateMedia` 合同处理。当前 Skill 的具名入口覆盖注册和回读，不自动修改既有媒体元数据。
- 404 / 410 时核对媒体 ID 及原素材状态；429 参考 Retry-After，500 / 503 或超时导致结果未知时先查已有媒体或幂等状态，避免自动重放写入。
- 上游默认约 10 req/s、burst 10，以实际响应头和分配配额为准。收到 450 / 453 / 454 / 459 按 [店铺保护](spapi-protection.md) 处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"SELLER_ID","region":"NA","method":"POST","path":"aplus/2020-11-01/media","contentType":"application/json","body":"{\"mediaType\":\"IMAGE\",\"uploadDestinationId\":\"THUMBNAIL_UPLOAD_DESTINATION_ID\",\"title\":\"Product demonstration thumbnail\"}"}'
```

## 接口：回读媒体及视频缩略图配对（getMedia）

> 官方：[getMedia](https://developer-docs.amazon/sp-api/reference/getmedia)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`。
- 权限要求同 `createMedia`，请求使用原媒体所属的授权店铺和区域。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 当前成员已授权的 Seller ID，最长 64 字符。 |
| region | string | 是 | `NA` / `EU` / `FE`，须与授权记录匹配。 |
| path | string | 是 | `aplus/2020-11-01/media/{mediaId}`，mediaId 路径段做百分号编码，总长最多 2048 字符。 |
| method | string | 是 | 上游方法 `GET`；LinkFox 外层仍为 POST。 |
| queryString | string | 否 | 可选 `associatedMediaId=<百分号编码后的ID>`，最长 4096 字符，无前导问号。 |
| body | string | 否 | 本操作不传。 |
| contentType | string | 否 | 无正文时不需要。 |

#### 上游路径与查询参数

| 字段 | 位置 | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| mediaId | path | string | 是 | 从 createMedia 等结果取得的原媒体 ID。 |
| associatedMediaId | query | string | 否 | 指定时只返回该缩略图与视频的配对，省略时返回全部关联。 |

本操作不带 `marketplaceId`。脚本参数及编码方式见 [script-usage.md](script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | 上游 200 表示回读成功。 |
| contentType | string | 上游响应 Content-Type。 |
| body | string | 上游原文，解码后字段见公共规则的“Media 上游响应与状态”。 |
| xAmznRequestId | string | 上游请求标识，可为空。 |
| retryAfter | string | 上游重试提示，可为空。 |
| xAmznRateLimitLimit | string | 上游实际配额，可为空。 |

### 响应码规则

#### 业务规则

- 网关正常且上游 200 时解析媒体 JSON。具名脚本核对返回 ID 与查询目标、媒体类型及 title、status 的基础结构，缺失或不匹配时保留诊断并非零退出。无论是否有 mediaUrl，都要读取视频、配对的 status 和 issues；请求成功不代表媒体已 AVAILABLE。
- 400 核对路径及可选关联 ID，403 核对当前卖家授权和应用 Media API 准入，404 / 410 核对 ID 与原素材状态。429 按 Retry-After 和任务上限安排后续只读查询，500 / 503 保留诊断后按用户范围恢复。
- 处理或审核可能耗时较长；单次脚本不自动轮询。输出媒体 ID、当前状态和续查入口，等待范围按公共状态规则处理。
- 上游默认约 10 req/s、burst 10，以实际配额为准；450 / 453 / 454 / 459 适用 [店铺保护](spapi-protection.md)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"SELLER_ID","region":"NA","method":"GET","path":"aplus/2020-11-01/media/VIDEO_MEDIA_ID","queryString":"associatedMediaId=THUMBNAIL_MEDIA_ID"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-aplus-content",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
