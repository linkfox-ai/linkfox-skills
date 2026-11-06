---
name: linkfox-temu-order-global
description: 管理 Temu 全球区订单，支持订单列表与详情、常规及敏感收货地址、供货价及税费拆分、可合并发货订单组、定制商品内容、SN/IMEI 或二手商品鉴真信息上传及加签资源下载。适用于全球区店铺订单处理和 ERP 对账；美国区、欧洲区订单以及商品维护、价格维护、取消、售后和履约发货使用对应技能。
---
# Temu 全球站订单管理

## 适用范围

### 适用

管理已授权的 Temu 全球区店铺订单，按需读取订单、地址、金额与定制内容，并提交订单核验信息。

**场景速查**

| 用户表达 | 查询场景 |
|------|------|
| 看全球区待发货订单和某单详情 | 按条件查列表，再读取指定父单的子单详情。 |
| 查询订单地址或解密地址 | 读取常规地址限制提示，按实际任务获取敏感地址。 |
| 获取供货价或 V2 税费明细用于对账 | 比较父单汇总和子单金额。 |
| 哪些订单可以合并发货 | 展示可合并的父单组。 |
| 查看订单刻字、图案或 SVG 内容 | 按子单读取定制内容及资源。 |
| 为订单上传 SN、IMEI 或鉴真编码 | 核对订单后提交核验信息。 |

### 边界

