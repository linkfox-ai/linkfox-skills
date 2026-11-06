# Amazon 店铺文件上传 接口说明

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



## 接口：创建上传目的地（createUploadDestinationForResource）

Uploads v2020-11-01。官方参考：[createUploadDestinationForResource](https://developer-docs.amazon.com/sp-api/reference/createuploaddestinationforresource)、[Create an upload destination](https://developer-docs.amazon.com/sp-api/docs/create-an-upload-destination)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/spApi/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | NA / EU / FE；也支持小写，须与授权记录匹配。 |
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符；服务端要求非空，并按当前成员、sellerId 与 region 解析令牌。 |
| path | string | 是 | `uploads/2020-11-01/uploadDestinations/{resource}`；相对资源路径，最长 2048 字符。`resource` 为 greedy path，须保留内部 `/`，其余字符做百分号编码，不得把路径分隔符预编码为 `%2F`；具体构造见 [script-usage.md](script-usage.md)。 |
| method | string | 是 | 本操作上游方法为 `POST`；LinkFox 外层始终 POST。 |
| queryString | string | 否 | 不含 ? 的查询字符串，最长 4096 字符；键值按 RFC 3986 百分号编码，+ 按字面加号处理。 |
| body | string | 否 | 上游请求正文字符串，最长 1,048,576 字符；网关不定义内部业务字段。 |
| contentType | string | 否 | 上游正文类型，最长 128 字符；有正文时默认 application/json。 |

操作所需的脚本输入、路径、查询串与正文构造见 [script-usage.md](script-usage.md)。

#### 上游 Path 与 Query 合同

| 参数 | 位置 / 类型 | 必填 | 说明 |
|---|---|---|---|
| resource | path / string | 是 | 未编码的下游资源路径，按 greedy path 编码并保留内部 `/`。A+ 图片、视频和缩略图均使用 `aplus/2020-11-01/contentDocuments`；Messaging 使用对应业务操作的资源路径。 |
| marketplaceIds | query / array<string> | 是 | 目标站点集合，最多一个站点。 |
| contentMD5 | query / string | 是 | 原始文件字节的 Base64 MD5 摘要，须与后续实际上传的文件一致。 |
| contentType | query / string | 条件必填 | 文件 MIME 类型。A+ 内容必须提供，例如 `image/jpeg`、`image/png` 或对应视频类型。 |

本操作不要求上游 JSON 请求体。代理外层 `contentType` 表示请求正文类型，Query 的 `contentType` 表示文件 MIME 类型，按所处层次分别传值。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态分别判断。 |
| contentType | string | 上游 Content-Type；响应头缺失时可为空。 |
| body | string | 上游原始响应正文；可为空字符串。网关不定义其内部业务字段。 |
| xAmznRequestId | string | 上游 x-amzn-requestid 响应头原值，可为空。 |
| retryAfter | string | 上游 Retry-After 响应头原值，可为空；不限定为数字。 |
| xAmznRateLimitLimit | string | 上游 x-amzn-RateLimit-Limit 响应头原值，可为空。 |

上游成功 `body` JSON 支持 `{"errors":[],"payload":{...}}` 包装和历史扁平目的地两种结构。目的地字段见下表，包装结构下位于 `payload` 内。预签名 URL 和请求头只供实际上传使用，CLI 保留原包装，同时提供展开后的 `resolvedUploadDestination`，输出可能含临时签名凭据，不要对外分享。取数路径见 [脚本输出](script-usage.md#脚本输出与业务结果)。

| 字段 | 类型 | 说明 |
|---|---|---|
| uploadDestinationId | string | 上传资源标识，成功上传后交下游业务引用。 |
| url | string | Amazon 返回的预签名上传地址，包含目的地要求的签名字段。 |
| headers | object<string,string> / null | Amazon 要求的上传请求头；null 表示没有附加请求头。 |

上游失败 `body` 通常包含以下错误结构，按实际返回保留诊断。

| 字段 | 类型 | 说明 |
|---|---|---|
| errors | array<object> | 上游错误列表。 |
| errors[].code | string | Amazon 错误代码。 |
| errors[].message | string | 错误说明。 |
| errors[].details | string | 可选错误详情。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 创建目的地通常返回上游 HTTP 201；脚本也接受上游 200。成功创建目的地不代表文件上传完成。
- 上游 403 表示 Uploads 或下游角色未授权；上游 429 为限流，官方默认速率为 10 次/秒、burst 10，以实际响应头及分配配额为准。
- 网关 `errcode=1005` 时结合 `errmsg` 区分：路径白名单拒绝需放行 `uploads/2020-11-01/` 前缀；授权信息失效需重新授权。
- 收到 450 / 453 / 454 / 459 按 [店铺保护与重试](spapi-protection.md) 停止调用和处理；453 涉及该店铺全部 SP-API。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/spApi/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sellerId":"A1...","region":"NA","method":"POST","path":"uploads/2020-11-01/uploadDestinations/aplus/2020-11-01/contentDocuments","contentType":"application/json","queryString":"marketplaceIds=ATVPDKIKX0DER&contentMD5=kAFQmDzST7DWlj99KOF%2Fcg%3D%3D&contentType=image%2Fjpeg"}'
```


## 操作：上传文件到预签名地址（非 LinkFox 接口）

### 调用规范

- **请求地址**：`uploadDestination.url` 或 `uploadUrl`，按目的地要求执行 PUT 或 multipart POST，不经 developerProxy。
- **请求头**：PUT 完整附带返回的 headers；POST 使用带 boundary 的 multipart/form-data，文件 MIME 类型放在文件 part，其余返回头按目的地要求携带。不添加 LinkFox API key；超时 300 秒，无自动重试。

### 请求参数

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| uploadDestination | object | 是，或 uploadUrl | 创建接口返回的完整对象，兼容 `payload` 包装或裸目的地，也可传 `resolvedUploadDestination`。 |
| uploadDestination.payload.url / uploadDestination.url | string | 条件必填 | 优先使用展开后的地址，正常裸对象缺失时回退 uploadUrl；明确失败的包装不允许回退绕过。 |
| uploadDestination.payload.headers / uploadDestination.headers | object[string,string] / null | 是，或 headers | 优先使用展开后的值，空值回退外层 headers；null 视为没有附加头。 |
| uploadUrl | string | 条件必填 | 无目的地 URL 时使用。 |
| headers | object[string,string] | 条件必填 | 外层请求头；未提供时脚本使用空对象，调用者仍应完整带上目的地请求头。键和值转为字符串。 |
| method | string | 否 | 默认 PUT；A+ 表单目的地传 POST，大小写兼容。 |
| formFields | object[string,string] | 否 | POST 补充表单字段；URL 查询参数自动解码并移入表单，file 由脚本生成。 |
| fileName | string | 否 | POST 文件名，默认取 filePath 文件名，无路径时为 upload.bin。 |
| contentType | string | 否 | POST 文件 MIME 类型，优先此值，再用返回头中的 Content-Type，最后按扩展名推断或用 application/octet-stream。 |
| filePath | string | 三选一 | 原始文件字节，路径支持 `~`，文件须存在。 |
| contentBase64 | string | 三选一 | Base64 二进制内容。 |
| content | string | 三选一 | UTF-8 文本。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存结果。 |
| --no-cache | CLI flag | 否 | 兼容公共入口，上传操作始终无缓存。 |
| --help | CLI flag | 否 | 查看帮助，不发请求。 |

POST 对去掉查询串的 URL 发送 multipart 表单：查询参数解码为表单字段并保留原值，file 为最后一个 part；PUT 使用完整 URL。A+ 表单流程见 [Amazon 上传流程](https://developer-docs.amazon/sp-api/docs/create-edit-publish-aplus-content)。

素材优先级 filePath > contentBase64 > content，拒绝空字节。PUT 使用的字节必须与申请 contentMD5 时完全一致；申请时显式填写摘要也不能改变该要求。上传 URL 应使用 Amazon 返回的预签名地址，脚本拒绝 LinkFox 域名及配置的网关主机（忽略域名大小写与末尾的点），以免直接向网关上传素材；无须认证技能或 LinkFox 密钥。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| uploadUrl | string | 实际上传地址，POST 时已去掉查询串。 |
| method | string | 实际上传方式 PUT 或 POST。 |
| bytesUploaded | integer | 本次请求准备发送的字节数；失败时不能据此认为已上传成功。 |
| requestHeaders | object | 实际附带的请求头。 |
| httpStatus | integer | 上传端 HTTP 状态；连接失败时缺失。 |
| success | boolean | HTTP 2xx 时 true，其余或连接失败时 false。 |
| error | string | 失败原因。 |
| details | string | HTTP 错误正文，最多保留前 2000 字符。 |

### 响应码规则

#### 业务规则

本操作无 LinkFox errcode，以目标服务器 HTTP 2xx 判断成功。失败时仍保存结果并以退出码 1 结束；上传成功后才交由下游业务引用资源。结果不确定时保留 uploadDestinationId 及既有 reportId / feedId 等任务 ID，先核验状态，不直接重放。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-uploads",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
