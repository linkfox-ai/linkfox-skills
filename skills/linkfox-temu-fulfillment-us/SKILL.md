---
name: linkfox-temu-fulfillment-us
description: 管理 Temu 美国站店铺的发货与物流履约，支持在线购标、面单、Scan Form、揽收预约、合作仓履约、卖家自发货、运单更正及轨迹查询。适用于已授权店铺的包裹发货、出库交运和履约状态核对；不适用于商品库存维护、退货退款、订单取消或其他站点的履约。
---
# Temu 美国站发货与物流履约

## 适用范围

### 适用

处理美国站店铺的 Buy-Shipping、合作仓、卖家自发货及物流跟踪，覆盖 27 个履约操作和加签文件下载。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查可用物流渠道、买面单或打印面单 | 在线购标、购标结果和文档获取。 |
| 为这批包裹生成 Scan Form、安排揽收 | 候选分组、扫描单与上门揽收。 |
| 让合作仓发货或取消履约 | 服务商选择、授权、提交和取消合作仓履约。 |
| 已有运单号，回传发货或更正跟踪号 | 卖家自发货、子包裹及发货方式更新。 |
| 查包裹最新物流轨迹 | 包裹跟踪号和物流节点查询。 |

### 边界

订单列表、详情及地址交给 `linkfox-temu-order-us`；订单取消交给 `linkfox-temu-cancel-order-us`；商品库存交给 `linkfox-temu-manage-product-us`；退货退款交给 `linkfox-temu-returns-refunds-us`。其他站点使用相应站点的履约技能，全球站没有本技能的 Scan Form 能力。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 取消合作仓履约单 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.cooperativewarehouse.fulfill.cancel` | `references/apis/bg-cooperativewarehouse-fulfill-cancel.md` | `scripts/us_co_warehouse_cooperativewarehouse_fulfill_cancel.py` | 美国站履约操作。 |
| 提交合作仓履约 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.cooperativewarehouse.fulfill.submit` | `references/apis/bg-cooperativewarehouse-fulfill-submit.md` | `scripts/us_co_warehouse_cooperativewarehouse_fulfill_submit.py` | 美国站履约操作。 |
| 合作仓服务商列表 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.cooperativewarehouse.provider.list` | `references/apis/bg-cooperativewarehouse-provider-list.md` | `scripts/us_co_warehouse_cooperativewarehouse_provider_list.py` | 美国站履约操作。 |
| 合作仓 Token 授权 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.cooperativewarehouse.token.authorization` | `references/apis/bg-cooperativewarehouse-token-authorization.md` | `scripts/us_co_warehouse_cooperativewarehouse_token_authorization.py` | 美国站履约操作。 |
| 获取区域可用物流商 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.companies.get` | `references/apis/bg-logistics-companies-get.md` | `scripts/us_self_fulfilled_logistics_companies_get.py` | 美国站履约操作。 |
| 在线下单购标 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipment.create` | `references/apis/bg-logistics-shipment-create.md` | `scripts/us_buy_shipping_logistics_shipment_create.py` | 美国站履约操作。 |
| 获取面单/运单文档 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipment.document.get` | `references/apis/bg-logistics-shipment-document-get.md` | `scripts/us_buy_shipping_logistics_shipment_document_get.py` | 美国站履约操作。 |
| 查询购标/在线下单结果 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipment.result.get` | `references/apis/bg-logistics-shipment-result-get.md` | `scripts/us_buy_shipping_logistics_shipment_result_get.py` | 美国站履约操作。 |
| 更新物流跟踪号 / 发货方式 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipment.shippingtype.update` | `references/apis/bg-logistics-shipment-shippingtype-update.md` | `scripts/us_self_fulfilled_logistics_shipment_shippingtype_update.py` | 美国站履约操作。 |
| 确认子包裹发货 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipment.sub.confirm` | `references/apis/bg-logistics-shipment-sub-confirm.md` | `scripts/us_self_fulfilled_logistics_shipment_sub_confirm.py` | 美国站履约操作。 |
| 更新发货/重试购标 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipment.update` | `references/apis/bg-logistics-shipment-update.md` | `scripts/us_buy_shipping_logistics_shipment_update.py` | 美国站履约操作。 |
| 确认发货 V2 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipment.v2.confirm` | `references/apis/bg-logistics-shipment-v2-confirm.md` | `scripts/us_self_fulfilled_logistics_shipment_v2_confirm.py` | 美国站履约操作。 |
| 查询发货信息 V2 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipment.v2.get` | `references/apis/bg-logistics-shipment-v2-get.md` | `scripts/us_self_fulfilled_logistics_shipment_v2_get.py` | 美国站履约操作。 |
| 确认包裹已发货 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shipped.package.confirm` | `references/apis/bg-logistics-shipped-package-confirm.md` | `scripts/us_buy_shipping_logistics_shipped_package_confirm.py` | 美国站履约操作。 |
| 查询可用物流渠道 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.shippingservices.get` | `references/apis/bg-logistics-shippingservices-get.md` | `scripts/us_buy_shipping_logistics_shippingservices_get.py` | 美国站履约操作。 |
| 店铺仓库列表 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.logistics.warehouse.list.get` | `references/apis/bg-logistics-warehouse-list-get.md` | `scripts/us_buy_shipping_logistics_warehouse_list_get.py` | 美国站履约操作。 |
| 查询未发货包裹 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`bg.order.unshipped.package.get` | `references/apis/bg-order-unshipped-package-get.md` | `scripts/us_buy_shipping_order_unshipped_package_get.py` | 美国站履约操作。 |
| 候选 Scan Form 包裹列表 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.candidate.scanform.list.get` | `references/apis/temu-logistics-candidate-scanform-list-get.md` | `scripts/us_buy_shipping_logistics_candidate_scanform_list_get.py` | 美国站履约操作。 |
| 面单列表查询 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.label.list.get` | `references/apis/temu-logistics-label-list-get.md` | `scripts/us_buy_shipping_logistics_label_list_get.py` | 美国站履约操作。 |
| 创建 Scan Form | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.scanform.create` | `references/apis/temu-logistics-scanform-create.md` | `scripts/us_buy_shipping_logistics_scanform_create.py` | 美国站履约操作。 |
| 获取 Scan Form 文档 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.scanform.document.get` | `references/apis/temu-logistics-scanform-document-get.md` | `scripts/us_buy_shipping_logistics_scanform_document_get.py` | 美国站履约操作。 |
| 查询 Scan Form 详情 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.scanform.get` | `references/apis/temu-logistics-scanform-get.md` | `scripts/us_buy_shipping_logistics_scanform_get.py` | 美国站履约操作。 |
| 在线发货物流类型 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.shiplogisticstype.get` | `references/apis/temu-logistics-shiplogisticstype-get.md` | `scripts/us_buy_shipping_logistics_shiplogisticstype_get.py` | 美国站履约操作。 |
| 取消上门揽收预约 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.shipment.pickup.reservation.cancel` | `references/apis/temu-logistics-shipment-pickup-reservation-cancel.md` | `scripts/us_buy_shipping_logistics_shipment_pickup_reservation_cancel.py` | 美国站履约操作。 |
| 预约上门揽收 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.shipment.pickup.reservation.create` | `references/apis/temu-logistics-shipment-pickup-reservation-create.md` | `scripts/us_buy_shipping_logistics_shipment_pickup_reservation_create.py` | 美国站履约操作。 |
| 查询上门揽收预约结果 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.logistics.shipment.pickup.reservation.result.get` | `references/apis/temu-logistics-shipment-pickup-reservation-result-get.md` | `scripts/us_buy_shipping_logistics_shipment_pickup_reservation_result_get.py` | 美国站履约操作。 |
| 物流轨迹详情查询 | POST `/temu/proxy` → 上游 path：`/openapi/router`；type：`temu.track.trackinginfo.get` | `references/apis/temu-track-trackinginfo-get.md` | `scripts/us_tracking_track_trackinginfo_get.py` | 美国站履约操作。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_us_file_download.py` | 下载面单或 Scan Form 的加签资源。 |

