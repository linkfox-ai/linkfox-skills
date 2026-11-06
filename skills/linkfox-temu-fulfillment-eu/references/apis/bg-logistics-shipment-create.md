# Temu 欧洲站 在线下单购标 接口说明

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

## 接口：在线下单购标（bg.logistics.shipment.create）

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

本操作的 `type` 固定为 `bg.logistics.shipment.create`。脚本：`scripts/eu_buy_shipping_logistics_shipment_create.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家在线向 Temu 集成承运商下单购标，创建包裹并获取 **packageSn**；是 Buy-Shipping 购标核心接口。）

> **前置依赖：** `warehouseId` 来自 **`bg.logistics.warehouse.list.get`**；`channelId` / `shipCompanyId` / `shipLogisticsType` / `signServiceId` 等来自 **`bg.logistics.shippingservices.get`** 或 **`temu.logistics.shiplogisticstype.get`**；`parentOrderSn` / `orderSn` / `quantity` 来自 **`linkfox-temu-order-eu`**。
> **异步说明：** 部分场景下单为异步处理；若返回成功但无运单，请用 [**`bg.logistics.shipment.result.get`**](./bg-logistics-shipment-result-get.md) 按 **`packageSnList`** 查询结果（错误码 `120012013`）。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sendType | INTEGER | **是** | SendType（发货方式），见下表 |
| sendRequestList | OBJECT[] | 否* | Package List Information（包裹列表信息；购标时**须传**至少一个包裹） |
| shipLater | BOOLEAN | 否 | Ship Later（是否稍后发货），见下表 |
| shipLaterLimitTime | STRING | 否 | 稍后发货截止时间（小时数，字符串形式），见下表 |

\* Partner 请求表将 **`sendRequestList`** 标为选填（False），但购标业务**必须**传入有效包裹明细。

##### `sendType`

| 值 | 说明 |
|----|------|
| `0` | All the products in **one parent order** are shipped in **one package** with **one tracking number**（同一父订单全部商品，一个包裹、一个运单号） |
| `1` | **Partial** products in one parent order are shipped in **multiple packages** with multiple tracking numbers; **all products in that parent order must be submitted in one API call**（同一父订单部分商品拆多包裹；该父订单下所有待发商品须在一次调用中全部提交） |
| `2` | All the products in **multiple parent orders** are shipped in **one package** with **one tracking number**（多个父订单合并为一个包裹、一个运单号） |

##### `shipLater`

| 值 | 说明 |
|----|------|
| `true` | Apply to create the package and tracking numbers from Temu-integrated carriers online; mark this package as **「ship later」**（在线购标并创建运单，包裹标记为稍后发货）。带 **「Y2_advance_sale」** 标签的订单购标时**必须**设为 `true`（错误码 `120015534`） |
| `false` | Apply to create the package and tracking numbers online, **ship the package immediately** and mark as shipped（在线购标、创建运单并立即发货）。**COD 订单**不允许 `shipLater=true`（错误码 `120011053`） |

##### `shipLaterLimitTime`

| 订单标签 | 可选值（小时，字符串） |
|----------|------------------------|
| **无** `Y2_advance_sale` 标签 | `24`, `48`, `72`, `96`, `120` |
| **有** `Y2_advance_sale` 标签 | `144`, `168`, `192`, `216`, `240`, `264`, `288`, `312`, `336`, `360` |

> 无效枚举将报错 `120015532`。与 **`shipLater=true`** 配合使用，表示稍后发货的截止时间。

##### `sendRequestList[]` 元素字段

> Partner 请求表中 `sendRequestList` 子行在导出 HTML 中为折叠状态；下列字段、类型与说明来自 **请求表**（顶层）、**请求示例**、**响应示例** 关联字段及 Partner **业务错误码** 表。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouseId | STRING | **是** | Warehouse ID（发货仓库 ID；来自 **`bg.logistics.warehouse.list.get`** 的 **`warehouseId`**） |
| weight | STRING | **是** | 包裹重量。美国本地：整数**磅**写在 **`weight`**，小数/盎司部分写在 **`extendWeight`**（单位 **`oz`**）；须为整数时见错误码 `120015521` |
| weightUnit | STRING | **是** | 重量单位。美国包裹：**`lb`**；其他国家：**`kg`** |
| extendWeight | STRING | 否 | 扩展重量（美国本地订单的小数/盎司部分） |
| extendWeightUnit | STRING | 否 | 扩展重量单位。美国本地：**`oz`** |
| length | STRING | **是** | 包裹长度，保留两位小数 |
| width | STRING | **是** | 包裹宽度，保留两位小数 |
| height | STRING | **是** | 包裹高度，保留两位小数 |
| dimensionUnit | STRING | **是** | 尺寸单位。美国：**`in`**；其他国家：**`cm`** |
| shipCompanyId | INTEGER / LONG | **是** | Shipping company ID（物流公司 ID；与 **`bg.logistics.shippingservices.get`** 返回的 **`shipCompanyId`** 一致） |
| channelId | INTEGER / LONG | 条件 | Channel ID（物流渠道 ID；与 **`bg.logistics.shippingservices.get`** 返回的 **`channelId`** 一致）。与 **`shipLogisticsType`** **二选一**作为履约方式（错误码 `120015032`） |
| shipLogisticsType | STRING | 条件 | Ship logistics type（物流类型标识；来自 **`temu.logistics.shiplogisticstype.get`** 或查价返回）。选定后 Temu 可自动匹配推荐 **`channelId`**。与 **`channelId`** **二选一** |
| signServiceId | INTEGER | 否 | Signature service ID（签收/签名服务 ID；来自查价 **`onlineChannelDtoList[].signServiceId`**） |
| pickupStartTime | INTEGER | 条件 | Pickup window start time（预约上门揽收开始时间；**需要预约揽收的渠道**必填，见 **`pickupRules`** / **`availablePickupTimeSlotList`**） |
| pickupEndTime | INTEGER | 条件 | Pickup window end time（预约上门揽收结束时间；须晚于 **`pickupStartTime`**） |
| orderSendInfoList | OBJECT[] | **是** | Product list in this package（本包裹内要发货的商品行） |
| confirmAcceptance | STRING[] | 否 | Confirmation matters for this shipment（本批发货需确认的异常/预警事项），见下表 |
| splitSubPackage | BOOLEAN | 否 | 是否为**单件 SKU 拆多包裹**（`true`：单件 SKU 多包裹；`false`/不传：否）。为 `true` 时 **`quantity` 须为 1**（`120011045`），且须传 **`sendSubRequestList`** |
| sendSubRequestList | OBJECT[] | 条件 | Attached sub-packages for single-SKU multi-package scenario（单件 SKU 多包裹时的**附属包裹**列表；**最多 10 个**，`120011044`）。**COD 订单**不允许（`120011051`） |
| interlineShipCompanyList | OBJECT[] | 条件 | Interline / split-channel shipping legs（联运/分段渠道信息；使用分段渠道时**必填**，`120011111`） |
| cooperativeWarehouseShipment | BOOLEAN | 否 | Whether fulfillment uses **cooperative warehouse** mode（合作仓发货；部分渠道强制合作仓，`120018085`） |
| uspsMailingDateOffset | INTEGER | 条件 | USPS mailing date offset（USPS 邮寄日期偏移；部分 USPS 渠道禁止为 `0`，`120018086`） |
| autoConfirmAfterPickup | BOOLEAN | 否 | Auto-confirm shipment after pickup（揽收后自动确认发货） |

###### `orderSendInfoList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号）；每项**不可缺失**（`120011113`） |
| goodsId | LONG | **是** | Goods ID（商品 ID） |
| skuId | LONG | **是** | SKU 标识（SKU ID） |
| quantity | INTEGER | **是** | Quantity of the product（本行发货数量；**splitSubPackage=true** 时须为 1） |

