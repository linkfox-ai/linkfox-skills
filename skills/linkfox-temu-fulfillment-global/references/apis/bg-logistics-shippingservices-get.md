# 查询可用物流渠道 接口说明

[接口导航与运行约定](../api.md)

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

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

**说明：** （卖家根据包裹尺寸与重量查询可用物流承运商/渠道，用于 Buy-Shipping 购标前选渠道与估价。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 `request`。建议使用 **`tokenPurpose=order-shipping`**。  
> **前置依赖：** `warehouseId` 来自 **`bg.logistics.warehouse.list.get`**；`parentOrderSn` / `orderSn` 来自 **`linkfox-temu-order-global`**。购标下一步通常使用返回的 **`channelId`**、**`shipLogisticsType`** 等调用 **`bg.logistics.shipment.create`**。

**限流：** AppKey 100 次 / 1 秒（Partner Rate Limiting Rules）。

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能为 `global`；Global 业务脚本默认此值，不能因上游主机相同而改用 US/EU 店铺令牌。 |
| managementType | string | 是 | 本技能业务为 `semi-managed`，Global 业务脚本默认此值。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；HTTP 请求必须携带。脚本可从本地 storeKey 解析后填入。 |
| storeKey | string | 仅脚本，与 accessToken 二选一 | 本地令牌键；脚本按 site、managementType、tokenPurpose 解析，不将此键发送给网关。 |
| tokenPurpose | string | 否，仅脚本 | 本技能默认 `order-shipping`，用于选择本地令牌，不进入网关 Body。 |
| type | string | 是 | 本接口的操作标识，见下方。专用脚本固定该值，通用代理须传入。 |
| params | object | 否 | 原样转发的业务参数；本接口字段见下方。 |
| params.request | OBJECT | 否（官方顶层） | Temu Request 表标为选填；包含必填子字段或接口要求时须提供完整对象。 |

#### 脚本 JSON 与 CLI

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥兼容别名，按此顺序优先于环境变量；仅用于请求头，不作为业务参数。 |
| params | object | 否 | 显式提供对象时优先转发该对象；否则 Global 脚本将非保留顶层字段作为 params，包括 request。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装调用公共 run 时始终附加；不读取或写入响应缓存。 |

保留键为 token、linkfoxToken、linkfox_token、accessToken、storeKey、site、managementType、tokenPurpose、type、params。通用入口 `temu_proxy.py` 只接受显式 params 对象；Global 入口兼容顶层业务字段。认证、本地令牌与输出约定见 [运行约定](../api.md#运行约定)。

本接口 `type` 固定为 `bg.logistics.shippingservices.get`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    ├── warehouseId                 ← 必填
    ├── orderSnList[]               ← 选填（与 shipOrderInfoList 二选一，且至少传一种）
    ├── shipOrderInfoList[]         ← 选填
    │   ├── parentOrderSn
    │   ├── orderSn
    │   └── quantity
    ├── weight                      ← 必填
    ├── weightUnit                  ← 必填
    ├── extendWeight                ← 选填
    ├── extendWeightUnit            ← 选填
    ├── length                      ← 必填
    ├── width                       ← 必填
    ├── height                      ← 必填
    ├── dimensionUnit               ← 必填
    └── signatureOnDelivery         ← 选填
```

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

> Partner Request 表中 `shipOrderInfoList` 子行在导出 HTML 中未展开；下列字段来自 **Request Example** 与错误码说明，与自发货 **`orderSendInfoList`** 结构一致。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |
| quantity | INTEGER | **是** | Quantity of the product（本行对应子订单在包裹中的商品数量） |

### 响应结构

#### LinkFox 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断，不能把 0 或 false 视为空。 |
| errmsg | string | 若返回，保留完整网关错误消息。 |
| code | integer | 网关错误码：1002 为参数或 LinkFox Token 无效，1003 为转发失败；不替代外层 HTTP 与 errcode 判断。 |
| body | string | 原始 Temu JSON 字符串，保留原值。 |
| temuBody | object / array / scalar | 脚本仅在非空 body 可解析为 JSON 时添加；不强制改写其结构，解析失败仍保留 body。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |

以下为 body 解析后的 Temu 业务结构；如存在 response 包装，读取其内对象，否则读取根对象。

| 字段 | 类型 | 说明 |
|------|------|------|
| response | OBJECT | Partner 表的 Temu 响应包装；实际响应可能直接使用根对象，不能假定每次都有此层。 |

```text
response
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)
    ├── onlineChannelDtoList[] (OBJECT[])      ← 可用渠道
    │   ├── estimatedText
    │   ├── estimatedCurrencyCode
    │   ├── channelRules
    │   ├── signServiceName
    │   ├── infoNeeded[]
    │   ├── shipCompanyId
    │   ├── pickupRules
    │   ├── availablePickupTimeSlotList[]
    │   │   ├── pickupStartTime
    │   │   └── pickupEndTime
    │   ├── supportInterlineShipping
    │   ├── interlineChannelInfoList[]
    │   │   ├── shipStageType
    │   │   ├── shipLogisticsType
    │   │   ├── shippingCompanyName
    │   │   ├── channelId
    │   │   └── shipCompanyId
    │   ├── shipLogisticsType
    │   ├── signServiceId
    │   ├── shippingCompanyName
    │   ├── estimatedAmount
    │   ├── channelId
    │   └── payWayCode
    └── unavailableChannelDtoList[] (OBJECT[]) ← 不可用渠道
        ├── estimatedText
        ├── unavailableReason
        ├── supportInterlineShipping
        ├── shipLogisticsType
        ├── shippingCompanyName
        ├── channelId
        ├── shipCompanyId
        └── unavailableInterlineChannelList[]
            ├── shipStageType
            ├── shipLogisticsType
            ├── shippingCompanyName
            ├── channelId
            └── shipCompanyId
```

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

> Partner Response 表中 `result` 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **Response Example**，说明结合字段语义与 Buy-Shipping 流程整理。若 Partner 在线文档有补充枚举，以在线表为准。

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

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

| 错误码 | 错误信息 | 处理建议 |
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
| 120011072 | The request area is incorrect... US / global | 请求区域须与店铺一致；本技能为 global，美国订单使用 US 对应技能 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "global",
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
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
