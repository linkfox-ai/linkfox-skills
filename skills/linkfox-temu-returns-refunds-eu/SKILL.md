---
name: linkfox-temu-returns-refunds-eu
description: 管理 Temu 欧洲站退货与退款售后，查询父子售后单、退款明细、退货物流和寄回地址，准备退货面单、查询承运商与售后签名、提交面单并获取加签资源。适用于已授权店铺的 EU 售后跟踪与退货履约；不适用于取消订单、普通订单查询、商品管理或发货履约。
---

# Temu 欧洲站退货与退款

## 适用范围

### 适用

处理 Partner EU 的 Return and Refund / 售后退货退款业务，覆盖已接入的 9 个售后操作及加签文件下载。

**场景速查**

| 用户表达 | 查询场景 |
|------|------|
| 看欧洲站最近待处理的退货退款 | 查询父售后单，再看详情与子售后行。 |
| 这笔售后退了多少钱、包含哪些 SKU | 展示退款汇总及子售后明细。 |
| 为这个退货提交面单 | 获取面单准备信息、承运商，按需取签名，再提交面单。 |
| 看退货寄回哪里、运单走到哪 | 按场景查询寄回地址、退货仓和跟踪号。 |
| 获取这张 Temu 加签面单资源 | 调用加签下载并解释网关返回。 |

### 边界

买家或卖家取消订单（含缺货取消、申诉）转交 `linkfox-temu-cancel-order-eu`；订单列表、详情、金额与售后上下文转交 `linkfox-temu-order-eu`。商品管理和普通发货履约分别使用 `linkfox-temu-manage-product-eu` 与 `linkfox-temu-fulfillment-eu`。美区、全球区售后分别使用 `linkfox-temu-returns-refunds-us`、`linkfox-temu-returns-refunds-global`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|------|------|------|------|------|
| 子售后单列表查询（`bg.aftersales.aftersales.list.get`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`bg.aftersales.aftersales.list.get` | [bg-aftersales-aftersales-list-get.md](references/apis/bg-aftersales-aftersales-list-get.md) | `scripts/eu_returns_refunds_aftersales_aftersales_list_get.py` | 子售后单列表查询。 |
| 父售后单列表查询（`bg.aftersales.parentaftersales.list.get`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`bg.aftersales.parentaftersales.list.get` | [bg-aftersales-parentaftersales-list-get.md](references/apis/bg-aftersales-parentaftersales-list-get.md) | `scripts/eu_returns_refunds_aftersales_parentaftersales_list_get.py` | 父售后单列表查询。 |
| 父退货物流信息（`bg.aftersales.parentreturnorder.get`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`bg.aftersales.parentreturnorder.get` | [bg-aftersales-parentreturnorder-get.md](references/apis/bg-aftersales-parentreturnorder-get.md) | `scripts/eu_returns_refunds_aftersales_parentreturnorder_get.py` | 父退货物流信息。 |
| 承运商列表（`temu.aftersales.carrier.get`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`temu.aftersales.carrier.get` | [temu-aftersales-carrier-get.md](references/apis/temu-aftersales-carrier-get.md) | `scripts/eu_returns_refunds_aftersales_carrier_get.py` | 承运商列表。 |
| 父售后单详情（`temu.aftersales.parentaftersales.detail.get`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`temu.aftersales.parentaftersales.detail.get` | [temu-aftersales-parentaftersales-detail-get.md](references/apis/temu-aftersales-parentaftersales-detail-get.md) | `scripts/eu_returns_refunds_aftersales_parentaftersales_detail_get.py` | 父售后单详情。 |
| 退货地址查询（`temu.aftersales.returnaddress.get`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`temu.aftersales.returnaddress.get` | [temu-aftersales-returnaddress-get.md](references/apis/temu-aftersales-returnaddress-get.md) | `scripts/eu_returns_refunds_aftersales_returnaddress_get.py` | 退货地址查询。 |
| 退货面单准备信息（`temu.aftersales.returnlabel.prepare.get`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`temu.aftersales.returnlabel.prepare.get` | [temu-aftersales-returnlabel-prepare-get.md](references/apis/temu-aftersales-returnlabel-prepare-get.md) | `scripts/eu_returns_refunds_aftersales_returnlabel_prepare_get.py` | 退货面单准备信息。 |
| 售后签名获取（`temu.aftersales.signature.get`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`temu.aftersales.signature.get` | [temu-aftersales-signature-get.md](references/apis/temu-aftersales-signature-get.md) | `scripts/eu_returns_refunds_aftersales_signature_get.py` | 售后签名获取。 |
| 上传退货面单（`temu.aftersales.upload.returnlabel`） | POST `/temu/proxy` → 上游 path：`/openapi/router`，Body.type：`temu.aftersales.upload.returnlabel` | [temu-aftersales-upload-returnlabel.md](references/apis/temu-aftersales-upload-returnlabel.md) | `scripts/eu_returns_refunds_aftersales_upload_returnlabel.py` | 上传退货面单。 |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md) | `scripts/temu_eu_file_download.py` | 获取加签资源的网关响应。 |

