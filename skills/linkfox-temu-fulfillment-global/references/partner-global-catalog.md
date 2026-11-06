# Partner Global — Fulfillment 接口目录（合一）

Partner Platform for **Global（全球区，非 US/EU）** **Fulfillment / 电商履行**：**Buy-Shipping**、**Co-Warehouse**、**Self-Fulfilled Shipments**、**Tracking**。

文档根 `menu_code`（浏览器地址栏常见）：`7289390cfd724be4a196f11ebe45a896`。

本 skill 经 `temu_global_proxy`（`POST /temu/proxy`）调用 **23** 个 `type`，默认 **`site=global`**、**`tokenPurpose=order-shipping`**。

脚本前缀：`global_buy_shipping_*`、`global_co_warehouse_*`、`global_self_fulfilled_*`、`global_tracking_*`。

> **与 US 版差异**：全球站 **不含** Scan Form 相关 4 个接口（`temu.logistics.scanform.create`、`temu.logistics.scanform.get`、`temu.logistics.scanform.document.get`、`temu.logistics.candidate.scanform.list.get`）；美国站请用 **`linkfox-temu-fulfillment-us`** 若需 Scan Form。

## 已接入（23）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `bg.logistics.warehouse.list.get` | `global_buy_shipping_logistics_warehouse_list_get.py` | [apis/bg-logistics-warehouse-list-get.md](./apis/bg-logistics-warehouse-list-get.md) |
| — | `temu.logistics.shiplogisticstype.get` | `global_buy_shipping_logistics_shiplogisticstype_get.py` | [apis/temu-logistics-shiplogisticstype-get.md](./apis/temu-logistics-shiplogisticstype-get.md) |
| — | `bg.logistics.shippingservices.get` | `global_buy_shipping_logistics_shippingservices_get.py` | [apis/bg-logistics-shippingservices-get.md](./apis/bg-logistics-shippingservices-get.md) |
| — | `bg.logistics.shipment.create` | `global_buy_shipping_logistics_shipment_create.py` | [apis/bg-logistics-shipment-create.md](./apis/bg-logistics-shipment-create.md) |
| — | `bg.logistics.shipment.result.get` | `global_buy_shipping_logistics_shipment_result_get.py` | [apis/bg-logistics-shipment-result-get.md](./apis/bg-logistics-shipment-result-get.md) |
| — | `bg.logistics.shipment.update` | `global_buy_shipping_logistics_shipment_update.py` | [apis/bg-logistics-shipment-update.md](./apis/bg-logistics-shipment-update.md) |
| — | `bg.logistics.shipment.document.get` | `global_buy_shipping_logistics_shipment_document_get.py` | [apis/bg-logistics-shipment-document-get.md](./apis/bg-logistics-shipment-document-get.md) |
| — | `bg.order.unshipped.package.get` | `global_buy_shipping_order_unshipped_package_get.py` | [apis/bg-order-unshipped-package-get.md](./apis/bg-order-unshipped-package-get.md) |
| — | `temu.logistics.label.list.get` | `global_buy_shipping_logistics_label_list_get.py` | [apis/temu-logistics-label-list-get.md](./apis/temu-logistics-label-list-get.md) |
| — | `bg.logistics.shipped.package.confirm` | `global_buy_shipping_logistics_shipped_package_confirm.py` | [apis/bg-logistics-shipped-package-confirm.md](./apis/bg-logistics-shipped-package-confirm.md) |
| — | `temu.logistics.shipment.pickup.reservation.create` | `global_buy_shipping_logistics_shipment_pickup_reservation_create.py` | [apis/temu-logistics-shipment-pickup-reservation-create.md](./apis/temu-logistics-shipment-pickup-reservation-create.md) |
| — | `temu.logistics.shipment.pickup.reservation.result.get` | `global_buy_shipping_logistics_shipment_pickup_reservation_result_get.py` | [apis/temu-logistics-shipment-pickup-reservation-result-get.md](./apis/temu-logistics-shipment-pickup-reservation-result-get.md) |
| — | `temu.logistics.shipment.pickup.reservation.cancel` | `global_buy_shipping_logistics_shipment_pickup_reservation_cancel.py` | [apis/temu-logistics-shipment-pickup-reservation-cancel.md](./apis/temu-logistics-shipment-pickup-reservation-cancel.md) |
| — | `bg.cooperativewarehouse.provider.list` | `global_co_warehouse_cooperativewarehouse_provider_list.py` | [apis/bg-cooperativewarehouse-provider-list.md](./apis/bg-cooperativewarehouse-provider-list.md) |
| — | `bg.cooperativewarehouse.token.authorization` | `global_co_warehouse_cooperativewarehouse_token_authorization.py` | [apis/bg-cooperativewarehouse-token-authorization.md](./apis/bg-cooperativewarehouse-token-authorization.md) |
| — | `bg.cooperativewarehouse.fulfill.submit` | `global_co_warehouse_cooperativewarehouse_fulfill_submit.py` | [apis/bg-cooperativewarehouse-fulfill-submit.md](./apis/bg-cooperativewarehouse-fulfill-submit.md) |
| — | `bg.cooperativewarehouse.fulfill.cancel` | `global_co_warehouse_cooperativewarehouse_fulfill_cancel.py` | [apis/bg-cooperativewarehouse-fulfill-cancel.md](./apis/bg-cooperativewarehouse-fulfill-cancel.md) |
| — | `bg.logistics.companies.get` | `global_self_fulfilled_logistics_companies_get.py` | [apis/bg-logistics-companies-get.md](./apis/bg-logistics-companies-get.md) |
| — | `bg.logistics.shipment.v2.confirm` | `global_self_fulfilled_logistics_shipment_v2_confirm.py` | [apis/bg-logistics-shipment-v2-confirm.md](./apis/bg-logistics-shipment-v2-confirm.md) |
| — | `bg.logistics.shipment.v2.get` | `global_self_fulfilled_logistics_shipment_v2_get.py` | [apis/bg-logistics-shipment-v2-get.md](./apis/bg-logistics-shipment-v2-get.md) |
| — | `bg.logistics.shipment.sub.confirm` | `global_self_fulfilled_logistics_shipment_sub_confirm.py` | [apis/bg-logistics-shipment-sub-confirm.md](./apis/bg-logistics-shipment-sub-confirm.md) |
| — | `bg.logistics.shipment.shippingtype.update` | `global_self_fulfilled_logistics_shipment_shippingtype_update.py` | [apis/bg-logistics-shipment-shippingtype-update.md](./apis/bg-logistics-shipment-shippingtype-update.md) |
| — | `temu.track.trackinginfo.get` | `global_tracking_track_trackinginfo_get.py` | [apis/temu-track-trackinginfo-get.md](./apis/temu-track-trackinginfo-get.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.logistics.warehouse.list.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.logistics.shiplogisticstype.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shippingservices.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipment.create` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipment.result.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipment.update` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipment.document.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.order.unshipped.package.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.logistics.label.list.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipped.package.confirm` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.logistics.shipment.pickup.reservation.create` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.logistics.shipment.pickup.reservation.result.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.logistics.shipment.pickup.reservation.cancel` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.cooperativewarehouse.provider.list` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.cooperativewarehouse.token.authorization` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.cooperativewarehouse.fulfill.submit` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.cooperativewarehouse.fulfill.cancel` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.companies.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipment.v2.confirm` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipment.v2.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipment.sub.confirm` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.logistics.shipment.shippingtype.update` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.track.trackinginfo.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |

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
| **履约/发货**（本 skill，`site=global`） | **`linkfox-temu-fulfillment-global`** |
| 订单查询、地址、金额 | `linkfox-temu-order-global` |
| 取消订单 | `linkfox-temu-cancel-order-global` |
| 商品管理 | `linkfox-temu-manage-product-global` |
| 美国站履约（含 Scan Form） | `linkfox-temu-fulfillment-us` |
| 欧洲站履约 | `linkfox-temu-fulfillment-eu` |

## Token 说明

建议使用 **`tokenPurpose=order-shipping`**。详见 [access-token.md](./access-token.md)。
