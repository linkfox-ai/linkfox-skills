# Partner Global — Returns & Refunds 接口目录

Partner Platform for **Global** 菜单：**Return and Refund / 退货与退款**（与 US 版对齐的 **9** 个 `type`）。

文档根 `menu_code`（与 `linkfox-temu-fulfillment-global` 等一致）：`7289390cfd724be4a196f11ebe45a896`。

本 skill 经 `temu_global_proxy`（`POST /temu/proxy`）调用，默认 **`site=global`**、**`tokenPurpose=order-shipping`**。

> Global Partner 各子菜单 `sub_menu_code` 请在 [partner-global.temu.com](https://partner-global.temu.com/documentation) 按 `type` 打开后补全。

## 已接入（9）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `bg.aftersales.parentaftersales.list.get` | `global_returns_refunds_aftersales_parentaftersales_list_get.py` | [apis/bg-aftersales-parentaftersales-list-get.md](./apis/bg-aftersales-parentaftersales-list-get.md) |
| — | `bg.aftersales.aftersales.list.get` | `global_returns_refunds_aftersales_aftersales_list_get.py` | [apis/bg-aftersales-aftersales-list-get.md](./apis/bg-aftersales-aftersales-list-get.md) |
| — | `temu.aftersales.parentaftersales.detail.get` | `global_returns_refunds_aftersales_parentaftersales_detail_get.py` | [apis/temu-aftersales-parentaftersales-detail-get.md](./apis/temu-aftersales-parentaftersales-detail-get.md) |
| — | `bg.aftersales.parentreturnorder.get` | `global_returns_refunds_aftersales_parentreturnorder_get.py` | [apis/bg-aftersales-parentreturnorder-get.md](./apis/bg-aftersales-parentreturnorder-get.md) |
| — | `temu.aftersales.returnaddress.get` | `global_returns_refunds_aftersales_returnaddress_get.py` | [apis/temu-aftersales-returnaddress-get.md](./apis/temu-aftersales-returnaddress-get.md) |
| — | `temu.aftersales.returnlabel.prepare.get` | `global_returns_refunds_aftersales_returnlabel_prepare_get.py` | [apis/temu-aftersales-returnlabel-prepare-get.md](./apis/temu-aftersales-returnlabel-prepare-get.md) |
| — | `temu.aftersales.signature.get` | `global_returns_refunds_aftersales_signature_get.py` | [apis/temu-aftersales-signature-get.md](./apis/temu-aftersales-signature-get.md) |
| — | `temu.aftersales.upload.returnlabel` | `global_returns_refunds_aftersales_upload_returnlabel.py` | [apis/temu-aftersales-upload-returnlabel.md](./apis/temu-aftersales-upload-returnlabel.md) |
| — | `temu.aftersales.carrier.get` | `global_returns_refunds_aftersales_carrier_get.py` | [apis/temu-aftersales-carrier-get.md](./apis/temu-aftersales-carrier-get.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.aftersales.parentaftersales.list.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.aftersales.aftersales.list.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.parentaftersales.detail.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.aftersales.parentreturnorder.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.returnaddress.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.returnlabel.prepare.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.signature.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.upload.returnlabel` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.carrier.get` | https://partner-global.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |

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
| **退货与退款**（本 skill） | **`linkfox-temu-returns-refunds-global`** |
| 取消订单 | `linkfox-temu-cancel-order-global` |
| 订单查询 | `linkfox-temu-order-global` |
| 商品管理 | `linkfox-temu-manage-product-global` |
| 履约/发货 | `linkfox-temu-fulfillment-global` |
| 美国站 | `linkfox-temu-returns-refunds-us` |
| 欧洲站 | `linkfox-temu-returns-refunds-eu` |

## Token 说明

建议使用 **`tokenPurpose=order-shipping`**（半托管 Global 订单/售后，见 [access-token.md](access-token.md)）。
