---
name: linkfox-temu-returns-refunds-us
description: 查询和处理 Temu 美国站退货退款售后，支持父子售后单、退款明细、退货物流、寄回地址、承运商、揽收准备、售后签名、上传退货面单及加签文件下载。适用于已授权店铺的退货退款跟进和面单处理；不适用于买卖家取消订单、商品管理或常规订单履约。
---
# Temu 美国站退货与退款

## 适用范围

### 适用

围绕已授权 Temu 美国站店铺的退货退款售后，查询父子售后单与退款明细，准备或上传退货面单，并跟进退货物流。

**场景速查**

| 用户表达 | 查询场景 |
|------|------|
| 看这段时间有哪些退货退款售后 | 父售后单列表与子售后行项。 |
| 这笔退款包括哪些费用，买家为什么退货 | 父售后详情、退款汇总与原因。 |
| 查买家寄回地址或退货运单 | 地址与退货物流查询。 |
| 为这笔售后准备并上传面单 | 退货仓、揽收时间、承运商、签名与上传结果。 |
| 下载售后相关的加签资源 | 使用店铺授权信息转发下载请求。 |

### 边界

买家或卖家取消订单使用 `linkfox-temu-cancel-order-us`；订单上下文使用 `linkfox-temu-order-us`；商品管理与常规履约分别使用 `linkfox-temu-manage-product-us`、`linkfox-temu-fulfillment-us`。本技能已接入的操作以接口清单为准，不承诺未定义的直接发起退款或审批能力。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 子售后单列表查询（`bg.aftersales.aftersales.list.get`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=bg.aftersales.aftersales.list.get` | `references/apis/bg-aftersales-aftersales-list-get.md` | `scripts/us_returns_refunds_aftersales_aftersales_list_get.py` | 子售后单列表查询。 |
| 父售后单列表查询（`bg.aftersales.parentaftersales.list.get`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=bg.aftersales.parentaftersales.list.get` | `references/apis/bg-aftersales-parentaftersales-list-get.md` | `scripts/us_returns_refunds_aftersales_parentaftersales_list_get.py` | 父售后单列表查询。 |
| 父退货物流信息（`bg.aftersales.parentreturnorder.get`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=bg.aftersales.parentreturnorder.get` | `references/apis/bg-aftersales-parentreturnorder-get.md` | `scripts/us_returns_refunds_aftersales_parentreturnorder_get.py` | 父退货物流信息。 |
| 承运商列表（`temu.aftersales.carrier.get`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=temu.aftersales.carrier.get` | `references/apis/temu-aftersales-carrier-get.md` | `scripts/us_returns_refunds_aftersales_carrier_get.py` | 承运商列表。 |
| 父售后单详情（`temu.aftersales.parentaftersales.detail.get`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=temu.aftersales.parentaftersales.detail.get` | `references/apis/temu-aftersales-parentaftersales-detail-get.md` | `scripts/us_returns_refunds_aftersales_parentaftersales_detail_get.py` | 父售后单详情。 |
| 退货地址查询（`temu.aftersales.returnaddress.get`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=temu.aftersales.returnaddress.get` | `references/apis/temu-aftersales-returnaddress-get.md` | `scripts/us_returns_refunds_aftersales_returnaddress_get.py` | 退货地址查询。 |
| 退货面单准备信息（`temu.aftersales.returnlabel.prepare.get`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=temu.aftersales.returnlabel.prepare.get` | `references/apis/temu-aftersales-returnlabel-prepare-get.md` | `scripts/us_returns_refunds_aftersales_returnlabel_prepare_get.py` | 退货面单准备信息。 |
| 售后签名获取（`temu.aftersales.signature.get`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=temu.aftersales.signature.get` | `references/apis/temu-aftersales-signature-get.md` | `scripts/us_returns_refunds_aftersales_signature_get.py` | 售后签名获取。 |
| 上传退货面单（`temu.aftersales.upload.returnlabel`） | POST `/temu/proxy` -> 转发 path：`/openapi/router`；Body `type=temu.aftersales.upload.returnlabel` | `references/apis/temu-aftersales-upload-returnlabel.md` | `scripts/us_returns_refunds_aftersales_upload_returnlabel.py` | 上传退货面单。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_us_file_download.py`、`scripts/temu_file_download.py` | 转发加签资源下载。 |

## 前置条件

**先确定店铺、站点和售后目标**：LinkFox 密钥与 Temu 店铺授权分别配置。Temu Token 由用户在卖家后台手动获取，可直接提供或通过本地店铺记录读取；详见 [授权说明](references/access-token.md) 与 [授权流程](references/authorization-flow.md)。网关字段、Token 匹配和工具 CLI 见 [运行约定](references/api.md#运行约定)。

## 退货退款处理流程

1. 取得目标店铺的订单和售后上下文；缺少订单信息时通过订单技能获取。
2. 根据用户指定范围查询父售后单列表，再按需读取父售后详情与子售后行项，核对退款汇总、售后状态和可执行操作。
3. 需要处理面单时，先查询退货仓与揽收准备信息，再查询承运商；后续操作确有签名要求时获取售后签名。
4. 按用户明确的售后处理范围提交面单与物流信息，解释上传结果；寄出后按需查询退货运单。买家自行寄回的场景先查询寄回地址。
5. 仅在任务需要时使用加签文件下载；保留原始响应与已取得的数据。操作参数、限制和错误处理详见各接口文档，不为完整跑流程而额外调用无关操作。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次，优先复用已保存的响应。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续查询时，先说明原因与调用范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-returns-refunds-us-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- UTF-8 响应体不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- UTF-8 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见状态和计数（如 `success`、`total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分单号和业务层级**：父订单、子订单、父售后单与子售后单是不同对象；先核对其归属，再按目标售后单跟进，不把取消订单混作退货退款。
- **清晰展示数据**：标明店铺与美国站，先展示售后状态与退款汇总，再列子售后行项、原因、面单或物流结果；金额带响应币种，时间带单位和时区，缺失项不补造。
- **解释操作条件**：依据卖家可执行操作与截止时间判断下一步，区分请求完成和业务成功。上传成功不代表已完成退款，具体判断见接口参考。
- **脚本入口**：9 个专用业务脚本以接口清单为准；US 通用入口为 `scripts/temu_us_proxy.py`，多站点兼容入口为 `scripts/temu_proxy.py`。本地 Token 工具与鉴权探测见运行约定，不主动探测或遍历店铺。
- **响应缓存**：业务封装按 [运行约定](references/api.md#运行约定) 禁用公共调用器响应缓存，不读写响应缓存文件；已保存的响应可按需读取。
- **维护接口来源**：[Partner US 目录](references/partner-us-catalog.md) 保留菜单编号、子菜单编号与官方来源；[接口文档索引](references/apis/README.md) 提供全部单接口文档。新增操作须以用户提供的完整 Partner 定义为依据，按运行约定同步目录与脚本。

## 使用示例

### 查询退款明细

用户：看看这笔售后退了哪些费用，关联哪些商品。

核对店铺和售后目标，查询父售后详情，按币种展示退款汇总与子售后行项，必要时补查子单列表。

### 上传退货面单

用户：为指定售后单上传我提供的退货面单。

核对目标售后及用户提供的面单，按需查询准备信息与承运商，再提交面单，展示实际业务结果。

### 跟进寄回地址和物流

用户：查这笔退货应该寄到哪里，是否已经有退货运单。

按售后场景查询寄回地址与退货物流，说明地址是否可查及已有跟踪信息，不自动附带面单上传。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
