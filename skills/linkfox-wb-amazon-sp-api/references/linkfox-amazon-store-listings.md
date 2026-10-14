# Reference archive: linkfox-amazon-store-listings

本文件归档该子能力的执行说明、API 契约、参数约束、错误处理和工作流；按需阅读相关章节。

## Capability instructions


## MCP 调用

| 项 | 值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `spApi/developerProxy` |
| `arguments` | 直接使用本 reference 对应的网关请求对象 |

```json
{
  "toolName": "spApi/developerProxy",
  "arguments": {
    "sellerId": "A1234567890",
    "region": "NA",
    "path": "listings/2021-08-01/items/{sellerId}/{sku}",
    "method": "GET",
    "queryString": "<按本 reference 的参数规则编码；无查询参数时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-listings/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `body` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `items` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `numberOfResults` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `pagination` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-listings
description: 亚马逊卖家 Listing 刊登与商品类型定义管理。用于按 SKU 查询或搜索 Listing，创建、全量更新、局部修改和删除刊登，检查 ASIN 刊登限制，并查询 product type 及其 JSON Schema 属性要求。用户提到亚马逊 Listing、刊登商品、修改商品信息、删除 Listing、卖家 SKU、ASIN 能否销售、刊登限制、product type、商品类型定义、JSON Schema、Listings Items、Listings Restrictions 时触发。即使未明确提及 API，只要希望管理卖家自己的商品刊登或确认上架所需字段与资格，也应触发此技能；查询亚马逊全站商品目录使用 linkfox-amazon-store-catalog，批量提交使用 linkfox-amazon-store-feeds。
---

# Amazon 店铺 Listings 与相关 API


| 操作 | 官方参考 |
|------|----------|
| 单条刊登 | [getListingsItem](https://developer-docs.amazon.com/sp-api/reference/getlistingsitem) |
| 检索列表 | [searchListingsItems](https://developer-docs.amazon.com/sp-api/reference/searchlistingsitems) |
| 部分更新刊登 | [patchListingsItem](https://developer-docs.amazon.com/sp-api/reference/patchlistingsitem) |
| 创建 / 全量更新刊登 | [putListingsItem](https://developer-docs.amazon.com/sp-api/reference/putlistingsitem) |
| 删除刊登 | [deleteListingsItem](https://developer-docs.amazon.com/sp-api/reference/deletelistingsitem) |
| 刊登限制（ASIN） | [getListingsRestrictions](https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions) |
| 搜索 product type | [searchDefinitionsProductTypes](https://developer-docs.amazon.com/sp-api/reference/searchdefinitionsproducttypes) |
| 获取 product type 定义 | [getDefinitionsProductType](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype) |

---

## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## Prerequisites（必须先读）

本 skill **依赖** **`linkfox-amazon-store-auth`**。流程与 `linkfox-amazon-store-report` 相同：

2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。

---

## Current Capabilities

| 能力 | Path 要点 | 脚本 |
|------|-----------|------|
| **获取单条 Listing** | `listings/2021-08-01/items/{sellerId}/{sku}` + Query | `get_listings_item` 操作 |
| **搜索刊登列表** | `listings/2021-08-01/items/{sellerId}` + Query（**无**路径尾段 SKU） | `search_listings_items` 操作 |
| **部分更新 Listing（PATCH）** | 同 **get** 路径 + Query + JSON body | `patch_listings_item` 操作 |
| **创建 / 全量更新 Listing（PUT）** | 同 **get** 路径 + Query + body；**marketplaceIds 仅 1 个** | `put_listings_item` 操作 |
| **删除 Listing（DELETE）** | 同 **get** 路径 + Query（**marketplaceIds 仅 1 个**） | `delete_listings_item` 操作 |
| **刊登限制** | `listings/2021-08-01/restrictions` + Query（asin、sellerId、marketplaceIds 等） | `get_listings_restrictions` 操作 |
| **搜索 Product Type** | `definitions/2020-09-01/productTypes` + Query | `search_definitions_product_types` 操作 |
| **获取 Product Type 定义** | `definitions/2020-09-01/productTypes/{productType}` + Query；**marketplaceIds 仅 1 个** | `get_definitions_product_type` 操作 |

**searchListingsItems** 下 `identifiers` / `variationParentSku` / `packageHierarchySku` **三者互斥**（仅该接口；见 **`references/api.md`**）。**searchDefinitionsProductTypes** 下 **`keywords`** 与 **`itemName`** **互斥**。

---

## Quick Parameters

### getListingsItem（单条）

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | **卖家 SKU**（非 ASIN） |
| marketplaceIds | 是 | 建议仅 **一个** marketplace id |
| includedData / issueLocale | 否 | 见 `references/api.md` |

### searchListingsItems（列表）

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceIds | 是 | 建议仅 **一个** marketplace id |
| identifiers + identifiersType | 否 | 最多 **20** 个；与 `variationParentSku`、`packageHierarchySku` **不能同用** |
| variationParentSku / packageHierarchySku | 否 | 与 identifiers **互斥** |
| 时间窗 / 状态 / 排序 / 分页 | 否 | `createdAfter`、`lastUpdatedBefore`、`withStatus`、`sortBy`、`pageSize`（≤20）、`pageToken` 等，见 **`references/api.md`** |

### patchListingsItem（部分更新）

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | **卖家 SKU** |
| marketplaceIds | 是 | 数组或逗号字符串；脚本拼入 Query |
| productType | 是 | Amazon product type |
| patches | 是 | **至少 1 条** JSON Patch（`op`、`path` 等） |
| includedData / mode / issueLocale | 否 | 见 **`references/api.md`** |

### putListingsItem（创建 / 全量更新）

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | **卖家 SKU** |
| marketplaceIds | 是 | **恰好一个** marketplace id |
| productType | 是 | Amazon product type |
| requirements | 是 | `LISTING` \| `LISTING_PRODUCT_ONLY` \| `LISTING_OFFER_ONLY` |
| attributes | 是 | 须符合该 product type schema |
| includedData / mode / issueLocale | 否 | 见 **`references/api.md`** |

### deleteListingsItem（删除）

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 已授权 Seller ID |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | **卖家 SKU** |
| marketplaceIds | 是 | **恰好一个** marketplace id |
| issueLocale | 否 | 见 **`references/api.md`** |

### getListingsRestrictions

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 用于 `storeTokens` 与 Query |
| region | 是 | `NA` / `EU` / `FE` |
| asin | 是 | 目录 ASIN |
| marketplaceIds | 是 | 数组或逗号字符串 |
| conditionType / reasonLocale | 否 | 见 **`references/api.md`** |

### searchDefinitionsProductTypes

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 用于 `storeTokens` |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceIds | 是 | 数组或逗号字符串 |
| keywords **或** itemName | 否 | **二者不可同时传**（非空时互斥） |
| locale / searchLocale | 否 | 见 **`references/api.md`** |

### getDefinitionsProductType

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId | 是 | 用于 `storeTokens` |
| region | 是 | `NA` / `EU` / `FE` |
| productType | 是 | 如 `LUGGAGE`（写入 path） |
| marketplaceIds | 是 | **恰好一个** id |
| querySellerId | 否 | 若需上游 Query **`sellerId`**（卖家专属 schema），传入；常与 `sellerId` 相同 |
| productTypeVersion / requirements / requirementsEnforced / locale | 否 | 见 **`references/api.md`** |

---

## Scripts

- **`get_listings_item` 操作** — 单条 listing。
- **`search_listings_items` 操作** — 搜索列表。
- **`patch_listings_item` 操作** — PATCH 部分更新。
- **`put_listings_item` 操作** — PUT 创建或全量更新。
- **`delete_listings_item` 操作** — DELETE 删除刊登。
- **`get_listings_restrictions` 操作** — GET 刊登限制。
- **`search_definitions_product_types` 操作** — GET 搜索 product type。
- **`get_definitions_product_type` 操作** — GET product type JSON Schema。
- **`amazon_store_listings__check_auth_dependency` 操作** — 依赖检测。

示例：



---

## Display Rules

1. **items** 类接口：路径含 **卖家 SKU** 时强调非 ASIN；**searchListingsItems** 路径仅到 `sellerId`。
2. 展示网关结果时说明 **`errcode` / `httpStatus`**；成功后再解析 `body`（`listing` / `searchResult` / `patchResult` / `putResult` / `deleteResult` / **`restrictionsResult`** / **`productTypesSearchResult`** / **`productTypeDefinitionResult`**）。
3. **searchListingsItems** 多页：从 `searchResult` 取下一页 token（字段名以 Amazon 响应为准），传入 `pageToken`。
4. **restrictions** / **definitions** 路径与 **items** 不同；**1005** 时需为 **`listings/2021-08-01/restrictions`** 与 **`definitions/2020-09-01/productTypes`** 等前缀分别配置白名单（以运维为准）。
5. **patch** / **put** / **delete** 为写操作；**delete** 须谨慎；**put** 为全量 **`attributes`**；**patch** 仅顶层属性可 patch（以官方为准）。

---

## Important Limitations

- **marketplaceIds**：**get** / **searchListingsItems** 脚本对多 id 常仅取第一个；**put** / **delete** / **getDefinitionsProductType** 多于 1 个即报错；**patch**、**restrictions**、**searchDefinitionsProductTypes** 行为见 **`references/api.md`**。
- **searchListingsItems**：`pageSize` **≤ 20**；`identifiers` **≤ 20**。
- **patch**：`patches` 至少 1 条；JSON Patch 的 **`delete`** 与 **deleteListingsItem** 接口不同；Vendor 对部分 patch 可能 **400**。
- **put**：**LISTING_OFFER_ONLY** 对 Vendor **400**。
- **白名单**：`listings/.../items`、`listings/.../restrictions`、`definitions/2020-09-01/productTypes` 均须按需放行。

## Amazon SP-API 接口保护与重试指引

同一店铺连续收到 Amazon SP-API 的 400、403、404 或 429 时，网关会返回 450、453、454 或 459 并短暂冷却。这些自定义状态码不是 Amazon 原生状态，也不表示封号；目的是避免持续异常或高频调用扩大店铺风险。

| 状态与 message | 范围 | 触发与冷却 | 处理 |
|---|---|---|---|
| `450`：`400，请求异常，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：20 分钟 | 停止原参数重试，检查必填字段、marketplace、ID、日期和请求体 |
| `453`：`403，店铺未授权，请先授权` | 店铺全部接口 | 60 秒内超过 2 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 停止该店铺调用，检查授权、权限、店铺归属和区域 |
| `454`：`404，资源不存在，请优化您的参数` | 店铺+接口 | 60 秒内超过 3 次：5 分钟；10 分钟内超过 4 次：30 分钟 | 确认资源 ID、所属店铺/站点、资源状态和接口路径 |
| `459`：`429限流中，请降低频率` | 店铺+接口 | 首次：15 秒；2 分钟内超过 2 次：30 秒；3 分钟内超过 4 次：2 分钟 | 降低并发、分页和轮询频率并逐级退避 |

