# 更新发货/重试购标 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：更新发货/重试购标（bg.logistics.shipment.update）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=bg.logistics.shipment.update`；**对应脚本**：`scripts/us_buy_shipping_logistics_shipment_update.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=43a8da366d5847b9a7faf13915ce57d6

### 请求参数

#### 网关与脚本参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是；美国站脚本默认 | `us`；通用脚本支持 `cn`、`partner`、`us`、`global`、`eu`，本技能业务使用美国站。 |
| managementType | string | 是；美国站脚本默认 | `semi-managed`；通用脚本还兼容 `full-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；显式传入时优先于本地存储。 |
| storeKey | string | 与 accessToken 二选一 | 脚本按店铺、站点、托管类型和用途从本地令牌库读取，不发送给网关。 |
| tokenPurpose | string | 否 | 美国站脚本本地选令牌默认 `order-shipping`；通用脚本默认 `default`。此字段不进入实际网关 Body。 |
| type | string | 是；专用脚本固定 | 本节列出的 Temu 操作标识；上游路径为 `https://openapi-b-us.temu.com/openapi/router`，通过 type 区分操作，没有 developerProxy.path 字段。 |
| params | object | 否 | 业务参数；有显式对象时原样转发，否则美国站脚本将非保留顶层字段收集为 params。 |
| params.request | OBJECT | 否（Partner 表） | 本接口业务对象；子字段必填与实际使用要求见下文，不因外层选填而省略必要内容。专用脚本也接受顶层 request 并收进 params。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 密钥兼容别名，按列出顺序优先于环境变量；只用于请求头，不进入业务参数。 |
| --inline | CLI flag | 否 | 完整打印并保存响应。 |
| --no-cache | CLI flag | 否 | 保留可传选项；业务封装内部始终禁用缓存，既不读也不写响应缓存。 |

