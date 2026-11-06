---
name: linkfox-temu-cancel-order-eu
description: 处理 Temu 欧洲站买家与卖家发起的取消订单，支持查询买家取消售后、同意取消、提交卖家申诉取消或缺货取消并查询审核结果，以及下载相关加签文件。适用于已授权欧洲站店铺的取消订单处理与进度核对；不适用于其他站点取消、一般订单查询、发货、商品管理或退货退款。
---

# Temu 欧洲站取消订单

## 适用范围

### 适用

处理欧洲站店铺的买家取消售后和卖家取消申请，核对申请进度与失败原因。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看看有哪些买家取消申请待处理 | 查询取消售后列表。 |
| 同意这个买家的取消申请 | 核对订单与售后单，提交同意取消。 |
| 买家地址有误，需要申请取消 | 准备理由与证据，提交卖家申诉取消。 |
| 这个订单缺货，申请取消并查看进度 | 提交缺货申请并查询异步审核结果。 |
| 查询上次取消申请是否通过 | 根据原申请记录查询对应审核结果。 |
| 下载取消业务涉及的加签文件 | 请求加签资源下载。 |

### 边界

订单列表、详情、地址、金额及发货状态由 `linkfox-temu-order-eu` 获取；美国站取消用 `linkfox-temu-cancel-order-us`，全球站取消用 `linkfox-temu-cancel-order-global`。自配送、商品管理及退货退款分别使用 `linkfox-temu-fulfillment-eu`、`linkfox-temu-manage-product-eu`、`linkfox-temu-returns-refunds-eu`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 取消订单售后列表查询（`bg.aftersales.cancel.list.get`） | POST `/temu/proxy` -> Partner EU path：`/openapi/router`；Body `type=bg.aftersales.cancel.list.get` | [references/apis/bg-aftersales-cancel-list-get.md](references/apis/bg-aftersales-cancel-list-get.md) | `scripts/eu_cancel_aftersales_cancel_list_get.py` | 查询取消售后。 |
| 同意买家取消订单（`bg.aftersales.cancel.agree`） | POST `/temu/proxy` -> Partner EU path：`/openapi/router`；Body `type=bg.aftersales.cancel.agree` | [references/apis/bg-aftersales-cancel-agree.md](references/apis/bg-aftersales-cancel-agree.md) | `scripts/eu_cancel_aftersales_cancel_agree.py` | 同意指定买家申请。 |
| 卖家发起取消申请（`temu.order.cancel.appeal.apply`） | POST `/temu/proxy` -> Partner EU path：`/openapi/router`；Body `type=temu.order.cancel.appeal.apply` | [references/apis/temu-order-cancel-appeal-apply.md](references/apis/temu-order-cancel-appeal-apply.md) | `scripts/eu_seller_cancel_order_cancel_appeal_apply.py` | 提交申诉取消申请。 |
| 查询取消申请结果（`temu.order.cancel.appeal.result.get`） | POST `/temu/proxy` -> Partner EU path：`/openapi/router`；Body `type=temu.order.cancel.appeal.result.get` | [references/apis/temu-order-cancel-appeal-result-get.md](references/apis/temu-order-cancel-appeal-result-get.md) | `scripts/eu_seller_cancel_order_cancel_appeal_result_get.py` | 查询申诉审核状态。 |
| 缺货取消申请（`temu.order.cancel.outofstock.apply`） | POST `/temu/proxy` -> Partner EU path：`/openapi/router`；Body `type=temu.order.cancel.outofstock.apply` | [references/apis/temu-order-cancel-outofstock-apply.md](references/apis/temu-order-cancel-outofstock-apply.md) | `scripts/eu_seller_cancel_order_cancel_outofstock_apply.py` | 提交缺货取消风控审核。 |
| 查询缺货取消审核结果（`temu.order.cancel.outofstock.result.get`） | POST `/temu/proxy` -> Partner EU path：`/openapi/router`；Body `type=temu.order.cancel.outofstock.result.get` | [references/apis/temu-order-cancel-outofstock-result-get.md](references/apis/temu-order-cancel-outofstock-result-get.md) | `scripts/eu_seller_cancel_order_cancel_outofstock_result_get.py` | 查询缺货取消审核状态。 |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md) | `scripts/temu_eu_file_download.py`（兼容 `scripts/temu_file_download.py`） | 请求下载 Temu 加签资源。 |

## 前置条件

确认目标店铺、欧洲站与用户要处理的订单或申请。LinkFox 用户密钥与 Temu 店铺令牌分别准备，不能混用。Temu 店铺授权须由用户在卖家后台完成并复制令牌，可使用本地保存工具；详见 [授权与令牌](references/access-token.md) 和 [授权流程](references/authorization-flow.md)。业务参数及脚本兼容约定见 [接口说明](references/api.md)。

## 取消订单处理流程

1. 核对用户已指定的店铺、订单与操作，区分买家取消、卖家申诉取消和缺货取消；需要订单上下文时，先由 `linkfox-temu-order-eu` 查询订单与发货状态。
2. **买家取消**：可先通过 `bg.order.list.v2.get` / `bg.order.detail.v2.get` 找到 `pending_buyer_cancellation` 标签，再按父订单号定位本技能取消售后列表。取得匹配的父售后单与父订单后，按用户授权提交同意取消，再查取消列表或订单状态核对结果。具体筛选与状态含义见接口定义。
3. **卖家申诉取消**：准备取消理由与证据，按接口定义完成图片签名准备；提交申请后保存申请单号，后续使用该单号查询审核状态，再刷新订单状态。
4. **缺货取消**：核对父订单及子订单后提交风控审核；先解释申请受理结果与逐单失败原因，再以相同订单范围查询异步审核结果，最后刷新订单状态。
5. 根据本次返回展示结果；后续查询依照用户任务范围与成本约束执行，不把提交受理当作订单最终取消。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：不消耗算力 （限时）。业务脚本不读取或写入响应缓存；同一会话避免无意义的重复调用。失败或空结果时，先核对筛选、订单范围与错误原因；翻页和后续审核查询按用户任务范围执行，禁止连续试探、重复提交取消申请或无界轮询。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-cancel-order-eu-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 个 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 个 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、响应体中的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分取消路径**：买家取消售后、卖家申诉取消与缺货取消具有不同的单号、结果和审核流程，应按实际业务选择。
- **清晰展示数据**：注明店铺和站点，用表格展示父订单、子订单、售后单或申请单、当前状态、失败原因与本次返回范围；保留原始状态值，缺失字段不补造。
- **解释异步结果**：区分网关收到请求、申请受理、审核通过和订单最终状态。缺货审核状态的含义未定义时如实展示，不擅自套用申诉状态枚举。
- **认证与脚本**：支持手动店铺授权、本地令牌存储与通用 CLI；具体参数、默认值、认证优先级及无缓存运行约定见 [接口说明](references/api.md#脚本运行约定)。
- **处理空结果和错误**：区分当前筛选无记录与请求失败，说明错误原因及尚未确认的状态，保留已取得的数据。

## 使用示例

### 处理买家取消

用户：查看这个订单的待处理取消申请，并同意指定申请。

先定位对应取消售后，核对目标订单与售后单，按用户已指定的范围同意取消，再核对返回与订单状态。

### 卖家申诉取消

用户：买家地址错误，按我提供的材料申请取消。

核对订单与证据，完成签名准备并提交申请，保存申请单号，说明申请受理与审核状态的区别。

### 缺货取消与进度查询

用户：为这些缺货子订单提交取消，并查看审核进度。

核对订单范围，提交缺货取消，展示受理结果与失败原因，再按相同范围查询异步审核结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
