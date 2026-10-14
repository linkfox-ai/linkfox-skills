# linkfox-shopee-store-shop

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


# Shopee 店铺 Shop

Shopee Open Platform **Shop 模块**（9 个 API）。**依赖 `linkfox-shopee-store-auth`** 选店；经 `proxy_call`（`toolName=shopee/developerProxy`） 传入 `shopId`（或 `merchantId`），由服务端解析 token 转发（`path` 须 `api/v2/shop/...`）。

## 调用方式

仅使用 `LinkFox.proxy_call`。所有 operation 的精确 `toolName` 均为 `shopee/developerProxy`；请求形状、解析顺序、去重和错误分层见上方 MCP 传输契约及各 operation 的 MCP 调用节。


## 认证和积分问题

按 `onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。WorkBuddy 自动注入 Authorization；不得收集或传入 Key/token。


## 官方参考

Shop 模块索引：[v2.shop.get_shop_info](https://open.shopee.com/documents/v2/v2.shop.get_shop_info?module=92&type=1)

---

## Prerequisites（必须先读）

先用 `shopee/authorizedStores` 按 `shopId`/`merchantId + appType` 确认授权；缺失时按授权 reference 获取新授权 URL。

---

## Core Concepts

- **转发链路**：`developerProxy`（`shopId`/`merchantId` 选店，服务端注入 token）→ 紫鸟 `shopee-proxy` → Shopee API
- **信息 vs 资料**：`get_shop_info` 返回 region/status/授权过期等；`get_profile` 返回店名/logo/描述
- **写操作**：`update_profile`（店名 30 天仅可改一次）、`set_shop_holiday_mode`（开启后买家无法下单）
- **仓库**：`get_warehouse_detail` 可选 `warehouse_type`（1=揽收仓，2=退货仓）
- **区域限制**：`get_br_shop_onboarding_info` 仅巴西站



## Usage Scenarios

### 1. 查看店铺基本信息
1. auth skill 定位 `shopId`
2. `get_shop_info`：region、status（NORMAL/BANNED/FROZEN）、expire_time
3. 可选 `get_profile`：店名、logo、描述

### 2. 更新店铺资料
`update_profile` 传 `shop_name` / `shop_logo` / `description` 至少一项（logo 须为 Shopee 图片 URL）

### 3. 假期模式
1. `get_shop_holiday_mode` 查当前状态
2. `set_shop_holiday_mode` 传 `holiday_mode_on: true/false`

### 4. 仓库与通知
- 仓库：`get_warehouse_detail`（可选 `warehouse_type=1|2`）
- 卖家通知：`get_shop_notification`（`page_size` 最大 50，`cursor` 分页）
- 授权品牌：`get_authorised_reseller_brand`（必填 `page_no`、`page_size` ≤30）

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 字段
- GET：业务参数放 JSON 顶层（调用方编码为 queryString）
- POST：传 `body` 或顶层 body 字段
- 每个 operation 文档 含 **官方文档 URL**（`module=92`）

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 商户信息 → `linkfox-shopee-store-merchant`
- 订单 → `linkfox-shopee-store-orders`
- 物流发货 → `linkfox-shopee-store-logistics`
- 退货退款 → `linkfox-shopee-store-returns`
- 商品 listing → `linkfox-shopee-store-product`
- 店铺分类 Shop Category → `linkfox-shopee-store-shop-category`
- 账户健康 Account Health → `linkfox-shopee-store-account-health`
- 跨境全球商品 → `linkfox-shopee-store-global-product`

## 积分消耗规则

不消耗积分。

---

## Operation: get_authorised_reseller_brand

| 项 | 值 |
|----|-----|
| operation | `get_authorised_reseller_brand` |
| Method / path | GET `api/v2/shop/get_authorised_reseller_brand` |
| 官方文档 | [get_authorised_reseller_brand](https://open.shopee.com/documents/v2/v2.shop.get_authorised_reseller_brand?module=92&type=1) |
| 用途 | page_size min 1 max 30 |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `page_size` | — | **是** | Query 必填（见 notes / 官方文档） |
| `page_no` | — | **是** | Query 必填（见 notes / 官方文档） |

- Method：**GET**
- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：page_size min 1 max 30

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
    "path": "api/v2/shop/get_authorised_reseller_brand",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/get-authorised-reseller-brand.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.is_authorised_reseller` | 来源未说明 | 来源仅列出字段名 |
| `response.total_count` | 来源未说明 | 来源仅列出字段名 |
| `response.more` | 来源未说明 | 来源仅列出字段名 |
| `response.authorised_brand_list` | array | 来源以 `authorised_brand_list[]` 明确为数组 |
| `response.authorised_brand_list[]` | object | 数组元素；内部字段来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_authorised_reseller_brand?module=92&type=1)

