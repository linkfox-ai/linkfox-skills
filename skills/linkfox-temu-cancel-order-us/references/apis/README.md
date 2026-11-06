# Cancel Order — 接口文档索引

每个 `type` 单独一份文档，经 `POST /temu/proxy` 调用。

以下为 6 个取消订单操作；辅助加签文件下载 `POST /temu/fileDownload` 定义于 [../api.md](../api.md)，合计 7 个接口（不含 Feedback）。通用代理与 LinkFox Token 探测复用现有端点，不单独计数。

## 买家/消费者取消（2）

| type | 文档 |
|------|------|
| `bg.aftersales.cancel.list.get` | [bg-aftersales-cancel-list-get.md](./bg-aftersales-cancel-list-get.md) |
| `bg.aftersales.cancel.agree` | [bg-aftersales-cancel-agree.md](./bg-aftersales-cancel-agree.md) |

## 卖家/店家取消（4）

| type | 文档 |
|------|------|
| `temu.order.cancel.appeal.apply` | [temu-order-cancel-appeal-apply.md](./temu-order-cancel-appeal-apply.md) |
| `temu.order.cancel.appeal.result.get` | [temu-order-cancel-appeal-result-get.md](./temu-order-cancel-appeal-result-get.md) |
| `temu.order.cancel.outofstock.apply` | [temu-order-cancel-outofstock-apply.md](./temu-order-cancel-outofstock-apply.md) |
| `temu.order.cancel.outofstock.result.get` | [temu-order-cancel-outofstock-result-get.md](./temu-order-cancel-outofstock-result-get.md) |
