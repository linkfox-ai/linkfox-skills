---
name: linkfox-temu-order-us
description: 管理 Temu 美国站已授权店铺的订单，支持订单列表与详情、收货地址及解密信息、供货价与金额、可合并发货订单组、定制商品内容查询，以及 SN、IMEI 和二手鉴真信息上传与授权文件获取。适用于美国站订单处理、ERP 对账和发货准备；不适用于欧洲或全球站订单、商品与价格管理、取消订单、退货退款及履约发货操作。
---
# Temu 美国站订单管理

## 适用范围

### 适用

查询和处理 Temu 美国站店铺订单，准备对账、定制生产和发货所需资料。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查看待发货、逾期或某段时间内的订单 | 订单列表及分页查询。 |
| 查看这个订单的子单和履约提示 | 订单详情查询。 |
| 读取收货地址或解密地址 | 常规地址与敏感地址查询。 |
| 核对订单供货价、运费和预估收入 | 金额查询与 ERP 对账。 |
| 哪些订单可以合并发货 | 查询可合并的父订单组。 |
| 取得定制文字、图片和 SVG 文件 | 子订单定制内容与授权资源获取。 |
| 上传商品 SN、IMEI 或二手鉴真编码 | 订单核验资料上传。 |

### 边界

欧洲站与全球站订单分别转交 `linkfox-temu-order-eu`、`linkfox-temu-order-global`；商品管理、发品、价格分别使用 `linkfox-temu-manage-product-us`、`linkfox-temu-add-product-us`、`linkfox-temu-price-us`。取消、退货退款、履约发货分别使用 `linkfox-temu-cancel-order-us`、`linkfox-temu-returns-refunds-us`、`linkfox-temu-fulfillment-us`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 订单金额/供货价查询（`bg.order.amount.query`） | POST `/temu/proxy` → 转发 type：`bg.order.amount.query`（上游 path：`/openapi/router`） | [references/apis/bg-order-amount-query.md](references/apis/bg-order-amount-query.md) | `scripts/us_order_amount_query.py` | 为自研 ERP 查询订单供货价和金额信息。 |
| 可合并发货订单组列表（`bg.order.combinedshipment.list.get`） | POST `/temu/proxy` → 转发 type：`bg.order.combinedshipment.list.get`（上游 path：`/openapi/router`） | [references/apis/bg-order-combinedshipment-list-get.md](references/apis/bg-order-combinedshipment-list-get.md) | `scripts/us_order_combinedshipment_list_get.py` | 查询可合并发货订单组，每组列出可合并发货的父订单。 |
| 订单定制商品内容批量查询（`bg.order.customization.get`） | POST `/temu/proxy` → 转发 type：`bg.order.customization.get`（上游 path：`/openapi/router`） | [references/apis/bg-order-customization-get.md](references/apis/bg-order-customization-get.md) | `scripts/us_order_customization_get.py` | 供自研卖家和第三方 ISV 批量读取子订单的定制商品内容。 |
| 订单收货地址解密查询（`bg.order.decryptshippinginfo.get`） | POST `/temu/proxy` → 转发 type：`bg.order.decryptshippinginfo.get`（上游 path：`/openapi/router`） | [references/apis/bg-order-decryptshippinginfo-get.md](references/apis/bg-order-decryptshippinginfo-get.md) | `scripts/us_order_decryptshippinginfo_get.py` | 查询指定父订单的敏感收货信息，包括解密后的姓名、电话与详细地址。 |
| 订单详情查询 V2（`bg.order.detail.v2.get`） | POST `/temu/proxy` → 转发 type：`bg.order.detail.v2.get`（上游 path：`/openapi/router`） | [references/apis/bg-order-detail-v2-get.md](references/apis/bg-order-detail-v2-get.md) | `scripts/us_order_detail_v2_get.py` | 读取当前店铺指定父订单及其子订单的完整详情。 |
| 订单列表查询 V2（`bg.order.list.v2.get`） | POST `/temu/proxy` → 转发 type：`bg.order.list.v2.get`（上游 path：`/openapi/router`） | [references/apis/bg-order-list-v2-get.md](references/apis/bg-order-list-v2-get.md) | `scripts/us_order_list_v2_get.py` | 按筛选条件批量查询当前店铺的订单列表。 |
| 订单收货地址查询 V2（`bg.order.shippinginfo.v2.get`） | POST `/temu/proxy` → 转发 type：`bg.order.shippinginfo.v2.get`（上游 path：`/openapi/router`） | [references/apis/bg-order-shippinginfo-v2-get.md](references/apis/bg-order-shippinginfo-v2-get.md) | `scripts/us_order_shippinginfo_v2_get.py` | 查询指定父订单的常规收货地址及地址返回限制提示。 |
| 订单核验信息上传（`temu.local.order.verification.upload`） | POST `/temu/proxy` → 转发 type：`temu.local.order.verification.upload`（上游 path：`/openapi/router`） | [references/apis/temu-local-order-verification-upload.md](references/apis/temu-local-order-verification-upload.md) | `scripts/us_order_verification_upload.py` | 上传高价值商品的 SN / IMEI，或二手商品的鉴真信息。 |
| 加签文件下载 | POST `/temu/fileDownload` → 目标 `url` | [references/api.md](references/api.md#接口加签文件下载) | `scripts/temu_us_file_download.py` | 获取授权文件资源。 |

## 前置条件

先确定美国站目标店铺和订单任务，准备 LinkFox 用户密钥及对应店铺的 Temu 授权。Temu 授权须在卖家后台手动完成；授权步骤与本地令牌脚本见 [access-token.md](references/access-token.md) 和 [authorization-flow.md](references/authorization-flow.md)。

## 订单处理流程

1. 按用户指定的状态、时间或父订单范围读取列表，再按需查询父单与子单详情；已有指定订单时可直接查询详情。
2. 发货准备时读取常规收货地址与限制提示；确需明文时查询解密地址。ERP 对账时读取金额，与详情中的子单号对齐。
3. 合并发货任务先查询父订单组，再按组内父单读取地址。合并确认、面单和实际发货交由履约技能。
4. 定制任务使用已有子订单号；缺少时可从订单列表或详情取得，再查询定制文字、预览图与 SVG 资源，按接口参考的下载要求及时获取文件。
5. 上传核验资料前从订单详情核对需提交的 SN、IMEI 或二手鉴真类型及履约提示；按用户指定内容上传，说明业务结果，再交由履约流程继续。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，本技能封装始终禁用响应缓存，应复用已保存的响应。失败或空结果时，不得自动翻页或修改筛选条件连续试探；需要继续查询时，先向用户说明原因和查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-order-us-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、可用的常见计数与状态字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分父单与子单**：`parentOrderSn` 用于父订单查询与关联，`orderSn` 用于定制与核验资料，不混用两种编号。
- **清晰展示订单**：注明店铺、美国站、本次筛选与返回范围，以父单和子单表格展示订单状态、待履约数量、时间、标签和履约提示。概念、枚举及适用卖家类型见对应接口参考。
- **对账与金额**：保留币种并区分供货价、零售价、折扣、税费和预估收入，按接口定义转换金额单位，与详情子单对齐；不将预估收入当作最终结算。
- **敏感信息**：姓名、电话、完整地址等按任务需要存储与展示，不写入普通日志或公开渠道；保存的完整响应亦需妥善管理。
- **履约与资源**：地址限制、主站合并标记、物流商限制、自提和鉴定报告提示均需传递到后续履约流程。定制内容按返回类型展示，纯文本与预览项文字区分呈现；下载有效期及签名规则见接口参考。
- **解释执行结果**：区分网关响应与 Temu 业务结果，说明空列表和错误原因，保留已取得的数据；核验上传会改变店铺订单资料，结果不确定时先核对，避免重复提交。
- **认证与运行兼容**：业务封装不读写响应缓存，公共调用器可能创建空缓存目录。实际参数、限制、CLI 与认证优先级见 [api.md](references/api.md#脚本运行约定)。
- **维护接口目录**：新增操作时须以用户提供的 Partner 文档为依据，保留完整字段层级，并同步接口参考、薄封装、[接口目录](references/partner-us-catalog.md) 与本清单；不把待补充接口视为现有能力。

## 使用示例

### 查看待发货订单并对账

用户：查看我的美国站待发货订单，并核对指定订单的供货价。

确认店铺与范围，查询订单列表，按需读取指定订单详情和金额，展示父单、子单与金额对应关系。

### 准备定制订单

用户：取出这些订单的定制文字和图稿。

使用已有子订单号，或从订单列表、详情取得后查询定制内容，区分文本与图文结果，按接口参考获取资源并说明返回范围。

### 上传核验资料

用户：按这些商品的 SN 和 IMEI 上传到对应子订单。

核对目标订单和用户提供的资料，提交核验信息，说明 Temu 业务结果及后续需处理的履约提示。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
