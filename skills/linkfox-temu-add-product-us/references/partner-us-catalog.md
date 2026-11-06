# Partner US — 商品（Product）API 目录

**平台**：Partner Platform for US（`site=us`）  
**菜单**：`Product`（`menu_code=fb16b05f7a904765aac4af3a24b87d4a`）  
**网关**：`POST https://tool-gateway.linkfox.com/temu/proxy`

---

## A. Add Products — Recommended V2（4 个）

菜单路径：**Product > Add Products > Recommended V2 Interfaces**

| sub_menu_code | type | 脚本 | 说明 |
|---------------|------|------|------|
| `91657460a9be4a609df2eef01bc6deef` | `temu.local.goods.v2.add` | `us_goods_add.py` | 发布商品 V2 |
| `1ecd9ad752a14d5e9f5297edfd6c8848` | `temu.local.product.attributes.get` | `us_goods_attrs.py` | 类目属性（US V2） |
| `d23bfec96065492ebe8290c6fe867a19` | `temu.local.product.variation.get` | `us_goods_variation.py` | 商品规格 Variation |
| `37d470d8c6e149f78953311aa0b0296d` | `temu.local.goods.image.v2.upload` | `us_goods_image_upload.py` | 图片上传 V2 |

文档：[product-publish-apis.md](./product-publish-apis.md)、[category-spec-apis.md](./category-spec-apis.md) 中的 V2 属性与规格接口

**推荐发品顺序**：`attributes.get` → `variation.get` → `image.v2.upload` → `goods.v2.add`

---

## B. 标准商品接口（15 个）

同一 `menu_code` 下商品能力扩展接口（`sub_menu_code` 与 Partner 文档页一一对应）。

### 商品查询

| sub_menu_code | type | 脚本 | 文档 |
|---------------|------|------|------|
| `c313f7e3983f407d82d0f7cd88ab5c62` | `temu.goods.list.get` | `us_goods_list.py` | [product-query-apis.md](./product-query-apis.md) |
| `7ce116fe6b87443ba2a5320b25bf2b20` | `temu.goods.detail.get` | `us_goods_detail.py` | [product-query-apis.md](./product-query-apis.md) |

### 商品编辑

| sub_menu_code | type | 脚本 | 文档 |
|---------------|------|------|------|
| `e93835a33b7a40ce8769fdf75561aff4` | `temu.goods.update` | `us_goods_update.py` | [product-edit-apis.md](./product-edit-apis.md) |
| `93fecd4d21fd441a8abcfc1497fa085e` | `temu.goods.edit.property` | `us_goods_edit_property.py` | [product-edit-apis.md](./product-edit-apis.md) |
| `fc3de2c8546a496d8a5be8d36953e1bd` | `temu.goods.edit.sensitive.attr` | `us_goods_edit_sensitive.py` | [product-edit-apis.md](./product-edit-apis.md) |
| `a8f8f3dca5ac4e2c8b9e7bc9d64704c8` | `temu.goods.migrate` | `us_goods_migrate.py` | [product-edit-apis.md](./product-edit-apis.md) |

### 类目、属性、规格、品牌

| sub_menu_code | type | 脚本 | 文档 |
|---------------|------|------|------|
| `7f9ded1bfce7485798c3862467d5c30e` | `bg.goods.cats.get` | `us_goods_cats.py` | [category-spec-apis.md](./category-spec-apis.md) |
| `2b42b46f51c348b69bf8f69c5397279e` | `bg.goods.attrs.get` | `us_goods_attrs_bg.py` | [category-spec-apis.md](./category-spec-apis.md) |
| `8a6a6e8b14814d518fe8f004f35b2192` | `bg.glo.goods.parentspec.get` | `us_goods_parent_spec.py` | [category-spec-apis.md](./category-spec-apis.md) |
| `f8065a07b2d6441f9f33c2d808dcc593` | `bg.glo.goods.brand.get` | `us_goods_brand.py` | [category-spec-apis.md](./category-spec-apis.md) |
| `3f15de61844e4a989d042767a385d8f5` | `bg.goods.category.mapping` | `us_goods_category_mapping.py` | [category-spec-apis.md](./category-spec-apis.md) |

### 库存、价格、发品（非 V2）

| sub_menu_code | type | 脚本 | 文档 |
|---------------|------|------|------|
| `d72b66d07b1f499bbd80720367e58e1f` | `bg.btg.goods.stock.quantity.get` | `us_goods_stock_get.py` | [stock-price-apis.md](./stock-price-apis.md) |
| `e84f651da04f4fedb85d37e375a4e2d8` | `bg.btg.goods.stock.quantity.update` | `us_goods_stock_update.py` | [stock-price-apis.md](./stock-price-apis.md) |
| `a084faecbad64d7f93c485378b5bd9bf` | `temu.goods.price.list.get` | `us_goods_price_list.py` | [stock-price-apis.md](./stock-price-apis.md) |
| `1b99296745854ae08d39a7bbe1e4f7a8` | `temu.goods.add` | `us_goods_add_legacy.py` | [product-publish-apis.md](./product-publish-apis.md) |

---

## 站点与鉴权

| 项 | 值 |
|----|-----|
| 默认 `site` | `us` |
| 默认 `managementType` | `semi-managed` |
| 默认 `tokenPurpose` | `product-inventory` |
| LinkFox | `LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token` |
| Temu | Body `accessToken` 或 `storeKey` |

授权步骤见 `references/access-token.md`。

---

## 未封装接口

`scripts/temu_us_proxy.py` 透传任意 `type`；加签文件下载用 `temu_us_file_download.py` → `/temu/fileDownload`。

---

## 参数文档索引

| 文档 | 内容 |
|------|------|
| [api.md](./api.md) | 网关、鉴权、通用响应 |
| [product-query-apis.md](./product-query-apis.md) | 列表、详情 |
| [product-edit-apis.md](./product-edit-apis.md) | 更新、改属性、敏感品、迁移 |
| [product-publish-apis.md](./product-publish-apis.md) | V2 发品、图片、legacy 发品 |
| [category-spec-apis.md](./category-spec-apis.md) | V2 属性/规格 + 类目/品牌/映射 |
| [stock-price-apis.md](./stock-price-apis.md) | 库存、供货价 |
