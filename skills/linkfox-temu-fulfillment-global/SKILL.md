---
name: linkfox-temu-fulfillment-global
description: 管理 Temu 全球站半托管店铺的购标面单、合作仓履约、卖家自发货、上门揽收预约和物流追踪，支持加签面单文件下载。适用于全球站发货准备、履约提交、结果核对和物流跟进；不适用于美国站、欧洲站、Scan Form、订单查询、商品库存管理或退货退款。
---
# Temu 全球站履约与发货

## 适用范围

### 适用

面向已授权 Temu 全球站半托管店铺，处理购标、面单、合作仓、自发货、揽收和物流轨迹。覆盖 Buy-Shipping 13 项、Co-Warehouse 4 项、Self-Fulfilled 5 项和 Tracking 1 项业务操作，以及加签文件下载。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 这批订单选哪个仓库和物流，帮我购标 | 发货准备：核对仓库、渠道与包裹，再提交购标。 |
| 购标完成了吗，下载面单 | 结果核验：查询异步状态，取面单链接与加签文件。 |
| 预约或取消上门揽收 | 揽收管理：提交预约、查异步结果或取消已有预约。 |
| 交给合作仓发货，或取消履约 | 合作仓：选择服务商、授权、提交或取消履约。 |
| 我有运单号，确认发货或修正物流 | 自发货：提交物流、追加子包裹或更正跟踪号。 |
| 查这个包裹的物流轨迹 | 物流跟进：查询节点、时间和状态。 |

### 边界

