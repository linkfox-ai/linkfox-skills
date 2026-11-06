# Partner EU — Order 接口目录

Partner Platform for EU 菜单：**Order**（`menu_code=dbd3d395963a408984b8ae7dbc5f64f9`）。

文档根 `menu_code`（浏览器地址栏常见）：`7289390cfd724be4a196f11ebe45a896`。

本 skill 覆盖与 US 版对齐的 **10** 个订单 `type`。调用经 `temu_eu_proxy`（`POST /temu/proxy`），默认 **`site=eu`**、**`tokenPurpose=order-shipping`**。

> EU 菜单 HTML 导出中 **Order** 子项未展开，各接口 `sub_menu_code` 请在 [partner-eu.temu.com](https://partner-eu.temu.com/documentation) 按 `type` 打开后补全。

## 已接入（10）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `bg.order.list.v2.get` | `eu_order_list_v2_get.py` | [apis/bg-order-list-v2-get.md](./apis/bg-order-list-v2-get.md) |
| — | `bg.order.detail.v2.get` | `eu_order_detail_v2_get.py` | [apis/bg-order-detail-v2-get.md](./apis/bg-order-detail-v2-get.md) |
| — | `bg.order.shippinginfo.v2.get` | `eu_order_shippinginfo_v2_get.py` | [apis/bg-order-shippinginfo-v2-get.md](./apis/bg-order-shippinginfo-v2-get.md) |
| — | `bg.order.decryptshippinginfo.get` | `eu_order_decryptshippinginfo_get.py` | [apis/bg-order-decryptshippinginfo-get.md](./apis/bg-order-decryptshippinginfo-get.md) |
| — | `bg.order.amount.query` | `eu_order_amount_query.py` | [apis/bg-order-amount-query.md](./apis/bg-order-amount-query.md) |
| `91661bf0642440ddbd462b25fa96edfb` | `temu.order.amount.v2.query` | `eu_order_amount_v2_query.py` | [apis/temu-order-amount-v2-query.md](./apis/temu-order-amount-v2-query.md) |
| `3ffe9c4c79b9418285eb7ec09cf7b329` | `temu.order.amount.v3.query` | `eu_order_amount_v3_query.py` | [apis/temu-order-amount-v3-query.md](./apis/temu-order-amount-v3-query.md) |
| — | `bg.order.combinedshipment.list.get` | `eu_order_combinedshipment_list_get.py` | [apis/bg-order-combinedshipment-list-get.md](./apis/bg-order-combinedshipment-list-get.md) |
| — | `bg.order.customization.get` | `eu_order_customization_get.py` | [apis/bg-order-customization-get.md](./apis/bg-order-customization-get.md) |
| — | `temu.local.order.verification.upload` | `eu_order_verification_upload.py` | [apis/temu-local-order-verification-upload.md](./apis/temu-local-order-verification-upload.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.order.list.v2.get` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.detail.v2.get` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.shippinginfo.v2.get` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.decryptshippinginfo.get` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.amount.query` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `temu.order.amount.v2.query` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9&sub_menu_code=91661bf0642440ddbd462b25fa96edfb |
| `temu.order.amount.v3.query` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9&sub_menu_code=3ffe9c4c79b9418285eb7ec09cf7b329 |
| `bg.order.combinedshipment.list.get` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `bg.order.customization.get` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |
| `temu.local.order.verification.upload` | https://partner-eu.temu.com/documentation?menu_code=dbd3d395963a408984b8ae7dbc5f64f9 |

## 上游 OpenAPI（EU）

`POST` https://openapi-b-eu.temu.com/openapi/router（经 LinkFox 网关 `site=eu` 转发）

## 通用脚本

| 脚本 | 说明 |
|------|------|
| `temu_eu_proxy.py` | 任意 `type` + `params` |
| `temu_eu_file_download.py` | 加签文件下载 |

全球站（非 US/EU）订单使用 `linkfox-temu-order-global`。

## 与其他 Temu skill 的关系

| 能力 | skill |
|------|--------|
| 订单查询与发货准备 | `linkfox-temu-order-eu` |
| 取消订单 | `linkfox-temu-cancel-order-eu` |
| 退货与退款 | `linkfox-temu-returns-refunds-eu` |
| 履约/发货（购标、合作仓、自发货、跟踪） | `linkfox-temu-fulfillment-eu` |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 价格 | `linkfox-temu-price-eu` |
| 网关、Token | 本 skill `scripts/` |

## Token 说明

订单类接口建议使用 **`tokenPurpose=order-shipping`**。详见 [access-token.md](./access-token.md)。

通用转发和加签文件下载的完整定义见 [接口参考](api.md)。10 个具名操作之外，加签文件下载另计一项，总计 11 项；通用代理是复用入口，不重复计数。
