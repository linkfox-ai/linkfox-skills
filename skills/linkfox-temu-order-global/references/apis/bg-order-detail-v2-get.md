# 订单详情查询 V2 接口说明

接口总览见 [../api.md](../api.md)，认证指引见 [../onboarding.md](../onboarding.md)。

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

## 接口：订单详情查询 V2（bg.order.detail.v2.get）

读取指定父单及子单详情。

官方文档：https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `global`；全球区，非 US/EU。通用脚本兼容 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；通用脚本兼容 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；业务脚本优先直接使用，或从本地令牌存储读取后填入。 |
| storeKey | string | 与 accessToken 二选一 | 令牌键，对应 `~/.linkfox/temu-access-tokens.json` 中的记录（路径可由 `TEMU_TOKEN_STORE_PATH` 覆盖）；本技能脚本在本地解析，不把此字段转发到网关。 |
| tokenPurpose | string | 否 | 令牌用途，订单建议 `order-shipping`；本技能脚本仅用于本地选取令牌，不转发此字段。 |
| type | string | 是 | 本接口操作名，见下方操作标识；Temu 操作放在 Body，不是 URL path。 |
| params | object | 否 | 业务参数，使用本接口下方定义的 `request` 结构；无业务字段时脚本可省略。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accessToken | string | 与 storeKey 二选一 | 直接提供时优先于本地令牌。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌键；按 site + managementType + tokenPurpose 精确匹配，不跨店铺、站点或用途回退。 |
| tokenPurpose | string | 否 | 全球区订单脚本默认 `order-shipping`；仅用于本地令牌选择，不转发为业务字段。 |
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序读取首个非空值，优先于环境变量；用于 LinkFox 用户鉴权，与 Temu accessToken 不同。 |
| --inline | CLI flag | 否 | 保存完整响应并强制全量打印。 |
| --no-cache | CLI flag | 否 | 业务脚本不使用响应缓存；调用公共 run 时始终传入此选项，不读取或保存响应缓存。 |

LinkFox 环境变量按 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY` 顺序读取；Header `Authorization` 与 `Token` 同值。基础地址按 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL` 顺序兼容，默认正式网关。HTTP 超时默认 150 秒。
全球区专用脚本允许业务字段放在输入顶层，或放在对象 `params` 内；后者优先。顶层 `request` 整体作为 `params.request` 转发，不自动把任意业务字段再包一层。通用 `temu_proxy.py` 需显式传 site、managementType、type 和对象 params。令牌存储与授权 CLI 见 [../access-token.md](../access-token.md)。
会话数据保存在当前工作目录，禁止回退到临时目录；目录不可写时在请求前报错。无响应缓存仍可能由公共调用器创建空缓存目录，不保存响应缓存文件。

本接口 `type` 固定为 `bg.order.detail.v2.get`；对应脚本 `scripts/global_order_detail_v2_get.py`。

#### params 业务载荷

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 业务请求对象，官方标注为选填；子字段必填性见下表。 |

#### `request`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent order number（父订单号） |
| fulfillmentTypeList | STRING[] | 否 | The type of order fulfillment（订单履约类型），见下表 |

##### `fulfillmentTypeList[]`

| 值 | 说明 |
|----|------|
| `fulfillBySeller` | fulfill by seller（卖家履约） |
| `fulfillByCooperativeWarehouse` | fulfill by Cooperative Warehouse（合作仓履约） |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 外层状态；遵循公共响应码基本规则，不替换为 Temu 成功判断。 |
| errmsg | string | LinkFox 外层消息；错误时保留。 |
| code | integer | 网关错误码：1002 为参数或 Token 问题，1003 为转发失败。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | object / array | 脚本对非空且合法的 body 解析所得；解析失败时不生成，不补造业务结果。 |
| transportHttpStatus | integer / null | 脚本记录的外层 HTTP 状态，连接失败时为 null。 |
| error / details | string | 连接异常或非 JSON HTTP 错误的说明与原始内容（存在时保留）。 |