## 前置条件

先确定店铺、EU 站点和售后目标，并准备已授权的 Temu 店铺令牌。LinkFox 用户认证与 Temu 店铺认证各自独立，手动授权步骤及本地保存方式见 [references/access-token.md](references/access-token.md) 与 [references/authorization-flow.md](references/authorization-flow.md)。缺少订单上下文时先从订单技能取得。

## 退货退款流程

1. 从订单上下文确认父订单与售后目标，按用户范围查询父售后单。
2. 查询父售后详情，查看退款汇总、可操作项与子售后；需要 SKU 或行项信息时查询子售后列表。
3. 需要提供面单时，先查询面单准备信息，确定可用退货仓和揽收时段，再查询对应承运商。
4. 后续操作要求签名时先获取售后签名，依据用户授权的退货目标提交面单、运单及揽收信息。
5. 退货寄出后查询父退货运单与退货仓；买家自寄场景按需查询寄回地址，通常在发货或上传面单前取得。
6. 需要读取加签资源时使用下载入口，保存并解释实际网关结果。各环节已有数据足够时直接复用，流程不要求把全部接口逐一调用。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：算力规则见下方“算力消耗预估”。同一会话、同一参数组合默认只调用一次，复用已保存的响应；脚本不提供响应缓存。失败或空结果时，不得自动翻页或修改查询条件连续试探；需要继续查询时，先向用户说明查询目标与范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-returns-refunds-eu-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8,000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8,000 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分业务对象**：父订单、父售后、子售后与退货物流关联展示，避免混淆单号；售后不等于取消订单。
- **清晰展示数据**：注明店铺与站点，展示状态、退款币种和金额、关联 SKU、可操作事项及截止时间；物流结果展示退货仓、承运商与跟踪号，缺失字段不补造。
- **依据当前售后状态处理**：提交面单前核对可执行操作与时限，区分平台已退款、退货寄出和面单提交成功。参数与限制、地址能力限制及错误处理见各接口文档。
- **店铺授权方式**：Temu 令牌由用户在卖家后台手动授权复制，本地 CLI 按用途和站点存储、读取；列表默认脱敏，`get_temu_access_token.py` 指定读取时返回原令牌；不提供自动 OAuth。LinkFox 凭据不当作店铺令牌。
- **使用适合的入口**：专用脚本固定售后操作；`scripts/temu_eu_proxy.py` 为 EU 通用代理，`scripts/temu_proxy.py` 与 `scripts/temu_file_download.py` 支持多站点调用，运行约定及辅助 CLI 见 [references/api.md](references/api.md)。
- **复用响应并解释结果**：遵循上方成本约束，复用会话中已保存的响应；脚本不读写响应缓存，细则见接口运行约定。区分网关响应与 Temu 业务结果，不能把空结果或请求完成解释为售后处理完成。
- **接口目录维护**：Partner EU 菜单、文档入口和后续接入维护约定见 [references/partner-eu-catalog.md](references/partner-eu-catalog.md)，详细索引见 [references/apis/README.md](references/apis/README.md)。

## 使用示例

### 查询待处理退货与退款

用户：查看欧洲站最近的待处理售后，以及其中一笔的退款明细。

确认目标店铺与时间范围，查询父售后列表，再读取指定父售后详情；需要商品行项时查询子售后列表，展示当前状态与退款构成。

### 提交退货面单

用户：为这笔欧洲站退货提交我提供的面单和运单信息。

确认用户指定的售后目标，查询面单准备信息与承运商，按需取得签名，再提交面单，说明实际业务结果与后续退货物流查询方式。

### 查询寄回地址与退货物流

用户：这笔退货应该寄往哪里，寄出后查一下运单。

按当前售后场景查询寄回地址；寄出后查询父退货物流并展示跟踪号与退货仓。下载资源时使用加签下载入口。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
