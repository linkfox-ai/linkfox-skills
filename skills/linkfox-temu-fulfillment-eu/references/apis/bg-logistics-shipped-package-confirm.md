# Temu 欧洲站 确认包裹已发货 接口说明

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

## 接口：确认包裹已发货（bg.logistics.shipped.package.confirm）

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

本操作的 `type` 固定为 `bg.logistics.shipped.package.confirm`。脚本：`scripts/eu_buy_shipping_logistics_shipped_package_confirm.py`（相对技能根目录）。

#### params 业务对象

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否（请求表标注） | 业务请求对象；其子字段、条件必填与特殊约定见下文。业务请求以各子字段要求为准。 |

#### 业务前提与限制

（卖家将已通过 **Temu 集成物流** 成功履约、但状态仍为**未发货确认**的包裹，批量确认为**已发货**；若 **48 小时内**未手动确认，系统将自动转为已发货。）

> **前置依赖：**
> - **`packageSn`**、**`trackingNumber`** 通常来自 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md) / [**`bg.logistics.shipment.result.get`**](./bg-logistics-shipment-result-get.md) 或 [**`bg.order.unshipped.package.get`**](./bg-order-unshipped-package-get.md)。
> - 打印面单后出库前调用；**`trackingNumber`** 须与 **`packageSn`** 匹配（错误码 **120014002**）。
> - 合作仓包裹可能禁止手动确认发货（**120018087**）。

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSendInfoList | OBJECT[] | **是** | This field is used to confirm the list of packages that have been transitioned to the shipped status（待确认为**已发货**状态的包裹列表；支持批量） |

##### `packageSendInfoList[]` 元素字段

> Partner 请求表中 `packageSendInfoList` 子行在导出 HTML 中为折叠状态；下列字段来自 **请求示例** 与错误码说明。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSn | STRING | **是** | Package SN（包裹号；购标/履约成功后由平台分配，见 **`bg.logistics.shipment.create`** 等返回） |
| trackingNumber | STRING | **是** | Tracking Number（物流运单号；须与 **`packageSn`** 对应，错误码 **120014002**） |
| packageDetail | OBJECT[] | **是** | Package detail / order lines in this package（本包裹内要确认发货的商品行明细；数量须与包裹内实际一致，错误码 **120013002**） |

###### `packageSendInfoList[].packageDetail[]` 元素字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentOrderSn | STRING | **是** | Parent Order Number（父订单号） |
| orderSn | STRING | **是** | Order Number（子订单号 / 订单号） |
| quantity | INTEGER | **是** | Quantity（本行商品数量；须与包裹内该订单行数量一致，错误码 **120013002**） |

> **不支持子包裹单独确认**（错误码 **120011046** Sub package not allowed）。已发货订单重复提交无效（**120012004**）。无匹配可发订单时返回 **120012012**。

> 官方请求表将顶层 **`request`** 标为选填（False），但 **`packageSendInfoList`** 为必填。Partner **请求示例** CURL 将 **`packageSendInfoList`** 写在顶层；经 LinkFox 网关时建议放在 **`params.request.packageSendInfoList`**。

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
| warningMessage | OBJECT[] | Per-package warning messages（按包裹返回的警告信息；部分包裹确认成功、部分有提示时非空） |

##### `warningMessage[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package SN（关联的包裹号） |
| warningMessage | STRING | Warning message text（该包裹的警告说明；具体文案以 Temu 返回为准） |

> 调用成功时先判断 **`response.success === true`**。若 **`result.warningMessage`** 非空，须逐条检查哪些 **`packageSn`** 未完全确认成功。无警告通常表示请求列表中的包裹均已处理完成（仍建议用 **`bg.order.unshipped.package.get`** 或订单接口复核状态）。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

网关正常后，判断 Temu 的 `success`、`errorCode`、`errorMsg` 与各项业务状态；`success=true` 不代表异步履约或审核已最终完成。业务错误保留原文，不自动重试写入。

> 若 **48 小时内**未调用本接口，平台可能自动将符合条件的包裹转为已发货；仍建议在出库后主动确认，便于与 **`packageDetail`** 数量、运单一致。

| 错误码 | 错误信息（原文） | 处理建议 |
|--------|------------------|----------|
| 120018027 | The packageSn is invalid. Please check the request area or if the packageSn is nonexistent etc. | 核对 **`packageSn`** 与站点 |
| 120014002 | The field trackingNumber {*} does not match packageSn {*}. Please check the matching relationship between the two fields. | **`trackingNumber`** 与 **`packageSn`** 必须匹配 |
| 120012004 | The order has been shipped. This submission is not effective for the shipped order. | 订单已发货，无需重复确认 |
| 120012012 | There are no shippable orders matching the item. | 包裹内无可发订单行 |
| 120013002 | Item quantity does not match. | **`packageDetail[].quantity`** 与包裹实际数量不一致 |
| 120011046 | Sub package not allowed. | 不支持对子包裹单独确认 |
| 120018087 | The current package {*} is shipped from a cooperative warehouse and manual confirmation of shipment is prohibited | 合作仓包裹禁止手动确认发货 |
| 120011030 | Cooperative warehouse order fulfillment restricted. | 合作仓履约受限 |
| 120018010 / 120018015 | The package(s) {*} have been canceled... | 包裹/订单已取消，需重新履约 |
| 120012007 / 120012016 | The parentOrder or Order is invalid... | 父子订单号无效或不匹配 |
| 120018025 | Orders exist after-sales applications, please complete the processing before operation | 先处理售后申请 |
| 120011072 | The request area is incorrect. Please check the request area and replace it with the correct request area. The request area for the United States is US, and the request area for other non-European countries is global. | 核对站点与令牌区域；本技能使用 `site=eu`，勿因 US 示例自动切换站点 |
| 120018010 | The packages {*} have been canceled. Please fulfill again by Temu non-integrated logistics or Temu integrated logistics. |  |
| 120018015 | The package has been canceled, please fulfill again by Temu non-integrated logistics or Temu integrated logistics. |  |
| 120015026 | A large items template has been used for the items in this package. Only specified logistics providers can be used for shipping. |  |
| 120015027 | A large items template has been used for the items in this package. Only special channels can be used for shipping. |  |
| 120012007 | The parentOrder or Order is invalid. Please check if the parentOrder matches the Order, the parentOrder or Order is nonexistent etc. |  |
| 120012016 | The parentOrder or Order is invalid. Please check if the parentOrder matches the Order, the parentOrder or Order is nonexistent etc. |  |

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
  "type": "bg.logistics.shipped.package.confirm",
  "params": {
    "request": {
      "packageSendInfoList": [
        {
          "packageSn": "PKG-001",
          "trackingNumber": "1Z999AA10123456784",
          "packageDetail": [
            {
              "parentOrderSn": "PO-20260101001",
              "orderSn": "O-20260101001-1",
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