先检查外层 HTTP 与 errcode，再检查网关 code（如有错误），然后解析 body，依据 Temu 的 success / errorCode / errorMsg / result 解释结果。下列为 Temu body 解析后的原始业务字段。

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功（success） |
| errorCode | INTEGER | 错误码（error code） |
| errorMsg | STRING | 错误消息（error message） |
| result | OBJECT | 业务结果（result） |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentOrderMap | OBJECT | Parent order information（父订单信息） |
| orderList | OBJECT[] | Order information（子订单列表） |

#### `parentOrderMap`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentOrderSn | STRING | Parent order number（父订单号） |
| parentOrderStatus | INTEGER | 父订单状态：1 待处理、2 待发货、3 已取消、4 已发货、41 部分发货、5 已送达、51 部分送达（Status of the parent order：`1` PENDING；`2` UN_SHIPPING；`3` CANCELED；`4` SHIPPED；`41` PARTIALLY_SHIPPED；`5` DELIVERED；`51` PARTIALLY_DELIVERED） |
| parentOrderTime | INTEGER | Time when the parent order was placed（下单时间，秒） |
| expectShipLatestTime | INTEGER | Latest shipment time（最晚发货时间，秒） |
| parentOrderPendingFinishTime | INTEGER | Time when the parent order finish pending（待处理完成时间，秒） |
| latestDeliveryTime | INTEGER | Latest delivery time（最晚送达时间，秒） |
| parentShippingTime | INTEGER | Time when the parent order was shipped（父订单发货时间，秒） |
| siteId | LONG | 站点 ID（Site ID） |
| regionId | LONG | 区域 ID，例如美国为 211（Region ID，e.g. USA - **211**） |
| parentOrderLabel | OBJECT[] | List of PO order status labels（父订单状态标签） |
| fulfillmentWarning | STRING[] | Fulfillment Prompt（履约提示），见下表 |
| hasShippingFee | BOOLEAN | 用户实付运费是否为零：`true` 为零，`false` 非零（**only for local mall**） |
| regionName1 | STRING | Address region 1（地址区域 1） |
| regionName2 | STRING | 二级地址区域（Address region 2） |
| regionName3 | STRING | 三级地址区域（Address region 3） |
| orderPaymentType | STRING | 订单支付方式：COD 货到付款、PPD 预付（Order payment type：`COD`、`PPD`） |
| batchOrderNumberList | STRING[] | batchOrderNumberList；**仅合作仓履约**有值，否则为空 |
| shippingMethod | INTEGER | 配送渠道：1 标准配送、2 门店配送、3 买家自提（delivery channel type：`1` Standard Shipping，`2` Store Delivery，`3` Customer Pickup） |
| isShipmentConsolidatedByMainMall | BOOLEAN | 为 `true` 表示 PO 已由主站合并发货，需在主站侧确认发货/面单 |
| parentConfirmTime | INTEGER | 父订单确认时间，秒级时间戳（Confirmation time of parent order in seconds (timestamp)） |

##### `parentOrderMap.parentOrderLabel[]` — `name` 常见值

| name | 说明 |
|------|------|
| `soon_to_be_overdue` | 即将逾期 |
| `past_due` | 已逾期 |
| `pending_buyer_cancellation` | 买家取消待处理 |
| `pending_buyer_address_change` | 买家改地址待处理 |
| `pending_risk_control_alert` | 风控预警待处理 |
| `signature_required_on_delivery` | 需要签收 |

| 参数 | 类型 | 说明 |
|------|------|------|
| name | STRING | 标签名称（Label name） |
| value | INTEGER | 标签是否存在：`0` 无标签，`1` 有标签 |

##### `parentOrderMap.fulfillmentWarning[]`

