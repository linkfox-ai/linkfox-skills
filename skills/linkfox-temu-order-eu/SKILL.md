---
name: linkfox-temu-order-eu
description: 管理 Temu 欧洲站订单，支持订单列表与详情、常规及敏感收货地址、供货价与金额对账、可合并发货订单组、定制商品内容、SN/IMEI 和二手鉴真信息上传及相关文件下载。适用于已授权店铺的欧洲站订单处理和发货准备；不适用于美国站或全球站订单、商品维护、定价、取消、退货退款和实际发货履约。
---
# Temu 欧洲站订单管理

## 适用范围

### 适用

查看和处理已授权 Temu 欧洲站店铺的订单，准备发货所需的地址、定制内容和核验资料。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查欧洲店铺待发货订单，再看某单详情 | 订单列表与详情。 |
| 获取这笔订单的收货地址 | 常规地址；业务需要时查询敏感地址。 |
| 核对供货价、收入和消费者实付 | 订单金额与 ERP 对账。 |
| 哪些订单可以合并发货 | 可合并发货父订单组。 |
| 下载这笔订单的定制内容 | 定制文字、图文、SVG 或压缩包。 |
| 上传这些商品的 SN、IMEI 或二手鉴真编码 | 订单核验信息上传。 |

### 边界

美国站和全球站订单分别使用 `linkfox-temu-order-us`、`linkfox-temu-order-global`。商品维护、定价、取消、退货退款、实际发货分别使用 `linkfox-temu-manage-product-eu`、`linkfox-temu-price-eu`、`linkfox-temu-cancel-order-eu`、`linkfox-temu-returns-refunds-eu`、`linkfox-temu-fulfillment-eu`。发品可参考 `linkfox-temu-add-product-us`，使用前需核实适用站点，不将其视为 EU 发品能力。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 订单列表查询 V2（`bg.order.list.v2.get`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`bg.order.list.v2.get` | `references/apis/bg-order-list-v2-get.md` | `scripts/eu_order_list_v2_get.py` | 读取对应订单数据。 |
| 订单详情查询 V2（`bg.order.detail.v2.get`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`bg.order.detail.v2.get` | `references/apis/bg-order-detail-v2-get.md` | `scripts/eu_order_detail_v2_get.py` | 读取对应订单数据。 |
| 订单收货地址查询 V2（`bg.order.shippinginfo.v2.get`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`bg.order.shippinginfo.v2.get` | `references/apis/bg-order-shippinginfo-v2-get.md` | `scripts/eu_order_shippinginfo_v2_get.py` | 读取对应订单数据。 |
| 订单收货地址解密查询（`bg.order.decryptshippinginfo.get`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`bg.order.decryptshippinginfo.get` | `references/apis/bg-order-decryptshippinginfo-get.md` | `scripts/eu_order_decryptshippinginfo_get.py` | 读取对应订单数据。 |
| 订单金额/供货价查询（`bg.order.amount.query`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`bg.order.amount.query` | `references/apis/bg-order-amount-query.md` | `scripts/eu_order_amount_query.py` | 读取对应订单数据。 |
| 订单金额查询 V2（`temu.order.amount.v2.query`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`temu.order.amount.v2.query` | `references/apis/temu-order-amount-v2-query.md` | `scripts/eu_order_amount_v2_query.py` | 读取对应订单数据。 |
| 订单金额查询 V3（`temu.order.amount.v3.query`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`temu.order.amount.v3.query` | `references/apis/temu-order-amount-v3-query.md` | `scripts/eu_order_amount_v3_query.py` | 读取对应订单数据。 |
| 可合并发货订单组列表（`bg.order.combinedshipment.list.get`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`bg.order.combinedshipment.list.get` | `references/apis/bg-order-combinedshipment-list-get.md` | `scripts/eu_order_combinedshipment_list_get.py` | 读取对应订单数据。 |
| 订单定制商品内容批量查询（`bg.order.customization.get`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`bg.order.customization.get` | `references/apis/bg-order-customization-get.md` | `scripts/eu_order_customization_get.py` | 读取对应订单数据。 |
| 订单核验信息上传（`temu.local.order.verification.upload`） | POST `/temu/proxy` -> path：`/openapi/router`；type：`temu.local.order.verification.upload` | `references/apis/temu-local-order-verification-upload.md` | `scripts/eu_order_verification_upload.py` | 上传订单核验信息。 |
| 加签文件下载 | POST `/temu/fileDownload` -> path：请求中的 `url` | `references/api.md` | `scripts/temu_eu_file_download.py`、`scripts/temu_file_download.py` | 下载 Temu 加签资源。 |