完整 Partner 目录、文档标识及待接入操作见 `references/partner-us-catalog.md`；分类导航见 `references/apis/README.md`。`scripts/temu_us_proxy.py` 是已有操作的通用代理入口，不另计接口。

## 前置条件

先确定用户授权的店铺和包裹。LinkFox 用户密钥与 Temu 店铺令牌分别准备，不能互换。Temu 令牌需在卖家后台手动授权复制；本地保存、脱敏列出与读取脚本见 `references/access-token.md`，没有自动 OAuth。主账号权限、分站授权、有效期和 IP 白名单要求见该文档。

## 履约流程

1. 确认美国站店铺和所需履约方式，先通过 `linkfox-temu-order-us` 查询待发货订单、地址、数量、履约方式及可操作时间，再读取本次操作的接口文档。通过本地令牌辅助脚本准备授权；令牌获取步骤见 `references/access-token.md` 与 `references/authorization-flow.md`。
2. **在线购标（Buy-Shipping）**：查询仓库 → 查询在线物流类型 → 按实际包裹查可用渠道与估价 → 创建物流单并保留包裹号 → 查询购标结果。根据任务需要，预约、查询或取消揽收；购标失败时先查状态，再按允许范围更新或重试。购标成功后获取面单；USPS 需要 manifestation 时，查询候选包裹分组 → 创建 Scan Form → 查询状态 → 获取 Scan Form 文档，再获取可打印面单。按需查询面单列表及已购标待确认包裹，核对可发货与已取消商品行后确认发货，最后刷新订单状态。
3. **合作仓（Co-Warehouse）**：查询合作仓服务商与授权许可 → 按所选授权方式准备凭证或完成绑定 → 提交履约并保存 ERP 和合作仓单号 → 按用户要求取消指定履约单 → 在卖家中心或订单状态中复核。合作仓履约查询和 SKU 关系操作仍为待接入，不能将其当成已提供的专用能力。
4. **卖家自发货（Self-Fulfilled）**：查询订单并确认卖家履约 → 查询承运商和仓库 → 提交主包裹发货信息 → 查询发货结果。最小 SKU 必须拆包时追加子包裹；更正跟踪号或集成改非集成时先取得承运商信息，再更新并查询核对，最后刷新订单状态。
5. **物流跟踪与文件**：以真实返回的包裹号查询轨迹；以文档接口返回的链接进行加签下载。完整处理顺序、字段限制、异步状态及错误恢复条件见对应接口文档；继续查询和重试遵守调用约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，业务脚本不使用响应缓存。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续查询时，先说明目的与范围。写操作结果不明确时先查状态，避免重复提交。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-fulfillment-us-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
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

