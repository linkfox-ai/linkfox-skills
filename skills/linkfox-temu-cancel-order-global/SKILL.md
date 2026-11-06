---
name: linkfox-temu-cancel-order-global
description: 处理 Temu 全球站（非美国、欧洲）的买家与卖家取消订单，支持查询买家取消售后、同意取消、卖家申诉取消、缺货取消及异步审核结果查询，并获取相关加签文件。适用于已授权店铺的取消售后处理和取消进度核对；不适用于美国站、欧洲站取消，也不负责商品管理、普通退货退款或订单发货。
---

# Temu 全球站取消订单（买家与卖家）

## 适用范围

### 适用

处理全球站店铺的取消订单售后，区分买家取消与卖家申诉、缺货取消，并核对申请进度和最终订单状态。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看全球站待处理的买家取消 | 查询取消售后列表，核对售后单与父订单。 |
| 同意这个买家的取消申请 | 对用户指定的取消售后提交同意。 |
| 地址错误或疑似批量退款，申请取消 | 提交卖家申诉取消并查询审核进度。 |
| 这些子订单缺货，需要取消 | 提交缺货取消并查询异步风控审核结果。 |
| 下载取消业务相关的加签文件 | 通过店铺授权获取加签资源。 |

### 边界

美国站取消使用 `linkfox-temu-cancel-order-us`，欧洲站取消使用 `linkfox-temu-cancel-order-eu`。订单列表、详情与最终状态刷新交给 `linkfox-temu-order-global`；履约发货使用 `linkfox-temu-fulfillment-global`，商品管理使用 `linkfox-temu-manage-product-global`。普通退货退款参见 `linkfox-temu-returns-refunds-us` / `linkfox-temu-returns-refunds-eu` 的相应兼容场景，不能以取消申请替代。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 取消订单售后列表查询（`bg.aftersales.cancel.list.get`） | POST `/temu/proxy` → Temu path：`/openapi/router`；type：`bg.aftersales.cancel.list.get` | [references/apis/bg-aftersales-cancel-list-get.md](references/apis/bg-aftersales-cancel-list-get.md) | `scripts/global_cancel_aftersales_cancel_list_get.py` | 买家取消 |
| 同意取消订单（`bg.aftersales.cancel.agree`） | POST `/temu/proxy` → Temu path：`/openapi/router`；type：`bg.aftersales.cancel.agree` | [references/apis/bg-aftersales-cancel-agree.md](references/apis/bg-aftersales-cancel-agree.md) | `scripts/global_cancel_aftersales_cancel_agree.py` | 买家取消 |
| 卖家发起取消申请（`temu.order.cancel.appeal.apply`） | POST `/temu/proxy` → Temu path：`/openapi/router`；type：`temu.order.cancel.appeal.apply` | [references/apis/temu-order-cancel-appeal-apply.md](references/apis/temu-order-cancel-appeal-apply.md) | `scripts/global_seller_cancel_order_cancel_appeal_apply.py` | 卖家取消 |
| 查询取消申请结果（`temu.order.cancel.appeal.result.get`） | POST `/temu/proxy` → Temu path：`/openapi/router`；type：`temu.order.cancel.appeal.result.get` | [references/apis/temu-order-cancel-appeal-result-get.md](references/apis/temu-order-cancel-appeal-result-get.md) | `scripts/global_seller_cancel_order_cancel_appeal_result_get.py` | 卖家取消 |
| 缺货取消申请（`temu.order.cancel.outofstock.apply`） | POST `/temu/proxy` → Temu path：`/openapi/router`；type：`temu.order.cancel.outofstock.apply` | [references/apis/temu-order-cancel-outofstock-apply.md](references/apis/temu-order-cancel-outofstock-apply.md) | `scripts/global_seller_cancel_order_cancel_outofstock_apply.py` | 卖家取消 |
| 查询缺货取消审核结果（`temu.order.cancel.outofstock.result.get`） | POST `/temu/proxy` → Temu path：`/openapi/router`；type：`temu.order.cancel.outofstock.result.get` | [references/apis/temu-order-cancel-outofstock-result-get.md](references/apis/temu-order-cancel-outofstock-result-get.md) | `scripts/global_seller_cancel_order_cancel_outofstock_result_get.py` | 卖家取消 |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md) | `scripts/temu_global_file_download.py`（兼容 `temu_file_download.py`） | 下载 Temu 加签资源 |

