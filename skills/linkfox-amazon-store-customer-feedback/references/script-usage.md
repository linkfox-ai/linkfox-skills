# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：商品评论主题（getItemReviewTopics）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE` 等区域。 |
| asin | string | 是 | 商品 ASIN，一般使用子体 ASIN；脚本去除首尾空白后按 path 分段编码。 |
| marketplaceId | string | 条件必填 | 单站点编号；优先于 marketplaceIds，无默认值。 |
| marketplaceIds | array[string] / string | 条件必填 | marketplaceId 未传时的兼容输入；数组只取首项，多项向 stderr 警告；非空字符串作为单值。两种输入至少提供一种。 |
| sortBy | string | 是 | `MENTIONS` 或 `STAR_RATING_IMPACT`；脚本去除首尾空白并转大写，其他值在请求前报错。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部流程已确认依赖时跳过本地安装检查，不绕过店铺授权。 |

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 单个站点编号，例如 `ATVPDKIKX0DER`；不是多站点列表。 |
| sortBy | string | 是 | `MENTIONS`（主题提及量）或 `STAR_RATING_IMPACT`（星级影响）；按任务可分别查询对照。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终添加，不读取或保存响应缓存。公共调用器仍可能创建空缓存目录。 |

使用 `python scripts/get_item_review_topics.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查通过返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-amazon-store-auth`，不另行实现授权。依赖检测支持目录别名 `linkfox-amazon-spapi-auth`，兼容常见安装目录及 Hermes 分类与插件目录。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。接口密钥兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`；会话头包含 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。完整响应写入当前工作目录，不回退到 `/tmp`；根目录及实际会话 data 目录不可写时均在请求前报错。

#### 接口使用限制

- 依赖 `linkfox-amazon-store-auth` 选店及授权；通常需 Brand Analytics 或 Selling Partner Insights 等角色。站点支持以 Amazon 为准，常见 US / UK / DE 等。
- 网关白名单需包含 `customerFeedback/2024-06-01/`；转发上游 GET。
- 数据刷新以 Amazon 为准，通常按周；本接口不是 Orders 订单接口。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，保留错误和 body。 |
| resolvedPath | string | 实际使用的编码后 path。 |
| queryString | string | 实际发送的查询串，无问号前缀。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| itemReviewTopics | object / array / scalar / null | 外层及网关正常、上游 httpStatus 为 200 时解析的完整 body；空 body 或解析失败为 null。非成功时不创建此字段。 |
| itemReviewTopicsRaw | string | 仅 JSON 解析失败时保留原始非空 body。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接异常时的错误说明（若返回）。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文（若返回）。 |

## 接口：商品所属类目（getItemBrowseNode）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE` 等区域。 |
| asin | string | 是 | 商品 ASIN，一般使用子体 ASIN；脚本去除首尾空白后按 path 分段编码。 |
| marketplaceId | string | 条件必填 | 单站点编号；优先于 marketplaceIds，无默认值。 |
| marketplaceIds | array[string] / string | 条件必填 | marketplaceId 未传时的兼容输入；数组只取首项，多项向 stderr 警告；非空字符串作为单值。两种输入至少提供一种。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部流程已确认依赖时跳过本地安装检查，不绕过店铺授权。 |

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 单个站点编号，例如 `ATVPDKIKX0DER`；不是多站点列表。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终添加，不读取或保存响应缓存。公共调用器仍可能创建空缓存目录。 |

