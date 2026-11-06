# Partner Global — Manage Product 接口目录

Partner Platform for **Global（全球区，非 US/EU）** 菜单：**Product > Manage Product**。

本 skill 覆盖 **24** 个 `bg.local.*` / `temu.local.*` 商品管理接口（`type` 与 US/EU 版对齐）。调用经 `temu_global_proxy`（`POST /temu/proxy`），默认 **`site=global`**、**`tokenPurpose=product-inventory`**。

> **说明**：`sub_menu_code` 暂引用 US Partner 文档索引（全球区请在 [partner-global.temu.com](https://partner-global.temu.com/documentation) 按 `type` 核对并更新）。欧洲站请用 **`linkfox-temu-manage-product-eu`**（`site=eu`）；美国站请用 **`linkfox-temu-manage-product-us`**（`site=us`）。

目录与单接口文档中的两组编号存在差异：`bg.local.goods.list.query` 的目录编号为 `d2a836cf1711473ba1f83597a1b52fb0`，单接口文档编号为 `7b50a3af47824c4482c7238c6e11aedc`；`temu.local.goods.list.retrieve` 的目录编号为 `7b50a3af47824c4482c7238c6e11aedc`，单接口文档编号为 `9775b60761c54bf38022c77c717183a9`。这些编号仅用于文档定位，不用于选择操作，也不代表 Global 地址已经验证有效。按 `type` 识别接口，字段定义见对应单接口文档；文档地址须在 Global Partner 后台核对。

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| [`d2a836cf1711473ba1f83597a1b52fb0`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=d2a836cf1711473ba1f83597a1b52fb0) | `bg.local.goods.list.query` | `global_manage_list_query.py` | [apis/bg-local-goods-list-query.md](./apis/bg-local-goods-list-query.md) |
| [`7b50a3af47824c4482c7238c6e11aedc`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=7b50a3af47824c4482c7238c6e11aedc) | `temu.local.goods.list.retrieve` | `global_manage_goods_list_retrieve.py` | [apis/temu-local-goods-list-retrieve.md](./apis/temu-local-goods-list-retrieve.md) |
| [`9ebbd5d269014322ad4a6c123b1dfdae`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=9ebbd5d269014322ad4a6c123b1dfdae) | `bg.local.goods.detail.query` | `global_manage_detail_query.py` | [apis/bg-local-goods-detail-query.md](./apis/bg-local-goods-detail-query.md) |
| [`87a0d398417049bfbeb5b190f68a22b2`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=87a0d398417049bfbeb5b190f68a22b2) | `bg.local.goods.sku.list.query` | `global_manage_sku_list_query.py` | [apis/bg-local-goods-sku-list-query.md](./apis/bg-local-goods-sku-list-query.md) |
| [`9775b60761c54bf38022c77c717183a9`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=9775b60761c54bf38022c77c717183a9) | `temu.local.sku.list.retrieve` | `global_manage_sku_list_retrieve.py` | [apis/temu-local-sku-list-retrieve.md](./apis/temu-local-sku-list-retrieve.md) |
| [`1d70452c1eba40a2b2382fb08833ae4e`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=1d70452c1eba40a2b2382fb08833ae4e) | `bg.local.goods.publish.status.get` | `global_manage_publish_status_get.py` | [apis/bg-local-goods-publish-status-get.md](./apis/bg-local-goods-publish-status-get.md) |
| [`f14a3f28b654441b80f90e76a0a77c6e`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=f14a3f28b654441b80f90e76a0a77c6e) | `temu.local.goods.sku.stock.query` | `global_manage_sku_stock_query.py` | [apis/temu-local-goods-sku-stock-query.md](./apis/temu-local-goods-sku-stock-query.md) |
| [`429ffa60b265451d9421cd5a2004eeef`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=429ffa60b265451d9421cd5a2004eeef) | `bg.local.goods.stock.edit` | `global_manage_stock_edit.py` | [apis/bg-local-goods-stock-edit.md](./apis/bg-local-goods-stock-edit.md) |
| [`6de74ed5afe74f89966b3ff23dfd7498`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=6de74ed5afe74f89966b3ff23dfd7498) | `bg.local.goods.partial.update` | `global_manage_partial_update.py` | [apis/bg-local-goods-partial-update.md](./apis/bg-local-goods-partial-update.md) |
| [`b05f4b7598fb4dc7ac47c864aa5d5fc4`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=b05f4b7598fb4dc7ac47c864aa5d5fc4) | `bg.local.goods.update` | `global_manage_goods_update.py` | [apis/bg-local-goods-update.md](./apis/bg-local-goods-update.md) |
| [`97853cce1f5140e0aa302b5e530a8c99`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=97853cce1f5140e0aa302b5e530a8c99) | `temu.local.goods.delete` | `global_manage_goods_delete.py` | [apis/temu-local-goods-delete.md](./apis/temu-local-goods-delete.md) |
| [`1094942488d844acaf9d7a3f2c097acd`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=1094942488d844acaf9d7a3f2c097acd) | `temu.local.goods.spec.info.get` | `global_manage_spec_info_get.py` | [apis/temu-local-goods-spec-info-get.md](./apis/temu-local-goods-spec-info-get.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.category.check` | `global_manage_category_check.py` | [apis/bg-local-goods-category-check.md](./apis/bg-local-goods-category-check.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.property.get` | `global_manage_property_get.py` | [apis/bg-local-goods-property-get.md](./apis/bg-local-goods-property-get.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.property.relations` | `global_manage_property_relations.py` | [apis/bg-local-goods-property-relations.md](./apis/bg-local-goods-property-relations.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.property.relations.level.template` | `global_manage_property_relations_level_template.py` | [apis/bg-local-goods-property-relations-level-template.md](./apis/bg-local-goods-property-relations-level-template.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.property.relations.template` | `global_manage_property_relations_template.py` | [apis/bg-local-goods-property-relations-template.md](./apis/bg-local-goods-property-relations-template.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.out.sn.set` | `global_manage_out_sn_set.py` | [apis/bg-local-goods-out-sn-set.md](./apis/bg-local-goods-out-sn-set.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.sku.out.sn.set` | `global_manage_sku_out_sn_set.py` | [apis/bg-local-goods-sku-out-sn-set.md](./apis/bg-local-goods-sku-out-sn-set.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.compliance.goods.list.query` | `global_manage_compliance_list_query.py` | [apis/bg-local-compliance-goods-list-query.md](./apis/bg-local-compliance-goods-list-query.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.compliance.edit` | `global_manage_compliance_edit.py` | [apis/bg-local-goods-compliance-edit.md](./apis/bg-local-goods-compliance-edit.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.sale.status.set` | `global_manage_sale_status_set.py` | [apis/bg-local-goods-sale-status-set.md](./apis/bg-local-goods-sale-status-set.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `temu.local.goods.pre.sale.status.edit` | `global_manage_pre_sale_status_edit.py` | [apis/temu-local-goods-pre-sale-status-edit.md](./apis/temu-local-goods-pre-sale-status-edit.md) |
| [`2a343c65a03d42d380e9ad835aa7b54b`](https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b) | `bg.local.goods.videocoverimage.get` | `global_manage_videocoverimage_get.py` | [apis/bg-local-goods-videocoverimage-get.md](./apis/bg-local-goods-videocoverimage-get.md) |

## 上游 OpenAPI（Global）

`POST` https://openapi-b-global.temu.com/openapi/router（经 LinkFox 网关 `site=global` 转发）

## 与相关 skill 的关系

| 能力 | skill |
|------|--------|
| 商品管理（本 skill，`site=global`） | **`linkfox-temu-manage-product-global`** |
| 美国站商品管理 | `linkfox-temu-manage-product-us` |
| 欧洲站商品管理 | `linkfox-temu-manage-product-eu` |
| 发品 V2 add | `linkfox-temu-add-product-us`（调用时 `site=global`） |
| 价格 | 全球区使用 `linkfox-temu-price-global`；如复用 `linkfox-temu-price-us`，须先确认其支持范围并显式传 `site=global`。 |
| 促销 | `linkfox-temu-promotion-global` |
| 电商合规 | `linkfox-temu-compliance-global` |
| 网关、Token | 本 skill `scripts/` |