## 前置条件

先确定目标店铺、区域和操作范围，具备 LinkFox 密钥及目标店铺的 Temu 授权。Temu 授权需在卖家后台手动完成；获取、保存与按店铺读取令牌见 [授权说明](references/access-token.md) 和 [授权流程](references/authorization-flow.md)。通用转发入口 `scripts/temu_eu_proxy.py`、`scripts/temu_proxy.py` 复用同一网关。接口参数、默认值、使用限制和脚本兼容约定见 [接口参考](references/api.md)，官方菜单与文档线索见 [Partner EU 目录](references/partner-eu-catalog.md)。

## 订单处理流程

1. 按用户指定的状态、时间或父订单范围查询列表，再按需读取详情。
2. 发货准备时读取常规收货地址，检查返回的地址及履约限制；确需明文敏感信息时再查解密地址。
3. ERP 对账时按店铺所在国/区域选取适用金额版本：V1 查询供货价；欧洲含税价对账优先 V3，需要细粒度税费拆分时用 V2。按父单与子单关系对齐。
4. 需要合并发货时查询可合并父单组，再按需获取组内地址；合并确认和面单操作转交履约技能。
5. 定制订单先从列表或详情取得子订单，再读取定制内容；需要素材时按接口参考中的下载要求处理。
6. 需要核验的订单按实际商品准备 SN、IMEI 或二手鉴真编码，在用户授权范围内上传，再交由履约流程发货。取消、退货退款使用对应技能。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，脚本不启用响应缓存。失败或空结果时，不得自动更换筛选条件、翻页或连续试探；需要扩大查询范围时，先向用户说明后续查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-order-eu-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`）和响应中存在的 `costToken` 等字段、最大列表字段的长度和前 3 条样本。
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

- **区分订单标识**：父订单对应整笔订单，子订单对应具体商品；定制内容和核验信息按子订单对齐，不能混用。
- **区分金额口径**：供货价、卖家收入与消费者实付分别展示；V2 拆分税费，V3 侧重含税价。金额展示注明币种与单位，计算公式及空值语义见对应接口文档。
- **展示订单状态和限制**：先列目标店铺、区域、查询范围和分页情况，再展示父子订单、商品、需履约数量、时间与告警。保留地址变更、自提、指定物流、主站合并和资质上传提示的业务含义。
- **保护敏感信息**：解密地址含姓名、电话和详细地址，只在授权的订单处理范围内使用；业务展示脱敏，不额外复制到诊断日志或公开渠道。按输出策略保存的完整响应也须妥善保护。
- **区分读取与写入**：核验上传会改变订单资料；根据用户指定的订单和内容操作，结果不确定时先核实，避免重复上传。
- **保留数据与解释失败**：按接口参考区分网关、转发和 Temu 业务结果，保留原始响应与告警；空列表只表示当前条件无匹配数据。不得把未接入的合并确认或面单能力描述为已完成。
- **遵循实际缓存行为**：业务脚本调用公共调用器时始终传入 `--no-cache`，不读写响应缓存；本地令牌存储与响应缓存分开，具体运行约定见接口参考。
- **维护接口目录**：后续有新的 Partner 文档时，在本技能的接口目录、分接口文档、薄封装和清单中同步维护。

## 使用示例

### 查看待发货订单并准备地址

用户：查欧洲店铺的待发货订单，查看指定订单的详情和收货限制。

先查订单列表，再读取用户指定订单的详情与常规地址，展示限制及后续履约所需信息。

### 核对订单金额

用户：核对这笔欧洲订单的收入和消费者实付。

按店铺区域与对账口径选取金额版本，展示父单汇总和子单明细，注明税费口径、币种和告警。

### 获取定制内容或上传核验资料

用户：下载这个定制商品的文件，并为指定订单上传我提供的序列号。

从详情核对子订单，取得定制内容与下载资源；核对用户指定的核验资料后上传，说明每一步的实际返回结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
