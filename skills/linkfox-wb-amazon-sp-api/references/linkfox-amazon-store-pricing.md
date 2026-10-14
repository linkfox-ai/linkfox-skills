# Reference archive: linkfox-amazon-store-pricing

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
    "path": "products/pricing/v0/price",
    "method": "GET",
    "queryString": "<按本 reference 的参数规则编码；无查询参数时省略>"
  }
}
```

`toolName` 必须精确匹配并区分大小写。WorkBuddy 自动注入 Authorization；`arguments` 中不得加入网关 `headers`、API Key、Amazon access/refresh token、JWT、手机号或其他凭证。MCP/`proxy_call` 缺失时停止，禁止 curl、`urllib`、`requests`、`httpx` 或本地脚本回退。同一任务内相同 `toolName + arguments` 不重复调用；失败、空结果或不理想时不自动重试。先检查 MCP/schema/`isError`，再读取 structured content 或仅解析一次 text JSON，随后检查下游 `errcode`/`code`、`errmsg`/`msg`、`httpStatus`，最后按响应字段读取结果。

## 来源响应字段表

来源：`skills/linkfox-amazon-store-pricing/references/api.md`。仅转录来源响应章节明确给出的字段或响应 JSON；未说明属性不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `errcode` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `errmsg` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `httpStatus` | number | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `contentType` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `body` | string | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `pricing` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `competitivePricing` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `listingOffers` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `itemOffers` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `itemOffersBatch` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `listingOffersBatch` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `featuredOfferExpectedPriceBatch` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |
| `competitiveSummary` | 来源未说明 | 来源响应契约字段；来源未提供的必填、可空、枚举或格式属性不补猜。 |


---
name: linkfox-amazon-store-pricing
description: 亚马逊商品报价与竞争定价查询。用于按 ASIN 或卖家 SKU 获取商品价格、竞争价格、Listing Offers、Item Offers、批量报价、Featured Offer Expected Price（FOEP）和竞争摘要。用户提到亚马逊定价、商品报价、竞品价格、最低报价、购物车价格、Buy Box、Featured Offer、listing offers、item offers、batch pricing、FOEP、competitive summary、Product Pricing API 时触发。即使未明确提及 SP-API，只要希望比较亚马逊商品报价、判断竞争力或估算赢得 Featured Offer 的价格，也应触发此技能；修改 Listing 售价使用 linkfox-amazon-store-listings 或批量 Feed。
---

# Amazon 店铺 Product Pricing


## 调用方式

仅按本文开头的 MCP 契约调用；预签名上传/下载例外仅使用本 skill 保留的对应本地 helper。


## 认证和积分问题

按 `references/onboarding.md` 分层处理 MCP 401、下游 401/402、403 和其他业务错误。


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

2. **不要**在本 skill 内绕过依赖实现授权或令牌逻辑。

---

## Current Capabilities（脚本一览）

| 能力 | developerProxy `path`（要点） | 脚本 |
|------|------------------------------|------|
| getPricing | `products/pricing/v0/price` + Query | `get_pricing` 操作 |
| getCompetitivePricing | `products/pricing/v0/competitivePrice` + Query | `get_competitive_pricing` 操作 |
| getListingOffers | `products/pricing/v0/listings/{sku}/offers` + Query | `get_listing_offers` 操作 |
| getItemOffers | `products/pricing/v0/items/{asin}/offers` + Query | `get_item_offers` 操作 |
| getItemOffersBatch | `batches/products/pricing/v0/itemOffers`，POST JSON body | `post_item_offers_batch` 操作 |
| getListingOffersBatch | `batches/products/pricing/v0/listingOffers`，POST JSON body | `post_listing_offers_batch` 操作 |
| getFeaturedOfferExpectedPriceBatch | `batches/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice`，POST | `post_featured_offer_expected_price_batch` 操作 |
| getCompetitiveSummary | `batches/products/pricing/2022-05-01/items/competitiveSummary`，POST | `post_competitive_summary_batch` 操作 |


---

## Quick Parameters（摘要）

- **getPricing / getCompetitivePricing**：`sellerId`、`region`、`marketplaceId`（或 `marketplaceIds` 取首）、`itemType`、`asins` 或 `skus`（≤20）；getPricing 另有 `itemCondition`、`offerType`；getCompetitivePricing 另有 `customerType`。
- **getListingOffers / getItemOffers**：`sku`+path 或 **`asin`**+path；**`itemCondition` 必填**；可选 `customerType`。
- **Item / Listing Offers Batch**：`requests` 数组，默认每项为简化对象（见 `references/api.md`）；**1～20** 条（FOEP 批量脚本为 **最多 40** 条）。
- **getCompetitiveSummary 批量**：每项需 **`asin`**、**`marketplaceId`**、**`includedData`**（非空字符串数组）；可选 **`lowestPricedOffersInputs`**。
- **getFeaturedOfferExpectedPriceBatch**：每项需 **`marketplaceId`**、**`sku`**、**`segment`**（对象，结构以官方为准）。

---

## Scripts

- `get_pricing` 操作 · `get_competitive_pricing` 操作 · `get_listing_offers` 操作 · `get_item_offers` 操作
- `post_item_offers_batch` 操作 · `post_listing_offers_batch` 操作 · `post_featured_offer_expected_price_batch` 操作 · `post_competitive_summary_batch` 操作
- `amazon_store_pricing__check_auth_dependency` 操作 · `_spapi_pricing_common` 操作（内部模块）



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

**Feedback：** 见 `references/api.md`，`skillName`：`linkfox-amazon-store-pricing`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

## Archived reference: api.md

# Amazon 店铺 Product Pricing API 参考（v0 + 2022-05-01 批量）


> 官方入口：[getPricing](https://developer-docs.amazon.com/sp-api/reference/getpricing) · [getCompetitivePricing](https://developer-docs.amazon.com/sp-api/reference/getcompetitivepricing) · [getListingOffers](https://developer-docs.amazon.com/sp-api/reference/getlistingoffers) · [getItemOffers](https://developer-docs.amazon.com/sp-api/reference/getitemoffers) · [getItemOffersBatch](https://developer-docs.amazon.com/sp-api/reference/getitemoffersbatch) · [getListingOffersBatch](https://developer-docs.amazon.com/sp-api/reference/getlistingoffersbatch) · [getFeaturedOfferExpectedPriceBatch](https://developer-docs.amazon.com/sp-api/reference/getfeaturedofferexpectedpricebatch) · [getCompetitiveSummary](https://developer-docs.amazon.com/sp-api/reference/getcompetitivesummary)

> ⚠️ **依赖**：需已安装并完成授权 **`linkfox-amazon-store-auth`**。应用需具备 **Product Pricing** 等相关角色/权限，否则上游可能返回 403。

---

## 调用规范（与 store-report 相同）

| 项 | 说明 |
|----|------|
| **SP-API 转发** | `proxy_call` 的 `spApi/developerProxy`，Body 见下节 |

---

## `proxy_call` 的 `spApi/developerProxy`（定价类 GET / POST）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 是 | `NA` / `EU` / `FE` |
| path | string | 是 | 不含主机名。示例：**`products/pricing/v0/price`**、**`products/pricing/v0/items/{Asin}/offers`**、**`batches/products/pricing/v0/itemOffers`**、**`batches/products/pricing/2022-05-01/items/competitiveSummary`** 等（见各节） |
| method | string | 是 | **`GET`** 或 **`POST`**（与上游一致） |
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

官方参数名 **大小写敏感**。多值 **`Asins`** / **`Skus`** 采用重复键形式：`Asins=B0...&Asins=B0...`（本 reference 的请求构造按此拼接）。

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

- **`httpStatus=200`** 时解析 `body`：`get_pricing` 操作 → **`pricing`**；`get_competitive_pricing` 操作 → **`competitivePricing`**；`get_listing_offers` 操作 → **`listingOffers`**；`get_item_offers` 操作 → **`itemOffers`**；`post_item_offers_batch` 操作 → **`itemOffersBatch`**；`post_listing_offers_batch` 操作 → **`listingOffersBatch`**；`post_featured_offer_expected_price_batch` 操作 → **`featuredOfferExpectedPriceBatch`**；`post_competitive_summary_batch` 操作 → **`competitiveSummary`**。

---

## getItemOffers — Path 与 Query

- **Path**：`products/pricing/v0/items/{Asin}/offers`（`{Asin}` 路径编码）
- **Query**：**`MarketplaceId`**（必填）、**`ItemCondition`**（必填）、**`CustomerType`**（可选）

**速率（文档默认值）**：约 **0.5 req/s**，burst **1**（见 [getItemOffers](https://developer-docs.amazon.com/sp-api/reference/getitemoffers)）。

---

## 批量 POST（ItemOffers / ListingOffers / FOEP / CompetitiveSummary）

上游均为 **`POST`** + **JSON body**，根字段为 **`requests`** 数组。子请求字段以 Amazon 模型为准；本 reference 的请求构造在**默认模式**下将简化 JSON 展开为官方形状；若传 **`useAmazonRequestShape`: true**，则 **`requests`** 须已是 Amazon 原始对象（脚本只做条数校验）。

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

## 脚本 JSON 入参（`get_pricing` 操作）

与 Amazon Query 的对应关系：

| 脚本字段 | 必填 | 映射 |
|----------|------|------|
| sellerId | 是 | 仅用于 `spApi/storeTokens` |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceId | 是* | → `MarketplaceId`。若只提供 **`marketplaceIds`** 数组，则取 **第一个** 并 stderr 警告（与同系列 listing 脚本习惯一致） |
| itemType | 是 | `Asin` 或 `Sku` |
| asins | 条件 | `itemType=Asin` 时至少 1 个、≤20 |
| skus | 条件 | `itemType=Sku` 时至少 1 个、≤20 |
| itemCondition | 否 | → `ItemCondition` |
| offerType | 否 | → `OfferType` |
| skipDepCheck | 否 | `true` 时跳过 `amazon_store_pricing__check_auth_dependency` 操作 |

---

## 脚本 JSON 入参（`get_competitive_pricing` 操作）

| 脚本字段 | 必填 | 映射 |
|----------|------|------|
| sellerId | 是 | `spApi/storeTokens` |
| region | 是 | `NA` / `EU` / `FE` |
| marketplaceId | 是* | → `MarketplaceId`；或 **`marketplaceIds`** 取第一个 |
| itemType | 是 | `Asin` 或 `Sku` |
| asins / skus | 条件 | 与 getPricing 相同（1～20） |
| customerType | 否 | → `CustomerType`：`Consumer` / `Business` |
| skipDepCheck | 否 | 同左 |

---

## 脚本 JSON 入参（`get_listing_offers` 操作）

| 脚本字段 | 必填 | 映射 |
|----------|------|------|
| sellerId | 是 | `spApi/storeTokens` |
| region | 是 | `NA` / `EU` / `FE` |
| sku | 是 | 卖家 SKU → path 中的 `{SellerSKU}` |
| marketplaceId | 是* | → `MarketplaceId`；或 **`marketplaceIds`** 取第一个 |
| itemCondition | 是 | → `ItemCondition` |
| customerType | 否 | → `CustomerType`：`Consumer` / `Business` |
| skipDepCheck | 否 | 同左 |

---

## 脚本 JSON 入参（`get_item_offers` 操作）

| 脚本字段 | 必填 | 说明 |
|----------|------|------|
| sellerId / region | 是 | storeTokens |
| asin | 是 | path 中的 ASIN |
| marketplaceId | 是* | Query `MarketplaceId` |
| itemCondition | 是 | Query `ItemCondition` |
| customerType | 否 | Query `CustomerType` |
| skipDepCheck | 否 | 同左 |

---

## 脚本 JSON 入参（`post_item_offers_batch` 操作 / `post_listing_offers_batch` 操作）

| 脚本字段 | 必填 | 说明 |
|----------|------|------|
| sellerId / region | 是 | storeTokens |
| requests | 是 | 1～20；默认每项 **item batch**：`asin`+`marketplaceId`+`itemCondition` 或 **listing batch**：`sku`+`marketplaceId`+`itemCondition` |
| useAmazonRequestShape | 否 | `true` 时 `requests` 为 Amazon 原始子请求 |
| skipDepCheck | 否 | 同左 |

成功时 stdout 含 **`requestBody`**（已发送的 JSON 对象）。

---

## 脚本 JSON 入参（`post_featured_offer_expected_price_batch` 操作）

| 脚本字段 | 必填 | 说明 |
|----------|------|------|
| sellerId / region | 是 | storeTokens |
| requests | 是 | 1～40；每项 `marketplaceId`、`sku`、`segment`（或 `useAmazonRequestShape`） |
| useAmazonRequestShape / skipDepCheck | 否 | 同上 |

---

## 脚本 JSON 入参（`post_competitive_summary_batch` 操作）

| 脚本字段 | 必填 | 说明 |
|----------|------|------|
| sellerId / region | 是 | storeTokens |
| requests | 是 | 1～20；每项 `asin`、`marketplaceId`、`includedData`（数组），可选 `lowestPricedOffersInputs` |
| useAmazonRequestShape / skipDepCheck | 否 | 同上 |

---

## MCP 示例见本文开头




**2）getPricing（按 ASIN）**



> 请将示例 ASIN / token 换为真实值；多 ASIN 时重复 `Asins=` 键。

**3）getCompetitivePricing（按 ASIN + 企业买家视角）**



**4）getListingOffers（单 SKU；path 中 SKU 若含特殊字符须先编码）**



**5）getItemOffersBatch（POST body 示意；`requests` 以实网为准）**



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

## Archived reference: onboarding.md

认证和积分问题统一按本 skill 的 `references/onboarding.md` 处理。
