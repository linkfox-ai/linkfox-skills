# 脚本输入、构参与本地输出

网关参数与响应定义见 [inbound.md](inbound.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：列出入仓计划（listInboundPlans）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans`
- **当前脚本**：`../../scripts/list_inbound_plans.py`；统一入口 api / operation 取 `listInboundPlans`。

#### Path 参数

无路径占位参数。

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |
| status | string | 否 | 入仓计划状态筛选，按官方模型。 |
| sortBy | string | 否 | 排序字段，按官方模型。 |
| sortOrder | string | 否 | 排序方向，按官方模型。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：创建入仓计划（createInboundPlan）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans`
- **当前脚本**：`../../scripts/create_inbound_plan.py`；统一入口 api / operation 取 `createInboundPlan`。

#### Path 参数

无路径占位参数。

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：获取入仓计划（getInboundPlan）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}`
- **当前脚本**：`../../scripts/get_inbound_plan.py`；统一入口 api / operation 取 `getInboundPlan`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出计划箱件（listInboundPlanBoxes）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes`
- **当前脚本**：`../../scripts/list_inbound_plan_boxes.py`；统一入口 api / operation 取 `listInboundPlanBoxes`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：取消入仓计划（cancelInboundPlan）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`PUT`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation`
- **当前脚本**：`../../scripts/cancel_inbound_plan.py`；统一入口 api / operation 取 `cancelInboundPlan`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出计划商品（listInboundPlanItems）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items`
- **当前脚本**：`../../scripts/list_inbound_plan_items.py`；统一入口 api / operation 取 `listInboundPlanItems`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：更新计划名称（updateInboundPlanName）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`PUT`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name`
- **当前脚本**：`../../scripts/update_inbound_plan_name.py`；统一入口 api / operation 取 `updateInboundPlanName`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出装箱组箱件（listPackingGroupBoxes）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes`
- **当前脚本**：`../../scripts/list_packing_group_boxes.py`；统一入口 api / operation 取 `listPackingGroupBoxes`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| packingGroupId | string | 是 | 装箱组标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出装箱组商品（listPackingGroupItems）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items`
- **当前脚本**：`../../scripts/list_packing_group_items.py`；统一入口 api / operation 取 `listPackingGroupItems`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| packingGroupId | string | 是 | 装箱组标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：设置装箱信息（setPackingInformation）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation`
- **当前脚本**：`../../scripts/set_packing_information.py`；统一入口 api / operation 取 `setPackingInformation`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出装箱选项（listPackingOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions`
- **当前脚本**：`../../scripts/list_packing_options.py`；统一入口 api / operation 取 `listPackingOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：生成装箱选项（generatePackingOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions`
- **当前脚本**：`../../scripts/generate_packing_options.py`；统一入口 api / operation 取 `generatePackingOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：确认装箱选项（confirmPackingOption）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation`
- **当前脚本**：`../../scripts/confirm_packing_option.py`；统一入口 api / operation 取 `confirmPackingOption`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| packingOptionId | string | 是 | 装箱选项标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出计划托盘（listInboundPlanPallets）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets`
- **当前脚本**：`../../scripts/list_inbound_plan_pallets.py`；统一入口 api / operation 取 `listInboundPlanPallets`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出放置选项（listPlacementOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions`
- **当前脚本**：`../../scripts/list_placement_options.py`；统一入口 api / operation 取 `listPlacementOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：生成放置选项（generatePlacementOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions`
- **当前脚本**：`../../scripts/generate_placement_options.py`；统一入口 api / operation 取 `generatePlacementOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：确认放置选项（confirmPlacementOption）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation`
- **当前脚本**：`../../scripts/confirm_placement_option.py`；统一入口 api / operation 取 `confirmPlacementOption`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| placementOptionId | string | 是 | 放置选项标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：获取现行入仓货件（getShipment）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}`
- **当前脚本**：`../../scripts/get_inbound_shipment.py`；统一入口 api / operation 取 `getShipment`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出货件箱件（listShipmentBoxes）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes`
- **当前脚本**：`../../scripts/list_shipment_boxes.py`；统一入口 api / operation 取 `listShipmentBoxes`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出货件内容更新预览（listShipmentContentUpdatePreviews）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews`
- **当前脚本**：`../../scripts/list_shipment_content_update_previews.py`；统一入口 api / operation 取 `listShipmentContentUpdatePreviews`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：生成货件内容更新预览（generateShipmentContentUpdatePreviews）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews`
- **当前脚本**：`../../scripts/generate_shipment_content_update_previews.py`；统一入口 api / operation 取 `generateShipmentContentUpdatePreviews`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：获取货件内容更新预览（getShipmentContentUpdatePreview）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}`
- **当前脚本**：`../../scripts/get_shipment_content_update_preview.py`；统一入口 api / operation 取 `getShipmentContentUpdatePreview`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |
| contentUpdatePreviewId | string | 是 | 货件内容更新预览标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：确认货件内容更新预览（confirmShipmentContentUpdatePreview）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation`
- **当前脚本**：`../../scripts/confirm_shipment_content_update_preview.py`；统一入口 api / operation 取 `confirmShipmentContentUpdatePreview`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |
| contentUpdatePreviewId | string | 是 | 货件内容更新预览标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：获取交货单文档（getDeliveryChallanDocument）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument`
- **当前脚本**：`../../scripts/get_delivery_challan_document.py`；统一入口 api / operation 取 `getDeliveryChallanDocument`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出送达窗口选项（listDeliveryWindowOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions`
- **当前脚本**：`../../scripts/list_delivery_window_options.py`；统一入口 api / operation 取 `listDeliveryWindowOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：生成送达窗口选项（generateDeliveryWindowOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions`
- **当前脚本**：`../../scripts/generate_delivery_window_options.py`；统一入口 api / operation 取 `generateDeliveryWindowOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：确认送达窗口选项（confirmDeliveryWindowOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation`
- **当前脚本**：`../../scripts/confirm_delivery_window_options.py`；统一入口 api / operation 取 `confirmDeliveryWindowOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |
| deliveryWindowOptionId | string | 是 | 送达窗口选项标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出现行货件商品（listShipmentItems）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items`
- **当前脚本**：`../../scripts/list_shipment_items.py`；统一入口 api / operation 取 `listShipmentItems`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：更新货件名称（updateShipmentName）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`PUT`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name`
- **当前脚本**：`../../scripts/update_shipment_name.py`；统一入口 api / operation 取 `updateShipmentName`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出货件托盘（listShipmentPallets）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets`
- **当前脚本**：`../../scripts/list_shipment_pallets.py`；统一入口 api / operation 取 `listShipmentPallets`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：取消自配送预约（cancelSelfShipAppointment）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`PUT`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation`
- **当前脚本**：`../../scripts/cancel_self_ship_appointment.py`；统一入口 api / operation 取 `cancelSelfShipAppointment`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：获取自配送预约时段（getSelfShipAppointmentSlots）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots`
- **当前脚本**：`../../scripts/get_self_ship_appointment_slots.py`；统一入口 api / operation 取 `getSelfShipAppointmentSlots`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：生成自配送预约时段（generateSelfShipAppointmentSlots）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots`
- **当前脚本**：`../../scripts/generate_self_ship_appointment_slots.py`；统一入口 api / operation 取 `generateSelfShipAppointmentSlots`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：安排自配送预约（scheduleSelfShipAppointment）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule`
- **当前脚本**：`../../scripts/schedule_self_ship_appointment.py`；统一入口 api / operation 取 `scheduleSelfShipAppointment`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |
| slotId | string | 是 | 自配送预约时段标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：更新货件发货地址（updateShipmentSourceAddress）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`PUT`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress`
- **当前脚本**：`../../scripts/update_shipment_source_address.py`；统一入口 api / operation 取 `updateShipmentSourceAddress`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：更新货件跟踪信息（updateShipmentTrackingDetails）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`PUT`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails`
- **当前脚本**：`../../scripts/update_shipment_tracking_details.py`；统一入口 api / operation 取 `updateShipmentTrackingDetails`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |
| shipmentId | string | 是 | 货件标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出运输选项（listTransportationOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions`
- **当前脚本**：`../../scripts/list_transportation_options.py`；统一入口 api / operation 取 `listTransportationOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| pageSize | integer | 否 | 每页条数；脚本不设置默认值或取值范围，须符合本节链接的官方定义。 |
| paginationToken | string | 否 | 现行入仓的分页令牌，不自动翻页。 |
| placementOptionId | string | 否 | 放置选项标识。 |
| shipmentId | string | 否 | 货件标识。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：生成运输选项（generateTransportationOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions`
- **当前脚本**：`../../scripts/generate_transportation_options.py`；统一入口 api / operation 取 `generateTransportationOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：确认运输选项（confirmTransportationOptions）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation`
- **当前脚本**：`../../scripts/confirm_transportation_options.py`；统一入口 api / operation 取 `confirmTransportationOptions`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| inboundPlanId | string | 是 | 入仓计划标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出商品合规信息（listItemComplianceDetails）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/items/compliance`
- **当前脚本**：`../../scripts/list_item_compliance_details.py`；统一入口 api / operation 取 `listItemComplianceDetails`。

#### Path 参数

无路径占位参数。

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点标识；保持单数键名。 |
| mskus | string / array[string] | 否 | 商家 SKU 列表；字段名为 mskus，数组生成重复键。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：更新商品合规信息（updateItemComplianceDetails）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`PUT`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/items/compliance`
- **当前脚本**：`../../scripts/update_item_compliance_details.py`；统一入口 api / operation 取 `updateItemComplianceDetails`。

