# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：创建 Feed 文档（createFeedDocument）

### 脚本输入与构参

#### 上游方法与路径

`POST feeds/2021-06-30/documents`。路径占位值须分别百分号编码；不要编码整个路径。

#### 脚本 JSON 参数与选项

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地认证技能安装探测，不绕过授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 call_api.run 时始终添加；不读取或写入响应缓存。 |
| contentType | string | 是 | 脚本直接接收并写入 body.contentType；须与上传 MIME 一致，如 `text/tab-separated-values; charset=UTF-8`。 |

本地依赖检查返回 0 表示找到认证技能，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失；依赖 `linkfox-amazon-store-auth`，兼容目录名 `linkfox-amazon-spapi-auth`。支持环境变量、OpenClaw、Hermes 分类及插件目录探测。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY` > `STORE_API_BASE_URL` > `SPAPI_BASE_URL` > `https://tool-gateway.linkfox.com`；API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。会话头支持 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。业务层调用公共调用器时禁用响应缓存；空的 `.cache` 目录不表示复用响应。数据只写当前工作目录，不可写时在发起请求前报错，不回退到 `/tmp`。

应用需具备 Feeds 相关角色；网关白名单需包含 `feeds/2021-06-30/`，并允许本操作的上游方法。

#### Amazon Body 字段（网关 body JSON 字符串内部）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| body.contentType | string | 是 | 创建上传文档时的文件 MIME；对应脚本 contentType。 |

脚本先组成上述业务对象，再序列化为网关 body 字符串；外层网关 contentType 为 application/json。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，失败时保留错误。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| requestBody | object | 提交前的业务对象，区别于网关 body 字符串。 |
| feedDocument | object / null | 外层与网关正常且上游为 200 / 201 / 202 / 204 时解析 body；空响应或解析失败为 null，否则不添加。 |
| feedDocumentRaw | string | 仅 JSON 解析失败时保留原始 body。 |


#### 业务结果使用

解析后的 feedDocument 含 feedDocumentId、url；只使用本次响应的上传 URL。

## 接口：获取 Feed 文档（getFeedDocument）

### 脚本输入与构参

#### 上游方法与路径

`GET feeds/2021-06-30/documents/{feedDocumentId}`。路径占位值须分别百分号编码；不要编码整个路径。

#### 脚本 JSON 参数与选项

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地认证技能安装探测，不绕过授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 call_api.run 时始终添加；不读取或写入响应缓存。 |
| feedDocumentId | string | 是 | 路径参数；脚本按 URL path 分段编码。结果文件使用 resultFeedDocumentId。 |
| enableContentEncodingUrlHeader | boolean | 否 | 查询参数；传入时输出 true / false，GZIP 时便于客户端自动解压；不传则省略，无本地默认值。 |

本地依赖检查返回 0 表示找到认证技能，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失；依赖 `linkfox-amazon-store-auth`，兼容目录名 `linkfox-amazon-spapi-auth`。支持环境变量、OpenClaw、Hermes 分类及插件目录探测。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY` > `STORE_API_BASE_URL` > `SPAPI_BASE_URL` > `https://tool-gateway.linkfox.com`；API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。会话头支持 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。业务层调用公共调用器时禁用响应缓存；空的 `.cache` 目录不表示复用响应。数据只写当前工作目录，不可写时在发起请求前报错，不回退到 `/tmp`。

应用需具备 Feeds 相关角色；网关白名单需包含 `feeds/2021-06-30/`，并允许本操作的上游方法。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，失败时保留错误。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| queryString | string / null | 实际发送的查询串，无问号；未传时为 null。 |
| feedDocument | object / null | 外层与网关正常且上游为 200 / 201 / 202 / 204 时解析 body；空响应或解析失败为 null，否则不添加。 |
| feedDocumentRaw | string | 仅 JSON 解析失败时保留原始 body。 |


#### 业务结果使用

按本次响应 URL 下载结果文档；GZIP 时按实际内容处理。

## 接口：提交 Feed（createFeed）

### 脚本输入与构参

#### 上游方法与路径

`POST feeds/2021-06-30/feeds`。

