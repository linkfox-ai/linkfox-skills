# Edit Product

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `tiktokShop/developerProxy` |
| `arguments` | 直接使用本 reference 的请求对象；不得额外包裹 `body`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-tiktok-shop-product/references/apis/edit_product.md`；只按其响应契约核对字段表 |

```json
{
  "toolName": "tiktokShop/developerProxy",
  "arguments": {"appType": "erp", "openId": "<openId>", "path": "product/202309/products/{product_id}", "method": "PUT"}
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，禁止 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得传 LinkFox `headers`、API Key、`token`、JWT 或手机号。
- 收费失败、空结果或结果不理想时不自动重试；相同 `toolName + arguments` 在同一任务内不重复调用。
- 先处理 MCP/schema/`isError`；text JSON 只解析一次；再检查下游错误字段和业务结果。

> 官方文档：https://partner.tiktokshop.com/docv2/page/edit-product-202309

## LinkFox 转发映射（本 skill）

| 项 | 值 |
|----|----|
| 具名 api | `edit_product` |
| 脚本 | `proxy_call` |
| 网关 | `POST tiktokShop/developerProxy` |
| appType | **`erp`（固定）** |
| 上游 path | `product/202309/products/{product_id}` |
| method | `PUT` |
| shop_cipher | 是（Query `shop_cipher`；必须显式传入；可先调用本域 Get Authorized Shops 取得） |
| 令牌 | 网关按 `openId` + `appType=erp` 从库取 token（`ttsAccessToken` 已废弃忽略；401/过期时自动刷新并重试一次） |

### developerProxy 示例

```json
{
  "appType": "erp",
  "openId": "7010...",
  "path": "product/202309/products/{product_id}",
  "method": "PUT",
  "queryString": "shop_cipher=GCP_...",
  "body": "{...}"
}
```

### 脚本示例

> 旧 HTTP/脚本示例已移除；使用本页 `MCP 调用` 的完整 `proxy_call` 参数结构。

---

## 官方接口原文（TikTok Shop Partner Center）

# Path: /product/202309/products/{product_id}
# Method: [PUT]
# Function Description
Edit all properties (e.g. description, brand, images) of an existing product that is not in the `FREEZE` or `DELETED` state.
After editing the product, the latest product content (referred to as v2) will be resent for audit review. If the audit passes, v2 is published to the shop, otherwise, the existing product stays live and remains unchanged (keeping v1). However, edits to the `price` or `inventory` fields do not require a reaudit and will be immediately published on the platform. Use the [Product status change](https://partner.tiktokshop.com/docv2/page/650956aff1fd3102b90b6261) webhook to keep track of the review status.
**Note**:

* This API is applicable only for **active sellers/shops** that have completed the KYC onboarding process.
* There may be a limit to the number of products you can relist per day. We recommend prioritizing key products first to ensure they get published. You can find your listing limit on the Seller Center homepage.
* All inputs, including blanks, in the request payload will overwrite existing values. To retain an existing value, make sure to include it in your request. Exceptions to this rule are the `price` and `inventory` fields, which will remain unchanged if they are omitted from the request. Therefore, **it is strongly recommended to retrieve the latest product data using** Get Product（文档 ID：`6509d85b4a0bb702c057fdda`） **and submit the complete data when editing**. This ensures accuracy and helps avoid errors or unintentional data loss due to missing fields.
* If you wish to edit only certain properties, you can use the Partial Edit Product API（文档 ID：`650a98d74a0bb702c06c3289`）, Update Inventory API（文档 ID：`6503068fc20ad60284b38858`）, or the Update Price API（文档 ID：`650307de5a12ff0294eac8b0`）.
* The language used in the product content must align with the target market's language (e.g. don't use Chinese), otherwise the listing will fail or be rejected.
   **For global sellers**:
   If you're using the local replication listing method, note the following sync rules:
* To sync any changes to other markets, please provide the `seller_sku` and complete `replicated_products` data.
* Note that **category changes** and **sales attribute changes** (in sales attribute id/name) must be synced to other markets. The API call will fail if you don't provide these details.
   **For Tokopedia sellers**:
   Note that a product can have **only one active version** across all platforms at any time. If a product is live on both platforms, audit results for the latest version are handled as follows:
* **Mixed audit results**: If the product passes audit on one platform but fails on another, on the successful platform, the product will stay live and be updated with content from the latest version (v2), while on the failed platform, the product will be deactivated and hidden entirely.
* **Audit failure on all platforms**: If the product fails audit on all platforms, the existing product stays live and remains unchanged (keeping v1).


---


# Common Parameters
For common parameters, refer to [How to call TikTok Shop APIs - Common Parameters](https://partner.tiktokshop.com/docv2/page/64f199679495ef0281851ee5#Back%20To%20Top)
| Properties | Location | Type | Require | Sample | Properties description |
| --- | --- | --- | --- | --- | --- |
| shop_cipher | query | string | Y | GCP_XF90igAAAABh00qsWgtvOiGFNqyubMt3 | Use this property to pass shop information in requesting the API. Failure in passing the correct value when requesting the API for cross-border shops will return incorrect response. |
| Get by API [Get Authorization Shop](https://partner.tiktokshop.com/docv2/page/6507ead7b99d5302be949ba9?external_id=6507ead7b99d5302be949ba9) |  |  |  |  |  |
| content-type | header | string | Y | application/json | Allowed type: application/json |
# Request Path Parameters
| Properties | Type | Require | Sample | Properties description |
| --- | --- | --- | --- | --- |
| product_id | string | Y | 1729409636071801988 | The product ID generated by TikTok Shop. |
# Request Query Parameters
| Properties | Type | Require | Sample | Properties description |
| --- | --- | --- | --- | --- |
| app_key | string | Y | 38abcd | Every single app will have a unique key. Please use the specific key assigned to your app. |
| sign | string | Y | 5361235029d141222525e303d742f9e38aea052d10896d3197ab9d6233730b8c | Signature generated by gen algorithm. When you send API requests to TTS, you must sign them so that TTS can identify the senders. |
| timestamp | int | Y | 1623812664 | Unix timestamp GMT (UTC+00:00). This timestamp is used across all API requests. Developers can use this convert to local time. |
# Request Body Parameters
| Properties | Type | Require | Sample | Properties description |
| --- | --- | --- | --- | --- |
| save_mode | string | N | AS_DRAFT | Indicates how the product should be saved. |
| Possible values: |  |  |  |  |

* AS_DRAFT: Save the product as a draft for future editing.
* LISTING: Immediately list the product in the shop.
   Default: LISTING

**Note**:

* Saving as draft is not supported in the following cases:
   * The product status is `DELETED`.
   * The product status is `PENDING` or `FREEZE` on any listing platform.
* If you are saving a post-live draft with `save_mode=AS_DRAFT`, `inventory` and `delivery_option_ids` fields are not supported and will not be saved. |
   description |string |Y |
   Please compare above detailed size with your measurement before purchase.
* M-Size
* XL-Size

![Image](https://p16-oec-va.ibyteimg.com/tos-maliva-i-o3syd03w52-us/181595ea7d26489284b5667488d708c1~tplv-o3syd03w52-origin-jpeg.jpeg?from=1432613627)
 |The product description in HTML format.
**Note**:

* The content must conform to the [HTML syntax](https://html.spec.whatwg.org/). All HTML tags are accepted but to optimize display on the TikTok Shop product detail page, the system will automatically convert certain tags into alternative formats, such as rendering `<table>` tags as images.
* Max length: 10,000 characters.
* Image guidelines: You must use TikTok Shop image URLs（文档 ID：`6509df95defece02be598a22`）. Max 30 `<img>` tags, each under 4000px with `src`, `width`, and `height` attributes.

**Recommendations**:

* If you are syncing a pre-existing description from another platform, include the full HTML source description here.
* Provide a detailed description, ideally over 300 characters.
* Include 3-5 key selling points, each under 250 characters, with supporting images.
* Use 1600x1600 px for the image dimensions. |
   category_id |string |Y |600001 |The ID of the category of this product. It must be a leaf category that corresponds to the category tree type specified in the `category_version` property. Use the [Get Categories API](https://partner.tiktokshop.com/docv2/page/6509c89d0fcef602bf1acd9b) to obtain the available categories.

**Note**:

* Refer to TikTok Shop Academy for information on product category restrictions.
* For the US market, if you change a product's category to an `INVITE_ONLY` category, you must submit a separate application through the Qualification Center on TikTok Shop Seller Center to gain access. Otherwise, even if the product audit is passed, the product will not be listed and made available to buyers. (The product status will be `PENDING` and the audit status will be `PRE_APPROVED`)
* For the Indonesia market, to list a product on both TikTok Shop and Tokopedia, you must use only categories that are available on both platforms. |
   brand_id |string |N |7082427311584347905 |The ID of the brand of this product.
   Use the [Get Brands API](https://partner.tiktokshop.com/docv2/page/6503075656e2bb0289dd5d01) to get the list of available brands for a shop.

**Note**: Unauthorized brands won't be displayed on TikTok Shop. |
main_images |[]object |Y | |A list of images to display in the product image gallery.

* Max count: 9
* Arrange your image URIs in the sequence that they should appear on TikTok Shop.
* Image dimensions: [300x300 px, 4000x4000 px]

**Recommendations**:

* Use a minimum of 5 images.
* The first image should have a white background. Use the [Optimize Images API](https://partner.tiktokshop.com/docv2/page/665692b35d39dc02deb49a97) to change the background to white |
   ^uri |string |Y |tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe |The URI of the image.
   Obtain this URI by uploading the images through the Upload Product Image API（文档 ID：`6509df95defece02be598a22`） with `use_case=MAIN_IMAGE`. You can use the returned URI directly, or process it through the Optimize Images API（文档 ID：`665692b35d39dc02deb49a97`） first and use the resulting URI. |
   skus |[]object |Y | |A list of Stock Keeping Units (SKUs) used to identify distinct variants of the product.

**Note**:

* Max SKUs for BR, EU, MX, JP, UK, US: 300
* Max SKUs for other regions: 100

**Recommendations**: Place the most important variant at the beginning of the array. |
^id |string |N |1729592969712207000 |The SKU ID generated by TikTok Shop. One product can contain multiple SKU IDs.
**Note**:

* To edit an existing SKU, include its SKU ID.
* Any existing SKU IDs not listed here will result in the deletion of those SKUs. For example, if this product contains 5 SKUs and you only provide 2 SKU IDs, the remaining 3 will be deleted.
* To create new SKUs, leave the SKU ID blank and complete the other fields. |
   ^sales_attributes |[]object |N | |A list of attributes (e.g. size, color, length) that define each variant of a product.

**Note**:

* You must retain at least 1 sales attribute, deleting all existing sales attributes is not allowed.
* You can only have up to 3 types of sales attributes per product.
* Each SKU must include the same number and type of sales attributes. For example, you cannot have one SKU that has only a Color attribute, while another SKU has both Color and Size attributes.
* Provide either a built-in ID or a custom name; if both are provided, the ID takes priority.
* The `id/name` and `value_id/value_name` pairs must be unique in each SKU. For example, you cannot repeat `"name": "Color"`, `"value_name": "Red"` in different SKUs. |
   ^^id |string |N |100089 |The ID of the sales attribute.
   This is either a built-in sales attribute ID from [Get Attributes API](https://partner.tiktokshop.com/docv2/page/6509c5784a0bb702c0561cc8) or a custom attribute ID returned after calling [Create Product API](https://partner.tiktokshop.com/docv2/page/6502fc8da57708028b42b18a). |
   ^^name |string |N |Specification |A self-defined custom sales attribute name if the existing attributes do not satisfy your needs. The system will auto-generate an ID after editing.

**Note**:

* Do not include sensitive characters.
* Max length: 20 characters
   |
   ^^value_id |string |N |1729592969712401100 |The ID of the sales attribute value.
   This is either a built-in sales attribute value ID from [Get Attributes API](https://partner.tiktokshop.com/docv2/page/6509c5784a0bb702c0561cc8) or a custom sales attribute value ID returned after calling [Create Product API](https://partner.tiktokshop.com/docv2/page/6502fc8da57708028b42b18a). |
   ^^value_name |string |N |XL |A self-defined custom sales attribute value if the existing values do not satisfy your needs. The system will auto-generate an ID after editing.

**Note**:

* No duplicates allowed under the same attribute.
* Max length: 50 characters. |
   ^^sku_img |object |N | |The default/main image for each value (e.g. red) of the primary sales attribute (e.g. color). This appears in the product options gallery on TikTok Shop.

You can attach images to only 1 type of sales attribute, which will serve as the primary attribute for display. An image must be provided for each value of the primary attribute. For example, if a product has 2 colors and 3 sizes, you can choose to attach images for either the color sales attribute or the size sales attribute. If you choose to attach images for color, you must attach 2 images, one for each color. If you want to add more images, use `supplementary_sku_images`. |
^^^uri |string |Y |tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe |The URI of the image.
Obtain this URI by uploading the images through the Upload Product Image API（文档 ID：`6509df95defece02be598a22`） with `use_case=ATTRIBUTE_IMAGE`. |
^^supplementary_sku_images |[]object |N | |A list of supplementary images for each value (e.g. red) of the primary sales attribute (e.g. color) to provide multiple views or details of the product for that attribute value. These appear in the product options gallery on TikTok Shop.
**Note**:

* Max number of image URIs: 8.
* Arrange your image URIs in the sequence that they should appear on TikTok Shop.
* Applicable only for the US market. |
   ^^^uri |string |Y |tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe |The URI of the image.
   Obtain this URI by uploading the images through the Upload Product Image API（文档 ID：`6509df95defece02be598a22`） with `use_case=ATTRIBUTE_IMAGE`. |
   ^seller_sku |string |N |Color-Red-XM001 |An internal code/name for managing SKUs, not visible to buyers.
* Valid length: 1-50 characters
* Format: Text without spaces |
   ^price |object |N | |SKU pricing information.

**Note**: If you omit this object in the API request, the existing information will remain unchanged. |
^^amount |string |N |1.21 |**Local sellers/Intra-EU sellers**
The SKU's **local display price** shown on the product page before any discounts. Refer to [Product Pricing](https://partner.tiktokshop.com/docv2/page/67e1288d76cfee049d9af858) for the allowed price ranges in each market.
**Global sellers**
The SKU's **local pre-tax price**. This excludes any applicable charges such as cross-border shipping costs, taxes, and other fees, and therefore does not appear on the product page.
Refer to [Product Pricing](https://partner.tiktokshop.com/docv2/page/67e1288d76cfee049d9af858) for the allowed price ranges in each market.

* **Note**: Not applicable for JP and US shops using China warehouses, please use `price.sale_price` instead. |
   ^^currency |string |Y |USD |The currency.
   Possible values based on the region:
* BRL: Brazil
* CZK: Czech Republic
* EUR: France, Germany, Ireland, Italy, Spain, Netherlands, Belgium, Austria, Greece, Portugal
* GBP: United Kingdom
* HUF: Hungary
* IDR: Indonesia
* JPY: Japan
* MXN: Mexico
* MYR: Malaysia
* PHP: Philippines
* PLN: Poland
* SGD: Singapore
* THB: Thailand
* USD: United States
* VND: Vietnam |
   ^^sale_price |string |N |1.21 |**Global sellers**
   The SKU's **local display price** shown on the product page before any discounts.
   Refer to [Product Pricing](https://partner.tiktokshop.com/docv2/page/67e1288d76cfee049d9af858) for the allowed price ranges in each market.

**Note**:

* Applicable only for global sellers.
* Required for JP and US shops using China warehouses, optional for others.
* This is the definitive final price shown on the product page, all other prices will be ignored. |
   ^^starting_bid_price |string |N |2.3 |starting bid price for auction product |
   ^external_sku_id |string |N |1729592969712207012 |An external identifier used in an external ecommerce platform. This is used to associate the SKU between TikTok Shop and the external ecommerce platform.
   Max length: 999 characters |
   ^identifier_code |object |N | |A regulated identifier code assigned to a product based on international standardized regulations (e.g. GTIN) to ensure the product is universally identifiable across various platforms and systems.

**Note**: Editable only if the product is in DRAFT state. Otherwise, changes are not allowed. |
^^code |string |N |12345678901234 |The identifier code.
**Format**:

* GTIN: 14 digits
* EAN: 8, 13, or 14 digits
* UPC: 12 digits
* ISBN: 13 digits, or 9 digits ending in capital `X`
* JAN: 8 or 13 digits

**Note**: The identifier code must be unique for each SKU, with no repetition allowed. |
^^type |string |N |GTIN |The type of identifier code.
Possible values:

* GTIN
* EAN
* UPC
* ISBN
* JAN |
   ^inventory |[]object |N | |SKU inventory information.

**Note**:

* If you omit this object array in the API request, the existing information will remain unchanged.
* If you are saving a post-live draft with `save_mode=AS_DRAFT`, this field is not supported and will not be saved. When using Get Product to retrieve the draft, the values will reflect those in the base version. |
   ^^warehouse_id |string |Y |7068517275539719942 |The ID of the warehouse where the SKU is stored.
   Retrieve the list of warehouses available for your shop from the [Get Warehouse List API](https://partner.tiktokshop.com/docv2/page/650aa418defece02be6e66b6). |
   ^^quantity |int |N |999 |The total SKU quantity available in the warehouse.
   Valid range: [1, 99,999] |
   ^combined_skus |[]object |N | |If this SKU belongs to a virtual bundle, this object contains the list of individual SKUs that form the bundle (e.g. gift basket, starter pack). |
   ^^product_id |string |Y |1729582718312380123 |The ID of the source product included in the virtual bundle. |
   ^^sku_id |string |Y |2729382476852921560 |The ID of the source SKU included in the virtual bundle. |
   ^^sku_count |int |Y |2 |The quantity of the source SKU included in the virtual bundle. |
   ^sku_unit_count |string |N |100.00 |The total quantity/volume of the product represented by the SKU.
   For example, if the SKU represents 500ml of water, this value would be 500 if the unit type is defined as ml.
   Valid range: [0.01, 99,999.9999]
   Applicable only for the EU market.

**Note**:

* This is mainly used to calculate the unit price of the SKU, and is required only if you wish to display the unit price to facilitate easier price comparisons across different products and packaging sizes.
* Unit price = Selling price/(SKU unit count/base unit count). Therefore if you want to obtain the unit price, you would also need to define the "base unit count" and the "unit type" product attributes. Retrieve the relevant information for these product attributes by using the [Get Attributes API](https://partner.tiktokshop.com/docv2/page/6509c5784a0bb702c0561cc8). The unit price would then be returned in the [Get Product API](https://partner.tiktokshop.com/docv2/page/6509d85b4a0bb702c057fdda). |
   ^external_urls |[]string |N |["https://example.com/path1", "https://example.com/path2"] |A comma-delimited list of URLs for third-party product listing pages where consumers can place orders. Add this property if you have products listed on third-party sites other than TikTok Shop and would like to map them.
   Max string length: 500 |
   ^extra_identifier_codes |[]string |N | ["00012345678905","9780596520687"] |If the SKU belongs to a virtual bundle (containing multiple individual SKUs), you can add up to 10 additional identifier codes here for the SKUs included in the bundle.

**Format**:
GTIN: 14 digits
EAN: 8, 13, or 14 digits
UPC: 12 digits
ISBN: 13 digits, or 9 digits ending in capital `X`
**Note**:

* Applicable only for the EU market.
* The identifier code must be unique for each SKU, with no repetition allowed. |
   ^pre_sale |object |N | |SKU presale information, used to tag a product as a presale product based on its presale type.
   Applicable only if `allowed_special_product_types` from Get Category Rules（文档 ID：`6509c0febace3e02b74594a9`） is not empty.

**General usage rules**:

* Omit this object to retain the current presale settings.

**Rules for the US market**:

* Regular / Preorder product: Once the product goes live, you cannot change the product type.
* Made-to-order product: You can change it to a regular product at any time. |
   ^^type |string |N |PRE_ORDER |The type of pre-sale.
   Possible values based on the region:
   **US**
* `PRE_ORDER`: The product is not yet available or released. Fulfillment can be extended by specifying a **release date**.
* `MADE_TO_ORDER`: The product is produced only after the order is received. Fulfillment can be extended by specifying a **duration**.
* `CUSTOM`: The product requires a fulfillment timeline that exceeds the standard due to other factors. Fulfillment can be extended by specifying a **duration**.

**UK, EU, SEA, and JP**

* `PRE_ORDER`: The product is not yet available or released. Fulfillment can be extended by specifying a **duration**.

**ALL**

* `NONE`: To convert the product to a regular (non-presale) product. |
   ^^fulfillment_type |object |N | |Information about the type of pre-sale order fulfillment and the corresponding timeframe.
* `handling_duration_days` is for fulfillment with an extended duration.
* `release_date` is for starting fulfillment on a fixed date.

**Note**: Provide either the `handling_duration_days` or the `release_date`, depending on the value of `pre_sale.type` and your shop's region. |
^^^handling_duration_days |int |N |7 |The desired duration for handling a pre-sale order and handing it over to a shipping carrier.
Applicable only for the following regions and pre-sale type:
**US**

* `MADE_TO_ORDER`: Business days, from 3 to 14 days.
* `CUSTOM`: Business days, from 3 to 30 days.

**UK, EU, SEA, and JP**

* `PRE_ORDER`: Calendar days, from 3 to 30 days. |
   ^^^release_date |int |N |1619611761 |The date on which the product gets converted into a regular product and becomes available for general purchase. On this date, order handling will also start, changing the status of the order to [AWAITING_SHIPMENT](https://partner.tiktokshop.com/docv2/page/650b1b4bbace3e02b76d1011).

Applicable only for `PRE_ORDER` in the US.
**Note**:

* Valid range: The date must fall within 3 - 60 days from the current date.
* This date is a unix timestamp (seconds) based on the seller-selected timezone in Seller Center.
* This date cannot be modified once the product goes live. |
   ^list_price |object |N | |The SKU's list price information. This is equivalent to the manufacturer's suggested retail price (MSRP), or the recommended retail price (RRP).
   Applicable only for US local sellers.

**Note**: This value may appear as the strikethrough price on the product page. However, whether the strikethrough price is shown and the amount shown are subject to the audit team's review and decision based on various pricing information. |
^^amount |string |Y |1 |The price amount.
Valid range: [0.01, 7600]
**Note**:

* The value must be equal to or greater than `skus.price.amount`. Otherwise, it will be discarded.
* If the value is verified to be legitimate by the audit team, it will be stored and returned in the Get Product API（文档 ID：`6509d85b4a0bb702c057fdda`）. |
   ^^currency |string |Y |USD |The currency.
   Possible values: USD |
   ^external_list_prices |[]object |N | |The SKU list price (e.g. MSRP, RRP) or original price information on external ecommerce platforms.
   Applicable only for selected local sellers in the US market.

**Note**: This value may appear as the strikethrough price on the product page. However, whether the strikethrough price is shown and the amount shown are subject to the audit team's review and decision based on various pricing information. |
^^source |string |Y |SHOPIFY_COMPARE_AT_PRICE |The external ecommerce platform from which the price is sourced.
Possible values:

* SHOPIFY_COMPARE_AT_PRICE: The compare_at_price in Shopify. |
   ^^amount |string |Y |1 |The price amount.
   Valid range: [0.01, 7600] |
   ^^currency |string |Y |USD |The currency.
   Possible values: USD |
   ^fees |[]object |N | |The fees required for this product based on TikTok Shop policies. Fees are required only for certain product categories, retrieve the requirements from the [Get Category Rules API](https://partner.tiktokshop.com/docv2/page/6509c0febace3e02b74594a9). |
   ^^type |string |N |PFAND |The type of fee.
   Possible values: PFAND |
   ^^amount |string |N |1.01 |The fee amount.
   Valid range:
* PFAND: [0.00 - 6300.00] |
   ^^additional_attribute |string |N |SINGLE_USE |An optional attribute that provides additional context for the fee. The accepted values may vary by fee type and market.

Possible values for Pfand:

* SINGLE_USE
* REUSABLE
* NOT_APPLICABLE |
   ^sku_dimensions |object |N | |The dimensions of the sku.

Note:

* Provide the dimensions measured after packing the product.
* These values impact the shipping cost, so it is important to ensure that dimensions are accurate. Any discrepancies in measurements may lead to additional shipping fees.
* Optional for ID, TH, VN regions. |
   ^^length |string |Y |10 |The package length. A positive whole number.
   Note: For the BR market, decimal values using . or , as separators are also accepted but will be rounded to the nearest whole number. |
   ^^width |string |Y |10 |The package width. A positive whole number.
   Note: For the BR market, decimal values using . or , as separators are also accepted but will be rounded to the nearest whole number. |
   ^^height |string |Y |10 |The package height. A positive whole number.
   Note: For the BR market, decimal values using . or , as separators are also accepted but will be rounded to the nearest whole number. |
   ^^unit |string |Y |CENTIMETER |The unit for the package dimensions.
   Possible values based on region:
* US: CENTIMETER, INCH
* Other regions: CENTIMETER

Note: You must use the same system of measurement (metric system or imperial system) for package_weight and package_dimensions. In other words, if you are using KILOGRAM for the weight, you must use CENTIMETER for the dimensions. |
^sku_weight |object |N | |The weight of the sku
Note:

* All the products package weight is mandatory by default, except for products under Virtual Products categories.
* Provide the weight measured after packing the product.
* This value impacts the shipping cost, so it is important to ensure that dimensions are accurate. Any discrepancies in measurements may lead to additional shipping fees.
* The package weight will take precedence over package dimensions in fee calculation if the fee based on weight is higher. |
   ^^value |string |Y |1.32 |The package weight, which must be a positive number.
   The number format varies based on the unit:
* GRAM: integer
* KILOGRAM: up to 3 decimal places
* POUND: up to 2 decimal places |
   ^^unit |string |Y |KILOGRAM |The unit for the package weight.
   Possible values based on region:
* US: KILOGRAM, POUND
* BR, JP, MX: KILOGRAM, GRAM
* Other countries: KILOGRAM

Note: You must use the same system of measurement (metric system or imperial system) for package_weight and package_dimensions. In other words, if you are using KILOGRAM for the weight, you must use CENTIMETER for the dimensions. |
title |string |Y |Men's Fashion Sports Low Cut Cotton Breathable Ankle Short Boat Invisible Socks
|The product title.
Title length:

* DE, ES, FR, IE, IT, JP, UK, US: [1, 255]
* BR, MX: [1, 300]
* Other regions: [25, 255] |
   is_cod_allowed |bool |N |false |A flag indicating whether to show the Cash On Delivery (COD) payment option during checkout.
   Use the [Get Category Rules API](https://partner.tiktokshop.com/docv2/page/6509c0febace3e02b74594a9) to check if COD is supported for your product category.

Applicable only for the following markets:

* Global sellers: MY, PH, SA, TH, VN
* Local sellers: ID, MY, PH, SA, TH, VN

**Note**: If COD is not supported, the listing will fail if you set this to `true`. |
certifications |[]object |N | |The list of certifications for your product.
Max count: 10
As per TikTok Shop guidelines, certifications are required for certain restricted product categories. Retrieve the certification requirements for your product from the [Get Category Rules API](https://partner.tiktokshop.com/docv2/page/6509c0febace3e02b74594a9). Refer to [TikTok Shop Restricted Products Policy](https://seller-us.tiktok.com/university/essay?identity=1&role=1&knowledge_id=3238037484275457&from=policy) for information on product category restrictions. |
^id |string |Y |7182427311584347905 |The ID to identify the type of certification required for the product category.
Retrieve this value from the [Get Category Rules API](https://partner.tiktokshop.com/docv2/page/6509c0febace3e02b74594a9). |
^images |[]object |N | |A list of certification related images. |
^^uri |string |Y |tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe |The URI of the image.
Obtain this URI by uploading the images through the Upload Product Image API（文档 ID：`6509df95defece02be598a22`） with `use_case=CERTIFICATION_IMAGE`. |
^files |[]object |N | |A list of certification related files. |
^^id |string |Y |v09e40f40000cfu0ovhc77ub7fl97k4w |The ID of the certification file.
Use the [Upload Product File API](https://partner.tiktokshop.com/docv2/page/6509dffdc16ffe02b8dc10c5) to upload the files first and obtain the corresponding file ID. |
^^name |string |Y |Certificate.pdf |The name of the certification file, including the file extension. |
^^format |string |Y |PDF |The format of the certification file. Only PDF is supported. |
^expiration_date |int |N |1741235456 |The expiration date of this certification expressed in unix timestamp (seconds) UTC+0.
This field may be required for certain certifications. Use the [Get Category Rules API](https://partner.tiktokshop.com/docv2/page/6509c0febace3e02b74594a9) to find out the requirements. |
package_weight |object |N | |The weight of the product package.
**Note**:

* All the products package weight is **mandatory by default**, except for products under **Virtual Products** categories. [Get Categories API](https://partner.tiktokshop.com/docv2/page/get-categories-202309) e.g **Digital Games**.
* Provide the weight measured after packing the product.
* This value impacts the shipping cost, so it is important to ensure that dimensions are accurate. Any discrepancies in measurements may lead to additional shipping fees.
* The package weight will take precedence over package dimensions in fee calculation if the fee based on weight is higher. |
   ^value |string |Y |1.32 |The package weight, which must be a positive number.
   The number format varies based on the `unit`:
* `GRAM`: integer
* `KILOGRAM`: up to 3 decimal places
* `POUND`: up to 2 decimal places |
   ^unit |string |Y |KILOGRAM |The unit for the package weight.
   Possible values based on region:
* US: `KILOGRAM`, `POUND`
* BR, JP, MX: `KILOGRAM`, `GRAM`
* Other countries: `KILOGRAM`

**Note**: You must use the same system of measurement (metric system or imperial system) for `package_weight` and `package_dimensions`. In other words, if you are using `KILOGRAM` for the weight, you must use `CENTIMETER` for the dimensions. |
product_attributes |[]object |N | |A list of general attributes (e.g. manufacturer, country of origin, materials used) that describe the product as a whole, regardless of variant.
**Important**: The attributes available for use are determined by the system based on the product's assigned category, with some being mandatory. You must provide the product attributes marked as `is_required` in the response of the Get Attributes API（文档 ID：`6509c5784a0bb702c0561cc8`） to avoid listing failure. |
^id |string |Y |100392 |The ID of the product attribute, retrieved from the [Get Attributes API](https://partner.tiktokshop.com/docv2/page/6509c5784a0bb702c0561cc8). |
^values |[]object |Y | |A list of selectable values for the product attribute.
**Note**: Provide either a built-in ID or a custom name; if both are provided, the ID takes priority. |
^^id |string |N |1001533 |The ID of the product attribute value.
This is either a built-in product attribute value ID from [Get Attributes API](https://partner.tiktokshop.com/docv2/page/6509c5784a0bb702c0561cc8) or a custom product attribute value ID returned after calling [Create Product API](https://partner.tiktokshop.com/docv2/page/6502fc8da57708028b42b18a). |
^^name |string |N |Birthday |A self-defined custom product attribute value if the built-in values do not satisfy your needs. The system will auto-generate an ID after editing.
**Note**:

* No duplicates allowed under the same attribute.
* Max length: 2000 characters |
   size_chart |object |N | |The measurement details of the product to help buyers find the right size.

**Note**:

* For certain product categories, size charts may be required or not supported. Use the [Get Category Rules API](https://partner.tiktokshop.com/docv2/page/6509c0febace3e02b74594a9) to check the requirements.
* If size charts are not supported, even if you provide a size chart here, the size chart will not be saved.
* Provide either a TikTok Shop size chart template ID or a size chart image; if both are provided, the ID takes priority. |
   ^image |object |N | |An image of the size chart.

**Recommendations**:

* Resolution: Minimum 1024px on the shorter side
* Content: Include key measurement dimensions (e.g., bust, waist, hips, inseam), the more the better.
* Format: Use a table with distinct columns and row.
   * Use only one table per product and image.
   * Display each dimension in a separate row.
   * Display units in column headers. |
      ^^uri |string |Y |tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe |The URI of the size chart image.
      Obtain this URI by uploading the images through the Upload Product Image API（文档 ID：`6509df95defece02be598a22`） with `use_case=SIZE_CHART_IMAGE`. |
      ^template |object |N | |A TikTok Shop size chart template generated by the size chart tool in Seller Center > Manage Products > Bulk action > Batch manage size charts. |
      ^^id |string |Y |7267563252536723205 |The size chart template ID. |
      package_dimensions |object |N | |The dimensions of the product package.

**Note**:

* Provide the dimensions measured after packing the product.
* These values impact the shipping cost, so it is important to ensure that dimensions are accurate. Any discrepancies in measurements may lead to additional shipping fees.
* Optional for ID, TH, VN regions. |
   ^length |string |Y |10 |The package length. A positive whole number.
   **Note**: For the BR market, decimal values using `.` or `,` as separators are also accepted but will be rounded to the nearest whole number. |
   ^width |string |Y |10 |The package width. A positive whole number.
   **Note**: For the BR market, decimal values using `.` or `,` as separators are also accepted but will be rounded to the nearest whole number. |
   ^height |string |Y |10 |The package height. A positive whole number.
   **Note**: For the BR market, decimal values using `.` or `,` as separators are also accepted but will be rounded to the nearest whole number. |
   ^unit |string |Y |CENTIMETER |The unit for the package dimensions.
   Possible values based on region:
* US: CENTIMETER, INCH
* Other regions: CENTIMETER

**Note**: You must use the same system of measurement (metric system or imperial system) for `package_weight` and `package_dimensions`. In other words, if you are using KILOGRAM for the weight, you must use CENTIMETER for the dimensions. |
external_product_id |string |N |172959296971220002 |An external identifier used in an external ecommerce platform. This is used to associate the product between TikTok Shop and the external ecommerce platform.
Max length: 999 characters |
delivery_option_ids |[]string |N |["1729592969712203232"] |This field is returned for seller accounts in the following regions only:

* ID
* MX
* MY
* PH
* SG
* TH
* VN

For all other regions, this field is NOT used and will NOT be processed if passed for create, edit, or partial edit operations.
The custom delivery option IDs to apply to this product if you want to override the default warehouse delivery options. To retrieve the available option IDs, call [Get Warehouse Delivery Options](https://partner.tiktokshop.com/docv2/page/650aa46ebace3e02b75d9afa) with `scope=PRODUCT`.
**Note**:

* Leave this field blank to inherit the default delivery options configured for the warehouse.
* If you are saving a post-live draft with `save_mode=AS_DRAFT`, this field is not supported and will not be saved. When using Get Product to retrieve the draft, the values will reflect those in the base version. |
   video |object |N | |A product introduction or promotion video to display for your product.

**Recommendations**:

* Aspect ratio: 1:1
* Resolution: HD 720p or higher
* Duration: 20 - 60 seconds |
   ^id |string |Y |v09e40f40000cfu0ovhc77ub7fl97k4w |The ID of the product video.
   Use the [Upload Product File API](https://partner.tiktokshop.com/docv2/page/6509dffdc16ffe02b8dc10c5) to upload the video first and obtain the corresponding file ID. |
   category_version |string |N |v1 |Filter categories by the category tree version.Possible values based on region:
* US, EU and SEA: v2, represents the 7-level category tree.
   Important: For US, EU and SEA shops, you must pass v2 when using this API.
* Other regions: v1, represents the 3-level category tree.Default: v1 |
   manufacturer_ids |[]string |N |["172959296971220002"] |A comma-delimited list of manufacturer IDs. Retrieve the IDs from the Search Manufacturers API（文档 ID：`67066a580dcee902fa03ccf9`）.

**Note**: Applicable only for the EU market in certain categories. Use the Get Category Rules API（文档 ID：`6509c0febace3e02b74594a9`） to check the requirements. |
responsible_person_ids |[]string |N |["172959296971220003"] |A comma-delimited list of responsible person IDs. Retrieve the IDs from the Search Responsible Persons API（文档 ID：`67066a55f17b7d02f95d2fb1`）.
**Note**: Applicable only for the EU market in certain categories. Use the Get Category Rules API（文档 ID：`6509c0febace3e02b74594a9`） to check the requirements. |
listing_platforms |[]string |N |["TIKTOK_SHOP"] |The platforms for listing the product.
Possible values:

* TOKOPEDIA
* TIKTOK_SHOP
   Applicable only for sellers that migrated from Tokopedia.

**IMPORTANT**: This field controls the product's visibility on the listing platforms.

* If the product is live on both platforms but the request contains only 1 platform, the product will be deactivated and hidden from the omitted platform.
* If the product is live on 1 platform but the request contains a different platform, the product will be deactivated and hidden from the omitted platform.
* If you omit this array, the product will be sent for audit on the currently active platforms or on the platforms specified in the previous request.
* If you want to deactivate the product on both platforms, use the Deactivate Product API. |
   shipping_insurance_requirement |string |N |REQUIRED |The shipping insurance purchase requirement imposed on buyers for the product.

Possible values:

* REQUIRED: Shipping insurance is mandatory and buyers can't opt out.
* OPTIONAL: Buyers can choose to purchase shipping insurance through the platform.
* NOT_SUPPORTED: Shipping insurance is not supported for the product.
   Default: OPTIONAL

Applicable only if the listing platforms include TOKOPEDIA. |
is_pre_owned |bool |N |false |A flag to indicate if the product is pre-owned.
Applicable only if TOKOPEDIA is the sole listing platform.
**Note**: To list pre-owned products on the TikTok Shop platform, please specify the ID of one of the designated pre-owned product categories (e.g. pre-owned luxury bags, luggage, and accessories) in `category_id`. |
minimum_order_quantity |int |N |1 |The minimum order quantity for the product.
Valid range: [1, 20]
Applicable only for the Indonesia market and selected sellers in other SEA markets. Contact your account manager for more information about gaining access to this field. |
replicated_products |[]object |N | |The list of local market replicas to which updates should be synced. As this is a full edit endpoint, all fields will be synced.
Note that **category changes** and **sales attribute changes** (in sales attribute id/name) must be synced to other markets. Therefore, you must provide the `seller_sku` above and complete the details in this object. The API call will fail if you don't provide these details. |
^region |string |Y |US |The market where you want to publish the global product.Possible values:

* AT: Austria
* BE:Belgium
* CZ:Czech Republic
* DE: Germany
* ES: Spain
* FR: France
* GB: United Kingdom
* GR: Greece
* HU:Hungary
* ID: Indonesia
* IE: Ireland
* IT: Italy
* JP: Japan
* MY: Malaysia
* NL: Netherlands(NL)
* PH: Philippines
* PO: Poland
* PT:Portugal
* SG: Singapore
* TH: Thailand
* US: United States
* VN: Vietnam
* MX: Mexico |
   ^skus |[]object |N | |The SKUs to be synced to the specified market.

**Note**:

* You must pass in all existing SKUs. Any existing SKU IDs not listed here will result in the deletion of those SKUs. For example, if this product contains 5 SKUs and you only provide 2 SKU IDs, the remaining 3 will be deleted.
* To create new SKUs, leave the SKU ID blank and provide the seller_sku. |
   ^^id |string |N |1729592969712207001 |The SKU ID generated by TikTok Shop. Provide this for existing SKUs. |
   ^^seller_sku |string |N |Color-Red-XM002 |The seller_sku value of the source product above. Provide this for new SKUs.
* Valid length: 1-50 characters
* Format: Text without spaces |
   ^^price |object |Y | |The SKU's **local display price** shown on the product page before any discounts. |
   ^^^currency |string |Y |USD |The currency.
   Possible values based on the region:
* BRL: Brazil
* CZK: Czech Republic
* EUR: France, Germany, Ireland, Italy, Spain, Netherlands, Belgium, Austria, Greece, Portugal
* GBP: United Kingdom
* HUF: Hungary
* IDR: Indonesia
* JPY: Japan
* MXN: Mexico
* MYR: Malaysia
* PHP: Philippines
* PLN: Poland
* SGD: Singapore
* THB: Thailand
* USD: United States
* VND: Vietnam |
   ^^^sale_price |string |Y |1.21 |The SKU's local display price shown on the product page before any discounts.
   Refer to [Product Pricing](https://partner.tiktokshop.com/docv2/page/67e1288d76cfee049d9af858) for the allowed price ranges in each market. |
   ^^inventory |[]object |N | |SKU inventory information per warehouse. This field is mandatory for other regions. But when syncing products from the US to MX, the MX product inventory field is optional. |
   ^^^warehouse_id |string |N |7068517275539719942 |The warehouse ID. Retrieve this value from the Get Warehouse List API（文档 ID：`650aa418defece02be6e66b6`） or Get Inventory Rules API. This field is mandatory for other regions. But when syncing products from the US to MX, the MX product inventory field is optional. |
   ^^^quantity |int |N |999 |The SKU quantity available in the warehouse.
   Valid range: [1, 999,999]. This field is mandatory for other regions. But when syncing products from the US to MX, the MX product inventory field is optional. |
   ^inventory_mode |string |N |SHARED |Defines the inventory mode for the duplicated target product. This parameter supports two modes: SHARED and EXCLUSIVE.
* SHARED: In this mode, the inventory of all interconnected (shared) products must be strictly consistent; otherwise, an error will be returned.
* EXCLUSIVE: In this mode, the inventory for each product can be set independently without affecting others.

Applicability:
This feature is applicable ONLY for the EU market.
Default Value:
If left empty, the system defaults to the EXCLUSIVE mode. |
subscribe_info_edit |object |N | |All the editable Save and Subscribe promotion info associated with the given product. |
^subscribe_status |string |N |ENABLED |An enum outlining whether the given product has an active Subscribe and Save promotion:

* ENABLED
* NOT_ENABLED

This field is required if the subscription is being created or modified. |
^discount_details |[]object |N | |All of the Save and Subscribe discount details. |
^^discount_level |string |N |REGULAR |An enum that communicated the type of discount:

* REGULAR
* FIRST_ORDER
* RETENTION |
   ^^discount_value |int |N |10 |The value of the discount. A value of 10, would indicate a 10% discount. |
   shipping_template_id |string |N |7552764259994699538 |Identifier of the shipping template that will be bound to the product |
   scheduled_sale |object |N | |Scheduled listing configuration for the product, including whether scheduled listing is enabled and the scheduled listing time. |
   ^is_enabled_scheduled_sale |bool |Y |false |Whether scheduled listing is enabled for this product. If true, scheduled_sale_time must be provided. |
   ^schedule_sale_time |int |Y |1768899145000 |Scheduled listing time, expressed as a Unix timestamp in milliseconds; must be later than the current time and within 90 days, and is required when is_enabled_scheduled_sale is true. |
   locale |string |N |en-US |The BCP-47 locale codes for displaying category information.
   Default: The default locale of your shop.
   Possible values:
* cs-CZ
* de-AT
* de-BE
* de-DE
* el-GR
* en-GB
* en-IE
* en-US
* es-ES
* es-MX
* fr-FR
* fr-BE
* hu-HU
* id-ID
* it-IT
* ja-JP
* ms-MY
* nl-NL
* nl-BE
* pl-PL
* pt-BR
* pt-PT
* th-TH
* vi-VN
* zh-CN |
   auto_translate_enabled |bool |N |false |The field works only if products need to list with more than one languages in determined country, otherwise it does not need to fill in. |
   search_terms |[]string |N |["sneakers","running shoes","athletic"] |Search terms (ST words). ST words will not be displayed to consumers; they are only used in search engines to increase your search weight and gain more traffic. Please ensure that ST words are consistent with the product description, with a maximum of 15 terms and a total of no more than 250 characters. |
   key_product_features |[]string |N |["Breathable mesh upper", "Cushioned foam midsole"] |Key Product Features. They will be displayed in the Product highlight module on the product detail page and will be used by search engines to increase your search weight for more traffic. The total number of items should not exceed 5, and the total character count should not exceed 1500. |
   inventory_mode |string |N |SHARED |Defines the inventory mode for the duplicated source product. This parameter supports two modes: SHARED and EXCLUSIVE.
* SHARED: In this mode, the inventory of all interconnected (shared) products must be strictly consistent; otherwise, an error will be returned.
* EXCLUSIVE: In this mode, the inventory for each product can be set independently without affecting others.

Applicability:
This feature is applicable ONLY for the EU market.
Default Value:
If left empty, the system defaults to the EXCLUSIVE mode. |
product_tag_operations |[]object |N | |product tag to identity special type product
Possible values: AUCTION |
^product_tag |string |Y |AUCTION |Possible values: AUCTION |
^enable |bool |Y |false |true,false |
# Request Sample
**Query**
```Plain Text
https://open-api.tiktokglobalshop.com/product/202309/products/1729409636071801988?app_key=123abc&sign=5361235029d141222525e303d742f9e38aea052d10896d3197ab9d6233730b8c&timestamp=1625484268&shop_cipher=ROW_RHkDDABBAAB8tKAVoAqsMTjsQZFLyNfY
```

**Body**
```json
{"save_mode":"AS_DRAFT","description":" \u003cp\u003ePlease compare above detailed size with your measurement before purchase.\u003c/p\u003e\n\u003cul\u003e \n  \u003cli\u003eM-Size\u003c/li\u003e\n  \u003cli\u003eXL-Size\u003c/li\u003e\n\u003c/ul\u003e \n\u003cimg src=\"https://p16-oec-va.ibyteimg.com/tos-maliva-i-o3syd03w52-us/181595ea7d26489284b5667488d708c1~tplv-o3syd03w52-origin-jpeg.jpeg?from=1432613627\" width='100' height='100' /\u003e","category_id":"600001","brand_id":"7082427311584347905","main_images":[{"uri":"tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe"}],"skus":[{"id":"1729592969712207000","sales_attributes":[{"id":"100089","name":"Specification","value_id":"1729592969712401100","value_name":"XL","sku_img":{"uri":"tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe"},"supplementary_sku_images":[{"uri":"tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe"}]}],"seller_sku":"Color-Red-XM001","price":{"amount":"1.21","currency":"USD","sale_price":"1.21","starting_bid_price":"2.3"},"external_sku_id":"1729592969712207012","identifier_code":{"code":"12345678901234","type":"GTIN"},"inventory":[{"warehouse_id":"7068517275539719942","quantity":999}],"combined_skus":[{"product_id":"1729582718312380123","sku_id":"2729382476852921560","sku_count":2}],"sku_unit_count":"100.00","external_urls":["https://example.com/path1","https://example.com/path2"],"extra_identifier_codes":["00012345678905","9780596520687"],"pre_sale":{"type":"PRE_ORDER","fulfillment_type":{"handling_duration_days":7,"release_date":1619611761}},"list_price":{"amount":"1","currency":"USD"},"external_list_prices":[{"source":"SHOPIFY_COMPARE_AT_PRICE","amount":"1","currency":"USD"}],"fees":[{"type":"PFAND","amount":"1.01","additional_attribute":"SINGLE_USE"}],"sku_dimensions":{"length":"10","width":"10","height":"10","unit":"CENTIMETER"},"sku_weight":{"value":"1.32","unit":"KILOGRAM"}}],"title":"Men's Fashion Sports Low Cut Cotton Breathable Ankle Short Boat Invisible Socks\n","is_cod_allowed":false,"certifications":[{"id":"7182427311584347905","images":[{"uri":"tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe"}],"files":[{"id":"v09e40f40000cfu0ovhc77ub7fl97k4w","name":"Certificate.pdf","format":"PDF"}],"expiration_date":1741235456}],"package_weight":{"value":"1.32","unit":"KILOGRAM"},"product_attributes":[{"id":"100392","values":[{"id":"1001533","name":"Birthday"}]}],"size_chart":{"image":{"uri":"tos-maliva-i-o3syd03w52-us/c668cdf70b7f483c94dbe"},"template":{"id":"7267563252536723205"}},"package_dimensions":{"length":"10","width":"10","height":"10","unit":"CENTIMETER"},"external_product_id":"172959296971220002","delivery_option_ids":["1729592969712203232"],"video":{"id":"v09e40f40000cfu0ovhc77ub7fl97k4w"},"category_version":"v1","manufacturer_ids":["172959296971220002"],"responsible_person_ids":["172959296971220003"],"listing_platforms":["TIKTOK_SHOP"],"shipping_insurance_requirement":"REQUIRED","is_pre_owned":false,"minimum_order_quantity":1,"replicated_products":[{"region":"US","skus":[{"id":"1729592969712207001","seller_sku":"Color-Red-XM002","price":{"currency":"USD","sale_price":"1.21"},"inventory":[{"warehouse_id":"7068517275539719942","quantity":999}]}],"inventory_mode":"SHARED"}],"subscribe_info_edit":{"subscribe_status":"ENABLED","discount_details":[{"discount_level":"REGULAR","discount_value":10}]},"shipping_template_id":"7552764259994699538","scheduled_sale":{"is_enabled_scheduled_sale":false,"schedule_sale_time":1768899145000},"locale":"en-US","auto_translate_enabled":false,"search_terms":["sneakers","running shoes","athletic"],"key_product_features":["Breathable mesh upper","Cushioned foam midsole"],"inventory_mode":"SHARED","product_tag_operations":[{"product_tag":"AUCTION","enable":false}]}
```

# Response Parameters
| Properties | Type | Sample | Properties description |
| --- | --- | --- | --- |
| code | int | 0 | The success or failure status code returned in API response. |
| message | string | Success | The success or failure messages returned in API response. Reasons of failure will be described in the message. |
| request_id | string | 202203070749000101890810281E8C70B7 | Request log |
| data | object |  | Specific return information |
| ^product_id | string | 1729592969712207008 | The product ID generated by TikTok Shop. |
| ^skus | []object |  | A list of Stock Keeping Units (SKUs) used to identify distinct variants of the product. |
| ^^id | string | 1729592969712207012 | The SKU ID generated by TikTok Shop. One product can contain multiple SKU IDs. |
| ^^seller_sku | string | Color-Red-XM001 | An internal code/name for managing SKUs, not visible to buyers. |
| ^^sales_attributes | []object |  | A list of attributes (e.g. size, color, length) that define each variant of a product. |
| ^^^id | string | 100000 | The sales attribute ID. |
| If you included the custom sales attribute name in the request, this is a newly generated ID. |  |  |  |
| ^^^value_id | string | 1729592969712207123 | The sales attribute value ID. |
| If you included the custom sales attribute value name in the request, this is a newly generated ID. |  |  |  |
| ^^external_sku_id | string | 1729592969712207234 | An external identifier used in an external ecommerce platform. This is used to associate the SKU between TikTok Shop and the external ecommerce platform. |
| ^^fees | []object |  | The fees required for this product based on TikTok Shop policies. Fees are required only for certain product categories, retrieve the requirements from the [Get Category Rules API](https://partner.tiktokshop.com/docv2/page/6509c0febace3e02b74594a9). |
| ^^^type | string | PFAND | The type of fee. |
| Possible values: PFAND |  |  |  |
| ^^^amount | string | 1.01 | The fee amount. |
| Valid range: |  |  |  |

* PFAND: [0.00 - 6300.00] |
   ^^^additional_attribute |string |SINGLE_USE |An optional attribute that provides additional context for the fee. The accepted values may vary by fee type and market.

Possible values for Pfand:

* SINGLE_USE
* REUSABLE
* NOT_APPLICABLE |
   ^warnings |[]object | |Warning information that the API caller needs to pay special attention to. |
   ^^message |string |The [brand_id]:123 field is incorrect and has been automatically cleared by the system. Reason: [Brand does not exist]. You can edit it later. |A warning message for any critical problems/blockers. Please respond in a timely manner. |
   ^audit |object | |Product audit information.
   **Note**: Applicable only to products listed on TikTok Shop. Not applicable for products listed only on Tokopedia. |
   ^^status |string |AUDITING |The product audit status.
   Possible values:
* NONE: The product is not applicable for audit because it has not been submitted for listing on this platform, or it is in a draft, frozen, or deactivated state.
* AUDITING: The product is currently being audited.
* APPROVED: If you only edited the `price` or `inventory` fields of an approved product, the product remains approved and the new information is immediately published on the platform. |

# Response Sample
```json
{"code":0,"data":{"product_id":"1729592969712207008","skus":[{"id":"1729592969712207012","seller_sku":"Color-Red-XM001","sales_attributes":[{"id":"100000","value_id":"1729592969712207123"}],"external_sku_id":"1729592969712207234","fees":[{"type":"PFAND","amount":"1.01","additional_attribute":"SINGLE_USE"}]}],"warnings":[{"message":"The [brand_id]:123 field is incorrect and has been automatically cleared by the system. Reason: [Brand does not exist]. You can edit it later."}],"audit":{"status":"AUDITING"}},"message":"Success","request_id":"202203070749000101890810281E8C70B7"}
```

# Error Code
For common error codes, refer to [How to call TikTok Shop APIs - Common Error Code](https://partner.tiktokshop.com/docv2/page/64f199679495ef0281851ee5#Back%20To%20Top)
| Code | Message |
| --- | --- |
| 12019006 | product description is invalid |
| 12019011 | product package weight is invalid |
| 12019012 | product package size is invalid |
| 12019013 | brand id is invalid |
| 12019019 | sale property is invalid |
| 12019022 | SKU must contain a valid warehouse. |
| 12019056 | sku not allow add |
| 12019057 | sku not allow delete |
| 12019061 | Product weight or dimensions unit does not support the imperial units on non-US local products. |
| 12019095 | `pre_sale.fulfillment_type` is missing or empty. |
| 12019096 | The value for `pre_sale.type` is missing. |
| 12019097 | `pre_sale.fulfillment_type.release_date` must be set to a non-zero value. |
| 12019098 | `pre_sale.fulfillment_type.handling_duration_days` must be set to a non-zero value. |
| 12019100 | All SKUs of a product must have the same `pre_sale.type`. Do not assign different values. |
| 12019215 | deposit balance is not enough |
| 12052002 | Incorrect category format |
| 12052003 | Incorrect parcel height format |
| 12052004 | Incorrect parcel width format |
| 12052005 | Incorrect parcel length format |
| 12052013 | The product description cannot exceed maximum characters |
| 12052015 | The product description is required |
| 12052023 | Category does not exist |
| 12052024 | Category is not final category |
| 12052025 | The category is invalid |
| 12052026 | Brand does not exist |
| 12052028 | Main product image is required |
| 12052032 | The product does not exist |
| 12052034 | This product doesn't belong to this shop |
| 12052037 | Couldn't update inventory. Possible causes: |

* Inventory is automatically allocated and cannot be modified manually
* Warehouse IDs provided are incorrect
* Missing warehouse IDs (all warehouses that stock the product must be included) |
   12052038 |Product price locked due to ongoing promotion. |
   12052048 |You cannot edit the specified product(s) as it isn't listed in your account or shop. |
   12052050 |A single product cannot have more than 100 different SKUs |
   12052051 |The product name exceed max limit characters |
   12052054 |The seller SKU text length cannot exceed max limit characters |
   12052055 |The SKU inventory quantity for the warehouse must be within allowed limits. |
   12052056 |The num of image in description cannot exceed max limit |
   12052073 |The product price is invalid |
   12052084 |The provided currency is not available for this shop/region. |
   12052092 |product sale price is invalid |
   12052094 |No multiple warehouse permission |
   12052095 |Warehouse information parsing error |
   12052096 |Unable to update the price for SKUs with no warehouse. Assign a warehouse and try again. |
   12052097 |The warehouse does not exist |
   12052104 |property is required |
   12052105 |required qualification miss |
   12052115 |seller has no warehouse |
   12052116 |product package size is invalid |
   12052128 |Size chart not found |
   12052141 |please edit stock from global |
   12052144 |platform warehouse not support to edit |
   12052151 |product property value contain restricted words |
   12052152 |sale property name contains restricted words |
   12052153 |sale property value contains restricted words |
   12052158 |category unable to change |
   12052159 |unique item total quantity must be one |
   12052160 |sku count must be one and disable variables |
   12052162 |unique item sku count must be one and disable varialbes |
   12052163 |The gift product are not allowed to be edited |
   12052181 |The package weight of the product can not be zero. |
   12052182 |The '{{sub_property_name}}' field is required as you've selected '{{parent_property_value}}' for '{{parent_property_name}}'. |
   12052183 |The '{{sub_property_name}}' field should be left empty as you've selected '{{parent_property_value}}' for '{{parent_property_name}}'. |
   12052200 |brand is expired |
   12052201 |You are not authorized to sell this brand in this category. To do so, apply through the Qualification Center in Seller Center. |
   12052207 |receipt brand not support warehouse |
   12052208 |A brand authorization is required to publish this listing. |
   12052217 |All region shops must use V2 categories. Check the documentation for further details. |
   12052220 |This category is prohibited or unsupported on TikTok Shop. Select another category. |
   12052221 |Only whitelisted sellers are permitted to trade under current category |
   12052222 |category do not support cod |
   12052223 |This category is restricted. To sell in this category, apply through the Qualification Center in Seller Center. |
   12052225 |You are not authorized to sell in this category because it does not fall under your shop's main category. Contact your account manager for help or select another category. |
   12052226 |This category is restricted. To sell in this category, apply through the Qualification Center in Seller Center. |
   12052227 |the category is unauthorized or unavailable |
   12052230 |Category version and categoryID are not matched. |
   12052235 |The format of url is invalid |
   12052238 |The length of the url is greater than 200 |
   12052240 |Do not support custom property. |
   12052241 |attribute name or attribute id is empty. |
   12052242 |The attribute name characters cannot exceed max_limit |
   12052243 |The product attribute or sale attribute name characters contain Chinese. |
   12052244 |The attribute name duplicate. |
   12052245 |The product attributes contained invalid characters. Please modify and re-submit. |
   12052246 |The {{property_type}} not support multi selected, attribute id is :{{property_id}}. |
   12052247 |Do not support custom product attribute. |
   12052248 |The {{property_type}} value name or attribute value id is empty. |
   12052249 |The {{property_type}} value name characters cannot exceed {{max_limit}}, attribute value name is :{{property_value_name}}. |
   12052250 |The {{property_type}} value name characters contain Chinese. |
   12052251 |Duplicated attribute values found for an attribute. Remove or modify the duplicated value. |
   12052253 |Duplicate attribute value id |
   12052254 |Duplicate attribute id |
   12052256 |The {{property_name}} value need to be positive integers or positive decimals . |
   12052260 |The product ID does not exist |
   12052261 |product name is empty |
   12052262 |Chinese characters are not supported in product name |
   12052263 |product name prefix illegal |
   12052273 |After the pre-sale product has been onlive product, the pre-sale info cannot be modified. |
   12052275 |sku's mto day is invalid |
   12052278 |seller does not support make to order |
   12052282 |Product manufacturer is required. |
   12052284 |Manufacturer ID {{manufacturer_id}} is not found |
   12052285 |Manufacturer ID {{manufacturer_id}} is not associated with the seller |
   12052287 |Product responsible person is required |
   12052289 |Responsible person ID {{rp_id}} is not found |
   12052294 |The format of the extra identification code is incorrect. |
   12052300 |product main image uri illegal |
   12052301 |Width and length of main image must be at least {{min_limit}}, check uri {{uri}} |
   12052302 |The main images size exceed limit. |
   12052304 |Main product image format not support. |
   12052305 |The main images aspect ratio cannot exceed max limit. |
   12052306 |main product images count exceed limit |
   12052307 |skus in the lottery cannot be deleted |
   12052308 |There's an ongoing appeal. If you wish to edit product details, please revoke the appeal first. |
   12052310 |The futures information filled in by the seller does not meet the requirements. |
   12052311 |The number of backorder product exceeds the limit max_num, or the proportion of backorder product exceeds the limit max_ratio |
   12052314 |Standard product cannot be converted to MTO product |
   12052315 |Standard product cannot be converted to preorder product |
   12052316 |product second hand not applicable in this sale platform |
   12052317 |purchase order quantity not support |
   12052319 |maximum order quantity smaller than minimum order quantity |
   12052324 |Product description image file format is not supported |
   12052329 |A pre-order product can't be changed to a regular product |
   12052330 |product is not supported to list in designated sale platform |
   12052332 |The seller center is locked during shop integration, only editing stock and price is allowed |
   12052340 |product description image uri illegal |
   12052341 |The description images size cannot exceed limit. |
   12052342 |The description images space cannot exceed limit. |
   12052343 |Product description image format not support. |
   12052344 |The product description html syntax with error |
   12052345 |The product description html tag not support. |
   12052346 |The product description has Chinese characters |
   12052348 |The product description html tag required attribute is miss. |
   12052349 |The product description html tag not support nest. |
   12052350 |The product description html tag contain illegal attribute. |
   12052352 |The product description nest exceeding limit |
   12052357 |'supplementary_sku_images' is only allowed when 'sku_img' is specified. Add an image to 'sku_img' and try again. |
   12052359 |save subscribe not support |
   12052360 |The video id is not exist. |
   12052361 |This base unit value count is not supported. The supported base unit values can be obtained from the Get Attribute API. |
   12052362 |SKU unit count is required. |
   12052364 |The warehouse is unavailable because this product cannot be shipped to the target market from this warehouse. |
   12052365 |The manufacturer lacks language version information for this market. |
   12052371 |Auction product is bidding when it is not supported to change product info |
   12052372 |Generate EU energy label image failed |
   12052375 |product list price is invalid |
   12052376 |list price not support |
   12052382 |Can't edit Dilayani Tokopedia warehouse quantity |
   12052383 |product list price exceed limit |
   12052385 |Please enter valid certificate expiration date |
   12052393 |Product locked for Promotion and stock can't be updated below current stock |
   12052402 |seller shipping template is empty |
   12052403 |The warehouse does not support fulfillment for the current shop. |
   12052404 |multi-warehouse not support customize logistics service |
   12052405 |The warehouse has not opened the subscribed logistics service |
   12052420 |warehouse didn't set logistics service |
   12052424 |Missing 'sale price' value |
   12052446 |Category is not open in this market |
   12052465 |warehouse is unavailable for eu gpr product |
   12052490 |The handling time must be within the allowed limits. |
   12052503 |If the inventory allocation mode is SHARED, the inventory quantity must be the same across all SKUs. |
   12052508 |The SKU ID in `replicated_products` is invalid and cannot be found. |
   12052509 |Missing seller_sku in `replicated_products`. You must indicate the seller_sku for all new SKUs. |
   12052510 |No matching seller_sku found in the source product. Ensure you indicate the seller_sku in both `skus.seller_sku` and `replicated_products.skus.seller_sku`. |
   12052511 |Missing SKU details in `replicated_products`. You must complete the SKU details. |
   12052512 |No replicas exist for this product. You can replicate the product first by using the Replicate Product endpoint. |
   12052513 |No replicas exist for this product in the stated region. You can replicate the product first by using the Replicate Product endpoint. |
   12052514 |Missing regions in `replicated_products`. The category was changed, therefore you must sync the product to all other markets where replicas exist. |
   12052515 |Missing regions in `replicated_products`. The sales attributes were changed, therefore you must sync the product to all other markets where replicas exist. |
   12052516 |Missing inventory details. You must include all warehouse IDs assigned to the SKU, along with the respective quantity. Do not omit any or add unrelated warehouses. |
   12052520 |product sale property image uri illegal |
   12052521 |The sale property images size over limit. |
   12052522 |Product sale property image is required |
   12052523 |Product sale property image format not support. |
   12052524 |The sale property image aspect ratio invalid |
   12052525 |The attribute max num cannot exceed 3. |
   12052526 |The attribute value max num over limit. |
   12052527 |The sale attribute id not exist. |
   12052528 |You can add images to only 1 product variation, which will serve as the primary variation for display in the product options gallery. |
   12052529 |The property value id not exist. |
   12052530 |The warehouse ' {{warehouse ID}} ' does not belong to this shop/seller. |
   12052531 |The warehouse is disabled. |
   12052532 |the warehouse not delivery warehouse |
   12052533 |Removal, addition, and change of warehouses are not permitted. Please specify the original warehouses for the SKUs. |
   12052534 |warehouse unable to delete |
   12052535 |Couldn't publish this product as you haven't set the return warehouse for your shop. Add the return warehouse information on TikTok Shop Seller Center first and try again. |
   12052550 |SKU property must contain all properties |
   12052553 |Sku id duplicate |
   12052554 |sku name contain Chinese characters |
   12052557 |The SKU ID does not belong to the product. |
   12052558 |Number of product skus exceed limit. |
   12052559 |The product with duplicate default sku. |
   12052560 |The SKU contains duplicate sales attribute. |
   12052570 |product price exceed limit |
   12052571 |Missing price for SKU(s) |
   12052572 |the sale price is invalid |
   12052574 |unit price config is invalid |
   12052592 |Identifier code already entered, cannot enter the same code twice |
   12052593 |The identifier code cannot be changed once be submitted |
   12052650 |product qualification image uri illegal |
   12052651 |The qualification images size over limit. |
   12052655 |qualification id not exist |
   12052656 |qualification id duplicate |
   12052657 |qualification image and pdf file is out of limit. |
   12052658 |product qualification file uri illegal |
   12052670 |The size chart image URI is invalid. Note: API users must use the URI generated by the Upload Product Image API. |
   12052671 |The sizechart images size over limit. |
   12052673 |Product sizechart image is required |
   12052700 |The seller is inactive. |
   12052701 |do not support cross-boarder seller create local product directly |
   12052702 |seller does not support pre-order |
   12052703 |Invalid seller tax number |
   12052704 |seller id not exist |
   12052706 |The minimum sales quantity should not be exceed limit |
   12052707 |Setting minimum sales quantity is not supported |
   12052712 |sku's pre_order is invalid |
   12052805 |Bundle does not support adding this product type |
   12052815 |product in bundle deal cannot set minimum sale quantity |
   12052832 |The sub-SKU coefficient associated with each combo SKU cannot exceed {{max_limit}}, and cannot less {{min_limit}}. |
   12052834 |The number of combo sku associated with a sku cannot exceed limit. |
   12052835 |Sub product ID not exist |
   12052836 |The category of the combo is inconsistent with the category of the main sub-product. |
   12052838 |The first-level categories of the sub-products in the combo are inconsistent |
   12052841 |The sub-sku relationship corresponding to different combo sku cannot be duplicated. |
   12052843 |The main sub-product in the combo cannot be changed |
   12052844 |The sub-sku is not in the sub-product |
   12052846 |combo does not support adding this product type |
   12052847 |The combo sku relationship cannot be changed |
   12052850 |The stock of combo does not support being edited. |
   12052853 |The sale property of combo mismatch. |
   12052857 |Combined products and normal products cannot be converted to each other. |
   12052859 |When the combined SKU is only associated with one sub-SKU, the coefficient of this sub-SKU cannot be less than 2. |
   12052863 |All SKU of a combined product need to be the combined SKU. |
   12052864 |Unable to add deactivated SKUs to the combined product. |
   12052881 |identity internal error |
   36009003 |Internal error. Please try again. If the issue persists after multiple attempts, please contact platform support. |
   12052901 |The product in its current status is not available for this operation. Change the product status and try again. |
   12052902 |The SKU list is empty. Either omit the list entirely, or provide all required details. |
   12052910 |Invalid input parameters. Refer to the API documentation for details. |
   12052915 |package weight unit and dimension unit miss match. |
   12052921 |Couldn't edit the inventory quantity because this product shares the inventory with the source shop |
   12052922 |edit fields limit |
   12052931 |The title must follow these formatting rules: it cannot contain HTML escape characters (e.g.,  ), emojis, or ASCII control characters (e.g., \u007F). It also cannot consist solely of symbols (e.g., //// or !@#$$$&), nor can it have more than 9 consecutive repeated characters (e.g., aaaaaaaaa or 111111111). |
   12052932 |The description must follow these formatting rules: it cannot contain HTML escape characters (e.g.,  ), emojis, or ASCII control characters (e.g., \u007F). It also cannot consist solely of symbols (e.g., //// or !@#$$$&), nor can it have more than 9 consecutive repeated characters (e.g., aaaaaaaaa or 111111111). |
   12052933 |Sales attribute names must follow these formatting rules: it cannot contain HTML escape characters (e.g.,  ), emojis, or ASCII control characters (e.g., \u007F). It also cannot consist solely of symbols (e.g., //// or !@#$$$&), nor can it have more than 9 consecutive repeated characters (e.g., aaaaaaaaa or 111111111). |
   12052934 |Sales attribute value names must follow these formatting rules: it cannot contain HTML escape characters (e.g.,  ), emojis, or ASCII control characters (e.g., \u007F). It also cannot consist solely of symbols (e.g., //// or !@#$$$&), nor can it have more than 9 consecutive repeated characters (e.g., aaaaaaaaa or 111111111). |
   12052935 |Product attribute value names must follow these formatting rules: it cannot contain HTML escape characters (e.g.,  ), emojis, or ASCII control characters (e.g., \u007F). It also cannot consist solely of symbols (e.g., //// or !@#$$$&), nor can it have more than 9 consecutive repeated characters (e.g., aaaaaaaaa or 111111111). |
   12052994 |seller is not toko seller |
