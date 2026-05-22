---
name: linkfox-amazon-store-catalog
description: 亚马逊店铺商品目录 Catalog（与 linkfox-amazon-store-auth / report / listings / pricing / orders / feeds 同系列），经 /spApi/developerProxy 调用 SP-API Catalog Items：v0 listCatalogCategories；v2022-04-01（默认）或 v2020-12-01 的 searchCatalogItems、getCatalogItem。当用户提到亚马逊目录、Catalog Items、listCatalogCategories、searchCatalogItems、getCatalogItem、按 ASIN 查目录、关键词搜商品目录、类目节点、includedData、summaries/images 时触发。
---

# Amazon 店铺 Catalog Items

本 skill 与 **`linkfox-amazon-store-auth`** 等同属 **Amazon Store** 系列：先 **`POST /spApi/storeTokens`**，再 **`POST /spApi/developerProxy`** 转发 **GET**。

## 官方参考索引

| 能力 | 文档 |
|------|------|
| listCatalogCategories | [listCatalogCategories](https://developer-docs.amazon.com/sp-api/reference/listcatalogcategories) |
| searchCatalogItems | [searchCatalogItems](https://developer-docs.amazon.com/sp-api/reference/searchcatalogitems) |
| getCatalogItem | [getCatalogItem](https://developer-docs.amazon.com/sp-api/reference/getcatalogitem) |

---

## Prerequisites

1. 依赖 **`linkfox-amazon-store-auth`**；`python scripts/check_auth_dependency.py`，exit **42** 时需先安装授权 skill。
2. 应用需具备 **Catalog Items** 相关角色；`searchCatalogItems` 按 **identifiers+SKU** 检索时 query 须带 **`sellerId`**（脚本在 `identifiersType=SKU` 时自动使用入参 `sellerId`）。

---

## Current Capabilities

| 能力 | path | 脚本 |
|------|------|------|
| listCatalogCategories | `catalog/v0/categories` | `list_catalog_categories.py` |
| searchCatalogItems | `catalog/{2022-04-01\|2020-12-01}/items` | `search_catalog_items.py` |
| getCatalogItem | `catalog/{version}/items/{asin}` | `get_catalog_item.py` |

默认 Catalog Items 版本：**`2022-04-01`**；入参 **`catalogItemsVersion`** 可改为 **`2020-12-01`**。

共享模块：**`_spapi_catalog_common.py`**。

---

## Quick Parameters

- **listCatalogCategories**：`marketplaceId` + **`asin`** 或 **`sellerSku`**（二选一）。
- **searchCatalogItems**：`marketplaceIds` + **`keywords`** 或 **`identifiers` + `identifiersType`**（互斥）；可选 `includedData`、`brandNames`、`classificationIds`、`pageSize`、`pageToken`。
- **getCatalogItem**：`asin`、`marketplaceIds`；可选 `includedData`、`locale`。

---

## Scripts

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

python scripts/list_catalog_categories.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","asin":"B08N5WRWNW"}'

python scripts/search_catalog_items.py '{"sellerId":"A1...","region":"NA","marketplaceIds":["ATVPDKIKX0DER"],"keywords":["wireless mouse"]}'

python scripts/get_catalog_item.py '{"sellerId":"A1...","region":"NA","asin":"B08N5WRWNW","marketplaceIds":["ATVPDKIKX0DER"],"includedData":["summaries","images"]}'
```

---

## Display Rules

1. 先看 **`developerProxy.errcode` / `httpStatus`**，再读 **`categories`** / **`catalogItems`** / **`catalogItem`**。
2. **listCatalogCategories** 使用 v0 查询键 **`MarketplaceId`**（单数），与 search/get 的 **`marketplaceIds`** 不同。
3. 网关 path 白名单需包含 **`catalog/v0/`** 与 **`catalog/2022-04-01/`**（或 `2020-12-01`）。

---

## Important Limitations

- 本 skill 读的是 **Amazon 商品目录（Catalog）**，不是卖家订单；订单见 **`linkfox-amazon-store-orders`**。
- `includedData`、返回字段以 Amazon schema 为准，详见 **`references/api.md`**。

**Feedback：** `skillName`：`linkfox-amazon-store-catalog`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*
