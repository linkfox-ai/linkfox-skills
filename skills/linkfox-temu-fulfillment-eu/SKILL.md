---
name: linkfox-temu-fulfillment-eu
description: 管理 Temu 欧洲站已授权店铺的购标、面单、Scan Form、上门揽收、合作仓履约、卖家自发货、物流跟踪及自配送 POD 上传与审核，支持下载加签文件。适用于欧洲站订单发货、出库核对和履约跟进；不适用于订单列表与地址查询、取消订单、商品库存管理、售后退款或其他站点履约。
---

# Temu 欧洲站履约与发货

## 适用范围

### 适用

管理已授权 Temu 欧洲站店铺的包裹、运单、面单、合作仓履约和签收凭证。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 给这些订单购标并下载面单 | 购标：选仓、查物流方案、下单、核对结果与取面单。 |
| 预约揽收或生成 Scan Form | 交运：按可用渠道与包裹状态处理揽收或扫描单。 |
| 用合作仓发货，查看或取消已提交的履约 | 合作仓：核对服务商授权并提交或取消履约。 |
| 我有运单号，需要自发货或更正物流 | 自发货：确认发货、追加子包裹或更新跟踪号。 |
| 查看包裹轨迹，或提交签收凭证 | 履约跟进：物流跟踪及 POD 签名、提交和审核查询。 |

### 边界

订单列表、详情、地址和状态复核使用 `linkfox-temu-order-eu`；取消订单使用 `linkfox-temu-cancel-order-eu`；商品库存使用 `linkfox-temu-manage-product-eu`；售后退款使用 `linkfox-temu-returns-refunds-eu`。美国站与全球站履约分别使用 `linkfox-temu-fulfillment-us`、`linkfox-temu-fulfillment-global`，全球站不含 Scan Form。

## 接口清单