通用兼容入口为 `scripts/temu_global_proxy.py` 和 `scripts/temu_proxy.py`；它们复用代理端点，不另计业务接口。官方菜单与链接见 [references/partner-global-catalog.md](references/partner-global-catalog.md)，分文档索引见 [references/apis/README.md](references/apis/README.md)。

## 前置条件

先确定目标全球站店铺、订单、取消发起方与用户要求的操作范围。LinkFox 用户密钥与 Temu 店铺令牌分别配置；Temu 令牌需用户在对应卖家后台手动授权复制，不能以 LinkFox 密钥替代。授权步骤、本地保存与读取脚本见 [references/access-token.md](references/access-token.md) 和 [references/authorization-flow.md](references/authorization-flow.md)。完整参数和兼容约定见 [references/api.md](references/api.md)。

## 取消订单处理流程

1. 核对店铺与订单，区分买家取消售后、卖家申诉取消、缺货取消；卖家场景先通过订单技能取得父子订单号与发货状态。
2. 买家取消：可先通过订单技能的买家取消标签定位订单，再查待处理取消售后，使用返回的父售后单号与父订单号同意用户指定的取消；按接口文档的状态组筛选复核已同意，或刷新订单状态。
3. 卖家申诉取消：准备原因与所需证据，提交申请后保留申请单号，再按申请单号查询审核进度；不要把申请提交当作订单已取消。
4. 缺货取消：提交指定父订单及子订单，展示受理情况和失败原因，再查询异步审核结果。
5. 需要时下载业务相关加签文件；处理后通过订单技能刷新最终状态。后续查询、翻页按用户任务范围与调用约束执行，避免自动连续试探。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；业务脚本不使用响应缓存，每次执行都会发起请求。失败或空结果时，不得自动更换筛选条件、翻页或连续试探；后续查询按用户任务范围执行，不自动重试同意取消或提交申请。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-cancel-order-global-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
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

- **区分两套认证**：LinkFox 密钥用于网关，Temu 令牌用于具体店铺。多站点分别授权；子账号无法进入服务市场时由主账号授权，令牌过期后重新复制保存，并按需配置 IP 白名单。
- **区分业务概念**：取消售后状态组、父售后状态、申诉状态、缺货审核状态各自独立，具体枚举与判断见接口文档。
- **清晰展示结果**：标明店铺与全球站，用表格展示父订单、子订单、父售后单、申请单、受理情况、审核结果和失败原因。仅展示接口返回的字段，不补造未知枚举或不存在的数据。
- **说明异步结果**：区分请求完成、申请受理、审核通过与订单最终取消；同意取消与提交申请按用户已明确的目标执行。
- **保留完整证据**：保存完整响应，JSON 字符串解析失败时仍保留响应文本，按接口定义解释网关和 Temu 两层错误。
- **认证工具按需使用**：本地授权指导与令牌管理无需请求业务接口；`check_linkfox_token.py` 会发送网关探测，仅在确需诊断时使用，运行细节见接口参考。

## 使用示例

### 处理买家取消

用户：查全球站待处理取消，同意我指定的这一单。

查询取消售后并核对目标，提交同意，再按用户范围核对售后或订单状态。

### 提交卖家取消并查看结果

用户：这个订单地址错误，按我提供的证据申请取消，并查看审核结果。

核对订单与证据，提交申诉，保留申请单号并查询状态。缺货场景则提交缺货申请，再查询相应异步审核结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
