# 订单列表查询 V2 接口说明

返回 [接口总览](../api.md)。Partner 文档入口：https://partner-us.temu.com/documentation（`menu_code` / `sub_menu_code` 以后台对应接口页为准）。

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

## 接口：订单列表查询 V2 — `bg.order.list.v2.get`

按筛选条件批量查询当前店铺的订单列表。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 美国站为 `us`；US 脚本默认 `us`。 |
| managementType | string | 是 | 美国半托管为 `semi-managed`；US 脚本默认此值。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先使用显式 accessToken。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌替代字段，为 `~/.linkfox/temu-access-tokens.json` 中的店铺键；脚本在本地解析后发送 accessToken。 |
| tokenPurpose | string | 否 | 建议 `order-shipping`（订单/发货）；脚本用于选取对应用途的本地令牌，不混入业务参数，也不转发此字段。 |
| type | string | 是 | 本接口标识：`bg.order.list.v2.get`，写在 Body 中，不是 URL 路径。 |
| params | object | 否 | 官方业务参数对象，业务字段位于 `params.request`。 |
| params.request | OBJECT | 否 | 官方声明为选填对象；内部字段按下表约定，不因外层选填而免除内部必填要求。 |

脚本允许业务字段放在顶层（如 `request`）或嵌套 `params`；存在对象类型的 `params` 时优先使用该对象。认证、站点等保留键不会混入业务参数。脚本认证兼容与选项见 [运行约定](../api.md#脚本运行约定)。

```text
params
└── request (OBJECT, 选填)
    ├── pageNumber
    ├── pageSize
    ├── parentOrderStatus
    ├── parentOrderSnList[]
    ├── createAfter / createBefore
    ├── expectShipLatestTimeStart / expectShipLatestTimeEnd
    ├── updateAtStart / updateAtEnd
    ├── parentConfirmTimeStart / parentConfirmTimeEnd
    ├── regionId
    ├── fulfillmentTypeList[]
    ├── parentOrderLabel[]
    ├── packageAbnormalTypeList[]
    ├── sortby
    ├── hasPreSaleOrder
    ├── hasQualificationRequiredOrder
    └── skuId
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNumber | INTEGER | 否 | 页码，**默认 1** |
| pageSize | INTEGER | 否 | 每页条数，**默认 10**，**最大 100** |
| parentOrderStatus | INTEGER | 否 | 父订单状态；**默认查询全部** |
| parentOrderSnList | STRING[] | 否 | 父订单号列表，**单次最多 20 条** |
| createAfter | INTEGER | 否 | 父订单创建时间起始值，秒级时间戳；**须与 `createBefore` 成对使用** |
| createBefore | INTEGER | 否 | 父订单创建时间结束值，秒级时间戳，**闭区间**；**须与 `createAfter` 成对使用** |
| expectShipLatestTimeStart | INTEGER | 否 | 查询最晚发货时间的起始值，单位秒 |
| expectShipLatestTimeEnd | INTEGER | 否 | 查询最晚发货时间的结束值，单位秒 |
| updateAtStart | INTEGER | 否 | 订单更新或状态变更时间起始值，秒级时间戳；**须与 `updateAtEnd` 成对使用** |
| updateAtEnd | INTEGER | 否 | 订单更新或状态变更时间结束值，秒级时间戳，**闭区间**；**须与 `updateAtStart` 成对使用** |
| parentConfirmTimeStart | INTEGER | 否 | 父订单确认开始时间（秒级时间戳）；**须与 `parentConfirmTimeEnd` 成对使用** |
| parentConfirmTimeEnd | INTEGER | 否 | 父订单确认结束时间（秒级时间戳）；**须与 `parentConfirmTimeStart` 成对使用** |
| regionId | LONG | 否 | 区域 ID，例如 USA - **211** |
| fulfillmentTypeList | STRING[] | 否 | 订单履约类型列表，见下表 |
| parentOrderLabel | STRING[] | 否 | PO 订单状态标签筛选，见下表 |
| packageAbnormalTypeList | STRING[] | 否 | 发货后物流异常类型筛选，见下表 |
| sortby | STRING | 否 | 排序字段，**默认按订单创建时间**；输出为**倒序** |
| hasPreSaleOrder | BOOLEAN | 否 | 父订单是否含在途预售子单 |
| hasQualificationRequiredOrder | BOOLEAN | 否 | 是否含需上传资质子单 |
| skuId | LONG | 否 | SKU 编号 |

##### `parentOrderStatus`（入参筛选）

| 值 | 说明 |
|----|------|
| `0` | All（全部） |
| `1` | PENDING（待处理） |
| `2` | UN_SHIPPING（待发货） |
| `3` | CANCELED（已取消） |
| `4` | SHIPPED（已发货） |
| `5` | RECEIPTED（已签收） |
| `41` | Partially shipped（部分发货，仅本土商城） |
| `51` | Partially received（部分签收，仅本土商城） |

##### `fulfillmentTypeList[]`

| 值 | 说明 |
|----|------|
| `fulfillBySeller` | 卖家履约 |
| `fulfillByCooperativeWarehouse` | 合作仓履约 |

##### `parentOrderLabel[]`（筛选）

| 值 | 说明 |
|----|------|
| `soon_to_be_overdue` | 即将逾期 |
| `past_due` | 已逾期 |
| `pending_buyer_cancellation` | 买家待取消 |
| `pending_buyer_address_change` | 买家待改地址 |
| `pending_risk_control_alert` | 风控预警待处理 |
| `signature_required_on_delivery` | 签收需签名 |

##### `packageAbnormalTypeList[]`（筛选）

| 值 | 说明 |
|----|------|
| `WRONG_SHIPPING_ADDRESS` | 收货地址错误 |
| `SUSPECTED_ERROR_PROVIDER` | 疑似承运商异常 |
| `NO_TRACK` | 无轨迹 |
| `TRACK_TOO_EARLY` | 轨迹过早 |
| `OVERTIME_COLLECTION` | 揽收超时 |
| `TRACK_COLLECT_FAIL` | 揽收失败 |

##### `sortby`

| 值 | 说明 |
|----|------|
| `createTime` | 按创建时间排序（**默认**） |
| `updateTime` | 按更新时间排序 |

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共响应码基本规则判断；保留原始值。 |
| errmsg | string | 网关错误消息；完整保留。 |
| code | integer | 网关错误码：`1002` 参数或 Token 错误，`1003` 转发失败；不得与 Temu `errorCode` 混淆。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | JSON value | 脚本在 `body` 为非空且可解析的 JSON 字符串时增加的解析结果；解析失败时不增加此字段。 |
| error | string | HTTP 非 JSON 错误或连接错误信息（仅错误时出现）。 |
| details | string | 非 JSON HTTP 错误的原始响应内容（仅错误时出现）。 |
| gatewayResponse | JSON value | 仅当网关返回非对象 JSON 时，脚本在落盘与展示层包装原始值；不属于 Temu 业务字段。 |

以下为 Temu `body` 解析后的业务字段。先判断外层 HTTP 与 `errcode`，再检查网关 `code` 和 Temu `success` / `errorCode` / `errorMsg`，不得仅因 JSON 可解析而判成功。

```text
response
├── success
├── errorCode
├── errorMsg
└── result
    ├── pageItems[]
    │   ├── parentOrderMap
    │   │   ├── parentOrderSn
    │   │   ├── parentOrderStatus
    │   │   ├── parentOrderTime
    │   │   ├── expectShipLatestTime
    │   │   ├── parentOrderPendingFinishTime
    │   │   ├── latestDeliveryTime
    │   │   ├── parentShippingTime
    │   │   ├── siteId
    │   │   ├── regionId
    │   │   ├── parentOrderLabel[]
    │   │   │   ├── name
    │   │   │   └── value
    │   │   ├── fulfillmentWarning[]
    │   │   ├── hasShippingFee
    │   │   ├── updateTime
    │   │   ├── orderPaymentType
    │   │   ├── batchOrderNumberList[]
    │   │   ├── shippingMethod
    │   │   ├── isShipmentConsolidatedByMainMall
    │   │   └── parentConfirmTime
    │   └── orderList[]
    │       ├── orderSn
    │       ├── quantity
    │       ├── canceledQuantityBeforeShipment
    │       ├── originalOrderQuantity
    │       ├── goodsId
    │       ├── skuId
    │       ├── spec
    │       ├── originalSpecName
    │       ├── thumbUrl
    │       ├── goodsName
    │       ├── originalGoodsName
    │       ├── orderStatus
    │       ├── productList[]
    │       │   ├── productId
    │       │   ├── productSkuId
    │       │   ├── soldFactor
    │       │   └── extCode
    │       ├── packageAbnormalTypeList[]
    │       ├── orderLabel[]
    │       │   ├── name
    │       │   └── value
    │       ├── fulfillmentWarning[]
    │       ├── fulfillmentType
    │       ├── inventoryDeductionWarehouseId
    │       ├── inventoryDeductionWarehouseName
    │       ├── orderPaymentType
    │       ├── isCancelledDuringPending
    │       ├── earliestTimeBuyShippingLabel
    │       ├── earliestTimeGetShippingDocument
    │       ├── orderShippingTime
    │       ├── isShipmentConsolidatedByMainMall
    │       ├── orderCreateTime
    │       └── qualificationUploadEndTime
    └── totalItemNum
```

#### `response` 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果 |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| pageItems | OBJECT[] | 分页订单条目 |
| totalItemNum | INTEGER | 匹配记录总数 |

#### `result.pageItems[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentOrderMap | OBJECT | 父订单信息 |
| orderList | OBJECT[] | 子订单列表 |

#### `parentOrderMap`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentOrderSn | STRING | 父订单号 |
| parentOrderStatus | INTEGER | 父订单状态，见下表（**出参枚举**） |
| parentOrderTime | INTEGER | 下单时间，秒 |
| expectShipLatestTime | INTEGER | 最晚发货时间，秒 |
| parentOrderPendingFinishTime | INTEGER | 待处理完成时间，秒 |
| latestDeliveryTime | INTEGER | 最晚送达时间，秒 |
| parentShippingTime | INTEGER | 父订单发货时间，秒 |
| siteId | LONG | 站点 ID |
| regionId | LONG | 区域 ID，例如 USA - **211** |
| parentOrderLabel | OBJECT[] | 父订单标签列表 |
| fulfillmentWarning | STRING[] | 履约提示，见下表 |
| hasShippingFee | BOOLEAN | 用户实付运费是否为零：`true` 为零，`false` 非零（**仅 本土商城**） |
| updateTime | LONG | 订单更新时间，秒 |
| orderPaymentType | STRING | 订单支付类型：`COD`、`PPD` |
| batchOrderNumberList | STRING[] | 批次单号列表；**仅合作仓履约**有值，否则为空 |
| shippingMethod | INTEGER | 配送渠道类型：`1` 标准配送，`2` 店铺配送，`3` 买家自提 |
| isShipmentConsolidatedByMainMall | BOOLEAN | 为 `true` 表示主站已合并发货，需在主站侧确认发货/面单 |
| parentConfirmTime | INTEGER | 父订单确认时间，秒级时间戳 |

##### `parentOrderStatus`（出参）

| 值 | 说明 |
|----|------|
| `1` | PENDING（待处理） |
| `2` | UN_SHIPPING（待发货） |
| `3` | CANCELED（已取消） |
| `4` | SHIPPED（已发货） |
| `41` | PARTIALLY_SHIPPED（部分发货） |
| `5` | DELIVERED（已送达） |
| `51` | PARTIALLY_DELIVERED（部分送达） |

##### `parentOrderMap.parentOrderLabel[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| name | STRING | 标签名 |
| value | INTEGER | 是否存在标签：`0` 无标签，`1` 有标签 |

##### `parentOrderMap.fulfillmentWarning[]`（父订单）

| 值 | 说明 |
|----|------|
| `SUGGEST_SIGNATURE_ON_DELIVERY` | 建议购买签收服务 |
| `CONFIRMED_CHANGED_ADDRESS` | 地址已变更并确认，建议重新拉单获取最新地址 |
| `RESTRICT_FEDEX_SELF_SHIPPING` | 限制使用 FedEx 运单号确认发货 |
| `RESTRICT_USPS_SELF_SHIPPING` | 限制使用 USPS 运单号确认发货 |
| `RESTRICT_SELF_SHIPPING` | 限制使用运单号确认发货 |
| `BLOCK_LOGISTICS_PROVIDERS_{Name1,Name2,...}` | 买家屏蔽部分物流商（名称在响应中展开） |
| `REQUIRES_CUSTOMER_PICKUP` | 仅支持买家自提履约 |

#### `orderList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| orderSn | STRING | 子订单号 |
| quantity | INTEGER | 卖家需履约数量：`quantity = originalOrderQuantity - canceledQuantityBeforeShipment` |
| canceledQuantityBeforeShipment | INTEGER | 发货前取消数量 |
| originalOrderQuantity | INTEGER | 原始下单数量 |
| goodsId | LONG | 商品 ID |
| skuId | LONG | SKU ID；**仅 LOCAL 卖家有效，非 SEMI** |
| spec | STRING | 买家可见规格描述 |
| originalSpecName | STRING | 卖家可见规格描述；**确认时间在近 6 个月内**的订单建议填写 |
| thumbUrl | STRING | 缩略图 URL |
| goodsName | STRING | 买家可见商品名称 |
| originalGoodsName | STRING | 卖家可见商品名称；**确认时间在近 6 个月内**的订单建议填写 |
| orderStatus | INTEGER | 子订单状态：`1` PENDING；`2` UN_SHIPPING；`3` CANCELED；`4` SHIPPED；`41` PARTIALLY_SHIPPED；`5` DELIVERED；`51` PARTIALLY_DELIVERED |
| productList | OBJECT[] | 商品 SKU 信息；**仅 SEMI 卖家有效，非 LOCAL** |
| packageAbnormalTypeList | STRING[] | 发货后物流异常类型，见下表（含 `SIGNED_BUT_UNRECEIVED_TASK`） |
| orderLabel | OBJECT[] | 子订单标签 |
| fulfillmentWarning | STRING[] | 子订单履约提示，见下表 |
| fulfillmentType | STRING | `fulfillBySeller` / `fulfillByCooperativeWarehouse` |
| inventoryDeductionWarehouseId | STRING | 库存扣减仓库 ID |
| inventoryDeductionWarehouseName | STRING | 库存扣减仓库名称 |
| orderPaymentType | STRING | `COD`、`PPD` |
| isCancelledDuringPending | BOOLEAN | 订单是否在待处理阶段全部取消 |
| earliestTimeBuyShippingLabel | INTEGER | 仅在此时间之后可购买面单 |
| earliestTimeGetShippingDocument | INTEGER | 仅在此时间之后可获取发货文件 |
| orderShippingTime | INTEGER | 子订单发货时间；含未发货/延迟包裹时可能为 `null` |
| isShipmentConsolidatedByMainMall | BOOLEAN | 主站合并发货标记，同 `parentOrderMap` |
| orderCreateTime | INTEGER | 子订单创建时间 |
| qualificationUploadEndTime | LONG | 订单资质文件上传截止时间 |

##### `productList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| productId | LONG | 商品 ID |
| productSkuId | LONG | 商品变体的 SKU ID |
| soldFactor | LONG | 商品数量与件数换算因子 |
| extCode | STRING | 货号 |

##### `orderList[].packageAbnormalTypeList[]`（出参，比入参多一项）

| 值 | 说明 |
|----|------|
| `WRONG_SHIPPING_ADDRESS` | 收货地址错误 |
| `SUSPECTED_ERROR_PROVIDER` | 疑似承运商异常 |
| `NO_TRACK` | 无轨迹 |
| `TRACK_TOO_EARLY` | 轨迹过早 |
| `OVERTIME_COLLECTION` | 揽收超时 |
| `TRACK_COLLECT_FAIL` | 揽收失败 |
| `SIGNED_BUT_UNRECEIVED_TASK` | 已签收但未收货任务 |

##### `orderList[].orderLabel[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| name | STRING | 标签名，如 `customized_products`、`pre_sale_order`、`made_to_order` 等 |
| value | INTEGER | `0` 无标签，`1` 有标签；BBC 订单需结合 `is_US_to_CA_BBC` 判断 |

##### `orderList[].fulfillmentWarning[]`

| 值 | 说明 |
|----|------|
| `SAVE_SN_INFORMATION_FOR_RETURN` | 建议保存 SN 便于退货鉴真 |
| `REQUIRES_AUTHENTICATION_REPORT_SUBMISSION` | 须在卖家中心提交鉴定报告，超时自动取消并可能处罚 |
| `REQUIRES_AGE_VERIFICATION` | 建议购买签收人年龄验证服务 |
| `SPECIFIC_LOGISTICS_REQUIRED` | 须选择指定物流履约 |
| `REQUIRES_CUSTOMER_PICKUP` | 仅支持买家自提 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 表示参数或 LinkFox Token 无效，核对参数与认证；`code=1003` 表示转发失败，核对 Temu token、用途、IP 白名单与网络。
- Temu 业务结果以 `body` 中的 `success`、`errorCode`、`errorMsg` 判断；`success=false` 时按上游错误说明处理。保留原始错误，不补造业务结果或未知响应码。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.order.list.v2.get",
  "params": {
    "request": {
      "pageNumber": 1,
      "pageSize": 20,
      "parentOrderStatus": 2
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
  "skillName": "linkfox-temu-order-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
