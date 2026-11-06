# Partner US — 取消订单接口目录

Partner Platform for US：**买家取消** + **卖家取消**（`menu_code` / `sub_menu_code` 以 Partner 后台为准）。

本 skill 经 `temu_us_proxy`（`POST /temu/proxy`）调用 **6** 个 `type`，默认 **`site=us`**、**`tokenPurpose=order-shipping`**。

另提供 1 个辅助接口 `POST /temu/fileDownload`，定义见 [api.md](./api.md)。本目录仅列取消订单操作；包含辅助接口时合计 7 个接口，不含 Feedback。

## 已接入（6）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| _TBD_ | `bg.aftersales.cancel.list.get` | `us_cancel_aftersales_cancel_list_get.py` | [apis/bg-aftersales-cancel-list-get.md](./apis/bg-aftersales-cancel-list-get.md) |
| _TBD_ | `bg.aftersales.cancel.agree` | `us_cancel_aftersales_cancel_agree.py` | [apis/bg-aftersales-cancel-agree.md](./apis/bg-aftersales-cancel-agree.md) |
| _TBD_ | `temu.order.cancel.appeal.apply` | `us_seller_cancel_order_cancel_appeal_apply.py` | [apis/temu-order-cancel-appeal-apply.md](./apis/temu-order-cancel-appeal-apply.md) |
| _TBD_ | `temu.order.cancel.appeal.result.get` | `us_seller_cancel_order_cancel_appeal_result_get.py` | [apis/temu-order-cancel-appeal-result-get.md](./apis/temu-order-cancel-appeal-result-get.md) |
| _TBD_ | `temu.order.cancel.outofstock.apply` | `us_seller_cancel_order_cancel_outofstock_apply.py` | [apis/temu-order-cancel-outofstock-apply.md](./apis/temu-order-cancel-outofstock-apply.md) |
| _TBD_ | `temu.order.cancel.outofstock.result.get` | `us_seller_cancel_order_cancel_outofstock_result_get.py` | [apis/temu-order-cancel-outofstock-result-get.md](./apis/temu-order-cancel-outofstock-result-get.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.aftersales.cancel.list.get` | https://partner-us.temu.com/documentation（`sub_menu_code` 待补） |
| `bg.aftersales.cancel.agree` | https://partner-us.temu.com/documentation（`sub_menu_code` 待补） |
| `temu.order.cancel.appeal.apply` | https://partner-us.temu.com/documentation（`sub_menu_code` 待补） |
| `temu.order.cancel.appeal.result.get` | https://partner-us.temu.com/documentation（`sub_menu_code` 待补） |
| `temu.order.cancel.outofstock.apply` | https://partner-us.temu.com/documentation（`sub_menu_code` 待补） |
| `temu.order.cancel.outofstock.result.get` | https://partner-us.temu.com/documentation（`sub_menu_code` 待补） |

## 通用脚本

| 脚本 | 说明 |
|------|------|
| `temu_us_proxy.py` | 任意 `type` + `params` |
| `temu_us_file_download.py` | 加签文件下载 |

## 与其他 Temu skill 的关系

| 能力 | skill |
|------|--------|
| **取消订单**（本 skill，买家+卖家） | **`linkfox-temu-cancel-order-us`** |
| 订单查询、发货 | `linkfox-temu-order-us` |
| 欧洲站取消 | `linkfox-temu-cancel-order-eu` |
| 退货退款 | `linkfox-temu-returns-refunds-us` |

## Token 说明

建议使用 **`tokenPurpose=order-shipping`**。详见 [access-token.md](./access-token.md)。
