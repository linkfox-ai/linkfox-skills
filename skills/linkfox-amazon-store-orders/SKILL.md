---
name: linkfox-amazon-store-orders
description: 查询和管理已授权亚马逊卖家店铺的订单，支持订单搜索、详情、订单商品、买家信息、收货地址、管制商品信息，以及发货确认、配送状态和买家核验状态更新。适用于卖家订单查询与履约处理；不适用于 MCF 多渠道配送、FBA 入仓或 External Fulfillment 货件管理。
---
# Amazon 店铺订单查询与履约管理

## 适用范围

### 适用

查询亚马逊商城产生的卖家订单，或按用户要求处理指定订单的发货、配送和管制商品核验。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查看这段时间的新订单或更新订单 | 搜索订单并说明本次返回范围。 |
| 查这个订单号的详情、商品和买家信息 | 读取指定订单与业务所需数据。 |
| 查询订单收货地址 | 展示权限允许的地址信息。 |
| 确认订单发货或更新自提状态 | 核对目标订单和履约资料，提交指定变更。 |
| 查看管制商品订单并更新核验结果 | 读取管制信息，按用户要求处理核验状态。 |

### 边界

MCF 多渠道配送、FBA 入仓和 External Fulfillment 货件管理转交对应履约技能。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 搜索订单（`searchOrders`） | POST `/spApi/developerProxy` → GET path：`orders/2026-01-01/orders` | `scripts/search_orders.py` | 读取订单数据。 |
| 获取订单详情（`getOrder`） | POST `/spApi/developerProxy` → GET path：`orders/2026-01-01/orders/{orderId}` | `scripts/get_order.py` | 读取订单数据。 |
| 获取订单买家信息（`getOrderBuyerInfo`） | POST `/spApi/developerProxy` → GET path：`orders/v0/orders/{orderId}/buyerInfo` | `scripts/get_order_buyer_info.py` | 读取订单数据。 |
| 获取收货地址（`getOrderAddress`） | POST `/spApi/developerProxy` → GET path：`orders/v0/orders/{orderId}/address` | `scripts/get_order_address.py` | 读取订单数据。 |
| 获取订单商品（`getOrderItems`） | POST `/spApi/developerProxy` → GET path：`orders/v0/orders/{orderId}/orderItems` | `scripts/get_order_items.py` | 读取订单数据。 |
| 获取订单商品买家信息（`getOrderItemsBuyerInfo`） | POST `/spApi/developerProxy` → GET path：`orders/v0/orders/{orderId}/orderItems/buyerInfo` | `scripts/get_order_items_buyer_info.py` | 读取订单数据。 |
| 更新配送状态（`updateShipmentStatus`） | POST `/spApi/developerProxy` → POST path：`orders/v0/orders/{orderId}/shipment` | `scripts/update_shipment_status.py` | 提交指定订单的履约或核验变更。 |
| 获取管制订单信息（`getOrderRegulatedInfo`） | POST `/spApi/developerProxy` → GET path：`orders/v0/orders/{orderId}/regulatedInfo` | `scripts/get_order_regulated_info.py` | 读取订单数据。 |
| 更新买家核验状态（`updateVerificationStatus`） | POST `/spApi/developerProxy` → PATCH path：`orders/v0/orders/{orderId}/regulatedInfo` | `scripts/update_verification_status.py` | 提交指定订单的履约或核验变更。 |
| 确认发货（`confirmShipment`） | POST `/spApi/developerProxy` → POST path：`orders/v0/orders/{orderId}/shipmentConfirmation` | `scripts/confirm_shipment.py` | 提交指定订单的履约或核验变更。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；检测结果为缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。依赖检测约定见 `references/api.md`。
确认用户指定的店铺、区域、站点和订单范围；各接口所需信息见 `references/api.md`。

## 订单查询与履约流程

1. 确定目标店铺及本次查询或变更范围，检查认证依赖；按需阅读 `references/api.md` 对应操作。
2. 查询订单列表或指定订单详情；需要商品、买家、地址或管制信息时，再选择对应读取能力。
3. 处理发货、配送或核验变更前，核对订单和用户提供的资料，按用户已明确的操作范围准备并提交请求。
4. 根据返回状态与订单数据展示结果，说明后续页是否可查；异常时遵循接口参考中的店铺保护与重试要求，保留已取得的数据。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；订单业务脚本始终禁用响应缓存，重复执行会重新请求。失败或空结果时，不得自动更换条件或连续翻页试探；按用户任务范围继续检索，并遵循接口限速与店铺保护要求。

### 输出策略

- 订单业务脚本始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-orders-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、存在于顶层的常见计数或状态（如 `total`、`costToken`）、最大非空列表字段的长度和前 3 条样本。
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

- **核对运行约定**：通用执行方式在本技能中的适用差异，见 `references/api.md` 各操作的运行约定。
- **清晰展示数据**：注明店铺、站点、订单号及本次返回范围，用表格展示可用订单状态、商品、配送和核验结果。
- **优先选择当前订单能力**：新集成优先采用新版订单搜索和详情；旧版买家、地址和订单商品能力的弃用及受限数据说明见 `references/api.md`。
- **解释返回层次**：区分网关请求、Amazon 上游状态与订单业务结果。写入结果中保留已组装的请求资料，便于核对；不要把请求完成直接描述为包裹已经送达。
- **保护买家信息**：仅展示业务所需信息，反馈和分享数据前脱敏。
- **处理错误和分页**：按 `references/api.md` 解释原因、限速和店铺保护，保留已取得的数据；写入结果不确定时先查状态，不直接重放。

## 使用示例

### 查询指定时间段订单

用户：查看美国站这段时间更新过的订单。

确认店铺、站点和时间范围，搜索订单，展示订单状态与本次返回范围。

### 查看订单详情与商品

用户：查这个订单的详情和商品。

读取指定订单，按需补充订单商品及允许访问的信息，说明缺失数据或权限限制。

### 确认发货或更新核验结果

用户：按我提供的包裹资料确认这个订单发货。

核对店铺、订单及包裹资料后提交指定变更，解释返回状态；结果不确定时先读取状态。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