- **缓存行为**：业务脚本始终禁用响应缓存。重复执行会重新请求，不能依赖缓存避免重复写入。详见 `references/api.md` 的运行约定。
- **区分履约方式**：购标、合作仓和卖家自发货使用各自流程；提交前核对订单、包裹、仓库、承运商、数量和目的地区域。
- **区分受理与最终状态**：保留包裹号、ERP 履约单号、预约号和 Scan Form 编号；异步操作按返回状态复核，结果不明确时先查询，避免重复购标、预约或确认发货。
- **展示完整业务结果**：注明店铺和站点，用表格展示包裹、运单、仓库、承运商、当前状态、警告与失败原因；金额注明实际币种，物流轨迹按时间展示。不要补造未知状态枚举。
- **处理异常与写入**：商家明确选择继续履约时才准备拒绝取消、拒绝改址或风险确认事项。写入根据用户已授权范围进行；有警告、售后、取消或风控事项时解释影响，保留已有数据。
- **说明返回范围**：列表展示本次筛选、分页及是否仍有数据；接口限制与恢复要求以 `references/api.md` 和对应接口文档为准。
- **认证与范围**：订单发货令牌与商品库存令牌用途不同。通用脚本提供兼容入口，使用时仍按本技能的美国站业务范围选店。

## 使用示例

### 在线购标并取得面单

用户：为这些美国站订单选择物流并购买面单。

先核对订单和包裹实测信息，查询仓库及渠道后按用户选择购标，查询实际购标结果；满足打印条件后获取面单，需要 Scan Form 时完成相应步骤，展示运单和警告。

### 合作仓履约

用户：将这些订单交给指定合作仓履约。

核对服务商和授权状态，准备合作仓及订单明细，提交后保存返回单号并复核状态；取消时定位用户指定的履约单。

### 卖家已有运单号

用户：回传这些包裹的承运商和运单号。

查询承运商与仓库，匹配订单商品数量后确认发货，再查询发货信息核对；需要拆包或更正跟踪号时使用对应操作。

### 查询轨迹与揽收

用户：检查这些包裹的揽收和物流进展。

读取预约结果与物流轨迹，区分处理中、失败和已完成，按包裹展示状态；不会因缺少轨迹自动创建新的预约。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
