# linkfox-shopee-store-ams

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


# Shopee 联盟营销 AMS

Shopee Open Platform **AMS（Affiliate Marketing Solutions）模块**（36 个 API）。**依赖 `linkfox-shopee-store-auth`** 选店；经 `proxy_call`（`toolName=shopee/developerProxy`） 传入 `shopId`（或 `merchantId`），由服务端解析 token 转发（`path` 须 `api/v2/ams/...`）。

## 调用方式

仅使用 `LinkFox.proxy_call`。所有 operation 的精确 `toolName` 均为 `shopee/developerProxy`；请求形状、解析顺序、去重和错误分层见上方 MCP 传输契约及各 operation 的 MCP 调用节。


## 认证和积分问题

按 `onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。WorkBuddy 自动注入 Authorization；不得收集或传入 Key/token。


## 官方参考

AMS 模块索引：[v2.ams.get_open_campaign_added_product](https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_added_product?module=127&type=1)

---

## Prerequisites（必须先读）

先用 `shopee/authorizedStores` 按 `shopId`/`merchantId + appType` 确认授权；缺失时按授权 reference 获取新授权 URL。

---

## Core Concepts

- **转发链路**：`developerProxy`（`shopId`/`merchantId` 选店，服务端注入 token）→ 紫鸟 `shopee-proxy` → Shopee API
- **Open Campaign**：开放推广，所有达人可推广 → `get_open_campaign_added_product`、`batch_add_products_to_open_campaign`
- **Targeted Campaign**：定向推广，指定达人 → `create_new_targeted_campaign`、`edit_affiliate_list_of_targeted_campaign`
- **效果**：`get_shop_performance`、`get_product_performance`、`get_affiliate_performance`
- **佣金**：`get_shop_suggested_rate`、`batch_get_products_suggested_rate`



## Usage Scenarios

### 1. 管理 Open Campaign 商品
1. `get_open_campaign_added_product` 查已加入商品
2. `get_open_campaign_not_added_product` 查可加入商品
3. `batch_add_products_to_open_campaign` 批量添加

### 2. 创建定向达人 Campaign
1. `get_recommended_affiliate_list` 选达人
2. `create_new_targeted_campaign` 传完整 `body`
3. `get_targeted_campaign_performance` 查效果

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 字段
- GET：业务参数放 JSON 顶层
- POST：复杂接口传 `body`
- 每个 operation 文档 含 **官方文档 URL**（`module=127`）

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 站内 CPC 广告 → `linkfox-shopee-store-ads`
- 商品 listing → `linkfox-shopee-store-product`
- 店铺视频 → `linkfox-shopee-store-video`
- 订单 → `linkfox-shopee-store-orders`

## 积分消耗规则

不消耗积分。

---

## Operation: add_all_products_to_open_campaign

| 项 | 值 |
|----|-----|
| operation | `add_all_products_to_open_campaign` |
| Method / path | POST `api/v2/ams/add_all_products_to_open_campaign` |
| 官方文档 | [add_all_products_to_open_campaign](https://open.shopee.com/documents/v2/v2.ams.add_all_products_to_open_campaign?module=127&type=1) |
| 用途 | Add all eligible products to Open Campaign |

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
- Registry notes：Add all eligible products to Open Campaign

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
    "path": "api/v2/ams/add_all_products_to_open_campaign",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/add-all-products-to-open-campaign.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: batch_add_products_to_open_campaign

| 项 | 值 |
|----|-----|
| operation | `batch_add_products_to_open_campaign` |
| Method / path | POST `api/v2/ams/batch_add_products_to_open_campaign` |
| 官方文档 | [batch_add_products_to_open_campaign](https://open.shopee.com/documents/v2/v2.ams.batch_add_products_to_open_campaign?module=127&type=1) |
| 用途 | Batch add products to Open Campaign |

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
- Registry notes：Batch add products to Open Campaign

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
    "path": "api/v2/ams/batch_add_products_to_open_campaign",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/batch-add-products-to-open-campaign.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: batch_edit_products_open_campaign_setting

| 项 | 值 |
|----|-----|
| operation | `batch_edit_products_open_campaign_setting` |
| Method / path | POST `api/v2/ams/batch_edit_products_open_campaign_setting` |
| 官方文档 | [batch_edit_products_open_campaign_setting](https://open.shopee.com/documents/v2/v2.ams.batch_edit_products_open_campaign_setting?module=127&type=1) |
| 用途 | Batch edit Open Campaign product settings |

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
- Registry notes：Batch edit Open Campaign product settings

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
    "path": "api/v2/ams/batch_edit_products_open_campaign_setting",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/batch-edit-products-open-campaign-setting.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: batch_get_products_suggested_rate

| 项 | 值 |
|----|-----|
| operation | `batch_get_products_suggested_rate` |
| Method / path | POST `api/v2/ams/batch_get_products_suggested_rate` |
| 官方文档 | [batch_get_products_suggested_rate](https://open.shopee.com/documents/v2/v2.ams.batch_get_products_suggested_rate?module=127&type=1) |
| 用途 | Batch get suggested commission rates |

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
- Registry notes：Batch get suggested commission rates

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
    "path": "api/v2/ams/batch_get_products_suggested_rate",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/batch-get-products-suggested-rate.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: batch_remove_products_open_campaign_setting

| 项 | 值 |
|----|-----|
| operation | `batch_remove_products_open_campaign_setting` |
| Method / path | POST `api/v2/ams/batch_remove_products_open_campaign_setting` |
| 官方文档 | [batch_remove_products_open_campaign_setting](https://open.shopee.com/documents/v2/v2.ams.batch_remove_products_open_campaign_setting?module=127&type=1) |
| 用途 | Batch remove products from Open Campaign |

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
- Registry notes：Batch remove products from Open Campaign

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
    "path": "api/v2/ams/batch_remove_products_open_campaign_setting",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/batch-remove-products-open-campaign-setting.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: create_new_targeted_campaign

| 项 | 值 |
|----|-----|
| operation | `create_new_targeted_campaign` |
| Method / path | POST `api/v2/ams/create_new_targeted_campaign` |
| 官方文档 | [create_new_targeted_campaign](https://open.shopee.com/documents/v2/v2.ams.create_new_targeted_campaign?module=127&type=1) |
| 用途 | Create targeted affiliate campaign |

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
- Registry notes：Create targeted affiliate campaign

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
    "path": "api/v2/ams/create_new_targeted_campaign",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/create-new-targeted-campaign.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: edit_affiliate_list_of_targeted_campaign

| 项 | 值 |
|----|-----|
| operation | `edit_affiliate_list_of_targeted_campaign` |
| Method / path | POST `api/v2/ams/edit_affiliate_list_of_targeted_campaign` |
| 官方文档 | [edit_affiliate_list_of_targeted_campaign](https://open.shopee.com/documents/v2/v2.ams.edit_affiliate_list_of_targeted_campaign?module=127&type=1) |
| 用途 | Edit affiliates in targeted campaign |

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
- Registry notes：Edit affiliates in targeted campaign

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
    "path": "api/v2/ams/edit_affiliate_list_of_targeted_campaign",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/edit-affiliate-list-of-targeted-campaign.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: edit_all_products_open_campaign_setting

| 项 | 值 |
|----|-----|
| operation | `edit_all_products_open_campaign_setting` |
| Method / path | POST `api/v2/ams/edit_all_products_open_campaign_setting` |
| 官方文档 | [edit_all_products_open_campaign_setting](https://open.shopee.com/documents/v2/v2.ams.edit_all_products_open_campaign_setting?module=127&type=1) |
| 用途 | Edit all products Open Campaign settings |

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
- Registry notes：Edit all products Open Campaign settings

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
    "path": "api/v2/ams/edit_all_products_open_campaign_setting",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/edit-all-products-open-campaign-setting.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: edit_product_list_of_targeted_campaign

| 项 | 值 |
|----|-----|
| operation | `edit_product_list_of_targeted_campaign` |
| Method / path | POST `api/v2/ams/edit_product_list_of_targeted_campaign` |
| 官方文档 | [edit_product_list_of_targeted_campaign](https://open.shopee.com/documents/v2/v2.ams.edit_product_list_of_targeted_campaign?module=127&type=1) |
| 用途 | Edit products in targeted campaign |

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
- Registry notes：Edit products in targeted campaign

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
    "path": "api/v2/ams/edit_product_list_of_targeted_campaign",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/edit-product-list-of-targeted-campaign.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_affiliate_performance

| 项 | 值 |
|----|-----|
| operation | `get_affiliate_performance` |
| Method / path | GET `api/v2/ams/get_affiliate_performance` |
| 官方文档 | [get_affiliate_performance](https://open.shopee.com/documents/v2/v2.ams.get_affiliate_performance?module=127&type=1) |
| 用途 | Affiliate performance |

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
- Registry notes：Affiliate performance

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
    "path": "api/v2/ams/get_affiliate_performance",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-affiliate-performance.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_auto_add_new_product_toggle_status

| 项 | 值 |
|----|-----|
| operation | `get_auto_add_new_product_toggle_status` |
| Method / path | GET `api/v2/ams/get_auto_add_new_product_toggle_status` |
| 官方文档 | [get_auto_add_new_product_toggle_status](https://open.shopee.com/documents/v2/v2.ams.get_auto_add_new_product_toggle_status?module=127&type=1) |
| 用途 | Auto-add new product toggle status |

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
- Registry notes：Auto-add new product toggle status

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
    "path": "api/v2/ams/get_auto_add_new_product_toggle_status",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-auto-add-new-product-toggle-status.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_campaign_key_metrics_performance

| 项 | 值 |
|----|-----|
| operation | `get_campaign_key_metrics_performance` |
| Method / path | GET `api/v2/ams/get_campaign_key_metrics_performance` |
| 官方文档 | [get_campaign_key_metrics_performance](https://open.shopee.com/documents/v2/v2.ams.get_campaign_key_metrics_performance?module=127&type=1) |
| 用途 | Campaign key metrics |

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
- Registry notes：Campaign key metrics

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
    "path": "api/v2/ams/get_campaign_key_metrics_performance",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-campaign-key-metrics-performance.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_content_performance

| 项 | 值 |
|----|-----|
| operation | `get_content_performance` |
| Method / path | GET `api/v2/ams/get_content_performance` |
| 官方文档 | [get_content_performance](https://open.shopee.com/documents/v2/v2.ams.get_content_performance?module=127&type=1) |
| 用途 | Content performance |

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
- Registry notes：Content performance

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
    "path": "api/v2/ams/get_content_performance",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-content-performance.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_conversion_report

| 项 | 值 |
|----|-----|
| operation | `get_conversion_report` |
| Method / path | GET `api/v2/ams/get_conversion_report` |
| 官方文档 | [get_conversion_report](https://open.shopee.com/documents/v2/v2.ams.get_conversion_report?module=127&type=1) |
| 用途 | Conversion report |

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
- Registry notes：Conversion report

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
    "path": "api/v2/ams/get_conversion_report",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-conversion-report.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_managed_affiliate_list

| 项 | 值 |
|----|-----|
| operation | `get_managed_affiliate_list` |
| Method / path | GET `api/v2/ams/get_managed_affiliate_list` |
| 官方文档 | [get_managed_affiliate_list](https://open.shopee.com/documents/v2/v2.ams.get_managed_affiliate_list?module=127&type=1) |
| 用途 | Managed affiliates |

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
- Registry notes：Managed affiliates

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
    "path": "api/v2/ams/get_managed_affiliate_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-managed-affiliate-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_open_campaign_added_product

| 项 | 值 |
|----|-----|
| operation | `get_open_campaign_added_product` |
| Method / path | GET `api/v2/ams/get_open_campaign_added_product` |
| 官方文档 | [get_open_campaign_added_product](https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_added_product?module=127&type=1) |
| 用途 | Products in Open Campaign |

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
- Registry notes：Products in Open Campaign

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
    "path": "api/v2/ams/get_open_campaign_added_product",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-open-campaign-added-product.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_open_campaign_batch_task_result

| 项 | 值 |
|----|-----|
| operation | `get_open_campaign_batch_task_result` |
| Method / path | GET `api/v2/ams/get_open_campaign_batch_task_result` |
| 官方文档 | [get_open_campaign_batch_task_result](https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_batch_task_result?module=127&type=1) |
| 用途 | Batch task result for Open Campaign ops |

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
- Registry notes：Batch task result for Open Campaign ops

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
    "path": "api/v2/ams/get_open_campaign_batch_task_result",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-open-campaign-batch-task-result.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_open_campaign_not_added_product

| 项 | 值 |
|----|-----|
| operation | `get_open_campaign_not_added_product` |
| Method / path | GET `api/v2/ams/get_open_campaign_not_added_product` |
| 官方文档 | [get_open_campaign_not_added_product](https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_not_added_product?module=127&type=1) |
| 用途 | Products not yet in Open Campaign |

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
- Registry notes：Products not yet in Open Campaign

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
    "path": "api/v2/ams/get_open_campaign_not_added_product",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-open-campaign-not-added-product.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_open_campaign_performance

| 项 | 值 |
|----|-----|
| operation | `get_open_campaign_performance` |
| Method / path | GET `api/v2/ams/get_open_campaign_performance` |
| 官方文档 | [get_open_campaign_performance](https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_performance?module=127&type=1) |
| 用途 | Open Campaign performance |

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
- Registry notes：Open Campaign performance

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
    "path": "api/v2/ams/get_open_campaign_performance",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-open-campaign-performance.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_optimization_suggestion_product

| 项 | 值 |
|----|-----|
| operation | `get_optimization_suggestion_product` |
| Method / path | GET `api/v2/ams/get_optimization_suggestion_product` |
| 官方文档 | [get_optimization_suggestion_product](https://open.shopee.com/documents/v2/v2.ams.get_optimization_suggestion_product?module=127&type=1) |
| 用途 | Product optimization suggestions |

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
- Registry notes：Product optimization suggestions

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
    "path": "api/v2/ams/get_optimization_suggestion_product",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-optimization-suggestion-product.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_performance_data_update_time

| 项 | 值 |
|----|-----|
| operation | `get_performance_data_update_time` |
| Method / path | GET `api/v2/ams/get_performance_data_update_time` |
| 官方文档 | [get_performance_data_update_time](https://open.shopee.com/documents/v2/v2.ams.get_performance_data_update_time?module=127&type=1) |
| 用途 | Performance data last update time |

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
- Registry notes：Performance data last update time

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
    "path": "api/v2/ams/get_performance_data_update_time",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-performance-data-update-time.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_product_performance

| 项 | 值 |
|----|-----|
| operation | `get_product_performance` |
| Method / path | GET `api/v2/ams/get_product_performance` |
| 官方文档 | [get_product_performance](https://open.shopee.com/documents/v2/v2.ams.get_product_performance?module=127&type=1) |
| 用途 | Product AMS performance |

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
- Registry notes：Product AMS performance

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
    "path": "api/v2/ams/get_product_performance",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-product-performance.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_recommended_affiliate_list

| 项 | 值 |
|----|-----|
| operation | `get_recommended_affiliate_list` |
| Method / path | GET `api/v2/ams/get_recommended_affiliate_list` |
| 官方文档 | [get_recommended_affiliate_list](https://open.shopee.com/documents/v2/v2.ams.get_recommended_affiliate_list?module=127&type=1) |
| 用途 | Recommended affiliates |

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
- Registry notes：Recommended affiliates

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
    "path": "api/v2/ams/get_recommended_affiliate_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-recommended-affiliate-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_shop_performance

| 项 | 值 |
|----|-----|
| operation | `get_shop_performance` |
| Method / path | GET `api/v2/ams/get_shop_performance` |
| 官方文档 | [get_shop_performance](https://open.shopee.com/documents/v2/v2.ams.get_shop_performance?module=127&type=1) |
| 用途 | Shop AMS performance |

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
- Registry notes：Shop AMS performance

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
    "path": "api/v2/ams/get_shop_performance",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-shop-performance.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_shop_suggested_rate

| 项 | 值 |
|----|-----|
| operation | `get_shop_suggested_rate` |
| Method / path | GET `api/v2/ams/get_shop_suggested_rate` |
| 官方文档 | [get_shop_suggested_rate](https://open.shopee.com/documents/v2/v2.ams.get_shop_suggested_rate?module=127&type=1) |
| 用途 | Shop suggested commission rate |

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
- Registry notes：Shop suggested commission rate

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
    "path": "api/v2/ams/get_shop_suggested_rate",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-shop-suggested-rate.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_targeted_campaign_addable_product_list

| 项 | 值 |
|----|-----|
| operation | `get_targeted_campaign_addable_product_list` |
| Method / path | GET `api/v2/ams/get_targeted_campaign_addable_product_list` |
| 官方文档 | [get_targeted_campaign_addable_product_list](https://open.shopee.com/documents/v2/v2.ams.get_targeted_campaign_addable_product_list?module=127&type=1) |
| 用途 | Products addable to targeted campaign |

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
- Registry notes：Products addable to targeted campaign

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
    "path": "api/v2/ams/get_targeted_campaign_addable_product_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-targeted-campaign-addable-product-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_targeted_campaign_list

| 项 | 值 |
|----|-----|
| operation | `get_targeted_campaign_list` |
| Method / path | GET `api/v2/ams/get_targeted_campaign_list` |
| 官方文档 | [get_targeted_campaign_list](https://open.shopee.com/documents/v2/v2.ams.get_targeted_campaign_list?module=127&type=1) |
| 用途 | Targeted campaign list |

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
- Registry notes：Targeted campaign list

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
    "path": "api/v2/ams/get_targeted_campaign_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-targeted-campaign-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_targeted_campaign_performance

| 项 | 值 |
|----|-----|
| operation | `get_targeted_campaign_performance` |
| Method / path | GET `api/v2/ams/get_targeted_campaign_performance` |
| 官方文档 | [get_targeted_campaign_performance](https://open.shopee.com/documents/v2/v2.ams.get_targeted_campaign_performance?module=127&type=1) |
| 用途 | Targeted campaign performance |

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
- Registry notes：Targeted campaign performance

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
    "path": "api/v2/ams/get_targeted_campaign_performance",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-targeted-campaign-performance.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_targeted_campaign_settings

| 项 | 值 |
|----|-----|
| operation | `get_targeted_campaign_settings` |
| Method / path | GET `api/v2/ams/get_targeted_campaign_settings` |
| 官方文档 | [get_targeted_campaign_settings](https://open.shopee.com/documents/v2/v2.ams.get_targeted_campaign_settings?module=127&type=1) |
| 用途 | Targeted campaign settings detail |

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
- Registry notes：Targeted campaign settings detail

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
    "path": "api/v2/ams/get_targeted_campaign_settings",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-targeted-campaign-settings.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_validation_list

| 项 | 值 |
|----|-----|
| operation | `get_validation_list` |
| Method / path | GET `api/v2/ams/get_validation_list` |
| 官方文档 | [get_validation_list](https://open.shopee.com/documents/v2/v2.ams.get_validation_list?module=127&type=1) |
| 用途 | Validation list |

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
- Registry notes：Validation list

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
    "path": "api/v2/ams/get_validation_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-validation-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: get_validation_report

| 项 | 值 |
|----|-----|
| operation | `get_validation_report` |
| Method / path | GET `api/v2/ams/get_validation_report` |
| 官方文档 | [get_validation_report](https://open.shopee.com/documents/v2/v2.ams.get_validation_report?module=127&type=1) |
| 用途 | Validation report |

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
- Registry notes：Validation report

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
    "path": "api/v2/ams/get_validation_report",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/get-validation-report.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: query_affiliate_list

| 项 | 值 |
|----|-----|
| operation | `query_affiliate_list` |
| Method / path | GET `api/v2/ams/query_affiliate_list` |
| 官方文档 | [query_affiliate_list](https://open.shopee.com/documents/v2/v2.ams.query_affiliate_list?module=127&type=1) |
| 用途 | Query affiliate list with filters |

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
- Registry notes：Query affiliate list with filters

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
    "path": "api/v2/ams/query_affiliate_list",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/query-affiliate-list.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: remove_all_products_open_campaign_setting

| 项 | 值 |
|----|-----|
| operation | `remove_all_products_open_campaign_setting` |
| Method / path | POST `api/v2/ams/remove_all_products_open_campaign_setting` |
| 官方文档 | [remove_all_products_open_campaign_setting](https://open.shopee.com/documents/v2/v2.ams.remove_all_products_open_campaign_setting?module=127&type=1) |
| 用途 | Remove all products from Open Campaign |

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
- Registry notes：Remove all products from Open Campaign

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
    "path": "api/v2/ams/remove_all_products_open_campaign_setting",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/remove-all-products-open-campaign-setting.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: terminate_targeted_campaign

| 项 | 值 |
|----|-----|
| operation | `terminate_targeted_campaign` |
| Method / path | POST `api/v2/ams/terminate_targeted_campaign` |
| 官方文档 | [terminate_targeted_campaign](https://open.shopee.com/documents/v2/v2.ams.terminate_targeted_campaign?module=127&type=1) |
| 用途 | Terminate targeted campaign |

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
- Registry notes：Terminate targeted campaign

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
    "path": "api/v2/ams/terminate_targeted_campaign",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/terminate-targeted-campaign.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: update_auto_add_new_product_setting

| 项 | 值 |
|----|-----|
| operation | `update_auto_add_new_product_setting` |
| Method / path | POST `api/v2/ams/update_auto_add_new_product_setting` |
| 官方文档 | [update_auto_add_new_product_setting](https://open.shopee.com/documents/v2/v2.ams.update_auto_add_new_product_setting?module=127&type=1) |
| 用途 | Update auto-add new product setting |

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
- Registry notes：Update auto-add new product setting

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
    "path": "api/v2/ams/update_auto_add_new_product_setting",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/update-auto-add-new-product-setting.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
---

## Operation: update_basic_info_of_targeted_campaign

| 项 | 值 |
|----|-----|
| operation | `update_basic_info_of_targeted_campaign` |
| Method / path | POST `api/v2/ams/update_basic_info_of_targeted_campaign` |
| 官方文档 | [update_basic_info_of_targeted_campaign](https://open.shopee.com/documents/v2/v2.ams.update_basic_info_of_targeted_campaign?module=127&type=1) |
| 用途 | Update targeted campaign basic info |

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
- Registry notes：Update targeted campaign basic info

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
    "path": "api/v2/ams/update_basic_info_of_targeted_campaign",
    "method": "POST",
    "shopId": "67890",
    "body": "<按本 operation 参数表构造的 JSON 字符串；无请求体时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-ams/references/apis/update-basic-info-of-targeted-campaign.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；内部结构来源未说明 |