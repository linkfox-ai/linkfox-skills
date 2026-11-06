# Partner US — Fulfillment 接口目录（合一）

Partner Platform for US **Fulfillment / 电商履行**：**Buy-Shipping**、**Co-Warehouse**、**Self-Fulfilled Shipments**、**Tracking**。

本 skill 经 `temu_us_proxy`（`POST /temu/proxy`）调用 **27** 个 `type`，默认 **`site=us`**、**`tokenPurpose=order-shipping`**。

脚本前缀：`us_buy_shipping_*`、`us_co_warehouse_*`、`us_self_fulfilled_*`、`us_tracking_*`。

## 已接入（27）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| `bd462f852e7547a7a62bf6bba6023a24` | `bg.logistics.warehouse.list.get` | `us_buy_shipping_logistics_warehouse_list_get.py` | [apis/bg-logistics-warehouse-list-get.md](./apis/bg-logistics-warehouse-list-get.md) |
| `81e2cc2b0d6f4443b29ea8d1596e0fca` | `temu.logistics.shiplogisticstype.get` | `us_buy_shipping_logistics_shiplogisticstype_get.py` | [apis/temu-logistics-shiplogisticstype-get.md](./apis/temu-logistics-shiplogisticstype-get.md) |
| `18c1c2de89184d4e93a0f958da7bfc88` | `bg.logistics.shippingservices.get` | `us_buy_shipping_logistics_shippingservices_get.py` | [apis/bg-logistics-shippingservices-get.md](./apis/bg-logistics-shippingservices-get.md) |
| `1eadab72ed8041318604b163dd75cdac` | `bg.logistics.shipment.create` | `us_buy_shipping_logistics_shipment_create.py` | [apis/bg-logistics-shipment-create.md](./apis/bg-logistics-shipment-create.md) |
| `6aca164dab4c448e8c86229306c86590` | `bg.logistics.shipment.result.get` | `us_buy_shipping_logistics_shipment_result_get.py` | [apis/bg-logistics-shipment-result-get.md](./apis/bg-logistics-shipment-result-get.md) |
| `43a8da366d5847b9a7faf13915ce57d6` | `bg.logistics.shipment.update` | `us_buy_shipping_logistics_shipment_update.py` | [apis/bg-logistics-shipment-update.md](./apis/bg-logistics-shipment-update.md) |
| `e2d5025ff75e4c7881cd786912ec8b63` | `bg.logistics.shipment.document.get` | `us_buy_shipping_logistics_shipment_document_get.py` | [apis/bg-logistics-shipment-document-get.md](./apis/bg-logistics-shipment-document-get.md) |
| `5798cc84b38e4ca59bb60895d66630c9` | `bg.order.unshipped.package.get` | `us_buy_shipping_order_unshipped_package_get.py` | [apis/bg-order-unshipped-package-get.md](./apis/bg-order-unshipped-package-get.md) |
| `df97424d08f641f7adf942aa5accde3b` | `temu.logistics.label.list.get` | `us_buy_shipping_logistics_label_list_get.py` | [apis/temu-logistics-label-list-get.md](./apis/temu-logistics-label-list-get.md) |
| `aa4f29c85bfe460a8666bb92025a1743` | `bg.logistics.shipped.package.confirm` | `us_buy_shipping_logistics_shipped_package_confirm.py` | [apis/bg-logistics-shipped-package-confirm.md](./apis/bg-logistics-shipped-package-confirm.md) |
| `5b920f670469435f9cbbf9d70ae0b86b` | `temu.logistics.candidate.scanform.list.get` | `us_buy_shipping_logistics_candidate_scanform_list_get.py` | [apis/temu-logistics-candidate-scanform-list-get.md](./apis/temu-logistics-candidate-scanform-list-get.md) |
| `f70e104a1e114ce4a16bc17fcd7996fb` | `temu.logistics.scanform.create` | `us_buy_shipping_logistics_scanform_create.py` | [apis/temu-logistics-scanform-create.md](./apis/temu-logistics-scanform-create.md) |
| `9cc3edb526494a059c477fd99953fa3e` | `temu.logistics.scanform.get` | `us_buy_shipping_logistics_scanform_get.py` | [apis/temu-logistics-scanform-get.md](./apis/temu-logistics-scanform-get.md) |
| `1c9d0c2fade74f48a6bb22296c6fc509` | `temu.logistics.scanform.document.get` | `us_buy_shipping_logistics_scanform_document_get.py` | [apis/temu-logistics-scanform-document-get.md](./apis/temu-logistics-scanform-document-get.md) |
| `aff85d40b1364572a8383bcf5171f75b` | `temu.logistics.shipment.pickup.reservation.create` | `us_buy_shipping_logistics_shipment_pickup_reservation_create.py` | [apis/temu-logistics-shipment-pickup-reservation-create.md](./apis/temu-logistics-shipment-pickup-reservation-create.md) |
| `5cfaf127fdea4d419c6c9aa9c1b2536a` | `temu.logistics.shipment.pickup.reservation.result.get` | `us_buy_shipping_logistics_shipment_pickup_reservation_result_get.py` | [apis/temu-logistics-shipment-pickup-reservation-result-get.md](./apis/temu-logistics-shipment-pickup-reservation-result-get.md) |
| `eed978adf76e473e8d7239b0bbc19c9e` | `temu.logistics.shipment.pickup.reservation.cancel` | `us_buy_shipping_logistics_shipment_pickup_reservation_cancel.py` | [apis/temu-logistics-shipment-pickup-reservation-cancel.md](./apis/temu-logistics-shipment-pickup-reservation-cancel.md) |
| `e77d444a60b540039bfa1fc64e3cada7` | `bg.cooperativewarehouse.provider.list` | `us_co_warehouse_cooperativewarehouse_provider_list.py` | [apis/bg-cooperativewarehouse-provider-list.md](./apis/bg-cooperativewarehouse-provider-list.md) |
| `607fb76a2ef943d78e97dadbeca71aad` | `bg.cooperativewarehouse.token.authorization` | `us_co_warehouse_cooperativewarehouse_token_authorization.py` | [apis/bg-cooperativewarehouse-token-authorization.md](./apis/bg-cooperativewarehouse-token-authorization.md) |
| `d2d218ed9b8c4356aec5033744abe90b` | `bg.cooperativewarehouse.fulfill.submit` | `us_co_warehouse_cooperativewarehouse_fulfill_submit.py` | [apis/bg-cooperativewarehouse-fulfill-submit.md](./apis/bg-cooperativewarehouse-fulfill-submit.md) |
| `085d46b8a6604228b371e0706ac4af7d` | `bg.cooperativewarehouse.fulfill.cancel` | `us_co_warehouse_cooperativewarehouse_fulfill_cancel.py` | [apis/bg-cooperativewarehouse-fulfill-cancel.md](./apis/bg-cooperativewarehouse-fulfill-cancel.md) |
| `97bf9f5f4f454a589fb3192725bfeb7a` | `bg.logistics.companies.get` | `us_self_fulfilled_logistics_companies_get.py` | [apis/bg-logistics-companies-get.md](./apis/bg-logistics-companies-get.md) |
| _TBD_ | `bg.logistics.shipment.v2.confirm` | `us_self_fulfilled_logistics_shipment_v2_confirm.py` | [apis/bg-logistics-shipment-v2-confirm.md](./apis/bg-logistics-shipment-v2-confirm.md) |
| _TBD_ | `bg.logistics.shipment.v2.get` | `us_self_fulfilled_logistics_shipment_v2_get.py` | [apis/bg-logistics-shipment-v2-get.md](./apis/bg-logistics-shipment-v2-get.md) |
| _TBD_ | `bg.logistics.shipment.sub.confirm` | `us_self_fulfilled_logistics_shipment_sub_confirm.py` | [apis/bg-logistics-shipment-sub-confirm.md](./apis/bg-logistics-shipment-sub-confirm.md) |
| _TBD_ | `bg.logistics.shipment.shippingtype.update` | `us_self_fulfilled_logistics_shipment_shippingtype_update.py` | [apis/bg-logistics-shipment-shippingtype-update.md](./apis/bg-logistics-shipment-shippingtype-update.md) |
| `e4ec6bc629bf42e38346de78b297d349` | `temu.track.trackinginfo.get` | `us_tracking_track_trackinginfo_get.py` | [apis/temu-track-trackinginfo-get.md](./apis/temu-track-trackinginfo-get.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.logistics.warehouse.list.get` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=bd462f852e7547a7a62bf6bba6023a24 |
| `temu.logistics.shiplogisticstype.get` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=81e2cc2b0d6f4443b29ea8d1596e0fca |
| `bg.logistics.shippingservices.get` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=18c1c2de89184d4e93a0f958da7bfc88 |
| `bg.logistics.shipment.create` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=1eadab72ed8041318604b163dd75cdac |
| `bg.logistics.shipment.result.get` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=6aca164dab4c448e8c86229306c86590 |
| `bg.logistics.shipment.update` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=43a8da366d5847b9a7faf13915ce57d6 |
| `bg.order.unshipped.package.get` | https://partner-us.temu.com/documentation?menu_code=746951536ea1455faaf17ae9d60e5b34&sub_menu_code=5798cc84b38e4ca59bb60895d66630c9 |
| `bg.logistics.shipment.document.get` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=e2d5025ff75e4c7881cd786912ec8b63 |
| `temu.logistics.label.list.get` | https://partner-us.temu.com/documentation?menu_code=746951536ea1455faaf17ae9d60e5b34&sub_menu_code=df97424d08f641f7adf942aa5accde3b |
| `bg.logistics.shipped.package.confirm` | https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=aa4f29c85bfe460a8666bb92025a1743 |
| `temu.logistics.candidate.scanform.list.get` | https://partner-us.temu.com/documentation?menu_code=729bda2db47944d98b3bf5f100dc9e2f&sub_menu_code=5b920f670469435f9cbbf9d70ae0b86b |
| `temu.logistics.scanform.create` | https://partner-us.temu.com/documentation?menu_code=729bda2db47944d98b3bf5f100dc9e2f&sub_menu_code=f70e104a1e114ce4a16bc17fcd7996fb |
| `temu.logistics.scanform.get` | https://partner-us.temu.com/documentation?menu_code=d8425dcd25b04658843e622e178a3b42&sub_menu_code=9cc3edb526494a059c477fd99953fa3e |
| `temu.logistics.scanform.document.get` | https://partner-us.temu.com/documentation?menu_code=442a5ca8a9fd4bf7bb5493344a7e818f&sub_menu_code=1c9d0c2fade74f48a6bb22296c6fc509 |
| `temu.logistics.shipment.pickup.reservation.create` | https://partner-us.temu.com/documentation?menu_code=cf516cfc49364acba34be29c2600ec20&sub_menu_code=aff85d40b1364572a8383bcf5171f75b |
| `temu.logistics.shipment.pickup.reservation.result.get` | https://partner-us.temu.com/documentation?menu_code=cf516cfc49364acba34be29c2600ec20&sub_menu_code=5cfaf127fdea4d419c6c9aa9c1b2536a |
| `temu.logistics.shipment.pickup.reservation.cancel` | https://partner-us.temu.com/documentation?menu_code=cf516cfc49364acba34be29c2600ec20&sub_menu_code=eed978adf76e473e8d7239b0bbc19c9e |
| `bg.cooperativewarehouse.provider.list` | https://partner-us.temu.com/documentation?menu_code=fd19c5c9a430407a8c587d7f3e492c4a&sub_menu_code=e77d444a60b540039bfa1fc64e3cada7 |
| `bg.cooperativewarehouse.token.authorization` | https://partner-us.temu.com/documentation?menu_code=fd19c5c9a430407a8c587d7f3e492c4a&sub_menu_code=607fb76a2ef943d78e97dadbeca71aad |
| `bg.cooperativewarehouse.fulfill.submit` | https://partner-us.temu.com/documentation?menu_code=fd19c5c9a430407a8c587d7f3e492c4a&sub_menu_code=d2d218ed9b8c4356aec5033744abe90b |
| `bg.cooperativewarehouse.fulfill.cancel` | https://partner-us.temu.com/documentation?menu_code=fd19c5c9a430407a8c587d7f3e492c4a&sub_menu_code=085d46b8a6604228b371e0706ac4af7d |
| `bg.logistics.companies.get` | https://partner-us.temu.com/documentation?menu_code=38e79b35d2cb463d85619c1c786dd303&sub_menu_code=97bf9f5f4f454a589fb3192725bfeb7a |
| `bg.logistics.shipment.v2.confirm` | https://partner-us.temu.com/documentation?menu_code=38e79b35d2cb463d85619c1c786dd303（`sub_menu_code` 待补） |
| `bg.logistics.shipment.v2.get` | https://partner-us.temu.com/documentation?menu_code=38e79b35d2cb463d85619c1c786dd303（`sub_menu_code` 待补） |
| `bg.logistics.shipment.sub.confirm` | https://partner-us.temu.com/documentation（`menu_code` / `sub_menu_code` 待补） |
| `bg.logistics.shipment.shippingtype.update` | https://partner-us.temu.com/documentation（`menu_code` / `sub_menu_code` 待补） |
| `temu.track.trackinginfo.get` | https://partner-us.temu.com/documentation?menu_code=e8a433cf16604acf82e20af25672cec0&sub_menu_code=e4ec6bc629bf42e38346de78b297d349 |

## 通用脚本

| 脚本 | 说明 |
|------|------|
| `temu_us_proxy.py` | 任意已确认 type + params 的通用入口 |
| `temu_us_file_download.py` | 加签文件下载 |

## 与其他 Temu skill 的关系

| 能力 | skill |
|------|--------|
| **履约/发货**（本 skill） | **`linkfox-temu-fulfillment-us`** |
| 订单查询、地址、金额 | `linkfox-temu-order-us` |
| 取消订单 | `linkfox-temu-cancel-order-us` |
| 商品管理 | `linkfox-temu-manage-product-us` |
| 欧洲站履约/发货 | `linkfox-temu-fulfillment-eu` |

## Token 说明

建议使用 **`tokenPurpose=order-shipping`**。详见 [access-token.md](./access-token.md)。