使用 `python scripts/get_item_browse_node.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查通过返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-amazon-store-auth`，不另行实现授权。依赖检测支持目录别名 `linkfox-amazon-spapi-auth`，兼容常见安装目录及 Hermes 分类与插件目录。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。接口密钥兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`；会话头包含 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。完整响应写入当前工作目录，不回退到 `/tmp`；根目录及实际会话 data 目录不可写时均在请求前报错。

#### 接口使用限制

- 依赖 `linkfox-amazon-store-auth` 选店及授权；通常需 Brand Analytics 或 Selling Partner Insights 等角色。站点支持以 Amazon 为准，常见 US / UK / DE 等。
- 网关白名单需包含 `customerFeedback/2024-06-01/`；转发上游 GET。
- 数据刷新以 Amazon 为准，通常按周；本接口不是 Orders 订单接口。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，保留错误和 body。 |
| resolvedPath | string | 实际使用的编码后 path。 |
| queryString | string | 实际发送的查询串，无问号前缀。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| itemBrowseNode | object / array / scalar / null | 外层及网关正常、上游 httpStatus 为 200 时解析的完整 body；空 body 或解析失败为 null。非成功时不创建此字段。 |
| itemBrowseNodeRaw | string | 仅 JSON 解析失败时保留原始非空 body。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接异常时的错误说明（若返回）。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文（若返回）。 |

## 接口：商品评论趋势（getItemReviewTrends）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE` 等区域。 |
| asin | string | 是 | 商品 ASIN，一般使用子体 ASIN；脚本去除首尾空白后按 path 分段编码。 |
| marketplaceId | string | 条件必填 | 单站点编号；优先于 marketplaceIds，无默认值。 |
| marketplaceIds | array[string] / string | 条件必填 | marketplaceId 未传时的兼容输入；数组只取首项，多项向 stderr 警告；非空字符串作为单值。两种输入至少提供一种。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部流程已确认依赖时跳过本地安装检查，不绕过店铺授权。 |

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 单个站点编号，例如 `ATVPDKIKX0DER`；不是多站点列表。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终添加，不读取或保存响应缓存。公共调用器仍可能创建空缓存目录。 |

使用 `python scripts/get_item_review_trends.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查通过返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-amazon-store-auth`，不另行实现授权。依赖检测支持目录别名 `linkfox-amazon-spapi-auth`，兼容常见安装目录及 Hermes 分类与插件目录。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。接口密钥兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`；会话头包含 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。完整响应写入当前工作目录，不回退到 `/tmp`；根目录及实际会话 data 目录不可写时均在请求前报错。

#### 接口使用限制

- 依赖 `linkfox-amazon-store-auth` 选店及授权；通常需 Brand Analytics 或 Selling Partner Insights 等角色。站点支持以 Amazon 为准，常见 US / UK / DE 等。
- 网关白名单需包含 `customerFeedback/2024-06-01/`；转发上游 GET。
- 数据刷新以 Amazon 为准，通常按周；本接口不是 Orders 订单接口。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，保留错误和 body。 |
| resolvedPath | string | 实际使用的编码后 path。 |
| queryString | string | 实际发送的查询串，无问号前缀。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| itemReviewTrends | object / array / scalar / null | 外层及网关正常、上游 httpStatus 为 200 时解析的完整 body；空 body 或解析失败为 null。非成功时不创建此字段。 |
| itemReviewTrendsRaw | string | 仅 JSON 解析失败时保留原始非空 body。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接异常时的错误说明（若返回）。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文（若返回）。 |

## 接口：类目评论主题（getBrowseNodeReviewTopics）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE` 等区域。 |
| browseNodeId | string | 是 | 类目 browse node 编号，可从 getItemBrowseNode 的实际响应取得；脚本去除首尾空白后按 path 分段编码。 |
| marketplaceId | string | 条件必填 | 单站点编号；优先于 marketplaceIds，无默认值。 |
| marketplaceIds | array[string] / string | 条件必填 | marketplaceId 未传时的兼容输入；数组只取首项，多项向 stderr 警告；非空字符串作为单值。两种输入至少提供一种。 |
| sortBy | string | 是 | `MENTIONS` 或 `STAR_RATING_IMPACT`；脚本去除首尾空白并转大写，其他值在请求前报错。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部流程已确认依赖时跳过本地安装检查，不绕过店铺授权。 |

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 单个站点编号，例如 `ATVPDKIKX0DER`；不是多站点列表。 |
| sortBy | string | 是 | `MENTIONS`（主题提及量）或 `STAR_RATING_IMPACT`（星级影响）；按任务可分别查询对照。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终添加，不读取或保存响应缓存。公共调用器仍可能创建空缓存目录。 |

