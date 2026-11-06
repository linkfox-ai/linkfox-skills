---
name: linkfox-amazon-store-fulfillment-outbound
description: 管理亚马逊库存面向站外客户的多渠道配送（MCF），支持配送报价、订单预览、创建、查询、列表、更新和取消，查看包裹跟踪、签收凭证及关联发票头，并提供测试订单和包裹状态模拟。适用于已授权卖家的 Fulfillment Outbound v2026-07-04 履约管理；不适用于 External Fulfillment、普通订单管理或旧版 v2020-07-01 履约操作。
---
# Amazon 店铺多渠道出仓履约

## 适用范围

### 适用

用亚马逊库存向非亚马逊渠道的客户发货，查询配送选项、可履约性、订单进展与签收情况。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看这些 SKU 配送到这个邮编有哪些选项 | 比较配送报价和有效期。 |
| 预览并创建这笔 MCF 订单 | 展示费用与限制，确认后创建。 |
| 释放暂存订单，或取消这笔订单 | 查询当前状态，确认变更后提交并核实。 |
| 跟踪订单、看包裹或签收凭证 | 展示实际返回的物流与签收数据。 |
| 查相关发票 | 查询发票头与后续分页情况。 |
| 模拟测试订单或包裹状态 | 按接口参考核对动态沙箱范围。 |

### 边界

旧版履约、退货、feature 和迁移场景参见 [迁移说明](references/migration.md)，旧版能力保留在 `linkfox-amazon-store-fba`；External Fulfillment 与普通 Orders 管理使用对应技能。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 预览履约订单（`getOrderPreview`） | POST `/spApi/developerProxy` → 上游 POST，path：`fulfillment/outbound/2026-07-04/previews` | `scripts/get_order_preview.py` | 查看计划发运、费用、限制与可履约性。 |
| 获取配送报价（`getOffers`） | POST `/spApi/developerProxy` → 上游 POST，path：`fulfillment/outbound/2026-07-04/offers` | `scripts/get_offers.py` | 比较多个 SKU 的配送选项与报价有效期。 |
| 创建履约订单（`createOrder`） | POST `/spApi/developerProxy` → 上游 POST，path：`fulfillment/outbound/2026-07-04/orders` | `scripts/create_order.py` | 提交已确认的多渠道履约订单。 |
| 列出履约订单（`listOrders`） | POST `/spApi/developerProxy` → 上游 GET，path：`fulfillment/outbound/2026-07-04/orders` | `scripts/list_orders.py` | 按更新时间或分页令牌查看订单。 |
| 查询履约订单（`getOrder`） | POST `/spApi/developerProxy` → 上游 GET，path：`fulfillment/outbound/2026-07-04/orders/{orderId}` | `scripts/get_order.py` | 读取订单、包裹、跟踪和签收信息。 |
| 更新履约订单（`updateOrder`） | POST `/spApi/developerProxy` → 上游 PUT，path：`fulfillment/outbound/2026-07-04/orders/{orderId}` | `scripts/update_order.py` | 更新履约配置，释放暂存订单。 |
| 取消履约订单（`cancelOrder`） | POST `/spApi/developerProxy` → 上游 PUT，path：`fulfillment/outbound/2026-07-04/orders/{orderId}/cancel` | `scripts/cancel_order.py` | 提交取消并核实最终状态。 |
| 模拟订单状态（`updateOrderStatus`） | POST `/spApi/developerProxy` → 上游 PUT，path：`fulfillment/outbound/2026-07-04/orders/{orderId}/status` | `scripts/update_order_status.py` | 仅用于 Amazon 动态沙箱订单。 |
| 模拟包裹状态（`updatePackage`） | POST `/spApi/developerProxy` → 上游 PUT，path：`fulfillment/outbound/2026-07-04/orders/{orderId}/packages/{packageId}` | `scripts/update_package.py` | 仅用于 Amazon 动态沙箱包裹。 |
| 查询发票头（`getInvoiceHeaders`） | POST `/spApi/developerProxy` → 上游 GET，path：`finances/invoices/2026-06-25/invoices` | `scripts/get_invoice_headers.py` | 关联的 Invoices v2026-06-25 操作。 |

## 前置条件