全球站不包含 Scan Form 创建、查询、文档获取及候选列表；美国站和 Scan Form 使用 `linkfox-temu-fulfillment-us`，欧洲站使用 `linkfox-temu-fulfillment-eu`。
订单列表、详情和地址使用 `linkfox-temu-order-global`；取消订单使用 `linkfox-temu-cancel-order-global`；商品库存使用 `linkfox-temu-manage-product-global`；退货退款使用 `linkfox-temu-returns-refunds-global`。取消合作仓履约与取消订单是不同业务。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 取消合作仓履约单（`bg.cooperativewarehouse.fulfill.cancel`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.cooperativewarehouse.fulfill.cancel` | [references/apis/bg-cooperativewarehouse-fulfill-cancel.md](references/apis/bg-cooperativewarehouse-fulfill-cancel.md) | `scripts/global_co_warehouse_cooperativewarehouse_fulfill_cancel.py` | 取消合作仓履约单。 |
| 提交合作仓履约（`bg.cooperativewarehouse.fulfill.submit`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.cooperativewarehouse.fulfill.submit` | [references/apis/bg-cooperativewarehouse-fulfill-submit.md](references/apis/bg-cooperativewarehouse-fulfill-submit.md) | `scripts/global_co_warehouse_cooperativewarehouse_fulfill_submit.py` | 提交合作仓履约。 |
| 合作仓服务商列表（`bg.cooperativewarehouse.provider.list`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.cooperativewarehouse.provider.list` | [references/apis/bg-cooperativewarehouse-provider-list.md](references/apis/bg-cooperativewarehouse-provider-list.md) | `scripts/global_co_warehouse_cooperativewarehouse_provider_list.py` | 合作仓服务商列表。 |
| 合作仓 Token 授权（`bg.cooperativewarehouse.token.authorization`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.cooperativewarehouse.token.authorization` | [references/apis/bg-cooperativewarehouse-token-authorization.md](references/apis/bg-cooperativewarehouse-token-authorization.md) | `scripts/global_co_warehouse_cooperativewarehouse_token_authorization.py` | 合作仓 Token 授权。 |
| 获取区域可用物流商（`bg.logistics.companies.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.companies.get` | [references/apis/bg-logistics-companies-get.md](references/apis/bg-logistics-companies-get.md) | `scripts/global_self_fulfilled_logistics_companies_get.py` | 获取区域可用物流商。 |
| 在线下单购标（`bg.logistics.shipment.create`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipment.create` | [references/apis/bg-logistics-shipment-create.md](references/apis/bg-logistics-shipment-create.md) | `scripts/global_buy_shipping_logistics_shipment_create.py` | 在线下单购标。 |
| 获取面单/运单文档（`bg.logistics.shipment.document.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipment.document.get` | [references/apis/bg-logistics-shipment-document-get.md](references/apis/bg-logistics-shipment-document-get.md) | `scripts/global_buy_shipping_logistics_shipment_document_get.py` | 获取面单/运单文档。 |
| 查询购标/在线下单结果（`bg.logistics.shipment.result.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipment.result.get` | [references/apis/bg-logistics-shipment-result-get.md](references/apis/bg-logistics-shipment-result-get.md) | `scripts/global_buy_shipping_logistics_shipment_result_get.py` | 查询购标/在线下单结果。 |
| 更新物流跟踪号 / 发货方式（`bg.logistics.shipment.shippingtype.update`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipment.shippingtype.update` | [references/apis/bg-logistics-shipment-shippingtype-update.md](references/apis/bg-logistics-shipment-shippingtype-update.md) | `scripts/global_self_fulfilled_logistics_shipment_shippingtype_update.py` | 更新物流跟踪号 / 发货方式。 |
| 确认子包裹发货（`bg.logistics.shipment.sub.confirm`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipment.sub.confirm` | [references/apis/bg-logistics-shipment-sub-confirm.md](references/apis/bg-logistics-shipment-sub-confirm.md) | `scripts/global_self_fulfilled_logistics_shipment_sub_confirm.py` | 确认子包裹发货。 |
| 更新发货/重试购标（`bg.logistics.shipment.update`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipment.update` | [references/apis/bg-logistics-shipment-update.md](references/apis/bg-logistics-shipment-update.md) | `scripts/global_buy_shipping_logistics_shipment_update.py` | 更新发货/重试购标。 |
| 确认发货 V2（`bg.logistics.shipment.v2.confirm`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipment.v2.confirm` | [references/apis/bg-logistics-shipment-v2-confirm.md](references/apis/bg-logistics-shipment-v2-confirm.md) | `scripts/global_self_fulfilled_logistics_shipment_v2_confirm.py` | 确认发货 V2。 |
| 查询发货信息 V2（`bg.logistics.shipment.v2.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipment.v2.get` | [references/apis/bg-logistics-shipment-v2-get.md](references/apis/bg-logistics-shipment-v2-get.md) | `scripts/global_self_fulfilled_logistics_shipment_v2_get.py` | 查询发货信息 V2。 |
| 确认包裹已发货（`bg.logistics.shipped.package.confirm`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shipped.package.confirm` | [references/apis/bg-logistics-shipped-package-confirm.md](references/apis/bg-logistics-shipped-package-confirm.md) | `scripts/global_buy_shipping_logistics_shipped_package_confirm.py` | 确认包裹已发货。 |
| 查询可用物流渠道（`bg.logistics.shippingservices.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.shippingservices.get` | [references/apis/bg-logistics-shippingservices-get.md](references/apis/bg-logistics-shippingservices-get.md) | `scripts/global_buy_shipping_logistics_shippingservices_get.py` | 查询可用物流渠道。 |
| 店铺仓库列表（`bg.logistics.warehouse.list.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.logistics.warehouse.list.get` | [references/apis/bg-logistics-warehouse-list-get.md](references/apis/bg-logistics-warehouse-list-get.md) | `scripts/global_buy_shipping_logistics_warehouse_list_get.py` | 店铺仓库列表。 |
| 查询未发货包裹（`bg.order.unshipped.package.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`bg.order.unshipped.package.get` | [references/apis/bg-order-unshipped-package-get.md](references/apis/bg-order-unshipped-package-get.md) | `scripts/global_buy_shipping_order_unshipped_package_get.py` | 查询未发货包裹。 |
| 面单列表查询（`temu.logistics.label.list.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`temu.logistics.label.list.get` | [references/apis/temu-logistics-label-list-get.md](references/apis/temu-logistics-label-list-get.md) | `scripts/global_buy_shipping_logistics_label_list_get.py` | 面单列表查询。 |
| 在线发货物流类型（`temu.logistics.shiplogisticstype.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`temu.logistics.shiplogisticstype.get` | [references/apis/temu-logistics-shiplogisticstype-get.md](references/apis/temu-logistics-shiplogisticstype-get.md) | `scripts/global_buy_shipping_logistics_shiplogisticstype_get.py` | 在线发货物流类型。 |
| 取消上门揽收预约（`temu.logistics.shipment.pickup.reservation.cancel`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`temu.logistics.shipment.pickup.reservation.cancel` | [references/apis/temu-logistics-shipment-pickup-reservation-cancel.md](references/apis/temu-logistics-shipment-pickup-reservation-cancel.md) | `scripts/global_buy_shipping_logistics_shipment_pickup_reservation_cancel.py` | 取消上门揽收预约。 |
| 预约上门揽收（`temu.logistics.shipment.pickup.reservation.create`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`temu.logistics.shipment.pickup.reservation.create` | [references/apis/temu-logistics-shipment-pickup-reservation-create.md](references/apis/temu-logistics-shipment-pickup-reservation-create.md) | `scripts/global_buy_shipping_logistics_shipment_pickup_reservation_create.py` | 预约上门揽收。 |
| 查询上门揽收预约结果（`temu.logistics.shipment.pickup.reservation.result.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`temu.logistics.shipment.pickup.reservation.result.get` | [references/apis/temu-logistics-shipment-pickup-reservation-result-get.md](references/apis/temu-logistics-shipment-pickup-reservation-result-get.md) | `scripts/global_buy_shipping_logistics_shipment_pickup_reservation_result_get.py` | 查询上门揽收预约结果。 |
| 物流轨迹详情查询（`temu.track.trackinginfo.get`） | POST `/temu/proxy` -> path：`/temu-proxy/global/semi-managed`；type：`temu.track.trackinginfo.get` | [references/apis/temu-track-trackinginfo-get.md](references/apis/temu-track-trackinginfo-get.md) | `scripts/global_tracking_track_trackinginfo_get.py` | 物流轨迹详情查询。 |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md#接口加签文件下载) | `scripts/temu_global_file_download.py` | 获取加签面单文件；兼容 `scripts/temu_file_download.py`。 |

