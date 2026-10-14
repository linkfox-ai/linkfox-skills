# linkfox-shopee-store-shop-flash-sale

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


# Shopee 店铺秒杀 Shop Flash Sale

Shopee Open Platform **Shop Flash Sale 模块**（11 个 API）。**依赖 `linkfox-shopee-store-auth`** 选店；经 `proxy_call`（`toolName=shopee/developerProxy`） 传入 `shopId`（或 `merchantId`），由服务端解析 token 转发（`path` 须 `api/v2/shop_flash_sale/...`）。

## 调用方式

仅使用 `LinkFox.proxy_call`。所有 operation 的精确 `toolName` 均为 `shopee/developerProxy`；请求形状、解析顺序、去重和错误分层见上方 MCP 传输契约及各 operation 的 MCP 调用节。


## 认证和积分问题

按 `onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。WorkBuddy 自动注入 Authorization；不得收集或传入 Key/token。


## 官方参考

Shop Flash Sale 模块索引：[v2.shop_flash_sale.get_time_slot_id](https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_time_slot_id?module=123&type=1)

---

## Prerequisites

2. 其它促销：Discount / Bundle Deal / Voucher / Shop Flash Sale / Follow Prize → 对应促销 skill。



## Usage Scenarios

### 1. 创建店铺秒杀
1. `get_time_slot_id` 获取可用时段
2. `create_shop_flash_sale` 创建活动
3. `add_shop_flash_sale_items` 添加商品
4. `get_shop_flash_sale_list` 确认状态

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 限时折扣 Discount → `linkfox-shopee-store-discount`
- 优惠券 Voucher → `linkfox-shopee-store-voucher`
- 商品 listing → `linkfox-shopee-store-product`

## 积分消耗规则

不消耗积分。


---

## Operation: add_shop_flash_sale_items

| 项 | 值 |
|----|-----|
| operation | `add_shop_flash_sale_items` |
| Method / path | POST `api/v2/shop_flash_sale/add_shop_flash_sale_items` |
| 官方文档 | [add_shop_flash_sale_items](https://open.shopee.com/documents/v2/v2.shop_flash_sale.add_shop_flash_sale_items?module=123&type=1) |
| 用途 | Add items to flash sale |

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
- Registry notes：Add items to flash sale

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
    "path": "api/v2/shop_flash_sale/add_shop_flash_sale_items",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/add-shop-flash-sale-items.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: create_shop_flash_sale

| 项 | 值 |
|----|-----|
| operation | `create_shop_flash_sale` |
| Method / path | POST `api/v2/shop_flash_sale/create_shop_flash_sale` |
| 官方文档 | [create_shop_flash_sale](https://open.shopee.com/documents/v2/v2.shop_flash_sale.create_shop_flash_sale?module=123&type=1) |
| 用途 | Create shop flash sale event; pass full body |

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
- Registry notes：Create shop flash sale event; pass full body

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
    "path": "api/v2/shop_flash_sale/create_shop_flash_sale",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/create-shop-flash-sale.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: delete_shop_flash_sale

| 项 | 值 |
|----|-----|
| operation | `delete_shop_flash_sale` |
| Method / path | POST `api/v2/shop_flash_sale/delete_shop_flash_sale` |
| 官方文档 | [delete_shop_flash_sale](https://open.shopee.com/documents/v2/v2.shop_flash_sale.delete_shop_flash_sale?module=123&type=1) |
| 用途 | Delete flash sale |

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
- Registry notes：Delete flash sale

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
    "path": "api/v2/shop_flash_sale/delete_shop_flash_sale",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/delete-shop-flash-sale.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: delete_shop_flash_sale_items

| 项 | 值 |
|----|-----|
| operation | `delete_shop_flash_sale_items` |
| Method / path | POST `api/v2/shop_flash_sale/delete_shop_flash_sale_items` |
| 官方文档 | [delete_shop_flash_sale_items](https://open.shopee.com/documents/v2/v2.shop_flash_sale.delete_shop_flash_sale_items?module=123&type=1) |
| 用途 | Remove items from flash sale |

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
- Registry notes：Remove items from flash sale

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
    "path": "api/v2/shop_flash_sale/delete_shop_flash_sale_items",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/delete-shop-flash-sale-items.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_item_criteria

| 项 | 值 |
|----|-----|
| operation | `get_item_criteria` |
| Method / path | GET `api/v2/shop_flash_sale/get_item_criteria` |
| 官方文档 | [get_item_criteria](https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_item_criteria?module=123&type=1) |
| 用途 | Get item eligibility criteria for flash sale |

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
- Registry notes：Get item eligibility criteria for flash sale

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
    "path": "api/v2/shop_flash_sale/get_item_criteria",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/get-item-criteria.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_shop_flash_sale

| 项 | 值 |
|----|-----|
| operation | `get_shop_flash_sale` |
| Method / path | GET `api/v2/shop_flash_sale/get_shop_flash_sale` |
| 官方文档 | [get_shop_flash_sale](https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_shop_flash_sale?module=123&type=1) |
| 用途 | Flash sale detail by flash_sale_id |

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
- Registry notes：Flash sale detail by flash_sale_id

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
    "path": "api/v2/shop_flash_sale/get_shop_flash_sale",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/get-shop-flash-sale.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_shop_flash_sale_items

| 项 | 值 |
|----|-----|
| operation | `get_shop_flash_sale_items` |
| Method / path | GET `api/v2/shop_flash_sale/get_shop_flash_sale_items` |
| 官方文档 | [get_shop_flash_sale_items](https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_shop_flash_sale_items?module=123&type=1) |
| 用途 | Items in flash sale |

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
- Registry notes：Items in flash sale

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
    "path": "api/v2/shop_flash_sale/get_shop_flash_sale_items",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/get-shop-flash-sale-items.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_shop_flash_sale_list

| 项 | 值 |
|----|-----|
| operation | `get_shop_flash_sale_list` |
| Method / path | GET `api/v2/shop_flash_sale/get_shop_flash_sale_list` |
| 官方文档 | [get_shop_flash_sale_list](https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_shop_flash_sale_list?module=123&type=1) |
| 用途 | List shop flash sales; pagination/status filters |

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
- Registry notes：List shop flash sales; pagination/status filters

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
    "path": "api/v2/shop_flash_sale/get_shop_flash_sale_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/get-shop-flash-sale-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_time_slot_id

| 项 | 值 |
|----|-----|
| operation | `get_time_slot_id` |
| Method / path | GET `api/v2/shop_flash_sale/get_time_slot_id` |
| 官方文档 | [get_time_slot_id](https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_time_slot_id?module=123&type=1) |
| 用途 | Get available flash sale time slot IDs |

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
- Registry notes：Get available flash sale time slot IDs

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
    "path": "api/v2/shop_flash_sale/get_time_slot_id",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/get-time-slot-id.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: update_shop_flash_sale

| 项 | 值 |
|----|-----|
| operation | `update_shop_flash_sale` |
| Method / path | POST `api/v2/shop_flash_sale/update_shop_flash_sale` |
| 官方文档 | [update_shop_flash_sale](https://open.shopee.com/documents/v2/v2.shop_flash_sale.update_shop_flash_sale?module=123&type=1) |
| 用途 | Update flash sale settings |

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
- Registry notes：Update flash sale settings

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
    "path": "api/v2/shop_flash_sale/update_shop_flash_sale",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/update-shop-flash-sale.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: update_shop_flash_sale_items

| 项 | 值 |
|----|-----|
| operation | `update_shop_flash_sale_items` |
| Method / path | POST `api/v2/shop_flash_sale/update_shop_flash_sale_items` |
| 官方文档 | [update_shop_flash_sale_items](https://open.shopee.com/documents/v2/v2.shop_flash_sale.update_shop_flash_sale_items?module=123&type=1) |
| 用途 | Update flash sale item settings |

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
- Registry notes：Update flash sale item settings

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
    "path": "api/v2/shop_flash_sale/update_shop_flash_sale_items",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-shop-flash-sale/references/apis/update-shop-flash-sale-items.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；内部结构来源未说明 |