| 值 | 说明 |
|----|------|
| `SUGGEST_SIGNATURE_ON_DELIVERY` | 建议为此订单购买签收服务以保障履约（It is recommended to purchase signature service for this order to ensure fulfillment） |
| `CONFIRMED_CHANGED_ADDRESS` | 地址已变更并确认，重新拉单以获取最新地址（Address has been changed and confirmed; pull the order again for the latest address） |
| `RESTRICT_FEDEX_SELF_SHIPPING` | 限制使用 FedEx 运单号确认发货（Restricted from confirming shipment by FedEx tracking number） |
| `RESTRICT_USPS_SELF_SHIPPING` | 限制使用 USPS 运单号确认发货（Restricted from confirming shipment by USPS tracking number） |
| `RESTRICT_SELF_SHIPPING` | 限制使用运单号确认发货（Restricted from confirming shipment by tracking number） |
| `BLOCK_LOGISTICS_PROVIDERS_{Name1,Name2,...}` | 买家屏蔽了部分物流商，名称在响应中展开（Consumer blocked some logistics providers (names in response)） |
| `REQUIRES_CUSTOMER_PICKUP` | 该订单只能通过买家自提履约（This order can only be fulfilled via customer pickup） |

#### `orderList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| orderSn | STRING | Order number (sub-order number)（子订单号） |
| quantity | INTEGER | 卖家需履约数量（The quantity seller needs to fulfill：`quantity = originalOrderQuantity - canceledQuantityBeforeShipment`） |
| canceledQuantityBeforeShipment | INTEGER | 发货前取消数量（The quantity of canceled before shipment） |
| originalOrderQuantity | INTEGER | 原始下单数量（originalOrderQuantity） |
| goodsId | LONG | 商品 ID（Goods ID） |
| packageSnInfo | OBJECT[] | package information（包裹信息） |
| packageAbnormalTypeList | STRING[] | Logistics anomalies after shipment，见下表 |
| skuId | LONG | SKU ID；**仅 LOCAL 卖家有效，非 SEMI** |
| spec | STRING | 买家可见商品规格（Product specification description for customer） |
| originalSpecName | STRING | 卖家侧商品规格，仅确认时间在近六个月内的订单适用（Product specification for seller；**Only for orders whose confirmation time is within no more than six months**） |
| thumbUrl | STRING | 缩略图 URL（Thumbnail image URL） |
| goodsName | STRING | 买家可见商品名称（Product name for customer） |
| originalGoodsName | STRING | 卖家侧商品名称，仅确认时间在近六个月内的订单适用（Product name for seller；**Only for orders whose confirmation time is within no more than six months**） |
| orderStatus | INTEGER | 子订单状态：1 待处理、2 待发货、3 已取消、4 已发货、41 部分发货、5 已送达、51 部分送达（Status of the order：`1` PENDING；`2` UN_SHIPPING；`3` CANCELED；`4` SHIPPED；`41` PARTIALLY_SHIPPED；`5` DELIVERED；`51` PARTIALLY_DELIVERED） |
| productList | OBJECT[] | Product information；**仅 SEMI 卖家有效，非 LOCAL** |
| orderLabel | OBJECT[] | The label of order（子订单标签） |
| fulfillmentWarning | STRING[] | Fulfillment Prompt（子订单履约提示），见下表 |
| fulfillmentType | STRING | 卖家履约 / 合作仓履约（`fulfillBySeller` / `fulfillByCooperativeWarehouse`） |
| inventoryDeductionWarehouseId | STRING | 扣减库存仓库 ID（The id of inventory deduction warehouse） |
| inventoryDeductionWarehouseName | STRING | 扣减库存仓库名称（The name of inventory deduction warehouse） |
| orderPaymentType | STRING | 订单支付方式：COD 货到付款、PPD 预付（Order payment type：`COD`、`PPD`） |
| isCancelledDuringPending | BOOLEAN | 是否在待处理期间全部取消（Whether the order is completely cancelled during the pending period） |
| earliestTimeBuyShippingLabel | INTEGER | 允许购买面单的最早时间（Order can only buy shipping label after this time） |
| earliestTimeGetShippingDocument | INTEGER | 允许获取发货单据的最早时间（Order can only get shipping document after this time） |
| orderShippingTime | INTEGER | Time when the order was shipped；若含未发货或延迟包裹，返回 **null** |
| isShipmentConsolidatedByMainMall | BOOLEAN | 主站合并发货标记 |
| orderCreateTime | INTEGER | 子订单创建时间（The time when the order was created） |
| qualificationUploadEndTime | LONG | 订单资质文件上传截止时间（Deadline for uploading order qualification documents） |
| hasUploadedEvidence | BOOLEAN | 商家是否已上传 SN、IMEI、鉴定报告等核验信息（Whether the merchant has uploaded verification information such as SN, IMEI, and appraisal report） |

