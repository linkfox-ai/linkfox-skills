---
name: linkfox-temu-cancel-order-us
description: 管理 Temu 美国站的买家与卖家取消订单，支持查询买家取消售后、同意取消、提交卖家取消申诉或缺货取消申请、查询审核结果，以及获取相关加签文件。适用于美国站取消订单处理与进度核对；不适用于欧洲站、全球站取消订单、订单发货管理或退货退款。
---
# Temu 美国站取消订单

## 适用范围

### 适用

处理已授权 Temu 美国站店铺的买家取消售后和卖家主动取消申请，核对受理与审核进度。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看看哪些买家正在申请取消订单 | 买家取消：查询售后列表。 |
| 同意这笔订单的买家取消申请 | 买家取消：核对订单与售后记录后同意。 |
| 因地址错误或疑似批量退款申请取消 | 卖家取消：准备说明与证明后提交申诉。 |
| 这些子订单缺货，需要取消 | 缺货取消：提交风控审核并核对结果。 |
| 看看取消申请审核到哪一步了 | 进度查询：按申请或订单记录读取状态。 |
| 获取取消处理相关的加签文件 | 文件获取：使用店铺授权获取响应。 |

### 边界

订单查询、地址、金额和发货状态使用 `linkfox-temu-order-us`，履约使用 `linkfox-temu-fulfillment-us`，商品管理使用 `linkfox-temu-manage-product-us`，退货退款使用 `linkfox-temu-returns-refunds-us`。欧洲站与全球站取消分别使用 `linkfox-temu-cancel-order-eu`、`linkfox-temu-cancel-order-global`。

## 接口清单

6 个取消订单操作与 1 个辅助文件接口合计 7 个接口，通用代理与认证探测复用已有端点。转发与参数约定见 [references/api.md](references/api.md) 及各操作文档。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 取消订单售后列表查询 | POST `/temu/proxy` → 转发 path：`/openapi/router`，`type=bg.aftersales.cancel.list.get` | [references/apis/bg-aftersales-cancel-list-get.md](references/apis/bg-aftersales-cancel-list-get.md) | `scripts/us_cancel_aftersales_cancel_list_get.py` | 查询买家取消申请及售后状态。 |
| 同意取消订单 | POST `/temu/proxy` → 转发 path：`/openapi/router`，`type=bg.aftersales.cancel.agree` | [references/apis/bg-aftersales-cancel-agree.md](references/apis/bg-aftersales-cancel-agree.md) | `scripts/us_cancel_aftersales_cancel_agree.py` | 同意指定买家取消申请。 |
| 卖家发起取消申请 | POST `/temu/proxy` → 转发 path：`/openapi/router`，`type=temu.order.cancel.appeal.apply` | [references/apis/temu-order-cancel-appeal-apply.md](references/apis/temu-order-cancel-appeal-apply.md) | `scripts/us_seller_cancel_order_cancel_appeal_apply.py` | 提交申诉类取消申请。 |
| 查询取消申请结果 | POST `/temu/proxy` → 转发 path：`/openapi/router`，`type=temu.order.cancel.appeal.result.get` | [references/apis/temu-order-cancel-appeal-result-get.md](references/apis/temu-order-cancel-appeal-result-get.md) | `scripts/us_seller_cancel_order_cancel_appeal_result_get.py` | 查询取消申诉审核状态。 |
| 缺货取消申请 | POST `/temu/proxy` → 转发 path：`/openapi/router`，`type=temu.order.cancel.outofstock.apply` | [references/apis/temu-order-cancel-outofstock-apply.md](references/apis/temu-order-cancel-outofstock-apply.md) | `scripts/us_seller_cancel_order_cancel_outofstock_apply.py` | 提交缺货取消风控审核。 |
| 查询缺货取消审核结果 | POST `/temu/proxy` → 转发 path：`/openapi/router`，`type=temu.order.cancel.outofstock.result.get` | [references/apis/temu-order-cancel-outofstock-result-get.md](references/apis/temu-order-cancel-outofstock-result-get.md) | `scripts/us_seller_cancel_order_cancel_outofstock_result_get.py` | 获取异步缺货取消审核结果。 |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md) | `scripts/temu_us_file_download.py`、`scripts/temu_file_download.py` | 获取店铺授权下的加签资源响应。 |

