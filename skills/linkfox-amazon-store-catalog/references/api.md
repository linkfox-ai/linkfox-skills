# linkfox-amazon-store-catalog — API 参考

经 **LinkFox** `storeTokens` + `developerProxy` 调用 SP-API **Catalog Items**（与 listings / pricing 系列相同）。

环境变量：`LINKFOX_AGENT_API_KEY`（或 `LINKFOXAGENT_API_KEY`）；可选 `LINKFOX_TOOL_GATEWAY`（回退 `STORE_API_BASE_URL` / `SPAPI_BASE_URL`，默认 `https://tool-gateway.linkfox.com`）。

---

## 1. 脚本与 path

| 脚本 | method | path |
|------|--------|------|
| `list_catalog_categories.py` | GET | `catalog/v0/categories` |
| `search_catalog_items.py` | GET | `catalog/2022-04-01/items`（默认） |
| `get_catalog_item.py` | GET | `catalog/2022-04-01/items/{asin}`（默认） |

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

- **403**：Catalog Items 权限不足。
- **1005**（网关）：需放行 `catalog/v0/`、`catalog/2020-12-01/`、`catalog/2022-04-01/`。
- **429**：按官方 usage plan 降频。

---

## 7. Feedback

上报时注明 **`skillName`: `linkfox-amazon-store-catalog`**。