**Query（必填）**：`page_no`（从 1 起）、`page_size`（1–30）

---

## Operation: get_br_shop_onboarding_info

| 项 | 值 |
|----|-----|
| operation | `get_br_shop_onboarding_info` |
| Method / path | GET `api/v2/shop/get_br_shop_onboarding_info` |
| 官方文档 | [get_br_shop_onboarding_info](https://open.shopee.com/documents/v2/v2.shop.get_br_shop_onboarding_info?module=92&type=1) |
| 用途 | Brazil shop only — KYC / tax onboarding |

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
- Registry notes：Brazil shop only — KYC / tax onboarding

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
    "path": "api/v2/shop/get_br_shop_onboarding_info",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/get-br-shop-onboarding-info.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.<kyc-or-tax-field>` | 来源未说明 | 来源仅说明返回 KYC/税号相关字段，未给出具体字段名 |
| `response.onboarding_status` | 来源未说明 | 来源仅列出字段名 |
| `response.billing_address` | 来源未说明 | 来源仅列出字段名，未明确类型或内部结构 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_br_shop_onboarding_info?module=92&type=1)

**Query**：无额外业务参数

**区域**：仅巴西站。

---

## Operation: get_profile

| 项 | 值 |
|----|-----|
| operation | `get_profile` |
| Method / path | GET `api/v2/shop/get_profile` |
| 官方文档 | [get_profile](https://open.shopee.com/documents/v2/v2.shop.get_profile?module=92&type=1) |
| 用途 | shop_name, shop_logo, description; BR may include invoice_issuer |

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
- Registry notes：shop_name, shop_logo, description; BR may include invoice_issuer

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
    "path": "api/v2/shop/get_profile",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/get-profile.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.shop_name` | 来源未说明 | 来源仅列出字段名 |
| `response.shop_logo` | 来源未说明 | 来源仅列出字段名 |
| `response.description` | 来源未说明 | 来源仅列出字段名 |
| `response.invoice_issuer` | 来源未说明 | 来源说明巴西 CNPJ 卖家可能包含该字段 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_profile?module=92&type=1)

**Query**：无额外业务参数

---

## Operation: get_shop_holiday_mode

| 项 | 值 |
|----|-----|
| operation | `get_shop_holiday_mode` |
| Method / path | GET `api/v2/shop/get_shop_holiday_mode` |
| 官方文档 | [get_shop_holiday_mode](https://open.shopee.com/documents/v2/v2.shop.get_shop_holiday_mode?module=92&type=1) |
| 用途 | Returns holiday_mode_on and holiday_mode_mtime |

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
- Registry notes：Returns holiday_mode_on and holiday_mode_mtime

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
    "path": "api/v2/shop/get_shop_holiday_mode",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/get-shop-holiday-mode.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.holiday_mode_on` | 来源未说明 | 来源仅列出字段名 |
| `response.holiday_mode_mtime` | 来源未说明 | 来源仅列出字段名 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_shop_holiday_mode?module=92&type=1)

**Query**：无额外业务参数

---

## Operation: get_shop_info

| 项 | 值 |
|----|-----|
| operation | `get_shop_info` |
| Method / path | GET `api/v2/shop/get_shop_info` |
| 官方文档 | [get_shop_info](https://open.shopee.com/documents/v2/v2.shop.get_shop_info?module=92&type=1) |
| 用途 | Region, status, auth/expire time, merchant_id, fulfillment flags |

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
- Registry notes：Region, status, auth/expire time, merchant_id, fulfillment flags

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
    "path": "api/v2/shop/get_shop_info",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/get-shop-info.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.shop_name` | 来源未说明 | 来源仅列出字段名 |
| `response.region` | 来源未说明 | 来源仅列出字段名 |
| `response.status` | 来源未说明 | 来源列出的值为 `NORMAL`、`BANNED`、`FROZEN` |
| `response.is_cb` | 来源未说明 | 来源仅列出字段名 |
| `response.auth_time` | 来源未说明 | 来源仅列出字段名 |
| `response.expire_time` | 来源未说明 | 来源仅列出字段名 |
| `response.merchant_id` | 来源未说明 | 来源仅列出字段名 |
| `response.shop_fulfillment_flag` | 来源未说明 | 来源仅列出字段名 |
| `response.<sip-or-cross-border-field>` | 来源未说明 | 来源仅说明还包含 SIP/跨境直发相关字段，未给出具体字段名 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_shop_info?module=92&type=1)

**Query**：无额外业务参数（仅店铺公共 query）

---

## Operation: get_shop_notification