美国站默认值、兼容认证头、参数提取和输出约定详见 [运行约定](../api.md#运行约定)。以下 Partner 字段表的路径均相对于 `params.request`；响应子表路径相对于解析后的 Temu 对象。

#### 业务说明与前置限制

> **典型场景：**
> 1. 仅更新 **`shipLaterLimitTime`**（须由 **`bg.logistics.shipment.create`** 且 **`shipLater=true`** 创建）。
> 2. **`retrySendPackageRequestList`**：对 **失败状态** 的包裹（`packageSn`）调整仓库/尺寸重量/渠道后重试购标。
> **前置：** `packageSn` 来自 **`bg.logistics.shipment.result.get`**；渠道参数来自 **`bg.logistics.shippingservices.get`**。

（卖家延后创建物流单，或在购标/下单失败后对包裹重新在线下单。）

#### `request` 内字段

> Partner **Request** 表将 **`request`**、**`retrySendPackageRequestList`**、**`shipLaterLimitTime`** 均标为选填（False）；下列说明列内容来自 Partner 导出页 **Required** 列（该页将长说明写在 Required 列而非 Description 列）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| retrySendPackageRequestList | OBJECT[] | 否 | retry Package List Information（失败包裹重试列表；每项对应一个待重试的 **`packageSn`** 及新的物流/尺寸参数） |
| shipLaterLimitTime | STRING | 否 | **Usage Rules:** shipLaterLimitTime can be updated only if the order was created with **shipLater=true** via **`bg.logistics.shipment.create`**. **Available Options by Order Label:** For orders **without** the **`Y2_advance_sale`** label, available options are: **24, 48, 72, 96, 120** hours. For orders **with** the **`Y2_advance_sale`** label, available options are: **144, 168, 192, 216, 240, 264, 288, 312, 336, 360** hours.（仅 **`shipLater=true`** 创建的订单可更新；无效值见错误码 **`120015532`**、**`120018078`**） |

##### `shipLaterLimitTime` 可选值（Partner）

| 订单标签 | 可选小时（字符串） |
|----------|-------------------|
| 无 **`Y2_advance_sale`** 标签 | `24`、`48`、`72`、`96`、`120` |
| 有 **`Y2_advance_sale`** 标签 | `144`、`168`、`192`、`216`、`240`、`264`、`288`、`312`、`336`、`360` |

> 与 **`bg.logistics.shipment.create`** 入参 **`shipLaterLimitTime`** 规则一致；无效值见错误码 `120015532`。

##### `retrySendPackageRequestList[]` 元素字段

> Partner Request 表中 `retrySendPackageRequestList` 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **Request Example**，说明结合 Partner 错误码、**`bg.logistics.shipment.create`** 的 **`sendRequestList[]`** 同名字段及 Buy-Shipping 流程整理。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSn | STRING | **是**（重试时） | Package SN（包裹号；须为 **购标失败** 状态的包裹，见错误码 `120018002`、`120018027`） |
| splitSubPackage | BOOLEAN | 否 | 是否拆分子包裹发货。为 **true** 时 **`orderSendInfoList[].quantity`** 须为 **1**（`120011045`）；跨国拆包等限制见错误码 `120012029`、`120018084` |
| warehouseId | STRING | **是**（重试时） | Warehouse ID（发货仓库；来自 **`bg.logistics.warehouse.list.get`**，错误码 `120011006`） |
| weight | STRING | **是**（重试时） | 包裹重量。美国本地订单填**整数**（lb），小数用 **`extendWeight`**（oz）；非美国本地默认两位小数（`120015521`） |
| weightUnit | STRING | **是**（重试时） | 重量单位：美国 **`lb`**，其他 **`kg`** |
| extendWeight | STRING | 否 | 扩展重量（美国本地 oz 部分） |
| extendWeightUnit | STRING | 否 | 扩展重量单位：美国本地 **`oz`** |
| length | STRING | **是**（重试时） | 长度（两位小数） |
| width | STRING | **是**（重试时） | 宽度（两位小数） |
| height | STRING | **是**（重试时） | 高度（两位小数） |
| dimensionUnit | STRING | **是**（重试时） | 尺寸单位：美国 **`in`**，其他 **`cm`** |
| shipCompanyId | INTEGER | 否 | Shipping company ID（物流公司 ID；与 **`channelId`** / **`shipLogisticsType`** 配合，二选一方式见 `120015032`） |
| channelId | INTEGER | 否 | Channel ID（物流渠道 ID；来自 **`bg.logistics.shippingservices.get`** 的 **`onlineChannelDtoList`**） |
| shipLogisticsType | STRING | 否 | Ship logistics type（物流类型标识；与 **`channelId`** 二选一，见 `120015032`） |
| signServiceId | INTEGER | 否 | Signature service ID（签收服务 ID；订单带 **`signature_required_on_delivery`** 时须从推荐渠道选取，见 `120015545`） |
| pickupStartTime | INTEGER | 否 | Pickup window start time（预约揽收开始时间；须满足 `120019019` 等时间窗规则） |
| pickupEndTime | INTEGER | 否 | Pickup window end time（预约揽收结束时间；**pickupStartTime** 须早于 **pickupEndTime**） |
| confirmAcceptance | STRING[] | 否 | Confirmation matters for this shipment（发货前需确认的异常事项，如拒绝取消/改址/风控预警），枚举同 **`linkfox-temu-fulfillment-us`** 的 `DENY_CANCELLATION`、`DENY_ADDRESS_CHANGE`、`DENY_PARENT_RISK_WARNING` |
| uspsMailingDateOffset | INTEGER | 否 | USPS mailing date offset（USPS 邮寄日偏移；部分渠道禁止为 **0**，见 `120018086`） |
| autoConfirmAfterPickup | BOOLEAN | 否 | Auto confirm shipment after pickup（揽收后是否自动确认发货） |
| cooperativeWarehouseShipment | BOOLEAN | 否 | 是否合作仓发货（合作仓模式限制见 `120018074`、`120018079`、`120011030` 等） |
| interlineShipCompanyList | OBJECT[] | 否 | Interline / multi-leg shipping company list（联运各段承运信息） |
| orderSendInfoList | OBJECT[] | 否 | Product lines in this package（本包裹商品行；重试时若调整订单行须传） |
| retrySendSubRequestList | OBJECT[] | 否 | Retry sub-package list（子包裹重试参数；结构与子包裹物流字段类似 **`sendSubRequestList`**，见 `120011043`） |

###### `retrySendPackageRequestList[].orderSendInfoList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号） |
| quantity | INTEGER | **是** | Quantity（本行数量；**splitSubPackage=true** 时须为 **1**） |
| goodsId | LONG | 否 | Goods ID（商品 ID） |
| skuId | LONG | 否 | SKU ID |

###### `retrySendPackageRequestList[].interlineShipCompanyList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shipLogisticsType | STRING | **是** | Logistics type for this leg（该段物流类型） |
| shipStageType | STRING | **是** | Shipping stage type（运输段类型，如首程/末程） |
| shipCompanyId | INTEGER | **是** | Shipping company ID（该段物流公司 ID） |
| channelId | INTEGER | **是** | Channel ID（该段渠道 ID） |

###### `retrySendPackageRequestList[].retrySendSubRequestList[]` 元素字段

> 子包裹重试对象**不含** `orderSendInfoList`（见 Request Example）；物流/渠道/尺寸字段与父级包裹项类似。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSn | STRING | **是** | Sub-package SN（子包裹号） |
| warehouseId | STRING | **是** | Warehouse ID |
| weight | STRING | **是** | 重量 |
| weightUnit | STRING | **是** | 重量单位 |
| extendWeight | STRING | 否 | 扩展重量 |
| extendWeightUnit | STRING | 否 | 扩展重量单位 |
| length | STRING | **是** | 长度 |
| width | STRING | **是** | 宽度 |
| height | STRING | **是** | 高度 |
| dimensionUnit | STRING | **是** | 尺寸单位 |
| shipCompanyId | INTEGER | 否 | 物流公司 ID |
| channelId | INTEGER | 否 | 渠道 ID |
| shipLogisticsType | STRING | 否 | 物流类型 |
| signServiceId | INTEGER | 否 | 签收服务 ID |
| pickupStartTime | INTEGER | 否 | 揽收开始时间 |
| pickupEndTime | INTEGER | 否 | 揽收结束时间 |
| confirmAcceptance | STRING[] | 否 | 发货确认事项 |
| uspsMailingDateOffset | INTEGER | 否 | USPS 邮寄日偏移 |
| interlineShipCompanyList | OBJECT[] | 否 | 联运段列表（结构同上） |

> **调整范围（错误码 `120018004`）：** 一般仅允许修改 **`warehouseId`**、重量尺寸、物流公司/渠道等；不可随意变更业务不允许的字段。
> **重试限制：** 同一包裹不支持重复重试两次（`120018017`）、部分包裹类型不支持重试（`120018013`）。包裹须处于 **失败** 状态（`120018002`）。

### 响应结构

#### LinkFox 外层与脚本解析字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer / null | 脚本本地诊断字段，记录本次真实 HTTP 状态；连接失败时为 null，不是网关保证字段。先按此判断 HTTP 结果，401/402 转入 onboarding 引导，不以正文中的成功字段覆盖。 |
| _raw_response | 以实际响应为准 | 仅当响应根不是对象，或上游已有同名 _http_status 时，脚本将完整原响应放在此字段，并在外层记录真实状态；此时从原响应读取业务内容。 |
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断；不将 `0` 或 `false` 当成空。 |
| errmsg | string | 若返回，网关消息或错误说明。 |
| code | integer | 网关业务错误码：`1002` 为参数或 LinkFox Token 问题，`1003` 为转发失败；不能据 HTTP 成功推断履约成功。 |
| body | string | Temu 原始 JSON 字符串，保留原值。 |
| temuBody | object / array / scalar | 脚本对可解析的非空 body 增加的解析结果；解析失败时不生成此字段，仍保留原始 body。 |

以下为 Temu `body` 解析后的结构；Partner 表中的 `response` 可能是结构标注，实际响应也可能直接以 success 等字段为根，不强行增删层级。

#### 顶层字段

> Partner **Response** 表对上述字段 **Description** 列为空；下列说明结合 **Response Example**（`result: true/false`）与通用网关语义整理。

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | BOOLEAN | result（业务结果；更新/重试是否受理成功；Partner Response 表类型为 **BOOLEAN**，Response Example 为 `true`/`false`） |

> 调用成功时先判断 **`response.success === true`**，再读 **`result`**。异步购标结果仍须用 **`bg.logistics.shipment.result.get`** 查询包裹状态。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

| 错误码 | 错误信息（Partner） | 处理建议 |
|---|---|---|
| 120018078 | Cannot set shipLaterLimitTime: order was created for immediate shipment. | 仅 **`shipLater=true`** 创建的订单可改 **`shipLaterLimitTime`** |
| 120018002 | The package is not in failed state, please check the package status. | 仅对失败包裹调用 **`retrySendPackageRequestList`** |
| 120018027 | The packageSn is invalid. Please check the request area or if the packageSn is nonexistent etc. | 核对 **`packageSn`** 与站点 |
| 120018017 | Does not support retrying twice | 勿对同一包裹重复重试 |
| 120018013 | Does not support this package retry | 该包裹类型不可重试 |
| 120018004 | Only allow adjustments to warehouseId, weight, dimensions, shipping company, etc. | 仅调整允许的物流参数字段 |
| 120018062 | COD orders do not allow updating shipping information. | COD 订单不可更新 |
| 120018049 | Failed to update shipping information. Please cancel the appointment for pickup first. | 先取消揽收预约 |
| 120015532 | shipLaterLimitTime is invalid, please check the valid value for orders with "Y2_advance_sale" label | 按订单是否 **Y2_advance_sale** 选合法小时数 |
| 120015507 | Wrong package {*} information. Try again. | 检查重量尺寸单位 |
| 120015032 | You should choose one fulfillment way and fulfill channelId or shipLogisticsType. | **`channelId`** 与 **`shipLogisticsType`** 择一传全 |
| 120011006 | The parameter warehouseId is invalid. | 使用有效 **`warehouseId`** |
| 120011043 | Missing required parameters for 'sendSubRequestList'. | 拆包子包裹时补全 **`retrySendSubRequestList`** |
| 120011045 | For splitSubPackage quantity needs to be 1. | 拆包时 **quantity=1** |
| 120011044 | Exceeded maximum allowed attached packages. Limit is 10. | 子包裹最多 10 个 |
| 120019019 | Invalid pickup time range. Please ensure times are within the next 5 calendar days (8:00-17:00), on the same day, and can't be weekend, and pickupStartTime is before pickupEndTime | 按 Partner 规则设置揽收时间段 |
| 120019009 | Invalid pickup reservation time. See pickupRules for valid options. | 参考 **`bg.logistics.shippingservices.get`** 返回的 **pickupRules** |
| 120018088 | Failed to buy-shipping on platform , reason :{*} | 查看平台返回原因后调整参数重试 |
| 120015038 | Please note that the Buy Shipping service is not applicable to age-restricted product sales. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018074 | The cooperative warehouse mode does not support merging and shipping orders from multiple stores | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018079 | The warehouseid has not completed the cooperative warehouse authorization | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018080 | The current channel must be shipped later | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018082 | This channel is not supported for shipping | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018084 | Shipping from a cooperative warehouse and do not support unpacking sub packages | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018085 | The channel used by {*} needs to be shipped through a cooperative warehouse | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018086 | The current channel USPSMailingDateOffset prohibits the input of 0 | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011020 | Invalid request parameters | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011018 | Orders with "signature_required_on_delivery" can only buy shipping label from the channel which provide signature service,please call "bg.logistics.shippingservices.get" to get the recommended channels. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011017 | The input warehouse does not support the USPS Ground Advantage shipping service. It is recommended to use a warehouse where "supportsUspsGroundAdvantage" is true by calling the bg.logistics.warehouse.list.get API. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012044 | This channel requires passing the exam to gain access. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012061 | The current parent order has a pending risk control alert, It is not recommended to proceed with the performance. You can submit a cancellation request. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011015 | Incomplete warehouse details. Update in Seller Central to process shipment. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015040 | The parent order {*} can not be fulfilled by the selected logistics provider due to the customer's delivery preferences. Please change another logistics provider to fulfill again. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015545 | Orders with "signature_required_on_delivery" can only buy shipping label from the channel which provide signature service. Please call "bg.logistics.shippingservices.get" to get the recommended channel and request with the field "signServiceId". | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015543 | The Order with label "signature_required_on_delivery" and other orders cannot be fulfilled at the same time. Please fulfill the order with label "signature_required_on_delivery" separately. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015037 | This logistics provider does not support this business scenario. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018063 | Your funds have been reserved, so you are temporarily unable to use the 'Buy shipping' function. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018010 | The packages {*} have been canceled. Please fulfill again by Temu non-integrated logistics or Temu integrated logistics. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011051 | COD orders do not allow adding sub-packages | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012037 | Order can only buy shipping label after the "earliestTimeBuyShippingLabel". | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011030 | Cooperative warehouse order fulfillment restricted. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011089 | Purchasing shipping labels for Amazon FBA warehouses is not supported. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015531 | Only order with "Y2_advance_sale" label can be fulfilled by warehouse in "other" type. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015533 | The order with "Y2_advance_sale" label and the order without "Y2_advance_sale" label can't be fulfilled simultaneously. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015534 | Order with "Y2_advance_sale" label should set "shipLater=true" when you are fulfilled by Temu integrated logistics. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011082 | Failed to buy the shipping label. Please fill in the warehouse management type and warehouse brand in the Temu seller center first. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015518 | The order with "US-to-CA" Label and the order without "US-to-CA" Label can't be shipped together. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012029 | Warehouse and recipient in different countries splitSubPackage cannot enter "TRUE". | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015520 | Call failed: Cannot convert subPackage to self-shipment. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012023 | Address change pending. Please process before shipping. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012030 | Order cancel pending. Please process before shipping. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120019016 | Unexpected parameter pickupTime. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120019017 | Miss required parameter pickupTime. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015026 | A large items template has been used for the items in this package. Only specified logistics providers can be used for shipping. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120013007 | Product sku sensitive query fail | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120013008 | Order lacks necessary sensitive attributes. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120013009 | Order lacks necessary sensitive attributes. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011047 | Not support local mall | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011048 | Usage channel does not match the confirmation scenario | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012031 | The current parent order has a pending risk control alert. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018020 | The BBC order is not allowed. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015027 | A large items template has been used for the items in this package. Only special channels can be used for shipping. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120018025 | Orders exist after-sales applications, please complete the processing before operation | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012007 | The parentOrder or Order is invalid. Please check if the parentOrder matches the Order, the parentOrder or Order is nonexistent etc. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015521 | The parameter Weight should be integer. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120011072 | The request area is incorrect. Please check the request area and replace it with the correct request area. The request area for the United States is US, and the request area for other non-European countries is global. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120012016 | The parentOrder or Order is invalid. Please check if the parentOrder matches the Order, the parentOrder or Order is nonexistent etc. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |
| 120015528 | O-orders of COD type exist in body, and COD type O-orders can only be shipped with Temu Label. | 根据错误消息核对业务条件，继续调用遵守成本约束。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.logistics.shipment.update",
  "params": {
    "request": {
      "shipLaterLimitTime": "48"
    }
  }
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
