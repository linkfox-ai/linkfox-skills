# Temu 欧洲站 更新发货/重试购标 接口说明

[接口导航](../api.md)；[授权与脚本兼容约定](../api.md#运行约定)。

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

> 官方：[Partner EU 文档](https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896)

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `eu`；必须匹配店铺令牌所属站点。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；合作仓仅支持半托管。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；与 LinkFox API Key 不同。脚本调用网关前解析本地选店并填入此字段。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌库中的店铺键，指向 `~/.linkfox/temu-access-tokens.json`；当前脚本在本地读取并转换为 `accessToken`，不发送此字段。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`；脚本用于本地令牌选择，不发送至网关。 |
| type | string | 是 | 当前操作的 Temu 接口标识，见本接口说明。 |
| params | object | 否 | Temu 业务参数；通常使用下方 `request` 对象。 |

本操作的 `type` 固定为 `bg.logistics.shipment.update`。脚本：`scripts/eu_buy_shipping_logistics_shipment_update.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家延后创建物流单，或在购标/下单失败后对包裹重新在线下单。）

> **典型场景：**
> 1. 仅更新 **`shipLaterLimitTime`**（须由 **`bg.logistics.shipment.create`** 且 **`shipLater=true`** 创建）。
> 2. **`retrySendPackageRequestList`**：对 **失败状态** 的包裹（`packageSn`）调整仓库/尺寸重量/渠道后重试购标。
> **前置：** `packageSn` 来自 **`bg.logistics.shipment.result.get`**；渠道参数来自 **`bg.logistics.shippingservices.get`**。

#### `request` 内字段

> Partner **请求** 表将 **`request`**、**`retrySendPackageRequestList`**、**`shipLaterLimitTime`** 均标为选填（False）；下列说明列内容来自 Partner 导出页 **必填** 列（该页将长说明写在必填列而非说明列）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| retrySendPackageRequestList | OBJECT[] | 否 | retry Package List Information（失败包裹重试列表；每项对应一个待重试的 **`packageSn`** 及新的物流/尺寸参数） |
| shipLaterLimitTime | STRING | 否 | **Usage Rules:** shipLaterLimitTime can be updated only if the order was created with **shipLater=true** via **`bg.logistics.shipment.create`**. **Available Options by Order Label:** For orders **without** the **`Y2_advance_sale`** label, available options are: **24, 48, 72, 96, 120** hours. For orders **with** the **`Y2_advance_sale`** label, available options are: **144, 168, 192, 216, 240, 264, 288, 312, 336, 360** hours.（仅 **`shipLater=true`** 创建的订单可更新；无效值见错误码 **`120015532`**、**`120018078`**） |

##### `shipLaterLimitTime` 可选值

| 订单标签 | 可选小时（字符串） |
|----------|-------------------|
| 无 **`Y2_advance_sale`** 标签 | `24`、`48`、`72`、`96`、`120` |
| 有 **`Y2_advance_sale`** 标签 | `144`、`168`、`192`、`216`、`240`、`264`、`288`、`312`、`336`、`360` |

> 与 **`bg.logistics.shipment.create`** 入参 **`shipLaterLimitTime`** 规则一致；无效值见错误码 `120015532`。

##### `retrySendPackageRequestList[]` 元素字段

> Partner 请求表中 `retrySendPackageRequestList` 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **请求示例**，说明结合 Partner 错误码、**`bg.logistics.shipment.create`** 的 **`sendRequestList[]`** 同名字段及 Buy-Shipping 流程整理。

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
| confirmAcceptance | STRING[] | 否 | Confirmation matters for this shipment（发货前需确认的异常事项，如拒绝取消/改址/风控预警），枚举同 **`linkfox-temu-fulfillment-eu`** 的 `DENY_CANCELLATION`、`DENY_ADDRESS_CHANGE`、`DENY_PARENT_RISK_WARNING` |
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
| skuId | LONG | 否 | SKU 标识（SKU ID） |

###### `retrySendPackageRequestList[].interlineShipCompanyList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shipLogisticsType | STRING | **是** | Logistics type for this leg（该段物流类型） |
| shipStageType | STRING | **是** | Shipping stage type（运输段类型，如首程/末程） |
| shipCompanyId | INTEGER | **是** | Shipping company ID（该段物流公司 ID） |
| channelId | INTEGER | **是** | Channel ID（该段渠道 ID） |

###### `retrySendPackageRequestList[].retrySendSubRequestList[]` 元素字段

> 子包裹重试对象**不含** `orderSendInfoList`（见 请求示例）；物流/渠道/尺寸字段与父级包裹项类似。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSn | STRING | **是** | Sub-package SN（子包裹号） |
| warehouseId | STRING | **是** | 发货仓库 ID |
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

#### 网关与脚本响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回此字段，按公共规则判断，不将 `0` 或 `false` 视为空。 |
| errmsg | string | 若返回此字段，为网关消息；保留原文。 |
| body | string | Temu 原始 JSON 字符串；先判断网关状态，再解析业务内容。 |
| code | integer | 网关错误码：`1002` 为参数或 Token 无效，`1003` 为转发失败；不可当作 Temu 错误码。 |
| temuBody | object / array / scalar | 脚本在 `body` 可解析为 JSON 时增加的字段，完整保留原 `body`；不可解析时不增加。 |
| _http_status | integer / null | 仅脚本附加的本次 HTTP 状态码，不是网关字段；连接失败无 HTTP 响应时为 `null`，错误原因仍保留在 `error`。大响应摘要也展示该状态。 |

网关正常响应后，解析 `body`；若存在 `response` 包装则读取其业务对象。以下为 Temu 业务字段，不能替代外层 HTTP 与 `errcode` 判断。

#### 顶层字段

> Partner **响应** 表对上述字段 **说明** 列为空；下列说明结合 **响应示例**（`result: true/false`）与通用网关语义整理。

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | BOOLEAN | result（业务结果；更新/重试是否受理成功；Partner 响应表类型为 **BOOLEAN**，响应示例 为 `true`/`false`） |

> 调用成功时先判断 **`response.success === true`**，再读 **`result`**。异步购标结果仍须用 **`bg.logistics.shipment.result.get`** 查询包裹状态。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
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
| 120015038 | Please note that the Buy Shipping service is not applicable to age-restricted product sales. |  |
| 120018074 | The cooperative warehouse mode does not support merging and shipping orders from multiple stores |  |
| 120018079 | The warehouseid has not completed the cooperative warehouse authorization |  |
| 120018080 | The current channel must be shipped later |  |
| 120018082 | This channel is not supported for shipping |  |
| 120018084 | Shipping from a cooperative warehouse and do not support unpacking sub packages |  |
| 120018085 | The channel used by {*} needs to be shipped through a cooperative warehouse |  |
| 120018086 | The current channel USPSMailingDateOffset prohibits the input of 0 |  |
| 120011020 | Invalid request parameters |  |
| 120011018 | Orders with "signature_required_on_delivery" can only buy shipping label from the channel which provide signature service,please call "bg.logistics.shippingservices.get" to get the recommended channels. |  |
| 120011017 | The input warehouse does not support the USPS Ground Advantage shipping service. It is recommended to use a warehouse where "supportsUspsGroundAdvantage" is true by calling the bg.logistics.warehouse.list.get API. |  |
| 120012044 | This channel requires passing the exam to gain access. |  |
| 120012061 | The current parent order has a pending risk control alert, It is not recommended to proceed with the performance. You can submit a cancellation request. |  |
| 120011015 | Incomplete warehouse details. Update in Seller Central to process shipment. |  |
| 120015040 | The parent order {*} can not be fulfilled by the selected logistics provider due to the customer's delivery preferences. Please change another logistics provider to fulfill again. |  |
| 120015545 | Orders with "signature_required_on_delivery" can only buy shipping label from the channel which provide signature service. Please call "bg.logistics.shippingservices.get" to get the recommended channel and request with the field "signServiceId". |  |
| 120015543 | The Order with label "signature_required_on_delivery" and other orders cannot be fulfilled at the same time. Please fulfill the order with label "signature_required_on_delivery" separately. |  |
| 120015037 | This logistics provider does not support this business scenario. |  |
| 120018063 | Your funds have been reserved, so you are temporarily unable to use the 'Buy shipping' function. |  |
| 120018010 | The packages {*} have been canceled. Please fulfill again by Temu non-integrated logistics or Temu integrated logistics. |  |
| 120011051 | COD orders do not allow adding sub-packages |  |
| 120012037 | Order can only buy shipping label after the "earliestTimeBuyShippingLabel". |  |
| 120011030 | Cooperative warehouse order fulfillment restricted. |  |
| 120011089 | Purchasing shipping labels for Amazon FBA warehouses is not supported. |  |
| 120015531 | Only order with "Y2_advance_sale" label can be fulfilled by warehouse in "other" type. |  |
| 120015533 | The order with "Y2_advance_sale" label and the order without "Y2_advance_sale" label can't be fulfilled simultaneously. |  |
| 120015534 | Order with "Y2_advance_sale" label should set "shipLater=true" when you are fulfilled by Temu integrated logistics. |  |
| 120011082 | Failed to buy the shipping label. Please fill in the warehouse management type and warehouse brand in the Temu seller center first. |  |
| 120015518 | The order with "US-to-CA" Label and the order without "US-to-CA" Label can't be shipped together. |  |
| 120012029 | Warehouse and recipient in different countries splitSubPackage cannot enter "TRUE". |  |
| 120015520 | Call failed: Cannot convert subPackage to self-shipment. |  |
| 120012023 | Address change pending. Please process before shipping. |  |
| 120012030 | Order cancel pending. Please process before shipping. |  |
| 120019016 | Unexpected parameter pickupTime. |  |
| 120019017 | Miss required parameter pickupTime. |  |
| 120015026 | A large items template has been used for the items in this package. Only specified logistics providers can be used for shipping. |  |
| 120013007 | Product sku sensitive query fail |  |
| 120013008 | Order lacks necessary sensitive attributes. |  |
| 120013009 | Order lacks necessary sensitive attributes. |  |
| 120011047 | Not support local mall |  |
| 120011048 | Usage channel does not match the confirmation scenario |  |
| 120012031 | The current parent order has a pending risk control alert. |  |
| 120018020 | The BBC order is not allowed. |  |
| 120015027 | A large items template has been used for the items in this package. Only special channels can be used for shipping. |  |
| 120018025 | Orders exist after-sales applications, please complete the processing before operation |  |
| 120012007 | The parentOrder or Order is invalid. Please check if the parentOrder matches the Order, the parentOrder or Order is nonexistent etc. |  |
| 120015521 | The parameter Weight should be integer. |  |
| 120011072 | The request area is incorrect. Please check the request area and replace it with the correct request area. The request area for the United States is US, and the request area for other non-European countries is global. |  |
| 120012016 | The parentOrder or Order is invalid. Please check if the parentOrder matches the Order, the parentOrder or Order is nonexistent etc. |  |
| 120015528 | O-orders of COD type exist in body, and COD type O-orders can only be shipped with Temu Label. |  |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.logistics.shipment.update",
  "params": {
    "request": {
      "shipLaterLimitTime": "48"
    }
  }
}
'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
