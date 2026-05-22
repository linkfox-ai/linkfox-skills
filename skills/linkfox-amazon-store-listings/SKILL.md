---
name: linkfox-amazon-store-listings
description: 亚马逊店铺 Listing 与刊登相关定义/限制（与 linkfox-amazon-store-auth / linkfox-amazon-store-report 同系列），经 LinkFox /spApi/developerProxy 调用 SP-API：Listings Items（get/search/patch/put/delete）、Listings Restrictions（getListingsRestrictions）、Product Type Definitions（searchDefinitionsProductTypes、getDefinitionsProductType）。当用户提到获取或删除 Listing、刊登限制、ASIN 能否卖、product type 定义、JSON Schema 刊登属性、searchDefinitionsProductTypes、getDefinitionsProductType、getListingsRestrictions、Listings Restrictions、亚马逊刊登列表 时触发。
---

# Amazon 店铺 Listings 与相关 API

本 skill 与 **`linkfox-amazon-store-auth`**、**`linkfox-amazon-store-report`** 同属 **Amazon Store** 系列：使用 **`POST /spApi/storeTokens`** 取 `accessToken`，再经 **`POST /spApi/developerProxy`** 转发上游 **GET**、**PATCH**、**PUT** 或 **DELETE**。

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

## Prerequisites（必须先读）

本 skill **依赖** **`linkfox-amazon-store-auth`**。流程与 `linkfox-amazon-store-report` 相同：

1. 运行 `python scripts/check_auth_dependency.py`；若 exit code **42** 且 stderr 含 `DEPENDENCY_MISSING:`，请先安装 **`linkfox-amazon-store-auth`**。
2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。

---

## Current Capabilities

| 能力 | Path 要点 | 脚本 |
|------|-----------|------|
| **获取单条 Listing** | `listings/2021-08-01/items/{sellerId}/{sku}` + Query | `scripts/get_listings_item.py` |
| **搜索刊登列表** | `listings/2021-08-01/items/{sellerId}` + Query（**无**路径尾段 SKU） | `scripts/search_listings_items.py` |
| **部分更新 Listing（PATCH）** | 同 **get** 路径 + Query + JSON body | `scripts/patch_listings_item.py` |
| **创建 / 全量更新 Listing（PUT）** | 同 **get** 路径 + Query + body；**marketplaceIds 仅 1 个** | `scripts/put_listings_item.py` |
| **删除 Listing（DELETE）** | 同 **get** 路径 + Query（**marketplaceIds 仅 1 个**） | `scripts/delete_listings_item.py` |
| **刊登限制** | `listings/2021-08-01/restrictions` + Query（asin、sellerId、marketplaceIds 等） | `scripts/get_listings_restrictions.py` |
| **搜索 Product Type** | `definitions/2020-09-01/productTypes` + Query | `scripts/search_definitions_product_types.py` |
| **获取 Product Type 定义** | `definitions/2020-09-01/productTypes/{productType}` + Query；**marketplaceIds 仅 1 个** | `scripts/get_definitions_product_type.py` |

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

- **`scripts/get_listings_item.py`** — 单条 listing。
- **`scripts/search_listings_items.py`** — 搜索列表。
- **`scripts/patch_listings_item.py`** — PATCH 部分更新。
- **`scripts/put_listings_item.py`** — PUT 创建或全量更新。
- **`scripts/delete_listings_item.py`** — DELETE 删除刊登。
- **`scripts/get_listings_restrictions.py`** — GET 刊登限制。
- **`scripts/search_definitions_product_types.py`** — GET 搜索 product type。
- **`scripts/get_definitions_product_type.py`** — GET product type JSON Schema。
- **`scripts/check_auth_dependency.py`** — 依赖检测。

示例：

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

python scripts/get_listings_item.py '{"sellerId":"A1...","region":"NA","sku":"MY-SKU","marketplaceIds":["ATVPDKIKX0DER"]}'

python scripts/search_listings_items.py '{"sellerId":"A1...","region":"NA","marketplaceIds":["ATVPDKIKX0DER"],"identifiers":["B0XXXXXXXX"],"identifiersType":"ASIN"}'

python scripts/patch_listings_item.py '{"sellerId":"A1...","region":"NA","sku":"MY-SKU","marketplaceIds":["ATVPDKIKX0DER"],"productType":"LUGGAGE","patches":[{"op":"replace","path":"/attributes/item_name","value":[{"value":"New Title","marketplace_id":"ATVPDKIKX0DER"}]}]}'

python scripts/put_listings_item.py '{"sellerId":"A1...","region":"NA","sku":"MY-SKU","marketplaceIds":["ATVPDKIKX0DER"],"productType":"LUGGAGE","requirements":"LISTING","attributes":{"item_name":[{"value":"Title","marketplace_id":"ATVPDKIKX0DER"}]}}'

python scripts/delete_listings_item.py '{"sellerId":"A1...","region":"NA","sku":"MY-SKU","marketplaceIds":["ATVPDKIKX0DER"]}'

python scripts/get_listings_restrictions.py '{"sellerId":"A1...","region":"NA","asin":"B0XXXXXXXX","marketplaceIds":["ATVPDKIKX0DER"]}'

python scripts/search_definitions_product_types.py '{"sellerId":"A1...","region":"NA","marketplaceIds":["ATVPDKIKX0DER"],"keywords":["luggage"]}'

python scripts/get_definitions_product_type.py '{"sellerId":"A1...","region":"NA","productType":"LUGGAGE","marketplaceIds":["ATVPDKIKX0DER"],"querySellerId":"A1..."}'
```

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

**Feedback：** 见 `references/api.md` 中 Feedback API，`skillName`：`linkfox-amazon-store-listings`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*
