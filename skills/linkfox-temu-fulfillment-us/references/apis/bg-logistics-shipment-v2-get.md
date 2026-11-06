# 查询发货信息 V2 接口说明

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

**操作标识**：`type=bg.logistics.shipment.v2.get`；**对应脚本**：`scripts/us_self_fulfilled_logistics_shipment_v2_get.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=38e79b35d2cb463d85619c1c786dd303（`sub_menu_code` 以 Partner 后台该接口页为准）

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

> 通常在 **`bg.logistics.shipment.v2.confirm`** 确认发货之后调用，用于核对运单号、包裹号、承运商及子包裹信息；`parentOrderSn` / `orderSn` 来自 **`linkfox-temu-order-us`**。

（卖家自发货后，按订单查询并核对已提交的发货/物流信息）

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |

> 官方表将顶层 **`request`** 标为选填（False），但 **`parentOrderSn`**、**`orderSn`** 均为必填；实际调用时**应传入完整 `request` 对象**。

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
| carrierName | STRING | Carrier name（承运商名称）；Partner 描述为与 `bg.logistics.companies.get` 中对应 ID 的名称一致（字段 **`logisticsServiceProviderName`**） |
| trackingNumber | STRING | Tracking Number（物流运单号）。**Y2 订单**：仅当 API 调用时间戳 **≥ `earliestTimeGetShippingDocument`** 时才会返回 `trackingNumber` |
| skuId | LONG | SKU ID |
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

> 调用成功时先判断 **`response.success === true`**，再解析 **`result.shipmentInfoDTO`**。若需核对平台侧订单状态，可配合 **`linkfox-temu-order-us`** 的 `bg.order.detail.v2.get`。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

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
  "skillName": "linkfox-temu-fulfillment-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