#### 脚本 JSON 参数与选项

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地认证技能安装探测，不绕过授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 call_api.run 时始终添加；不读取或写入响应缓存。 |
| feedType | string | 是 | Feed 类型；须与已上传文件的格式及用途匹配，以 [Feed Type Values](https://developer-docs.amazon.com/sp-api/docs/feed-type-values) 为准。 |
| marketplaceIds | string[] / string | 是 | 1～25 个站点 ID；支持逗号分隔字符串。未提供时兼容 marketplaceId 单个站点输入。 |
| inputFeedDocumentId | string | 是 | 已成功上传内容的 feedDocumentId。 |
| feedOptions | object | 否 | 因 feedType 而异；提供非 null 值时脚本要求为对象，不传则省略。 |

本地依赖检查返回 0 表示找到认证技能，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失；依赖 `linkfox-amazon-store-auth`，兼容目录名 `linkfox-amazon-spapi-auth`。支持环境变量、OpenClaw、Hermes 分类及插件目录探测。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY` > `STORE_API_BASE_URL` > `SPAPI_BASE_URL` > `https://tool-gateway.linkfox.com`；API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。会话头支持 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。业务层调用公共调用器时禁用响应缓存；空的 `.cache` 目录不表示复用响应。数据只写当前工作目录，不可写时在发起请求前报错，不回退到 `/tmp`。

应用需具备 Feeds 相关角色；网关白名单需包含 `feeds/2021-06-30/`，并允许本操作的上游方法。

#### Amazon Body 字段（网关 body JSON 字符串内部）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| body.feedType | string | 是 | 对应脚本 feedType，去除首尾空白。 |
| body.marketplaceIds | string[] | 是 | 对应脚本归一化后的站点列表。 |
| body.inputFeedDocumentId | string | 是 | 对应脚本 inputFeedDocumentId，去除首尾空白。 |
| body.feedOptions | object | 否 | 提供非 null 的 feedOptions 时加入。 |

脚本先组成上述业务对象，再序列化为网关 body 字符串；外层网关 contentType 为 application/json。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，失败时保留错误。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| requestBody | object | 提交前的业务对象，区别于网关 body 字符串。 |
| feed | object / null | 外层与网关正常且上游为 200 / 201 / 202 / 204 时解析 body；空响应或解析失败为 null，否则不添加。 |
| feedRaw | string | 仅 JSON 解析失败时保留原始 body。 |

#### 业务结果使用

保存本次响应的 feedId，用于后续查询或取消；202 只表示提交被接受，处理进度与结果须另行查询。

## 接口：查询 Feed（getFeed）

### 脚本输入与构参

#### 上游方法与路径

`GET feeds/2021-06-30/feeds/{feedId}`。路径占位值须分别百分号编码；不要编码整个路径。

#### 脚本 JSON 参数与选项

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地认证技能安装探测，不绕过授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 call_api.run 时始终添加；不读取或写入响应缓存。 |
| feedId | string | 是 | 目标任务 ID；脚本按 URL path 分段编码。本操作不发送文档下载查询参数。 |

本地依赖检查返回 0 表示找到认证技能，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失；依赖 `linkfox-amazon-store-auth`，兼容目录名 `linkfox-amazon-spapi-auth`。支持环境变量、OpenClaw、Hermes 分类及插件目录探测。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY` > `STORE_API_BASE_URL` > `SPAPI_BASE_URL` > `https://tool-gateway.linkfox.com`；API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。会话头支持 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。业务层调用公共调用器时禁用响应缓存；空的 `.cache` 目录不表示复用响应。数据只写当前工作目录，不可写时在发起请求前报错，不回退到 `/tmp`。

应用需具备 Feeds 相关角色；网关白名单需包含 `feeds/2021-06-30/`，并允许本操作的上游方法。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，失败时保留错误。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| feed | object / null | 外层与网关正常且上游为 200 / 201 / 202 / 204 时解析 body；空响应或解析失败为 null，否则不添加。 |
| feedRaw | string | 仅 JSON 解析失败时保留原始 body。 |


#### 业务结果使用

读取本次响应的 processingStatus（如 IN_QUEUE、IN_PROGRESS、DONE、FATAL）；处理完成时使用 resultFeedDocumentId 获取结果文档。

## 接口：列出 Feed（getFeeds）

### 脚本输入与构参

#### 上游方法与路径

`GET feeds/2021-06-30/feeds`。路径占位值须分别百分号编码；不要编码整个路径。

#### 脚本 JSON 参数与选项

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地认证技能安装探测，不绕过授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 call_api.run 时始终添加；不读取或写入响应缓存。 |
| feedTypes | string[] / string | 条件 | 与 nextToken 二选一；首查必需，最多 10 个；字符串支持逗号分隔。 |
| nextToken | string | 条件 | 仅使用上一页返回值；分页时单独发送此查询参数。脚本收到非空值时忽略其他过滤字段；不叫 paginationToken。 |
| marketplaceIds | string[] / string | 否 | 最多 10 个；可用逗号分隔字符串。 |
| processingStatuses | string[] / string | 否 | `CANCELLED` / `DONE` / `FATAL` / `IN_PROGRESS` / `IN_QUEUE`；可用逗号分隔字符串。 |
| createdSince | string | 否 | ISO 8601 日期时间；不传时由上游决定范围。 |
| createdUntil | string | 否 | ISO 8601 日期时间；不传时由上游决定范围。 |
| pageSize | integer | 否 | 1～100，Amazon 默认 10；脚本未提供时不发送。 |

本地依赖检查返回 0 表示找到认证技能，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失；依赖 `linkfox-amazon-store-auth`，兼容目录名 `linkfox-amazon-spapi-auth`。支持环境变量、OpenClaw、Hermes 分类及插件目录探测。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY` > `STORE_API_BASE_URL` > `SPAPI_BASE_URL` > `https://tool-gateway.linkfox.com`；API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。会话头支持 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。业务层调用公共调用器时禁用响应缓存；空的 `.cache` 目录不表示复用响应。数据只写当前工作目录，不可写时在发起请求前报错，不回退到 `/tmp`。

应用需具备 Feeds 相关角色；网关白名单需包含 `feeds/2021-06-30/`，并允许本操作的上游方法。

列表用重复键名构造查询串，各值单独百分号编码；nextToken 模式只保留 nextToken。字段数量、范围和枚举按上述约束提交，脚本按上述方式映射查询字段，不替代 Amazon 参数校验。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，失败时保留错误。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| queryString | string / null | 实际发送的查询串，无问号；未传时为 null。 |
| feeds | object / null | 外层与网关正常且上游为 200 / 201 / 202 / 204 时解析 body；空响应或解析失败为 null，否则不添加。 |
| feedsRaw | string | 仅 JSON 解析失败时保留原始 body。 |

## 接口：取消 Feed（cancelFeed）

### 脚本输入与构参

#### 上游方法与路径

`DELETE feeds/2021-06-30/feeds/{feedId}`。路径占位值须分别百分号编码；不要编码整个路径。

#### 脚本 JSON 参数与选项

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| skipDepCheck | boolean | 否 | 默认 false；跳过本地认证技能安装探测，不绕过授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用 call_api.run 时始终添加；不读取或写入响应缓存。 |
| feedId | string | 是 | 目标任务 ID，脚本按 URL path 分段编码。 |

本地依赖检查返回 0 表示找到认证技能，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失；依赖 `linkfox-amazon-store-auth`，兼容目录名 `linkfox-amazon-spapi-auth`。支持环境变量、OpenClaw、Hermes 分类及插件目录探测。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY` > `STORE_API_BASE_URL` > `SPAPI_BASE_URL` > `https://tool-gateway.linkfox.com`；API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。会话头支持 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。业务层调用公共调用器时禁用响应缓存；空的 `.cache` 目录不表示复用响应。数据只写当前工作目录，不可写时在发起请求前报错，不回退到 `/tmp`。

应用需具备 Feeds 相关角色；网关白名单需包含 `feeds/2021-06-30/`，并允许本操作的上游方法。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，失败时保留错误。 |
| resolvedPath | string | 实际编码后的资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