#### `packageSnInfo[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | 订单包裹号（package number of this order） |
| packageDeliveryType | INTEGER | 包裹配送类型：1 卖家非集成、2 卖家 Temu 集成、3 合作仓非集成、4 合作仓 Temu 集成（Package delivery type：`1` Seller non-integrated；`2` Seller Temu-integrated；`3` Cooperative warehouse non-integrated；`4` Cooperative warehouse Temu-integrated） |
| callSuccess | BOOLEAN | Whether the latest request `bg.logistics.shipment.create` is successful；与 Temu 非集成物流无关 |

##### `orderList[].packageAbnormalTypeList[]`

| 值 | 说明 |
|----|------|
| `WRONG_SHIPPING_ADDRESS` | 收货地址错误（Wrong shipping address） |
| `SUSPECTED_ERROR_PROVIDER` | 疑似承运商异常（Suspected error provider） |
| `NO_TRACK` | 无物流轨迹（No track） |
| `TRACK_TOO_EARLY` | 物流轨迹过早（Track too early） |
| `OVERTIME_COLLECTION` | 揽收超时（Overtime collection） |
| `TRACK_COLLECT_FAIL` | 揽收失败（Track collect fail） |
| `SIGNED_BUT_UNRECEIVED_TASK` | 已签收但未收货任务（Signed but unreceived task） |

##### `productList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| productId | LONG | 产品 ID（Product Id） |
| productSkuId | LONG | 产品变体 SKU ID；**仅 SEMI 卖家有效，非 LOCAL** |
| soldFactor | LONG | 商品数量与件数的换算因子（Conversion factor between product quantity and item quantity） |
| extCode | STRING | 商品编码（Item code） |

##### `orderList[].orderLabel[]` — `name` 常见值

`customized_products`、`US_to_CA`、`is_US_to_CA_BBC`、`Y2_advance_sale`、`pre_sale_order`、`made_to_order`、`vacation_order`、`second_hand_collectible_order`、`second_hand_luxury_order`

| 参数 | 类型 | 说明 |
|------|------|------|
| name | STRING | 标签名称（Label name） |
| value | INTEGER | 标签是否存在：0 无标签、1 有标签；BBC 订单结合 is_US_to_CA_BBC 判断（Is there a label：`0` = no label，`1` = labeled；BBC orders need to judge combined with `is_US_to_CA_BBC`） |

##### `orderList[].fulfillmentWarning[]`

| 值 | 说明 |
|----|------|
| `SAVE_SN_INFORMATION_FOR_RETURN` | 建议保存该订单 SN，用于退货鉴真（It is recommended to save sn information for this order to identify the authenticity of the returned goods） |
| `REQUIRES_AUTHENTICATION_REPORT_SUBMISSION` | Requires submission of an authentication report in Temu Seller Center；超时自动取消并可能处罚 |
| `REQUIRES_AGE_VERIFICATION` | 建议购买签收人年龄验证服务（It is recommended to purchase the age verification service for the signatory） |
| `SPECIFIC_LOGISTICS_REQUIRED` | 须使用指定物流履约（It is required to choose specific logistics to fulfill this order） |
| `REQUIRES_CUSTOMER_PICKUP` | 该订单只能通过买家自提履约（This order can only be fulfilled via customer pickup） |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `code=1002`：修正参数或 LinkFox Token；`code=1003`：检查 Temu 令牌、用途、IP 白名单和转发情况。
- Temu `success=false` 时根据 `errorCode`、`errorMsg` 解释失败；外层 HTTP 正常不代表 Temu 操作成功。保留 `result` 与 warning，不自动重试、翻页或换参数试探。
- body 不是合法 JSON 时保留原文，不把解析失败当作空业务结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.order.detail.v2.get",
  "params": {
    "request": {
      "parentOrderSn": "PO-123456789",
      "fulfillmentTypeList": [
        "fulfillBySeller"
      ]
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
  "skillName": "linkfox-temu-order-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
