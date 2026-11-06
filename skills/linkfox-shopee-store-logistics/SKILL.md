---
name: linkfox-shopee-store-logistics
description: 管理已授权 Shopee（虾皮）店铺的物流履约，支持单笔与批量发货、Booking 发货、运单号和轨迹查询、面单生成与下载，以及地址、物流渠道、营业时段、包装、配送区域和暂停状态维护。适用于店铺发货、打印面单及物流跟踪；不适用于店铺授权、订单查询或取消拆单、退货退款、商品刊登、头程或仓储库存管理。
---
# Shopee 店铺物流管理

## 适用范围

### 适用

为已授权 Shopee 店铺完成物流发货、面单处理和物流配置维护。用户希望发货、查询运单或轨迹、打印面单时使用，无需明确提到“物流”。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 把这些待发货订单发出去 | 查询发货条件，按指定订单执行单笔或批量发货。 |
| 查运单号、揽收进度或物流轨迹 | 查询普通订单或 Booking 的运单与轨迹。 |
| 打印面单，下载批量面单结果 | 查询面单参数、生成结果或异步任务，再下载。 |
| 调整揽收地址、渠道或营业时间 | 查询现有配置，维护用户指定的物流设置。 |
| 查询包装、配送区域或暂停状态 | 处理 Mart 包装、配送区域和物流暂停设置。 |

### 边界

选店与授权使用 `linkfox-shopee-store-auth`；订单查询、取消与拆单使用 `linkfox-shopee-store-orders`。退货退款、店铺资料、商品刊登、FirstMile 头程、SBS 库存和 FBS 巴西仓储分别属于 `linkfox-shopee-store-returns`、`linkfox-shopee-store-shop`、`linkfox-shopee-store-product`、`linkfox-shopee-store-first-mile`、`linkfox-shopee-store-sbs`、`linkfox-shopee-store-fbs`。

## 接口清单