接口清单按转发操作计数，23 个业务 type 加 1 个文件下载接口；通用代理和认证探测复用上述端点，不重复计数。Partner 目录和官方地址见 [references/partner-global-catalog.md](references/partner-global-catalog.md)。

## 前置条件

**先确定店铺、区域与履约目标**：准备 LinkFox 用户密钥和对应区域的 Temu 店铺令牌。Temu 令牌须在卖家后台手动授权取得，两种令牌不可混淆；授权步骤、本地保存与脱敏查询见 [references/access-token.md](references/access-token.md) 和 [references/authorization-flow.md](references/authorization-flow.md)。
先取得待发货订单、包裹和实际尺寸重量；合作仓还需服务商提供的授权信息。各接口字段及限制见 [references/api.md](references/api.md) 与接口清单中的文档。

## 履约流程

1. **确定发货方式**：从订单技能取得待履约订单与业务上下文，选择购标、合作仓或卖家自发货流程，核对用户指定店铺和区域。
2. **购标与面单**：查询仓库及在线物流类型，按包裹条件查询可用渠道；提交购标后先查异步结果，再取面单并按需下载。延后发货或购标失败时，按接口定义准备更新或重试，随后核对购标结果。可查询面单列表与未发货包裹，再确认实际出库的包裹，最后刷新订单状态。
3. **揽收预约**：需要上门揽收时使用渠道提供的可用时段提交预约，再查询预约结果。用户要求取消时先核对预约，再取消并复核结果。
4. **合作仓**：查询服务商及许可状态，按授权方式完成绑定或准备直接授权资料，提交履约并保留 ERP 与合作仓履约号。取消已有履约时核对目标单号，随后通过订单或服务商复核。`bg.cooperativewarehouse.fulfill.query` 尚未在本技能定义，不将它作为已接入操作承诺执行。
5. **卖家自发货**：取得承运商和仓库，提交实际运单并确认发货；查询发货信息核对包裹。最小 SKU 拆包时按需追加子包裹；更正跟踪号或改为非集成物流后再次核对，最后刷新订单状态。
6. **物流跟进**：按包裹查询物流轨迹，结合订单状态说明当前进度。异步状态未完成时，仅在任务需要且遵守调用约束的范围内继续查询。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：脚本不读取或写入响应缓存。同一会话优先复用已保存结果；失败或空结果时，不得自动更换参数、翻页或连续试探。异步状态复核与必要的后续查询按履约目标进行，提交结果不确定时先查询，避免重复写入。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-fulfillment-global-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、响应体中存在的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分履约概念**：购标是创建包裹和面单，自发货是同步实际运单，合作仓履约还涉及服务商授权。提交受理、面单成功、预约成功和实际发货分别展示，不能相互替代。
- **清晰展示数据**：注明店铺、区域及查询时间；用表格列出包裹、父子订单、仓库、渠道、运单、状态与警告。运费注明响应币种，物流节点按返回时间展示，未知枚举保留原值。
- **保留业务警告**：逐包裹展示失败原因与警告；异步购标未成功时不承诺可打印面单或已发货。具体状态与时间门槛见接口定义。
- **遵循用户操作范围**：购标、确认发货、改跟踪号、合作仓提交/取消和预约/取消会影响业务，按用户已明确的目标准备资料。拒绝取消、拒绝改址或确认风险等事项须符合商家选择，不能自行勾选。
- **结果不确定时先核对**：提交超时或重复单提示后先查询已有结果，避免重复购标、重复履约或重复预约。参数互斥、拆包、COD、预售、合作仓与重试限制见各接口文档。
- **保护令牌**：使用本地令牌管理与通用代理 CLI；面向用户的结果不展示未脱敏密钥。认证与兼容约定统一见 [运行约定](references/api.md#运行约定)。

## 使用示例

### 购标并下载面单

用户：给全球站这批订单购标，下载可打印的面单。

核对订单、仓库和包裹资料，查询物流渠道并提交购标；核验结果后取面单，按需调用加签下载，展示包裹与面单对应关系。

### 合作仓履约

用户：把这些订单交给已授权的合作仓。

核对服务商、仓库和待履约商品，按授权方式准备资料后提交，记录履约号与状态，再结合订单信息复核。

### 自发货和物流跟进

用户：用我提供的运单号确认发货，再查包裹轨迹。

取得承运商和仓库，提交实际发货信息后查询核对，再展示包裹的物流节点和可用预警。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
