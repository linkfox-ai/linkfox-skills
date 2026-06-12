---
name: linkfox-temu-add-product-us
description: Temu 美国站发品（Add Product）API，经 LinkFox 网关转发 Partner US 商品接口：V2发品(temu.local.goods.v2.add)、类目属性、规格、图片上传、商品列表/详情/编辑、类目映射、SKU库存、供货价等。当用户提到 Temu 美国站发品、Temu US Add Product、goods.list、goods.detail、temu.local.goods.v2.add、商品类目映射、SKU库存、供货价、Partner US 发品文档 时触发。订单/物流请用其他 Temu skill。
---

# Temu 美国站发品 API（Partner US）

本 skill（`linkfox-temu-add-product-us`）覆盖 Partner Platform for US **Product** 菜单（`menu_code=fb16b05f7a904765aac4af3a24b87d4a`）下 **19 个商品接口**：**4 个 V2 推荐发品** + **15 个标准商品 API**（查询、编辑、类目、库存、价格等）。

**网关（本 skill 内置）**：

| 能力 | 方法 | 网关路径 |
|------|------|----------|
| 商品 OpenAPI（全部 `us_goods_*`、`temu_us_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载（`temu_us_file_download`） | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

商品 `type` 写在 Body，**不是** URL 路径。

> **不是订单 skill**：订单、发货、物流见 `linkfox-temu-order-us` 或其它履约类 skill。

## API Usage

完整入参/出参见 `references/`（已内联 Partner 文档要点，无需外链）：

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、通用响应、错误码 |
| [partner-us-catalog.md](./references/partner-us-catalog.md) | 全部接口与 `sub_menu_code` 对照 |
| [product-query-apis.md](./references/product-query-apis.md) | 列表、详情 |
| [product-edit-apis.md](./references/product-edit-apis.md) | 更新、改属性、敏感品、迁移 |
| [product-publish-apis.md](./references/product-publish-apis.md) | V2 发品、图片、legacy 发品 |
| [category-spec-apis.md](./references/category-spec-apis.md) | 类目/属性/规格/品牌/映射 |
| [stock-price-apis.md](./references/stock-price-apis.md) | 库存、供货价 |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `us` | Partner US |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose（storeKey） | `product-inventory` | 酷鸟卖家助手 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`

## Scripts

### V2 推荐发品

| 脚本 | type |
|------|------|
| `us_goods_attrs.py` | `temu.local.product.attributes.get` |
| `us_goods_variation.py` | `temu.local.product.variation.get` |
| `us_goods_image_upload.py` | `temu.local.goods.image.v2.upload` |
| `us_goods_add.py` | `temu.local.goods.v2.add` |

### 查询 / 编辑 / 类目 / 库存

| 脚本 | type |
|------|------|
| `us_goods_list.py` | `temu.goods.list.get` |
| `us_goods_detail.py` | `temu.goods.detail.get` |
| `us_goods_update.py` | `temu.goods.update` |
| `us_goods_edit_property.py` | `temu.goods.edit.property` |
| `us_goods_edit_sensitive.py` | `temu.goods.edit.sensitive.attr` |
| `us_goods_migrate.py` | `temu.goods.migrate` |
| `us_goods_cats.py` | `bg.goods.cats.get` |
| `us_goods_attrs_bg.py` | `bg.goods.attrs.get` |
| `us_goods_parent_spec.py` | `bg.glo.goods.parentspec.get` |
| `us_goods_brand.py` | `bg.glo.goods.brand.get` |
| `us_goods_category_mapping.py` | `bg.goods.category.mapping` |
| `us_goods_stock_get.py` | `bg.btg.goods.stock.quantity.get` |
| `us_goods_stock_update.py` | `bg.btg.goods.stock.quantity.update` |
| `us_goods_price_list.py` | `temu.goods.price.list.get` |
| `us_goods_add_legacy.py` | `temu.goods.add` |
| `temu_us_proxy.py` | 任意 `type` |
| `temu_us_file_download.py` | 加签文件下载 |

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 商品列表
python scripts/us_goods_list.py '{"accessToken":"TOKEN","page":1,"pageSize":20}'

# 类目映射
python scripts/us_goods_category_mapping.py '{
  "accessToken":"TOKEN",
  "goodsName":"测试商品",
  "goodsNameEn":"Test Product"
}'

# V2 发品流程
python scripts/us_goods_attrs.py '{"accessToken":"TOKEN","params":{"catId":12345}}'
python scripts/us_goods_image_upload.py '{"accessToken":"TOKEN","params":{"image":"<BASE64>"}}'
python scripts/us_goods_add.py '{"accessToken":"TOKEN","params":{"..."}}'
```

**Feedback：** `skillName`：`linkfox-temu-add-product-us`

## 网关与授权脚本

| 脚本 | 说明 |
|------|------|
| `check_linkfox_token.py` | 校验 LinkFox 用户 Token |
| `temu_token_guide.py` | Temu accessToken 后台授权步骤 |
| `save_temu_access_token.py` | 保存 accessToken 到本地 |
| `list_temu_access_tokens.py` | 列出已保存 token |
| `get_temu_access_token.py` | 读取已保存 token |
| `temu_proxy.py` | 通用网关转发（多 site） |
| `temu_file_download.py` | 加签文件下载（多 site） |

授权说明：[references/access-token.md](./references/access-token.md)

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/check_linkfox_token.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `get_temu_access_token.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_file_download.py`, `temu_proxy.py`, `temu_token_guide.py`, `temu_us_file_download.py`, `temu_us_proxy.py`, `us_goods_add.py`, `us_goods_add_legacy.py`, `us_goods_attrs.py`, `us_goods_attrs_bg.py`, `us_goods_brand.py`, `us_goods_category_mapping.py`, `us_goods_cats.py`, `us_goods_detail.py`, `us_goods_edit_property.py`, `us_goods_edit_sensitive.py`, `us_goods_image_upload.py`, `us_goods_list.py`, `us_goods_migrate.py`, `us_goods_parent_spec.py`, `us_goods_price_list.py`, `us_goods_stock_get.py`, `us_goods_stock_update.py`, `us_goods_update.py`, `us_goods_variation.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
