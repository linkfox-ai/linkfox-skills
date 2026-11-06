# Temu 欧洲站 查询购标/在线下单结果 接口说明

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

## 接口：查询购标/在线下单结果（bg.logistics.shipment.result.get）

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

本操作的 `type` 固定为 `bg.logistics.shipment.result.get`。脚本：`scripts/eu_buy_shipping_logistics_shipment_result_get.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家查询**在线物流下单/购标**结果；**`shippingLabelStatus`** 表示面单状态：**0**=进行中、**1**=成功、**2**=失败。）

> **前置依赖：** **`packageSnList`** 中的包裹号通常来自 **`bg.logistics.shipment.create`** 或订单/包裹相关接口返回的 **`packageSn`**。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSnList | STRING[] | 否 | Package number list（包裹号列表；传入一个或多个 **`packageSn`** 批量查询购标/在线下单结果） |

> 官方请求表将 **`request`** 与 **`packageSnList`** 均标为选填（False）；实际查询须传入有效 **`packageSn`**（错误码 **120018027**）。Partner **请求示例** CURL 将 **`packageSnList`** 写在顶层，经 LinkFox 网关时建议放在 **`params.request.packageSnList`**（与 Partner 请求表一致）。

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

Partner **响应** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`。**`result`** 在导出 HTML 中为折叠状态，下列子层级按 **响应表 + 响应示例** 全部展开。

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

> Partner **响应** 表中 **`result`** 子行在导出 HTML 中为折叠状态；下列字段与类型来自 **响应示例**，说明结合接口说明 与 Buy-Shipping 流程整理。若 Partner 在线文档 **Expand** 后有更完整枚举，以在线表为准。

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
| skuId | LONG | SKU 标识（SKU ID） |

> 调用成功时先判断 **`success === true`**，再按 **`packageSn`** 在 **`result.packageInfoResultList`** 中查看 **`shippingLabelStatus`**：**1** 表示购标成功，可继续取面单；**0** 可轮询本接口；**2** 查看 **`failReasonText`**。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120018027 | The packageSn is invalid. Please check the request area or if the packageSn is nonexistent etc. |  |

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
  "type": "bg.logistics.shipment.result.get",
  "params": {
    "request": {
      "packageSnList": [
        "PKG-001",
        "PKG-002"
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
