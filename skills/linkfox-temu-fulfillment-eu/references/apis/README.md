# Temu 欧洲站履约接口分类索引

完整接口与认证约定见 [../api.md](../api.md)，官方子菜单见 [../partner-eu-catalog.md](../partner-eu-catalog.md)。

## 购标、面单、Scan Form 与揽收

| type | 文档 |
|------|------|
| `bg.logistics.shipment.create` | [在线下单购标](bg-logistics-shipment-create.md) |
| `bg.logistics.shipment.document.get` | [获取面单/运单文档](bg-logistics-shipment-document-get.md) |
| `bg.logistics.shipment.result.get` | [查询购标/在线下单结果](bg-logistics-shipment-result-get.md) |
| `bg.logistics.shipment.update` | [更新发货/重试购标](bg-logistics-shipment-update.md) |
| `bg.logistics.shipped.package.confirm` | [确认包裹已发货](bg-logistics-shipped-package-confirm.md) |
| `bg.logistics.shippingservices.get` | [查询可用物流渠道](bg-logistics-shippingservices-get.md) |
| `bg.logistics.warehouse.list.get` | [店铺仓库列表](bg-logistics-warehouse-list-get.md) |
| `bg.order.unshipped.package.get` | [查询未发货包裹](bg-order-unshipped-package-get.md) |
| `temu.logistics.candidate.scanform.list.get` | [候选 Scan Form 包裹列表](temu-logistics-candidate-scanform-list-get.md) |
| `temu.logistics.label.list.get` | [面单列表查询](temu-logistics-label-list-get.md) |
| `temu.logistics.scanform.create` | [创建 Scan Form](temu-logistics-scanform-create.md) |
| `temu.logistics.scanform.document.get` | [获取 Scan Form 文档](temu-logistics-scanform-document-get.md) |
| `temu.logistics.scanform.get` | [查询 Scan Form 详情](temu-logistics-scanform-get.md) |
| `temu.logistics.shiplogisticstype.get` | [在线发货物流类型](temu-logistics-shiplogisticstype-get.md) |
| `temu.logistics.shipment.pickup.reservation.cancel` | [取消上门揽收预约](temu-logistics-shipment-pickup-reservation-cancel.md) |
| `temu.logistics.shipment.pickup.reservation.create` | [预约上门揽收](temu-logistics-shipment-pickup-reservation-create.md) |
| `temu.logistics.shipment.pickup.reservation.result.get` | [查询上门揽收预约结果](temu-logistics-shipment-pickup-reservation-result-get.md) |

## 合作仓履约

| type | 文档 |
|------|------|
| `bg.cooperativewarehouse.fulfill.cancel` | [取消合作仓履约单](bg-cooperativewarehouse-fulfill-cancel.md) |
| `bg.cooperativewarehouse.fulfill.submit` | [提交合作仓履约](bg-cooperativewarehouse-fulfill-submit.md) |
| `bg.cooperativewarehouse.provider.list` | [合作仓服务商列表](bg-cooperativewarehouse-provider-list.md) |
| `bg.cooperativewarehouse.token.authorization` | [合作仓 Token 授权](bg-cooperativewarehouse-token-authorization.md) |

## 自发货与 POD

| type | 文档 |
|------|------|
| `bg.logistics.companies.get` | [获取区域可用物流商](bg-logistics-companies-get.md) |
| `bg.logistics.shipment.shippingtype.update` | [更新物流跟踪号 / 发货方式](bg-logistics-shipment-shippingtype-update.md) |
| `bg.logistics.shipment.sub.confirm` | [确认子包裹发货](bg-logistics-shipment-sub-confirm.md) |
| `bg.logistics.shipment.v2.confirm` | [确认发货 V2](bg-logistics-shipment-v2-confirm.md) |
| `bg.logistics.shipment.v2.get` | [查询发货信息 V2](bg-logistics-shipment-v2-get.md) |
| `temu.logistics.self.delivery.pod.audit.result.get` | [自配送 POD 审核结果查询](temu-logistics-self-delivery-pod-audit-result-get.md) |
| `temu.logistics.self.delivery.pod.upload.signature.query` | [自配送 POD 上传签名查询](temu-logistics-self-delivery-pod-upload-signature-query.md) |
| `temu.logistics.self.delivery.pod.upload` | [自配送 POD 上传](temu-logistics-self-delivery-pod-upload.md) |

## 物流跟踪

| type | 文档 |
|------|------|
| `temu.track.trackinginfo.get` | [物流轨迹详情查询](temu-track-trackinginfo-get.md) |

## 文件下载

[加签文件下载](file-download.md)。

## 尚未接入

`bg.cooperativewarehouse.fulfill.query`、`temu.cooperativewarehouse.skurelationship.create`、`temu.cooperativewarehouse.skurelationship.get` 尚无本技能专用文档与脚本，不计入已接入数量。