46 个物流操作及 1 个授权状态查询兼容操作；Feedback 不计入。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 获取发货参数（`get_shipping_parameter`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_shipping_parameter` | [references/apis/get-shipping-parameter.md](references/apis/get-shipping-parameter.md) | `scripts/get_shipping_parameter.py` | 获取发货参数。 |
| 获取批量发货参数（`get_mass_shipping_parameter`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/get_mass_shipping_parameter` | [references/apis/get-mass-shipping-parameter.md](references/apis/get-mass-shipping-parameter.md) | `scripts/get_mass_shipping_parameter.py` | 获取批量发货参数。 |
| 单订单发货（`ship_order`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/ship_order` | [references/apis/ship-order.md](references/apis/ship-order.md) | `scripts/ship_order.py` | 单订单发货。 |
| 批量发货（mass）（`mass_ship_order`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/mass_ship_order` | [references/apis/mass-ship-order.md](references/apis/mass-ship-order.md) | `scripts/mass_ship_order.py` | 批量发货（mass）。 |
| 更新已发货订单信息（`update_shipping_order`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/update_shipping_order` | [references/apis/update-shipping-order.md](references/apis/update-shipping-order.md) | `scripts/update_shipping_order.py` | 更新已发货订单信息。 |
| 获取运单号（`get_tracking_number`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_tracking_number` | [references/apis/get-tracking-number.md](references/apis/get-tracking-number.md) | `scripts/get_tracking_number.py` | 获取运单号。 |
| 批量获取运单号（`get_mass_tracking_number`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/get_mass_tracking_number` | [references/apis/get-mass-tracking-number.md](references/apis/get-mass-tracking-number.md) | `scripts/get_mass_tracking_number.py` | 批量获取运单号。 |
| 获取面单参数（`get_shipping_document_parameter`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_shipping_document_parameter` | [references/apis/get-shipping-document-parameter.md](references/apis/get-shipping-document-parameter.md) | `scripts/get_shipping_document_parameter.py` | 获取面单参数。 |
| 创建面单（`create_shipping_document`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/create_shipping_document` | [references/apis/create-shipping-document.md](references/apis/create-shipping-document.md) | `scripts/create_shipping_document.py` | 创建面单。 |
| 查询面单生成结果（`get_shipping_document_result`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_shipping_document_result` | [references/apis/get-shipping-document-result.md](references/apis/get-shipping-document-result.md) | `scripts/get_shipping_document_result.py` | 查询面单生成结果。 |
| 下载面单 PDF（`download_shipping_document`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/download_shipping_document` | [references/apis/download-shipping-document.md](references/apis/download-shipping-document.md) | `scripts/download_shipping_document.py` | 下载面单 PDF。 |
| 获取面单数据（`get_shipping_document_data_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_shipping_document_data_info` | [references/apis/get-shipping-document-data-info.md](references/apis/get-shipping-document-data-info.md) | `scripts/get_shipping_document_data_info.py` | 获取面单数据。 |
| 查询物流轨迹（`get_tracking_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_tracking_info` | [references/apis/get-tracking-info.md](references/apis/get-tracking-info.md) | `scripts/get_tracking_info.py` | 查询物流轨迹。 |
| 查询揽收与退货地址（`get_address_list`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_address_list` | [references/apis/get-address-list.md](references/apis/get-address-list.md) | `scripts/get_address_list.py` | 查询揽收与退货地址。 |
| 设置默认地址（`set_address_config`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/set_address_config` | [references/apis/set-address-config.md](references/apis/set-address-config.md) | `scripts/set_address_config.py` | 设置默认地址。 |
| 更新揽收与退货地址（`update_address`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/update_address` | [references/apis/update-address.md](references/apis/update-address.md) | `scripts/update_address.py` | 更新揽收与退货地址。 |
| 删除地址（`delete_address`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/delete_address` | [references/apis/delete-address.md](references/apis/delete-address.md) | `scripts/delete_address.py` | 删除地址。 |
| 查询物流渠道（`get_channel_list`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_channel_list` | [references/apis/get-channel-list.md](references/apis/get-channel-list.md) | `scripts/get_channel_list.py` | 查询物流渠道。 |
| 更新物流渠道设置（`update_channel`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/update_channel` | [references/apis/update-channel.md](references/apis/update-channel.md) | `scripts/update_channel.py` | 更新物流渠道设置。 |
| 查询揽收营业时段（`get_operating_hours`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_operating_hours` | [references/apis/get-operating-hours.md](references/apis/get-operating-hours.md) | `scripts/get_operating_hours.py` | 查询揽收营业时段。 |
| 查询营业时段限制（`get_operating_hour_restrictions`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_operating_hour_restrictions` | [references/apis/get-operating-hour-restrictions.md](references/apis/get-operating-hour-restrictions.md) | `scripts/get_operating_hour_restrictions.py` | 查询营业时段限制。 |
| 更新营业时段（`update_operating_hours`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/update_operating_hours` | [references/apis/update-operating-hours.md](references/apis/update-operating-hours.md) | `scripts/update_operating_hours.py` | 更新营业时段。 |
| 删除特殊营业时段（`delete_special_operating_hour`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/delete_special_operating_hour` | [references/apis/delete-special-operating-hour.md](references/apis/delete-special-operating-hour.md) | `scripts/delete_special_operating_hour.py` | 删除特殊营业时段。 |
| 批量更新 TPF 仓库物流状态（`batch_update_tpf_warehouse_tracking_status`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/batch_update_tpf_warehouse_tracking_status` | [references/apis/batch-update-tpf-warehouse-tracking-status.md](references/apis/batch-update-tpf-warehouse-tracking-status.md) | `scripts/batch_update_tpf_warehouse_tracking_status.py` | 批量更新 TPF 仓库物流状态。 |
| 批量发货（batch）（`batch_ship_order`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/batch_ship_order` | [references/apis/batch-ship-order.md](references/apis/batch-ship-order.md) | `scripts/batch_ship_order.py` | 批量发货（batch）。 |
| 更新物流状态（`update_tracking_status`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/update_tracking_status` | [references/apis/update-tracking-status.md](references/apis/update-tracking-status.md) | `scripts/update_tracking_status.py` | 更新物流状态。 |
| 获取 Booking 发货参数（`get_booking_shipping_parameter`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_booking_shipping_parameter` | [references/apis/get-booking-shipping-parameter.md](references/apis/get-booking-shipping-parameter.md) | `scripts/get_booking_shipping_parameter.py` | 获取 Booking 发货参数。 |
| Booking 发货（`ship_booking`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/ship_booking` | [references/apis/ship-booking.md](references/apis/ship-booking.md) | `scripts/ship_booking.py` | Booking 发货。 |
| 获取 Booking 运单号（`get_booking_tracking_number`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_booking_tracking_number` | [references/apis/get-booking-tracking-number.md](references/apis/get-booking-tracking-number.md) | `scripts/get_booking_tracking_number.py` | 获取 Booking 运单号。 |
| 获取 Booking 面单参数（`get_booking_shipping_document_parameter`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_booking_shipping_document_parameter` | [references/apis/get-booking-shipping-document-parameter.md](references/apis/get-booking-shipping-document-parameter.md) | `scripts/get_booking_shipping_document_parameter.py` | 获取 Booking 面单参数。 |
| 创建 Booking 面单（`create_booking_shipping_document`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/create_booking_shipping_document` | [references/apis/create-booking-shipping-document.md](references/apis/create-booking-shipping-document.md) | `scripts/create_booking_shipping_document.py` | 创建 Booking 面单。 |
| 查询 Booking 面单生成结果（`get_booking_shipping_document_result`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_booking_shipping_document_result` | [references/apis/get-booking-shipping-document-result.md](references/apis/get-booking-shipping-document-result.md) | `scripts/get_booking_shipping_document_result.py` | 查询 Booking 面单生成结果。 |
| 下载 Booking 面单（`download_booking_shipping_document`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/download_booking_shipping_document` | [references/apis/download-booking-shipping-document.md](references/apis/download-booking-shipping-document.md) | `scripts/download_booking_shipping_document.py` | 下载 Booking 面单。 |
| 获取 Booking 面单数据（`get_booking_shipping_document_data_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_booking_shipping_document_data_info` | [references/apis/get-booking-shipping-document-data-info.md](references/apis/get-booking-shipping-document-data-info.md) | `scripts/get_booking_shipping_document_data_info.py` | 获取 Booking 面单数据。 |
| 查询 Booking 物流轨迹（`get_booking_tracking_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_booking_tracking_info` | [references/apis/get-booking-tracking-info.md](references/apis/get-booking-tracking-info.md) | `scripts/get_booking_tracking_info.py` | 查询 Booking 物流轨迹。 |
| 下载 TO 标签（`download_to_label`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/download_to_label` | [references/apis/download-to-label.md](references/apis/download-to-label.md) | `scripts/download_to_label.py` | 下载 TO 标签。 |
| 创建异步面单任务（`create_shipping_document_job`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/create_shipping_document_job` | [references/apis/create-shipping-document-job.md](references/apis/create-shipping-document-job.md) | `scripts/create_shipping_document_job.py` | 创建异步面单任务。 |
| 查询异步面单任务状态（`get_shipping_document_job_status`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_shipping_document_job_status` | [references/apis/get-shipping-document-job-status.md](references/apis/get-shipping-document-job-status.md) | `scripts/get_shipping_document_job_status.py` | 查询异步面单任务状态。 |
| 下载异步面单任务结果（`download_shipping_document_job`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/download_shipping_document_job` | [references/apis/download-shipping-document-job.md](references/apis/download-shipping-document-job.md) | `scripts/download_shipping_document_job.py` | 下载异步面单任务结果。 |
| 更新自提订单物流（`update_self_collection_order_logistics`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/update_self_collection_order_logistics` | [references/apis/update-self-collection-order-logistics.md](references/apis/update-self-collection-order-logistics.md) | `scripts/update_self_collection_order_logistics.py` | 更新自提订单物流。 |
| 查询 Mart 包装信息（`get_mart_packaging_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_mart_packaging_info` | [references/apis/get-mart-packaging-info.md](references/apis/get-mart-packaging-info.md) | `scripts/get_mart_packaging_info.py` | 查询 Mart 包装信息。 |
| 设置 Mart 包装信息（`set_mart_packaging_info`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/set_mart_packaging_info` | [references/apis/set-mart-packaging-info.md](references/apis/set-mart-packaging-info.md) | `scripts/set_mart_packaging_info.py` | 设置 Mart 包装信息。 |
| 上传可配送区域多边形（`upload_serviceable_polygon`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/upload_serviceable_polygon` | [references/apis/upload-serviceable-polygon.md](references/apis/upload-serviceable-polygon.md) | `scripts/upload_serviceable_polygon.py` | 上传可配送区域多边形。 |
| 查询配送区域更新状态（`check_polygon_update_status`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/check_polygon_update_status` | [references/apis/check-polygon-update-status.md](references/apis/check-polygon-update-status.md) | `scripts/check_polygon_update_status.py` | 查询配送区域更新状态。 |
| 查询物流暂停状态（`get_pause_status`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/logistics/get_pause_status` | [references/apis/get-pause-status.md](references/apis/get-pause-status.md) | `scripts/get_pause_status.py` | 查询物流暂停状态。 |
| 设置物流暂停状态（`set_pause_status`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/logistics/set_pause_status` | [references/apis/set-pause-status.md](references/apis/set-pause-status.md) | `scripts/set_pause_status.py` | 设置物流暂停状态。 |
| 查询店铺授权状态（`storeTokens`） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_logistics_common.py` 中 `resolve_store_tokens` | 查询已有店铺授权状态，不返回原始令牌；日常物流脚本由代理服务端解析令牌。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店与授权。运行 `python scripts/check_auth_dependency.py` 检查安装情况；缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。依赖检测和认证兼容约定见 `references/api.md`。
确认用户指定的店铺、订单及需要执行的物流操作。所需字段和限制按接口清单读取对应文档。

