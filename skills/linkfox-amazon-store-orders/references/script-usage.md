# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：搜索订单（searchOrders）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| marketplaceIds | string[] / string | 是 | 站点 ID 列表，长度 1～50（上游要求以 Amazon 为准）；脚本接受逗号分隔字符串，并在请求前检查非空及数量。 |
| createdAfter | string | 条件 | ISO 8601；与 lastUpdatedAfter 二选一，使用本字段时不得同时传另一组的时间字段。 |
| createdBefore | string | 否 | 与 createdAfter 同组使用；不可与 lastUpdatedAfter 同用。 |
| lastUpdatedAfter | string | 条件 | ISO 8601；与 createdAfter 二选一。 |
| lastUpdatedBefore | string | 否 | 与 lastUpdatedAfter 同组使用；不可与 createdAfter 同用。 |
| fulfillmentStatuses | string[] / string | 否 | 如 PENDING、UNSHIPPED、SHIPPED、CANCELLED 等；脚本也接受逗号分隔字符串。 |
| fulfilledBy | string[] / string | 否 | MERCHANT、AMAZON；脚本也接受逗号分隔字符串。 |
| maxResultsPerPage | number / string | 否 | 上游每页 1～100，Amazon 默认 100；脚本使用 int() 转换（数值小数截断、兼容整数字符串），转换后必须在 1～100。不传或 null 时省略；布尔值、无法转换或转换后越界时请求前报错。 |
| paginationToken | string | 否 | 上一页响应 nextToken，去首尾空白后编码。 |
| includedData | string[] / string | 否 | BUYER、RECIPIENT、PROCEEDS、FULFILLMENT、PACKAGES 等，具体以官方 Orders 文档为准；脚本也接受逗号分隔字符串。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

#### 查询参数映射与限制

数组字段分别展开为重复键名，每个值单独百分号编码；字符串先按逗号切分并去空白。时间、分页字段去空白后编码，queryString 不含 ?。脚本在请求前检查时间组互斥、站点非空及最多 50 个、每页条数转换后为 1～100 的整数；不通过反复请求探测。searchOrders 默认速率约为 **0.0056 req/s**，注意 429，具体以 Amazon 实际配额为准。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| queryString | string / null | 实际查询串，不含 ?，没有查询时为 null。 |
| searchOrders | object / array / null | LinkFox 外层状态正常、网关 errcode 正常且上游 httpStatus 为 200 时解析 body；空 body 为 null，失败状态不添加。 |
| searchOrdersRaw | string | 仅 JSON 解析失败时保留原始 body，同时解析字段为 null。 |

#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：获取订单详情（getOrder）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |
| includedData | string[] / string | 否 | 官方 includedData 数据集，如 BUYER、FULFILLMENT、PACKAGES；支持数组或逗号字符串。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

#### 查询参数映射

includedData 按重复键名展开，每个值单独百分号编码；无值时不传 queryString。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| queryString | string / null | 实际查询串，不含 ?，没有查询时为 null。 |
| order | object / array / null | LinkFox 外层状态正常、网关 errcode 正常且上游 httpStatus 为 200 时解析 body；空 body 为 null，失败状态不添加。 |
| orderRaw | string | 仅 JSON 解析失败时保留原始 body，同时解析字段为 null。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：获取订单买家信息（getOrderBuyerInfo）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| buyerInfo | object / array / null | LinkFox 外层状态正常、网关 errcode 正常且上游 httpStatus 为 200 时解析 body；空 body 为 null，失败状态不添加。 |
| buyerInfoRaw | string | 仅 JSON 解析失败时保留原始 body，同时解析字段为 null。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：获取收货地址（getOrderAddress）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| shippingAddress | object / array / null | LinkFox 外层状态正常、网关 errcode 正常且上游 httpStatus 为 200 时解析 body；空 body 为 null，失败状态不添加。 |
| shippingAddressRaw | string | 仅 JSON 解析失败时保留原始 body，同时解析字段为 null。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：获取订单商品（getOrderItems）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |
| nextToken | string | 否 | 映射到大小写敏感的查询参数 NextToken。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

#### 查询参数映射

nextToken 去首尾空白后百分号编码，写入 `NextToken=<编码值>`；大小写保持 NextToken。不传时省略 queryString。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| queryString | string / null | 实际查询串，不含 ?，没有查询时为 null。 |
| orderItems | object / array / null | LinkFox 外层状态正常、网关 errcode 正常且上游 httpStatus 为 200 时解析 body；空 body 为 null，失败状态不添加。 |
| orderItemsRaw | string | 仅 JSON 解析失败时保留原始 body，同时解析字段为 null。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：获取订单商品买家信息（getOrderItemsBuyerInfo）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |
| nextToken | string | 否 | 映射到大小写敏感的查询参数 NextToken。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

