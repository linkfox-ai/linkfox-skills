# Partner US — Returns & Refunds 接口目录

Partner Platform for US 菜单：**Return and Refund**（`menu_code`=`d3d2812d87034d35adb016972349fcb0`）。

本 skill 经本 skill `temu_us_proxy`（`POST /temu/proxy`） 调用。内联参数见 [apis/README.md](./apis/README.md)。

## 已接入（9）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| `36d2f55993344cf2991815f675493560` | `bg.aftersales.parentaftersales.list.get` | `us_returns_refunds_aftersales_parentaftersales_list_get.py` | [bg-aftersales-parentaftersales-list-get.md](./apis/bg-aftersales-parentaftersales-list-get.md) |
| `d1675103eeed444fa3d650aa33b462be` | `bg.aftersales.aftersales.list.get` | `us_returns_refunds_aftersales_aftersales_list_get.py` | [bg-aftersales-aftersales-list-get.md](./apis/bg-aftersales-aftersales-list-get.md) |
| `f2551431265c4ea788e73fc3a741d075` | `temu.aftersales.parentaftersales.detail.get` | `us_returns_refunds_aftersales_parentaftersales_detail_get.py` | [temu-aftersales-parentaftersales-detail-get.md](./apis/temu-aftersales-parentaftersales-detail-get.md) |
| `986d1dc0ad9d4d44a380b8078405bae2` | `bg.aftersales.parentreturnorder.get` | `us_returns_refunds_aftersales_parentreturnorder_get.py` | [bg-aftersales-parentreturnorder-get.md](./apis/bg-aftersales-parentreturnorder-get.md) |
| `05d0a325704d4d538d708f3e256168e0` | `temu.aftersales.returnaddress.get` | `us_returns_refunds_aftersales_returnaddress_get.py` | [temu-aftersales-returnaddress-get.md](./apis/temu-aftersales-returnaddress-get.md) |
| `f6d52305e84d4945b2b1c8d3218bbe20` | `temu.aftersales.returnlabel.prepare.get` | `us_returns_refunds_aftersales_returnlabel_prepare_get.py` | [temu-aftersales-returnlabel-prepare-get.md](./apis/temu-aftersales-returnlabel-prepare-get.md) |
| `026c7431ac634dec9da8d7ab3c5a4825` | `temu.aftersales.signature.get` | `us_returns_refunds_aftersales_signature_get.py` | [temu-aftersales-signature-get.md](./apis/temu-aftersales-signature-get.md) |
| `9058c531e8cb41e0939db689ef059eaf` | `temu.aftersales.upload.returnlabel` | `us_returns_refunds_aftersales_upload_returnlabel.py` | [temu-aftersales-upload-returnlabel.md](./apis/temu-aftersales-upload-returnlabel.md) |
| `c1eceff2f3434bef8246668cc557ebb5` | `temu.aftersales.carrier.get` | `us_returns_refunds_aftersales_carrier_get.py` | [temu-aftersales-carrier-get.md](./apis/temu-aftersales-carrier-get.md) |

Partner 文档入口：

| type | URL |
|------|-----|
| `bg.aftersales.parentaftersales.list.get` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=36d2f55993344cf2991815f675493560 |
| `bg.aftersales.aftersales.list.get` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=d1675103eeed444fa3d650aa33b462be |
| `temu.aftersales.parentaftersales.detail.get` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=f2551431265c4ea788e73fc3a741d075 |
| `bg.aftersales.parentreturnorder.get` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=986d1dc0ad9d4d44a380b8078405bae2 |
| `temu.aftersales.returnaddress.get` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=05d0a325704d4d538d708f3e256168e0 |
| `temu.aftersales.returnlabel.prepare.get` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=f6d52305e84d4945b2b1c8d3218bbe20 |
| `temu.aftersales.signature.get` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=026c7431ac634dec9da8d7ab3c5a4825 |
| `temu.aftersales.upload.returnlabel` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=9058c531e8cb41e0939db689ef059eaf |
| `temu.aftersales.carrier.get` | https://partner-us.temu.com/documentation?menu_code=d3d2812d87034d35adb016972349fcb0&sub_menu_code=c1eceff2f3434bef8246668cc557ebb5 |

## 通用脚本（已就绪）

| 脚本 | 说明 |
|------|------|
| `temu_us_proxy.py` | 任意 `type` + `params` |
| `temu_us_file_download.py` | 加签文件下载 |

---

## 与其他 Temu US skill 的关系

| 能力 | skill |
|------|--------|
| **Returns & Refunds**（本 skill） | **`linkfox-temu-returns-refunds-us`** |
| 买家取消订单 | `linkfox-temu-cancel-order-us` |
| 卖家取消订单 | `linkfox-temu-cancel-order-us` |
| 订单查询 | `linkfox-temu-order-us` |
| 欧洲站退货退款 | `linkfox-temu-returns-refunds-eu` |
| 全球站退货退款 | `linkfox-temu-returns-refunds-global` |

## Token 说明

建议使用 **`tokenPurpose=order-shipping`**。详见 [Token 授权说明](access-token.md)。
