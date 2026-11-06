# Temu 全球站价格接口目录

Partner Platform for **Global（全球区，非 US/EU）** 菜单：**Product** 下与**价格/供货价**相关的接口。

本 skill 覆盖 **5** 个价格/供货价 `type`。调用经 `temu_global_proxy`（`POST /temu/proxy`），默认 **`site=global`**、**`tokenPurpose=product-inventory`**。

> **说明**：`sub_menu_code` 请在 [partner-global.temu.com](https://partner-global.temu.com/documentation) 按 `type` 核对。美国站请用 **`linkfox-temu-price-us`**（`site=us`）；欧洲站请用 **`linkfox-temu-price-eu`**（`site=eu`）。

## 已接入（5）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `temu.local.goods.baseprice.recommend` | `global_price_baseprice_recommend.py` | [apis/temu-local-goods-baseprice-recommend.md](./apis/temu-local-goods-baseprice-recommend.md) |
| — | `temu.local.goods.recommendedprice.query` | `global_price_recommendedprice_query.py` | [apis/temu-local-goods-recommendedprice-query.md](./apis/temu-local-goods-recommendedprice-query.md) |
| — | `bg.local.goods.priceorder.query` | `global_price_priceorder_query.py` | [apis/bg-local-goods-priceorder-query.md](./apis/bg-local-goods-priceorder-query.md) |
| — | `bg.local.goods.priceorder.change.sku.price` | `global_price_priceorder_change_sku_price.py` | [apis/bg-local-goods-priceorder-change-sku-price.md](./apis/bg-local-goods-priceorder-change-sku-price.md) |
| `a9bd154c38384f2c99e57c2ebe271299` | `bg.local.goods.sku.list.price.query` | `global_price_sku_list_price_query.py` | [apis/bg-local-goods-sku-list-price-query.md](./apis/bg-local-goods-sku-list-price-query.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `temu.local.goods.baseprice.recommend` | https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a |
| `temu.local.goods.recommendedprice.query` | https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a |
| `bg.local.goods.priceorder.query` | https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a |
| `bg.local.goods.priceorder.change.sku.price` | https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a |
| `bg.local.goods.sku.list.price.query` | https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=a9bd154c38384f2c99e57c2ebe271299 |

## 上游 OpenAPI（Global）

`POST` https://openapi-b-global.temu.com/openapi/router（经 LinkFox 网关 `site=global` 转发）

## 与 add-product / manage-product 区分

| skill | type | 说明 |
|-------|------|------|
| **本 skill** | `bg.local.goods.priceorder.*` / `temu.local.goods.*price*` / `bg.local.goods.sku.list.price.query` | 定价单、推荐价、SKU 供货价、批量改价 |
| `linkfox-temu-manage-product-global` | 商品管理域 | `site=global` |
| `linkfox-temu-add-product-us` | `temu.goods.price.list.get` | 发品侧（Global 调用时 `site=global`） |

## 其他相关场景

以下场景转交对应技能，仅在用户确实需要相应区域的业务时使用，不作为全球站价格管理的默认步骤。

| 场景 | 技能 |
|---|---|
| 全球站订单查询、发货、物流 | `linkfox-temu-order-global` |
| 美国站买家或卖家取消订单 | `linkfox-temu-cancel-order-us` |
| 美国站履约、发货及自发货 | `linkfox-temu-fulfillment-us` |
| 美国站发品、类目、V2 add | `linkfox-temu-add-product-us` |
