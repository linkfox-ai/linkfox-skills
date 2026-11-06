# Temu 欧洲站 查询可用物流渠道 接口说明

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

## 接口：查询可用物流渠道（bg.logistics.shippingservices.get）

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

本操作的 `type` 固定为 `bg.logistics.shippingservices.get`。脚本：`scripts/eu_buy_shipping_logistics_shippingservices_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家根据包裹尺寸与重量查询可用物流承运商/渠道，用于 Buy-Shipping 购标前选渠道与估价。）

> **前置依赖：** `warehouseId` 来自 **`bg.logistics.warehouse.list.get`**；`parentOrderSn` / `orderSn` 来自 **`linkfox-temu-order-eu`**。购标下一步通常使用返回的 **`channelId`**、**`shipLogisticsType`** 等调用 **`bg.logistics.shipment.create`**。

**限流：** AppKey 100 次 / 1 秒（Partner Rate Limiting Rules）。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouseId | STRING | **是** | Warehouse ID（仓库 ID；来自 **`bg.logistics.warehouse.list.get`** 的 **`warehouseId`**） |
| orderSnList | STRING[] | 否 | Product List in this package（本包裹内的子订单号列表） |
| shipOrderInfoList | OBJECT[] | 否 | Order Info List（订单信息列表；每项为父订单号 + 子订单号 + 数量组合） |
| weight | STRING | **是** | 包裹重量。美国本地订单：本字段填**整数**磅，小数部分通过 **`extendWeight`**（单位 **`oz`**）填写；非美国本地订单默认保留两位小数 |
| weightUnit | STRING | **是** | 重量单位。美国包裹为 **`lb`**，其他国家为 **`kg`** |
| extendWeight | STRING | 否 | 扩展重量（美国本地订单的小数/盎司部分；与 **`extendWeightUnit`**=`oz` 配合） |
| extendWeightUnit | STRING | 否 | 扩展重量单位。美国本地包裹为 **`oz`** |
| length | STRING | **是** | 包裹长度，须保留两位小数 |
| width | STRING | **是** | 包裹宽度，须保留两位小数 |
| height | STRING | **是** | 包裹高度，须保留两位小数 |
| dimensionUnit | STRING | **是** | 长宽高单位。美国为 **`in`**，其他国家为 **`cm`** |
| signatureOnDelivery | BOOLEAN | 否 | Is Signature Required for Delivery Confirmation?（是否需要签收确认/签名投递） |

##### `orderSnList` 与 `shipOrderInfoList` 互斥规则

| 规则 | 说明 |
|------|------|
| 二选一 | **`orderSnList`** 与 **`shipOrderInfoList`**（`<parentOrderSn, orderSn>` 列表）**只能传其中一种**（错误码 `120018070`） |
| 至少一种 | **`orderSnList`** 与 **`shipOrderInfoList`** **至少传一种**（错误码 `120018072`） |
| 父子匹配 | `shipOrderInfoList` 中的 **`orderSn`** 须属于对应 **`parentOrderSn`**（错误码 `120018071`） |

> 合并多父订单到一个包裹发货时，使用 **`shipOrderInfoList`** 并分别指定 **`parentOrderSn`** + **`orderSn`** + **`quantity`**；仅按子订单号列表传参时可使用 **`orderSnList`**。

##### `shipOrderInfoList[]` 元素字段

> Partner 请求表中 `shipOrderInfoList` 子行在导出 HTML 中未展开；下列字段来自 **请求示例** 与错误码说明，与自发货 **`orderSendInfoList`** 结构一致。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |
| quantity | INTEGER | **是** | Quantity of the product（本行对应子订单在包裹中的商品数量） |

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

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | result（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| onlineChannelDtoList | OBJECT[] | 当前包裹条件下**可用**的物流渠道列表（含估价、承运商、渠道 ID 等，供后续购标选用） |
| unavailableChannelDtoList | OBJECT[] | 当前条件下**不可用**的渠道列表及原因 |

##### `onlineChannelDtoList[]` 元素字段

> Partner 响应表中 `result` 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **响应示例**，说明结合字段语义与 Buy-Shipping 流程整理。若 Partner 在线文档有补充枚举，以在线表为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| estimatedText | STRING | Estimated delivery time text（预计送达/时效文案，展示用） |
| estimatedCurrencyCode | STRING | Currency code for **estimatedAmount**（预估运费币种代码，如 USD） |
| channelRules | STRING | Channel rules / constraints（渠道规则或限制说明文案） |
| signServiceName | STRING | Signature service name（签名/签收服务名称；与 **`signServiceId`** 对应） |
| infoNeeded | STRING[] | Additional information required from seller before using this channel（选用该渠道前需补充的信息项列表） |
| shipCompanyId | INTEGER | Shipping company ID（物流公司/承运商 ID） |
| pickupRules | STRING | Pickup rules description（上门揽收规则说明；需预约揽收时参考） |
| availablePickupTimeSlotList | OBJECT[] | Available pickup time slots（可预约揽收时间段列表） |
| supportInterlineShipping | BOOLEAN | Whether interline / multi-leg shipping is supported（是否支持联运/多段物流） |
| interlineChannelInfoList | OBJECT[] | Interline channel details when **supportInterlineShipping** is true（联运各段渠道信息） |
| shipLogisticsType | STRING | Ship logistics type identifier（物流类型标识；**`bg.logistics.shipment.create`** 等后续接口常需此字段） |
| signServiceId | INTEGER | Signature service ID（签名/签收服务 ID） |
| shippingCompanyName | STRING | Shipping company display name（物流公司/承运商名称） |
| estimatedAmount | STRING | Estimated shipping cost amount（预估运费金额，字符串形式，配合 **estimatedCurrencyCode**） |
| channelId | INTEGER | Channel ID（物流渠道 ID；购标 **`bg.logistics.shipment.create`** 时选用） |
| payWayCode | INTEGER | Payment method code for label purchase（面单支付方式编码） |

###### `onlineChannelDtoList[].availablePickupTimeSlotList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| pickupStartTime | INTEGER | Pickup window start time（揽收时段开始时间；Partner 示例为数值时间戳，具体精度以在线文档为准） |
| pickupEndTime | INTEGER | Pickup window end time（揽收时段结束时间） |

