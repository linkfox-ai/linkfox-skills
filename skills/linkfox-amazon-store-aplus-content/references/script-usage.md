# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：搜索 A+ 文档（searchContentDocuments）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| pageToken | string | 否 | 分页令牌，脚本去除两端空白后编码；不自动翻页。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `GET` |
| path | string | 是 | `aplus/2020-11-01/contentDocuments`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |
| pageToken | string | 否 | 上一页返回的分页令牌。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

本操作不传 `developerProxy.body`。

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `GET` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| searchContentDocumentsResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| searchContentDocumentsResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：创建 A+ 文档（createContentDocument）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| contentDocument | object | 是 | A+ 文档对象；按 Amazon 官方模型准备。脚本仅检查为 JSON 对象，内部字段透传，不内置模板校验。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `POST` |
| path | string | 是 | `aplus/2020-11-01/contentDocuments`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| contentDocument | object | 是 | 待创建、更新或校验的完整 A+ 文档对象；嵌套模型以 Amazon 官方定义为准；脚本透传内部字段，不内置模板校验。 |

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `POST` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| createContentDocumentResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| createContentDocumentResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：获取 A+ 文档（getContentDocument）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| contentReferenceKey | string | 是 | 非空文档引用键；路径段百分号编码（含 /、空格等），非永久链接，未来可能变化。 |
| includedDataSet | array<string> / string | 是 | 至少 1 项；可选 `CONTENTS`、`METADATA`，可并存。脚本接受单字符串、逗号串或数组，去空白后以一个逗号分隔的 Query 值发送。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `GET` |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |
| includedDataSet | string（CSV） | 是（≥1） | 至少 1 项；可选 `CONTENTS`、`METADATA`，可并存。使用单个 Query 键，例如 `includedDataSet=CONTENTS,METADATA`。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

本操作不传 `developerProxy.body`。

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `GET` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| getContentDocumentResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| getContentDocumentResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：更新 A+ 文档（updateContentDocument）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| contentReferenceKey | string | 是 | 非空文档引用键；路径段百分号编码（含 /、空格等），非永久链接，未来可能变化。 |
| contentDocument | object | 是 | A+ 文档对象；按 Amazon 官方模型准备。脚本仅检查为 JSON 对象，内部字段透传，不内置模板校验。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `POST` |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| contentDocument | object | 是 | 待创建、更新或校验的完整 A+ 文档对象；嵌套模型以 Amazon 官方定义为准；脚本透传内部字段，不内置模板校验。 |

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `POST` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| updateContentDocumentResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| updateContentDocumentResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：列出关联 ASIN（listContentDocumentAsinRelations）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| contentReferenceKey | string | 是 | 非空文档引用键；路径段百分号编码（含 /、空格等），非永久链接，未来可能变化。 |
| includedDataSet | array<string> / string | 否 | 可选 `METADATA`；不传通常只返回关联 ASIN。脚本接受单字符串、逗号串或数组，去空白后以一个逗号分隔的 Query 值发送。 |
| pageToken | string | 否 | 分页令牌，脚本去除两端空白后编码；不自动翻页。 |
| asinSet | array<string> / string | 否 | 可选 ASIN 集合；支持单字符串、逗号串或数组，以一个逗号分隔的 Query 值发送。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `GET` |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |
| includedDataSet | string（CSV） | 否 | 可选 `METADATA`；不传通常只返回关联 ASIN。使用单个 Query 键。 |
| pageToken | string | 否 | 上一页返回的分页令牌。 |
| asinSet | string（CSV） | 否 | 筛选关联 ASIN。使用单个 Query 键，例如 `asinSet=B000000001,B000000002`。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

