# Reference archive: linkfox-amazon-store-catalog

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
    "path": "catalog/2022-04-01/items",
    "method": "GET",
    "queryString": "<按本 reference 的参数规则编码；无查询参数时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-catalog/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `body` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-catalog
description: 亚马逊商品目录（Catalog Items）查询。用于按 ASIN 获取目录详情，按关键词、标识符或分类条件搜索商品，以及查询商品类目节点、标题摘要、图片和其他 includedData。用户提到亚马逊商品目录、Catalog Items、ASIN 查商品、关键词搜亚马逊商品、类目节点、商品图片或摘要、searchCatalogItems、getCatalogItem、listCatalogCategories 时触发。即使未明确说“Catalog”，只要希望查询亚马逊全站目录中的商品基础资料而不是卖家自己的 Listing，也应触发此技能；卖家 SKU 的刊登增删改查使用 linkfox-amazon-store-listings。
---

# Amazon 店铺 Catalog Items


## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


## 官方参考索引

| 能力 | 文档 |
|------|------|
| listCatalogCategories | [listCatalogCategories](https://developer-docs.amazon.com/sp-api/reference/listcatalogcategories) |
| searchCatalogItems | [searchCatalogItems](https://developer-docs.amazon.com/sp-api/reference/searchcatalogitems) |
| getCatalogItem | [getCatalogItem](https://developer-docs.amazon.com/sp-api/reference/getcatalogitem) |

---

## Prerequisites

2. 应用需具备 **Catalog Items** 相关角色；`searchCatalogItems` 按 **identifiers+SKU** 检索时 query 须带 **`sellerId`**（脚本在 `identifiersType=SKU` 时自动使用入参 `sellerId`）。

---

## Current Capabilities

| 能力 | path | 脚本 |
|------|------|------|
| listCatalogCategories | `catalog/v0/categories` | `list_catalog_categories` 操作 |
| searchCatalogItems | `catalog/{2022-04-01\|2020-12-01}/items` | `search_catalog_items` 操作 |
| getCatalogItem | `catalog/{version}/items/{asin}` | `get_catalog_item` 操作 |

默认 Catalog Items 版本：**`2022-04-01`**；入参 **`catalogItemsVersion`** 可改为 **`2020-12-01`**。

共享模块：**`_spapi_catalog_common` 操作**。

---

## Quick Parameters

- **listCatalogCategories**：`marketplaceId` + **`asin`** 或 **`sellerSku`**（二选一）。
- **searchCatalogItems**：`marketplaceIds` + **`keywords`** 或 **`identifiers` + `identifiersType`**（互斥）；可选 `includedData`、`brandNames`、`classificationIds`、`pageSize`、`pageToken`。
- **getCatalogItem**：`asin`、`marketplaceIds`；可选 `includedData`、`locale`。

---

## Scripts



---

## Display Rules

1. 先看 **`developerProxy.errcode` / `httpStatus`**，再读 **`categories`** / **`catalogItems`** / **`catalogItem`**。
2. **listCatalogCategories** 使用 v0 查询键 **`MarketplaceId`**（单数），与 search/get 的 **`marketplaceIds`** 不同。
3. 网关 path 白名单需包含 **`catalog/v0/`** 与 **`catalog/2022-04-01/`**（或 `2020-12-01`）。

---

## Important Limitations

- 本 skill 读的是 **Amazon 商品目录（Catalog）**，不是卖家订单；订单见 **`linkfox-amazon-store-orders`**。
- `includedData`、返回字段以 Amazon schema 为准，详见 **`references/api.md`**。

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

**Feedback：** `skillName`：`linkfox-amazon-store-catalog`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# linkfox-amazon-store-catalog — API 参考

经 **LinkFox** `storeTokens` + `developerProxy` 调用 SP-API **Catalog Items**（与 listings / pricing 系列相同）。


---

## 1. 脚本与 path

| 脚本 | method | path |
|------|--------|------|
| `list_catalog_categories` 操作 | GET | `catalog/v0/categories` |
| `search_catalog_items` 操作 | GET | `catalog/2022-04-01/items`（默认） |
| `get_catalog_item` 操作 | GET | `catalog/2022-04-01/items/{asin}`（默认） |

`catalogItemsVersion` 可选 **`2020-12-01`**，path 中版本段随之替换。

---

## 2. listCatalogCategories（v0）

### 入参（JSON）

| 字段 | 必填 | 说明 |
|------|------|------|
| sellerId, region | 是 | 店铺与区域 |
| marketplaceId / marketplaceIds | 是 | 仅使用**第一个**站点 ID → query **`MarketplaceId`** |
| asin / ASIN | 条件 | 与 sellerSku **二选一** |
| sellerSku / SellerSKU | 条件 | 与 asin **二选一** |

### Query（大小写敏感）

- `MarketplaceId`
- `ASIN` 或 `SellerSKU`

解析字段：**`categories`**

---

## 3. searchCatalogItems

### 入参

| 字段 | 必填 | 说明 |
|------|------|------|
| marketplaceIds | 是 | 文档通常 ≤1 个 |
| keywords | 条件 | 与 identifiers **互斥**，最多 20 个 |
| identifiers | 条件 | 最多 20 个；须配 **identifiersType** |
| identifiersType | 条件 | ASIN, EAN, GTIN, ISBN, JAN, MINSAN, SKU, UPC |
| includedData | 否 | summaries, images, attributes, salesRanks 等 |
| brandNames, classificationIds | 否 | 限缩关键词搜索 |
| locale, keywordsLocale | 否 | |
| pageSize | 否 | 1～20，默认 10 |
| pageToken | 否 | 分页 |
| catalogItemsVersion | 否 | `2022-04-01`（默认）或 `2020-12-01` |
| sellerIdForCatalog | 否 | 覆盖 query 中的 sellerId（默认用 sellerId） |

当 **identifiersType=SKU** 时，Amazon 要求 query 带 **sellerId**；脚本默认使用 JSON 里的 **sellerId**。

解析字段：**`catalogItems`**

---

## 4. getCatalogItem

| 字段 | 必填 | 说明 |
|------|------|------|
| asin | 是 | path 段 |
| marketplaceIds | 是 | |
| includedData | 否 | |
| locale | 否 | |
| catalogItemsVersion | 否 | |

解析字段：**`catalogItem`**

---

## 5. includedData 示例（2022-04-01）

`summaries`, `attributes`, `classifications`, `dimensions`, `identifiers`, `images`, `productTypes`, `relationships`, `salesRanks`, `vendorDetails`（以官方为准）。

---

## 6. 错误与白名单

- **401**：HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- **402**：HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- **403**：Catalog Items 权限不足。
- **1005**（网关）：需放行 `catalog/v0/`、`catalog/2020-12-01/`、`catalog/2022-04-01/`。
- **429**：按官方 usage plan 降频。

---

## 7. Feedback

上报时注明 **`skillName`: `linkfox-amazon-store-catalog`**。

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
