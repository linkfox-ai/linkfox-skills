# linkfox-shopee-store-account-health

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


# Shopee 账户健康 Account Health

Shopee Open Platform **Account Health 模块**（6 个 API，均为 GET）。**依赖 `linkfox-shopee-store-auth`** 选店；经 `proxy_call`（`toolName=shopee/developerProxy`） 传入 `shopId`（或 `merchantId`），由服务端解析 token 转发（`path` 须 `api/v2/account_health/...`）。

## 调用方式

仅使用 `LinkFox.proxy_call`。所有 operation 的精确 `toolName` 均为 `shopee/developerProxy`；请求形状、解析顺序、去重和错误分层见上方 MCP 传输契约及各 operation 的 MCP 调用节。


## 认证和积分问题

按 `onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。WorkBuddy 自动注入 Authorization；不得收集或传入 Key/token。


## 官方参考

Account Health 模块索引：[v2.account_health.get_shop_performance](https://open.shopee.com/documents/v2/v2.account_health.get_shop_performance?module=103&type=1)

---

## Prerequisites

2. 订单详情 → `linkfox-shopee-store-orders`；商品 listing → `linkfox-shopee-store-product`。



## Usage Scenarios

### 1. 查看店铺健康概况
1. auth skill 定位 `shopId`
2. 按本页 `get_shop_performance` operation 调用
3. 对失败指标按本页 `get_metric_source_detail` operation 传 `metric_id` 下钻
4. 用 `get_late_orders` / `get_listings_with_issues` 定位问题订单或 listing

### 2. 查逾期订单（`get_late_orders`）
1. auth skill 定位 `shopId`
2. 按本页 `get_late_orders` operation 传参调用
3. 按 `late_by_days` 优先处理更紧急的订单

### 3. 查处罚与扣分记录
1. 按本页 `get_penalty_point_history` operation 查扣分
2. 按本页 `get_punishment_history` operation 查处罚（必填 `punishment_status`：`1` 进行中 / `2` 已结束）

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 订单处理 → `linkfox-shopee-store-orders`
- 商品 listing → `linkfox-shopee-store-product`
- 店铺基础信息 → `linkfox-shopee-store-shop`

## 积分消耗规则

不消耗积分。



---

## Operation: get_late_orders — 逾期订单

| 项 | 值 |
|----|-----|
| operation | `get_late_orders` |
| Method / path | GET `api/v2/account_health/get_late_orders` |
| 官方文档 | [v2.account_health.get_late_orders](https://open.shopee.com/documents/v2/v2.account_health.get_late_orders?module=103&type=1) |
| 用途 | 查询逾期未发货订单，便于优先处理 |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `page_no` | int | 否 | 页码，从 **1** 起；默认 **1** |
| `page_size` | int | 否 | 每页条数，范围 **1–100**；默认 **10** |

- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query

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
    "path": "api/v2/account_health/get_late_orders",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-account-health/references/apis/get-late-orders.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.total_count` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.late_order_list` | array | 来源以 `late_order_list[]` 明确为数组 |
| `response.late_order_list[]` | object | 数组元素；内部字段如下，其他属性来源未说明 |
| `response.late_order_list[].order_sn` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.late_order_list[].shipping_deadline` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.late_order_list[].late_by_days` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
---

## Operation: get_listings_with_issues — 问题 Listing

| 项 | 值 |
|----|-----|
| operation | `get_listings_with_issues` |
| Method / path | GET `api/v2/account_health/get_listings_with_issues` |
| 官方文档 | [v2.account_health.get_listings_with_issues](https://open.shopee.com/documents/v2/v2.account_health.get_listings_with_issues?module=103&type=1) |
| 用途 | 查询存在账户健康问题、需改进的 listing |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `page_no` | int | 否 | 页码，从 **1** 起；默认 **1** |
| `page_size` | int | 否 | 每页条数，范围 **1–100**；默认 **10** |

- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query

### 响应中 `reason` 常用值

| 值 | 说明 |
|----|------|
| `1` | Prohibited |
| `2` | Counterfeit |
| `3` | Spam |
| `4` | Inappropriate Image |
| `5` | Insufficient Info |
| `6` | Mall Listing Improvement |
| `7` | Other Listing Improvement |

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
    "path": "api/v2/account_health/get_listings_with_issues",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-account-health/references/apis/get-listings-with-issues.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.total_count` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.listing_list` | array | 来源以 `listing_list[]` 明确为数组 |
| `response.listing_list[]` | object | 数组元素；内部字段如下，其他属性来源未说明 |
| `response.listing_list[].item_id` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.listing_list[].reason` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
---