- 立即停止自动或并发重试，不得通过换脚本或重复创建任务绕过保护；优先遵循 `retryAfter`、`blockedUntil`，没有时按表中时长说明。
- 450/453/454 必须先修正参数、授权或资源标识，冷却后最多谨慎重试一次；再次触发则停止调用。453 期间停止该店铺全部 SP-API。
- 保留已有 `reportId`、`feedId` 等任务 ID；写操作结果不确定时先查询状态，不直接重放。
- 向用户先说明店铺保护，再给原因、处理和等待时间。可回复：“为保护您的亚马逊店铺安全，检测到 Amazon SP-API 连续返回{原因}，当前已进入短暂保护。请先{处理动作}，预计{等待时间}后再试；这不代表封号，也不是套餐或积分限制。”不要只说“LinkFox 限流”或“服务器繁忙”。

## 积分消耗规则

不消耗积分。

**Feedback：** 见 `references/api.md` 中 Feedback API，`skillName`：`linkfox-amazon-store-listings`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# Amazon 店铺 Listings API 参考（Listings Items / Restrictions / Product Type Definitions）

本文档描述通过 **LinkFox 店铺网关** 调用 Selling Partner API 中与刊登相关的接口：**Listings Items v2021-08-01**（`getListingsItem`、`searchListingsItems`、`patchListingsItem`、`putListingsItem`、`deleteListingsItem`）、**Listings Restrictions v2021-08-01**（`getListingsRestrictions`）、**Product Type Definitions v2020-09-01**（`searchDefinitionsProductTypes`、`getDefinitionsProductType`）。流程与 `linkfox-amazon-store-report` **完全一致**——先选店，再经 **`proxy_call` 的 `spApi/developerProxy`** 转发上游 HTTP。

