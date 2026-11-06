# Partner US — Price 接口目录

Partner Platform for US 菜单：**Product**（`menu_code=fb16b05f7a904765aac4af3a24b87d4a`）下与**价格/供货价**相关的子菜单。

本技能经 `temu_us_proxy`（`POST /temu/proxy`） 调用，`type` 写在 Body。完整参数见 [apis/README.md](./apis/README.md)。

> **接口边界**：当前定义下列四项价格操作。其他操作需取得 Partner 文档中的 `type`、`sub_menu_code`、URL、完整参数与响应定义后才能调用，不能仅凭通用代理入口推断支持。

## 已接入（4）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| 待提供 | `temu.local.goods.baseprice.recommend` | `us_price_baseprice_recommend.py` | [apis/temu-local-goods-baseprice-recommend.md](./apis/temu-local-goods-baseprice-recommend.md) |
| 待提供 | `temu.local.goods.recommendedprice.query` | `us_price_recommendedprice_query.py` | [apis/temu-local-goods-recommendedprice-query.md](./apis/temu-local-goods-recommendedprice-query.md) |
| 待提供 | `bg.local.goods.priceorder.query` | `us_price_priceorder_query.py` | [apis/bg-local-goods-priceorder-query.md](./apis/bg-local-goods-priceorder-query.md) |
| 待提供 | `bg.local.goods.priceorder.change.sku.price` | `us_price_priceorder_change_sku_price.py` | [apis/bg-local-goods-priceorder-change-sku-price.md](./apis/bg-local-goods-priceorder-change-sku-price.md) |

Partner 文档入口：

| type | URL |
|------|-----|
| `temu.local.goods.baseprice.recommend` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a（`sub_menu_code` 待补） |
| `temu.local.goods.recommendedprice.query` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a（`sub_menu_code` 待补） |
| `bg.local.goods.priceorder.query` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a（`sub_menu_code` 待补） |
| `bg.local.goods.priceorder.change.sku.price` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a（`sub_menu_code` 待补） |

`sub_menu_code` 以 Partner 后台为准，未知值不补造。

## 与发品价格列表区分

`temu.goods.price.list.get` 使用 `productSkuIds`，属于 `linkfox-temu-add-product-us`；本技能定价单与推荐供货价不能替代该接口。