使用 `python scripts/get_browse_node_review_topics.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查通过返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-amazon-store-auth`，不另行实现授权。依赖检测支持目录别名 `linkfox-amazon-spapi-auth`，兼容常见安装目录及 Hermes 分类与插件目录。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。接口密钥兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`；会话头包含 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。完整响应写入当前工作目录，不回退到 `/tmp`；根目录及实际会话 data 目录不可写时均在请求前报错。

#### 接口使用限制

- 依赖 `linkfox-amazon-store-auth` 选店及授权；通常需 Brand Analytics 或 Selling Partner Insights 等角色。站点支持以 Amazon 为准，常见 US / UK / DE 等。
- 网关白名单需包含 `customerFeedback/2024-06-01/`；转发上游 GET。
- 数据刷新以 Amazon 为准，通常按周；本接口不是 Orders 订单接口。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，保留错误和 body。 |
| resolvedPath | string | 实际使用的编码后 path。 |
| queryString | string | 实际发送的查询串，无问号前缀。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| browseNodeReviewTopics | object / array / scalar / null | 外层及网关正常、上游 httpStatus 为 200 时解析的完整 body；空 body 或解析失败为 null。非成功时不创建此字段。 |
| browseNodeReviewTopicsRaw | string | 仅 JSON 解析失败时保留原始非空 body。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接异常时的错误说明（若返回）。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文（若返回）。 |

## 接口：类目评论趋势（getBrowseNodeReviewTrends）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE` 等区域。 |
| browseNodeId | string | 是 | 类目 browse node 编号，可从 getItemBrowseNode 的实际响应取得；脚本去除首尾空白后按 path 分段编码。 |
| marketplaceId | string | 条件必填 | 单站点编号；优先于 marketplaceIds，无默认值。 |
| marketplaceIds | array[string] / string | 条件必填 | marketplaceId 未传时的兼容输入；数组只取首项，多项向 stderr 警告；非空字符串作为单值。两种输入至少提供一种。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部流程已确认依赖时跳过本地安装检查，不绕过店铺授权。 |

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 单个站点编号，例如 `ATVPDKIKX0DER`；不是多站点列表。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终添加，不读取或保存响应缓存。公共调用器仍可能创建空缓存目录。 |

使用 `python scripts/get_browse_node_review_trends.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查通过返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-amazon-store-auth`，不另行实现授权。依赖检测支持目录别名 `linkfox-amazon-spapi-auth`，兼容常见安装目录及 Hermes 分类与插件目录。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。接口密钥兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`；会话头包含 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。完整响应写入当前工作目录，不回退到 `/tmp`；根目录及实际会话 data 目录不可写时均在请求前报错。

#### 接口使用限制

- 依赖 `linkfox-amazon-store-auth` 选店及授权；通常需 Brand Analytics 或 Selling Partner Insights 等角色。站点支持以 Amazon 为准，常见 US / UK / DE 等。
- 网关白名单需包含 `customerFeedback/2024-06-01/`；转发上游 GET。
- 数据刷新以 Amazon 为准，通常按周；本接口不是 Orders 订单接口。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，保留错误和 body。 |
| resolvedPath | string | 实际使用的编码后 path。 |
| queryString | string | 实际发送的查询串，无问号前缀。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| browseNodeReviewTrends | object / array / scalar / null | 外层及网关正常、上游 httpStatus 为 200 时解析的完整 body；空 body 或解析失败为 null。非成功时不创建此字段。 |
| browseNodeReviewTrendsRaw | string | 仅 JSON 解析失败时保留原始非空 body。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接异常时的错误说明（若返回）。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文（若返回）。 |

## 接口：类目退货主题（getBrowseNodeReturnTopics）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE` 等区域。 |
| browseNodeId | string | 是 | 类目 browse node 编号，可从 getItemBrowseNode 的实际响应取得；脚本去除首尾空白后按 path 分段编码。 |
| marketplaceId | string | 条件必填 | 单站点编号；优先于 marketplaceIds，无默认值。 |
| marketplaceIds | array[string] / string | 条件必填 | marketplaceId 未传时的兼容输入；数组只取首项，多项向 stderr 警告；非空字符串作为单值。两种输入至少提供一种。 |
| sortBy | string | 是 | `MENTIONS` 或 `STAR_RATING_IMPACT`；脚本去除首尾空白并转大写，其他值在请求前报错。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部流程已确认依赖时跳过本地安装检查，不绕过店铺授权。 |

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 单个站点编号，例如 `ATVPDKIKX0DER`；不是多站点列表。 |
| sortBy | string | 是 | `MENTIONS`（主题提及量）或 `STAR_RATING_IMPACT`（星级影响）；按任务可分别查询对照。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终添加，不读取或保存响应缓存。公共调用器仍可能创建空缓存目录。 |

