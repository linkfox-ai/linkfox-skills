# linkfox-shopee-store-returns

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


# Shopee 店铺 Returns

Shopee Open Platform **Returns 模块**（15 个 API）。**依赖 `linkfox-shopee-store-auth`** 选店；经 `proxy_call`（`toolName=shopee/developerProxy`） 传入 `shopId`（或 `merchantId`），由服务端解析 token 转发（`path` 须 `api/v2/returns/...`）。

## 调用方式

仅使用 `LinkFox.proxy_call`。所有 operation 的精确 `toolName` 均为 `shopee/developerProxy`；请求形状、解析顺序、去重和错误分层见上方 MCP 传输契约及各 operation 的 MCP 调用节。


## 认证和积分问题

按 `onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。WorkBuddy 自动注入 Authorization；不得收集或传入 Key/token。


## 官方参考

Returns 模块索引：[v2.returns.get_return_list](https://open.shopee.com/documents/v2/v2.returns.get_return_list?module=102&type=1)

---

## Prerequisites（必须先读）

先用 `shopee/authorizedStores` 按 `shopId`/`merchantId + appType` 确认授权；缺失时按授权 reference 获取新授权 URL。

---

## Core Concepts

- **转发链路**：`developerProxy`（`shopId`/`merchantId` 选店，服务端注入 token）→ 紫鸟 `shopee-proxy` → Shopee API
- **退货 vs 订单**：订单查询见 `linkfox-shopee-store-orders`；本 skill 处理**退货/退款/争议**
- **典型流程**：`get_return_list` → `get_return_detail` → `confirm` / `offer` / `dispute`
- **店铺级 API**：通常传 **`shopId`**



## Usage Scenarios

### 1. 查退货列表与详情
1. `get_return_list`：`page_no`、`page_size`
2. `get_return_detail`：`return_sn`

### 2. 处理退货
1. `get_available_solutions`：`return_sn`
2. `confirm` 或 `offer`：POST `body`
3. 如有争议：`dispute` / `cancel_dispute`

### 3. 凭证与逆向物流
- `upload_proof` / `query_proof`
- `get_reverse_tracking_info`

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 字段
- GET：业务参数放 JSON 顶层
- POST：复杂接口传 `body`
- 每个 operation 文档 含 **官方文档 URL**（`module=102`）

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 订单查询/取消 → `linkfox-shopee-store-orders`
- 正向物流发货 → `linkfox-shopee-store-logistics`
- 商品 listing → `linkfox-shopee-store-product`

## 积分消耗规则

不消耗积分。

---

## Operation: accept_offer

| 项 | 值 |
|----|-----|
| operation | `accept_offer` |
| Method / path | POST `api/v2/returns/accept_offer` |
| 官方文档 | [accept_offer](https://open.shopee.com/documents/v2/v2.returns.accept_offer?module=102&type=1) |
| 用途 | Accept buyer/seller offer; pass full body |

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
- Registry notes：Accept buyer/seller offer; pass full body

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
    "path": "api/v2/returns/accept_offer",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/accept-offer.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: cancel_dispute

| 项 | 值 |
|----|-----|
| operation | `cancel_dispute` |
| Method / path | POST `api/v2/returns/cancel_dispute` |
| 官方文档 | [cancel_dispute](https://open.shopee.com/documents/v2/v2.returns.cancel_dispute?module=102&type=1) |
| 用途 | Cancel dispute; pass body with return_sn |

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
- Registry notes：Cancel dispute; pass body with return_sn

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
    "path": "api/v2/returns/cancel_dispute",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/cancel-dispute.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: confirm

| 项 | 值 |
|----|-----|
| operation | `confirm` |
| Method / path | POST `api/v2/returns/confirm` |
| 官方文档 | [confirm](https://open.shopee.com/documents/v2/v2.returns.confirm?module=102&type=1) |
| 用途 | Seller confirm return; pass body with return_sn |

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
- Registry notes：Seller confirm return; pass body with return_sn

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
    "path": "api/v2/returns/confirm",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/confirm.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: convert_image

| 项 | 值 |
|----|-----|
| operation | `convert_image` |
| Method / path | POST `api/v2/returns/convert_image` |
| 官方文档 | [convert_image](https://open.shopee.com/documents/v2/v2.returns.convert_image?module=102&type=1) |
| 用途 | Convert image for return proof |

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
- Registry notes：Convert image for return proof

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
    "path": "api/v2/returns/convert_image",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/convert-image.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: dispute

| 项 | 值 |
|----|-----|
| operation | `dispute` |
| Method / path | POST `api/v2/returns/dispute` |
| 官方文档 | [dispute](https://open.shopee.com/documents/v2/v2.returns.dispute?module=102&type=1) |
| 用途 | Open return dispute; pass full body |

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
- Registry notes：Open return dispute; pass full body

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
    "path": "api/v2/returns/dispute",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/dispute.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_available_solutions

| 项 | 值 |
|----|-----|
| operation | `get_available_solutions` |
| Method / path | GET `api/v2/returns/get_available_solutions` |
| 官方文档 | [get_available_solutions](https://open.shopee.com/documents/v2/v2.returns.get_available_solutions?module=102&type=1) |
| 用途 | Available solutions for return |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `return_sn` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：Available solutions for return

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
    "path": "api/v2/returns/get_available_solutions",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/get-available-solutions.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_return_detail

| 项 | 值 |
|----|-----|
| operation | `get_return_detail` |
| Method / path | GET `api/v2/returns/get_return_detail` |
| 官方文档 | [get_return_detail](https://open.shopee.com/documents/v2/v2.returns.get_return_detail?module=102&type=1) |
| 用途 | Return detail by return_sn |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `return_sn` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：Return detail by return_sn

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
    "path": "api/v2/returns/get_return_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/get-return-detail.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_return_dispute_reason

| 项 | 值 |
|----|-----|
| operation | `get_return_dispute_reason` |
| Method / path | GET `api/v2/returns/get_return_dispute_reason` |
| 官方文档 | [get_return_dispute_reason](https://open.shopee.com/documents/v2/v2.returns.get_return_dispute_reason?module=102&type=1) |
| 用途 | Dispute reason list |

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
- Registry notes：Dispute reason list

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
    "path": "api/v2/returns/get_return_dispute_reason",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/get-return-dispute-reason.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_return_list

| 项 | 值 |
|----|-----|
| operation | `get_return_list` |
| Method / path | GET `api/v2/returns/get_return_list` |
| 官方文档 | [get_return_list](https://open.shopee.com/documents/v2/v2.returns.get_return_list?module=102&type=1) |
| 用途 | Return/refund list; optional page_no, page_size, create_time_from/to |

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
- Registry notes：Return/refund list; optional page_no, page_size, create_time_from/to

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
    "path": "api/v2/returns/get_return_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/get-return-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_reverse_tracking_info

| 项 | 值 |
|----|-----|
| operation | `get_reverse_tracking_info` |
| Method / path | GET `api/v2/returns/get_reverse_tracking_info` |
| 官方文档 | [get_reverse_tracking_info](https://open.shopee.com/documents/v2/v2.returns.get_reverse_tracking_info?module=102&type=1) |
| 用途 | Reverse logistics tracking; return_sn etc. |

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
- Registry notes：Reverse logistics tracking; return_sn etc.

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
    "path": "api/v2/returns/get_reverse_tracking_info",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/get-reverse-tracking-info.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_shipping_carrier

| 项 | 值 |
|----|-----|
| operation | `get_shipping_carrier` |
| Method / path | GET `api/v2/returns/get_shipping_carrier` |
| 官方文档 | [get_shipping_carrier](https://open.shopee.com/documents/v2/v2.returns.get_shipping_carrier?module=102&type=1) |
| 用途 | Return shipping carriers |

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
- Registry notes：Return shipping carriers

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
    "path": "api/v2/returns/get_shipping_carrier",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/get-shipping-carrier.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: offer

| 项 | 值 |
|----|-----|
| operation | `offer` |
| Method / path | POST `api/v2/returns/offer` |
| 官方文档 | [offer](https://open.shopee.com/documents/v2/v2.returns.offer?module=102&type=1) |
| 用途 | Seller offer solution; pass full body |

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
- Registry notes：Seller offer solution; pass full body

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
    "path": "api/v2/returns/offer",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/offer.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: query_proof

| 项 | 值 |
|----|-----|
| operation | `query_proof` |
| Method / path | GET `api/v2/returns/query_proof` |
| 官方文档 | [query_proof](https://open.shopee.com/documents/v2/v2.returns.query_proof?module=102&type=1) |
| 用途 | Query uploaded proof |

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
- Registry notes：Query uploaded proof

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
    "path": "api/v2/returns/query_proof",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/query-proof.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: upload_proof

| 项 | 值 |
|----|-----|
| operation | `upload_proof` |
| Method / path | POST `api/v2/returns/upload_proof` |
| 官方文档 | [upload_proof](https://open.shopee.com/documents/v2/v2.returns.upload_proof?module=102&type=1) |
| 用途 | Upload return proof; pass full body |

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
- Registry notes：Upload return proof; pass full body

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
    "path": "api/v2/returns/upload_proof",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/upload-proof.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: upload_shipping_proof

| 项 | 值 |
|----|-----|
| operation | `upload_shipping_proof` |
| Method / path | POST `api/v2/returns/upload_shipping_proof` |
| 官方文档 | [upload_shipping_proof](https://open.shopee.com/documents/v2/v2.returns.upload_shipping_proof?module=102&type=1) |
| 用途 | Upload return shipping proof |

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
- Registry notes：Upload return shipping proof

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
    "path": "api/v2/returns/upload_shipping_proof",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-returns/references/apis/upload-shipping-proof.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；内部结构来源未说明 |