###### `onlineChannelDtoList[].interlineChannelInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| shipStageType | STRING | Shipping stage type（运输段类型，如首程/末程等；联运场景区分各段） |
| shipLogisticsType | STRING | Logistics type for this stage（该段的物流类型标识） |
| shippingCompanyName | STRING | Carrier name for this stage（该段承运商名称） |
| channelId | INTEGER | Channel ID for this stage（该段渠道 ID） |
| shipCompanyId | INTEGER | Shipping company ID for this stage（该段物流公司 ID） |

##### `unavailableChannelDtoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| estimatedText | STRING | Estimated delivery text if shown for unavailable channel（不可用渠道上展示的时效文案，若有） |
| unavailableReason | STRING | Reason the channel is unavailable（渠道不可用原因说明） |
| supportInterlineShipping | BOOLEAN | Whether this channel supports interline shipping（该渠道是否声明支持联运） |
| shipLogisticsType | STRING | Ship logistics type identifier（物流类型标识） |
| shippingCompanyName | STRING | Shipping company name（物流公司名称） |
| channelId | INTEGER | Channel ID（渠道 ID） |
| shipCompanyId | INTEGER | Shipping company ID（物流公司 ID） |
| unavailableInterlineChannelList | OBJECT[] | Unavailable interline sub-channels（不可用的联运子渠道列表） |

###### `unavailableChannelDtoList[].unavailableInterlineChannelList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| shipStageType | STRING | Shipping stage type（运输段类型） |
| shipLogisticsType | STRING | Logistics type for this stage（该段物流类型） |
| shippingCompanyName | STRING | Carrier name for this stage（该段承运商名称） |
| channelId | INTEGER | Channel ID for this stage（该段渠道 ID） |
| shipCompanyId | INTEGER | Shipping company ID for this stage（该段物流公司 ID） |

> 调用成功时先判断 **`response.success === true`**，在 **`onlineChannelDtoList`** 中选择 **`channelId`** / **`shipLogisticsType`** 等，再调用 **`bg.logistics.shipment.create`** 购标。若 **`unavailableChannelDtoList`** 非空，可根据 **`unavailableReason`** 调整包裹尺寸、重量、签收选项或仓库后重试。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120015507 | Wrong package {*} information. Try again. | 检查重量、尺寸、单位与仓库是否匹配 |
| 120012061 | The current parent order has a pending risk control alert... | 父订单存在风控预警，谨慎履约或走取消流程 |
| 120018070 | Only one of orderSnList or &lt;parentOrderSn, orderSn&gt;list can be passed in. | 不要同时传 **orderSnList** 与 **shipOrderInfoList** |
| 120018072 | At least one of orderSnList and &lt;parentOrderSn, orderSn&gt;list must be passed in. | 至少传 **orderSnList** 或 **shipOrderInfoList** 之一 |
| 120018071 | This orderSn does not exist under the specified parentOrderSn. | 核对父子订单号对应关系 |
| 120011015 | Incomplete warehouse details. Update in Seller Central... | 在卖家中心完善仓库信息 |
| 120015544 | Orders {*} need to sign on delivery. Please request the field "signatureOnDelivery" with "True". | 将 **signatureOnDelivery** 设为 **true** |
| 120011030 | Cooperative warehouse order fulfillment restricted. | 合作仓履约受限，检查仓授权状态 |
| 120013007 | Product sku sensitive query fail | SKU 敏感属性查询失败 |
| 120013008 / 120013009 | Order lacks necessary sensitive attributes. | 订单缺少必要敏感属性 |
| 120011047 | Not support local mall | 不支持 local mall 场景 |
| 120011006 | The parameter warehouseId is invalid. | 使用 **warehouse.list.get** 返回的有效 **warehouseId** |
| 120012007 / 120012016 | The parentOrder or Order is invalid... | 检查父/子订单是否存在且匹配 |
| 120015521 | The parameter Weight should be integer. | 美国本地订单 **weight** 须为整数 |
| 120011072 | The request area is incorrect... US / global | 核对站点与令牌区域；本技能使用 `site=eu`，勿因 US 示例自动切换站点 |

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
  "type": "bg.logistics.shippingservices.get",
  "params": {
    "request": {
      "warehouseId": "WH-001",
      "shipOrderInfoList": [
        {
          "parentOrderSn": "PO-20260101001",
          "orderSn": "O-20260101001-1",
          "quantity": 1
        }
      ],
      "weight": "2",
      "weightUnit": "lb",
      "extendWeight": "8",
      "extendWeightUnit": "oz",
      "length": "12.00",
      "width": "8.00",
      "height": "4.00",
      "dimensionUnit": "in",
      "signatureOnDelivery": false
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
