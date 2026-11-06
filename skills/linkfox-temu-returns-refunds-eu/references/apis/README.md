# 退货与退款接口文档索引

每个 `type` 单独一份文档。网关见 [../api.md](../api.md)；目录见 [../partner-eu-catalog.md](../partner-eu-catalog.md)。

## 父售后单 / 列表与详情

| type | 说明 | 文档 |
|------|------|------|
| `bg.aftersales.parentaftersales.list.get` | 父售后单列表查询 | [bg-aftersales-parentaftersales-list-get.md](./bg-aftersales-parentaftersales-list-get.md) |
| `bg.aftersales.aftersales.list.get` | 子售后单列表查询 | [bg-aftersales-aftersales-list-get.md](./bg-aftersales-aftersales-list-get.md) |
| `temu.aftersales.parentaftersales.detail.get` | 父售后单详情 | [temu-aftersales-parentaftersales-detail-get.md](./temu-aftersales-parentaftersales-detail-get.md) |

## 退货物流 / 地址 / 面单

| type | 说明 | 文档 |
|------|------|------|
| `bg.aftersales.parentreturnorder.get` | 父退货物流信息 | [bg-aftersales-parentreturnorder-get.md](./bg-aftersales-parentreturnorder-get.md) |
| `temu.aftersales.returnaddress.get` | 退货地址查询 | [temu-aftersales-returnaddress-get.md](./temu-aftersales-returnaddress-get.md) |
| `temu.aftersales.returnlabel.prepare.get` | 退货面单准备信息 | [temu-aftersales-returnlabel-prepare-get.md](./temu-aftersales-returnlabel-prepare-get.md) |
| `temu.aftersales.upload.returnlabel` | 上传退货面单 | [temu-aftersales-upload-returnlabel.md](./temu-aftersales-upload-returnlabel.md) |

## 承运商与签名

| type | 说明 | 文档 |
|------|------|------|
| `temu.aftersales.signature.get` | 售后签名获取 | [temu-aftersales-signature-get.md](./temu-aftersales-signature-get.md) |
| `temu.aftersales.carrier.get` | 承运商列表 | [temu-aftersales-carrier-get.md](./temu-aftersales-carrier-get.md) |

> 买家/卖家**取消订单**见 `linkfox-temu-cancel-order-eu`。
