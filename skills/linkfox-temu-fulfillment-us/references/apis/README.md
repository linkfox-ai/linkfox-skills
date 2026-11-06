# Temu 美国站履约接口索引

网关公共规则、运行约定和加签文件下载见 [api.md](../api.md)。Partner 文档标识见 [partner-us-catalog.md](../partner-us-catalog.md)。

| 操作 | 接口文档 | 脚本 |
|---|---|---|
| `bg.cooperativewarehouse.fulfill.cancel` | [取消合作仓履约单](bg-cooperativewarehouse-fulfill-cancel.md) | `scripts/us_co_warehouse_cooperativewarehouse_fulfill_cancel.py` |
| `bg.cooperativewarehouse.fulfill.submit` | [提交合作仓履约](bg-cooperativewarehouse-fulfill-submit.md) | `scripts/us_co_warehouse_cooperativewarehouse_fulfill_submit.py` |
| `bg.cooperativewarehouse.provider.list` | [合作仓服务商列表](bg-cooperativewarehouse-provider-list.md) | `scripts/us_co_warehouse_cooperativewarehouse_provider_list.py` |
| `bg.cooperativewarehouse.token.authorization` | [合作仓 Token 授权](bg-cooperativewarehouse-token-authorization.md) | `scripts/us_co_warehouse_cooperativewarehouse_token_authorization.py` |
| `bg.logistics.companies.get` | [获取区域可用物流商](bg-logistics-companies-get.md) | `scripts/us_self_fulfilled_logistics_companies_get.py` |
| `bg.logistics.shipment.create` | [在线下单购标](bg-logistics-shipment-create.md) | `scripts/us_buy_shipping_logistics_shipment_create.py` |
| `bg.logistics.shipment.document.get` | [获取面单/运单文档](bg-logistics-shipment-document-get.md) | `scripts/us_buy_shipping_logistics_shipment_document_get.py` |
| `bg.logistics.shipment.result.get` | [查询购标/在线下单结果](bg-logistics-shipment-result-get.md) | `scripts/us_buy_shipping_logistics_shipment_result_get.py` |
| `bg.logistics.shipment.shippingtype.update` | [更新物流跟踪号 / 发货方式](bg-logistics-shipment-shippingtype-update.md) | `scripts/us_self_fulfilled_logistics_shipment_shippingtype_update.py` |
| `bg.logistics.shipment.sub.confirm` | [确认子包裹发货](bg-logistics-shipment-sub-confirm.md) | `scripts/us_self_fulfilled_logistics_shipment_sub_confirm.py` |
| `bg.logistics.shipment.update` | [更新发货/重试购标](bg-logistics-shipment-update.md) | `scripts/us_buy_shipping_logistics_shipment_update.py` |
| `bg.logistics.shipment.v2.confirm` | [确认发货 V2](bg-logistics-shipment-v2-confirm.md) | `scripts/us_self_fulfilled_logistics_shipment_v2_confirm.py` |
| `bg.logistics.shipment.v2.get` | [查询发货信息 V2](bg-logistics-shipment-v2-get.md) | `scripts/us_self_fulfilled_logistics_shipment_v2_get.py` |
| `bg.logistics.shipped.package.confirm` | [确认包裹已发货](bg-logistics-shipped-package-confirm.md) | `scripts/us_buy_shipping_logistics_shipped_package_confirm.py` |
| `bg.logistics.shippingservices.get` | [查询可用物流渠道](bg-logistics-shippingservices-get.md) | `scripts/us_buy_shipping_logistics_shippingservices_get.py` |
| `bg.logistics.warehouse.list.get` | [店铺仓库列表](bg-logistics-warehouse-list-get.md) | `scripts/us_buy_shipping_logistics_warehouse_list_get.py` |
| `bg.order.unshipped.package.get` | [查询未发货包裹](bg-order-unshipped-package-get.md) | `scripts/us_buy_shipping_order_unshipped_package_get.py` |
| `temu.logistics.candidate.scanform.list.get` | [候选 Scan Form 包裹列表](temu-logistics-candidate-scanform-list-get.md) | `scripts/us_buy_shipping_logistics_candidate_scanform_list_get.py` |
| `temu.logistics.label.list.get` | [面单列表查询](temu-logistics-label-list-get.md) | `scripts/us_buy_shipping_logistics_label_list_get.py` |
| `temu.logistics.scanform.create` | [创建 Scan Form](temu-logistics-scanform-create.md) | `scripts/us_buy_shipping_logistics_scanform_create.py` |
| `temu.logistics.scanform.document.get` | [获取 Scan Form 文档](temu-logistics-scanform-document-get.md) | `scripts/us_buy_shipping_logistics_scanform_document_get.py` |
| `temu.logistics.scanform.get` | [查询 Scan Form 详情](temu-logistics-scanform-get.md) | `scripts/us_buy_shipping_logistics_scanform_get.py` |
| `temu.logistics.shiplogisticstype.get` | [在线发货物流类型](temu-logistics-shiplogisticstype-get.md) | `scripts/us_buy_shipping_logistics_shiplogisticstype_get.py` |
| `temu.logistics.shipment.pickup.reservation.cancel` | [取消上门揽收预约](temu-logistics-shipment-pickup-reservation-cancel.md) | `scripts/us_buy_shipping_logistics_shipment_pickup_reservation_cancel.py` |
| `temu.logistics.shipment.pickup.reservation.create` | [预约上门揽收](temu-logistics-shipment-pickup-reservation-create.md) | `scripts/us_buy_shipping_logistics_shipment_pickup_reservation_create.py` |
| `temu.logistics.shipment.pickup.reservation.result.get` | [查询上门揽收预约结果](temu-logistics-shipment-pickup-reservation-result-get.md) | `scripts/us_buy_shipping_logistics_shipment_pickup_reservation_result_get.py` |
| `temu.track.trackinginfo.get` | [物流轨迹详情查询](temu-track-trackinginfo-get.md) | `scripts/us_tracking_track_trackinginfo_get.py` |

合作仓仅支持半托管。下列目录操作待接入，不计入 28 个已提供接口，不能按已实现操作执行；未列出的取消或改单同样未提供。

| 待接入操作 | 用途 |
|---|---|
| `bg.cooperativewarehouse.fulfill.query` | 查询合作仓履约状态 |
| `temu.cooperativewarehouse.skurelationship.create` | 创建合作仓 SKU 关系 |
| `temu.cooperativewarehouse.skurelationship.get` | 查询合作仓 SKU 关系 |