本操作不传 `developerProxy.body`。

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `GET` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| listContentDocumentAsinRelationsResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| listContentDocumentAsinRelationsResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：全量替换关联 ASIN（postContentDocumentAsinRelations）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| contentReferenceKey | string | 是 | 非空文档引用键；路径段百分号编码（含 /、空格等），非永久链接，未来可能变化。 |
| asinSet | array / string | 是 | 全量替换文档关联的全部 ASIN；空数组保留并透传。字符串或逗号串转数组；纯对象数组沿用旧入口原样透传，其他数组沿用原转换行为。上游合同要求 ASIN 字符串数组，CLI 兼容透传不表示对象数组是合法业务输入。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `POST` |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| asinSet | array<string> | 是 | 最终完整关联集合，使用 ASIN 字符串数组。移除 ASIN 会 suspend 其上的该内容，以 Amazon 行为为准。 |

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `POST` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| postContentDocumentAsinRelationsResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| postContentDocumentAsinRelationsResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：校验文档与 ASIN（validateContentDocumentAsinRelations）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| contentDocument | object | 是 | A+ 文档对象；按 Amazon 官方模型准备。脚本仅检查为 JSON 对象，内部字段透传，不内置模板校验。 |
| asinSet | array<string> / string | 否 | 可选 ASIN 集合；支持单字符串、逗号串或数组，以一个逗号分隔的 Query 值发送。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `POST` |
| path | string | 是 | `aplus/2020-11-01/contentAsinValidations`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |
| asinSet | string（CSV） | 否 | 待校验 ASIN 集合，使用单个 Query 键，例如 `asinSet=B000000001,B000000002`；仅放 Query，不写入 contentDocument 或请求体同级。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| contentDocument | object | 是 | 待创建、更新或校验的完整 A+ 文档对象；嵌套模型以 Amazon 官方定义为准；脚本透传内部字段，不内置模板校验。 |

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `POST` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| validateContentDocumentAsinRelationsResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| validateContentDocumentAsinRelationsResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：查询发布记录（searchContentPublishRecords）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| pageToken | string | 否 | 分页令牌，脚本去除两端空白后编码；不自动翻页。 |
| asin | string | 是 | 去除两端空白后长度至少 10；脚本在本地检查并百分号编码。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `GET` |
| path | string | 是 | `aplus/2020-11-01/contentPublishRecords`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |
| pageToken | string | 否 | 上一页返回的分页令牌。 |
| asin | string | 是 | ASIN，length ≥ 10。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

本操作不传 `developerProxy.body`。

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `GET` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| searchContentPublishRecordsResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| searchContentPublishRecordsResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：提交审核与发布（postContentDocumentApprovalSubmission）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| contentReferenceKey | string | 是 | 非空文档引用键；路径段百分号编码（含 /、空格等），非永久链接，未来可能变化。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `POST` |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/approvalSubmissions`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

本操作不传 `developerProxy.body`。

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `POST` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| postContentDocumentApprovalSubmissionResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| postContentDocumentApprovalSubmissionResponseRaw | string | 仅解析失败时保留原始 body。 |

## 接口：暂停前台展示（postContentDocumentSuspendSubmission）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE`。 |
| marketplaceId | string | 二选一 | 目标站点；优先于 marketplaceIds，去除两端空白；Query 始终使用单数 marketplaceId。 |
| marketplaceIds | array<string> / string | 二选一 | marketplaceId 缺失时兼容；数组只取第一个，多项打印 stderr 警告；非空字符串直接作为单站点。 |
| contentReferenceKey | string | 是 | 非空文档引用键；路径段百分号编码（含 /、空格等），非永久链接，未来可能变化。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| skipDepCheck | boolean | 否 | 默认 false；true 跳过本地安装检查，不绕过实际店铺授权，不建议常规使用。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共 run 传入此选项，不读写响应缓存。 |

运行 `python scripts/<对应脚本>.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查返回 0 表示找到 `linkfox-amazon-store-auth`；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。不得在本技能内另行实现授权或令牌逻辑；本地检测支持 `linkfox-amazon-store-auth`、`linkfox-amazon-spapi-auth` 目录名，以及 OpenClaw、Hermes 和环境变量注入路径。

基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最后为默认正式网关。密钥兼容两个环境变量。公共调用器使用 POST、150 秒超时及会话上下文请求头，业务封装不另行实现 HTTP、不自动重试。

业务输出锁定 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/`，禁止回退到家目录或 `/tmp`；工作目录不可写时在请求前报错。保留完整响应、会话索引与元数据；超过 8000 字节默认仅打印摘要，`--inline` 打印全量。固定公共执行器可能建立空缓存目录，但本技能不读写响应缓存文件。

