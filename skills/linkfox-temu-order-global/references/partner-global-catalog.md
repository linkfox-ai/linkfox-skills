# Partner Global — Order 接口目录

Partner Platform for **Global（全球区，非 US/EU）** 菜单：**Order / 订单管理**（`menu_code=dbd3d395963a408984b8ae7dbc5f64f9`）。

本 skill 覆盖 **9** 个订单 `type`。调用经 `temu_global_proxy`（`POST /temu/proxy`），默认 **`site=global`**、**`tokenPurpose=order-shipping`**。

> **说明**：各接口 `sub_menu_code` 请在 [partner-global.temu.com](https://partner-global.temu.com/documentation) 按 `type` 核对。美国站请用 **`linkfox-temu-order-us`**（`site=us`）；欧洲站请用 **`linkfox-temu-order-eu`**（`site=eu`）。

## 已接入（9）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `bg.order.list.v2.get` | `global_order_list_v2_get.py` | [apis/bg-order-list-v2-get.md](./apis/bg-order-list-v2-get.md) |
| — | `bg.order.detail.v2.get` | `global_order_detail_v2_get.py` | [apis/bg-order-detail-v2-get.md](./apis/bg-order-detail-v2-get.md) |
| — | `bg.order.shippinginfo.v2.get` | `global_order_shippinginfo_v2_get.py` | [apis/bg-order-shippinginfo-v2-get.md](./apis/bg-order-shippinginfo-v2-get.md) |
| — | `bg.order.decryptshippinginfo.get` | `global_order_decryptshippinginfo_get.py` | [apis/bg-order-decryptshippinginfo-get.md](./apis/bg-order-decryptshippinginfo-get.md) |
| — | `bg.order.amount.query` | `global_order_amount_query.py` | [apis/bg-order-amount-query.md](./apis/bg-order-amount-query.md) |
| — | `bg.order.combinedshipment.list.get` | `global_order_combinedshipment_list_get.py` | [apis/bg-order-combinedshipment-list-get.md](./apis/bg-order-combinedshipment-list-get.md) |
| — | `bg.order.customization.get` | `global_order_customization_get.py` | [apis/bg-order-customization-get.md](./apis/bg-order-customization-get.md) |
| — | `temu.local.order.verification.upload` | `global_order_verification_upload.py` | [apis/temu-local-order-verification-upload.md](./apis/temu-local-order-verification-upload.md) |
| `2ae82004ae7644c5a072e9dc1e33eaec` | `temu.order.amount.v2.query` | `global_order_amount_v2_query.py` | [apis/temu-order-amount-v2-query.md](./apis/temu-order-amount-v2-query.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.order.list.v2.get` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.detail.v2.get` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.shippinginfo.v2.get` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.decryptshippinginfo.get` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.amount.query` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.combinedshipment.list.get` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.customization.get` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `temu.local.order.verification.upload` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `temu.order.amount.v2.query` | https://partner-global.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9&sub_menu_code=2ae82004ae7644c5a072e9dc1e33eaec |
## 上游 OpenAPI（Global）

`POST` https://openapi-b-global.temu.com/openapi/router（经 LinkFox 网关 `site=global` 转发）

## 通用脚本

| 脚本 | 说明 |
|------|------|
| `temu_global_proxy.py` | 任意 `type` + `params` |
| `temu_global_file_download.py` | 加签文件下载 |

## 与其他 Temu skill 的关系

| 能力 | skill |
|------|--------|
| 订单查询（本 skill，`site=global`） | **`linkfox-temu-order-global`** |
| 美国站订单 | `linkfox-temu-order-us` |
| 欧洲站订单 | `linkfox-temu-order-eu` |
| 商品管理 | `linkfox-temu-manage-product-global` |
| 价格/供货价 | `linkfox-temu-price-global` |
| 取消订单 | `linkfox-temu-cancel-order-global` |
| 履约/发货 | `linkfox-temu-fulfillment-global` |
| 网关、Token | 本 skill `scripts/` |

## Token 说明

订单类接口建议使用 **`tokenPurpose=order-shipping`**。详见 [access-token.md](./access-token.md)。
