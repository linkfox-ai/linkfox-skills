# 脚本输入、构参与本地输出

网关参数与响应定义见 [prep-compliance-labels.md](prep-compliance-labels.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：列出商品合规信息（listItemComplianceDetails）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | inbound/fba/2024-03-20/items/compliance |

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

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| mskus | array<string> / string | 是 | Amazon wire 名称：`mskus`。 最少项数：`1`。 最多项数：`100`。 最短长度：`1`。 最长长度：`255`。 CLI 接受数组或逗号分隔字符串；wire 使用重复键。 必填，缺失时本地拒绝；默认值未指定。 |
| marketplaceId | string | 是 | Amazon wire 名称：`marketplaceId`。 最短长度：`1`。 最长长度：`20`。 必填，缺失时本地拒绝；默认值未指定。 |

MSKU 的 `%`、`+`、`,` 最终分别为 `%2525`、`%252B`、`%252C`；不静默截断超长列表，由调用方显式分批。

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
| complianceDetails | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 `complianceDetails`；India 专用。

## 接口：更新商品合规信息（updateItemComplianceDetails）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | PUT |
| path | string | 是 | inbound/fba/2024-03-20/items/compliance |

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

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | Amazon wire 名称：`marketplaceId`。 最短长度：`1`。 最长长度：`20`。 必填，缺失时本地拒绝；默认值未指定。 |

#### Amazon 请求体（脚本 requestBody）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object | 是 | 非空对象；必填键：msku, taxDetails。 |

推荐显式传 requestBody，也兼容将业务字段直接放在 JSON 顶层；本地控制、Path、Query 字段不混入请求体，不接受名为 body 的顶层字段。

| requestBody 内字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| msku | string | 是 | 目标卖家 SKU。 |
| taxDetails | object | 是 | India 税务合规信息；子字段清单未指定，不补造。 |

### 脚本输出与业务结果

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 当前操作名称，区别于异步 nextAction.operationId。 |
| method | string | PUT |
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

上游返回 `operationId`；India 专用。

## 接口：生成商品标签（createMarketplaceItemLabels）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | POST |
| path | string | 是 | inbound/fba/2024-03-20/items/labels |

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

#### Amazon 请求体（脚本 requestBody）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object | 是 | 非空对象；必填键：labelType, marketplaceId, mskuQuantities。 |

推荐显式传 requestBody，也兼容将业务字段直接放在 JSON 顶层；本地控制、Path、Query 字段不混入请求体，不接受名为 body 的顶层字段。

| requestBody 内字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| labelType | string | 是 | 商品标签类型，保留 Amazon 值。 |
| marketplaceId | string | 是 | 目标市场。 |
| mskuQuantities | array<object> | 是 | 1–100 项。 |
| mskuQuantities[].msku | string | 是 | 1–255 字符。 |
| mskuQuantities[].quantity | integer | 是 | 1–10000。 |
| pageType | string | 否 | 标签纸型。 |
| localeCode | string | 否 | 本地化语言代码。 |
| width | number | 否 | 自定义宽度，保留原值。 |
| height | number | 否 | 自定义高度，保留原值。 |

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
| marketplaceItemLabels | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 `documentDownloads`。

## 接口：列出预处理信息（listPrepDetails）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | inbound/fba/2024-03-20/items/prepDetails |

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

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | Amazon wire 名称：`marketplaceId`。 最短长度：`1`。 最长长度：`20`。 必填，缺失时本地拒绝；默认值未指定。 |
| mskus | array<string> / string | 是 | Amazon wire 名称：`mskus`。 最少项数：`1`。 最多项数：`100`。 最短长度：`1`。 最长长度：`255`。 CLI 接受数组或逗号分隔字符串；wire 使用重复键。 必填，缺失时本地拒绝；默认值未指定。 |

MSKU 的 `%`、`+`、`,` 最终分别为 `%2525`、`%252B`、`%252C`；不静默截断超长列表，由调用方显式分批。

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
| prepDetails | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 `mskuPrepDetails`。

## 接口：设置预处理信息（setPrepDetails）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | POST |
| path | string | 是 | inbound/fba/2024-03-20/items/prepDetails |

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

#### Amazon 请求体（脚本 requestBody）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object | 是 | 非空对象；必填键：marketplaceId, mskuPrepDetails。 |

推荐显式传 requestBody，也兼容将业务字段直接放在 JSON 顶层；本地控制、Path、Query 字段不混入请求体，不接受名为 body 的顶层字段。

| requestBody 内字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标市场。 |
| mskuPrepDetails | array<object> | 是 | 1–100 项。 |
| mskuPrepDetails[].msku | string | 是 | 1–255 字符。 |
| mskuPrepDetails[].prepCategory | string | 是 | FC_PROVIDED 不可更改；NONE 不代表无贴标要求。 |
| mskuPrepDetails[].prepTypes | array | 是 | 预处理类型列表，允许空列表；保留实际值。 |

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