#### 查询参数映射

nextToken 去首尾空白后百分号编码，写入 `NextToken=<编码值>`；大小写保持 NextToken。不传时省略 queryString。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| queryString | string / null | 实际查询串，不含 ?，没有查询时为 null。 |
| orderItemsBuyerInfo | object / array / null | LinkFox 外层状态正常、网关 errcode 正常且上游 httpStatus 为 200 时解析 body；空 body 为 null，失败状态不添加。 |
| orderItemsBuyerInfoRaw | string | 仅 JSON 解析失败时保留原始 body，同时解析字段为 null。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：更新配送状态（updateShipmentStatus）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |
| marketplaceId | string | 是 | 目标站点 ID，写入上游 body；脚本去首尾空白。 |
| shipmentStatus | string | 是 | ReadyForPickup、PickedUp、RefusedPickup，脚本校验该枚举。 |
| orderItems | object[] | 否 | 部分更新时的行项目与数量；传入时必须为数组，数组元素原样转发，内部字段按 Amazon schema 提供。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

#### 上游请求体映射

由 marketplaceId、shipmentStatus 及可选 orderItems 组装对象后序列化为网关 body。orderItems 中的嵌套对象保留原值。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| requestBody | object | 组装后的 Amazon 请求体，便于核对与排查。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：获取管制订单信息（getOrderRegulatedInfo）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| regulatedOrder | object / array / null | LinkFox 外层状态正常、网关 errcode 正常且上游 httpStatus 为 200 时解析 body；空 body 为 null，失败状态不添加。 |
| regulatedOrderRaw | string | 仅 JSON 解析失败时保留原始 body，同时解析字段为 null。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：更新买家核验状态（updateVerificationStatus）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |
| regulatedOrderVerificationStatus | object | 条件 | 未提供 requestBody 对象时必填，且必须为对象；脚本包装为 {"regulatedOrderVerificationStatus": ...}。内部 schema 按 Amazon 要求提供，不补造字段。 |
| requestBody | object | 条件 | 完整 PATCH body；提供对象时优先采用，不再包装。应包含 regulatedOrderVerificationStatus 对象，脚本不做深层校验。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

#### 上游请求体映射

requestBody 为对象时直接序列化；否则要求 regulatedOrderVerificationStatus 为对象，包装后序列化。支持两种输入方式，两者同时提供时采用 requestBody；不在本地推断或补造内部 schema。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| requestBody | object | 组装后的 Amazon 请求体，便于核对与排查。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |

## 接口：确认发货（confirmShipment）

### 脚本输入与构参

#### 脚本 JSON 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID；用于网关选店。 |
| region | string | 是 | NA / EU / FE 等，与授权区域一致。 |
| orderId | string | 是 | 亚马逊订单号；脚本去首尾空白并做 URL path 分段百分号编码。 |
| requestBody | object | 是 | 官方 confirmShipment 要求的完整 JSON 对象，通常含 packageDetail 等；原样转发，内部 schema 按 Amazon 要求提供。 |

#### 脚本选项与运行约定

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skipDepCheck | boolean | 否 | 默认 false；true 时跳过本地依赖探测，仅用于外部流程已确认依赖的情况，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 不启用响应缓存；业务封装调用 run 时始终加入此选项，读取和写入均不复用或保存响应缓存。 |

业务 CLI 的 JSON 顶层必须为对象；缺失、null 或纯空白的必填标识在请求前报错，合法的数组、逗号字符串及请求体输入按本接口定义处理。
本地依赖检测返回 0 表示找到认证技能；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失，先安装 `linkfox-amazon-store-auth`，不要在本技能绕过依赖实现授权或令牌逻辑。依赖检测也支持认证技能目录别名 `linkfox-amazon-spapi-auth`，并在支持的安装目录中探测。
环境变量优先级为 `LINKFOX_TOOL_GATEWAY`、`STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`；API key 支持 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。当前目录必须可写，请求前检查；会话结果不回退到家目录或临时目录。

#### 上游请求体映射

requestBody 必须为 JSON 对象，包含用户提供的完整 confirmShipment 资料；包含的 packageDetail 等嵌套字段全部原样转发。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object | 网关原样响应；先判断网关和上游状态，再读取业务字段。 |
| resolvedPath | string | 实际编码后的相对资源路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败时为 null。 |
| requestBody | object | 组装后的 Amazon 请求体，便于核对与排查。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 传输错误时可能出现，如连接失败或非 JSON HTTP 错误。 |
| details | string | 非 JSON HTTP 错误的原始响应内容，存在时保留。 |
