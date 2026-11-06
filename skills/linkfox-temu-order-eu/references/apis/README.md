# Temu EU 订单接口文档索引

每个 `type` 单独一份文档，经 `POST /temu/proxy` 调用。网关与鉴权见 [../api.md](../api.md)；目录与 `sub_menu_code` 见 [../partner-eu-catalog.md](../partner-eu-catalog.md)。

## 查询（4）

| type | 文档 |
|------|------|
| `bg.order.list.v2.get` | [bg-order-list-v2-get.md](./bg-order-list-v2-get.md) |
| `bg.order.detail.v2.get` | [bg-order-detail-v2-get.md](./bg-order-detail-v2-get.md) |
| `bg.order.shippinginfo.v2.get` | [bg-order-shippinginfo-v2-get.md](./bg-order-shippinginfo-v2-get.md) |
| `bg.order.decryptshippinginfo.get` | [bg-order-decryptshippinginfo-get.md](./bg-order-decryptshippinginfo-get.md) |

## 金额 / ERP（3）

| type | 文档 |
|------|------|
| `bg.order.amount.query` | [bg-order-amount-query.md](./bg-order-amount-query.md) |
| `temu.order.amount.v2.query` | [temu-order-amount-v2-query.md](./temu-order-amount-v2-query.md) |
| `temu.order.amount.v3.query` | [temu-order-amount-v3-query.md](./temu-order-amount-v3-query.md) |

## 发货 / 物流（1）

| type | 文档 |
|------|------|
| `bg.order.combinedshipment.list.get` | [bg-order-combinedshipment-list-get.md](./bg-order-combinedshipment-list-get.md) |

## 定制商品（1）

| type | 文档 |
|------|------|
| `bg.order.customization.get` | [bg-order-customization-get.md](./bg-order-customization-get.md) |

## 核验 / 鉴真上传（1）

| type | 文档 |
|------|------|
| `temu.local.order.verification.upload` | [temu-local-order-verification-upload.md](./temu-local-order-verification-upload.md) |

## 发货 / 物流（待补充）

| type | 文档 |
|------|------|
| _待用户提供 Partner 文档_ | — |

## 其他（待补充）

| type | 文档 |
|------|------|
| _待用户提供 Partner 文档_ | — |

通用转发及加签文件下载的定义见 [网关接口参考](../api.md)。