> 官方参考：[getListingsItem](https://developer-docs.amazon.com/sp-api/reference/getlistingsitem) · [searchListingsItems](https://developer-docs.amazon.com/sp-api/reference/searchlistingsitems) · [patchListingsItem](https://developer-docs.amazon.com/sp-api/reference/patchlistingsitem) · [putListingsItem](https://developer-docs.amazon.com/sp-api/reference/putlistingsitem) · [deleteListingsItem](https://developer-docs.amazon.com/sp-api/reference/deletelistingsitem) · [getListingsRestrictions](https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions) · [searchDefinitionsProductTypes](https://developer-docs.amazon.com/sp-api/reference/searchdefinitionsproducttypes) · [getDefinitionsProductType](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype)（路径、Query、Body、响应以 Amazon 文档为准）。

> ⚠️ **依赖**：调用前需已安装并完成授权流程 **`linkfox-amazon-store-auth`**（`spApi/storeTokens` 等），参见本 skill 的 `SKILL.md`。

---

## 调用规范（与 store-report 相同）

| 项 | 说明 |
|----|------|
| **SP-API 转发** | `proxy_call` 的 `spApi/developerProxy`，Body 见下节 |

---

## 通用接口：`proxy_call` 的 `spApi/developerProxy`

与 `linkfox-amazon-store-report` 的 `references/api.md` 中 **Developer Proxy** 定义相同。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 是 | `NA` / `EU` / `FE`，须与店铺授权区域一致 |
| path | string | 是 | **不含** SP-API 主机名前缀，仅 **资源路径**（见下文 Listings **items** / **restrictions**、**definitions/.../productTypes** 等模板） |
| method | string | 是 | **`GET`**（读操作）、**`PATCH`**、**`PUT`** 或 **`DELETE`**（写操作） |
| queryString | string | 视操作 | **无 `?` 前缀**。各操作必填/可选 Query 见各节（**put** / **delete** / **getDefinitionsProductType** 的 `marketplaceIds` 等见官方 **length ≤ 1** 说明） |
| body | string | 视操作 | **PATCH / PUT** 时 JSON 字符串。**GET** / **DELETE** 通常不传 |
| contentType | string | 视操作 | **PATCH / PUT** 建议 **`application/json`**。**GET** / **DELETE** 通常省略 |

**网关响应**（与报告 skill 一致）：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "httpStatus": 200,
  "contentType": "application/json",
  "body": "{... Amazon 返回的 JSON 字符串 ...}"
}
```

解析步骤：**先看 `errcode`**，再 **`httpStatus`**，最后将 **`body`** 做 `JSON.parse`。

### 白名单与错误码

- `path` 必须在后端 **`sp-api.developer-proxy.allowed-path-prefixes`** 白名单内。若 **`errcode=1005`**，需联系后端放行（常见前缀，以运维为准）：
  - **`listings/2021-08-01/items`**：`get` / `patch` / `put` / `delete` 为 `.../items/{sellerId}/{sku}`，`searchListingsItems` 为 `.../items/{sellerId}`；
  - **`listings/2021-08-01/restrictions`**：`getListingsRestrictions`（**无** path 变量，固定 `.../restrictions`）；
  - **`definitions/2020-09-01/productTypes`**：`searchDefinitionsProductTypes` 与 **`getDefinitionsProductType`**（后者 path 含 **`/{productType}`** 段）。
- 网关须允许 **`PATCH`**、**`PUT`**、**`DELETE`**（及已有 **GET**）转发。
- 其它 **`errcode`** / **`httpStatus`** 含义与处置与 `linkfox-amazon-store-report` 的 `references/api.md` 中 **Error Codes** / **Developer Proxy 上游状态码** 表格一致（400 参数、403 令牌/权限、404 无此 SKU 等）。
- HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。

---

## getListingsItem — 上游语义与网关映射

### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

其中 **`{sellerId}`**、**`{sku}`** 须做 **URL path 分段编码**（例如空格、`/` 等字符）；本 reference 的请求构造使用百分号编码后拼入 `path`。


### Path 参数（写入 path 的占位段）

| 名称 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家标识，与已授权店铺一致（与 `spApi/storeTokens` 所用 `sellerId` 相同） |
| sku | string | 是 | **卖家自定义 SKU**（Seller SKU），不是 ASIN。须与 Listing 在目标站点下实际存在的 seller SKU 一致 |

### Query 参数（写入 `developerProxy.queryString`，无 `?`）

以下按 Amazon 文档整理；**键名大小写**须与官方一致。

| 参数名 | 类型 | 必填 | 约束 / 说明 |
|--------|------|------|----------------|
| marketplaceIds | string | **是** | 目标 marketplace id。官方 schema 常见为 **单站点**（文档标注 length ≤ 1 时应只传 **一个** id）。多个 id 时本 reference 的请求构造 **仅取第一个** 并打 stderr 警告。示例：`ATVPDKIKX0DER`（美国）。**Query 中写法**：`marketplaceIds=ATVPDKIKX0DER`（单值；按上游参数契约编码，一般单站点即可） |
| includedData | string | 否 | 逗号分隔数据集列表，控制响应中包含哪些块。**不传**时上游通常等价于默认 **`summaries`**（以实网为准）。可选值（与官方一致）：`summaries`、`attributes`、`issues`、`offers`、`fulfillmentAvailability`、`procurement`、`relationships`、`productTypes`。示例：`includedData=summaries,attributes` |
| issueLocale | string | 否 | **issues** 等字段的本地化语言。示例：`en_US`、`fr_CA`。未传时通常使用第一个 marketplace 的默认语言；不可用回退行为以 Amazon 为准 |

### 官方默认与速率（摘要）

- **includedData** 默认集：文档为 **`summaries`**（若需结构化属性、报价、库存等，请在 `includedData` 中显式增加对应 token）。
- **Usage plan（文档默认值）**：约 **5 req/s**，burst **10**（以响应头 `x-amzn-RateLimit-Limit` 及账号实际配额为准）。

### 上游成功 / 常见错误（httpStatus）

| httpStatus | 含义（摘要） |
|------------|----------------|
| 200 | 成功，`body` 为 Listing 详情 JSON |
| 400 | Query / Path 非法或无法解析 |
| 403 | 拒绝访问（令牌、签名、权限等） |
| 404 | 指定 `sellerId`+`sku`+`marketplaceIds` 下无该 listing |
| 413 | 请求过大 |
| 415 | 不支持的媒体类型 |
| 429 | 限流 |
| 500 / 503 | 上游异常或维护 |

---

## 请求参数映射（`get_listings_item` 操作）

| 脚本 JSON 字段 | 映射到 developerProxy |
|----------------|-------------------------|
| sellerId | 用于 `storeTokens`；并编码进 `path` 第一段 |
| region | `region` |
| sku | 编码进 `path` 第二段 |
| marketplaceIds | `array[string]` 或单个 `string` → `queryString.marketplaceIds`（多元素时仅首元素） |
| includedData | 可选，`array` 用逗号拼接 → `queryString.includedData` |
| issueLocale | 可选 → `queryString.issueLocale` |

脚本在 stdout 打印 JSON：含 `developerProxy` 原始包、`resolvedPath`、`queryString`；若 `errcode==200` 且 `httpStatus==200`，额外解析 `listing` 对象（`body` 的 JSON）。

---

## searchListingsItems — 上游语义与网关映射

> 官方：[searchListingsItems](https://developer-docs.amazon.com/sp-api/reference/searchlistingsitems)

### HTTP 与方法

- **Method**：`GET`
- **资源路径**（写入 `developerProxy.path`，仅含 `sellerId`，**无**路径尾段的 SKU）：

```text
listings/2021-08-01/items/{sellerId}
```

`{sellerId}` 须 **URL 编码**（与 getListingsItem 相同约定）。

### Path 参数

| 名称 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sellerId | string | 是 | 卖家标识，与已授权店铺及 `storeTokens` 一致 |

### Query 参数（写入 `queryString`）

| 参数名 | 类型 | 必填 | 约束 / 说明 |
|--------|------|------|-------------|
| marketplaceIds | string | **是** | 文档为 **length ≤ 1** 的 marketplace id 列表（逗号分隔语义）；本 reference 的请求构造与 get 一致：**多传时仅取第一个** 并告警。示例：`ATVPDKIKX0DER` |
| issueLocale | string | 否 | 本地化 issues 等，如 `en_US`、`fr_CA`；未传时行为以 Amazon 为准 |
| includedData | string | 否 | 逗号分隔，默认文档为 **`summaries`**。可选：`summaries`、`attributes`、`issues`、`offers`、`fulfillmentAvailability`、`procurement`、`relationships`、`productTypes` |
| identifiers | string | 条件 | **最多 20 个**商品标识，逗号分隔（脚本接受 JSON 数组，输出为逗号拼接）。**与 `identifiersType` 成对出现**：传了 identifiers 必须带 identifiersType，反之亦然 |
| identifiersType | string | 条件 | 标识类型枚举：`SKU`、`ASIN`、`EAN`、`FNSKU`、`GTIN`、`ISBN`、`JAN`、`MINSAN`、`UPC`（以官方为准） |
| variationParentSku | string | 条件 | 只返回该 **父 SKU** 下的变体子体。**禁止**与 `identifiers` / `packageHierarchySku` 同时使用 |
| packageHierarchySku | string | 条件 | 返回包含或由该 SKU 构成的层级相关 listing。**禁止**与 `identifiers` / `variationParentSku` 同时使用 |
| createdAfter | string | 否 | ISO 8601 **date-time**，筛选创建时间 ≥ 该时刻 |
| createdBefore | string | 否 | ISO 8601，创建时间 ≤ 该时刻 |
| lastUpdatedAfter | string | 否 | ISO 8601，最后更新时间 ≥ 该时刻 |
| lastUpdatedBefore | string | 否 | ISO 8601，最后更新时间 ≤ 该时刻 |
| withIssueSeverity | string | 否 | 逗号分隔；取值：`ERROR`、`WARNING`（仅包含有对应严重度 issue 的刊登） |
| withStatus | string | 否 | 逗号分隔；取值：`BUYABLE`、`DISCOVERABLE`（文档注明 BUYABLE 不适用于 vendor listings） |
| withoutStatus | string | 否 | 逗号分隔；同上枚举，表示 **排除** 含该状态的刊登 |
| sortBy | string | 否 | 默认文档 **`lastUpdatedDate`**。允许：`sku`、`createdDate`、`lastUpdatedDate` |
| sortOrder | string | 否 | 默认 **`DESC`**。允许：`ASC`、`DESC` |
| pageSize | integer | 否 | 默认 **10**，**最大 20**（超出时脚本会截断为 20 并告警） |
| pageToken | string | 否 | 下一页令牌（上一页响应中的分页字段，以 `body` JSON 为准） |

### 互斥规则（官方 Note）

以下 **不能混用**（本仓库 `search_listings_items` 操作 会做校验）：

1. 使用 **`identifiers` / `identifiersType`** 时，**不得**再传 `variationParentSku` 或 `packageHierarchySku`。
2. 使用 **`variationParentSku`** 时，**不得**使用 `identifiers`（及 `identifiersType`）或 `packageHierarchySku`。
3. 使用 **`packageHierarchySku`** 时，**不得**使用 `identifiers` 或 `variationParentSku`。
4. **`variationParentSku`** 与 **`packageHierarchySku`** 亦不得同时使用。

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以 `x-amzn-RateLimit-Limit` 与账号配额为准；与 getListingsItem 的 burst 可能不同）。

### 成功响应

- **`httpStatus=200`** 时，`body` 为 JSON 字符串，通常含 **列表 + 分页**（字段名以 Amazon 响应为准，常见含 `items`、`numberOfResults`、`pagination` 等）。

---

## 请求参数映射（`search_listings_items` 操作）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId | `storeTokens` + path 编码 |
| region | `region` |
| marketplaceIds | 同 get；→ `marketplaceIds` |
| issueLocale / includedData | → Query |
| identifiers | `array` 或逗号字符串，≤20 个 → `identifiers` |
| identifiersType | → `identifiersType` |
| variationParentSku / packageHierarchySku | → 同名 Query |
| createdAfter / createdBefore / lastUpdatedAfter / lastUpdatedBefore | → 同名 Query |
| withIssueSeverity / withStatus / withoutStatus | `array` 或逗号字符串 → 逗号拼接 |
| sortBy / sortOrder / pageSize / pageToken | → 同名 Query |

成功且 `errcode==200`、`httpStatus==200` 时，脚本 stdout 中额外包含 **`searchResult`**（`body` 解析后的对象）。

---

## patchListingsItem — 上游语义与网关映射

> 官方：[patchListingsItem](https://developer-docs.amazon.com/sp-api/reference/patchlistingsitem)

仅支持对 **顶层** listing 属性做 JSON Patch；嵌套属性 patch 行为以 Amazon 文档为准。**Vendor** 场景下 **`delete`** 可能返回 **400**（官方说明）。

### HTTP 与方法

- **Method**：`PATCH`（经 `developerProxy.method` 传入 **`PATCH`**）
- **Path**（与 getListingsItem 相同，含 **sellerId** 与 **卖家 SKU**）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 逗号分隔的 marketplace id 列表（脚本接受 JSON 数组并拼为逗号）。与 get 不同，patch 文档为 **列表**；多站点时一并传入 |
| includedData | string | 否 | 逗号分隔；默认文档为 **`issues`**。可选：`identifiers`、`issues`。文档说明：**`identifiers`** 仅在 **`mode=VALIDATION_PREVIEW`** 时可请求 |
| mode | string | 否 | 枚举：**`VALIDATION_PREVIEW`**（校验预览模式，与 `includedData=identifiers` 等组合以官方为准） |
| issueLocale | string | 否 | 如 `en_US`、`fr_CA`；issues 本地化 |

### Body（`developerProxy.body`，JSON 字符串）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productType | string | **是** | Amazon **product type**（如 `LUGGAGE`、`PRODUCT` 等，须与该 listing 在目录中的类型一致，以 [Product Type Definitions](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype) 为准） |
| patches | array | **是** | **至少 1 条** [JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902) 操作（Amazon 支持子集） |

**单条 patch 对象**（`patches[]`）：

| 字段 | 必填 | 说明 |
|------|------|------|
| op | 是 | `add` \| `replace` \| `merge` \| `delete` |
| path | 是 | **JSON Pointer**，指向待修改属性（如 `/attributes/item_name`） |
| value | 视 op | `add` / `replace` / `merge` 通常需要；`delete` 可无（Vendor 可能不支持 delete） |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以响应头与账号配额为准）。

### 响应（httpStatus）

- **200**：已理解 patch 请求；是否被接受须解析 **`body`** 内 issues / status（以 Amazon 响应 schema 为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

---

## 请求参数映射（`patch_listings_item` 操作）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region / sku | `storeTokens` + `path` 编码 |
| marketplaceIds | 数组或逗号字符串 → `marketplaceIds`（Query，逗号拼接） |
| productType / patches | → **PATCH body** |
| includedData / mode / issueLocale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`patchResult`**（解析后的 `body`）。

---

## putListingsItem — 上游语义与网关映射

> 官方：[putListingsItem](https://developer-docs.amazon.com/sp-api/reference/putlistingsitem)

**创建**新刊登或对现有刊登做**全量**更新（非部分 patch）；请求体为完整 **`attributes`** 对象，须符合该 **productType** 的 JSON Schema。

### HTTP 与方法

- **Method**：`PUT`（经 `developerProxy.method` 传入 **`PUT`**）
- **Path**（与 getListingsItem / patchListingsItem 相同）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 官方约束：**length ≤ 1**（仅 **一个** marketplace id）。脚本在传入多个 id 时 **报错**（与 patch 允许多 id 不同） |
| includedData | string | 否 | 逗号分隔；默认文档为 **`issues`**。可选：`identifiers`、`issues`。**`identifiers`** 仅在 **`mode=VALIDATION_PREVIEW`** 时可请求 |
| mode | string | 否 | **`VALIDATION_PREVIEW`**（校验预览） |
| issueLocale | string | 否 | issues 本地化，如 `en_US` |

### Body（`developerProxy.body`，JSON 字符串）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productType | string | **是** | Amazon product type（与目录一致，参见 [Product Type Definitions](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype)） |
| requirements | string | **是** | **`LISTING`**（商品事实 + 销售条款）\| **`LISTING_PRODUCT_ONLY`**（仅商品事实）\| **`LISTING_OFFER_ONLY`**（仅销售条款；**Vendor 不支持**，会 **400**） |
| attributes | object | **是** | 以属性名为键的结构化刊登数据；须满足该 product type 的 schema |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**（以响应头与账号配额为准）。

### 响应（httpStatus）

- **200**：已理解创建/全量更新请求；是否被接受须解析 **`body`** 内 issues 等（以 Amazon 响应为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

---

## 请求参数映射（`put_listings_item` 操作）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region / sku | `storeTokens` + `path` 编码 |
| marketplaceIds | 数组或逗号字符串 → **恰好 1 个** id 写入 Query（多于 1 个则脚本拒绝） |
| productType / requirements / attributes | → **PUT body** |
| includedData / mode / issueLocale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`putResult`**（解析后的 `body`）。

---

## deleteListingsItem — 上游语义与网关映射

> 官方：[deleteListingsItem](https://developer-docs.amazon.com/sp-api/reference/deletelistingsitem)

删除指定 **marketplace** 下该 **sellerId + sku** 的刊登项；**无请求体**。

### HTTP 与方法

- **Method**：`DELETE`（经 `developerProxy.method` 传入 **`DELETE`**）
- **Path**（与 get / patch / put 相同）：

```text
listings/2021-08-01/items/{sellerId}/{sku}
```

两段路径均需 **URL 编码**。

### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| marketplaceIds | string | **是** | 官方约束：**length ≤ 1**（仅 **一个** marketplace id） |
| issueLocale | string | 否 | 本地化，如 `en_US`、`fr_CA` |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **5**（以响应头与账号配额为准）。

### 响应（httpStatus）

- **200**：已理解删除请求；是否被接受须解析 **`body`**（以 Amazon 响应为准）。
- **400 / 403 / 413 / 415 / 429 / 500 / 503**：与通用 SP-API 语义一致。

---

## 请求参数映射（`delete_listings_item` 操作）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region / sku | `storeTokens` + `path` 编码 |
| marketplaceIds | 数组或逗号字符串 → **恰好 1 个** id 写入 Query（多于 1 个则脚本拒绝） |
| issueLocale | 否 → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`deleteResult`**（解析后的 `body`）。

---

## getListingsRestrictions — 上游语义与网关映射

> 官方：[getListingsRestrictions](https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions)

返回目录 **ASIN** 在指定 **sellerId** 与 **marketplaceIds** 下的刊登限制。

### HTTP 与方法

- **Method**：`GET`
- **Path**（固定，无 path 参数）：

```text
listings/2021-08-01/restrictions
```

### Query 参数（`queryString`）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| asin | string | **是** | 目录 ASIN |
| sellerId | string | **是** | 卖家标识（与 `storeTokens` 所用可一致） |
| marketplaceIds | string | **是** | 逗号分隔 marketplace id 列表（脚本接受数组并拼接） |
| conditionType | string | 否 | 商品状况枚举，用于过滤限制（如 `new`、`used_like_new` 等，以官方枚举为准） |
| reasonLocale | string | 否 | 原因文案本地化，如 `en_US` |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。

### 响应

- **200**：成功返回限制信息；**404** 等资源类错误以 Amazon 为准。

---

## 请求参数映射（`get_listings_restrictions` 操作）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region | `storeTokens` |
| asin / marketplaceIds / conditionType / reasonLocale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`restrictionsResult`**。

---

## searchDefinitionsProductTypes — 上游语义与网关映射

> 官方：[searchDefinitionsProductTypes](https://developer-docs.amazon.com/sp-api/reference/searchdefinitionsproducttypes)

搜索可用的 **product type** 定义列表。

### HTTP 与方法

- **Method**：`GET`
- **Path**：

```text
definitions/2020-09-01/productTypes
```

### Query 参数

| 参数名 | 必填 | 说明 |
|--------|------|------|
| marketplaceIds | **是** | 逗号分隔（脚本接受数组） |
| keywords | 否 | 逗号分隔关键词列表；**不可与** `itemName` **同用** |
| itemName | 否 | ASIN 商品标题用于推荐 product type；**不可与** `keywords` **同用** |
| locale / searchLocale | 否 | 展示语言、搜索所用 locale |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。

---

## 请求参数映射（`search_definitions_product_types` 操作）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region | `storeTokens` |
| marketplaceIds | → Query |
| keywords / itemName | → Query（**互斥**，脚本校验） |
| locale / searchLocale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`productTypesSearchResult`**。

---

## getDefinitionsProductType — 上游语义与网关映射

> 官方：[getDefinitionsProductType](https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype)

按 **productType** 名称拉取 JSON Schema 定义。

### HTTP 与方法

- **Method**：`GET`
- **Path**：

```text
definitions/2020-09-01/productTypes/{productType}
```

`{productType}` 须 **URL 编码**（脚本使用 `urllib.parse.quote`）。

### Query 参数

| 参数名 | 必填 | 说明 |
|--------|------|------|
| marketplaceIds | **是** | 官方说明当前 **limited to one** `marketplaceId`；脚本 **多于 1 个即报错** |
| sellerId | 否 | 传入时填充卖家相关 schema；脚本字段 **`querySellerId`** → Query **`sellerId`**（避免与用于取令牌的 `sellerId` 混淆；通常可设为相同值） |
| productTypeVersion | 否 | 默认 **`LATEST`**；预发布可用 **`RELEASE_CANDIDATE`**（以官方为准） |
| requirements | 否 | `LISTING` \| `LISTING_PRODUCT_ONLY` \| `LISTING_OFFER_ONLY`（默认 **LISTING**） |
| requirementsEnforced | 否 | `ENFORCED` \| `NOT_ENFORCED` |
| locale | 否 | 展示标签等所用 locale（官方枚举见文档） |

### 速率（文档摘要）

- 默认约 **5 req/s**，burst **10**。大 schema 响应体可能较大。

---

## 请求参数映射（`get_definitions_product_type` 操作）

| 脚本 JSON 字段 | 映射 |
|----------------|------|
| sellerId / region | `storeTokens`（`sellerId` 为授权店铺） |
| productType | → path 末段（编码） |
| marketplaceIds | → Query，**恰好 1 个** id |
| querySellerId | → Query `sellerId`（可选） |
| productTypeVersion / requirements / requirementsEnforced / locale | → Query |

成功且 `errcode==200`、`httpStatus==200` 时，stdout 额外含 **`productTypeDefinitionResult`**。

---

## MCP 示例见本文开头（两步：取令牌 + 代理 GET / PATCH / PUT / DELETE）




**2）getListingsItem（path 与 query 按实际 sellerId / sku / marketplace 替换）**



> 若 `sku` 或 `sellerId` 含需编码字符，请使用与脚本一致的 **百分号编码** 后再放入 `path`。

**3）searchListingsItems（path 仅到 `sellerId`，query 含 marketplaceIds 与分页等）**



按 ASIN 搜索时，在 `queryString` 中增加 `identifiers` 与 `identifiersType`（**勿与** `variationParentSku` / `packageHierarchySku` 同用），例如：`identifiers=B08N5WRWNW&identifiersType=ASIN`（示例 ASIN 请替换为真实值）。

**4）patchListingsItem（`method` 为 `PATCH`，`body` 为 JSON 字符串；`productType` 与 `patches` 须按官方 schema 填写）**



> 上例 **`body` 仅演示字段形态**；真实 `path` / `value` 必须与 **product type JSON Schema** 一致，否则会 **400**。

**5）putListingsItem（`method` 为 `PUT`；`marketplaceIds` 在 Query 中仅 **一个** id；`body` 含 `productType`、`requirements`、`attributes`）**



> 上例 **`attributes` 仅演示键形态**；须与 **product type schema** 一致。**LISTING_OFFER_ONLY** 对 Vendor 会 **400**。

**6）deleteListingsItem（`method` 为 `DELETE`；`queryString` 仅含 **一个** `marketplaceIds`；不传 `body`）**



**7）getListingsRestrictions（固定 path `listings/2021-08-01/restrictions`，Query 含 asin、sellerId、marketplaceIds）**



**8）searchDefinitionsProductTypes（path `definitions/2020-09-01/productTypes`；`keywords` 与 `itemName` 勿同用）**



**9）getDefinitionsProductType（path 末段为 product type 名称；`marketplaceIds` 仅一个）**



---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-amazon-store-listings",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "getListingsItem / searchListingsItems / patchListingsItem / putListingsItem / deleteListingsItem / getListingsRestrictions / searchDefinitionsProductTypes / getDefinitionsProductType 结果符合预期。"
}
```

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
