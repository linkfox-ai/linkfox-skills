# linkfox-shopee-store-orders

> 本文件归档该业务能力的执行说明、接口参数、响应字段、错误处理与认证规则。通过 LinkFox MCP 执行。

## MCP 传输契约

本 reference 的所有业务 operation 共享以下传输层；各 operation 的业务 `path`、`method`、请求参数、响应字段、枚举、区域限制和状态机仍以各节为准。

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `shopee/developerProxy` |
| `arguments` | 直接使用对应 operation 的 developerProxy 请求对象 |

WorkBuddy 自动注入 Authorization；MCP 配置和 `arguments` 中禁止放置 `headers`、手工凭证、token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，不得用 curl、`urllib`、`requests`、`httpx` 或本地脚本静默回退。


# Shopee 店铺 Orders

Shopee Open Platform **Order 模块**（22 个 API）。**依赖 `linkfox-shopee-store-auth`** 选店；经 `proxy_call`（`toolName=shopee/developerProxy`） 传入 `shopId`（或 `merchantId`），由服务端解析 token 转发（`path` 须 `api/v2/order/...`）。

## 调用方式

仅使用 `LinkFox.proxy_call`。所有 operation 的精确 `toolName` 均为 `shopee/developerProxy`；请求形状、解析顺序、去重和错误分层见上方 MCP 传输契约及各 operation 的 MCP 调用节。


## 认证和积分问题

按 `onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。WorkBuddy 自动注入 Authorization；不得收集或传入 Key/token。


## 官方参考

Order 模块索引：[Shopee Open Platform — Order](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1)

---

## Prerequisites（必须先读）

先用 `shopee/authorizedStores` 按 `shopId`/`merchantId + appType` 确认授权；缺失时按授权 reference 获取新授权 URL。

---

## Core Concepts

- **转发链路**：`developerProxy`（`shopId`/`merchantId` 选店，服务端注入 token）→ 紫鸟 `shopee-proxy` → Shopee API（`partner_id`/`sign` 由代理自动处理）
- **列表 → 详情**：`get_order_list` 得 `order_sn` → `get_order_detail` 拉全量字段（≤50 个/次）
- **包裹流**：`search_package_list` / `get_package_detail` / `get_shipment_list` 用于发货前包裹视图
- **写操作**：`split_order`、`cancel_order`、`set_note` 等为 **POST JSON body**
- **时间窗**：`get_order_list` / `get_booking_list` 的 `time_from`/`time_to` 最大 **15 天**



## Usage Scenarios

### 1. 查待发货订单
1. auth skill 定位 `shopId`
2. `get_order_list`：`order_status=READY_TO_SHIP`，`time_range_field=update_time`，15 天内时间戳
3. `get_order_detail`：传入 `order_sn_list`

### 2. 包裹维度处理
1. `search_package_list`：传 `pagination.page_size` 及可选 `filter`/`sort`（或整体 `body`）
2. `get_package_detail`：`package_number_list`
3. 发货物流见 Logistics 模块（非本 skill）

### 3. 取消 / 备注 / 拆单
- 取消：`cancel_order`（`order_sn` + `cancel_reason`）
- 买家取消申请：`handle_buyer_cancellation`（`ACCEPT`/`REJECT`）
- 备注：`set_note`
- 拆单/合单：`split_order` / `unsplit_order`

### 4. 选店（高频）

| 用户上下文 | Agent 动作 |
|---|---|
| 只授权 1 家 | 直接用 `shopId` |
| 多家 + 店名 | auth skill `authorized_stores` 澄清 |
| 已给 order_sn | 直接详情/写操作脚本 |

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 解析字段
- GET：业务参数作为请求 JSON 顶层字段（调用方编码为 `queryString`）
- POST：传 `body` 对象，或按 api.md 传顶层 body 字段
- `upload_invoice_doc` 官方为 **multipart**；若网关不支持，需在文档中说明限制
- 分页：`get_order_list` 用 `cursor`/`next_cursor`；`search_package_list` 用 `pagination.cursor`

## 常见问题

### 1005 path 白名单

确认 path 为 `api/v2/order/...`。

### 区域限制

发票类 API 限 PH/BR；`get_buyer_invoice_info` 限 VN/TH/PH；FBS 发票限 BR。

### token 过期

回到 **`linkfox-shopee-store-auth`** 重新授权。

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 商户信息 → `linkfox-shopee-store-merchant`
- 店铺信息与设置 → `linkfox-shopee-store-shop`
- 商品 listing → `linkfox-shopee-store-product`
- 账户健康 Account Health → `linkfox-shopee-store-account-health`
- 跨境全球商品 → `linkfox-shopee-store-global-product`
- 物流发货 → `linkfox-shopee-store-logistics`
- 头程 FirstMile → `linkfox-shopee-store-first-mile`
- 退货退款 → `linkfox-shopee-store-returns`
- 支付结算 → `linkfox-shopee-store-payment`
- 选品 → `linkfox-youying-shopee-product-search`

## 积分消耗规则

不消耗积分。

---

## Operation: cancel_order

| 项 | 值 |
|----|-----|
| operation | `cancel_order` |
| Method / path | POST `api/v2/order/cancel_order` |
| 官方文档 | [cancel_order](https://open.shopee.com/documents/v2/v2.order.cancel_order?module=94&type=1) |
| 用途 | cancel_reason: OUT_OF_STOCK/CUSTOMER_REQUEST/UNDELIVERABLE_AREA/COD_NOT_SUPPORTED |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `order_sn` | — | 是 | 见 notes / 官方文档 |
| `cancel_reason` | — | 是 | 见 notes / 官方文档 |
| `item_list` | — | 否（POST body） | 见 notes / 官方文档 |
| `partial_cancel_item_list` | — | 否（POST body） | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：cancel_reason: OUT_OF_STOCK/CUSTOMER_REQUEST/UNDELIVERABLE_AREA/COD_NOT_SUPPORTED

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/cancel_order",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/cancel-order.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.cancel_order?module=94&type=1)

**Body（必填）**：`order_sn`、`cancel_reason`

**Body（可选）**：`item_list`、`partial_cancel_item_list`（`item_id`、`model_id`、`model_quantity` 等）

**cancel_reason**：`OUT_OF_STOCK`、`CUSTOMER_REQUEST`、`UNDELIVERABLE_AREA`（TW/MY）、`COD_NOT_SUPPORTED`

---

## Operation: download_fbs_invoices

| 项 | 值 |
|----|-----|
| operation | `download_fbs_invoices` |
| Method / path | POST `api/v2/order/download_fbs_invoices` |
| 官方文档 | [download_fbs_invoices](https://open.shopee.com/documents/v2/v2.order.download_fbs_invoices?module=94&type=1) |
| 用途 | Download link expires in 30 minutes |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `request_id_list` | — | 否（POST body） | 见 notes / 官方文档 |
| `request_id_list` | object | 否（可嵌在 body） | 嵌套对象；或整体传 `body` / `requestBody` |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：Download link expires in 30 minutes

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/download_fbs_invoices",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/download-fbs-invoices.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.download_fbs_invoices?module=94&type=1)

**Body（必填）**：`request_id_list.request_id`（int 数组）

**说明**：需先 `generate_fbs_invoices` → 本接口轮询结果 → 下载；链接 30 分钟过期。

---

## Operation: download_invoice_doc

| 项 | 值 |
|----|-----|
| operation | `download_invoice_doc` |
| Method / path | GET `api/v2/order/download_invoice_doc` |
| 官方文档 | [download_invoice_doc](https://open.shopee.com/documents/v2/v2.order.download_invoice_doc?module=94&type=1) |
| 用途 | PH/BR |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `order_sn` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：PH/BR

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/download_invoice_doc",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/download-invoice-doc.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.download_invoice_doc?module=94&type=1)

**Query（必填）**：`order_sn`

**区域**：PH、BR

---

## Operation: generate_fbs_invoices

| 项 | 值 |
|----|-----|
| operation | `generate_fbs_invoices` |
| Method / path | POST `api/v2/order/generate_fbs_invoices` |
| 官方文档 | [generate_fbs_invoices](https://open.shopee.com/documents/v2/v2.order.generate_fbs_invoices?module=94&type=1) |
| 用途 | BR FBS; batch_download.start/end YYYYMMDD |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `batch_download` | — | 否（POST body） | 见 notes / 官方文档 |
| `batch_download` | object | 否（可嵌在 body） | 嵌套对象；或整体传 `body` / `requestBody` |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：BR FBS; batch_download.start/end YYYYMMDD

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/generate_fbs_invoices",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/generate-fbs-invoices.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.generate_fbs_invoices?module=94&type=1)

**Body（必填）**：`batch_download`（`start`/`end` YYYYMMDD、`document_type`、`file_type`；可选 `document_status`）

**区域**：BR FBS

---

## Operation: get_booking_detail

| 项 | 值 |
|----|-----|
| operation | `get_booking_detail` |
| Method / path | GET `api/v2/order/get_booking_detail` |
| 官方文档 | [get_booking_detail](https://open.shopee.com/documents/v2/v2.order.get_booking_detail?module=94&type=1) |
| 用途 | booking_sn_list: comma-separated, max 50 |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `booking_sn_list` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：booking_sn_list: comma-separated, max 50

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_booking_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-booking-detail.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_booking_detail?module=94&type=1)

**Query（必填）**：`booking_sn_list`（逗号分隔，1–50 个）

**Query（可选）**：`response_optional_fields`

---

## Operation: get_booking_list

| 项 | 值 |
|----|-----|
| operation | `get_booking_list` |
| Method / path | GET `api/v2/order/get_booking_list` |
| 官方文档 | [get_booking_list](https://open.shopee.com/documents/v2/v2.order.get_booking_list?module=94&type=1) |
| 用途 | booking_status optional: READY_TO_SHIP/PROCESSED/SHIPPED/CANCELLED/MATCHED |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `time_range_field` | — | **是** | Query 必填（见 notes / 官方文档） |
| `page_size` | — | **是** | Query 必填（见 notes / 官方文档） |
| `time_to` | — | **是** | Query 必填（见 notes / 官方文档） |
| `time_from` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：booking_status optional: READY_TO_SHIP/PROCESSED/SHIPPED/CANCELLED/MATCHED

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_booking_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-booking-list.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_booking_list?module=94&type=1)

**Query（必填）**：`time_range_field`、`time_from`、`time_to`、`page_size`

**Query（可选）**：`cursor`、`booking_status`（`READY_TO_SHIP`/`PROCESSED`/`SHIPPED`/`CANCELLED`/`MATCHED`）

---

## Operation: get_buyer_invoice_info

| 项 | 值 |
|----|-----|
| operation | `get_buyer_invoice_info` |
| Method / path | POST `api/v2/order/get_buyer_invoice_info` |
| 官方文档 | [get_buyer_invoice_info](https://open.shopee.com/documents/v2/v2.order.get_buyer_invoice_info?module=94&type=1) |
| 用途 | VN/TH/PH local sellers |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `queries` | — | 是 | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：VN/TH/PH local sellers

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_buyer_invoice_info",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-buyer-invoice-info.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_buyer_invoice_info?module=94&type=1)

**Body（必填）**：`queries[]`（含 `order_sn`）

**区域**：VN、TH、PH 本地卖家

---

## Operation: get_estimiate_cancel_value

| 项 | 值 |
|----|-----|
| operation | `get_estimiate_cancel_value` |
| Method / path | POST `api/v2/order/get_estimiate_cancel_value` |
| 官方文档 | [get_estimiate_cancel_value](https://open.shopee.com/documents/v2/v2.order.get_estimiate_cancel_value?module=94&type=1) |
| 用途 | Official spelling: estimiate (not estimate) |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `order_sn` | — | 是 | 见 notes / 官方文档 |
| `partial_cancel_item_list` | — | 是 | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：Official spelling: estimiate (not estimate)

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_estimiate_cancel_value",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-estimiate-cancel-value.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_estimiate_cancel_value?module=94&type=1)

> 官方 API 名拼写为 **estimiate**（非 estimate）。

**Body（必填）**：`order_sn`、`partial_cancel_item_list[]`（`item_id`、`model_id`、`model_quantity`；可选 `order_item_id`、`promotion_group_id`）

---

### 错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 手工凭证 |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/order/...` |

紫鸟代理 HTTP：`400` 路径错误、`403` IP 白名单、`408` 超时、`5xx` 上游透传。

---

## Operation: get_fbs_invoices_result

| 项 | 值 |
|----|-----|
| operation | `get_fbs_invoices_result` |
| Method / path | POST `api/v2/order/get_fbs_invoices_result` |
| 官方文档 | [get_fbs_invoices_result](https://open.shopee.com/documents/v2/v2.order.get_fbs_invoices_result?module=94&type=1) |
| 用途 | Shopee Open API `get_fbs_invoices_result` |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `request_id_list` | — | 否（POST body） | 见 notes / 官方文档 |
| `request_id_list` | object | 否（可嵌在 body） | 嵌套对象；或整体传 `body` / `requestBody` |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_fbs_invoices_result",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-fbs-invoices-result.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_fbs_invoices_result?module=94&type=1)

**Body（必填）**：`request_id_list.request_id`（int 数组）

---

## Operation: get_order_detail

| 项 | 值 |
|----|-----|
| operation | `get_order_detail` |
| Method / path | GET `api/v2/order/get_order_detail` |
| 官方文档 | [get_order_detail](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1) |
| 用途 | order_sn_list: string or array, max 50, comma-joined |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `order_sn_list` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：order_sn_list: string or array, max 50, comma-joined

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_order_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-order-detail.md` 的响应要点与 `Response` 摘要。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
| `body.response.order_list` | array | 来源以 `order_list[]` 明确为数组 |
| `body.response.order_list[]` | object | 订单数组元素；除下列字段外，其他属性来源未说明 |
| `body.response.order_list[].order_sn` | 来源未说明 | 来源仅列出字段名 |
| `body.response.order_list[].order_status` | 来源未说明 | 来源仅列出字段名 |
| `body.response.order_list[].total_amount` | 来源未说明 | 来源仅列出字段名 |
| `body.response.order_list[].item_list` | 来源未说明 | 来源仅列出字段名，未明确类型或内部结构 |
| `body.response.order_list[].recipient_address` | 来源未说明 | 来源仅列出字段名，未明确类型或内部结构 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1)

**Query（必填）**：`order_sn_list`（逗号分隔或数组，1–50 个）

**Query（可选）**：`response_optional_fields`、`request_order_status_pending`


---

## Operation: get_order_list

| 项 | 值 |
|----|-----|
| operation | `get_order_list` |
| Method / path | GET `api/v2/order/get_order_list` |
| 官方文档 | [get_order_list](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1) |
| 用途 | time_from/time_to max 15 days; order_status optional filter |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `time_range_field` | — | **是** | Query 必填（见 notes / 官方文档） |
| `page_size` | — | **是** | Query 必填（见 notes / 官方文档） |
| `time_to` | — | **是** | Query 必填（见 notes / 官方文档） |
| `time_from` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：time_from/time_to max 15 days; order_status optional filter

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_order_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-order-list.md` 的响应要点与 `Response` 摘要。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
| `body.response.more` | 来源未说明 | 来源仅列出字段名 |
| `body.response.next_cursor` | 来源未说明 | 来源仅列出字段名 |
| `body.response.order_list` | array | 来源以 `order_list[]` 明确为数组 |
| `body.response.order_list[]` | object | 订单数组元素；除下列字段外，其他属性来源未说明 |
| `body.response.order_list[].order_sn` | 来源未说明 | 来源仅列出字段名 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1)

**Query（必填）**：`time_range_field`（`create_time`|`update_time`）、`time_from`、`time_to`（Unix 秒，跨度 ≤15 天）、`page_size`（1–100）

**Query（可选）**：`cursor`、`order_status`（`UNPAID`/`READY_TO_SHIP`/`PROCESSED`/`SHIPPED`/`COMPLETED`/`IN_CANCEL`/`CANCELLED`/`INVOICE_PENDING`）、`response_optional_fields`、`request_order_status_pending`、`logistics_channel_id`（仅 BR）


---

## Operation: get_package_detail

| 项 | 值 |
|----|-----|
| operation | `get_package_detail` |
| Method / path | GET `api/v2/order/get_package_detail` |
| 官方文档 | [get_package_detail](https://open.shopee.com/documents/v2/v2.order.get_package_detail?module=94&type=1) |
| 用途 | package_number_list: comma-separated, max 50 |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `package_number_list` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：package_number_list: comma-separated, max 50

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_package_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-package-detail.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_package_detail?module=94&type=1)

**Query（必填）**：`package_number_list`（逗号分隔，1–50 个）

---

## Operation: get_pending_buyer_invoice_order_list

| 项 | 值 |
|----|-----|
| operation | `get_pending_buyer_invoice_order_list` |
| Method / path | GET `api/v2/order/get_pending_buyer_invoice_order_list` |
| 官方文档 | [get_pending_buyer_invoice_order_list](https://open.shopee.com/documents/v2/v2.order.get_pending_buyer_invoice_order_list?module=94&type=1) |
| 用途 | PH/BR local sellers |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `page_size` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：PH/BR local sellers

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_pending_buyer_invoice_order_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-pending-buyer-invoice-order-list.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_pending_buyer_invoice_order_list?module=94&type=1)

**Query（必填）**：`page_size`（1–100）

**Query（可选）**：`cursor`

**区域**：PH、BR 本地卖家

---

## Operation: get_shipment_list

| 项 | 值 |
|----|-----|
| operation | `get_shipment_list` |
| Method / path | GET `api/v2/order/get_shipment_list` |
| 官方文档 | [get_shipment_list](https://open.shopee.com/documents/v2/v2.order.get_shipment_list?module=94&type=1) |
| 用途 | READY_TO_SHIP orders eligible for shipping |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `page_size` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：READY_TO_SHIP orders eligible for shipping

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_shipment_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-shipment-list.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_shipment_list?module=94&type=1)

**Query（必填）**：`page_size`（1–100）

**Query（可选）**：`cursor`

**说明**：返回可开始发货流程的 `READY_TO_SHIP` 订单/包裹。

---

## Operation: get_warehouse_filter_config

| 项 | 值 |
|----|-----|
| operation | `get_warehouse_filter_config` |
| Method / path | GET `api/v2/order/get_warehouse_filter_config` |
| 官方文档 | [get_warehouse_filter_config](https://open.shopee.com/documents/v2/v2.order.get_warehouse_filter_config?module=94&type=1) |
| 用途 | Multi-warehouse shops |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：Multi-warehouse shops

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/get_warehouse_filter_config",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/get-warehouse-filter-config.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_warehouse_filter_config?module=94&type=1)

无额外业务参数（仅店铺公共 query）。多仓店铺返回仓库过滤配置。

---

## Operation: handle_buyer_cancellation

| 项 | 值 |
|----|-----|
| operation | `handle_buyer_cancellation` |
| Method / path | POST `api/v2/order/handle_buyer_cancellation` |
| 官方文档 | [handle_buyer_cancellation](https://open.shopee.com/documents/v2/v2.order.handle_buyer_cancellation?module=94&type=1) |
| 用途 | operation: ACCEPT \| REJECT |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `order_sn` | — | 是 | 见 notes / 官方文档 |
| `operation` | — | 是 | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：operation: ACCEPT | REJECT

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/handle_buyer_cancellation",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/handle-buyer-cancellation.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.handle_buyer_cancellation?module=94&type=1)

**Body（必填）**：`order_sn`、`operation`（`ACCEPT`|`REJECT`）

---

## Operation: handle_prescription_check

| 项 | 值 |
|----|-----|
| operation | `handle_prescription_check` |
| Method / path | POST `api/v2/order/handle_prescription_check` |
| 官方文档 | [handle_prescription_check](https://open.shopee.com/documents/v2/v2.order.handle_prescription_check?module=94&type=1) |
| 用途 | operation: APPROVE \| REJECT; ID/PH whitelist |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `package_number` | — | 是 | 见 notes / 官方文档 |
| `order_sn` | — | 否（POST body） | 见 notes / 官方文档 |
| `operation` | — | 是 | 见 notes / 官方文档 |
| `reject_reason` | — | 否（POST body） | 见 notes / 官方文档 |
| `is_approved` | — | 否（POST body） | 见 notes / 官方文档 |
| `reject_reason_code` | — | 否（POST body） | 见 notes / 官方文档 |
| `items` | — | 否（POST body） | 见 notes / 官方文档 |
| `pharmacist_name` | — | 否（POST body） | 见 notes / 官方文档 |
| `free_text` | — | 否（POST body） | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：operation: APPROVE | REJECT; ID/PH whitelist

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/handle_prescription_check",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/handle-prescription-check.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.handle_prescription_check?module=94&type=1)

**Body（必填）**：`package_number`、`operation`（`APPROVE`|`REJECT`）

**Body（可选）**：`order_sn`、`reject_reason`、`is_approved`、`reject_reason_code`、`items`、`pharmacist_name`、`free_text`

**区域**：ID、PH 白名单卖家

---

## Operation: search_package_list

| 项 | 值 |
|----|-----|
| operation | `search_package_list` |
| Method / path | POST `api/v2/order/search_package_list` |
| 官方文档 | [search_package_list](https://open.shopee.com/documents/v2/v2.order.search_package_list?module=94&type=1) |
| 用途 | Pass body object or top-level filter/pagination/sort |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `filter` | object | 否（可嵌在 body） | 嵌套对象；或整体传 `body` / `requestBody` |
| `pagination` | object | 否（可嵌在 body） | 嵌套对象；或整体传 `body` / `requestBody` |
| `sort` | object | 否（可嵌在 body） | 嵌套对象；或整体传 `body` / `requestBody` |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：Pass body object or top-level filter/pagination/sort

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/search_package_list",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/search-package-list.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.search_package_list?module=94&type=1)

**Body（必填）**：`pagination.page_size`（1–100）

**Body（可选）**：
- `filter`：`package_status`、`product_location_ids`、`logistics_channel_ids`、`fulfillment_type`、`invoice_pending`、`sorting_group`（TW）、`order_type`、`is_pre_order`、`shipping_priority`
- `pagination.cursor`
- `sort`：`sort_type`（1=ShipByDate/2=CreateDate/3=ConfirmedDate）、`ascending`

**示例**：
```json
{
  "shopId": "67890",
  "filter": {"package_status": 2, "fulfillment_type": 2},
  "pagination": {"page_size": 20, "cursor": ""},
  "sort": {"sort_type": 1, "ascending": false}
}
```

---

## Operation: set_note

| 项 | 值 |
|----|-----|
| operation | `set_note` |
| Method / path | POST `api/v2/order/set_note` |
| 官方文档 | [set_note](https://open.shopee.com/documents/v2/v2.order.set_note?module=94&type=1) |
| 用途 | Shopee Open API `set_note` |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `order_sn` | — | 是 | 见 notes / 官方文档 |
| `note` | — | 是 | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/set_note",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/set-note.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.set_note?module=94&type=1)

**Body（必填）**：`order_sn`、`note`

---

## Operation: split_order

| 项 | 值 |
|----|-----|
| operation | `split_order` |
| Method / path | POST `api/v2/order/split_order` |
| 官方文档 | [split_order](https://open.shopee.com/documents/v2/v2.order.split_order?module=94&type=1) |
| 用途 | Shopee Open API `split_order` |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `order_sn` | — | 是 | 见 notes / 官方文档 |
| `package_list` | — | 是 | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/split_order",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/split-order.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.split_order?module=94&type=1)

**Body（必填）**：`order_sn`、`package_list[]`（含 `item_list[]`：`item_id`、`model_id`；可选 `order_item_id`、`promotion_group_id`、`model_quantity`）

---

## Operation: unsplit_order

| 项 | 值 |
|----|-----|
| operation | `unsplit_order` |
| Method / path | POST `api/v2/order/unsplit_order` |
| 官方文档 | [unsplit_order](https://open.shopee.com/documents/v2/v2.order.unsplit_order?module=94&type=1) |
| 用途 | Shopee Open API `unsplit_order` |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `order_sn` | — | 是 | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/unsplit_order",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/unsplit-order.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.unsplit_order?module=94&type=1)

**Body（必填）**：`order_sn`（仅 `READY_TO_SHIP` 且未发货的已拆分订单）

---

## Operation: upload_invoice_doc

| 项 | 值 |
|----|-----|
| operation | `upload_invoice_doc` |
| Method / path | POST `api/v2/order/upload_invoice_doc` |
| 官方文档 | [upload_invoice_doc](https://open.shopee.com/documents/v2/v2.order.upload_invoice_doc?module=94&type=1) |
| 用途 | Official API uses multipart/form-data; pass full body via body key if gateway supports it. PH/BR. |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：Official API uses multipart/form-data; pass full body via body key if gateway supports it. PH/BR.

---

### MCP 调用

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`shopee/developerProxy`（精确匹配且区分大小写）
- `arguments`：直接传入本 operation 的网关请求对象；不得增加 `headers`、手工凭证、token 或额外的 `body`/`data` 包装层。

```json
{
  "toolName": "shopee/developerProxy",
  "arguments": {
    "path": "api/v2/order/upload_invoice_doc",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-orders/references/api.md` 的 `developerProxy Response` 示例，以及 `skills/linkfox-shopee-store-orders/references/apis/upload-invoice-doc.md` 的响应要点。operation 来源中的 camelCase 结果键和 `errcode` 是旧脚本解析/包装位置，不是 `developerProxy` 下游响应字段，未纳入下表。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `body.response` | object | Shopee operation 结果对象；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.order.upload_invoice_doc?module=94&type=1)

**说明**：官方为 **multipart/form-data**（`order_sn`、`file_type`、`file`）。若 LinkFox 网关 `body` 仅支持 JSON 字符串，可能无法直接上传二进制；需确认网关能力或使用专用上传链路。

**区域**：PH、BR

---
