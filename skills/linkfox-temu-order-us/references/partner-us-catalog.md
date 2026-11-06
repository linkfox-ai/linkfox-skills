# Partner US 订单接口目录

本技能提供 8 个订单操作和 1 个加签文件下载操作。8 个订单操作均经 POST `/temu/proxy` 转发，Body `type` 区分操作，上游 path 为 `/openapi/router`；下载经 POST `/temu/fileDownload`。完整端点、脚本与接口参考以 [SKILL.md](../SKILL.md#接口清单) 为准，网关与认证兼容见 [api.md](api.md)。

Partner 文档入口：https://partner-us.temu.com/documentation 。菜单为 Order / 订单管理；各接口的 menu_code / sub_menu_code 和详情 URL 须以授权后台对应接口页为准，不猜测编号或链接。

| 接口 | 脚本 | 参数文档 |
|---|---|---|
| 订单金额/供货价查询（`bg.order.amount.query`） | `scripts/us_order_amount_query.py` | [apis/bg-order-amount-query.md](apis/bg-order-amount-query.md) |
| 可合并发货订单组列表（`bg.order.combinedshipment.list.get`） | `scripts/us_order_combinedshipment_list_get.py` | [apis/bg-order-combinedshipment-list-get.md](apis/bg-order-combinedshipment-list-get.md) |
| 订单定制商品内容批量查询（`bg.order.customization.get`） | `scripts/us_order_customization_get.py` | [apis/bg-order-customization-get.md](apis/bg-order-customization-get.md) |
| 订单收货地址解密查询（`bg.order.decryptshippinginfo.get`） | `scripts/us_order_decryptshippinginfo_get.py` | [apis/bg-order-decryptshippinginfo-get.md](apis/bg-order-decryptshippinginfo-get.md) |
| 订单详情查询 V2（`bg.order.detail.v2.get`） | `scripts/us_order_detail_v2_get.py` | [apis/bg-order-detail-v2-get.md](apis/bg-order-detail-v2-get.md) |
| 订单列表查询 V2（`bg.order.list.v2.get`） | `scripts/us_order_list_v2_get.py` | [apis/bg-order-list-v2-get.md](apis/bg-order-list-v2-get.md) |
| 订单收货地址查询 V2（`bg.order.shippinginfo.v2.get`） | `scripts/us_order_shippinginfo_v2_get.py` | [apis/bg-order-shippinginfo-v2-get.md](apis/bg-order-shippinginfo-v2-get.md) |
| 订单核验信息上传（`temu.local.order.verification.upload`） | `scripts/us_order_verification_upload.py` | [apis/temu-local-order-verification-upload.md](apis/temu-local-order-verification-upload.md) |

US 通用脚本 `scripts/temu_us_proxy.py` 接受 type + params；`scripts/temu_us_file_download.py` 获取加签文件。保留 `scripts/temu_proxy.py` / `scripts/temu_file_download.py` 多站点兼容入口，不扩大本技能工作流范围。

## 扩展约定

用户提供 Partner 文档（type、参数表、URL 和可用的 sub_menu_code）后，方可新增 `references/apis/<type-slug>.md` 完整入参与出参层级，添加调用 `_us_order_script.run_cli` 的 `scripts/us_order_<slug>.py` 薄封装，并同步本目录、[apis/README.md](apis/README.md) 和 SKILL.md 的接口清单。

## 场景与授权

订单查询、对账、定制内容、合并组与核验上传使用本技能。商品管理、发品、价格、取消、退货退款和履约技能转交见 [SKILL.md](../SKILL.md#边界)。全球站（非 US/EU）订单使用 `linkfox-temu-order-global`，欧洲站使用 `linkfox-temu-order-eu`。

半托管美国站订单与发货授权用途为 order-shipping，获取步骤与令牌脚本见 [access-token.md](access-token.md)。网关与 Token 能力由本技能 scripts 提供。
