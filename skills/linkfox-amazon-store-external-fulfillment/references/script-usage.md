# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：按 location 查询或发布库存（batchInventory）

### 脚本输入与构参

本接口上游方法为 `POST`，`path` 为 `externalFulfillment/inventory/2024-09-11/inventories`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| requests | object[] | 是 | 1～10 条，每项必须是 JSON 对象（两种模式均在请求前校验）；默认使用下方简化项；useAmazonRequestShape=true 时直接传官方原始数组。 |
| useAmazonRequestShape | boolean | 否 | 默认 false；true 时跳过简化项转换，但仍检查 requests 为 1～10 条。 |
| requests[].action | string | 简化项必填 | fetch / update；脚本去除首尾空白并转小写。 |
| requests[].locationId | string | 简化项必填 | MFN 单仓常用 DEFAULT；Seller Flex 使用 4 位仓码。 |
| requests[].skuId | string | 简化项必填 | 卖家 SKU；与 locationId 使用 urlencode 编码到子请求 uri。 |
| requests[].quantity | integer | update 必填 | 绝对库存，非增量；只同步有变化的 SKU。 |
| requests[].clientSequenceNumber | integer | 否 | 客户端序列号；fetch / update 简化项均支持，原值透传。 |
| requests[].marketplaceAttributes | object | 否 | 多站点常需提供站点与渠道信息。 |
| requests[].marketplaceAttributes.marketplaceId | string | 视渠道 | 目标站点 ID。 |
| requests[].marketplaceAttributes.channelName | string | 视渠道 | 渠道名，如 MFN。 |
| requests[].method | string | 官方原始项必填 | 官方子请求方法；简化模式对 fetch / update 均组装 POST。 |
| requests[].uri | string | 官方原始项必填 | 例如 /inventory/fetch?locationId=DEFAULT&skuId=SKU-1；update 为 /inventory/update。 |
| requests[].body | object | 视操作 | 子请求对象；简化模式含 marketplaceAttributes、quantity、clientSequenceNumber 中已提供字段，无字段时省略。 |
| requests[].body.quantity | integer | 原始 update 必填 | 绝对库存；简化 quantity 映射至此。 |
| requests[].body.clientSequenceNumber | integer | 否 | 客户端序列号。 |
| requests[].body.marketplaceAttributes | object | 否 | 与简化 marketplaceAttributes 同结构，包含 marketplaceId、channelName。 |
| requests[].body.marketplaceAttributes.marketplaceId | string | 视渠道 | 目标站点 ID；简化项映射至此。 |
| requests[].body.marketplaceAttributes.channelName | string | 视渠道 | 渠道名，如 MFN；简化项映射至此。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