###### `confirmAcceptance[]` 枚举值

| 值 | 说明 |
|----|------|
| `DENY_CANCELLATION` | Reject the cancellation request and proceed with shipment（拒绝取消申请后继续发货；订单存在待处理取消时，`120012030`） |
| `DENY_ADDRESS_CHANGE` | Reject the address change request and proceed（拒绝改地址申请后继续发货；`120012023`） |
| `DENY_PARENT_RISK_WARNING` | Reject/acknowledge parent order risk warning and proceed（确认父订单风控预警后继续发货；`120012031` / `120012061`） |
| `SUCCESSFUL_RETRY` | Confirm retry after a previous successful call（前次下 call 已成功后的再次请求确认） |
| `NO_DELIVERY_ON_SATURDAY` | Confirm Saturday non-delivery is acceptable（确认允许周六不派送） |

> 仅当订单存在对应待处理事项且商家选择继续发货时传入。

###### `sendSubRequestList[]` 元素字段

> 单件 SKU 拆多包裹时，主包裹 + 附属包裹共同完成发货；附属包裹**不含** `orderSendInfoList`（商品行在主包裹 **`sendRequestList`** 元素上）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouseId | STRING | **是** | Warehouse ID（附属包裹发货仓库） |
| weight | STRING | **是** | 包裹重量 |
| weightUnit | STRING | **是** | 重量单位（美国 **`lb`**） |
| extendWeight | STRING | 否 | 扩展重量 |
| extendWeightUnit | STRING | 否 | 扩展重量单位（美国 **`oz`**） |
| length | STRING | **是** | 包裹长度 |
| width | STRING | **是** | 包裹宽度 |
| height | STRING | **是** | 包裹高度 |
| dimensionUnit | STRING | **是** | 尺寸单位（美国 **`in`**） |
| shipCompanyId | INTEGER / LONG | **是** | 物流公司 ID |
| channelId | INTEGER / LONG | **是** | 物流渠道 ID |
| shipLogisticsType | STRING | 否 | Ship logistics type（若渠道按类型履约） |
| signServiceId | INTEGER | 否 | 签名或签收服务 ID |
| pickupStartTime | INTEGER | 条件 | 上门揽收开始时间 |
| pickupEndTime | INTEGER | 条件 | 上门揽收结束时间 |
| interlineShipCompanyList | OBJECT[] | 条件 | Interline legs（结构同主包裹） |
| confirmAcceptance | STRING[] | 否 | 发货确认事项 |

