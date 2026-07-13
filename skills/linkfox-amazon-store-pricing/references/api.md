# Amazon 店铺 Product Pricing API 参考（v0 + 2022-05-01 批量）

本文档描述通过 **LinkFox 店铺网关** 调用 Selling Partner API **Product Pricing**（**v0** 与 **2022-05-01** 批量）：与 `linkfox-amazon-store-report`、`linkfox-amazon-store-listings` **一致**——先 **`POST /spApi/storeTokens`** 取 `accessToken`，再经 **`POST /spApi/developerProxy`** 转发上游 **GET** 或 **POST**。

> 官方入口：[getPricing](https://developer-docs.amazon.com/sp-api/reference/getpricing) · [getCompetitivePricing](https://developer-docs.amazon.com/sp-api/reference/getcompetitivepricing) · [getListingOffers](https://developer-docs.amazon.com/sp-api/reference/getlistingoffers) · [getItemOffers](https://developer-docs.amazon.com/sp-api/reference/getitemoffers) · [getItemOffersBatch](https://developer-docs.amazon.com/sp-api/reference/getitemoffersbatch) · [getListingOffersBatch](https://developer-docs.amazon.com/sp-api/reference/getlistingoffersbatch) · [getFeaturedOfferExpectedPriceBatch](https://developer-docs.amazon.com/sp-api/reference/getfeaturedofferexpectedpricebatch) · [getCompetitiveSummary](https://developer-docs.amazon.com/sp-api/reference/getcompetitivesummary)

> ⚠️ **依赖**：需已安装并完成授权 **`linkfox-amazon-store-auth`**。应用需具备 **Product Pricing** 等相关角色/权限，否则上游可能返回 403。

---

## 调用规范（与 store-report 相同）

| 项 | 说明 |
|----|------|
| **Base URL** | `${LINKFOX_TOOL_GATEWAY}`（默认 `https://tool-gateway.linkfox.com`；可用 `STORE_API_BASE_URL` 或 `SPAPI_BASE_URL` 覆盖） |
| **网关认证** | Header `Authorization: <api_key>`，环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| **店铺令牌** | `POST /spApi/storeTokens`，Body：`{"sellerId":"...","region":"NA|EU|FE"}` → `accessToken` |
| **SP-API 转发** | `POST /spApi/developerProxy`，Body 见下节 |

---

## `POST /spApi/developerProxy`（定价类 GET / POST）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 是 | `NA` / `EU` / `FE` |
| path | string | 是 | 不含主机名。示例：**`products/pricing/v0/price`**、**`products/pricing/v0/items/{Asin}/offers`**、**`batches/products/pricing/v0/itemOffers`**、**`batches/products/pricing/2022-05-01/items/competitiveSummary`** 等（见各节） |
| method | string | 是 | **`GET`** 或 **`POST`**（与上游一致） |
| amzAccessToken | string | 是 | `/spApi/storeTokens` 返回的 `accessToken` |
| queryString | string | 视操作 | **无 `?` 前缀**。GET 定价类多 **必填**；POST 批量通常 **无** query，以 Amazon 为准 |
| body | string | 视操作 | **POST** 时多为 **JSON 字符串**（与 `put_listings_item` 相同，见 listings `references/api.md`） |
| contentType | string | 视操作 | POST 带 `body` 时一般为 **`application/json`** |

**网关响应**：`errcode`、`errmsg`、`httpStatus`、`contentType`、`body`（字符串）。先 **`errcode`**，再 **`httpStatus`**，再解析 **`body`**。

### 白名单与错误码

- `path` 须在网关 **`sp-api.developer-proxy.allowed-path-prefixes`** 内。若 **`errcode=1005`**，需联系后端放行 **`products/pricing/`** 与 **`batches/products/pricing/`** 等前缀（以运维配置为准）。
- 其它错误与 `linkfox-amazon-store-report` 的 Developer Proxy 说明一致。
- HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。
- HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。

---

## getPricing — Query 参数（写入 `queryString`）

官方参数名 **大小写敏感**。多值 **`Asins`** / **`Skus`** 采用重复键形式：`Asins=B0...&Asins=B0...`（本仓库脚本按此拼接）。

| 参数名 | 必填 | 说明 |
|--------|------|------|
| **MarketplaceId** | 是 | 单个 marketplace id，例如美国 `ATVPDKIKX0DER`。与 Listings API 的 `marketplaceIds` 不同，此处为 **单数键名** |
| **ItemType** | 是 | `Asin` 或 `Sku`（与下方 `Asins` / `Skus` 二选一对应） |
| **Asins** | 与 ItemType 对应 | 当 `ItemType=Asin` 时必填；**最多 20** 个 ASIN |
| **Skus** | 与 ItemType 对应 | 当 `ItemType=Sku` 时必填；**最多 20** 个卖家 SKU（注意 [URL 编码](https://developer-docs.amazon.com/sp-api/docs/url-encoding)） |
| **ItemCondition** | 否 | `New`、`Used`、`Collectible`、`Refurbished`、`Club` |
| **OfferType** | 否 | `B2C` 或 `B2B`；默认多为 B2C（以上游为准） |

### 速率（文档默认值，以账号实际为准）

- 约 **0.5 req/s**，burst **1**（见官方 Usage plan 表）。

---

## getCompetitivePricing — Query 参数（写入 `queryString`）

与 getPricing 相同：**`MarketplaceId`**、**`ItemType`**（`Asin` / `Sku`）、**`Asins`** 或 **`Skus`**（每请求最多 **20** 个，重复键拼接）。差异如下：

| 参数名 | 必填 | 说明 |
|--------|------|------|
| **CustomerType** | 否 | `Consumer` 或 `Business`；从 **消费者 / 企业买家** 视角看定价信息，默认多为 Consumer（以上游为准） |

**速率（文档默认值）**：约 **0.5 req/s**，burst **1**（见 [getCompetitivePricing Usage plan](https://developer-docs.amazon.com/sp-api/reference/getcompetitivepricing)）。

> getCompetitivePricing **没有** getPricing 的 `ItemCondition`、`OfferType` 参数；二者用途不同，勿混用字段名。

---

## getListingOffers — Path 与 Query

- **Path 模板**（写入 `developerProxy.path`）：

```text
products/pricing/v0/listings/{SellerSKU}/offers
```

其中 **`{SellerSKU}`** 为卖家 SKU，路径段须 **百分号编码**（与 `get_listings_item` 同理；脚本使用 `urllib.parse.quote(..., safe="")`）。

### Query（写入 `queryString`）

| 参数名 | 必填 | 说明 |
|--------|------|------|
| **MarketplaceId** | 是 | 单个 marketplace id |
| **ItemCondition** | 是 | `New`、`Used`、`Collectible`、`Refurbished`、`Club` |
| **CustomerType** | 否 | `Consumer` 或 `Business`（默认多为 Consumer，以上游为准） |

**语义**：针对**单个 SKU 刊登**返回较低报价类信息（官方描述为 lowest priced offers；具体结构见 [getListingOffers](https://developer-docs.amazon.com/sp-api/reference/getlistingoffers)）。

**速率（文档默认值）**：约 **1 req/s**，burst **2**（见官方 Usage plan）。

### 成功响应（摘要）

- **`httpStatus=200`** 时解析 `body`：`get_pricing.py` → **`pricing`**；`get_competitive_pricing.py` → **`competitivePricing`**；`get_listing_offers.py` → **`listingOffers`**；`get_item_offers.py` → **`itemOffers`**；`post_item_offers_batch.py` → **`itemOffersBatch`**；`post_listing_offers_batch.py` → **`listingOffersBatch`**；`post_featured_offer_expected_price_batch.py` → **`featuredOfferExpectedPriceBatch`**；`post_competitive_summary_batch.py` → **`competitiveSummary`**。

---

## getItemOffers — Path 与 Query

- **Path**：`products/pricing/v0/items/{Asin}/offers`（`{Asin}` 路径编码）
- **Query**：**`MarketplaceId`**（必填）、**`ItemCondition`**（必填）、**`CustomerType`**（可选）

**速率（文档默认值）**：约 **0.5 req/s**，burst **1**（见 [getItemOffers](https://developer-docs.amazon.com/sp-api/reference/getitemoffers)）。

---

## 批量 POST（ItemOffers / ListingOffers / FOEP / CompetitiveSummary）

上游均为 **`POST`** + **JSON body**，根字段为 **`requests`** 数组。子请求字段以 Amazon 模型为准；本仓库脚本在**默认模式**下将简化 JSON 展开为官方形状；若传 **`useAmazonRequestShape`: true**，则 **`requests`** 须已是 Amazon 原始对象（脚本只做条数校验）。

| 操作 | `path` | 子请求条数（脚本校验） | 文档速率（默认，以账号为准） |
|------|--------|------------------------|------------------------------|
| getItemOffersBatch | `batches/products/pricing/v0/itemOffers` | 1～20 | 约 0.1 req/s，burst 1 |
| getListingOffersBatch | `batches/products/pricing/v0/listingOffers` | 1～20 | 约 0.5 req/s，burst 1 |
| getFeaturedOfferExpectedPriceBatch | `batches/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice` | 1～40 | 约 0.033 req/s，burst 1 |
| getCompetitiveSummary | `batches/products/pricing/2022-05-01/items/competitiveSummary` | 1～20 | 约 0.033 req/s，burst 1 |

**Item / Listing Offers 批量子请求（简化 → 官方）**：每条展开为 **`uri`**（以 `/` 开头的资源路径，**无** query）、**`method`:** `GET`、**`MarketplaceId`**、**`ItemCondition`**，以及可选 **`CustomerType`**、**`headers`**。Item 的 `uri` 形如 **`/products/pricing/v0/items/{Asin}/offers`**；Listing 的 `uri` 形如 **`/products/pricing/v0/listings/{SellerSKU}/offers`**（SKU 路径编码）。

**getFeaturedOfferExpectedPriceBatch（简化）**：每条含 **`marketplaceId`**、**`sku`**、**`segment`**（对象，结构见官方）；脚本补充 **`uri`**、**`method`:** `POST`。

**getCompetitiveSummary（简化）**：每条含 **`asin`**、**`marketplaceId`**、**`includedData`**（非空字符串数组，如 `featuredBuyingOptions`），以及可选 **`lowestPricedOffersInputs`**；脚本补充 **`uri`**、**`method`:** `POST`。

---

## 脚本 JSON 入参（`get_pricing.py`）

与 Amazon Query 的对应关系：

| 脚本字段 | 必填 | 映射 |
|----------|------|------|
| sellerId | 是 | 仅用于 `/spApi/storeTokens` |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceId | 是* | → `MarketplaceId`。若只提供 **`marketplaceIds`** 数组，则取 **第一个** 并 stderr 警告（与同系列 listing 脚本习惯一致） |
| itemType | 是 | `Asin` 或 `Sku` |
| asins | 条件 | `itemType=Asin` 时至少 1 个、≤20 |
| skus | 条件 | `itemType=Sku` 时至少 1 个、≤20 |
| itemCondition | 否 | → `ItemCondition` |
| offerType | 否 | → `OfferType` |
| skipDepCheck | 否 | `true` 时跳过 `check_auth_dependency.py` |

---

## 脚本 JSON 入参（`get_competitive_pricing.py`）

| 脚本字段 | 必填 | 映射 |
|----------|------|------|
| sellerId | 是 | `/spApi/storeTokens` |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceId | 是* | → `MarketplaceId`；或 **`marketplaceIds`** 取第一个 |
| itemType | 是 | `Asin` 或 `Sku` |
| asins / skus | 条件 | 与 getPricing 相同（1～20） |
| customerType | 否 | → `CustomerType`：`Consumer` / `Business` |
| skipDepCheck | 否 | 同左 |

---

## 脚本 JSON 入参（`get_listing_offers.py`）

| 脚本字段 | 必填 | 映射 |
|----------|------|------|
| sellerId | 是 | `/spApi/storeTokens` |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | 卖家 SKU → path 中的 `{SellerSKU}` |
| marketplaceId | 是* | → `MarketplaceId`；或 **`marketplaceIds`** 取第一个 |
| itemCondition | 是 | → `ItemCondition` |
| customerType | 否 | → `CustomerType`：`Consumer` / `Business` |
| skipDepCheck | 否 | 同左 |

---

## 脚本 JSON 入参（`get_item_offers.py`）

| 脚本字段 | 必填 | 说明 |
|----------|------|------|
| sellerId / region | 是 | storeTokens |
| asin | 是 | path 中的 ASIN |
| marketplaceId | 是* | Query `MarketplaceId` |
| itemCondition | 是 | Query `ItemCondition` |
| customerType | 否 | Query `CustomerType` |
| skipDepCheck | 否 | 同左 |

---

## 脚本 JSON 入参（`post_item_offers_batch.py` / `post_listing_offers_batch.py`）

| 脚本字段 | 必填 | 说明 |
|----------|------|------|
| sellerId / region | 是 | storeTokens |
| requests | 是 | 1～20；默认每项 **item batch**：`asin`+`marketplaceId`+`itemCondition` 或 **listing batch**：`sku`+`marketplaceId`+`itemCondition` |
| useAmazonRequestShape | 否 | `true` 时 `requests` 为 Amazon 原始子请求 |
| skipDepCheck | 否 | 同左 |

成功时 stdout 含 **`requestBody`**（已发送的 JSON 对象）。

---

## 脚本 JSON 入参（`post_featured_offer_expected_price_batch.py`）

| 脚本字段 | 必填 | 说明 |
|----------|------|------|
| sellerId / region | 是 | storeTokens |
| requests | 是 | 1～40；每项 `marketplaceId`、`sku`、`segment`（或 `useAmazonRequestShape`） |
| useAmazonRequestShape / skipDepCheck | 否 | 同上 |

---

## 脚本 JSON 入参（`post_competitive_summary_batch.py`）

| 脚本字段 | 必填 | 说明 |
|----------|------|------|
| sellerId / region | 是 | storeTokens |
| requests | 是 | 1～20；每项 `asin`、`marketplaceId`、`includedData`（数组），可选 `lowestPricedOffersInputs` |
| useAmazonRequestShape / skipDepCheck | 否 | 同上 |

---

## curl 示例

**1）取 `accessToken`**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/storeTokens" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sellerId":"A1BCDEFGHIJK2","region":"NA"}'
```

**2）getPricing（按 ASIN）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "products/pricing/v0/price",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "MarketplaceId=ATVPDKIKX0DER&ItemType=Asin&Asins=B08N5WRWNW&ItemCondition=New"
  }'
```

> 请将示例 ASIN / token 换为真实值；多 ASIN 时重复 `Asins=` 键。

**3）getCompetitivePricing（按 ASIN + 企业买家视角）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "products/pricing/v0/competitivePrice",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "MarketplaceId=ATVPDKIKX0DER&ItemType=Asin&Asins=B08N5WRWNW&CustomerType=Business"
  }'
```

**4）getListingOffers（单 SKU；path 中 SKU 若含特殊字符须先编码）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "products/pricing/v0/listings/My-Seller-SKU-001/offers",
    "method": "GET",
    "amzAccessToken": "Atza|IwEBI...",
    "queryString": "MarketplaceId=ATVPDKIKX0DER&ItemCondition=New"
  }'
```

**5）getItemOffersBatch（POST body 示意；`requests` 以实网为准）**

```bash
curl -sS -X POST "https://tool-gateway.linkfox.com/spApi/developerProxy" \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "NA",
    "path": "batches/products/pricing/v0/itemOffers",
    "method": "POST",
    "amzAccessToken": "Atza|IwEBI...",
    "contentType": "application/json",
    "body": "{\"requests\":[{\"uri\":\"/products/pricing/v0/items/B08N5WRWNW/offers\",\"method\":\"GET\",\"MarketplaceId\":\"ATVPDKIKX0DER\",\"ItemCondition\":\"New\"}]}"
  }'
```

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-amazon-store-pricing",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Product Pricing（含批量与 2022-05-01）结果符合预期。"
}
```