简化 requests 转为 `{requests:[{method:"POST",uri:"/inventory/fetch?...",body:{...}}]}`；update 使用 `/inventory/update`。原始请求模式直接透传子项。官方：[发布 location 库存](https://developer-docs.amazon.com/sp-api/docs/publish-location-level-inventory)、[查询 location 库存](https://developer-docs.amazon.com/sp-api/docs/retrieve-location-level-inventory)。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| batchInventory | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| batchInventoryRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| requestBody | object / null | 脚本实际组装的请求体。 |
| batchInventory.responses | object[] | 批量操作逐项响应，HTTP 207 并不表示所有子项成功。 |
| batchInventory.responses[].status | integer | 每一子项的实际状态，逐条检查。 |

## 接口：查询货件列表（getShipments）

### 脚本输入与构参

本接口上游方法为 `GET`，`path` 为 `externalFulfillment/2024-09-11/shipments`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| status | string | 是 | 货件状态，如 ACCEPTED、CREATED、CONFIRMED、SHIPPED；以 Amazon schema 为准。 |
| locationId | string | 否 | 渠道 location。 |
| marketplaceId | string | 否 | 目标站点。 |
| channelName | string | 否 | 履约渠道。 |
| lastUpdatedAfter | string | 否 | 更新时间下界，ISO 8601。 |
| lastUpdatedBefore | string | 否 | 更新时间上界，ISO 8601。 |
| maxResults | integer | 否 | 1～100；脚本原值透传，不设置默认值。 |
| paginationToken | string | 否 | 上一页 nextToken；脚本不自动翻页。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

本接口除 sellerId、region、skipDepCheck 外的脚本字段全部写入 queryString；paginationToken 接收上一页 nextToken。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| shipments | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| shipmentsRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| queryString | string / null | 实际发出的无 ? 查询串。 |

## 接口：查询单个货件（getShipment）

### 脚本输入与构参

本接口上游方法为 `GET`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

shipmentId 写入路径；本接口不构造 queryString，也不使用列表筛选或分页参数。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| shipment | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| shipmentRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |

## 接口：确认或拒绝货件（processShipment）

### 脚本输入与构参

本接口上游方法为 `POST`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |
| operation | string | 是 | CONFIRM / REJECT；脚本去空白并转大写，写入 queryString。 |
| requestBody | object | 否 | 官方请求体；优先于简化 referenceId / lineItems。 |
| referenceId | string | 否 | 未传 requestBody 时合成 body.referenceId；REJECT 场景可用。 |
| lineItems | object[] | 否 | 未传 requestBody 时合成 body.lineItems；按官方 schema 传退拒明细。 |
| requestBody.referenceId | string | 否 | 官方请求体参考标识。 |
| requestBody.lineItems | object[] | 否 | 官方货件明细；子字段按渠道的 Amazon schema 提供，原值透传。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

operation 写入 queryString；requestBody 优先于 referenceId / lineItems，未提供任何 body 字段时省略 body；传空对象时也省略。REJECT 可按需要传明细。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| processShipment | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| processShipmentRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| queryString | string / null | 实际发出的无 ? 查询串。 |
| requestBody | object / null | 脚本实际组装的请求体。 |

## 接口：创建包裹（createPackages）

### 脚本输入与构参

本接口上游方法为 `POST`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |
| packages | object[] | 二选一 | 与 requestBody 二选一；脚本组装 {packages: [...]}。尺寸、重量与 packageLineItems 按官方 schema。 |
| requestBody | object | 二选一 | 官方完整对象；提供时优先于 packages。 |
| requestBody.packages | object[] | 官方体必需 | 包裹列表，按官方 schema。 |
| packages[].packageLineItems / requestBody.packages[].packageLineItems | object[] | 视渠道 | 包裹货品明细；尺寸、重量和明细子字段按渠道的 Amazon schema 提供，脚本原值透传。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| createPackages | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| createPackagesRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| requestBody | object / null | 脚本实际组装的请求体。 |

## 接口：更新包裹（updatePackage）

### 脚本输入与构参

本接口上游方法为 `PUT`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |
| packageId | string | 是 | 包裹 ID；位于路径或指定查询参数，脚本编码。 |
| requestBody | object | 是 | 官方包裹对象，尺寸、重量、packageLineItems 按官方 schema；原值透传。 |
| requestBody.packageLineItems | object[] | 视渠道 | 包裹货品明细；更深字段以 Amazon schema 为准。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| updatePackage | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| updatePackageRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| requestBody | object / null | 脚本实际组装的请求体。 |

## 接口：更新包裹状态（updatePackageStatus）

### 脚本输入与构参

本接口上游方法为 `PATCH`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |
| packageId | string | 是 | 包裹 ID；位于路径或指定查询参数，脚本编码。 |
| requestBody | object | 二选一 | 与 status 二选一；提供时优先，原值透传。 |
| status | string | 二选一 | 未传 requestBody 时必填，组装 body.status；主要用于 Self Delivery。 |
| subStatus | string | 否 | 未传 requestBody 时可附加子状态。 |
| reason | string | 否 | 未传 requestBody 时可附加原因。 |
| requestBody.status | string | 视官方体 | 包裹状态。 |
| requestBody.subStatus | string | 否 | 包裹子状态。 |
| requestBody.reason | string | 否 | 状态原因。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

主要用于 Self Delivery；requestBody 优先于 status / subStatus / reason，状态枚举及状态机以渠道 schema 为准。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| updatePackageStatus | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| updatePackageStatusRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| requestBody | object / null | 脚本实际组装的请求体。 |

## 接口：查询配送选项（retrieveShippingOptions）

### 脚本输入与构参

本接口上游方法为 `GET`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}/shippingOptions`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |
| packageId | string | 是 | 包裹 ID；位于路径或指定查询参数，脚本编码。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

shipmentId 写入路径，packageId 写入 queryString。Seller Flex 本接口常返回空。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| shippingOptions | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| shippingOptionsRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| queryString | string / null | 实际发出的无 ? 查询串。 |

## 接口：生成发票（generateInvoice）

### 脚本输入与构参

本接口上游方法为 `POST`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

shipmentId 写入路径，无其他脚本请求体。Easy Ship 全球多数站点可能不支持 generateInvoice（印度除外）。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| invoice | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| invoiceRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| invoice.document | object | 返回的发票文档。 |
| invoice.document.format | string | 文档格式。 |
| invoice.document.content | string | Base64 文档内容。 |

## 接口：读取发票（retrieveInvoice）

### 脚本输入与构参

本接口上游方法为 `GET`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

shipmentId 写入路径，无其他脚本请求体。Easy Ship 全球多数站点可能不支持 generateInvoice（印度除外）。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| invoice | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| invoiceRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| invoice.document | object | 返回的发票文档。 |
| invoice.document.format | string | 文档格式。 |
| invoice.document.content | string | Base64 文档内容。 |

## 接口：生成或重新生成面单（generateShipLabels）

### 脚本输入与构参

本接口上游方法为 `PUT`，`path` 为 `externalFulfillment/2024-09-11/shipments/{shipmentId}/shipLabels`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| shipmentId | string | 是 | 外部履约货件 ID；脚本按路径段百分号编码。 |
| operation | string | 是 | GENERATE / REGENERATE；去空白并转大写，写入 queryString。 |
| shippingOptionId | string | 否 | 写入 queryString；脚本按 RFC 3986 百分号编码，空格为 %20、字面加号为 %2B。 |
| requestBody | object | 否 | 官方完整对象，优先于 packageIds / courierSupportedAttributes。 |
| packageIds | string[] | 否 | 未传 requestBody 时组装 body.packageIds；第三方承运等场景使用。 |
| courierSupportedAttributes | object | 否 | 未传 requestBody 时组装 body.courierSupportedAttributes；按渠道 schema 原值透传。 |
| requestBody.packageIds | string[] | 否 | 目标包裹列表。 |
| requestBody.courierSupportedAttributes | object | 否 | 承运商支持的附加属性。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

operation、shippingOptionId 写入 queryString；requestBody 优先于简化字段，未提供任何 body 字段时省略 body，显式空 requestBody 则发送 `{}`。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| shipLabels | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| shipLabelsRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| queryString | string / null | 实际发出的无 ? 查询串。 |
| requestBody | object / null | 脚本实际组装的请求体。 |

## 接口：查询退货列表（listReturns）

### 脚本输入与构参

本接口上游方法为 `GET`，`path` 为 `externalFulfillment/2024-09-11/returns`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| returnLocationId | string | 否 | 退回 location。 |
| rmaId | string | 否 | 退货授权编号。 |
| status | string | 否 | 新退货常用 CREATED，其他值以 Amazon schema 为准。 |
| reverseTrackingId | string | 否 | 逆向物流追踪编号。 |
| createdSince | string | 否 | 创建时间下界。 |
| createdUntil | string | 否 | 创建时间上界。 |
| lastUpdatedSince | string | 否 | 更新时间下界。 |
| lastUpdatedUntil | string | 否 | 更新时间上界。 |
| maxResults | integer | 否 | 分页数量；脚本不设置范围或默认值，按渠道要求传入。 |
| nextToken | string | 否 | 下一页令牌；不自动翻页。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

所有筛选及分页字段写入 queryString，nextToken 接收上一页令牌。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| returns | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| returnsRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
| queryString | string / null | 实际发出的无 ? 查询串。 |

## 接口：查询单个退货（getReturn）

### 脚本输入与构参

本接口上游方法为 `GET`，`path` 为 `externalFulfillment/2024-09-11/returns/{returnId}`。

#### 脚本 JSON 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 已授权卖家 ID。 |
| region | string | 是 | NA / EU / FE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过本地依赖探测，不绕过店铺授权。 |
| returnId | string | 是 | 退货 ID；脚本按路径段百分号编码。 |

#### 脚本选项与运行约定

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --inline | CLI flag | 否 | 强制完整打印，同时落盘。 |
| --no-cache | CLI flag | 否 | 接受兼容选项；所有操作调用 run 时始终传此选项，不读取或写入响应缓存。 |

本地依赖检测返回 0 表示找到 `linkfox-amazon-store-auth`（兼容目录别名 `linkfox-amazon-spapi-auth`）；返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 时先安装依赖，不另行实现授权或令牌逻辑。依赖探测支持环境变量指定目录、常见安装目录及 Hermes 分类 / 插件目录。

脚本 JSON 顶层必须是对象；类型不符时在请求前报错并以退出码 1 结束。

API Key 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。基础地址优先 `LINKFOX_TOOL_GATEWAY`，其次 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`。会话数据保存在当前工作目录；请求前创建会话与 data 目录并验证 data 目录可写，失败则不发起请求；`SESSION_ID` 用于聚合同一任务。无自动重试或自动翻页。

商家必须加入 External Fulfillment allowlist，应用需 Direct-to-Consumer Shipping (Restricted) 角色。实际渠道能力以商家项目权限及 Amazon schema 为准。各渠道均勿混用普通 Orders、Feeds、库存报告或 FBA / MCF 接口。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| developerProxy | object / array / null | 网关完整响应；错误时也保留。 |
| resolvedPath | string | 实际使用的编码后路径。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时为 null。 |
| returnItem | object / array / null | 网关正常且上游状态成功时解析的完整 body；空正文或解析失败为 null；上游失败不输出此业务字段。 |
| returnItemRaw | string | 仅 JSON 解析失败时保留原始 body。 |
| success | boolean | 仅网关正常且上游 httpStatus=204 时为 true，此时业务字段为 null。 |
