# 在线下单购标 接口说明

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

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

**操作标识**：`type=bg.logistics.shipment.create`；**对应脚本**：`scripts/us_buy_shipping_logistics_shipment_create.py`。

**Partner 文档**：https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=1eadab72ed8041318604b163dd75cdac

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

> **前置依赖：** `warehouseId` 来自 **`bg.logistics.warehouse.list.get`**；`channelId` / `shipCompanyId` / `shipLogisticsType` / `signServiceId` 等来自 **`bg.logistics.shippingservices.get`** 或 **`temu.logistics.shiplogisticstype.get`**；`parentOrderSn` / `orderSn` / `quantity` 来自 **`linkfox-temu-order-us`**。
> **异步说明：** 部分场景下单为异步处理；若返回成功但无运单，请用 [**`bg.logistics.shipment.result.get`**](./bg-logistics-shipment-result-get.md) 按 **`packageSnList`** 查询结果（错误码 `120012013`）。

（卖家在线向 Temu 集成承运商下单购标，创建包裹并获取 **packageSn**；是 Buy-Shipping 购标核心接口。）

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sendType | INTEGER | **是** | SendType（发货方式），见下表 |
| sendRequestList | OBJECT[] | 否* | Package List Information（包裹列表信息；购标时**须传**至少一个包裹） |
| shipLater | BOOLEAN | 否 | Ship Later（是否稍后发货），见下表 |
| shipLaterLimitTime | STRING | 否 | 稍后发货截止时间（小时数，字符串形式），见下表 |

\* Partner Request 表将 **`sendRequestList`** 标为选填（False），但购标业务**必须**传入有效包裹明细。

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

> Partner Request 表中 `sendRequestList` 子行在导出 HTML 中为折叠状态；下列字段、类型与说明来自 **Request 表**（顶层）、**Request Example**、**Response Example** 关联字段及 Partner **Error Code** 表。

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
| skuId | LONG | **是** | SKU ID |
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
| shipCompanyId | INTEGER / LONG | **是** | Shipping company ID |
| channelId | INTEGER / LONG | **是** | Channel ID |
| shipLogisticsType | STRING | 否 | Ship logistics type（若渠道按类型履约） |
| signServiceId | INTEGER | 否 | Signature service ID |
| pickupStartTime | INTEGER | 条件 | Pickup start time |
| pickupEndTime | INTEGER | 条件 | Pickup end time |
| interlineShipCompanyList | OBJECT[] | 条件 | Interline legs（结构同主包裹） |
| confirmAcceptance | STRING[] | 否 | Confirmation matters |

###### `interlineShipCompanyList[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shipStageType | STRING | **是** | Shipping stage type（运输段类型，如首程/末程；与 **`bg.logistics.shippingservices.get`** 的 **`interlineChannelInfoList[].shipStageType`** 一致） |
| shipLogisticsType | STRING | **是** | Logistics type for this stage（该段物流类型标识） |
| shipCompanyId | INTEGER / LONG | **是** | Shipping company ID for this stage |
| channelId | INTEGER / LONG | **是** | Channel ID for this stage |

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

> Partner Response 表中 `result` 子行在导出 HTML 中为折叠状态；下列字段来自 **Response Example** 与购标后续流程约定。

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

- 外层正常响应后，先排除网关 `code=1002/1003`，再解析 `body`；以 Temu 对象的 `success`、`errorCode`、`errorMsg` 和本接口结果字段判断业务结果。`success=true` 不等于异步履约或预约已经完成。
- `1002`：修正参数与 LinkFox 密钥；`1003`：检查 Temu 令牌、用途、IP 白名单及转发错误。不自动重试写操作。

| 错误码 | 错误信息（Partner） | 处理建议 |
|---|---|---|
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
| 120011057 | COD vs PPD cannot mix in one request | 勿混 COD 与预付订单 |
| 120018028 | COD vs PPD cannot mix in one request | 勿混 COD 与预付订单 |
| 120012037 | Before earliestTimeBuyShippingLabel | 未到可购标时间 |
| 120015534 | Y2_advance_sale: shipLater=true required | 预售标签订单须稍后发货 |
| 120015532 | shipLaterLimitTime invalid | 按订单标签选合法小时数 |
| 120015533 | Y2_advance_sale cannot mix with normal orders | 勿混预售与普通订单 |
| 120011043 | Missing **sendSubRequestList** | splitSubPackage 场景补子包裹 |
| 120011044 | Max 10 attached packages | 子包裹 ≤ 10 |
| 120011045 | splitSubPackage: quantity must be 1 | 拆包场景数量为 1 |
| 120018084 | Cooperative warehouse: no split sub package | 合作仓不支持拆子包裹 |
| 120018086 | USPSMailingDateOffset cannot be 0 | 调整 USPS 偏移 |
| 120019009 | Invalid pickup time | 按 **pickupRules** 重选时段 |
| 120019019 | Invalid pickup time | 按 **pickupRules** 重选时段 |
| 120015507 | Wrong package information | 检查重量尺寸单位 |
| 120015521 | Weight should be integer (US) | 美国 **weight** 用整数磅 |
| 120011006 | warehouseId invalid | 用 **warehouse.list.get** 有效 ID |
| 120012007 | parentOrder/order invalid | 核对父子订单 |
| 120012016 | parentOrder/order invalid | 核对父子订单 |
| 120015528 | COD orders: Temu Label only | COD 仅 Temu 面单 |
| 120018063 | Funds reserved; Buy shipping disabled | 账户资金受限 |
| 120012061 | Risk control alert on parent order | 评估是否继续发货 |
| 120012031 | Risk control alert on parent order | 评估是否继续发货 |

> 完整错误码以 Partner 文档 **Error Code** 表为准（导出 HTML 含 70+ 条）。

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
