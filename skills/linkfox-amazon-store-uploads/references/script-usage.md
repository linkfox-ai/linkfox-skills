# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：创建上传目的地（createUploadDestinationForResource）

### 脚本输入与构参

#### Path 与 Query 参数

| 参数 | 位置 / 类型 | 必填 | 说明 |
|---|---|---|---|
| resource | path / string | 是 | 未编码的下游资源路径，可带前导 `/`；脚本移除前导 `/`，使用 greedy path 编码并保留内部 `/`，不得预编码成 `%2F`。A+ 示例：`aplus/2020-11-01/contentDocuments`；Messaging 示例：`messaging/v1/orders/{amazonOrderId}/messages/...`，实际 resource 须与下游文档一致。 |
| marketplaceIds | query / string | 是 | 单站点 ID，脚本由 marketplaceId 或 marketplaceIds 解析。 |
| contentMD5 | query / string | 是 | 文件字节的 Base64 MD5 摘要，非十六进制字符串。计算方式：`base64.b64encode(hashlib.md5(data).digest()).decode("ascii")`。 |
| contentType | query / string | A+ 必填 | 文件 MIME 类型，例如 `image/jpeg`、`image/png` 或对应视频类型。 |

Messaging 资源以 [Messaging API](https://developer-docs.amazon.com/sp-api/docs/messaging-api-v1-reference) 中对应操作的说明为准。

#### 脚本 JSON 参数与 CLI

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权卖家标识。 |
| region | string | 是 | 店铺授权区域。 |
| resource | string | 是 | 未编码的下游资源路径。 |
| marketplaceId | string | 是，或 marketplaceIds | 优先使用此值。 |
| marketplaceIds | array[string] / string | 兼容 | 未传 marketplaceId 时使用；数组仅取第一个，多值时 stderr 警告；非空字符串原样作为单值。 |
| contentMD5 | string | 是，或以下一种素材 | 显式提供时优先使用并去首尾空白；由调用者保证与上传字节一致。 |
| filePath | string | 条件必填 | 本地文件路径，支持 `~`；文件必须存在，读取原始字节。 |
| contentBase64 | string | 条件必填 | Base64 编码的二进制内容。 |
| content | string | 条件必填 | UTF-8 文本内容。 |
| contentType | string | A+ 必填 | 文件 MIME 类型，去首尾空白后写入 query。 |
| uploadFile | boolean | 否 | 默认 false；true 时同一进程申请目的地并上传，须提供非空 filePath、contentBase64 或 content。 |
| uploadMethod | string | 否 | uploadFile:true 时使用，可选 PUT 或 POST；A+ 默认 POST，其他资源默认 PUT。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部流程已确认依赖时跳过安装探测，不绕过授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 支持此选项；封装调用 run 时始终传入，不读取或保存响应缓存。公共调用器可能创建空缓存目录。 |
| --help | CLI flag | 否 | 查看帮助，不发请求。 |

自动计算摘要时提供 filePath / contentBase64 / content 之一。多来源优先级：filePath > contentBase64 > content；实际上传也使用同一优先级。自动摘要和上传均拒绝空字节；显式 contentMD5 可独立申请目的地。uploadFile:true 时只读取一次素材，使用相同字节计算 MD5 和上传；显式 contentMD5 不符时在请求前报错。uploadFile:false 保留只申请目的地的行为。

本地依赖检查返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`。支持认证技能别名 `linkfox-amazon-spapi-auth` 及多平台目录探测，不在正常上传流程中获取令牌。

网关地址优先级为 `LINKFOX_TOOL_GATEWAY` > `STORE_API_BASE_URL` > `SPAPI_BASE_URL` > 默认正式地址；密钥支持 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 两个环境变量，前者优先。会话跟踪头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 透传。业务输出只写当前工作目录，目录不可写时在请求前报错，不回退到用户目录或临时目录。

### 脚本输出与业务结果

#### 脚本输出与上传目的地

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，包含错误详情。 |
| transportHttpStatus | integer / null | 外层 LinkFox HTTP 状态，连接失败时为 null。 |
| resolvedPath | string | 实际发送的编码后资源路径。 |
| queryString | string | 实际发送的查询串。 |
| resource | string | 输入的 resource 去首尾空白后的值。 |
| uploadDestination | object / null | 上游 200 或 201 时解码后的完整 body，保留原包装。可为包含 `errors`、`payload` 的对象或历史扁平目的地；空 body 或解析失败为 null，其他失败情况下不返回此字段。 |
| uploadDestination.payload | object | 带包装响应中的目的地对象，包含 `uploadDestinationId`、`url`、`headers`。 |
| uploadDestination.payload.uploadDestinationId | string | 带包装响应中的原始资源标识；成功上传后交 A+ / Messaging 或 Media 引用。 |
| uploadDestination.payload.url | string | 带包装响应中的预签名地址。 |
| uploadDestination.payload.headers | object<string,string> / null | 带包装响应中的上传头；null 表示没有附加请求头。 |
| uploadDestination.uploadDestinationId | string | 历史扁平响应中的原始资源标识。 |
| uploadDestination.url | string | 历史扁平响应中的预签名地址。 |
| uploadDestination.headers | object<string,string> / null | 历史扁平响应中的上传头；null 按没有附加请求头处理。 |
| resolvedUploadDestination | object / null | 兼容展开后的目的地直对象，推荐从此字段读取资源 ID。原始 `uploadDestination` 的结构保持不变。 |
| resolvedUploadDestination.uploadDestinationId | string | 原始资源标识，保持原值。 |
| resolvedUploadDestination.url | string | 展开后的预签名地址，可用于后续独立上传。 |
| resolvedUploadDestination.headers | object<string,string> / null | 展开后的上传头；null 按没有附加请求头处理。 |
| uploadDestinationRaw | string | 仅 body 无法解析时保留原始内容。 |


`uploadFile: true` 先保存创建目的地结果，再上传并保存第二份结果，两个阶段保留各自原 envelope。创建失败或目的地无效时不会上传；创建成功不代表文件已上传。第二份上传结果字段见 [上传入口](api.md#操作上传文件到预签名地址非-linkfox-接口)，仅 success:true 后才交下游使用。推荐从 resolvedUploadDestination.uploadDestinationId 读取资源 ID；也可按实际包装读取 uploadDestination.payload.uploadDestinationId 或 uploadDestination.uploadDestinationId。原始输出可能含临时签名 URL 和请求头，不要对外分享。已有目的地仍可从创建结果文件中取完整对象交独立上传入口，不要求只能同进程使用。

#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 错误正文无法解析为 JSON，或连接失败时的错误说明。 |
| details | string | HTTP 错误返回非 JSON 正文时保留的原文；连接失败时不返回此字段。 |