## Operation: get_metric_source_detail — 指标来源明细

| 项 | 值 |
|----|-----|
| operation | `get_metric_source_detail` |
| Method / path | GET `api/v2/account_health/get_metric_source_detail` |
| 官方文档 | [v2.account_health.get_metric_source_detail](https://open.shopee.com/documents/v2/v2.account_health.get_metric_source_detail?module=103&type=1) |
| 用途 | 按 `metric_id` 查询指标来源明细（受影响订单 / listing 等） |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `metric_id` | int | **是** | 指标 ID（通常来自 `get_shop_performance` 的 `metric_list[].metric_id`） |
| `page_no` | int | 否 | 页码，从 **1** 起；默认 **1** |
| `page_size` | int | 否 | 每页条数，范围 **1–100**；默认 **10** |

- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query

### 支持的 `metric_id` 与返回列表字段（节选）

| metric_id | 含义 | 主要列表字段 |
|-----------|------|--------------|
| `1` / `85` | Late Shipment Rate | `lsr_order_list` |
| `3` / `88` | Non-Fulfilment Rate | `nfr_order_list` |
| `4` | Preparation Time | `apt_order_list` |
| `12` | Pre-order Listing % | `pre_order_listing_list` |
| `25` / `2001–2003` | Fast Handover Rate | `fhr_order_list` |
| `42` / `91` | Cancellation Rate | `cancellation_order_list` |
| `43` / `92` | Return-refund Rate | `return_refund_order_list` |
| `52` / `53` | Listing Violations | `violation_listing_list` |

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
    "path": "api/v2/account_health/get_metric_source_detail",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-account-health/references/apis/get-metric-source-detail.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.total_count` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.<metric-specific-list>` | array | 来源写作 `*_list`，实际字段随 `metric_id` 变化 |
| `response.<metric-specific-list>[]` | object | 指标来源记录；内部字段来源未说明 |
---

## Operation: get_penalty_point_history — 扣分历史

| 项 | 值 |
|----|-----|
| operation | `get_penalty_point_history` |
| Method / path | GET `api/v2/account_health/get_penalty_point_history` |
| 官方文档 | [v2.account_health.get_penalty_point_history](https://open.shopee.com/documents/v2/v2.account_health.get_penalty_point_history?module=103&type=1) |
| 用途 | 查询**当前季度**产生的扣分（penalty point）记录 |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `page_no` | int | 否 | 页码，从 **1** 起；默认 **1** |
| `page_size` | int | 否 | 每页条数，范围 **1–100**；默认 **10** |
| `violation_type` | int | 否 | 按违规类型筛选（见下表） |

- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query

### `violation_type` 常用值

| 值 | 说明 |
|----|------|
| `5` | High Late Shipment Rate |
| `6` | High Non-fulfilment Rate |
| `7` | High number of non-fulfilled orders |
| `8` | High number of late shipped orders |
| `9` | Prohibited Listings |
| `10` | Counterfeit / IP infringement |
| `11` | Spam |
| `12` | Copy/Steal images |
| `13` | Re-uploading deleted listings with no change |
| `16` | High percentage of pre-order listings |

完整枚举以官方文档为准。

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
    "path": "api/v2/account_health/get_penalty_point_history",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-account-health/references/apis/get-penalty-point-history.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.total_count` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.penalty_point_list` | array | 来源以 `penalty_point_list[]` 明确为数组 |
| `response.penalty_point_list[]` | object | 数组元素；内部字段如下，其他属性来源未说明 |
| `response.penalty_point_list[].issue_time` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.penalty_point_list[].original_point_num` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.penalty_point_list[].latest_point_num` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.penalty_point_list[].violation_type` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.penalty_point_list[].reference_id` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
---

## Operation: get_punishment_history — 处罚历史

| 项 | 值 |
|----|-----|
| operation | `get_punishment_history` |
| Method / path | GET `api/v2/account_health/get_punishment_history` |
| 官方文档 | [v2.account_health.get_punishment_history](https://open.shopee.com/documents/v2/v2.account_health.get_punishment_history?module=103&type=1) |
| 用途 | 查询**当前季度**处罚（punishment）记录 |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |
| `punishment_status` | int | **是** | `1`=Ongoing（进行中），`2`=Ended（已结束） |
| `page_no` | int | 否 | 页码，从 **1** 起；默认 **1** |
| `page_size` | int | 否 | 每页条数，范围 **1–100**；默认 **10** |

- GET：业务字段放 JSON **顶层**，调用方编码进 `queryString`（不含 `?`）
- `shopId` / `merchantId` / `skipDepCheck` 等为网关选店保留字段，不会进 Shopee query

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
    "path": "api/v2/account_health/get_punishment_history",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-account-health/references/apis/get-punishment-history.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode` 与 Shopee `response`；未提供三者的精确嵌套关系、类型或完整响应示例。旧脚本 camelCase 结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `developerProxy.httpStatus` | 来源未说明 | 来源要求先检查该状态，但未定义响应对象结构或类型 |
| `errcode` | 来源未说明 | 来源要求检查该业务错误字段，但未说明精确嵌套位置与类型 |
| `response` | 来源未说明 | Shopee operation 原始业务结果；除本节另列字段外，内部结构来源未说明 |
| `response.punishment_list` | array | 来源以 `punishment_list[]` 明确为数组 |
| `response.punishment_list[]` | object | 数组元素；内部字段如下，其他属性来源未说明 |
| `response.punishment_list[].punishment_type` | 来源未说明 | 来源列出的常见值（节选）：`103` 分类浏览不展示、`104` 搜索不展示、`105` 无法创建 listing、`106` 无法编辑 listing、`107` 无法参加营销活动、`109` 账号暂停、`1109-1112` 降低 Listing Limit、`2008` 应用 Order Limit |
| `response.punishment_list[].reason` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.punishment_list[].start_time` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.punishment_list[].end_time` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.punishment_list[].listing_limit` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.punishment_list[].order_limit` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
---

## Operation: get_shop_performance — 店铺绩效总览

| 项 | 值 |
|----|-----|
| operation | `get_shop_performance` |
| Method / path | GET `api/v2/account_health/get_shop_performance` |
| 官方文档 | [v2.account_health.get_shop_performance](https://open.shopee.com/documents/v2/v2.account_health.get_shop_performance?module=103&type=1) |
| 用途 | 查询店铺账户健康绩效指标总览（履约 / listing / 客服等） |

经 LinkFox MCP 的 `proxy_call`（`toolName=shopee/developerProxy`）转发；依赖 **`linkfox-shopee-store-auth`** 选店（传 `shopId` 或 `merchantId`）。

---

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `shopId` | string | 与 `merchantId` 二选一 | 店铺 ID（推荐） |
| `merchantId` | string | 与 `shopId` 二选一 | 商户 ID |

- 本接口**无**额外 Shopee 业务 query 参数
- GET：业务字段放 JSON **顶层**；`shopId` / `merchantId` / `skipDepCheck` 为网关选店保留字段，不会进 Shopee query

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
    "path": "api/v2/account_health/get_shop_performance",
    "method": "GET",
    "shopId": "67890",
    "queryString": "<按本 operation 参数表编码；无查询参数时省略>"
  }
}
```

返回处理：先检查 MCP `isError` 与代理层错误；代理成功后读取 structured content 或 text，text 为 JSON 字符串时只解析一次；再检查下游 `errcode`/`errorCode`/`code` 与 `errmsg`/`msg`。禁止 HTTP fallback。收费调用失败、空结果或结果不理想时不得自动重试；同一任务中相同 `toolName + arguments` 不得重复调用。

---

### 响应字段

响应来源：`skills/linkfox-shopee-store-account-health/references/apis/get-shop-performance.md` 的响应要点。来源只明确指出 `developerProxy.httpStatus`、`errcode`、Shopee `response` 以及下表业务字段；未提供完整响应示例。旧脚本结果键属于调用端解析包装，未列为下游字段。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `httpStatus` | integer | developerProxy 下游 HTTP 状态；来源示例为 `200` |
| `contentType` | string | 下游响应内容类型；来源示例为 `application/json` |
| `body` | string | 字符串化的 Shopee JSON 响应体；只解析一次 |
| `body.error` | string | Shopee 错误字段；来源示例成功时为空字符串 |
| `response` | object | Shopee operation 结果对象 |
| `response.overall_performance` | object | 来源明确为包含 `rating` 和各类 failed 计数的对象 |
| `response.overall_performance.rating` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.overall_performance.<failed-count-field>` | 来源未说明 | 来源只说明包含各类 failed 计数字段，未给出固定字段名 |
| `response.metric_list` | array | 来源以 `metric_list[]` 明确为数组 |
| `response.metric_list[]` | object | 数组元素；内部字段如下，其他属性来源未说明 |
| `response.metric_list[].metric_id` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.metric_list[].metric_name` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.metric_list[].current_period` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.metric_list[].last_period` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.metric_list[].target` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
| `response.metric_list[].unit` | 来源未说明 | 来源仅列出字段名，未提供进一步说明 |
