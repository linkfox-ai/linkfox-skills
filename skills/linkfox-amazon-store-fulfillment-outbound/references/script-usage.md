# 脚本输入、构参与本地输出

网关参数与响应定义见 [api.md](api.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：预览履约订单（getOrderPreview）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| requestBody | object | 是（或兼容平铺字段） | 见下表；也可兼容将业务体字段平铺到顶层，控制、路径及查询字段不会进入请求体。两种形式同时提供时仅使用 requestBody。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- 数组至少一项；India 货到付款及 line-item payment-on-delivery 字段仅在当前支持的 India 业务使用。跨境确认起运国、目的国和 perUnitDeclaredValue，以预览限制为准；Japan 预约配送和投递偏好、Unbranded / SIPP / Block AMZL 配置先确认可用性。未细分结构按上游实际契约传递，不增造字段。

#### Amazon 请求体（脚本 requestBody → 网关 body）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| destination | object | 是 | 配送目的地。 |
| destination.deliveryAddress | object | 是 | 收货地址。 |
| destination.deliveryAddress.name | string | 是 | 收件人，非空。 |
| destination.deliveryAddress.addressLine1 | string | 是 | 地址第一行，非空。 |
| destination.deliveryAddress.postalCode | string | 是 | 邮编，非空。 |
| destination.deliveryAddress.countryCode | string | 是 | 两位大写国家代码，匹配 [A-Z]{2}。 |
| destination.dropOffLocation | object | 否 | Japan 等受支持地区的投递偏好。 |
| destination.dropOffLocation.type | string | 否 | neighbor、delivery box、locker 等语义；完整枚举未列明，不自行猜测。 |
| destination.dropOffLocation.attributes | object；未细分 | 否 | 仅使用用户明确提供、当地支持的 attributes。 |
| lineItems | array<object> | 是 | 至少一项。 |
| lineItems[].product | object | 是 | 商品。 |
| lineItems[].product.productIdentifier | object | 是 | 商品标识。 |
| lineItems[].product.productIdentifier.amazonSku | string | 是 | 非空 Amazon SKU。 |
| lineItems[].amount | object | 是 | 数量。 |
| lineItems[].amount.value | string | 是 | 非空十进制数量字符串，不传 number。 |
| lineItems[].amount.unit | string | 否 | 提供时必须为 EACHES。 |
| lineItems[].perUnitDeclaredValue | 未细分 | 否 | 跨境单位申报价值，先核对 preview constraints。 |
| origin | object | 否 | 起运信息；提供时必须包含 countryCode（预览和报价本地校验）。 |
| origin.countryCode | string | 随 origin 必填 | 两位大写国家代码。 |
| fulfillmentConfiguration | object | 否 | 履约配置，以 preview/offers 返回的可用配置为准。 |
| fulfillmentConfiguration.action | string | 否 | 常见为 SHIP 或 HOLD；释放 HOLD 前确认。 |
| fulfillmentConfiguration.policy | string | 否 | FILL_OR_KILL / FILL_ALL / FILL_ALL_AVAILABLE。 |
| fulfillmentConfiguration.serviceLevel | object | 否 | 配送服务等级配置。 |
| fulfillmentConfiguration.serviceLevel.deliveryInterval | 未细分 | 否 | Japan 预约配送/时段先预览确认。 |
| fulfillmentConfiguration.services | object | 否 | 附加履约服务。 |
| fulfillmentConfiguration.services.packaging | 未细分 | 否 | Unbranded、SIPP 等包装配置，原样使用已确认且可用的配置。 |
| fulfillmentConfiguration.services.additional | 未细分 | 否 | Block AMZL 等附加配置，不猜测区域可用值。 |
| channel | 未细分 | 否 | 渠道信息。 |
| excludeEstimatedFees | boolean | 否 | 是否排除预估费用；脚本不设默认值。 |
| includePaymentOnDelivery | boolean | 否 | 是否包含货到付款；脚本不设默认值。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 getOrderPreview。 |
| method | string | 固定上游 POST。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| requestBody | object | 经校验的业务请求体。 |
| orderPreview | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |



#### 业务结果使用

必填 body：

- `destination.deliveryAddress`：地址至少包含 `name`、`addressLine1`、`postalCode`、两位大写 `countryCode`。
- `lineItems[]`：每项包含 `product.productIdentifier.amazonSku` 和 `amount.value`；`amount.unit` 如提供应为 `EACHES`。

可选：`channel`、`fulfillmentConfiguration`、`origin`、`excludeEstimatedFees`、`includePaymentOnDelivery`。响应关键字段：`plannedShipments[]`、`constraints[]`。

## 接口：获取配送报价（getOffers）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| requestBody | object | 是（或兼容平铺字段） | 见下表；也可兼容将业务体字段平铺到顶层，控制、路径及查询字段不会进入请求体。两种形式同时提供时仅使用 requestBody。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- 数组至少一项；India 货到付款及 line-item payment-on-delivery 字段仅在当前支持的 India 业务使用。跨境确认起运国、目的国和 perUnitDeclaredValue，以预览限制为准；Japan 预约配送和投递偏好、Unbranded / SIPP / Block AMZL 配置先确认可用性。未细分结构按上游实际契约传递，不增造字段。

#### Amazon 请求体（脚本 requestBody → 网关 body）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| origin | object | 是 | 起运信息。 |
| origin.countryCode | string | 是 | 两位大写国家代码。 |
| items | array<object> | 是 | 至少一项。 |
| items[].productIdentifier | object | 是（本地要求） | Amazon OfferItem schema 未标为 required，本技能仍要求 SKU，避免无效请求。 |
| items[].productIdentifier.amazonSku | string | 是（本地要求） | 非空 Amazon SKU。 |
| destination | object | 否 | 目的地；报价目的地子字段按实际契约传递。 |
| fulfillmentConfiguration | object | 否 | 履约配置，以 preview/offers 返回的可用配置为准。 |
| fulfillmentConfiguration.action | string | 否 | 常见为 SHIP 或 HOLD；释放 HOLD 前确认。 |
| fulfillmentConfiguration.policy | string | 否 | FILL_OR_KILL / FILL_ALL / FILL_ALL_AVAILABLE。 |
| fulfillmentConfiguration.serviceLevel | object | 否 | 配送服务等级配置。 |
| fulfillmentConfiguration.serviceLevel.deliveryInterval | 未细分 | 否 | Japan 预约配送/时段先预览确认。 |
| fulfillmentConfiguration.services | object | 否 | 附加履约服务。 |
| fulfillmentConfiguration.services.packaging | 未细分 | 否 | Unbranded、SIPP 等包装配置，原样使用已确认且可用的配置。 |
| fulfillmentConfiguration.services.additional | 未细分 | 否 | Block AMZL 等附加配置，不猜测区域可用值。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 getOffers。 |
| method | string | 固定上游 POST。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| requestBody | object | 经校验的业务请求体。 |
| offers | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |



#### 业务结果使用

必填 body：

- `origin.countryCode`
- `items[].productIdentifier.amazonSku`

Amazon 当前 schema 没有将 `OfferItem.productIdentifier` 标为 required，但空 item 无法定位 SKU；本技能为避免无效请求，在本地要求每个 item 提供 `productIdentifier.amazonSku`。预览、创建和报价的数组也要求至少一项。

可选 `destination` 和 `fulfillmentConfiguration`。响应关键字段为 `offerResults[]`，每项包含输入 item、`offers[]`、可能的 `constraints[]`。

## 接口：创建履约订单（createOrder）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| requestBody | object | 是（或兼容平铺字段） | 见下表；也可兼容将业务体字段平铺到顶层，控制、路径及查询字段不会进入请求体。两种形式同时提供时仅使用 requestBody。 |
| confirmWrite | boolean | 是 | 取得明确确认后必须为布尔 true，字符串或数字不能代替；仅本地控制，不转发。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- 数组至少一项；India 货到付款及 line-item payment-on-delivery 字段仅在当前支持的 India 业务使用。跨境确认起运国、目的国和 perUnitDeclaredValue，以预览限制为准；Japan 预约配送和投递偏好、Unbranded / SIPP / Block AMZL 配置先确认可用性。未细分结构按上游实际契约传递，不增造字段。

#### Amazon 请求体（脚本 requestBody → 网关 body）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| orderId | string | 是 | 卖家生成的唯一非空订单标识；不确定结果时不得另造标识重试。 |
| destination | object | 是 | 配送目的地。 |
| destination.deliveryAddress | object | 是 | 收货地址。 |
| destination.deliveryAddress.name | string | 是 | 收件人，非空。 |
| destination.deliveryAddress.addressLine1 | string | 是 | 地址第一行，非空。 |
| destination.deliveryAddress.postalCode | string | 是 | 邮编，非空。 |
| destination.deliveryAddress.countryCode | string | 是 | 两位大写国家代码，匹配 [A-Z]{2}。 |
| destination.dropOffLocation | object | 否 | Japan 等受支持地区的投递偏好。 |
| destination.dropOffLocation.type | string | 否 | neighbor、delivery box、locker 等语义；完整枚举未列明，不自行猜测。 |
| destination.dropOffLocation.attributes | object；未细分 | 否 | 仅使用用户明确提供、当地支持的 attributes。 |
| lineItems | array<object> | 是 | 至少一项。 |
| lineItems[].product | object | 是 | 商品。 |
| lineItems[].product.productIdentifier | object | 是 | 商品标识。 |
| lineItems[].product.productIdentifier.amazonSku | string | 是 | 非空 Amazon SKU。 |
| lineItems[].amount | object | 是 | 数量。 |
| lineItems[].amount.value | string | 是 | 非空十进制数量字符串，不传 number。 |
| lineItems[].amount.unit | string | 否 | 提供时必须为 EACHES。 |
| lineItems[].perUnitDeclaredValue | 未细分 | 否 | 跨境单位申报价值，先核对 preview constraints。 |
| lineItems[].lineItemId | string | 是 | 卖家控制的非空行标识，同一订单内唯一。 |
| channel | 未细分 | 否 | 渠道信息。 |
| origin | object | 否 | 起运信息。 |
| origin.countryCode | string | 随业务需要 | 起运国家，跨境时与目的国、申报价值一起展示确认。 |
| paymentInformation | object | 否 | 仅用于 Amazon India 当前支持的货到付款业务；未细分。 |
| fulfillmentConfiguration | object | 否 | 履约配置，以 preview/offers 返回的可用配置为准。 |
| fulfillmentConfiguration.action | string | 否 | 常见为 SHIP 或 HOLD；释放 HOLD 前确认。 |
| fulfillmentConfiguration.policy | string | 否 | FILL_OR_KILL / FILL_ALL / FILL_ALL_AVAILABLE。 |
| fulfillmentConfiguration.serviceLevel | object | 否 | 配送服务等级配置。 |
| fulfillmentConfiguration.serviceLevel.deliveryInterval | 未细分 | 否 | Japan 预约配送/时段先预览确认。 |
| fulfillmentConfiguration.services | object | 否 | 附加履约服务。 |
| fulfillmentConfiguration.services.packaging | 未细分 | 否 | Unbranded、SIPP 等包装配置，原样使用已确认且可用的配置。 |
| fulfillmentConfiguration.services.additional | 未细分 | 否 | Block AMZL 等附加配置，不猜测区域可用值。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 createOrder。 |
| method | string | 固定上游 POST。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| requestBody | object | 经校验的业务请求体。 |
| orderCreation | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |
| nextAction | object | 上游 202 且存在原订单标识时提供；不自动查询。 |
| nextAction.script | string | 固定 get_order.py。 |
| nextAction.params | object | sellerId、region、orderId；有 fulfillmentServiceId 时一并保留。 |
| nextAction.automaticPolling | boolean | 固定 false。 |



#### 业务结果使用

必填 body：

- `orderId`：卖家生成的唯一订单标识。
- `destination.deliveryAddress`
- `lineItems[]`：每项包含唯一 `lineItemId`、`product.productIdentifier.amazonSku`、`amount.value`。

可选：`channel`、`origin`、`fulfillmentConfiguration`、`paymentInformation`。`fulfillmentConfiguration.action` 常见为 `SHIP` 或 `HOLD`；policy 可为 `FILL_OR_KILL`、`FILL_ALL`、`FILL_ALL_AVAILABLE`。

HTTP 200 返回 `order`；HTTP 202 返回至少 `orderId` 和 `status`。202 后通过 `getOrder` 恢复状态。

## 接口：列出履约订单（listOrders）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| updatedAfter | string | 否 | 更新时间下界，ISO 8601 date-time；支持 Z 或显式 UTC 偏移。 |
| pageToken | string | 否 | 上一页 pagination.nextToken；不自动翻页。 |
| shipments | string | 否 | INCLUDE / EXCLUDE；脚本不设默认，忽略大小写输入并规范化为枚举；仅需要包裹与跟踪明细时使用 INCLUDE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- 本操作不接受 requestBody。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 listOrders。 |
| method | string | 固定上游 GET。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| queryString | string | 有值时记录实际查询串。 |
| orders | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |



#### 业务结果使用

query 参数：

- `updatedAfter`：ISO 8601 date-time。
- `pageToken`：从上一页 `pagination.nextToken` 获取。
- `shipments`：`INCLUDE` / `EXCLUDE`。

响应关键字段：`orders[]`、`pagination.nextToken`。脚本不自动翻页。

## 接口：查询履约订单（getOrder）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| orderId | string | 是 | 去空白后 1–40 字符，按 URL path 分段编码。 |
| shipments | string | 否 | INCLUDE / EXCLUDE；脚本不设默认，忽略大小写输入并规范化为枚举；需要包裹与跟踪明细时使用 INCLUDE。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- 本操作不接受 requestBody；通过 orderId 定位订单，按需传 shipments: "INCLUDE" 获取包裹与跟踪明细。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 getOrder。 |
| method | string | 固定上游 GET。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| queryString | string | 有值时记录实际查询串。 |
| order | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |



#### 业务结果使用

- path：`orderId`，1–40 字符。
- query：可选 `shipments=INCLUDE|EXCLUDE`。
- 响应：`order`；包含状态、配置、地址、line items，选择 INCLUDE 时可包含 shipments、packages 与 tracking。

`getOrder` 的当前响应模型已承载多个旧版独立查询场景，不需要在 v2026 路径上虚构额外 operation：

- `shipments[].packages[].tracking.carrier|amazon`：承运商/Amazon 的 `trackingNumber` 和 `trackingUrl`；
- `tracking.proofOfDelivery.deliveryPhotoUrl|receivedBy`：投递照片或签收人；
- `tracking.dropOffLocation`：包括日本 locker/delivery box 等投放位置；
- `shipments[].items[].unitIdentifiers`：商品实例/序列号标识；
- 多个 `shipments` / `packages` 以及 line item 的 `cancelledAmount` / `unfulfillableAmount`：用于拆包和部分履约状态；按 `shipmentItemIds` 将 package 与 shipment item 对应，分别展示 shipment/package status。

这些字段均由 wrapper 保留在完整响应中；仅在用户需要包裹/跟踪明细时传 `shipments: "INCLUDE"`。

## 接口：更新履约订单（updateOrder）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| orderId | string | 是 | 去空白后 1–40 字符，按 URL path 分段编码。 |
| requestBody | object | 是（或兼容平铺字段） | 见下表；也可兼容将业务体字段平铺到顶层，控制、路径及查询字段不会进入请求体。两种形式同时提供时仅使用 requestBody。 |
| confirmWrite | boolean | 是 | 取得明确确认后必须为布尔 true，字符串或数字不能代替；仅本地控制，不转发。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。

#### Amazon 请求体（脚本 requestBody → 网关 body）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fulfillmentConfiguration | object | 否 | 当前模型仅支持 action 更新；脚本兼容空 requestBody。 |
| fulfillmentConfiguration.action | string | 否 | SHIP / HOLD；通常用 SHIP 释放暂存订单。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 updateOrder。 |
| method | string | 固定上游 PUT。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| requestBody | object | 经校验的业务请求体。 |
| orderUpdate | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |
| nextAction | object | 上游 202 且存在原订单标识时提供；不自动查询。 |
| nextAction.script | string | 固定 get_order.py。 |
| nextAction.params | object | sellerId、region、orderId；有 fulfillmentServiceId 时一并保留。 |
| nextAction.automaticPolling | boolean | 固定 false。 |

成功响应体按实际返回值处理，不补造结果对象或未列明的细分字段。



#### 业务结果使用

- path：`orderId`。
- body：`fulfillmentConfiguration`；当前模型只允许更新 action。通常用 `{"fulfillmentConfiguration":{"action":"SHIP"}}` 释放 HOLD。
- HTTP 202 表示已接受，不代表更新完成；后续用 `getOrder` 核实。

## 接口：取消履约订单（cancelOrder）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| orderId | string | 是 | 去空白后 1–40 字符，按 URL path 分段编码。 |
| confirmWrite | boolean | 是 | 取得明确确认后必须为布尔 true，字符串或数字不能代替；仅本地控制，不转发。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- 本操作不接受 requestBody。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 cancelOrder。 |
| method | string | 固定上游 PUT。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| orderCancellation | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |
| nextAction | object | 上游 202 且存在原订单标识时提供；不自动查询。 |
| nextAction.script | string | 固定 get_order.py。 |
| nextAction.params | object | sellerId、region、orderId；有 fulfillmentServiceId 时一并保留。 |
| nextAction.automaticPolling | boolean | 固定 false。 |

成功响应体按实际返回值处理，不补造结果对象或未列明的细分字段。



#### 业务结果使用

- path：`orderId`。
- 无 request body。
- HTTP 202 表示取消请求已接受；后续用 `getOrder` 核实最终状态。

## 接口：模拟订单状态（updateOrderStatus）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| orderId | string | 是 | 去空白后 1–40 字符，按 URL path 分段编码。 |
| requestBody | object | 是（或兼容平铺字段） | 见下表；也可兼容将业务体字段平铺到顶层，控制、路径及查询字段不会进入请求体。两种形式同时提供时仅使用 requestBody。 |
| confirmWrite | boolean | 是 | 取得明确确认后必须为布尔 true，字符串或数字不能代替；仅本地控制，不转发。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- Amazon 标记 x-amzn-api-sandbox-only: true，只能用于动态沙箱测试数据；使用标准 developerProxy 请求，不接受或发送独立 sandbox 控制字段，不要求技能专属 sandbox 配置。可用性由统一网关及上游路由决定。

#### Amazon 请求体（脚本 requestBody → 网关 body）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| status | string | 是 | PROCESSING / COMPLETE / COMPLETE_PARTIAL / CANCELLED / UNFULFILLABLE / INVALID。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 updateOrderStatus。 |
| method | string | 固定上游 PUT。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| requestBody | object | 经校验的业务请求体。 |
| statusUpdate | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |

成功响应体按实际返回值处理，不补造结果对象或未列明的细分字段。

## 接口：模拟包裹状态（updatePackage）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| fulfillmentServiceId | string | 否 | 可选多租户服务标识，按网关字段约定校验，不放入 query/body。 |
| orderId | string | 是 | 去空白后 1–40 字符，按 URL path 分段编码。 |
| packageId | string | 是 | 非空包裹标识，按 URL path 分段编码；脚本不设独立长度上限。 |
| requestBody | object | 是（或兼容平铺字段） | 见下表；也可兼容将业务体字段平铺到顶层，控制、路径及查询字段不会进入请求体。两种形式同时提供时仅使用 requestBody。 |
| confirmWrite | boolean | 是 | 取得明确确认后必须为布尔 true，字符串或数字不能代替；仅本地控制，不转发。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- Amazon 标记 x-amzn-api-sandbox-only: true，只能用于动态沙箱测试数据；使用标准 developerProxy 请求，不接受或发送独立 sandbox 控制字段，不要求技能专属 sandbox 配置。可用性由统一网关及上游路由决定。
- 路径直接结束于 {packageId}，不得追加 /status。

#### Amazon 请求体（脚本 requestBody → 网关 body）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| status | string | 是 | PROCESSING / IN_TRANSIT / DELAYED / OUT_FOR_DELIVERY / DELIVERED / UNDELIVERABLE / EXPIRED。 |
| deliveryTime | string；格式未限定 | 否 | 投递时间，校验器不额外限制格式。 |
| tracking | object | 否 | 跟踪信息。 |
| tracking.carrier | object | 否 | 承运商信息。 |
| tracking.carrier.carrierCode | string | 提供 carrier 时必填 | 非空承运商代码。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 updatePackage。 |
| method | string | 固定上游 PUT。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| requestBody | object | 经校验的业务请求体。 |
| packageUpdate | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |

成功响应体按实际返回值处理，不补造结果对象或未列明的细分字段。

## 接口：查询发票头（getInvoiceHeaders）

### 脚本输入与构参

#### 脚本 JSON 参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 目标店铺。 |
| region | string | 是 | NA / EU / FE。 |
| marketplaceId | string | 是 | 目标站点，必填非空字符串。 |
| nextToken | string | 否 | 发票分页令牌；Amazon 可能返回空页，不自动翻页。 |
| fromIssueDate | string | 否 | 开票时间下界，ISO 8601 date-time；与 toIssueDate 同时提供或同时省略。 |
| toIssueDate | string | 否 | 开票时间上界，ISO 8601 date-time；不得早于起点，区间不得超过 90 天。 |
| invoicesModifiedAfter | string | 否 | 可选增量同步时间，ISO 8601 date-time。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 读/预览操作强制刷新，不读取或写入业务缓存；写操作始终不缓存。 |

#### 参数约束与运行约定

- 固定操作脚本不接受顶层 body、contentType、method、path、queryString、sandbox 覆盖（大小写不敏感）。不接收原始店铺令牌；店铺令牌由服务端根据 sellerId + region 解析和刷新。
- 认证密钥优先 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关优先 LINKFOX_TOOL_GATEWAY，其次 STORE_API_BASE_URL、SPAPI_BASE_URL，最终回退 https://tool-gateway.linkfox.com。请求同时透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。
- `check_auth_dependency.py` 返回 0 表示找到认证技能；42 与 stderr 的 DEPENDENCY_MISSING: 表示需先安装或加载 linkfox-amazon-store-auth。兼容认证技能目录 linkfox-amazon-spapi-auth、OpenClaw、Hermes 及现有环境变量安装路径；不得从本技能绕过认证依赖调用授权或令牌接口。
- 路径占位符分别 URL 编码，最终 path 最多 2048 字符；查询字符串按上表固定键生成，不自动翻页。未注明默认值的字段不补默认；非空查询值需符合类型与格式。
- 保留成功读/预览的 24 小时本地缓存，按操作、参数和 SESSION_ID 隔离；skipDepCheck 不进入缓存键。生产写入成功后清除当前会话业务缓存，写操作自身不缓存；沙箱操作不清理生产读缓存。公共 run 始终传 --no-cache，避免第二层响应缓存。
- 完整响应与元数据仅保存在当前可写工作目录的 linkfox 下，不写 /tmp，不回退家目录；请求前探测可写性。落盘会话名经过净化并在有变化时加哈希后缀，不改写请求头中的 SESSION_ID；缺少 SESSION_ID 时生成进程内稳定落盘会话名。大响应默认摘要，--inline 全量打印。
- LinkFox 鉴权/计费问题按 [onboarding.md](onboarding.md)；Amazon 授权问题核对店铺、区域和角色。路径白名单或模块未开放时确认当前部署，不改成旧版路径掩盖问题。
- 本操作不支持 fulfillmentServiceId，也不接受 requestBody；开票日期必须成对提供、终点不早于起点、范围不超过 90 天。

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| operationId | string | 固定 getInvoiceHeaders。 |
| method | string | 固定上游 GET。 |
| resolvedPath | string | URL 编码后的实际相对路径。 |
| developerProxy | object | 完整网关响应，含错误消息。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接或 JSON 解析失败时为 null；缓存记录未保存该字段时可能缺失。 |
| queryString | string | 有值时记录实际查询串。 |
| invoiceHeaders | object / array / scalar / string / null | 仅网关正常且上游状态在本接口成功集合时提供；是完整解析后的 body，不额外解包同名字段；无响应体为 null。 |


#### 业务结果使用

从实际返回的 `invoices[]`、`numOfRecords` 和 `nextToken` 展示发票头、记录数与后续分页情况；仅展示已有字段。空页也可能带 `nextToken`，不自动翻页。
