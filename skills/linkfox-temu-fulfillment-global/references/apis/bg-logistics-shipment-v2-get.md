# 查询发货信息 V2 接口说明

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

## 接口：查询发货信息 V2（bg.logistics.shipment.v2.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

**说明：** （卖家自发货后，按订单查询并核对已提交的发货/物流信息）。

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 `request`。建议使用 **`tokenPurpose=order-shipping`**。  
> 通常在 **`bg.logistics.shipment.v2.confirm`** 确认发货之后调用，用于核对运单号、包裹号、承运商及子包裹信息；`parentOrderSn` / `orderSn` 来自 **`linkfox-temu-order-global`**。

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

本接口 `type` 固定为 `bg.logistics.shipment.v2.get`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    ├── parentOrderSn    ← 必填
    └── orderSn          ← 必填
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |

> 官方表将顶层 **`request`** 标为选填（False），但 **`parentOrderSn`**、**`orderSn`** 均为必填；实际调用时**应传入完整 `request` 对象**。

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
    └── shipmentInfoDTO[]              ← shipment result（发货结果列表）
        ├── carrierId
        ├── carrierName
        ├── trackingNumber
        ├── skuId
        ├── quantity
        ├── packageSn
        ├── packageDeliveryType
        ├── trackingWarningLabel
        ├── cooperativeWarehouseDTO (OBJECT)   ← 合作仓履约时可能有值；卖家自发货时可能为空
        │   ├── warehouseProviderCode
        │   ├── warehouseProviderBrandName
        │   ├── warehouseCode
        │   └── warehouseName
        └── subPackageShipmentInfoList[]     ← subPackage Shipment result（子包裹发货结果）
            ├── carrierId
            ├── carrierName
            ├── packageSn
            ├── packageDeliveryType
            └── trackingNumber
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
| shipmentInfoDTO | OBJECT[] | shipment result（发货结果列表；每个元素对应一条主包裹维度的发货信息，可含子包裹列表） |

##### `shipmentInfoDTO[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| carrierId | LONG | Carrier ID（承运商 ID），与 **`bg.logistics.companies.get`** 返回的 **`logisticsServiceProviderId`** 相同 |
| carrierName | STRING | Carrier name（承运商名称）；与 `bg.logistics.companies.get` 中对应 ID 的名称一致（字段 **`logisticsServiceProviderName`**） |
| trackingNumber | STRING | Tracking Number（物流运单号）。**Y2 订单**：仅当 API 调用时间戳 **≥ `earliestTimeGetShippingDocument`** 时才会返回 `trackingNumber` |
| skuId | LONG | SKU 标识 |
| quantity | INTEGER | Quantity of the product（该包裹行对应的发货数量） |
| packageSn | STRING | Package number（包裹号） |
| packageDeliveryType | INTEGER | Package delivery type（包裹履约/发货渠道类型），见下表 |
| trackingWarningLabel | INTEGER | Tracking warning labels（轨迹预警标签），见下表 |
| cooperativeWarehouseDTO | OBJECT | 仅当该订单由**合作仓**履约时可能返回 DTO；**卖家自发货**时可能为空 |
| subPackageShipmentInfoList | OBJECT[] | subPackage Shipment result（子包裹发货结果列表；拆包/多包裹场景） |

###### `packageDeliveryType`（主包裹与子包裹共用）

| 值 | 说明 |
|----|------|
| `1` | Seller fulfills this order by **non-integrated** channel（卖家通过**非 Temu 集成**渠道履约） |
| `2` | Seller fulfills this order by **Temu-integrated** channel（卖家通过 **Temu 集成**渠道履约） |
| `3` | Cooperative warehouse fulfills this order by **non-integrated** channel（合作仓通过**非集成**渠道履约） |
| `4` | Cooperative warehouse fulfills this order by **Temu-integrated** channel（合作仓通过 **Temu 集成**渠道履约） |

###### `trackingWarningLabel`

| 值 | 说明 |
|----|------|
| `0` | No issues（无异常） |
| `1` | No tracking information（无轨迹信息） |
| `2` | Potentially incorrect（轨迹可能不正确） |
| `3` | The receiving address is inconsistent（收货地址不一致） |
| `4` | Over time collection（揽收超时） |

###### `cooperativeWarehouseDTO` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| warehouseProviderCode | STRING | Warehouse Provider Code（仓配服务商编码） |
| warehouseProviderBrandName | STRING | Warehouse Provider Brand Name（仓配服务商品牌名） |
| warehouseCode | STRING | warehouse Code（仓库编码） |
| warehouseName | STRING | Warehouse Name（仓库名称） |

> 卖家自发货（Self-Fulfilled）场景下，该对象常为 **空或不返回**；合作仓履约订单才需关注。

###### `subPackageShipmentInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| carrierId | LONG | Carrier ID，与 **`bg.logistics.companies.get`** 的 **`logisticsServiceProviderId`** 相同 |
| carrierName | STRING | Carrier name，与 `bg.logistics.companies.get` 中对应承运商名称一致 |
| packageSn | STRING | Package number（子包裹号） |
| packageDeliveryType | INTEGER | Package delivery type，枚举同主包裹 **`packageDeliveryType`** |
| trackingNumber | STRING | Tracking Number（子包裹运单号） |

> 调用成功时先判断 **`response.success === true`**，再解析 **`result.shipmentInfoDTO`**。若需核对平台侧订单状态，可配合 **`linkfox-temu-order-global`** 的 `bg.order.detail.v2.get`。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

- 业务错误按实际返回的 errorCode、errorMsg 解释，不预设独立错误码枚举。

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
  "type": "bg.logistics.shipment.v2.get",
  "params": {
    "request": {
      "parentOrderSn": "PO-20260101001",
      "orderSn": "O-20260101001-1"
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