###### `interlineShipCompanyList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shipStageType | STRING | **是** | Shipping stage type（运输段类型，如首程/末程；与 **`bg.logistics.shippingservices.get`** 的 **`interlineChannelInfoList[].shipStageType`** 一致） |
| shipLogisticsType | STRING | **是** | Logistics type for this stage（该段物流类型标识） |
| shipCompanyId | INTEGER / LONG | **是** | 当前运输段的物流公司 ID |
| channelId | INTEGER / LONG | **是** | 当前运输段的物流渠道 ID |

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

> Partner 响应表中 `result` 子行在导出 HTML 中为折叠状态；下列字段来自 **响应示例** 与购标后续流程约定。

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSnList | STRING[] | Package SN list（本次下单创建的**包裹号**列表；用于 **`bg.logistics.shipment.result.get`** 查询下单结果、**`bg.logistics.shipment.document.get`** 拉取面单） |
| warningMessage | STRING[] | Warning messages（警告信息列表；非阻塞提示，购标仍可能成功） |
| shipLaterLimitTime | STRING | Ship-later limit time returned when applicable（若请求 **`shipLater=true`**，可能返回确认的稍后发货截止时间/小时配置） |

> 调用成功时先判断 **`response.success === true`**，再使用 **`result.packageSnList`** 走结果查询与面单下载。若 **`warningMessage`** 非空，建议记录并人工确认是否影响发货。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

> 完整错误码以 Partner 文档 **业务错误码** 表为准（导出 HTML 含 70+ 条）。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120012013 | Already requested by Temu integrated logistics; check via result.get | 调用 **`bg.logistics.shipment.result.get`** 确认是否已成功 |
| 120015032 | Choose channelId **or** shipLogisticsType | 二选一履约，勿同时乱填 |
| 120011111 | Split channel requires **interlineShipCompanyList** | 补全联运分段渠道 |
| 120011110 | No eligible channelId | 核对渠道参数或重新 **shippingservices.get** |
| 120011112 | Missing **shipCompanyId** | 补全物流公司 ID |
| 120011113 | **orderSendInfoList** missing orderSn | 每项商品行须有 **orderSn** |
| 120013002 | Item quantity does not match | 核对 **quantity** 与订单待发数量 |
| 120012015 | Combined delivery: addresses differ | 合并发货时地址须一致 |
| 120011053 | COD: shipLater must be FALSE | COD 勿稍后发货 |
| 120011051 | COD: no sub-packages | COD 勿拆子包裹 |
| 120011057 / 120018028 | COD vs PPD cannot mix in one request | 勿混 COD 与预付订单 |
| 120012037 | Before earliestTimeBuyShippingLabel | 未到可购标时间 |
| 120015534 | Y2_advance_sale: shipLater=true required | 预售标签订单须稍后发货 |
| 120015532 | shipLaterLimitTime invalid | 按订单标签选合法小时数 |
| 120015533 | Y2_advance_sale cannot mix with normal orders | 勿混预售与普通订单 |
| 120011043 | Missing **sendSubRequestList** | splitSubPackage 场景补子包裹 |
| 120011044 | Max 10 attached packages | 子包裹 ≤ 10 |
| 120011045 | splitSubPackage: quantity must be 1 | 拆包场景数量为 1 |
| 120018084 | Cooperative warehouse: no split sub package | 合作仓不支持拆子包裹 |
| 120018086 | USPSMailingDateOffset cannot be 0 | 调整 USPS 偏移 |
| 120019009 / 120019019 | Invalid pickup time | 按 **pickupRules** 重选时段 |
| 120015507 | Wrong package information | 检查重量尺寸单位 |
| 120015521 | Weight should be integer (US) | 美国 **weight** 用整数磅 |
| 120011006 | warehouseId invalid | 用 **warehouse.list.get** 有效 ID |
| 120012007 / 120012016 | parentOrder/order invalid | 核对父子订单 |
| 120015528 | COD orders: Temu Label only | COD 仅 Temu 面单 |
| 120018063 | Funds reserved; Buy shipping disabled | 账户资金受限 |
| 120012061 / 120012031 | Risk control alert on parent order | 评估是否继续发货 |

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
  "type": "bg.logistics.shipment.create",
  "params": {
    "request": {
      "sendType": 0,
      "shipLater": false,
      "sendRequestList": [
        {
          "warehouseId": "WH-001",
          "length": "12.00",
          "width": "8.00",
          "height": "4.00",
          "dimensionUnit": "in",
          "weight": "2",
          "weightUnit": "lb",
          "extendWeight": "8",
          "extendWeightUnit": "oz",
          "shipCompanyId": 314439762,
          "channelId": 19409681780736,
          "orderSendInfoList": [
            {
              "parentOrderSn": "PO-20260101001",
              "orderSn": "O-20260101001-1",
              "goodsId": 6017592186252451,
              "skuId": 281474976920151,
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
