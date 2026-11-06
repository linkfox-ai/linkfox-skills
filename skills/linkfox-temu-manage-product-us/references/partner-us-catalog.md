# Partner US — Manage Product 接口目录

Partner Platform for US 菜单：**Product > Manage Product**（`menu_code=fb16b05f7a904765aac4af3a24b87d4a`）。

本 skill 覆盖 **24** 个 `bg.local.*` / `temu.local.*` 商品管理接口。调用经本 skill `temu_us_proxy`（`POST /temu/proxy`），`type` 写在 Body。

> **文档链接**：Partner 官方 URL 见下表；**内联参数**见 [apis/README.md](./apis/README.md)（每个 `type` 一个 `.md` 文件）。

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| `d2a836cf1711473ba1f83597a1b52fb0` | `bg.local.goods.list.query` | `us_manage_list_query.py` | [apis/bg-local-goods-list-query.md](./apis/bg-local-goods-list-query.md) |
| `7b50a3af47824c4482c7238c6e11aedc` | `temu.local.goods.list.retrieve` | `us_manage_goods_list_retrieve.py` | [apis/temu-local-goods-list-retrieve.md](./apis/temu-local-goods-list-retrieve.md) |
| `9ebbd5d269014322ad4a6c123b1dfdae` | `bg.local.goods.detail.query` | `us_manage_detail_query.py` | [apis/bg-local-goods-detail-query.md](./apis/bg-local-goods-detail-query.md) |
| `87a0d398417049bfbeb5b190f68a22b2` | `bg.local.goods.sku.list.query` | `us_manage_sku_list_query.py` | [apis/bg-local-goods-sku-list-query.md](./apis/bg-local-goods-sku-list-query.md) |
| `9775b60761c54bf38022c77c717183a9` | `temu.local.sku.list.retrieve` | `us_manage_sku_list_retrieve.py` | [apis/temu-local-sku-list-retrieve.md](./apis/temu-local-sku-list-retrieve.md) |
| `1d70452c1eba40a2b2382fb08833ae4e` | `bg.local.goods.publish.status.get` | `us_manage_publish_status_get.py` | [apis/bg-local-goods-publish-status-get.md](./apis/bg-local-goods-publish-status-get.md) |
| `f14a3f28b654441b80f90e76a0a77c6e` | `temu.local.goods.sku.stock.query` | `us_manage_sku_stock_query.py` | [apis/temu-local-goods-sku-stock-query.md](./apis/temu-local-goods-sku-stock-query.md) |
| `429ffa60b265451d9421cd5a2004eeef` | `bg.local.goods.stock.edit` | `us_manage_stock_edit.py` | [apis/bg-local-goods-stock-edit.md](./apis/bg-local-goods-stock-edit.md) |
| `6de74ed5afe74f89966b3ff23dfd7498` | `bg.local.goods.partial.update` | `us_manage_partial_update.py` | [apis/bg-local-goods-partial-update.md](./apis/bg-local-goods-partial-update.md) |
| `b05f4b7598fb4dc7ac47c864aa5d5fc4` | `bg.local.goods.update` | `us_manage_goods_update.py` | [apis/bg-local-goods-update.md](./apis/bg-local-goods-update.md) |
| `97853cce1f5140e0aa302b5e530a8c99` | `temu.local.goods.delete` | `us_manage_goods_delete.py` | [apis/temu-local-goods-delete.md](./apis/temu-local-goods-delete.md) |
| `1094942488d844acaf9d7a3f2c097acd` | `temu.local.goods.spec.info.get` | `us_manage_spec_info_get.py` | [apis/temu-local-goods-spec-info-get.md](./apis/temu-local-goods-spec-info-get.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.category.check` | `us_manage_category_check.py` | [apis/bg-local-goods-category-check.md](./apis/bg-local-goods-category-check.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.property.get` | `us_manage_property_get.py` | [apis/bg-local-goods-property-get.md](./apis/bg-local-goods-property-get.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.property.relations` | `us_manage_property_relations.py` | [apis/bg-local-goods-property-relations.md](./apis/bg-local-goods-property-relations.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.property.relations.level.template` | `us_manage_property_relations_level_template.py` | [apis/bg-local-goods-property-relations-level-template.md](./apis/bg-local-goods-property-relations-level-template.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.property.relations.template` | `us_manage_property_relations_template.py` | [apis/bg-local-goods-property-relations-template.md](./apis/bg-local-goods-property-relations-template.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.out.sn.set` | `us_manage_out_sn_set.py` | [apis/bg-local-goods-out-sn-set.md](./apis/bg-local-goods-out-sn-set.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.sku.out.sn.set` | `us_manage_sku_out_sn_set.py` | [apis/bg-local-goods-sku-out-sn-set.md](./apis/bg-local-goods-sku-out-sn-set.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.compliance.goods.list.query` | `us_manage_compliance_list_query.py` | [apis/bg-local-compliance-goods-list-query.md](./apis/bg-local-compliance-goods-list-query.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.compliance.edit` | `us_manage_compliance_edit.py` | [apis/bg-local-goods-compliance-edit.md](./apis/bg-local-goods-compliance-edit.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.sale.status.set` | `us_manage_sale_status_set.py` | [apis/bg-local-goods-sale-status-set.md](./apis/bg-local-goods-sale-status-set.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `temu.local.goods.pre.sale.status.edit` | `us_manage_pre_sale_status_edit.py` | [apis/temu-local-goods-pre-sale-status-edit.md](./apis/temu-local-goods-pre-sale-status-edit.md) |
| `2a343c65a03d42d380e9ad835aa7b54b` | `bg.local.goods.videocoverimage.get` | `us_manage_videocoverimage_get.py` | [apis/bg-local-goods-videocoverimage-get.md](./apis/bg-local-goods-videocoverimage-get.md) |

## 官方文档 URL（按 type）

文档基址：`https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=<code>`

| type | 文档 |
|------|------|
| `bg.local.goods.partial.update` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=6de74ed5afe74f89966b3ff23dfd7498 |
| `bg.local.goods.update` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=b05f4b7598fb4dc7ac47c864aa5d5fc4 |
| `temu.local.goods.sku.stock.query` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=f14a3f28b654441b80f90e76a0a77c6e |
| `bg.local.goods.stock.edit` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=429ffa60b265451d9421cd5a2004eeef |
| `temu.local.goods.delete` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=97853cce1f5140e0aa302b5e530a8c99 |
| `bg.local.goods.publish.status.get` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=1d70452c1eba40a2b2382fb08833ae4e |
| `bg.local.goods.detail.query` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=9ebbd5d269014322ad4a6c123b1dfdae |
| `bg.local.goods.sku.list.query` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=87a0d398417049bfbeb5b190f68a22b2 |
| `temu.local.sku.list.retrieve` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=9775b60761c54bf38022c77c717183a9 |
| `bg.local.goods.list.query` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=d2a836cf1711473ba1f83597a1b52fb0 |
| `temu.local.goods.list.retrieve` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=7b50a3af47824c4482c7238c6e11aedc |
| `temu.local.goods.spec.info.get` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=1094942488d844acaf9d7a3f2c097acd |
| `bg.local.goods.category.check` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b |
| `bg.local.goods.property.get` | 同上 |
| `bg.local.goods.property.relations` | 同上 |
| `bg.local.goods.property.relations.level.template` | 同上 |
| `bg.local.goods.property.relations.template` | 同上 |
| `bg.local.goods.out.sn.set` | 同上 |
| `bg.local.goods.sku.out.sn.set` | 同上 |
| `bg.local.compliance.goods.list.query` | 同上 |
| `bg.local.goods.compliance.edit` | 同上 |
| `bg.local.goods.sale.status.set` | 同上 |
| `temu.local.goods.pre.sale.status.edit` | 同上 |
| `bg.local.goods.videocoverimage.get` | 同上 |

> **说明**：属性/合规/上下架等 11 个接口指向同一 `sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b`（Partner 后台可能为同一文档分区下的多 `type`）。以 **`type` 字段** 区分调用，勿仅依赖 `sub_menu_code`。

全球站商品管理使用 `linkfox-temu-manage-product-global`。

## 与 `linkfox-temu-add-product-us` 的关系

| 能力 | skill |
|------|--------|
| V2 发品、类目映射、半托 `temu.goods.*` / `bg.goods.*` | `linkfox-temu-add-product-us` |
| 本 skill：`bg.local.*` / `temu.local.*` 商品管理（查、改、删、库存、合规） | `linkfox-temu-manage-product-us` |
| 网关、Token | 本 skill `scripts/`（`temu_us_proxy`、`check_linkfox_token` 等） |
