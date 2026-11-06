# Temu 欧洲站 确认发货 V2 接口说明

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

## 接口：确认发货 V2（bg.logistics.shipment.v2.confirm）

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

本操作的 `type` 固定为 `bg.logistics.shipment.v2.confirm`。脚本：`scripts/eu_self_fulfilled_logistics_shipment_v2_confirm.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（同步并回传订单履约/发货信息，将订单状态从待发货切换为已发货）。

> **前置依赖：** `carrierId` 与 `bg.logistics.companies.get` 返回的 **`logisticsServiceProviderId`** 相同；`selfShippingWarehouseId` 来自 **`linkfox-temu-fulfillment-eu`** 的 **`bg.logistics.warehouse.list.get`**（`warehouseId`）。订单号来自 **`linkfox-temu-order-eu`**（如 `bg.order.detail.v2.get`）。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sendType | INTEGER | **是** | SendType（发货方式），见下表 |
| sendRequestList | OBJECT[] | **是** | Shipment package details（发货包裹明细列表）；每个元素描述一个包裹及其运单、仓库、商品行 |

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
| selfShippingWarehouseId | STRING | **是** | The shipment warehouse ID（自发货仓库 ID），通过 **`linkfox-temu-fulfillment-eu`** 的 **`bg.logistics.warehouse.list.get`** 返回的 **`warehouseId`** 获取 |
| orderSendInfoList | OBJECT[] | **是** | Product List in this package（本包裹内要发货的商品行列表） |
| confirmAcceptance | STRING[] | 否 | Confirmation matters for this shipment（本批发货需确认的异常/预警事项），见下表 |
| subSendRequests | OBJECT[] | 否 | Sub Send Requests（子发货请求；用于一单多包裹等场景下的子运单明细） |

###### `orderSendInfoList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |
| goodsId | LONG | 否 | Goods ID（商品 ID） |
| skuId | LONG | 否 | SKU 标识（SKU ID） |
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

> 官方表将顶层 **`request`** 标为选填（False），但 **`sendType`**、**`sendRequestList`** 及其子字段多为必填；实际调用时**应传入完整 `request` 对象**。

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
| assistantAgreementText | STRING | Enables intelligent trajectory assistant to detect and correct potential mistakes in carrier entries（智能轨迹助手相关提示文案，用于检测并纠正承运商录入错误） |
| warningMessage | STRING[] | Provides relevant prompts related to the current shipping request（与本次发货请求相关的提示/警告信息列表） |

> 调用成功时先判断 **`response.success === true`**，再查看 **`result.warningMessage`** 是否有需向用户展示的警告；发货是否最终在平台侧生效，建议再调 **`linkfox-temu-order-eu`** 的 `bg.order.detail.v2.get` 核对订单状态。

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
