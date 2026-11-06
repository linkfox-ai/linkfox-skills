# Partner EU — Returns & Refunds 接口目录

Partner Platform for EU 菜单：**Return and Refund / 退货与退款**（与 US 版对齐的 **9** 个 `type`）。

文档根 `menu_code`（浏览器地址栏常见）：`7289390cfd724be4a196f11ebe45a896`。

本 skill 经 `temu_eu_proxy`（`POST /temu/proxy`）调用，默认 **`site=eu`**、**`tokenPurpose=order-shipping`**。

> EU Partner 各子菜单 `sub_menu_code` 请在 [partner-eu.temu.com](https://partner-eu.temu.com/documentation) 按 `type` 打开后补全。

## 已接入（9）

| sub_menu_code | type | 脚本 | 参数文档 |
|---------------|------|------|----------|
| — | `bg.aftersales.parentaftersales.list.get` | `eu_returns_refunds_aftersales_parentaftersales_list_get.py` | [apis/bg-aftersales-parentaftersales-list-get.md](./apis/bg-aftersales-parentaftersales-list-get.md) |
| — | `bg.aftersales.aftersales.list.get` | `eu_returns_refunds_aftersales_aftersales_list_get.py` | [apis/bg-aftersales-aftersales-list-get.md](./apis/bg-aftersales-aftersales-list-get.md) |
| — | `temu.aftersales.parentaftersales.detail.get` | `eu_returns_refunds_aftersales_parentaftersales_detail_get.py` | [apis/temu-aftersales-parentaftersales-detail-get.md](./apis/temu-aftersales-parentaftersales-detail-get.md) |
| — | `bg.aftersales.parentreturnorder.get` | `eu_returns_refunds_aftersales_parentreturnorder_get.py` | [apis/bg-aftersales-parentreturnorder-get.md](./apis/bg-aftersales-parentreturnorder-get.md) |
| — | `temu.aftersales.returnaddress.get` | `eu_returns_refunds_aftersales_returnaddress_get.py` | [apis/temu-aftersales-returnaddress-get.md](./apis/temu-aftersales-returnaddress-get.md) |
| — | `temu.aftersales.returnlabel.prepare.get` | `eu_returns_refunds_aftersales_returnlabel_prepare_get.py` | [apis/temu-aftersales-returnlabel-prepare-get.md](./apis/temu-aftersales-returnlabel-prepare-get.md) |
| — | `temu.aftersales.signature.get` | `eu_returns_refunds_aftersales_signature_get.py` | [apis/temu-aftersales-signature-get.md](./apis/temu-aftersales-signature-get.md) |
| — | `temu.aftersales.upload.returnlabel` | `eu_returns_refunds_aftersales_upload_returnlabel.py` | [apis/temu-aftersales-upload-returnlabel.md](./apis/temu-aftersales-upload-returnlabel.md) |
| — | `temu.aftersales.carrier.get` | `eu_returns_refunds_aftersales_carrier_get.py` | [apis/temu-aftersales-carrier-get.md](./apis/temu-aftersales-carrier-get.md) |

## 官方文档 URL

| type | URL |
|------|-----|
| `bg.aftersales.parentaftersales.list.get` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.aftersales.aftersales.list.get` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.parentaftersales.detail.get` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `bg.aftersales.parentreturnorder.get` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.returnaddress.get` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.returnlabel.prepare.get` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.signature.get` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.upload.returnlabel` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |
| `temu.aftersales.carrier.get` | https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 |

## 上游 OpenAPI（EU）

`POST` https://openapi-b-eu.temu.com/openapi/router（经 LinkFox 网关 `site=eu` 转发）

## 通用脚本

| 脚本 | 说明 |
|------|------|
| `temu_eu_proxy.py` | 任意 `type` + `params` |
| `temu_eu_file_download.py` | 加签文件下载 |

## 与其他 Temu skill 的关系

| 能力 | skill |
|------|--------|
| **退货与退款**（本 skill） | **`linkfox-temu-returns-refunds-eu`** |
| 取消订单 | `linkfox-temu-cancel-order-eu` |
| 订单查询 | `linkfox-temu-order-eu` |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 履约/发货 | `linkfox-temu-fulfillment-eu` |
| 美国站退货退款 | `linkfox-temu-returns-refunds-us` |
| 全球站退货退款 | `linkfox-temu-returns-refunds-global` |

## Token 说明

建议使用 **`tokenPurpose=order-shipping`**。详见 [access-token.md](./access-token.md)。

## 后续接口接入维护

收到完整 Partner 文档（type、sub_menu_code、URL、请求和响应参数表）后，再补充对应接口文件与专用 CLI；专用 CLI 复用 `_eu_returns_refunds_script.run_cli`，并同步本目录索引、接口清单与本目录表。未提供的 sub_menu_code 保持未确认，不猜测。
