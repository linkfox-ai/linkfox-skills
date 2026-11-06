# 脚本输入、构参与本地输出

网关参数与响应定义见 [legacy-v0.md](legacy-v0.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：获取旧版预处理说明（getPrepInstructions）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | fba/inbound/v0/prepInstructions |

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
| shipToCountryCode | string | 是 | Amazon wire 名称：`ShipToCountryCode`。 最短长度：`2`。 最长长度：`2`。 模式：`^[A-Z]{2}$`。 必填，缺失时本地拒绝；默认值未指定。 |
| sellerSKUList | array<string> / string | 否 | Amazon wire 名称：`SellerSKUList`。 最多项数：`50`。 CLI 接受数组或逗号分隔字符串；wire 使用 CSV，整体百分号编码。 未传则省略；默认值未指定。 |
| asinList | array<string> / string | 否 | Amazon wire 名称：`ASINList`。 最多项数：`50`。 CLI 接受数组或逗号分隔字符串；wire 使用 CSV，整体百分号编码。 未传则省略；默认值未指定。 |

通常应提供 sellerSKUList / asinList 至少一组，各最多 50 项；不静默替换输入标识。

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
| prepInstructions | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 prep instructions 和 invalid SKU/ASIN。

## 接口：获取箱唛标签（getLabels）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | fba/inbound/v0/shipments/{shipmentId}/labels |

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
| shipmentId | string | 是 | 非空标识。 URL path 分段百分号编码，不拼接未编码输入。 v2024 工作流必须使用 getShipment 返回的 shipmentConfirmationId；允许同名 CLI 别名，两个值不同则拒绝。仅原生 v0 货件允许 legacy shipmentId。 |
| shipmentConfirmationId | string | 推荐别名 | 替代 path 的 shipmentId；与 shipmentId 同传时须一致。 |

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| pageType | string | 是 | Amazon wire 名称：`PageType`。 枚举：`PackageLabel_Letter_2` / `PackageLabel_Letter_4` / `PackageLabel_Letter_6` / `PackageLabel_Letter_6_CarrierLeft` / `PackageLabel_A4_2` / `PackageLabel_A4_4` / `PackageLabel_Plain_Paper` / `PackageLabel_Plain_Paper_CarrierBottom` / `PackageLabel_Thermal` / `PackageLabel_Thermal_Unified` / `PackageLabel_Thermal_NonPCP` / `PackageLabel_Thermal_No_Carrier_Rotation`。 必填，缺失时本地拒绝；默认值未指定。 |
| labelType | string | 是 | Amazon wire 名称：`LabelType`。 枚举：`BARCODE_2D` / `UNIQUE` / `PALLET`。 必填，缺失时本地拒绝；默认值未指定。 |
| numberOfPackages | integer | 否 | Amazon wire 名称：`NumberOfPackages`。 未传则省略；默认值未指定。 |
| packageLabelsToPrint | array<string> / string | 否 | Amazon wire 名称：`PackageLabelsToPrint`。 CLI 接受数组或逗号分隔字符串；wire 使用 CSV，整体百分号编码。 未传则省略；默认值未指定。 |
| numberOfPallets | integer | 否 | Amazon wire 名称：`NumberOfPallets`。 未传则省略；默认值未指定。 |
| pageSize | integer | 否 | Amazon wire 名称：`PageSize`。 最大值：`1000`。 未传则省略；默认值未指定。 |
| pageStartIndex | integer | 否 | Amazon wire 名称：`PageStartIndex`。 未传则省略；默认值未指定。 |

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
| labels | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 `payload.DownloadURL`。

## 接口：获取提单（getBillOfLading）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | fba/inbound/v0/shipments/{shipmentId}/billOfLading |

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
| shipmentId | string | 是 | 非空标识。 URL path 分段百分号编码，不拼接未编码输入。 v2024 工作流必须使用 getShipment 返回的 shipmentConfirmationId；允许同名 CLI 别名，两个值不同则拒绝。仅原生 v0 货件允许 legacy shipmentId。 |
| shipmentConfirmationId | string | 推荐别名 | 替代 path 的 shipmentId；与 shipmentId 同传时须一致。 |

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
| billOfLading | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 `payload.DownloadURL`。

## 接口：查询旧版货件（getShipments）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | fba/inbound/v0/shipments |

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
| shipmentStatusList | array<string> / string | 否 | Amazon wire 名称：`ShipmentStatusList`。 枚举：`WORKING` / `READY_TO_SHIP` / `SHIPPED` / `RECEIVING` / `CANCELLED` / `DELETED` / `CLOSED` / `ERROR` / `IN_TRANSIT` / `DELIVERED` / `CHECKED_IN`。 CLI 接受数组或逗号分隔字符串；wire 使用 CSV，整体百分号编码。 未传则省略；默认值未指定。 |
| shipmentIdList | array<string> / string | 否 | Amazon wire 名称：`ShipmentIdList`。 最多项数：`999`。 CLI 接受数组或逗号分隔字符串；wire 使用 CSV，整体百分号编码。 未传则省略；默认值未指定。 |
| lastUpdatedAfter | string | 否 | Amazon wire 名称：`LastUpdatedAfter`。 格式：`date-time`。 未传则省略；默认值未指定。 |
| lastUpdatedBefore | string | 否 | Amazon wire 名称：`LastUpdatedBefore`。 格式：`date-time`。 未传则省略；默认值未指定。 |
| queryType | string | 是 | Amazon wire 名称：`QueryType`。 枚举：`SHIPMENT` / `DATE_RANGE` / `NEXT_TOKEN`。 必填，缺失时本地拒绝；默认值未指定。 |
| nextToken | string | 否 | Amazon wire 名称：`NextToken`。 未传则省略；默认值未指定。 |
| marketplaceId | string | 是 | Amazon wire 名称：`MarketplaceId`。 必填，缺失时本地拒绝；默认值未指定。 |

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
| shipments | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 `ShipmentData`、`NextToken`。

## 接口：按旧版货件查询商品（getShipmentItemsByShipmentId）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | fba/inbound/v0/shipments/{shipmentId}/items |

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
| shipmentId | string | 是 | 非空标识。 URL path 分段百分号编码，不拼接未编码输入。 |

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 否 | Amazon wire 名称：`MarketplaceId`。 未传则省略；默认值未指定。 |

marketplaceId 已废弃，正常调用省略；CLI 仍支持该字段的兼容映射，不自动分页。

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
| shipmentItems | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |



#### 业务结果使用

上游返回 `ItemData`、`NextToken`。

## 接口：查询旧版货件商品（getShipmentItems）

### 脚本输入与构参

#### Amazon 方法与资源

| 字段 | 类型 | 必填 | 固定值 |
|---|---|---|---|
| method | string | 是 | GET |
| path | string | 是 | fba/inbound/v0/shipments/{shipmentId}/items |

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
| shipmentId | string | 是 | 非空标识。 URL path 分段百分号编码，不拼接未编码输入。 |

#### Query 参数

| CLI 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 否 | Amazon wire 名称：`MarketplaceId`。 未传则省略；默认值未指定。 |

marketplaceId 已废弃，正常调用省略；CLI 仍支持该字段的兼容映射，不自动分页。

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
| shipmentItems | object / array / scalar / null | 仅上游 200 且网关正常时解析 body；空 body 为 null。 |

#### 业务结果使用

上游返回 `ItemData`、`NextToken`。
