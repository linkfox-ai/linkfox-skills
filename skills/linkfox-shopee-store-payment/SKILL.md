---
name: linkfox-shopee-store-payment
description: 查询已授权 Shopee（虾皮）店铺的订单托管与结算明细、打款汇总和明细、钱包流水、账单交易、收入概览与明细，生成和获取收入报告、收入对账单，并查询支付方式和管理店铺或商品分期。适用于店铺资金核对、收入报表和分期设置；不适用于店铺授权、订单查询处理或促销管理。
---
# Shopee 店铺支付与结算

## 适用范围

### 适用

处理已授权 Shopee 店铺的 Payment 业务，包括资金查询、收入报表和分期设置。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看这笔订单结算了多少 | 查询订单托管与结算明细。 |
| 查店铺打款和钱包流水 | 查询打款明细、汇总、钱包与账单交易。 |
| 导出收入报告或对账单 | 异步生成，再获取对应结果。 |
| 看店铺收入构成 | 查询收入概览与明细。 |
| 查询或修改分期付款 | 读取或设置店铺、商品分期状态。 |
| 看当前支持哪些支付方式 | 查询可用支付方式。 |

### 边界

店铺授权交由 `linkfox-shopee-store-auth`；订单查询与处理使用 `linkfox-shopee-store-orders`。Discount、Voucher 等促销业务不属于 Payment 模块。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 异步生成收入报告（`generate_income_report`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/payment/generate_income_report` | [references/apis/generate-income-report.md](references/apis/generate-income-report.md) | `scripts/generate_income_report.py` | 异步生成收入报告。 |
| 异步生成收入对账单（`generate_income_statement`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/payment/generate_income_statement` | [references/apis/generate-income-statement.md](references/apis/generate-income-statement.md) | `scripts/generate_income_statement.py` | 异步生成收入对账单。 |
| 查询账单交易信息（`get_billing_transaction_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_billing_transaction_info` | [references/apis/get-billing-transaction-info.md](references/apis/get-billing-transaction-info.md) | `scripts/get_billing_transaction_info.py` | 查询账单交易信息。 |
| 查询订单托管与结算明细（`get_escrow_detail`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_escrow_detail` | [references/apis/get-escrow-detail.md](references/apis/get-escrow-detail.md) | `scripts/get_escrow_detail.py` | 查询订单托管与结算明细。 |
| 批量查询托管明细（`get_escrow_detail_batch`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/payment/get_escrow_detail_batch` | [references/apis/get-escrow-detail-batch.md](references/apis/get-escrow-detail-batch.md) | `scripts/get_escrow_detail_batch.py` | 批量查询托管明细。 |
| 按时间范围查询托管列表（`get_escrow_list`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_escrow_list` | [references/apis/get-escrow-list.md](references/apis/get-escrow-list.md) | `scripts/get_escrow_list.py` | 按时间范围查询托管列表。 |
| 查询收入明细（`get_income_detail`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_income_detail` | [references/apis/get-income-detail.md](references/apis/get-income-detail.md) | `scripts/get_income_detail.py` | 查询收入明细。 |
| 查询收入概览（`get_income_overview`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_income_overview` | [references/apis/get-income-overview.md](references/apis/get-income-overview.md) | `scripts/get_income_overview.py` | 查询收入概览。 |
| 获取已生成的收入报告（`get_income_report`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_income_report` | [references/apis/get-income-report.md](references/apis/get-income-report.md) | `scripts/get_income_report.py` | 获取已生成的收入报告。 |
| 获取已生成的收入对账单（`get_income_statement`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_income_statement` | [references/apis/get-income-statement.md](references/apis/get-income-statement.md) | `scripts/get_income_statement.py` | 获取已生成的收入对账单。 |
| 查询商品分期状态（`get_item_installment_status`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_item_installment_status` | [references/apis/get-item-installment-status.md](references/apis/get-item-installment-status.md) | `scripts/get_item_installment_status.py` | 查询商品分期状态。 |
| 查询可用支付方式（`get_payment_method_list`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_payment_method_list` | [references/apis/get-payment-method-list.md](references/apis/get-payment-method-list.md) | `scripts/get_payment_method_list.py` | 查询可用支付方式。 |
| 查询打款明细（`get_payout_detail`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_payout_detail` | [references/apis/get-payout-detail.md](references/apis/get-payout-detail.md) | `scripts/get_payout_detail.py` | 查询打款明细。 |
| 查询打款汇总（`get_payout_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_payout_info` | [references/apis/get-payout-info.md](references/apis/get-payout-info.md) | `scripts/get_payout_info.py` | 查询打款汇总。 |
| 查询店铺分期状态（`get_shop_installment_status`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_shop_installment_status` | [references/apis/get-shop-installment-status.md](references/apis/get-shop-installment-status.md) | `scripts/get_shop_installment_status.py` | 查询店铺分期状态。 |
| 分页或按时间查询钱包流水（`get_wallet_transaction_list`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/payment/get_wallet_transaction_list` | [references/apis/get-wallet-transaction-list.md](references/apis/get-wallet-transaction-list.md) | `scripts/get_wallet_transaction_list.py` | 分页或按时间查询钱包流水。 |
| 设置商品分期状态（`set_item_installment_status`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/payment/set_item_installment_status` | [references/apis/set-item-installment-status.md](references/apis/set-item-installment-status.md) | `scripts/set_item_installment_status.py` | 设置商品分期状态。 |
| 开启或关闭店铺分期（`set_shop_installment_status`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/payment/set_shop_installment_status` | [references/apis/set-shop-installment-status.md](references/apis/set-shop-installment-status.md) | `scripts/set_shop_installment_status.py` | 开启或关闭店铺分期。 |
| 查询店铺授权状态（兼容辅助操作） | POST `/shopee/storeTokens` | [references/api.md](references/api.md#接口查询店铺授权状态兼容辅助操作) | `scripts/_shopee_payment_common.py`：`resolve_store_tokens` | 返回授权记录与状态；正常 Payment 流程由服务端解析令牌，无需另行调用。 |

## 前置条件

**先完成授权并确定店铺**：依赖 `linkfox-shopee-store-auth` 选店并完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内实现授权或令牌逻辑。依赖检测及兼容行为见 [references/api.md](references/api.md)。

## 业务流程

1. 检查认证技能依赖，确定用户要操作的已授权店铺及业务目标。
2. 查询订单结算时，先由订单技能取得订单号，再查询托管明细；查询资金往来时，选择打款、钱包或账单交易操作。
3. 收入报表先异步生成，再用对应获取操作读取结果；根据实际返回说明生成状态，不将生成请求完成视作文件已经可用。
4. 修改分期时，核对用户指定的店铺或商品以及开关目标，再按已授权范围提交设置。
5. 按接口参考先判断网关与上游状态，再读取解析结果；展示本次结果和可用的报表信息，保留错误原文供定位。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；业务脚本不使用响应缓存，重复执行不会复用缓存结果。失败或空结果时，不得自动更换查询条件或连续试探；需要继续查询时，先说明原因与范围，按用户任务范围执行。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-payment-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的顶层标量字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **资金概念**：Escrow 是订单托管与结算；Payout 是打款；钱包流水用于核对资金变动；收入报告与对账单采用异步生成、随后获取的流程。
- **转发链路**：店铺选择后由服务端解析令牌，经 `developerProxy` → 紫鸟 `shopee-proxy` → Shopee API。正常流程无需在本地获取令牌。
- **清晰展示数据**：注明店铺、查询范围和返回的币种；按实际数据展示结算、打款、钱包或收入信息，不补造缺失金额、报表链接或分期状态。
- **区分读取与设置**：分期设置会改变店铺或商品配置；生成报表是异步任务，结果未就绪时说明实际状态，后续调用遵守调用约束。
- **脚本兼容行为**：各业务入口均不使用响应缓存；具体参数映射、CLI、输出及依赖约定见 [references/api.md](references/api.md#运行约定)。
- **官方参考**：各操作文档保留 Shopee Payment 官方文档链接；未在接口参考中列明的上游字段以对应官方文档和实际响应为准，不推断必填、默认值、枚举或批量上限。

## 使用示例

### 查询订单结算

用户：查这笔订单的结算明细。

确认店铺，从订单技能获取订单号，再查询托管明细，解释返回的结算数据。

### 查询打款与钱包

用户：核对这个时间段的打款和钱包流水。

选择打款明细、打款汇总和钱包流水操作，按用户指定范围查询并展示资金记录。

### 获取收入报告

用户：生成店铺收入报告。

提交生成任务，再按实际返回和用户任务范围获取报告，展示生成状态及可用结果。

### 管理分期

用户：查看并调整指定店铺或商品的分期状态。

核对目标，按需查询当前状态，再按用户指定的设置提交并说明返回结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