| 项 | 值 |
|----|-----|
| operation | `get_shop_notification` |
| Method / path | GET `api/v2/shop/get_shop_notification` |
| 官方文档 | [get_shop_notification](https://open.shopee.com/documents/v2/v2.shop.get_shop_notification?module=92&type=1) |
| 用途 | Optional cursor, page_size (default 10, max 50) |

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
- Registry notes：Optional cursor, page_size (default 10, max 50)

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
    "path": "api/v2/shop/get_shop_notification",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/get-shop-notification.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.cursor` | 来源未说明 | 来源仅列出字段名 |
| `response.data` | 来源未说明 | `data.*` 字段的父级；来源未说明其类型 |
| `response.data.title` | 来源未说明 | 来源仅列出字段名 |
| `response.data.content` | 来源未说明 | 来源仅列出字段名 |
| `response.data.create_time` | 来源未说明 | 来源仅列出字段名 |
| `response.data.url` | 来源未说明 | 来源仅列出字段名 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_shop_notification?module=92&type=1)

**Query（可选）**：`cursor`（上一页 notification_id）、`page_size`（默认 10，最大 50）

---

## Operation: get_warehouse_detail

| 项 | 值 |
|----|-----|
| operation | `get_warehouse_detail` |
| Method / path | GET `api/v2/shop/get_warehouse_detail` |
| 官方文档 | [get_warehouse_detail](https://open.shopee.com/documents/v2/v2.shop.get_warehouse_detail?module=92&type=1) |
| 用途 | Optional query warehouse_type: 1=pickup (default), 2=return |

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
- Registry notes：Optional query warehouse_type: 1=pickup (default), 2=return

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
    "path": "api/v2/shop/get_warehouse_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/get-warehouse-detail.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.warehouse_id` | 来源未说明 | 来源仅列出字段名 |
| `response.warehouse_name` | 来源未说明 | 来源仅列出字段名 |
| `response.location_id` | 来源未说明 | 来源仅列出字段名 |
| `response.address_id` | 来源未说明 | 来源仅列出字段名 |
| `response.<address-field>` | 来源未说明 | 来源仅说明还包含地址字段，未给出具体字段名 |
| `response.holiday_mode_state` | 来源未说明 | 来源仅列出字段名 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.get_warehouse_detail?module=92&type=1)

**Query（可选）**：`warehouse_type` — `1` 揽收仓（默认）、`2` 退货仓

---

## Operation: set_shop_holiday_mode

| 项 | 值 |
|----|-----|
| operation | `set_shop_holiday_mode` |
| Method / path | POST `api/v2/shop/set_shop_holiday_mode` |
| 官方文档 | [set_shop_holiday_mode](https://open.shopee.com/documents/v2/v2.shop.set_shop_holiday_mode?module=92&type=1) |
| 用途 | true=enable holiday mode (blocks new orders) |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `holiday_mode_on` | — | 是 | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：true=enable holiday mode (blocks new orders)

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
    "path": "api/v2/shop/set_shop_holiday_mode",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/set-shop-holiday-mode.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.set_shop_holiday_mode?module=92&type=1)

**Body（必填）**：`holiday_mode_on`（boolean）— `true` 开启假期模式（买家无法下单）

---

### 错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 `shopId` 与请求参数 |
| 1003 | 代理/网络异常 | 停止并报告；不得自动重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/shop/...` |

---
---

## Operation: update_profile

| 项 | 值 |
|----|-----|
| operation | `update_profile` |
| Method / path | POST `api/v2/shop/update_profile` |
| 官方文档 | [update_profile](https://open.shopee.com/documents/v2/v2.shop.update_profile?module=92&type=1) |
| 用途 | At least one body field; shop_name change limited to once per 30 days |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（通常传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐；Public 等无店铺接口可省略） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `shop_name` | — | 否（POST body） | 见 notes / 官方文档 |
| `shop_logo` | — | 否（POST body） | 见 notes / 官方文档 |
| `description` | — | 否（POST body） | 见 notes / 官方文档 |

- Method：**POST**
- POST：传 `body` / `requestBody`，或把 `body_fields` 列在 JSON 顶层
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query/body
- Registry notes：At least one body field; shop_name change limited to once per 30 days

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
    "path": "api/v2/shop/update_profile",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop/references/apis/update-profile.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

### 业务补充

[官方文档](https://open.shopee.com/documents/v2/v2.shop.update_profile?module=92&type=1)

**Body（至少一项）**：
| 字段 | 说明 |
|------|------|
| `shop_name` | 新店名（30 天内仅可改一次） |
| `shop_logo` | Shopee 图片 URL |
| `description` | 描述（≤500 字符） |

---

