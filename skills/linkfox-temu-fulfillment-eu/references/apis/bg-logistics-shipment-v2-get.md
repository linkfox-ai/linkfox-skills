# Temu 欧洲站 查询发货信息 V2 接口说明

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

## 接口：查询发货信息 V2（bg.logistics.shipment.v2.get）

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

本操作的 `type` 固定为 `bg.logistics.shipment.v2.get`。脚本：`scripts/eu_self_fulfilled_logistics_shipment_v2_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家自发货后，按订单查询并核对已提交的发货/物流信息）。

> 通常在 **`bg.logistics.shipment.v2.confirm`** 确认发货之后调用，用于核对运单号、包裹号、承运商及子包裹信息；`parentOrderSn` / `orderSn` 来自 **`linkfox-temu-order-eu`**。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |

> 官方表将顶层 **`request`** 标为选填（False），但 **`parentOrderSn`**、**`orderSn`** 均为必填；实际调用时**应传入完整 `request` 对象**。

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
| shipmentInfoDTO | OBJECT[] | shipment result（发货结果列表；每个元素对应一条主包裹维度的发货信息，可含子包裹列表） |

##### `shipmentInfoDTO[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| carrierId | LONG | Carrier ID（承运商 ID），与 **`bg.logistics.companies.get`** 返回的 **`logisticsServiceProviderId`** 相同 |
| carrierName | STRING | Carrier name（承运商名称）；Partner 表述为与 `bg.logistics.companies.get` 中对应 ID 的名称一致（字段 **`logisticsServiceProviderName`**） |
| trackingNumber | STRING | Tracking Number（物流运单号）。**Y2 订单**：仅当 API 调用时间戳 **≥ `earliestTimeGetShippingDocument`** 时才会返回 `trackingNumber` |
| skuId | LONG | SKU 标识（SKU ID） |
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

> 调用成功时先判断 **`response.success === true`**，再解析 **`result.shipmentInfoDTO`**。若需核对平台侧订单状态，可配合 **`linkfox-temu-order-eu`** 的 `bg.order.detail.v2.get`。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

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
  "type": "bg.logistics.shipment.v2.get",
  "params": {
    "request": {
      "parentOrderSn": "PO-20260101001",
      "orderSn": "O-20260101001-1"
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