全球区与美国区、欧洲区分开：后两者使用 `linkfox-temu-order-us`、`linkfox-temu-order-eu`。商品维护使用 `linkfox-temu-manage-product-global`，价格维护使用 `linkfox-temu-price-global`，发品使用 `linkfox-temu-add-product-us`，取消使用 `linkfox-temu-cancel-order-global`，履约发货使用 `linkfox-temu-fulfillment-global`，退货退款使用 `linkfox-temu-returns-refunds-us`。本技能查询可合并组，不执行合并发货确认或购买面单。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 订单列表查询 V2（`bg.order.list.v2.get`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.order.list.v2.get` | [references/apis/bg-order-list-v2-get.md](references/apis/bg-order-list-v2-get.md) | `scripts/global_order_list_v2_get.py` | 分页获取父单和子单。 |
| 订单详情查询 V2（`bg.order.detail.v2.get`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.order.detail.v2.get` | [references/apis/bg-order-detail-v2-get.md](references/apis/bg-order-detail-v2-get.md) | `scripts/global_order_detail_v2_get.py` | 读取指定父单及子单详情。 |
| 订单收货地址查询 V2（`bg.order.shippinginfo.v2.get`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.order.shippinginfo.v2.get` | [references/apis/bg-order-shippinginfo-v2-get.md](references/apis/bg-order-shippinginfo-v2-get.md) | `scripts/global_order_shippinginfo_v2_get.py` | 获取常规收货地址及限制提示。 |
| 订单收货地址解密查询（`bg.order.decryptshippinginfo.get`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.order.decryptshippinginfo.get` | [references/apis/bg-order-decryptshippinginfo-get.md](references/apis/bg-order-decryptshippinginfo-get.md) | `scripts/global_order_decryptshippinginfo_get.py` | 获取指定订单的敏感收货地址。 |
| 订单金额/供货价查询（`bg.order.amount.query`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.order.amount.query` | [references/apis/bg-order-amount-query.md](references/apis/bg-order-amount-query.md) | `scripts/global_order_amount_query.py` | 为 ERP 提供订单供货价和金额。 |
| 订单金额查询 V2（`temu.order.amount.v2.query`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.order.amount.v2.query` | [references/apis/temu-order-amount-v2-query.md](references/apis/temu-order-amount-v2-query.md) | `scripts/global_order_amount_v2_query.py` | 读取父单和子单的税费拆分金额。 |
| 可合并发货订单组列表（`bg.order.combinedshipment.list.get`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.order.combinedshipment.list.get` | [references/apis/bg-order-combinedshipment-list-get.md](references/apis/bg-order-combinedshipment-list-get.md) | `scripts/global_order_combinedshipment_list_get.py` | 查询可合并发货的父订单组。 |
| 订单定制商品内容批量查询（`bg.order.customization.get`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.order.customization.get` | [references/apis/bg-order-customization-get.md](references/apis/bg-order-customization-get.md) | `scripts/global_order_customization_get.py` | 批量读取子订单的文字、图文和 SVG 定制内容。 |
| 订单核验信息上传（`temu.local.order.verification.upload`） | POST `/temu/proxy` -> 转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.local.order.verification.upload` | [references/apis/temu-local-order-verification-upload.md](references/apis/temu-local-order-verification-upload.md) | `scripts/global_order_verification_upload.py` | 上传 SN、IMEI 或二手商品鉴真信息。 |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md#接口加签文件下载) | `scripts/temu_global_file_download.py` | 获取加签资源的网关返回。 |

通用订单入口 `scripts/temu_global_proxy.py` 可转发上述 type，不另计接口；多站点兼容入口及授权辅助 CLI 见 [references/api.md](references/api.md)。Partner 目录见 [references/partner-global-catalog.md](references/partner-global-catalog.md)。

## 前置条件

确定全球区目标店铺与操作范围，准备 LinkFox 用户密钥及 Temu 店铺令牌。Temu 令牌需用户在卖家后台手动授权并复制，可按 [references/access-token.md](references/access-token.md) 保存本地后复用；授权判断流程见 [references/authorization-flow.md](references/authorization-flow.md)。

## 订单处理流程

1. 明确店铺与查询条件；已有订单号时直接查目标订单，否则先查询订单列表。
2. 从列表选择父单，再按需查询详情、常规地址及其限制提示；任务需要敏感信息时获取解密地址。
3. ERP 对账按需查询供货价或 V2 金额，将父单汇总与子单明细对齐。
4. 用户要求合并处理时查看可合并发货组；有定制商品时按子单读取定制内容，按接口参考下载所需资源。
5. 订单需要 SN/IMEI 或二手鉴真信息时，核对用户提供的核验资料并上传，解释提交结果与订单履约提示。
6. 取消、合并发货确认、面单、运单、合作仓和跟踪等后续操作按边界转交对应技能；不把查组结果当作已发货。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次；业务脚本不读取或保存响应缓存，已有数据优先复用已保存文件。失败或空结果时，不自动重试、翻页或修改参数连续试探；后续查询按用户明确的任务范围执行。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-order-global-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 字节（约 8 KB）：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 字节（约 8 KB）：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的顶层状态、计数和用量字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分订单标识**：父单与子单不同，展示时标明层级，定制和核验按子单对应处理。
- **清晰展示数据**：注明店铺、全球区、查询范围及分页情况；表格展示订单状态、时间、待履约数量和警告。保留地址限制、主站合并发货及资质截止提示，不将空结果解释为失败。
- **对齐金额口径**：展示币种、原始金额单位和换算口径；区分供货价、消费者实付和预估结算，V1 与 V2 结构分别解释，公式与单位见接口定义。
- **区分查询与提交**：核验上传会写入店铺订单；依据用户明确范围提交，外层请求正常与 Temu 上传成功分别判断。使用详情中的履约提示决定后续步骤。
- **保护敏感信息**：令牌、解密姓名、电话和详细地址不写入日志或公开渠道，按订单处理需要存储和展示；下载链接与签名材料按授权范围使用。
- **响应处理**：按接口参考检查网关及 Temu 两层结果，保留原始 body 与解析后的 temuBody，不补造缺失字段。
- **响应复用**：业务脚本不读取或保存响应缓存。相同任务已有数据时优先复用已保存文件；令牌存储与响应数据分开管理，详见 [references/api.md](references/api.md)。
- **接入维护**：只有取得完整 Partner 定义后才补充操作；同步接口文档、业务脚本、Partner 目录、文档索引与本页清单，不把未知 type 当作已接入接口。

## 使用示例

### 查单并对账

用户：查看全球区待发货订单，核对这单供货价和税费。

确认店铺后查询订单列表，读取指定父单详情与所需金额版本，按子单对齐展示金额和告警。

### 定制内容和核验上传

用户：查看这些订单的定制内容，并为指定商品提交我提供的 SN。

先从详情确认子单与定制内容，核对 SN 对应商品后按用户范围上传；返回提交结果及后续履约提示。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