#### 上游方法与路径

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| method | string | 是 | `POST` |
| path | string | 是 | `aplus/2020-11-01/contentDocuments/{contentReferenceKey}/suspendSubmissions`；占位段须百分号编码，脚本已处理。 |

#### Query 参数（写入 queryString，无 ?）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点 ID；脚本按百分号编码。 |

#### 上游 Body JSON（序列化为网关 body 字符串）

本操作不传 `developerProxy.body`。

#### 使用限制

- 应用须具备 A+ Content 角色/权限，否则上游 403；网关须支持上游 `POST` 并放行 `aplus/2020-11-01/` 前缀。
- 官方文档默认多为 10 req/s、burst 10，以 `x-amzn-RateLimit-Limit` 和账号实际配额为准，不能作为主动加速调用的目标。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应；错误时保留原始内容。 |
| resolvedPath | string | 实际使用的编码后相对资源路径。 |
| queryString | string | 实际发送的不带问号的查询串。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| postContentDocumentSuspendSubmissionResponse | object / null | 外层及网关正常、上游 httpStatus 为 200 时解析 body；JSON 解析失败为 null，业务对象按实际返回处理。 |
| postContentDocumentSuspendSubmissionResponseRaw | string | 仅解析失败时保留原始 body。 |
## 接口：注册图片或视频媒体（createMedia）

### 脚本输入与构参

入口为 `scripts/create_media.py`，格式为 `python scripts/create_media.py '<JSON 参数>' [--inline] [--no-cache]`。本操作会注册媒体或创建视频缩略图配对。

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 当前成员已授权的店铺标识，去除首尾空白后传网关。 |
| region | string | 是 | `NA` / `EU` / `FE`，兼容小写，标准化为大写。 |
| mediaRequest | object | 是 | 完整上游 `CreateMediaRequest`，字段及条件必填规则见 api.md，脚本不增加外层业务包装。 |
| skipDepCheck | boolean | 否 | 默认 false，跳过本地授权 Skill 安装检测；不能绕过真实授权。 |
| --inline | CLI flag | 否 | 强制完整展示结果，同时保存文件。 |
| --no-cache | CLI flag | 否 | 操作始终禁用响应缓存，保留此选项兼容统一入口。 |
| --help | CLI flag | 否 | 展示帮助后退出，不发请求。 |

脚本校验店铺与区域、请求对象、素材 ID 二选一，以及视频描述、唯一语言和恰好一条图片配对。配对标题至少三个词且不能全大写，图片引用也须满足 ID 二选一。具体文件和账号准入仍由 Amazon 检查，新增的上游字段在保持既有必填结构的前提下透传。

#### 上游方法、路径与 Body

| 字段 | 值或构造方式 |
|---|---|
| method | `POST` |
| path | `aplus/2020-11-01/media` |
| queryString | 不传；本接口没有 marketplaceId。 |
| contentType | `application/json` |
| body | `mediaRequest` 对象序列化成 JSON 字符串，直接作为上游请求对象，不包在 contentDocument 下。 |

#### 调用示例

```bash
python scripts/create_media.py '{"sellerId":"SELLER_ID","region":"NA","mediaRequest":{"mediaType":"VIDEO","uploadDestinationId":"VIDEO_UPLOAD_DESTINATION_ID","descriptions":[{"locale":"en-US","value":"A demonstration of cleaning and storing the product."}],"relatedMedia":[{"associationType":"VIDEO_PAIRING","title":"Product care demonstration","media":{"mediaType":"IMAGE","mediaId":"THUMBNAIL_MEDIA_ID"}}]}}' --no-cache
```