使用 `python scripts/get_browse_node_return_topics.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查通过返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-amazon-store-auth`，不另行实现授权。依赖检测支持目录别名 `linkfox-amazon-spapi-auth`，兼容常见安装目录及 Hermes 分类与插件目录。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。接口密钥兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`；会话头包含 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。完整响应写入当前工作目录，不回退到 `/tmp`；根目录及实际会话 data 目录不可写时均在请求前报错。

#### 接口使用限制

- 依赖 `linkfox-amazon-store-auth` 选店及授权；通常需 Brand Analytics 或 Selling Partner Insights 等角色。站点支持以 Amazon 为准，常见 US / UK / DE 等。
- 网关白名单需包含 `customerFeedback/2024-06-01/`；转发上游 GET。
- 数据刷新以 Amazon 为准，通常按周；本接口不是 Orders 订单接口。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，保留错误和 body。 |
| resolvedPath | string | 实际使用的编码后 path。 |
| queryString | string | 实际发送的查询串，无问号前缀。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| browseNodeReturnTopics | object / array / scalar / null | 外层及网关正常、上游 httpStatus 为 200 时解析的完整 body；空 body 或解析失败为 null。非成功时不创建此字段。 |
| browseNodeReturnTopicsRaw | string | 仅 JSON 解析失败时保留原始非空 body。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接异常时的错误说明（若返回）。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文（若返回）。 |

## 接口：类目退货趋势（getBrowseNodeReturnTrends）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID。 |
| region | string | 是 | `NA` / `EU` / `FE` 等区域。 |
| browseNodeId | string | 是 | 类目 browse node 编号，可从 getItemBrowseNode 的实际响应取得；脚本去除首尾空白后按 path 分段编码。 |
| marketplaceId | string | 条件必填 | 单站点编号；优先于 marketplaceIds，无默认值。 |
| marketplaceIds | array[string] / string | 条件必填 | marketplaceId 未传时的兼容输入；数组只取首项，多项向 stderr 警告；非空字符串作为单值。两种输入至少提供一种。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部流程已确认依赖时跳过本地安装检查，不绕过店铺授权。 |

#### Query 参数（写入 queryString）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 单个站点编号，例如 `ATVPDKIKX0DER`；不是多站点列表。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终添加，不读取或保存响应缓存。公共调用器仍可能创建空缓存目录。 |

使用 `python scripts/get_browse_node_return_trends.py '<JSON 参数>' [--inline] [--no-cache]`。依赖检查通过返回 0；缺失返回 42，stderr 含 `DEPENDENCY_MISSING:`，先安装 `linkfox-amazon-store-auth`，不另行实现授权。依赖检测支持目录别名 `linkfox-amazon-spapi-auth`，兼容常见安装目录及 Hermes 分类与插件目录。

网关环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。接口密钥兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`；会话头包含 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。完整响应写入当前工作目录，不回退到 `/tmp`；根目录及实际会话 data 目录不可写时均在请求前报错。

#### 接口使用限制

- 依赖 `linkfox-amazon-store-auth` 选店及授权；通常需 Brand Analytics 或 Selling Partner Insights 等角色。站点支持以 Amazon 为准，常见 US / UK / DE 等。
- 网关白名单需包含 `customerFeedback/2024-06-01/`；转发上游 GET。
- 数据刷新以 Amazon 为准，通常按周；本接口不是 Orders 订单接口。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| developerProxy | object | 完整网关响应，保留错误和 body。 |
| resolvedPath | string | 实际使用的编码后 path。 |
| queryString | string | 实际发送的查询串，无问号前缀。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| browseNodeReturnTrends | object / array / scalar / null | 外层及网关正常、上游 httpStatus 为 200 时解析的完整 body；空 body 或解析失败为 null。非成功时不创建此字段。 |
| browseNodeReturnTrendsRaw | string | 仅 JSON 解析失败时保留原始非空 body。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | HTTP 或连接异常时的错误说明（若返回）。 |
| details | string | 无法解析为 JSON 的 HTTP 错误响应正文（若返回）。 |