#### Path 参数

无路径占位参数。

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点标识；保持单数键名。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：创建站点商品标签（createMarketplaceItemLabels）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/items/labels`
- **当前脚本**：`../../scripts/create_marketplace_item_labels.py`；统一入口 api / operation 取 `createMarketplaceItemLabels`。

#### Path 参数

无路径占位参数。

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：列出商品预处理信息（listPrepDetails）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/items/prepDetails`
- **当前脚本**：`../../scripts/list_prep_details.py`；统一入口 api / operation 取 `listPrepDetails`。

#### Path 参数

无路径占位参数。

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| marketplaceId | string | 是 | 目标站点标识；保持单数键名。 |
| mskus | string / array[string] | 是 | 商家 SKU 列表；字段名为 mskus，数组生成重复键。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：设置商品预处理信息（setPrepDetails）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`POST`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/items/prepDetails`
- **当前脚本**：`../../scripts/set_prep_details.py`；统一入口 api / operation 取 `setPrepDetails`。

#### Path 参数

无路径占位参数。

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 按官方业务模型 | 本操作启用 body，嵌套字段须符合本节链接的官方接口模型，不以空对象示例代替完整业务数据；显式 requestBody 优先，否则按平铺字段组装。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |

## 接口：查询入仓异步操作状态（getInboundOperationStatus）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`inbound/fba/2024-03-20/operations/{operationId}`
- **当前脚本**：`../../scripts/get_inbound_operation_status.py`；统一入口 api / operation 取 `getInboundOperationStatus`。

#### Path 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| operationId | string | 是 | 异步操作标识。分段 URL 编码后写入 path。 |

#### Query 参数

本操作未声明同级查询字段；仍可通过 query 或 queryString 透传上游允许的字段。

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |
