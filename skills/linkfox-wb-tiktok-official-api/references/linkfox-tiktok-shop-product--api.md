# TikTok Shop ERP Product API Reference

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-product/references/api.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "product/202312/prerequisites", "method": "GET"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

本文档是 **`linkfox-tiktok-shop-product`** 的接口总览与转发说明。
**每个接口的完整官方参数/响应/错误码**见 `linkfox-tiktok-shop-product--apis--<api>.md`（已从 Partner Center 原文整理并加上 LinkFox 转发映射）。

> ⚠️ 依赖 **`linkfox-tiktok-shop-auth`**（`appType=erp`）。

---

## 1. 转发约定（Agent 必读）

### 调用链

```
linkfox-tiktok-shop-auth  →  openId（选店）
        ↓
POST tiktokShop/developerProxy
  appType = erp
  openId  = <ERP openId>          # 网关按 openId+appType 从库取 token
  path / method / queryString / body
        ↓
若上游 401 或 token expired/invalid → 网关自动 refresh 并重试一次，回写库
        ↓
紫鸟注入 app_key / timestamp / sign → TikTok Open API
```

> ⚠️ **ACCESS_TOKEN 已后台化**：勿传 `ttsAccessToken`（即使传入也会被忽略）。业务调用**不要**先调 `/storeTokens` 或 `/refreshToken`；普通取 token 也不会按过期时间提前刷新。

### developerProxy 入参

| 参数 | 必填 | 说明 |
|------|------|------|
| path | 是 | TikTok 相对路径，**不含**主机名 |
| method | 是 | `GET` / `POST` / `PUT` / `DELETE` |
| openId | 是 | 卖家 open_id；网关据此取库中 token |
| appType | 是 | **固定 `erp`** |
| region | 否 | 默认 `global`，美国站 `us` |
| queryString | 视接口 | 不含 `?`；多数需 `shop_cipher` |
| body | 视接口 | JSON 字符串 |
| contentType | 否 | 默认 `application/json` |
| multipartFileName | 图片上传时是 | 原始文件名，如 `product.png` |
| multipartFileBase64 | 图片上传时是 | 图片原始字节的 Base64；不要带 `data:image/...;base64,` 前缀 |
| useCase | 图片上传时否 | 默认 `MAIN_IMAGE`；网关转换为上游 multipart 表单的 `use_case` |
| ttsAccessToken | 否 | **已废弃**，忽略 |

### 网关响应

| 字段 | 说明 |
|------|------|
| httpStatus | 上游 HTTP 状态 |
| body | TikTok 业务 JSON 字符串（含 `code`/`message`/`data`） |
| errcode | 网关错误；**1005**=path 未白名单 |

### path 白名单

- `authorization/`
- `product/`

### shop_cipher

1. 调 `get_authorized_shops` → `data.shops[].cipher`
2. 写入后续请求 Query：`shop_cipher=<cipher>`
3. 多店必须显式指定；单店也须显式传入

---

## 2. 接口索引（完整定义点进子文档）

| api | Method | path | shop_cipher | 完整参考 | 官方 |
|-----|--------|------|-------------|----------|------|
| `get_authorized_shops` | GET | `authorization/202309/shops` | 否 | [Get Authorized Shops](linkfox-tiktok-shop-product--apis--get_authorized_shops.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-authorized-shops-202309) |
| `check_listing_prerequisites` | GET | `product/202312/prerequisites` | 是 | [Check Listing Prerequisites](linkfox-tiktok-shop-product--apis--check_listing_prerequisites.md) | [doc](https://partner.tiktokshop.com/docv2/page/check-listing-prerequisites-202312) |
| `get_categories` | GET | `product/202309/categories` | 是 | [Get Categories](linkfox-tiktok-shop-product--apis--get_categories.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-categories-202309) |
| `get_category_rules` | GET | `product/202309/categories/{category_id}/rules` | 是 | [Get Category Rules](linkfox-tiktok-shop-product--apis--get_category_rules.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-category-rules-202309) |
| `get_attributes` | GET | `product/202309/categories/{category_id}/attributes` | 是 | [Get Attributes](linkfox-tiktok-shop-product--apis--get_attributes.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-attributes-202309) |
| `recommend_category` | POST | `product/202309/categories/recommend` | 是 | [Recommend Category](linkfox-tiktok-shop-product--apis--recommend_category.md) | [doc](https://partner.tiktokshop.com/docv2/page/recommend-category-202309) |
| `get_brands` | GET | `product/202309/brands` | 是 | [Get Brands](linkfox-tiktok-shop-product--apis--get_brands.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-brands-202309) |
| `search_products` | POST | `product/202502/products/search` | 是 | [Search Products](linkfox-tiktok-shop-product--apis--search_products.md) | [doc](https://partner.tiktokshop.com/docv2/page/search-products-202502) |
| `get_product` | GET | `product/202309/products/{product_id}` | 是 | [Get Product](linkfox-tiktok-shop-product--apis--get_product.md) | [doc](https://partner.tiktokshop.com/docv2/page/get-product-202309) |
| `create_product` | POST | `product/202309/products` | 是 | [Create Product](linkfox-tiktok-shop-product--apis--create_product.md) | [doc](https://partner.tiktokshop.com/docv2/page/create-product-202309) |
| `edit_product` | PUT | `product/202309/products/{product_id}` | 是 | [Edit Product](linkfox-tiktok-shop-product--apis--edit_product.md) | [doc](https://partner.tiktokshop.com/docv2/page/edit-product-202309) |
| `partial_edit_product` | POST | `product/202309/products/{product_id}/partial_edit` | 是 | [Partial Edit Product](linkfox-tiktok-shop-product--apis--partial_edit_product.md) | [doc](https://partner.tiktokshop.com/docv2/page/partial-edit-product-202309) |
| `check_product_listing` | POST | `product/202309/products/listing_check` | 是 | [Check Product Listing](linkfox-tiktok-shop-product--apis--check_product_listing.md) | [doc](https://partner.tiktokshop.com/docv2/page/check-product-listing-202309) |
| `activate_product` | POST | `product/202309/products/activate` | 是 | [Activate Product](linkfox-tiktok-shop-product--apis--activate_product.md) | [doc](https://partner.tiktokshop.com/docv2/page/activate-product-202309) |
| `deactivate_products` | POST | `product/202309/products/deactivate` | 是 | [Deactivate Products](linkfox-tiktok-shop-product--apis--deactivate_products.md) | [doc](https://partner.tiktokshop.com/docv2/page/deactivate-products-202309) |
| `update_price` | POST | `product/202309/products/{product_id}/prices/update` | 是 | [Update Price](linkfox-tiktok-shop-product--apis--update_price.md) | [doc](https://partner.tiktokshop.com/docv2/page/update-price-202309) |
| `update_inventory` | POST | `product/202309/products/{product_id}/inventory/update` | 是 | [Update Inventory](linkfox-tiktok-shop-product--apis--update_inventory.md) | [doc](https://partner.tiktokshop.com/docv2/page/update-inventory-202309) |
| `delete_products` | DELETE | `product/202309/products` | 是 | [Delete Products](linkfox-tiktok-shop-product--apis--delete_products.md) | [doc](https://partner.tiktokshop.com/docv2/page/delete-products-202309) |
| `recover_products` | POST | `product/202309/products/recover` | 是 | [Recover Products](linkfox-tiktok-shop-product--apis--recover_products.md) | [doc](https://partner.tiktokshop.com/docv2/page/recover-products-202309) |
| `upload_product_image` | POST | `product/202309/images/upload` | 是 | [Upload Product Image](linkfox-tiktok-shop-product--apis--upload_product_image.md) | [doc](https://partner.tiktokshop.com/docv2/page/upload-product-image-202309) |
| `upload_product_file` | POST | `product/202309/files/upload` | 是 | [Upload Product File](linkfox-tiktok-shop-product--apis--upload_product_file.md) | [doc](https://partner.tiktokshop.com/docv2/page/upload-product-file-202309) |

### 推荐主链路

```
get_authorized_shops → shop_cipher
  → check_listing_prerequisites
  → get_categories / recommend_category / get_attributes / get_brands
  → check_product_listing → create_product → activate_product
  → search_products / get_product / update_price / update_inventory …
```

### 通用调用

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

---

## 3. Feedback

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: `linkfox-tiktok-shop-product`

## 4. Notes

1. `upload_product_image` 通过网关的 Base64 multipart 桥接调用：向 developerProxy 传 `multipartFileName`、`multipartFileBase64`、图片 MIME `contentType` 和 `useCase`；网关解码并向 TikTok 发送真正的 `multipart/form-data`。`upload_product_file` 仍暂不可调用。
2. Create/Edit 的嵌套 SKU/图片结构以对应 `apis/*.md` 官方原文为准。
3. 勿输出完整 ERP token。