## 物流履约流程

1. 通过订单技能取得待发货订单，核对目标店铺和订单状态。
2. 单订单先查询发货参数，再执行发货，随后获取运单号；批量任务先查询批量发货参数，再使用对应批量操作。Booking 使用独立的 Booking 发货与面单流程。
3. 打印面单时，先查询面单参数，再创建面单，按返回结果查询生成状态，准备好后下载；异步任务按“创建任务 → 查询状态 → 下载结果”执行。
4. 物流配置维护先读取现有配置，按用户指定范围提交修改，再解释实际返回结果；任务状态查询与后续操作遵守调用约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先复用已保存的数据；业务脚本不读写响应缓存。失败或空结果时，不得自动更换参数或连续试探；后续调用按用户任务范围执行，写入结果不确定时先核对状态。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-logistics-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、顶层常见计数（如 `total`、`costToken`，仅在实际存在时展示）、最大列表字段的长度和前 3 条样本。
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

- **转发与选店**：物流请求经 developerProxy、紫鸟 shopee-proxy 转发至 Shopee，由服务端解析已授权店铺令牌；通常使用店铺标识，不另行实现授权。
- **清晰展示数据**：注明店铺、订单或 Booking、包裹和操作，用表格展示运单号、轨迹、面单生成状态及配置变更结果；缺失值按实际返回说明。
- **区分物流流程**：普通订单、Booking、普通面单与异步面单任务分别使用对应操作，避免把批量接口或任务接口当成单笔接口。
- **保护店铺操作范围**：发货、更新物流、地址删除与配置修改会影响真实店铺；只处理用户指定目标。结果不确定时先解释已返回的信息，不盲目重复提交。
- **解释返回层级**：先判断网关，再判断 Shopee 上游状态与业务结果；发货请求完成、任务创建和最终面单可下载是不同结果。具体判断见对应接口文档。
- **保留原始数据**：下载类操作保留网关原始响应及内容类型；仅在返回内容可解析时展示结构化字段，不将非 JSON 面单内容误判为业务对象。

## 使用示例

### 单订单发货

用户：把这个待发货订单发出去，再给我运单号。

确认店铺与订单，查询发货参数，按实际揽收或寄件条件完成发货，再查询运单号，展示各步骤的实际结果。

### 打印普通面单或 Booking 面单

用户：下载这些订单的面单。

确认订单类型，读取对应面单参数并创建面单；根据生成状态下载，说明尚未就绪的订单和已取得的数据。

### 批量面单与物流配置

用户：查询这个面单任务的状态；把指定地址的营业时间更新为我提供的时段。

分别查询任务和现有营业配置，按用户明确的目标维护时段，展示任务状态与更新结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
