---
name: linkfox-amazon-store-pricing
description: 亚马逊店铺商品定价（与 linkfox-amazon-store-auth / linkfox-amazon-store-report / linkfox-amazon-store-listings 同系列），经 /spApi/developerProxy 调用 SP-API Product Pricing：v0 的 getPricing、getCompetitivePricing、getListingOffers、getItemOffers、getItemOffersBatch、getListingOffersBatch；2022-05-01 的 getFeaturedOfferExpectedPriceBatch、getCompetitiveSummary。含 ASIN/SKU 单条与批量、FOEP、竞争摘要。当用户提到亚马逊定价、比价、低价报价、listing/item offers、batch pricing、FOEP、featured offer、competitive summary、Product Pricing、SP-API 价格 时触发。
---

# Amazon 店铺 Product Pricing

本 skill 与 **`linkfox-amazon-store-auth`**、**`linkfox-amazon-store-report`**、**`linkfox-amazon-store-listings`** 同属 **Amazon Store** 系列：先 **`POST /spApi/storeTokens`** 取 `accessToken`，再 **`POST /spApi/developerProxy`** 转发上游 **GET** 或 **POST**（与 listings 的 PUT/PATCH 代理方式一致）。

## 官方参考索引

| 能力 | 文档 |
|------|------|
| getPricing | [getPricing](https://developer-docs.amazon.com/sp-api/reference/getpricing) |
| getCompetitivePricing | [getCompetitivePricing](https://developer-docs.amazon.com/sp-api/reference/getcompetitivepricing) |
| getListingOffers | [getListingOffers](https://developer-docs.amazon.com/sp-api/reference/getlistingoffers) |
| getItemOffers | [getItemOffers](https://developer-docs.amazon.com/sp-api/reference/getitemoffers) |
| getItemOffersBatch | [getItemOffersBatch](https://developer-docs.amazon.com/sp-api/reference/getitemoffersbatch) |
| getListingOffersBatch | [getListingOffersBatch](https://developer-docs.amazon.com/sp-api/reference/getlistingoffersbatch) |
| getFeaturedOfferExpectedPriceBatch | [getFeaturedOfferExpectedPriceBatch](https://developer-docs.amazon.com/sp-api/reference/getfeaturedofferexpectedpricebatch) |
| getCompetitiveSummary | [getCompetitiveSummary](https://developer-docs.amazon.com/sp-api/reference/getcompetitivesummary) |

---

## Prerequisites（必须先读）

本 skill **依赖** **`linkfox-amazon-store-auth`**。

1. 运行 `python scripts/check_auth_dependency.py`；若 exit code **42** 且 stderr 含 `DEPENDENCY_MISSING:`，请先安装 **`linkfox-amazon-store-auth`**。
2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。

---

## Current Capabilities（脚本一览）

| 能力 | developerProxy `path`（要点） | 脚本 |
|------|------------------------------|------|
| getPricing | `products/pricing/v0/price` + Query | `get_pricing.py` |
| getCompetitivePricing | `products/pricing/v0/competitivePrice` + Query | `get_competitive_pricing.py` |
| getListingOffers | `products/pricing/v0/listings/{sku}/offers` + Query | `get_listing_offers.py` |
| getItemOffers | `products/pricing/v0/items/{asin}/offers` + Query | `get_item_offers.py` |
| getItemOffersBatch | `batches/products/pricing/v0/itemOffers`，POST JSON body | `post_item_offers_batch.py` |
| getListingOffersBatch | `batches/products/pricing/v0/listingOffers`，POST JSON body | `post_listing_offers_batch.py` |
| getFeaturedOfferExpectedPriceBatch | `batches/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice`，POST | `post_featured_offer_expected_price_batch.py` |
| getCompetitiveSummary | `batches/products/pricing/2022-05-01/items/competitiveSummary`，POST | `post_competitive_summary_batch.py` |

批量脚本（`post_*_batch.py`）在默认模式下会按 Amazon 要求**组装**子请求；高级用法可设 **`useAmazonRequestShape`: true**，直接传 **`requests`** 为官方原始数组（仍受条数上限约束）。共享逻辑见 **`scripts/_spapi_pricing_common.py`**（仅供同目录脚本 import，非独立 CLI）。

---

## Quick Parameters（摘要）

- **getPricing / getCompetitivePricing**：`sellerId`、`region`、`marketplaceId`（或 `marketplaceIds` 取首）、`itemType`、`asins` 或 `skus`（≤20）；getPricing 另有 `itemCondition`、`offerType`；getCompetitivePricing 另有 `customerType`。
- **getListingOffers / getItemOffers**：`sku`+path 或 **`asin`**+path；**`itemCondition` 必填**；可选 `customerType`。
- **Item / Listing Offers Batch**：`requests` 数组，默认每项为简化对象（见 `references/api.md`）；**1～20** 条（FOEP 批量脚本为 **最多 40** 条）。
- **getCompetitiveSummary 批量**：每项需 **`asin`**、**`marketplaceId`**、**`includedData`**（非空字符串数组）；可选 **`lowestPricedOffersInputs`**。
- **getFeaturedOfferExpectedPriceBatch**：每项需 **`marketplaceId`**、**`sku`**、**`segment`**（对象，结构以官方为准）。

---

## Scripts

- `get_pricing.py` · `get_competitive_pricing.py` · `get_listing_offers.py` · `get_item_offers.py`
- `post_item_offers_batch.py` · `post_listing_offers_batch.py` · `post_featured_offer_expected_price_batch.py` · `post_competitive_summary_batch.py`
- `check_auth_dependency.py` · `_spapi_pricing_common.py`（内部模块）

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

python scripts/get_item_offers.py '{"sellerId":"A1...","region":"NA","asin":"B0...","marketplaceId":"ATVPDKIKX0DER","itemCondition":"New"}'

python scripts/post_item_offers_batch.py '{"sellerId":"A1...","region":"NA","requests":[{"asin":"B0...","marketplaceId":"ATVPDKIKX0DER","itemCondition":"New"}]}'
```

---

## Display Rules

1. **`MarketplaceId`**（单数）与 Listings 的 `marketplaceIds` 勿混用。
2. 先看网关 **`errcode` / `httpStatus`**，再解析各脚本对应的解析字段（如 **`itemOffers`**、**`itemOffersBatch`**、**`competitiveSummary`** 等）。
3. **POST** 类接口：`stdout` 中含 **`requestBody`**（脚本组装的 Amazon 请求体），便于排查。
4. **白名单**：除 `products/pricing/...` 外，批量路径以 **`batches/products/pricing/...`** 开头；**1005** 时需后端放行对应前缀。
5. 各接口 **Usage plan** 不同（尤其 2022-05-01 批量约 **0.033 req/s**），注意 **429**。

---

## Important Limitations

- 权限：**Product Pricing** 及相关角色；部分 2022-05-01 能力可能另有应用内配置要求，以 Amazon 为准。
- **FOEP 批量**：`segment` 须符合官方模型；条数上限脚本按 **40** 校验（与文档「up to 40」一致）。
- 返回结构以 Amazon schema 为准；详见 **`references/api.md`**。

**Feedback：** 见 `references/api.md`，`skillName`：`linkfox-amazon-store-pricing`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*
