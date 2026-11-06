# 查询未发货包裹 接口说明

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

## 接口：查询未发货包裹（bg.order.unshipped.package.get）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 使用限制

**说明：** （卖家查询经 **Temu 集成物流** 已成功履约、但尚未完成发货确认的**未发货包裹**信息，含运单、承运商及包裹内可发/已取消订单行。）

> **网关鉴权字段**由本 skill 网关脚本处理；业务参数见下方 **`request`**。建议使用 **`tokenPurpose=order-shipping`**。  
> **关联能力：** 购标后包裹号来自 [**`bg.logistics.shipment.create`**](./bg-logistics-shipment-create.md)；订单号来自 **`linkfox-temu-order-global`**；确认发货见 [**`bg.logistics.shipped.package.confirm`**](./bg-logistics-shipped-package-confirm.md)。

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

本接口 `type` 固定为 `bg.order.unshipped.package.get`。

#### Temu 业务参数层级

```text
params
└── request (OBJECT, 选填)
    ├── pageNumber          ← 必填
    ├── pageSize            ← 必填
    ├── parentOrderSnList[] ← 选填
    └── orderSnList[]       ← 选填
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNumber | INTEGER | **是** | Page number（页码，从 **1** 起） |
| pageSize | INTEGER | **是** | Page size（每页条数） |
| parentOrderSnList | STRING[] | 否 | Parent order number list（父订单号列表；按父订单筛选未发货包裹） |
| orderSnList | STRING[] | 否 | Order number list（子订单号 / 订单号列表；按子订单筛选未发货包裹） |

> 官方 Request 表将顶层 **`request`** 标为选填（False），但 **`pageNumber`**、**`pageSize`** 为必填。筛选时至少可传 **`parentOrderSnList`** 和/或 **`orderSnList`** 缩小范围；均不传时按分页返回店铺下符合条件的未发货包裹（以 Partner 与账号权限为准）。  
> Partner **Request Example** CURL 将字段写在顶层；经 LinkFox 网关时建议放在 **`params.request`**（与 Request 表一致）。

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

Partner **Response** 表顶层为 **`response`** 对象；网关解析后通常直接见到 `success` / `errorCode` / `errorMsg` / `result`。  
**`result`** 子行在导出 HTML 中为折叠状态；下列层级按 **Response 表 + Response Example** 全部展开。

```text
response（或解析后的根对象）
├── success
├── errorCode
├── errorMsg
└── result (OBJECT)
    ├── totalItemNum (INTEGER)
    └── unshippedPackage[] (OBJECT[])
        ├── packageSn
        ├── mainPackageSn
        ├── subPackageSnList[] (STRING[])
        ├── subPackageType
        ├── trackingNumber
        ├── carrierId
        ├── carrierName
        └── packageDetail (OBJECT)
            ├── shippableOrders[] (OBJECT[])
            │   ├── semiUniqueId
            │   ├── quantity
            │   ├── orderSn
            │   ├── parentOrderSn
            │   └── mallId
            └── canceledOrders[] (OBJECT[])
                ├── semiUniqueId
                ├── quantity
                ├── orderSn
                ├── parentOrderSn
                └── mallId
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
| totalItemNum | INTEGER | Total item count（符合查询条件的未发货包裹总条数，用于分页） |
| unshippedPackage | OBJECT[] | Unshipped package list（未发货包裹列表；经 Temu 集成物流已成功履约的包裹） |

##### `unshippedPackage[]` 元素字段

| 参数 | 类型 | 说明 |
|------|------|------|
| packageSn | STRING | Package SN（包裹号；与 **`bg.logistics.shipment.create`** 返回的 **`packageSnList`**、**`bg.logistics.shipment.result.get`** 等一致） |
| mainPackageSn | STRING | Main package SN（主包裹号；拆分子包裹时标识主包裹） |
| subPackageSnList | STRING[] | Sub-package SN list（子包裹号列表；一单多包裹/拆包场景） |
| subPackageType | STRING | Sub-package type（子包裹类型标识；具体枚举以 Partner 在线文档为准） |
| trackingNumber | STRING | Tracking number（物流运单号 / 跟踪号） |
| carrierId | INTEGER / LONG | Carrier ID（承运商 ID） |
| carrierName | STRING | Carrier name（承运商名称，展示用） |
| packageDetail | OBJECT | Package detail（包裹内订单行明细：可发货与已取消） |

###### `packageDetail` 内字段

| 参数 | 类型 | 说明 |
|------|------|------|
| shippableOrders | OBJECT[] | Shippable orders in this package（本包裹内**仍可发货**的订单商品行） |
| canceledOrders | OBJECT[] | Canceled orders in this package（本包裹内**已取消**、不可再发的订单商品行） |

###### `shippableOrders[]` / `canceledOrders[]` 元素字段

> 两类数组元素结构相同；**`canceledOrders`** 为购标后订单被取消等场景，**`shippableOrders`** 为仍可继续发货确认的行。

| 参数 | 类型 | 说明 |
|------|------|------|
| semiUniqueId | STRING | Semi-unique ID（半托管订单行唯一标识；与 **`bg.logistics.shipment.result.get`** 的 **`orderSendInfoList[].semiUniqueId`** 等同系列字段） |
| quantity | INTEGER | Quantity（该行商品数量） |
| orderSn | STRING | Order number（子订单号 / 订单号） |
| parentOrderSn | STRING | Parent order number（父订单号） |
| mallId | INTEGER / LONG | Mall ID（店铺/商城 ID） |

> 调用成功时先判断 **`success === true`**，再根据 **`result.totalItemNum`** 与 **`pageNumber` / `pageSize`** 翻页；对每个 **`unshippedPackage`** 查看 **`trackingNumber`**、**`packageSn`** 及 **`packageDetail.shippableOrders`**，再调用 **`bg.logistics.shipped.package.confirm`** 等完成发货确认。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关 `code=1002` 时核对参数与 LinkFox Token；`code=1003` 时核对 Temu 令牌、用途、白名单和转发错误，不视为 Temu 履约成功。
- 网关正常后解析 body；Temu `success` 为 true 才读取业务结果，失败时保留 errorCode、errorMsg。请求被接受与面单、预约、履约最终完成须分别判断。

| 错误码 | 错误信息 | 处理建议 |
|--------|------------------|----------|
| 120011030 | Cooperative warehouse order fulfillment restricted. | 合作仓履约受限 |
| 120011072 | The request area is incorrect... US / global | 请求区域须与店铺一致；本技能为 global，美国订单使用 US 对应技能 |
| 120012016 | The parentOrder or Order is invalid... | 核对 **`parentOrderSnList`** / **`orderSnList`** 与订单是否存在、父子关系是否匹配 |

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
  "type": "bg.order.unshipped.package.get",
  "params": {
    "request": {
      "pageNumber": 1,
      "pageSize": 20,
      "parentOrderSnList": [
        "PO-20260101001"
      ],
      "orderSnList": [
        "O-20260101001-1"
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
