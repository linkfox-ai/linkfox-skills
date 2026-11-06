# 查询购标/在线下单结果 接口说明

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

## 接口：查询购标/在线下单结果（bg.logistics.shipment.result.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

（卖家查询**在线物流下单/购标**结果；**`shippingLabelStatus`** 表示面单状态：**0**=进行中、**1**=成功、**2**=失败。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**。  
> **前置依赖：** **`packageSnList`** 中的包裹号通常来自 **`bg.logistics.shipment.create`** 或订单/包裹相关接口返回的 **`packageSn`**。

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

本接口 `type` 固定为 `bg.logistics.shipment.result.get`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    └── packageSnList[] (STRING[], 选填)
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSnList | STRING[] | 否 | Package number list（包裹号列表；传入一个或多个 **`packageSn`** 批量查询购标/在线下单结果） |

> 官方 Request 表将 **`request`** 与 **`packageSnList`** 均标为选填（False）；实际查询须传入有效 **`packageSn`**（错误码 **120018027**）。Partner **Request Example** CURL 将 **`packageSnList`** 写在顶层，经 LinkFox 网关时建议放在 **`params.request.packageSnList`**（与 Partner Request 表一致）。

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

Partner **Response** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`。**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **Response 表 + Response Example** 全部展开。

```text
response（或解析后的根对象）
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)
    └── packageInfoResultList[] (OBJECT[])
        ├── packageSn
        ├── shippingLabelStatus
        ├── failReasonText
        ├── trackingNumber
        ├── channelId
        ├── shipLogisticsType
        ├── shipCompanyId
        ├── shippingCompanyName
        ├── warehouseId
        ├── warehouseName
        ├── mainPackageSn
        ├── subPackageSnList[]
        ├── subPackageType
        ├── cwFulfillNo
        ├── reservationSn
        ├── estimatedText
        ├── estimatedAmount
        ├── estimatedCurrencyCode
        ├── solutionText
        ├── packageDeliveryType
        ├── dimensionUnit
        ├── length
        ├── width
        ├── height
        ├── weight
        ├── weightUnit
        ├── extendWeight
        ├── extendWeightUnit
        ├── pickupStartTime
        ├── pickupEndTime
        ├── shipLabelPrintableTime
        ├── isConfirmAfterPickup
        ├── canChangeToManualSend
        ├── signServiceId
        ├── uspsMailingDateOffset
        ├── warningMessage[]
        ├── interlineShipCompanyList[] (OBJECT[])
        │   ├── shipLogisticsType
        │   ├── shipStageType
        │   ├── shippingCompanyName
        │   ├── channelId
        │   └── shipCompanyId
        ├── shippingInfoList[] (OBJECT[])
        │   ├── shipLogisticsType
        │   ├── shipStageType
        │   ├── shippingCompanyName
        │   ├── trackingNumber
        │   └── shipCompanyId
        └── orderSendInfoList[] (OBJECT[])
            ├── semiUniqueId
            ├── quantity
            ├── orderSn
            ├── parentOrderSn
            ├── goodsId
            ├── mallId
            └── skuId