## 前置条件

先确定目标店铺、美国站和操作范围，并具备 LinkFox 用户密钥与 Temu 店铺授权，两者用途不同。Temu 授权须在卖家后台手动复制；授权步骤与本地令牌管理见 [references/access-token.md](references/access-token.md) 和 [references/authorization-flow.md](references/authorization-flow.md)。
按需使用 `scripts/temu_token_guide.py` 查看授权步骤，使用 `scripts/save_temu_access_token.py`、`scripts/list_temu_access_tokens.py`、`scripts/get_temu_access_token.py` 管理本地令牌。`scripts/check_linkfox_token.py` 为可选网关探测，不是纯本地检查；运行约定见接口参考。

## 取消订单处理流程

1. 确定买家取消、卖家申诉或缺货取消场景，核对店铺、父订单、子订单及发货状态；需要订单信息时使用 `linkfox-temu-order-us`。
2. 买家取消：可先通过 `bg.order.list.v2.get` / `bg.order.detail.v2.get` 找到带 `pending_buyer_cancellation` 标签的订单，再按 `parentOrderSnList` 查询本技能售后列表；取得匹配的父售后单号与父订单号后，同意用户指定的取消申请。
3. 卖家申诉：准备取消原因及证明，提交申请并保存 `applySn`，后续按申请单号查询审核结果；证明图片的签名要求见对应接口文档。
4. 缺货取消：从订单数据确定父订单与子订单列表，提交风控审核，先查看受理结果及失败原因，再按相同订单范围查询异步审核结果。
5. 展示本次受理或审核进度；买家取消可再次查售后列表，取消后可用 `linkfox-temu-order-us` 刷新订单状态。结果查询按用户任务范围进行，遵守调用约束，不自动重复提交取消申请。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；业务脚本不读取或保存响应缓存。失败或空结果时，不得自动变更条件、翻页或连续试探；需要继续查询时，按用户任务范围处理，不自动重复提交取消申请。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-cancel-order-us-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
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

- **区分取消场景**：买家同意取消、卖家申诉与缺货取消各有独立流程，不互相替代。按用户已明确的目标准备操作，不把读取进度扩展为取消写入。
- **区分受理与完成**：申请提交成功不代表最终取消；缺货取消需要风控审核，申诉需查询审核进度。业务状态、枚举与限制均见接口文档。
- **清晰展示结果**：注明店铺、站点、父订单、子订单、售后单或申请单号、当前状态和失败原因；区分请求完成、受理和最终订单状态。
- **保护授权信息**：展示本地令牌列表时沿用默认脱敏；LinkFox 密钥与 Temu accessToken 不互换。授权应用、过期更新和 IP 白名单要求见授权参考。
- **空结果与错误**：保留已获得的数据，结合网关及 Temu 业务响应解释原因；不从空对象、空列表或缺失状态推断取消成功。
- **通用入口**：`scripts/temu_us_proxy.py` 兼容美国站通用转发，`scripts/temu_proxy.py` 提供通用转发入口。缓存、参数归一化、输出目录及认证兼容的具体约定见 [references/api.md](references/api.md)。
- **文档维护**：取消操作目录见 [references/partner-us-catalog.md](references/partner-us-catalog.md) 和 [references/apis/README.md](references/apis/README.md)；官方未提供的菜单编号保持未确认，不补造。

## 使用示例

### 处理买家取消

用户：查一下这笔订单的待处理取消申请，同意我指定的那一条。

核对订单并读取售后列表，匹配父售后单与父订单后同意取消，展示返回结果；按需刷新售后或订单状态。

### 提交卖家申诉并查看进度

用户：这个订单地址错误，按我提供的说明和截图申请取消。

核对订单与签名证明，提交申请并保存申请单号；后续查询审核状态，明确说明受理与最终取消的区别。

### 缺货取消

用户：这些子订单缺货，请申请取消并查看审核结果。

提交用户指定的订单范围，展示受理结果与逐单失败原因，再查询异步审核结果，不因审核中重复提交。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