共 30 个履约操作及 1 个加签文件下载接口。统一转发通过 `type` 识别操作，没有请求体 `path` 字段；网关与上游转发路径见 `references/api.md`。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 取消合作仓履约单（`bg.cooperativewarehouse.fulfill.cancel`） | POST `/temu/proxy` → type：`bg.cooperativewarehouse.fulfill.cancel` | `references/apis/bg-cooperativewarehouse-fulfill-cancel.md` | `scripts/eu_co_warehouse_cooperativewarehouse_fulfill_cancel.py` | 取消合作仓履约单。 |
| 提交合作仓履约（`bg.cooperativewarehouse.fulfill.submit`） | POST `/temu/proxy` → type：`bg.cooperativewarehouse.fulfill.submit` | `references/apis/bg-cooperativewarehouse-fulfill-submit.md` | `scripts/eu_co_warehouse_cooperativewarehouse_fulfill_submit.py` | 提交合作仓履约。 |
| 合作仓服务商列表（`bg.cooperativewarehouse.provider.list`） | POST `/temu/proxy` → type：`bg.cooperativewarehouse.provider.list` | `references/apis/bg-cooperativewarehouse-provider-list.md` | `scripts/eu_co_warehouse_cooperativewarehouse_provider_list.py` | 合作仓服务商列表。 |
| 合作仓 Token 授权（`bg.cooperativewarehouse.token.authorization`） | POST `/temu/proxy` → type：`bg.cooperativewarehouse.token.authorization` | `references/apis/bg-cooperativewarehouse-token-authorization.md` | `scripts/eu_co_warehouse_cooperativewarehouse_token_authorization.py` | 合作仓 Token 授权。 |
| 获取区域可用物流商（`bg.logistics.companies.get`） | POST `/temu/proxy` → type：`bg.logistics.companies.get` | `references/apis/bg-logistics-companies-get.md` | `scripts/eu_self_fulfilled_logistics_companies_get.py` | 获取区域可用物流商。 |
| 在线下单购标（`bg.logistics.shipment.create`） | POST `/temu/proxy` → type：`bg.logistics.shipment.create` | `references/apis/bg-logistics-shipment-create.md` | `scripts/eu_buy_shipping_logistics_shipment_create.py` | 在线下单购标。 |
| 获取面单/运单文档（`bg.logistics.shipment.document.get`） | POST `/temu/proxy` → type：`bg.logistics.shipment.document.get` | `references/apis/bg-logistics-shipment-document-get.md` | `scripts/eu_buy_shipping_logistics_shipment_document_get.py` | 获取面单/运单文档。 |
| 查询购标/在线下单结果（`bg.logistics.shipment.result.get`） | POST `/temu/proxy` → type：`bg.logistics.shipment.result.get` | `references/apis/bg-logistics-shipment-result-get.md` | `scripts/eu_buy_shipping_logistics_shipment_result_get.py` | 查询购标/在线下单结果。 |
| 更新物流跟踪号 / 发货方式（`bg.logistics.shipment.shippingtype.update`） | POST `/temu/proxy` → type：`bg.logistics.shipment.shippingtype.update` | `references/apis/bg-logistics-shipment-shippingtype-update.md` | `scripts/eu_self_fulfilled_logistics_shipment_shippingtype_update.py` | 更新物流跟踪号 / 发货方式。 |
| 确认子包裹发货（`bg.logistics.shipment.sub.confirm`） | POST `/temu/proxy` → type：`bg.logistics.shipment.sub.confirm` | `references/apis/bg-logistics-shipment-sub-confirm.md` | `scripts/eu_self_fulfilled_logistics_shipment_sub_confirm.py` | 确认子包裹发货。 |
| 更新发货/重试购标（`bg.logistics.shipment.update`） | POST `/temu/proxy` → type：`bg.logistics.shipment.update` | `references/apis/bg-logistics-shipment-update.md` | `scripts/eu_buy_shipping_logistics_shipment_update.py` | 更新发货/重试购标。 |
| 确认发货 V2（`bg.logistics.shipment.v2.confirm`） | POST `/temu/proxy` → type：`bg.logistics.shipment.v2.confirm` | `references/apis/bg-logistics-shipment-v2-confirm.md` | `scripts/eu_self_fulfilled_logistics_shipment_v2_confirm.py` | 确认发货 V2。 |
| 查询发货信息 V2（`bg.logistics.shipment.v2.get`） | POST `/temu/proxy` → type：`bg.logistics.shipment.v2.get` | `references/apis/bg-logistics-shipment-v2-get.md` | `scripts/eu_self_fulfilled_logistics_shipment_v2_get.py` | 查询发货信息 V2。 |
| 确认包裹已发货（`bg.logistics.shipped.package.confirm`） | POST `/temu/proxy` → type：`bg.logistics.shipped.package.confirm` | `references/apis/bg-logistics-shipped-package-confirm.md` | `scripts/eu_buy_shipping_logistics_shipped_package_confirm.py` | 确认包裹已发货。 |
| 查询可用物流渠道（`bg.logistics.shippingservices.get`） | POST `/temu/proxy` → type：`bg.logistics.shippingservices.get` | `references/apis/bg-logistics-shippingservices-get.md` | `scripts/eu_buy_shipping_logistics_shippingservices_get.py` | 查询可用物流渠道。 |
| 店铺仓库列表（`bg.logistics.warehouse.list.get`） | POST `/temu/proxy` → type：`bg.logistics.warehouse.list.get` | `references/apis/bg-logistics-warehouse-list-get.md` | `scripts/eu_buy_shipping_logistics_warehouse_list_get.py` | 店铺仓库列表。 |
| 查询未发货包裹（`bg.order.unshipped.package.get`） | POST `/temu/proxy` → type：`bg.order.unshipped.package.get` | `references/apis/bg-order-unshipped-package-get.md` | `scripts/eu_buy_shipping_order_unshipped_package_get.py` | 查询未发货包裹。 |
| 候选 Scan Form 包裹列表（`temu.logistics.candidate.scanform.list.get`） | POST `/temu/proxy` → type：`temu.logistics.candidate.scanform.list.get` | `references/apis/temu-logistics-candidate-scanform-list-get.md` | `scripts/eu_buy_shipping_logistics_candidate_scanform_list_get.py` | 候选 Scan Form 包裹列表。 |
| 面单列表查询（`temu.logistics.label.list.get`） | POST `/temu/proxy` → type：`temu.logistics.label.list.get` | `references/apis/temu-logistics-label-list-get.md` | `scripts/eu_buy_shipping_logistics_label_list_get.py` | 面单列表查询。 |
| 创建 Scan Form（`temu.logistics.scanform.create`） | POST `/temu/proxy` → type：`temu.logistics.scanform.create` | `references/apis/temu-logistics-scanform-create.md` | `scripts/eu_buy_shipping_logistics_scanform_create.py` | 创建 Scan Form。 |
| 获取 Scan Form 文档（`temu.logistics.scanform.document.get`） | POST `/temu/proxy` → type：`temu.logistics.scanform.document.get` | `references/apis/temu-logistics-scanform-document-get.md` | `scripts/eu_buy_shipping_logistics_scanform_document_get.py` | 获取 Scan Form 文档。 |
| 查询 Scan Form 详情（`temu.logistics.scanform.get`） | POST `/temu/proxy` → type：`temu.logistics.scanform.get` | `references/apis/temu-logistics-scanform-get.md` | `scripts/eu_buy_shipping_logistics_scanform_get.py` | 查询 Scan Form 详情。 |
| 自配送 POD 审核结果查询（`temu.logistics.self.delivery.pod.audit.result.get`） | POST `/temu/proxy` → type：`temu.logistics.self.delivery.pod.audit.result.get` | `references/apis/temu-logistics-self-delivery-pod-audit-result-get.md` | `scripts/eu_self_fulfilled_logistics_self_delivery_pod_audit_result_get.py` | 自配送 POD 审核结果查询。 |
| 自配送 POD 上传签名查询（`temu.logistics.self.delivery.pod.upload.signature.query`） | POST `/temu/proxy` → type：`temu.logistics.self.delivery.pod.upload.signature.query` | `references/apis/temu-logistics-self-delivery-pod-upload-signature-query.md` | `scripts/eu_self_fulfilled_logistics_self_delivery_pod_upload_signature_query.py` | 自配送 POD 上传签名查询。 |
| 自配送 POD 上传（`temu.logistics.self.delivery.pod.upload`） | POST `/temu/proxy` → type：`temu.logistics.self.delivery.pod.upload` | `references/apis/temu-logistics-self-delivery-pod-upload.md` | `scripts/eu_self_fulfilled_logistics_self_delivery_pod_upload.py` | 自配送 POD 上传。 |
| 在线发货物流类型（`temu.logistics.shiplogisticstype.get`） | POST `/temu/proxy` → type：`temu.logistics.shiplogisticstype.get` | `references/apis/temu-logistics-shiplogisticstype-get.md` | `scripts/eu_buy_shipping_logistics_shiplogisticstype_get.py` | 在线发货物流类型。 |
| 取消上门揽收预约（`temu.logistics.shipment.pickup.reservation.cancel`） | POST `/temu/proxy` → type：`temu.logistics.shipment.pickup.reservation.cancel` | `references/apis/temu-logistics-shipment-pickup-reservation-cancel.md` | `scripts/eu_buy_shipping_logistics_shipment_pickup_reservation_cancel.py` | 取消上门揽收预约。 |
| 预约上门揽收（`temu.logistics.shipment.pickup.reservation.create`） | POST `/temu/proxy` → type：`temu.logistics.shipment.pickup.reservation.create` | `references/apis/temu-logistics-shipment-pickup-reservation-create.md` | `scripts/eu_buy_shipping_logistics_shipment_pickup_reservation_create.py` | 预约上门揽收。 |
| 查询上门揽收预约结果（`temu.logistics.shipment.pickup.reservation.result.get`） | POST `/temu/proxy` → type：`temu.logistics.shipment.pickup.reservation.result.get` | `references/apis/temu-logistics-shipment-pickup-reservation-result-get.md` | `scripts/eu_buy_shipping_logistics_shipment_pickup_reservation_result_get.py` | 查询上门揽收预约结果。 |
| 物流轨迹详情查询（`temu.track.trackinginfo.get`） | POST `/temu/proxy` → type：`temu.track.trackinginfo.get` | `references/apis/temu-track-trackinginfo-get.md` | `scripts/eu_tracking_track_trackinginfo_get.py` | 物流轨迹详情查询。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/apis/file-download.md` | `scripts/temu_eu_file_download.py` | 下载面单或 Scan Form 加签文件。 |

## 前置条件

确认目标店铺、订单或包裹及用户要求的操作范围。准备 LinkFox API Key 与 Temu 店铺令牌；两者属于不同认证体系。Temu 令牌需从卖家后台手动取得，可直接使用或保存在本地供选店读取。授权步骤见 `references/access-token.md` 和 `references/authorization-flow.md`，认证兼容及脚本约定见 `references/api.md`。

## 履约流程

1. **购标与交运**：从订单技能取得待发父子订单、数量和购标时机 → 筛选购标可用仓库，查询物流类型与渠道报价 → 创建购标包裹并记录包裹号 → 按需使用报价返回的可选时段预约揽收，查询预约单号与结果；取消预约后再次查询核对状态 → 查询购标结果，必要时按失败原因调整延后发货时限，或重新选渠道并重试失败包裹，随后复核结果 → 按需查询 Scan Form 候选分组、选取一组创建并核对扫描单，再获取文档 → 核对面单状态和可打印时间，获取面单并下载、打印 → 查询面单列表和待确认包裹，核对包裹、运单与商品数量后确认发货 → 回订单技能复核状态。每一步遵守对应接口的前提与限制，异步查询按任务范围与成本约束执行。
2. **合作仓履约**：取得待履约订单 → 查询服务商、仓库和许可状态 → 按所选授权方式完成服务商授权 → 提交履约并记录 ERP 与合作仓履约单号 → 按用户要求使用对应 ERP 履约单号取消履约 → 结合轨迹和订单状态核对结果。专用 `fulfill.query` 尚未接入，不能声称已取得该查询结果。
3. **卖家自发货**：取得卖家履约订单 → 查询并选择承运商与仓库 → 提交运单并确认发货 → 按父子订单查询发货信息，核对运单、包裹和预警，拆包时同时查看子包裹信息 → 按需追加同一最小 SKU 的子包裹，或更正运单及发货方式，再查询核对 → 回订单技能复核订单状态。已有包裹需要跟进时，查询物流轨迹并结合订单状态说明进展。
4. **自配送 POD**：从订单上下文确认目标包裹 → 获取上传签名 → 将凭证图片上传到 Temu 存储并取得文件 URL → 按包裹提交 POD → 使用返回的申请单号查询审核状态与拒绝原因 → 结合订单状态完成核对。获取签名不等于已上传文件，提交凭证也不等于审核通过。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；业务脚本不使用响应缓存，每次执行均会请求网关。失败或空结果时，先核对参数、业务错误和已保存响应，避免连续试探；写入结果不确定时先查询状态，避免重复提交。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-fulfillment-eu-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分履约方式**：购标使用 Temu 集成物流，自发货使用卖家自己的运单；合作仓另需服务商授权。POD 是签收凭证，不是面单。
- **核对变更范围**：购标、预约、授权、发货确认、取消和 POD 提交会改变业务状态；按用户明确的店铺和包裹范围执行，结果不确定时先核对状态，避免重复提交。
- **展示关键结果**：注明店铺与欧洲站，用表格展示订单、包裹、运单、承运商、面单或文档链接及当前状态；报价同时标注响应币种，警告与失败原因逐项保留。
- **区分处理阶段**：分别说明网关响应、Temu 受理、购标成功、发货生效和 POD 审核结果。按实际轨迹时间与语言展示节点，不推断未返回的状态或枚举。
- **保留原始数据**：先看摘要，按需读取落盘文件。接口参数、时间窗、批量上限、渠道适用性、Scan Form 条件与错误处理均以 `references/apis/` 的对应定义为准。
- **按需查阅目录**：Partner 官方目录、已知子菜单编号和尚未接入能力见 `references/partner-eu-catalog.md`；通用代理不意味着这些能力已拥有完整专用定义。

## 使用示例

### 购标并下载面单

用户：为指定订单选择合适渠道并购标，下载可以打印的面单。

确认订单与仓库，查询可用方案后按用户选择购标，核对异步结果及打印条件，再取文档并下载，展示包裹、运单和保存位置。

### 使用自己的运单发货

用户：用提供的运单号确认这些订单发货。

核对承运商、仓库与订单商品数量，确认发货后读取发货信息并复核订单，说明平台状态与警告。

### 合作仓履约或 POD 跟进

用户：提交这些订单给合作仓；或查看这些签收凭证的审核进度。

按对应流程核对服务商授权或申请单，展示实际受理结果与后续可核验状态。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
