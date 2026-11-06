---
name: linkfox-shopee-store-orders
description: 查询和处理已授权 Shopee（虾皮）店铺订单，支持订单及包裹列表与详情、拆单与撤销拆单、取消订单、买家取消申请、备注、预约、买家发票、FBS 发票与处方审核。适用于卖家自己的订单查询和订单处理；不适用于店铺授权、商品选品、商品刊登、物流发货、退货退款或支付结算。
---
# Shopee 店铺订单管理

## 适用范围

### 适用

管理已授权 Shopee 店铺的订单、包裹、预约及适用地区的发票和处方审核。用户提到虾皮订单、order_sn、READY_TO_SHIP、booking 或 FBS 发票，且希望查询或处理自己店铺的订单时使用。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看待发货订单或指定订单详情 | 查询订单列表并按需读取详情。 |
| 看包裹、可发货订单或预约 | 查询包裹、发货前视图与预约数据。 |
| 取消订单、处理买家取消、改备注或拆单 | 根据已明确的操作目标处理订单。 |
| 查询买家发票资料或 FBS 发票 | 按店铺适用范围获取发票信息与下载链接。 |
| 审核处方或看仓库筛选配置 | 查询多仓配置或处理适用店铺的处方审核。 |

### 边界

授权与选店依赖 `linkfox-shopee-store-auth`；商户信息、店铺设置、商品刊登、账户健康、全球商品分别交给 `linkfox-shopee-store-merchant`、`linkfox-shopee-store-shop`、`linkfox-shopee-store-product`、`linkfox-shopee-store-account-health`、`linkfox-shopee-store-global-product`。物流发货、头程、退货退款和支付结算分别交给 `linkfox-shopee-store-logistics`、`linkfox-shopee-store-first-mile`、`linkfox-shopee-store-returns`、`linkfox-shopee-store-payment`；市场选品使用 `linkfox-youying-shopee-product-search`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 查询订单列表（`get_order_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/get_order_list` | [references/apis/get-order-list.md](references/apis/get-order-list.md) | `scripts/get_order_list.py` | 查询订单列表。 |
| 查询订单详情（`get_order_detail`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/get_order_detail` | [references/apis/get-order-detail.md](references/apis/get-order-detail.md) | `scripts/get_order_detail.py` | 查询订单详情。 |
| 查询可发货订单（`get_shipment_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/get_shipment_list` | [references/apis/get-shipment-list.md](references/apis/get-shipment-list.md) | `scripts/get_shipment_list.py` | 查询可发货订单。 |
| 搜索包裹列表（`search_package_list`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/search_package_list` | [references/apis/search-package-list.md](references/apis/search-package-list.md) | `scripts/search_package_list.py` | 搜索包裹列表。 |
| 查询包裹详情（`get_package_detail`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/get_package_detail` | [references/apis/get-package-detail.md](references/apis/get-package-detail.md) | `scripts/get_package_detail.py` | 查询包裹详情。 |
| 拆分订单（`split_order`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/split_order` | [references/apis/split-order.md](references/apis/split-order.md) | `scripts/split_order.py` | 拆分订单。 |
| 撤销订单拆分（`unsplit_order`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/unsplit_order` | [references/apis/unsplit-order.md](references/apis/unsplit-order.md) | `scripts/unsplit_order.py` | 撤销订单拆分。 |
| 取消订单（`cancel_order`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/cancel_order` | [references/apis/cancel-order.md](references/apis/cancel-order.md) | `scripts/cancel_order.py` | 取消订单。 |
| 处理买家取消申请（`handle_buyer_cancellation`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/handle_buyer_cancellation` | [references/apis/handle-buyer-cancellation.md](references/apis/handle-buyer-cancellation.md) | `scripts/handle_buyer_cancellation.py` | 处理买家取消申请。 |
| 设置订单备注（`set_note`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/set_note` | [references/apis/set-note.md](references/apis/set-note.md) | `scripts/set_note.py` | 设置订单备注。 |
| 查询待开票订单（`get_pending_buyer_invoice_order_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/get_pending_buyer_invoice_order_list` | [references/apis/get-pending-buyer-invoice-order-list.md](references/apis/get-pending-buyer-invoice-order-list.md) | `scripts/get_pending_buyer_invoice_order_list.py` | 查询待开票订单。 |
| 查询买家发票信息（`get_buyer_invoice_info`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/get_buyer_invoice_info` | [references/apis/get-buyer-invoice-info.md](references/apis/get-buyer-invoice-info.md) | `scripts/get_buyer_invoice_info.py` | 查询买家发票信息。 |
| 上传发票文件（`upload_invoice_doc`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/upload_invoice_doc` | [references/apis/upload-invoice-doc.md](references/apis/upload-invoice-doc.md) | `scripts/upload_invoice_doc.py` | 上传发票文件。 |
| 下载发票文件（`download_invoice_doc`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/download_invoice_doc` | [references/apis/download-invoice-doc.md](references/apis/download-invoice-doc.md) | `scripts/download_invoice_doc.py` | 下载发票文件。 |
| 处理处方审核（`handle_prescription_check`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/handle_prescription_check` | [references/apis/handle-prescription-check.md](references/apis/handle-prescription-check.md) | `scripts/handle_prescription_check.py` | 处理处方审核。 |
| 查询仓库过滤配置（`get_warehouse_filter_config`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/get_warehouse_filter_config` | [references/apis/get-warehouse-filter-config.md](references/apis/get-warehouse-filter-config.md) | `scripts/get_warehouse_filter_config.py` | 查询仓库过滤配置。 |
| 查询预约列表（`get_booking_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/get_booking_list` | [references/apis/get-booking-list.md](references/apis/get-booking-list.md) | `scripts/get_booking_list.py` | 查询预约列表。 |
| 查询预约详情（`get_booking_detail`） | POST `/shopee/developerProxy` → GET path：`api/v2/order/get_booking_detail` | [references/apis/get-booking-detail.md](references/apis/get-booking-detail.md) | `scripts/get_booking_detail.py` | 查询预约详情。 |
| 生成 FBS 发票（`generate_fbs_invoices`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/generate_fbs_invoices` | [references/apis/generate-fbs-invoices.md](references/apis/generate-fbs-invoices.md) | `scripts/generate_fbs_invoices.py` | 生成 FBS 发票。 |
| 查询 FBS 发票生成结果（`get_fbs_invoices_result`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/get_fbs_invoices_result` | [references/apis/get-fbs-invoices-result.md](references/apis/get-fbs-invoices-result.md) | `scripts/get_fbs_invoices_result.py` | 查询 FBS 发票生成结果。 |
| 获取 FBS 发票下载链接（`download_fbs_invoices`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/download_fbs_invoices` | [references/apis/download-fbs-invoices.md](references/apis/download-fbs-invoices.md) | `scripts/download_fbs_invoices.py` | 获取 FBS 发票下载链接。 |
| 估算部分取消金额（`get_estimiate_cancel_value`） | POST `/shopee/developerProxy` → POST path：`api/v2/order/get_estimiate_cancel_value` | [references/apis/get-estimiate-cancel-value.md](references/apis/get-estimiate-cancel-value.md) | `scripts/get_estimiate_cancel_value.py` | 估算部分取消金额。 |
| 已授权状态兼容查询（`storeTokens`） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_orders_common.py` → `resolve_store_tokens` | 查询授权状态，不返回原始令牌；订单 CLI 不自动调用。 |

## 前置条件

**先完成授权并确定目标店铺**：运行 `python scripts/check_auth_dependency.py` 检查 `linkfox-shopee-store-auth`；依赖缺失时先安装并通过该技能授权，不在本技能内实现授权或令牌刷新。检测退出码和选店约定见 [references/api.md](references/api.md#运行约定)。确认目标店铺、订单、包裹或预约后，读取接口清单中的对应文档。

## 订单处理流程

1. **选店**：只授权一家时直接使用该店铺；多家且用户只给店名时，通过认证技能的 authorized_stores 澄清目标。已给订单编号时仍保留店铺上下文，可直接查详情或执行用户明确要求的处理。
2. **按任务选择链路**：查待发货订单时按更新时间查列表，再按需查详情；包裹任务先检索包裹，再读详情。预约和仓库配置使用相应查询，发货动作转交物流技能。
3. **处理订单**：根据用户已明确的目标执行取消、买家取消申请处理、备注或拆单与撤销拆单；先核对店铺及订单范围，写入结果不确定时核对状态再决定后续动作。
4. **处理发票与处方**：先核对店铺适用范围。FBS 发票按生成、查询结果、获取下载链接的顺序完成；上传发票前先读对应文档的网关能力限制。
5. **解释结果**：依接口参考逐层检查响应，展示本次数据、处理结果与分页范围；需要后续页或再次查询时遵守调用约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；业务入口始终禁用响应缓存。失败或空结果时，不得自动换参、翻页或连续试探；按用户任务范围决定后续查询，写入结果不确定时先核对状态。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-orders-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、可用的顶层状态或计数字段（如 `errcode`、`total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **转发概念**：developerProxy 根据选店标识解析 token，经紫鸟 shopee-proxy 转发 Shopee；签名由代理处理。参数和适用地区等限制统一见各接口文档。
- **区分视图**：订单列表用于取得编号，详情用于读取可用完整资料；包裹列表、包裹详情与可发货列表属于发货前视图，不代表已执行物流发货。
- **展示数据**：用表格注明店铺、订单或包裹编号、可用状态及本次操作结果；缺失字段不补造，保留原始错误与数据。
- **按需读文件**：先看摘要，需具体内容时从保存文件提取。脚本运行与无缓存约定见 [references/api.md](references/api.md#运行约定)；业务入口始终禁用响应缓存。
- **区分层次**：能够解析 body 不等于业务成功，按接口文档判断外层响应、网关、上游和 Shopee 业务结果。token 过期返回认证技能重新授权；path 白名单、地区和上传能力问题按对应接口说明处理。

## 使用示例

### 查询待发货订单

用户：查看这个店铺的待发货订单，并列出订单详情。

确认店铺与时间范围，查询待发货列表，再按需查询返回订单详情，展示状态及本次返回范围。

### 按包裹处理

用户：找出这些订单对应的包裹。

检索包裹并查询详情；用户要求发货时转交物流技能，不将查询包裹结果表述为已发货。

### 取消、备注或拆单

用户：按我提供的原因取消这笔订单。

核对店铺、订单与用户指定内容，执行对应处理并解释结果；写入状态不确定时先核对订单，不自动重复提交。

### 查询 FBS 发票

用户：获取这个店铺指定日期范围内的 FBS 发票。

核对适用范围，按生成、结果查询、下载链接顺序处理，说明链接的有效期和实际可用结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