```

#### 顶层字段（`response` 内，或根级）

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | success（当前请求是否成功，True 成功，False 失败） |
| errorCode | INTEGER | error code（错误码） |
| errorMsg | STRING | error message（错误信息） |
| result | OBJECT | result（业务结果对象） |

#### `result` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageInfoResultList | OBJECT[] | 按 **`packageSnList`** 查询得到的包裹购标/在线下单结果列表（与请求包裹号一一对应或按平台规则返回） |

##### `packageInfoResultList[]` 元素字段

> Partner **Response** 表中 **`result`** 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **Response Example**，说明结合接口 Description 与 Buy-Shipping 流程整理。若 Partner 在线文档 **Expand** 后有更完整枚举，以在线表为准。

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package number（包裹号；与请求 **`packageSnList`** 元素对应） |
| shippingLabelStatus | INTEGER | Shipping label status（物流面单/购标状态）：**0**=in-progress（进行中），**1**=successful（成功），**2**=failed（失败） |
| failReasonText | STRING | Failure reason text（购标/下单失败原因文案；**`shippingLabelStatus=2`** 时关注） |
| trackingNumber | STRING | Tracking number（运单号/追踪号；成功后可用于物流跟踪） |
| channelId | INTEGER | Channel ID（物流渠道 ID；与 **`bg.logistics.shippingservices.get`** / **`bg.logistics.shipment.create`** 一致） |
| shipLogisticsType | STRING | Ship logistics type（发货物流类型编码） |
| shipCompanyId | INTEGER | Ship company ID（物流公司/承运商 ID） |
| shippingCompanyName | STRING | Shipping company name（物流公司/承运商名称） |
| warehouseId | STRING | Warehouse ID（发货仓库 ID） |
| warehouseName | STRING | Warehouse name（发货仓库名称） |
| mainPackageSn | STRING | Main package number（主包裹号；拆分子包裹场景下的主单号） |
| subPackageSnList | STRING[] | Sub package number list（子包裹号列表） |
| subPackageType | STRING | Sub package type（子包裹类型） |
| cwFulfillNo | STRING | Cooperative warehouse fulfill number（合作仓履约单号/履约编号） |
| reservationSn | STRING | Reservation SN（预约/预留单号，如取件预约相关） |
| estimatedText | STRING | Estimated delivery time text（预计送达/时效展示文案） |
| estimatedAmount | STRING | Estimated shipping amount（预估运费金额，字符串形式保留精度） |
| estimatedCurrencyCode | STRING | Currency code for **estimatedAmount**（预估运费币种代码） |
| solutionText | STRING | Solution / service description text（方案或服务说明文案） |
| packageDeliveryType | INTEGER | Package delivery type（包裹配送类型；具体枚举以 Partner 文档为准） |
| dimensionUnit | STRING | Dimension unit（长宽高单位，如 **`in`** / **`cm`**） |
| length | STRING | Package length（包裹长度，通常保留两位小数） |
| width | STRING | Package width（包裹宽度） |
| height | STRING | Package height（包裹高度） |
| weight | STRING | Package weight（包裹重量） |
| weightUnit | STRING | Weight unit（重量单位，如 **`lb`** / **`kg`**） |
| extendWeight | STRING | Extended weight portion（扩展重量，如美国本地订单盎司部分） |
| extendWeightUnit | STRING | Extended weight unit（扩展重量单位，如 **`oz`**） |
| pickupStartTime | INTEGER | Pickup window start time（取件窗口开始时间，Unix 秒级时间戳） |
| pickupEndTime | INTEGER | Pickup window end time（取件窗口结束时间，Unix 秒级时间戳） |
| shipLabelPrintableTime | INTEGER | Ship label printable time（面单可打印时间，Unix 秒级时间戳；**`shippingLabelStatus=1`** 后用于 **`bg.logistics.shipment.document.get`** 等） |
| isConfirmAfterPickup | BOOLEAN | Whether shipment is confirmed after pickup（是否在取件后确认发货） |
| canChangeToManualSend | BOOLEAN | Whether seller can switch to manual send（是否允许改为卖家自发货/手动发货） |
| signServiceId | INTEGER | Signature service ID（签名/签收服务 ID） |
| uspsMailingDateOffset | INTEGER | USPS mailing date offset（USPS 邮寄日期偏移量，USPS 渠道相关） |
| warningMessage | STRING[] | Warning messages（警告信息列表，非致命提示） |
| interlineShipCompanyList | OBJECT[] | Interline shipping company list（联运/分段物流承运商列表） |
| shippingInfoList | OBJECT[] | Shipping info list by stage（分段物流信息列表，含各段运单号） |
| orderSendInfoList | OBJECT[] | Orders included in this package（本包裹关联的订单发货信息列表） |

##### `interlineShipCompanyList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| shipLogisticsType | STRING | Ship logistics type（该段物流类型编码） |
| shipStageType | STRING | Ship stage type（运输阶段类型，如干线/末端等；枚举以 Partner 为准） |
| shippingCompanyName | STRING | Shipping company name（该段承运商名称） |
| channelId | INTEGER | Channel ID（该段渠道 ID） |
| shipCompanyId | INTEGER | Ship company ID（该段物流公司 ID） |

##### `shippingInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| shipLogisticsType | STRING | Ship logistics type（该段物流类型编码） |
| shipStageType | STRING | Ship stage type（运输阶段类型） |
| shippingCompanyName | STRING | Shipping company name（该段承运商名称） |
| trackingNumber | STRING | Tracking number（该段运单号） |
| shipCompanyId | INTEGER | Ship company ID（该段物流公司 ID） |

##### `orderSendInfoList[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| semiUniqueId | STRING | Semi-managed unique identifier（半托管业务侧唯一标识） |
| quantity | INTEGER | Quantity of the product（本行商品发货数量） |
| orderSn | STRING | Order number（子订单号） |
| parentOrderSn | STRING | Parent order number（父订单号） |
| goodsId | LONG | Goods ID（商品 ID） |
| mallId | LONG | Mall ID（店铺/商城 ID） |
| skuId | LONG | SKU 标识 |

> 调用成功时先判断 **`success === true`**，再按 **`packageSn`** 在 **`result.packageInfoResultList`** 中查看 **`shippingLabelStatus`**：**1** 表示购标成功，可继续取面单；**0** 可轮询本接口；**2** 查看 **`failReasonText`**。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

| 错误码 | 错误信息 |
|------------|---------------|
| 120018027 | The packageSn is invalid. Please check the request area or if the packageSn is nonexistent etc. |

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
  "type": "bg.logistics.shipment.result.get",
  "params": {
    "request": {
      "packageSnList": [
        "PKG-001",
        "PKG-002"
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
