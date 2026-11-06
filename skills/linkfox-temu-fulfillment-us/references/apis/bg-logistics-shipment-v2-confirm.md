# 确认发货 V2 接口说明

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

## 接口：确认发货 V2（bg.logistics.shipment.v2.confirm）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=bg.logistics.shipment.v2.confirm`；**对应脚本**：`scripts/us_self_fulfilled_logistics_shipment_v2_confirm.py`。

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

> **前置依赖：** `carrierId` 与 `bg.logistics.companies.get` 返回的 **`logisticsServiceProviderId`** 相同；`selfShippingWarehouseId` 来自 **`linkfox-temu-fulfillment-us`** 的 **`bg.logistics.warehouse.list.get`**（`warehouseId`）。订单号来自 **`linkfox-temu-order-us`**（如 `bg.order.detail.v2.get`）。

（同步并回传订单履约/发货信息，将订单状态从待发货切换为已发货）

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sendType | INTEGER | **是** | SendType（发货方式），见下表 |
| sendRequestList | OBJECT[] | **是** | Shipment package details（发货包裹明细列表）；每个元素描述一个包裹及其运单、仓库、商品行 |

官方将外层 `request` 标为选填，但实际发货必须提供完整 `params.request`，包含 `sendType`、`sendRequestList` 及各必填子字段。

##### `sendType`

| 值 | 说明 |
|----|------|
| `0` | 同一 **父订单** 内全部商品，**一个包裹、一个运单号** 发货 |
| `1` | 同一 **父订单** 内**部分商品**分多个包裹、多个运单号发货；**该父订单下所有待发商品须在一次 API 调用中全部提交**（不可拆成多次 confirm 漏发） |
| `2` | **多个父订单** 的商品合并为 **一个包裹、一个运单号** 发货 |

##### `sendRequestList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| carrierId | LONG | **是** | Carrier ID（承运商 ID），与 **`bg.logistics.companies.get`** 返回的 **`logisticsServiceProviderId`** 相同 |
| trackingNumber | STRING | **是** | Tracking Number（物流运单号 / 跟踪号） |
| selfShippingWarehouseId | STRING | **是** | The shipment warehouse ID（自发货仓库 ID），通过 **`linkfox-temu-fulfillment-us`** 的 **`bg.logistics.warehouse.list.get`** 返回的 **`warehouseId`** 获取 |
| orderSendInfoList | OBJECT[] | **是** | Product List in this package（本包裹内要发货的商品行列表） |
| confirmAcceptance | STRING[] | 否 | Confirmation matters for this shipment（本批发货需确认的异常/预警事项），见下表 |
| subSendRequests | OBJECT[] | 否 | Sub Send Requests（子发货请求；用于一单多包裹等场景下的子运单明细） |

###### `orderSendInfoList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |
| goodsId | LONG | 否 | Goods ID（商品 ID） |
| skuId | LONG | 否 | SKU ID |
| quantity | INTEGER | **是** | Quantity of the product（本行发货数量） |

###### `confirmAcceptance[]` 枚举值

| 值 | 说明 |
|----|------|
| `DENY_CANCELLATION` | Reject the cancellation request for this order（拒绝该订单的取消申请后继续发货） |
| `DENY_ADDRESS_CHANGE` | Reject the address change request for this order（拒绝该订单的改地址申请后继续发货） |
| `DENY_PARENT_RISK_WARNING` | Reject the risk warning for this order（拒绝/确认父订单风险预警后继续发货） |

> 仅当订单存在对应待处理事项且商家选择「拒绝申请并继续发货」等场景时传入；无此类事项可省略。

###### `subSendRequests[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| carrierId | LONG | **是** | Logistics Company ID（子包裹承运商 ID） |
| trackingNumber | STRING | **是** | Waybill Number（子包裹运单号） |
| selfShippingWarehouseId | STRING | **是** | Self-Delivery Warehouse ID（子包裹自发货仓库 ID） |

> 使用 **`subSendRequests`** 时，父级 **`sendRequestList`** 元素仍须填写 **`orderSendInfoList`** 等；子项用于补充额外运单/仓库组合，具体与 **`sendType=1`** 等多包裹场景配合，以 Partner 文档与订单详情约束为准。

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
| assistantAgreementText | STRING | Enables intelligent trajectory assistant to detect and correct potential mistakes in carrier entries（智能轨迹助手相关提示文案，用于检测并纠正承运商录入错误） |
| warningMessage | STRING[] | Provides relevant prompts related to the current shipping request（与本次发货请求相关的提示/警告信息列表） |

> 调用成功时先判断 **`response.success === true`**，再查看 **`result.warningMessage`** 是否有需向用户展示的警告；发货是否最终在平台侧生效，建议再调 **`linkfox-temu-order-us`** 的 `bg.order.detail.v2.get` 核对订单状态。

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
  "type": "bg.logistics.shipment.v2.confirm",
  "params": {
    "request": {
      "sendType": 0,
      "sendRequestList": [
        {
          "carrierId": 123456789,
          "trackingNumber": "1Z999AA10123456784",
          "selfShippingWarehouseId": "WH-001",
          "orderSendInfoList": [
            {
              "parentOrderSn": "PO-xxx",
              "orderSn": "O-xxx",
              "goodsId": 987654321,
              "skuId": 111222333,
              "quantity": 1
            }
          ]
        }
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
  "skillName": "linkfox-temu-fulfillment-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
