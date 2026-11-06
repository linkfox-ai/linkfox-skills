# 确认包裹已发货 接口说明

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

## 接口：确认包裹已发货（bg.logistics.shipped.package.confirm）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

（卖家将已通过 **Temu 集成物流** 成功履约、但状态仍为**未发货确认**的包裹，批量确认为**已发货**；若 **48 小时内**未手动确认，系统将自动转为已发货。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**。  
> **前置依赖：**  
> - **`packageSn`**、**`trackingNumber`** 通常来自 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md) / [**`bg.logistics.shipment.result.get`**](./bg-logistics-shipment-result-get.md) 或 [**`bg.order.unshipped.package.get`**](./bg-order-unshipped-package-get.md)。  
> - 打印面单并实际出库后调用，确认已发货的包裹；**`trackingNumber`** 须与 **`packageSn`** 匹配（错误码 **120014002**）。  
> - 合作仓包裹可能禁止手动确认发货（**120018087**）。

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

本接口 `type` 固定为 `bg.logistics.shipped.package.confirm`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    └── packageSendInfoList[] (OBJECT[], 必填)
        ├── packageSn
        ├── trackingNumber
        └── packageDetail[] (OBJECT[])
            ├── orderSn
            ├── parentOrderSn
            └── quantity
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packageSendInfoList | OBJECT[] | **是** | This field is used to confirm the list of packages that have been transitioned to the shipped status（待确认为**已发货**状态的包裹列表；支持批量） |

##### `packageSendInfoList[]` 元素字段

> Partner Request 表中 `packageSendInfoList` 子行在导出 HTML 中为折叠状态；下列字段来自 **Request Example** 与错误码说明。

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
response
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)
    └── warningMessage[] (OBJECT[])
        ├── packageSn
        └── warningMessage
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
| warningMessage | OBJECT[] | Per-package warning messages（按包裹返回的警告信息；部分包裹确认成功、部分有提示时非空） |

##### `warningMessage[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package SN（关联的包裹号） |
| warningMessage | STRING | Warning message text（该包裹的警告说明；具体文案以 Temu 返回为准） |

> 调用成功时先判断 **`response.success === true`**。若 **`result.warningMessage`** 非空，须逐条检查哪些 **`packageSn`** 未完全确认成功。无警告通常表示请求列表中的包裹均已处理完成（仍建议用 **`bg.order.unshipped.package.get`** 或订单接口复核状态）。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

| 错误码 | 错误信息 | 处理建议 |
|--------|------------------|----------|
| 120018027 | The packageSn is invalid. Please check the request area or if the packageSn is nonexistent etc. | 核对 **`packageSn`** 与站点 |
| 120014002 | The field trackingNumber {*} does not match packageSn {*}. Please check the matching relationship between the two fields. | **`trackingNumber`** 与 **`packageSn`** 必须匹配 |
| 120012004 | The order has been shipped. This submission is not effective for the shipped order. | 订单已发货，无需重复确认 |
| 120012012 | There are no shippable orders matching the item. | 包裹内无可发订单行 |
| 120013002 | Item quantity does not match. | **`packageDetail[].quantity`** 与包裹实际数量不一致 |
| 120011046 | Sub package not allowed. | 不支持对子包裹单独确认 |
| 120018087 | The current package {*} is shipped from a cooperative warehouse and manual confirmation of shipment is prohibited | 合作仓包裹禁止手动确认发货 |
| 120011030 | Cooperative warehouse order fulfillment restricted. | 合作仓履约受限 |
| 120018010 | The packages {*} have been canceled. Please fulfill again by Temu non-integrated logistics or Temu integrated logistics. | 包裹/订单已取消，需重新履约 |
| 120018015 | The package has been canceled, please fulfill again by Temu non-integrated logistics or Temu integrated logistics. | 包裹/订单已取消，需重新履约 |
| 120012007 | The parentOrder or Order is invalid. Please check if the parentOrder matches the Order, the parentOrder or Order is nonexistent etc. | 父子订单号无效或不匹配 |
| 120012016 | The parentOrder or Order is invalid. Please check if the parentOrder matches the Order, the parentOrder or Order is nonexistent etc. | 父子订单号无效或不匹配 |
| 120018025 | Orders exist after-sales applications, please complete the processing before operation | 先处理售后申请 |
| 120011072 | The request area is incorrect. Please check the request area and replace it with the correct request area. The request area for the United States is US, and the request area for other non-European countries is global. | 请求区域须与店铺一致；本技能为 global，美国订单使用 US 对应技能 |
| 120015026 | A large items template has been used for the items in this package. Only specified logistics providers can be used for shipping. | 按错误信息核对业务条件，不自动重试。 |
| 120015027 | A large items template has been used for the items in this package. Only special channels can be used for shipping. | 按错误信息核对业务条件，不自动重试。 |

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
