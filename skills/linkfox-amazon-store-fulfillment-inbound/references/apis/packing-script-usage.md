# 脚本输入、构参与本地输出

网关参数与响应定义见 [packing.md](packing.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：列出装箱组箱信息（listPackingGroupBoxes）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes |

#### 脚本 JSON 与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE；CLI 自动转换为大写。 |
| skipDepCheck | boolean | 否 | 默认 false；仅本地调试或外部已确认依赖时跳过安装检测，不绕过授权。 |
| confirmWrite | boolean | 否 | 本操作不要求；仅八个确定性提交操作使用此控制字段。 |
| --inline | CLI flag | 否 | 强制打印完整业务结果，仍保存响应。 |
| --no-cache | CLI flag | 否 | 强制本次读取或生成访问网关；仅在用户要求刷新或确认外部状态变化后使用。写入本来不缓存。 |

完整认证、缓存、落盘与依赖检测约定见 [接口入口](../api.md#范围与脚本契约)。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |
| packingGroupId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | Amazon wire 名称：`pageSize`。 最小值：`1`。 最大值：`100`。 未传则省略；默认值未指定。 |
| paginationToken | string | 否 | Amazon wire 名称：`paginationToken`。 最短长度：`0`。 最长长度：`1024`。 未传则省略；默认值未指定。 |

分页：响应 `pagination.nextToken` 在下次请求映射为 `paginationToken`，保留首页全部过滤条件；不自动翻页。

本操作无 Amazon 请求体；脚本拒绝传入 requestBody。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 当前操作名称，区别于异步 nextAction.operationId。 |
| method | string | GET |
| resolvedPath | string | 编码后的实际路径。 |
| developerProxy | object | 网关完整响应。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| queryString | string | 有查询时返回实际编码查询串。 |
| requestBody | object | 有请求体时回显业务对象。 |
| boxes | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |

## 接口：列出装箱组商品（listPackingGroupItems）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items |

#### 脚本 JSON 与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE；CLI 自动转换为大写。 |
| skipDepCheck | boolean | 否 | 默认 false；仅本地调试或外部已确认依赖时跳过安装检测，不绕过授权。 |
| confirmWrite | boolean | 否 | 本操作不要求；仅八个确定性提交操作使用此控制字段。 |
| --inline | CLI flag | 否 | 强制打印完整业务结果，仍保存响应。 |
| --no-cache | CLI flag | 否 | 强制本次读取或生成访问网关；仅在用户要求刷新或确认外部状态变化后使用。写入本来不缓存。 |

完整认证、缓存、落盘与依赖检测约定见 [接口入口](../api.md#范围与脚本契约)。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |
| packingGroupId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | Amazon wire 名称：`pageSize`。 最小值：`1`。 最大值：`100`。 未传则省略；默认值未指定。 |
| paginationToken | string | 否 | Amazon wire 名称：`paginationToken`。 最短长度：`0`。 最长长度：`1024`。 未传则省略；默认值未指定。 |

分页：响应 `pagination.nextToken` 在下次请求映射为 `paginationToken`，保留首页全部过滤条件；不自动翻页。

本操作无 Amazon 请求体；脚本拒绝传入 requestBody。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 当前操作名称，区别于异步 nextAction.operationId。 |
| method | string | GET |
| resolvedPath | string | 编码后的实际路径。 |
| developerProxy | object | 网关完整响应。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| queryString | string | 有查询时返回实际编码查询串。 |
| requestBody | object | 有请求体时回显业务对象。 |
| items | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |

## 接口：提交装箱信息（setPackingInformation）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | POST |
| path | string | 是 | inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation |

#### 脚本 JSON 与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE；CLI 自动转换为大写。 |
| skipDepCheck | boolean | 否 | 默认 false；仅本地调试或外部已确认依赖时跳过安装检测，不绕过授权。 |
| confirmWrite | boolean | 否 | 本操作不要求；仅八个确定性提交操作使用此控制字段。 |
| --inline | CLI flag | 否 | 强制打印完整业务结果，仍保存响应。 |
| --no-cache | CLI flag | 否 | 强制本次读取或生成访问网关；仅在用户要求刷新或确认外部状态变化后使用。写入本来不缓存。 |

完整认证、缓存、落盘与依赖检测约定见 [接口入口](../api.md#范围与脚本契约)。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |

#### Amazon 请求体（脚本 requestBody）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object | 是 | 非空对象；必填键：packageGroupings。 |

推荐显式传 requestBody，也兼容将业务字段直接放在 JSON 顶层；本地控制、Path、Query 字段不混入请求体，不接受名为 body 的顶层字段。

| requestBody 内字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| packageGroupings | array<object> | 是 | 至少 1 项。 |
| packageGroupings[].packingGroupId | string | 二选一 | 已知箱规使用已确认装箱方案内的组 ID。 |
| packageGroupings[].shipmentId | string | 二选一 | Pack Later 或 India 特定顺序使用货件 ID。 |
| packageGroupings[].boxes | array<object> | 是 | 每组 1–5000 箱。 |
| packageGroupings[].boxes[].contentInformationSource | string | 是 | BARCODE_2D 或 MANUAL_PROCESS 时 items 必须保留 null。 |
| packageGroupings[].boxes[].dimensions | object | 是 | 箱尺寸，保持 Amazon 对象结构。 |
| packageGroupings[].boxes[].weight | object | 是 | 箱重量，保持 Amazon 对象结构。 |
| packageGroupings[].boxes[].quantity | integer | 是 | 1–10000。 |
| packageGroupings[].boxes[].items | array<object> / null | 按内容来源 | 不能清理掉必需的 null。 |

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 当前操作名称，区别于异步 nextAction.operationId。 |
| method | string | POST |
| resolvedPath | string | 编码后的实际路径。 |
| developerProxy | object | 网关完整响应。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| queryString | string | 有查询时返回实际编码查询串。 |
| requestBody | object | 有请求体时回显业务对象。 |
| operation | object / array / scalar / null | 仅上游 202 且网关正常时解析 body；空 body 为 null。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| nextAction | object | 有异步任务标识时返回，执行器不自动执行。 |
| nextAction.operationId | string | 异步任务 ID，来自 body.operationId 或 body.payload.operationId。 |
| nextAction.script | string | get_inbound_operation_status.py。 |
| nextAction.params | object | sellerId、region、operationId。 |
| nextAction.automaticPolling | boolean | 固定 false。 |


#### 业务结果使用

上游返回 `operationId`。

## 接口：列出装箱方案（listPackingOptions）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions |

#### 脚本 JSON 与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE；CLI 自动转换为大写。 |
| skipDepCheck | boolean | 否 | 默认 false；仅本地调试或外部已确认依赖时跳过安装检测，不绕过授权。 |
| confirmWrite | boolean | 否 | 本操作不要求；仅八个确定性提交操作使用此控制字段。 |
| --inline | CLI flag | 否 | 强制打印完整业务结果，仍保存响应。 |
| --no-cache | CLI flag | 否 | 强制本次读取或生成访问网关；仅在用户要求刷新或确认外部状态变化后使用。写入本来不缓存。 |

完整认证、缓存、落盘与依赖检测约定见 [接口入口](../api.md#范围与脚本契约)。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | Amazon wire 名称：`pageSize`。 最小值：`1`。 最大值：`20`。 未传则省略；默认值未指定。 |
| paginationToken | string | 否 | Amazon wire 名称：`paginationToken`。 最短长度：`0`。 最长长度：`1024`。 未传则省略；默认值未指定。 |

分页：响应 `pagination.nextToken` 在下次请求映射为 `paginationToken`，保留首页全部过滤条件；不自动翻页。

本操作无 Amazon 请求体；脚本拒绝传入 requestBody。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 当前操作名称，区别于异步 nextAction.operationId。 |
| method | string | GET |
| resolvedPath | string | 编码后的实际路径。 |
| developerProxy | object | 网关完整响应。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| queryString | string | 有查询时返回实际编码查询串。 |
| requestBody | object | 有请求体时回显业务对象。 |
| packingOptions | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 `packingOptions`。

## 接口：生成装箱方案（generatePackingOptions）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | POST |
| path | string | 是 | inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions |

#### 脚本 JSON 与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE；CLI 自动转换为大写。 |
| skipDepCheck | boolean | 否 | 默认 false；仅本地调试或外部已确认依赖时跳过安装检测，不绕过授权。 |
| confirmWrite | boolean | 否 | 本操作不要求；仅八个确定性提交操作使用此控制字段。 |
| --inline | CLI flag | 否 | 强制打印完整业务结果，仍保存响应。 |
| --no-cache | CLI flag | 否 | 强制本次读取或生成访问网关；仅在用户要求刷新或确认外部状态变化后使用。写入本来不缓存。 |

完整认证、缓存、落盘与依赖检测约定见 [接口入口](../api.md#范围与脚本契约)。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |

本操作无 Amazon 请求体；脚本拒绝传入 requestBody。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 当前操作名称，区别于异步 nextAction.operationId。 |
| method | string | POST |
| resolvedPath | string | 编码后的实际路径。 |
| developerProxy | object | 网关完整响应。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| queryString | string | 有查询时返回实际编码查询串。 |
| requestBody | object | 有请求体时回显业务对象。 |
| operation | object / array / scalar / null | 仅上游 202 且网关正常时解析 body；空 body 为 null。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| nextAction | object | 有异步任务标识时返回，执行器不自动执行。 |
| nextAction.operationId | string | 异步任务 ID，来自 body.operationId 或 body.payload.operationId。 |
| nextAction.script | string | get_inbound_operation_status.py。 |
| nextAction.params | object | sellerId、region、operationId。 |
| nextAction.automaticPolling | boolean | 固定 false。 |


#### 业务结果使用

上游返回 `operationId`。

## 接口：确认装箱方案（confirmPackingOption）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | POST |
| path | string | 是 | inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation |

#### 脚本 JSON 与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE；CLI 自动转换为大写。 |
| skipDepCheck | boolean | 否 | 默认 false；仅本地调试或外部已确认依赖时跳过安装检测，不绕过授权。 |
| confirmWrite | boolean | 提交类必填 | 八个提交操作须在用户明确确认后传 true；其余操作不要求此控制字段。 |
| --inline | CLI flag | 否 | 强制打印完整业务结果，仍保存响应。 |
| --no-cache | CLI flag | 否 | 强制本次读取或生成访问网关；仅在用户要求刷新或确认外部状态变化后使用。写入本来不缓存。 |

完整认证、缓存、落盘与依赖检测约定见 [接口入口](../api.md#范围与脚本契约)。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |
| packingOptionId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |

本操作无 Amazon 请求体；脚本拒绝传入 requestBody。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 当前操作名称，区别于异步 nextAction.operationId。 |
| method | string | POST |
| resolvedPath | string | 编码后的实际路径。 |
| developerProxy | object | 网关完整响应。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| queryString | string | 有查询时返回实际编码查询串。 |
| requestBody | object | 有请求体时回显业务对象。 |
| operation | object / array / scalar / null | 仅上游 202 且网关正常时解析 body；空 body 为 null。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| nextAction | object | 有异步任务标识时返回，执行器不自动执行。 |
| nextAction.operationId | string | 异步任务 ID，来自 body.operationId 或 body.payload.operationId。 |
| nextAction.script | string | get_inbound_operation_status.py。 |
| nextAction.params | object | sellerId、region、operationId。 |
| nextAction.automaticPolling | boolean | 固定 false。 |


#### 业务结果使用

上游返回 `operationId`。

## 接口：列出计划托盘（listInboundPlanPallets）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets |

#### 脚本 JSON 与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE；CLI 自动转换为大写。 |
| skipDepCheck | boolean | 否 | 默认 false；仅本地调试或外部已确认依赖时跳过安装检测，不绕过授权。 |
| confirmWrite | boolean | 否 | 本操作不要求；仅八个确定性提交操作使用此控制字段。 |
| --inline | CLI flag | 否 | 强制打印完整业务结果，仍保存响应。 |
| --no-cache | CLI flag | 否 | 强制本次读取或生成访问网关；仅在用户要求刷新或确认外部状态变化后使用。写入本来不缓存。 |

完整认证、缓存、落盘与依赖检测约定见 [接口入口](../api.md#范围与脚本契约)。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 长度 38–38；模式 `^[a-zA-Z0-9-]*$`。 URL path 分段百分号编码，不拼接未编码输入。 |

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | Amazon wire 名称：`pageSize`。 最小值：`1`。 最大值：`1000`。 未传则省略；默认值未指定。 |
| paginationToken | string | 否 | Amazon wire 名称：`paginationToken`。 最短长度：`0`。 最长长度：`1024`。 未传则省略；默认值未指定。 |

分页：响应 `pagination.nextToken` 在下次请求映射为 `paginationToken`，保留首页全部过滤条件；不自动翻页。

本操作无 Amazon 请求体；脚本拒绝传入 requestBody。

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 当前操作名称，区别于异步 nextAction.operationId。 |
| method | string | GET |
| resolvedPath | string | 编码后的实际路径。 |
| developerProxy | object | 网关完整响应。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态，连接失败为 null。 |
| queryString | string | 有查询时返回实际编码查询串。 |
| requestBody | object | 有请求体时回显业务对象。 |
| pallets | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |
