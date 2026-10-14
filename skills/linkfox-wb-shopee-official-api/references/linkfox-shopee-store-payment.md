# linkfox-shopee-store-payment

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


# Shopee 店铺 Payment

Shopee Open Platform **Payment 模块**（18 个 API）。**依赖 `linkfox-shopee-store-auth`** 选店；经 `proxy_call`（`toolName=shopee/developerProxy`） 传入 `shopId`（或 `merchantId`），由服务端解析 token 转发（`path` 须 `api/v2/payment/...`）。

## 调用方式

仅使用 `LinkFox.proxy_call`。所有 operation 的精确 `toolName` 均为 `shopee/developerProxy`；请求形状、解析顺序、去重和错误分层见上方 MCP 传输契约及各 operation 的 MCP 调用节。


## 认证和积分问题

按 `onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。WorkBuddy 自动注入 Authorization；不得收集或传入 Key/token。


## 官方参考

Payment 模块索引：[v2.payment.get_escrow_detail](https://open.shopee.com/documents/v2/v2.payment.get_escrow_detail?module=97&type=1)

---

## Prerequisites（必须先读）

先用 `shopee/authorizedStores` 按 `shopId`/`merchantId + appType` 确认授权；缺失时按授权 reference 获取新授权 URL。

---

## Core Concepts

- **转发链路**：`developerProxy`（`shopId`/`merchantId` 选店，服务端注入 token）→ 紫鸟 `shopee-proxy` → Shopee API
- **Escrow**：订单托管/结算明细 → `get_escrow_detail`（需 `order_sn`）
- **Payout**：打款 → `get_payout_detail`、`get_payout_info`
- **钱包**：`get_wallet_transaction_list`
- **收入报表**：`generate_income_*` 异步生成 → `get_income_*` 获取结果
- **订单查询** → `linkfox-shopee-store-orders`；本 skill 负责**资金/结算**



## Usage Scenarios

### 1. 查订单结算明细
1. orders skill 获取 `order_sn`
2. `get_escrow_detail`：`order_sn`

### 2. 查打款与钱包
- `get_payout_detail` / `get_payout_info`
- `get_wallet_transaction_list`

### 3. 收入报表
1. `generate_income_report` 或 `generate_income_statement`
2. `get_income_report` / `get_income_statement` 取结果

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 字段
- GET：业务参数放 JSON 顶层
- POST：传 `body` 或顶层 body 字段
- 每个 operation 文档 含 **官方文档 URL**（`module=97`）

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 订单查询/处理 → `linkfox-shopee-store-orders`
- 促销 Discount/Voucher 等 → 非 Payment 模块

## 积分消耗规则

不消耗积分。

---

## Operation: generate_income_report

| 项 | 值 |
|----|-----|
| operation | `generate_income_report` |
| Method / path | POST `api/v2/payment/generate_income_report` |
| 官方文档 | [generate_income_report](https://open.shopee.com/documents/v2/v2.payment.generate_income_report?module=97&type=1) |
| 用途 | Generate income report async |

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
- Registry notes：Generate income report async

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
    "path": "api/v2/payment/generate_income_report",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/generate-income-report.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: generate_income_statement

| 项 | 值 |
|----|-----|
| operation | `generate_income_statement` |
| Method / path | POST `api/v2/payment/generate_income_statement` |
| 官方文档 | [generate_income_statement](https://open.shopee.com/documents/v2/v2.payment.generate_income_statement?module=97&type=1) |
| 用途 | Generate income statement async |

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
- Registry notes：Generate income statement async

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
    "path": "api/v2/payment/generate_income_statement",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/generate-income-statement.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_billing_transaction_info

| 项 | 值 |
|----|-----|
| operation | `get_billing_transaction_info` |
| Method / path | GET `api/v2/payment/get_billing_transaction_info` |
| 官方文档 | [get_billing_transaction_info](https://open.shopee.com/documents/v2/v2.payment.get_billing_transaction_info?module=97&type=1) |
| 用途 | Billing transaction info |

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
- Registry notes：Billing transaction info

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
    "path": "api/v2/payment/get_billing_transaction_info",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-billing-transaction-info.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_escrow_detail

| 项 | 值 |
|----|-----|
| operation | `get_escrow_detail` |
| Method / path | GET `api/v2/payment/get_escrow_detail` |
| 官方文档 | [get_escrow_detail](https://open.shopee.com/documents/v2/v2.payment.get_escrow_detail?module=97&type=1) |
| 用途 | Escrow/settlement detail for order |

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
- Registry notes：Escrow/settlement detail for order

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
    "path": "api/v2/payment/get_escrow_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-escrow-detail.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_escrow_detail_batch

| 项 | 值 |
|----|-----|
| operation | `get_escrow_detail_batch` |
| Method / path | POST `api/v2/payment/get_escrow_detail_batch` |
| 官方文档 | [get_escrow_detail_batch](https://open.shopee.com/documents/v2/v2.payment.get_escrow_detail_batch?module=97&type=1) |
| 用途 | Batch escrow detail; pass body with order_sn_list |

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
- Registry notes：Batch escrow detail; pass body with order_sn_list

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
    "path": "api/v2/payment/get_escrow_detail_batch",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-escrow-detail-batch.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_escrow_list

| 项 | 值 |
|----|-----|
| operation | `get_escrow_list` |
| Method / path | GET `api/v2/payment/get_escrow_list` |
| 官方文档 | [get_escrow_list](https://open.shopee.com/documents/v2/v2.payment.get_escrow_list?module=97&type=1) |
| 用途 | Escrow list; time range filters |

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
- Registry notes：Escrow list; time range filters

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
    "path": "api/v2/payment/get_escrow_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-escrow-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_income_detail

| 项 | 值 |
|----|-----|
| operation | `get_income_detail` |
| Method / path | GET `api/v2/payment/get_income_detail` |
| 官方文档 | [get_income_detail](https://open.shopee.com/documents/v2/v2.payment.get_income_detail?module=97&type=1) |
| 用途 | Income detail breakdown |

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
- Registry notes：Income detail breakdown

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
    "path": "api/v2/payment/get_income_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-income-detail.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_income_overview

| 项 | 值 |
|----|-----|
| operation | `get_income_overview` |
| Method / path | GET `api/v2/payment/get_income_overview` |
| 官方文档 | [get_income_overview](https://open.shopee.com/documents/v2/v2.payment.get_income_overview?module=97&type=1) |
| 用途 | Income overview/summary |

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
- Registry notes：Income overview/summary

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
    "path": "api/v2/payment/get_income_overview",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-income-overview.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_income_report

| 项 | 值 |
|----|-----|
| operation | `get_income_report` |
| Method / path | GET `api/v2/payment/get_income_report` |
| 官方文档 | [get_income_report](https://open.shopee.com/documents/v2/v2.payment.get_income_report?module=97&type=1) |
| 用途 | Get generated income report |

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
- Registry notes：Get generated income report

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
    "path": "api/v2/payment/get_income_report",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-income-report.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_income_statement

| 项 | 值 |
|----|-----|
| operation | `get_income_statement` |
| Method / path | GET `api/v2/payment/get_income_statement` |
| 官方文档 | [get_income_statement](https://open.shopee.com/documents/v2/v2.payment.get_income_statement?module=97&type=1) |
| 用途 | Get generated income statement |

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
- Registry notes：Get generated income statement

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
    "path": "api/v2/payment/get_income_statement",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-income-statement.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_item_installment_status

| 项 | 值 |
|----|-----|
| operation | `get_item_installment_status` |
| Method / path | GET `api/v2/payment/get_item_installment_status` |
| 官方文档 | [get_item_installment_status](https://open.shopee.com/documents/v2/v2.payment.get_item_installment_status?module=97&type=1) |
| 用途 | Item installment status |

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
- Registry notes：Item installment status

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
    "path": "api/v2/payment/get_item_installment_status",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-item-installment-status.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_payment_method_list

| 项 | 值 |
|----|-----|
| operation | `get_payment_method_list` |
| Method / path | GET `api/v2/payment/get_payment_method_list` |
| 官方文档 | [get_payment_method_list](https://open.shopee.com/documents/v2/v2.payment.get_payment_method_list?module=97&type=1) |
| 用途 | Available payment methods |

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
- Registry notes：Available payment methods

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
    "path": "api/v2/payment/get_payment_method_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-payment-method-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_payout_detail

| 项 | 值 |
|----|-----|
| operation | `get_payout_detail` |
| Method / path | GET `api/v2/payment/get_payout_detail` |
| 官方文档 | [get_payout_detail](https://open.shopee.com/documents/v2/v2.payment.get_payout_detail?module=97&type=1) |
| 用途 | Payout detail; optional payout_time_from/to |

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
- Registry notes：Payout detail; optional payout_time_from/to

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
    "path": "api/v2/payment/get_payout_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-payout-detail.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_payout_info

| 项 | 值 |
|----|-----|
| operation | `get_payout_info` |
| Method / path | GET `api/v2/payment/get_payout_info` |
| 官方文档 | [get_payout_info](https://open.shopee.com/documents/v2/v2.payment.get_payout_info?module=97&type=1) |
| 用途 | Payout summary info |

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
- Registry notes：Payout summary info

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
    "path": "api/v2/payment/get_payout_info",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-payout-info.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_shop_installment_status

| 项 | 值 |
|----|-----|
| operation | `get_shop_installment_status` |
| Method / path | GET `api/v2/payment/get_shop_installment_status` |
| 官方文档 | [get_shop_installment_status](https://open.shopee.com/documents/v2/v2.payment.get_shop_installment_status?module=97&type=1) |
| 用途 | Shop installment status |

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
- Registry notes：Shop installment status

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
    "path": "api/v2/payment/get_shop_installment_status",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-shop-installment-status.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_wallet_transaction_list

| 项 | 值 |
|----|-----|
| operation | `get_wallet_transaction_list` |
| Method / path | GET `api/v2/payment/get_wallet_transaction_list` |
| 官方文档 | [get_wallet_transaction_list](https://open.shopee.com/documents/v2/v2.payment.get_wallet_transaction_list?module=97&type=1) |
| 用途 | Wallet transactions; pagination/time filters |

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
- Registry notes：Wallet transactions; pagination/time filters

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
    "path": "api/v2/payment/get_wallet_transaction_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/get-wallet-transaction-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: set_item_installment_status

| 项 | 值 |
|----|-----|
| operation | `set_item_installment_status` |
| Method / path | POST `api/v2/payment/set_item_installment_status` |
| 官方文档 | [set_item_installment_status](https://open.shopee.com/documents/v2/v2.payment.set_item_installment_status?module=97&type=1) |
| 用途 | Set item installment status; pass body |

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
- Registry notes：Set item installment status; pass body

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
    "path": "api/v2/payment/set_item_installment_status",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/set-item-installment-status.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: set_shop_installment_status

| 项 | 值 |
|----|-----|
| operation | `set_shop_installment_status` |
| Method / path | POST `api/v2/payment/set_shop_installment_status` |
| 官方文档 | [set_shop_installment_status](https://open.shopee.com/documents/v2/v2.payment.set_shop_installment_status?module=97&type=1) |
| 用途 | Enable/disable shop installment; pass body |

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
- Registry notes：Enable/disable shop installment; pass body

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
    "path": "api/v2/payment/set_shop_installment_status",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-payment/references/apis/set-shop-installment-status.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；内部结构来源未说明 |