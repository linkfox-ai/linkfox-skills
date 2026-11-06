# 确认发货 V2 接口说明

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

## 接口：确认发货 V2（bg.logistics.shipment.v2.confirm）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

**说明：** （同步并回传订单履约/发货信息，将订单状态从待发货切换为已发货）。

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 `request`。建议使用 **`tokenPurpose=order-shipping`**。  
> **前置依赖：** `carrierId` 与 `bg.logistics.companies.get` 返回的 **`logisticsServiceProviderId`** 相同；`selfShippingWarehouseId` 来自 **`linkfox-temu-fulfillment-global`** 的 **`bg.logistics.warehouse.list.get`**（`warehouseId`）。订单号来自 **`linkfox-temu-order-global`**（如 `bg.order.detail.v2.get`）。

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

本接口 `type` 固定为 `bg.logistics.shipment.v2.confirm`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    ├── sendType                    ← 必填
    └── sendRequestList[]           ← 必填（Shipment package details）
        ├── carrierId               ← 必填
        ├── trackingNumber          ← 必填
        ├── selfShippingWarehouseId ← 必填
        ├── orderSendInfoList[]     ← 必填（本包裹内商品行）
        │   ├── parentOrderSn       ← 必填
        │   ├── orderSn             ← 必填
        │   ├── goodsId             ← 选填
        │   ├── skuId               ← 选填
        │   └── quantity            ← 必填
        ├── confirmAcceptance[]     ← 选填
        └── subSendRequests[]       ← 选填（子包裹/子运单）
            ├── carrierId           ← 必填（当使用 subSendRequests 时）
            ├── trackingNumber      ← 必填
            └── selfShippingWarehouseId ← 必填
```

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
| selfShippingWarehouseId | STRING | **是** | The shipment warehouse ID（自发货仓库 ID），通过 **`linkfox-temu-fulfillment-global`** 的 **`bg.logistics.warehouse.list.get`** 返回的 **`warehouseId`** 获取 |
| orderSendInfoList | OBJECT[] | **是** | Product List in this package（本包裹内要发货的商品行列表） |
| confirmAcceptance | STRING[] | 否 | Confirmation matters for this shipment（本批发货需确认的异常/预警事项），见下表 |
| subSendRequests | OBJECT[] | 否 | Sub Send Requests（子发货请求；用于一单多包裹等场景下的子运单明细） |

###### `orderSendInfoList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |
| goodsId | LONG | 否 | Goods ID（商品 ID） |
| skuId | LONG | 否 | SKU 标识 |
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
    ├── assistantAgreementText
    └── warningMessage[]
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
| assistantAgreementText | STRING | Enables intelligent trajectory assistant to detect and correct potential mistakes in carrier entries（智能轨迹助手相关提示文案，用于检测并纠正承运商录入错误） |
| warningMessage | STRING[] | Provides relevant prompts related to the current shipping request（与本次发货请求相关的提示/警告信息列表） |

> 调用成功时先判断 **`response.success === true`**，再查看 **`result.warningMessage`** 是否有需向用户展示的警告；发货是否最终在平台侧生效，建议再调 **`linkfox-temu-order-global`** 的 `bg.order.detail.v2.get` 核对订单状态。

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
  "skillName": "linkfox-temu-fulfillment-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