占位 ID 需替换为同一店铺实际上传和注册所得 ID。完整素材流程与模块引用示例见 [modules.md](modules.md)。

### 脚本输出与业务结果

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应及上游状态、正文。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时可为空。 |
| resolvedPath | string | 实际上游路径。 |
| queryString | string | 本操作为空串。 |
| createMediaResponse | object / null | 网关正常、上游 200 或 201 且 JSON 可解析时的媒体响应，字段见 api.md。 |
| createMediaResponseRaw | string | 仅上游正文无法解码时保留的诊断。 |
| resultValidationError | string | 上游成功但必填媒体字段不完整、类型不匹配或复用媒体 ID 不一致时的诊断，脚本非零退出。 |
| resultWarnings | array<string> | 实测上游顶层 status 为空数组时给出兼容提示，原始数组保留。汇总状态未知，需检查具体配对状态；不视为可展示。 |

201 表示媒体或配对已新建，200 表示相同元数据的幂等复用。保存 ID 后继续检查媒体与配对状态，不以注册成功推断 AVAILABLE。媒体结果校验失败时非零退出，恢复见 api.md。超时、5xx 或结果未知时保留已得 ID，先回读再决定后续处理。

## 接口：回读媒体及视频缩略图配对（getMedia）

### 脚本输入与构参

入口为 `scripts/get_media.py`，格式为 `python scripts/get_media.py '<JSON 参数>' [--inline] [--no-cache]`。

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 当前成员已授权的原媒体所属店铺，去除首尾空白后传网关。 |
| region | string | 是 | `NA` / `EU` / `FE`，兼容小写，标准化为大写。 |
| mediaId | string | 是 | 原媒体 ID，须为非空字符串。 |
| associatedMediaId | string | 否 | 缩略图媒体 ID；传入时只返回指定配对，省略时回读全部关联。 |
| skipDepCheck | boolean | 否 | 默认 false，只跳过本地授权 Skill 安装检测。 |
| --inline | CLI flag | 否 | 强制完整展示结果，同时保存文件。 |
| --no-cache | CLI flag | 否 | 轮询状态始终禁用响应缓存。 |
| --help | CLI flag | 否 | 展示帮助后退出，不发请求。 |

#### 上游方法、路径与 Query

| 字段 | 值或构造方式 |
|---|---|
| method | `GET` |
| path | `aplus/2020-11-01/media/{mediaId}`，mediaId 先去首尾空白，再按路径段百分号编码。 |
| queryString | associatedMediaId 存在时构造 `associatedMediaId=<编码值>`，省略时为空；不传 marketplaceId。 |
| body | 不传。 |

#### 调用示例

```bash
python scripts/get_media.py '{"sellerId":"SELLER_ID","region":"NA","mediaId":"VIDEO_MEDIA_ID","associatedMediaId":"THUMBNAIL_MEDIA_ID"}' --no-cache
```

### 脚本输出与业务结果

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应及上游状态、正文。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时可为空。 |
| resolvedPath | string | 包含编码后 mediaId 的实际上游路径。 |
| queryString | string | 实际发送的可选关联查询串。 |
| getMediaResponse | object / null | 网关正常、上游 200 且 JSON 可解析时的媒体响应，字段见 api.md。 |
| getMediaResponseRaw | string | 仅上游正文无法解码时保留的诊断。 |
| resultValidationError | string | 上游成功但必填媒体字段不完整、类型无效或返回 ID 与查询目标不一致时的诊断，脚本非零退出。 |
| resultWarnings | array<string> | 实测上游顶层 status 为空数组时给出兼容提示，原始数组保留。汇总状态未知，需检查具体配对状态；不视为可展示。 |

每次执行只查询一次。HTTP 200 表示回读完成，需继续解释媒体、配对及关联图片的 status 和 issues。状态数组可同时包含阶段与责任方，未知状态保留原值。等待处理时设定次数、时限与间隔，到上限后输出媒体 ID、当前状态及续查命令，恢复见 api.md。