**先完成授权并选定店铺**：依赖 `linkfox-amazon-store-auth`，运行 `python scripts/check_auth_dependency.py` 检查安装情况，再通过认证技能选择已授权店铺。依赖缺失时先安装或加载，不在本技能内实现授权与令牌刷新。参数、依赖退出码和环境变量兼容见 [接口说明](references/api.md)。

## 履约流程

1. 选择已授权店铺和区域，确认用户要报价、预览、创建、查询、修改、取消还是测试；先阅读目标操作的接口定义。
2. 用 getOffers 比较多个 SKU 的配送选项与有效期，或用 getOrderPreview 查看计划发运、费用、限制和可履约性。出现 constraints 时停止创建，展示受影响商品及 Amazon 原因。
3. 创建前固定卖家控制的订单和行项目幂等标识，展示店铺、地址、SKU、数量、服务等级、费用及暂存或发货选择。取得明确确认后只创建一次。
4. 创建被异步接受时，以原订单标识安排 getOrder 核实，不自动轮询；结果不确定时不得另造订单或行项目标识再次提交。
5. 释放暂存订单前先查询当前状态，展示目标和配置变化，确认后用 updateOrder 提交，再查询核实。
6. 取消前查询最新状态，说明已拣货或发运的部分可能无法取消，确认后只提交一次，再查询最终状态；接受请求不等于业务完成。
7. 跟踪订单时使用 getOrder，列表查询使用 listOrders；按需请求包裹明细。展示已返回范围，额外翻页或刷新先取得用户同意，不自动遍历。
8. 发票查询使用 getInvoiceHeaders；先核对站点和日期条件，展示发票头与后续分页情况，不自动翻页。它是关联的 Invoices 操作，不属于九个 Outbound 操作。
9. 沙箱状态模拟先展示测试目标、订单或包裹标识和状态变化，确认后执行；环境与调用限制见接口说明。
10. Japan 时段或投递偏好、India 货到付款、跨境申报及特殊包装需求先预览，再将用户确认且 Amazon 支持的配置用于创建，具体字段见接口说明。
11. 写入遇到限流、上游故障或超时先保留原标识并查询状态，遵循 [店铺保护与重试](references/spapi-protection.md)，不自动重放写入。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次，脚本为成功的读取和预览结果提供 24 小时本地缓存。失败或空结果时，不得自动更改参数、翻页或连续试探；需要继续调用时，先说明已有结果与继续调用的目的，并取得用户同意。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-fulfillment-outbound-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、已有的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **展示真实业务进展**：区分网关调用结果、上游接受状态和订单最终状态，连同限制与下一步一起解释。状态判定见接口说明。
- **报价与预览**：把有效期、服务等级、配送区间、币种、价格和商品限制一起展示。
- **订单与包裹**：按实际返回展示订单标识、状态、行项目、分包、物流、签收证明、投放位置和单件标识。分包按返回的关联标识对应，不把单件标识误当行项目标识。
- **签收隐私**：仅在用户确实需要签收凭证时展示投递照片 URL 和收件人，不伪造缺失数据，不将这些信息写进反馈。
- **区域配置**：跨境履约同时展示并确认起运国、目的国和申报价值；Japan 投递偏好及特殊包装按预览给出的可用配置处理，不猜测当地可用值。
- **保留数据和凭据边界**：保留 Amazon 原始标识和完整响应，向用户展示业务结果，隐藏内部工具名及访问令牌。反馈仅附操作、脱敏标识、路径、状态和摘要。
- **失败或空结果**：先展示现有结果与原因；需要继续调用时先取得用户同意，不自动换参数或连续试探。
- **缓存与刷新**：脚本按当前会话隔离成功读取和预览的缓存，生产写入成功后失效；刷新、输出和依赖检测的详细约定见接口说明。
- **迁移与通知**：跟踪数据包含在 v2026-07-04 订单中；订单状态通知属于 Notifications 的 FULFILLMENT_ORDER_STATUS 订阅，不属于 Outbound 操作。迁移时阅读迁移说明。

## 使用示例

### 比较配送选项

用户：看这些亚马逊 SKU 配送到这个邮编有哪些选择。

选择店铺，获取配送报价，展示有效期、价格与限制。

### 预览后创建订单

用户：预览并创建这笔 MCF 订单。

先预览，展示费用、限制和目标；确认后只创建一次，解释是否需要后续核实。

### 查询跟踪与签收

用户：跟踪这笔订单并查看签收凭证。

查询订单及包裹明细，展示实际返回的跟踪和签收信息。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
