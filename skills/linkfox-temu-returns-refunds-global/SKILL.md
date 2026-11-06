---
name: linkfox-temu-returns-refunds-global
description: 查询和处理 Temu 全球站退货退款售后，支持父子售后单列表、父售后详情与退款汇总、退货物流、退货地址、面单准备、承运商、售后签名、面单上传和加签文件下载。适用于已授权店铺的退货退款查询与面单处理；不适用于取消订单、商品管理或常规发货。
---
# Temu 全球站退货与退款

## 适用范围

### 适用

管理已授权 Temu 全球站店铺的退货退款售后。用户需要查父子售后单、了解退款金额与原因、安排退货面单或跟踪退货包裹时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查看这段时间待处理的退货退款 | 父售后单列表与详情。 |
| 这笔售后涉及哪些商品、退多少钱 | 子售后行项、退款汇总与原因。 |
| 准备并上传退货面单 | 退货仓、揽收时间、承运商和面单提交。 |
| 买家寄回哪里、退货运单到哪了 | 退货地址与退货物流。 |
| 获取售后签名或下载加签文件 | 售后签名与文件下载。 |

### 边界

取消订单使用 `linkfox-temu-cancel-order-global`；缺少订单上下文时使用 `linkfox-temu-order-global`。商品管理和常规履约不属于本技能范围。

## 接口清单

九项具名售后操作加一项文件下载，共 10 项。通用代理和 Token 校验复用 `/temu/proxy`，不另增具名业务操作。`type` 位于请求体，并非 URL 字段；转发路径的具体参数见接口参考。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 子售后单列表查询（`bg.aftersales.aftersales.list.get`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.aftersales.aftersales.list.get` | `references/apis/bg-aftersales-aftersales-list-get.md` | `scripts/global_returns_refunds_aftersales_aftersales_list_get.py` | 读取子售后行项和商品信息。 |
| 父售后单列表查询（`bg.aftersales.parentaftersales.list.get`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.aftersales.parentaftersales.list.get` | `references/apis/bg-aftersales-parentaftersales-list-get.md` | `scripts/global_returns_refunds_aftersales_parentaftersales_list_get.py` | 按时间和状态定位父售后单。 |
| 父退货物流信息（`bg.aftersales.parentreturnorder.get`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=bg.aftersales.parentreturnorder.get` | `references/apis/bg-aftersales-parentreturnorder-get.md` | `scripts/global_returns_refunds_aftersales_parentreturnorder_get.py` | 读取承运商、退货仓和物流单号。 |
| 承运商列表（`temu.aftersales.carrier.get`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.aftersales.carrier.get` | `references/apis/temu-aftersales-carrier-get.md` | `scripts/global_returns_refunds_aftersales_carrier_get.py` | 按退货仓区域查询承运商。 |
| 父售后单详情（`temu.aftersales.parentaftersales.detail.get`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.aftersales.parentaftersales.detail.get` | `references/apis/temu-aftersales-parentaftersales-detail-get.md` | `scripts/global_returns_refunds_aftersales_parentaftersales_detail_get.py` | 读取退款汇总、原因和子售后单。 |
| 退货地址查询（`temu.aftersales.returnaddress.get`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.aftersales.returnaddress.get` | `references/apis/temu-aftersales-returnaddress-get.md` | `scripts/global_returns_refunds_aftersales_returnaddress_get.py` | 查询可用的买家寄回地址。 |
| 退货面单准备信息（`temu.aftersales.returnlabel.prepare.get`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.aftersales.returnlabel.prepare.get` | `references/apis/temu-aftersales-returnlabel-prepare-get.md` | `scripts/global_returns_refunds_aftersales_returnlabel_prepare_get.py` | 读取可用退货仓和揽收时间。 |
| 售后签名获取（`temu.aftersales.signature.get`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.aftersales.signature.get` | `references/apis/temu-aftersales-signature-get.md` | `scripts/global_returns_refunds_aftersales_signature_get.py` | 获取后续售后操作使用的签名。 |
| 上传退货面单（`temu.aftersales.upload.returnlabel`） | POST `/temu/proxy`；转发 path：`/temu-proxy/{site}/{managementType}`；Body `type=temu.aftersales.upload.returnlabel` | `references/apis/temu-aftersales-upload-returnlabel.md` | `scripts/global_returns_refunds_aftersales_upload_returnlabel.py` | 提交退货面单、物流及揽收信息。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_global_file_download.py`、`scripts/temu_file_download.py` | 请求下载加签资源，按真实响应展示结果。 |

## 前置条件

先确认目标店铺和全球站售后上下文。LinkFox 用户密钥与 Temu 店铺令牌分别配置；Temu 令牌须从卖家后台手动授权取得，可直接使用或保存在本地后按店铺读取。见 [授权与本地存储](references/access-token.md) 和 [授权流程](references/authorization-flow.md)。各接口所需信息见 [接口参考](references/api.md)。

## 退货退款流程

1. 按需取得订单与售后上下文，确定目标店铺及查询范围。
2. 查询父售后单列表，取得父售后单号；查询父售后详情，了解退款汇总、子单及可执行操作，再按需查子售后行项。
3. 需要面单时，先获取面单准备信息中的退货仓和揽收时间，再查询承运商；后续操作确需签名时获取售后签名，不推断未定义的签名入参。
4. 在用户已指定的操作范围内提交面单与物流信息；退货寄出后查询父退货物流。买家自行寄回时，按需先查退货地址。
5. 需要下载加签文件时使用文件下载入口。每一步以实际返回的数据和可执行状态决定是否继续，不把整条流程作为必调清单。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次；业务脚本不读写响应缓存，已有响应优先从落盘文件读取。失败或空结果时，不得自动修改条件、翻页或连续试探；需要继续查询时，先说明查询范围和原因。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-returns-refunds-global-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、常见字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分单号**：父订单、子订单、父售后、子售后各有独立标识，不混用；对应关系以响应为准。
- **展示售后上下文**：注明店铺和站点，用表格展示售后状态、商品、件数、退款金额及币种、原因、退货仓、承运商和物流单号。时间注明时区，秒和毫秒按接口定义解释。
- **区分查询与提交**：上传面单会改变售后资料；依据用户已明确的目标和范围准备请求。提交结果和退款最终状态分别说明，具体判断见接口参考。
- **处理无数据与错误**：展示本次查询范围和分页情况，保留已有数据；错误原因按接口参考解释，不凭错误消息补造售后结果。
- **兼容入口**：`scripts/temu_global_proxy.py` 为 Global 通用代理，`scripts/temu_proxy.py` 为多站点兼容代理；它们不扩大本技能的业务范围。本地授权脚本、环境变量和缓存运行约定见接口参考。
- **维护已有能力**：只有拿到新增接口的完整 Partner 类型、文档和请求响应定义后才扩展接入，并同步接口参考、专用入口与 [Partner 目录](references/partner-global-catalog.md)；不预设尚未接入的退款执行能力。

## 使用示例

### 查询待处理售后

用户：查看这段时间的待处理退货退款，并展开其中一笔。

确定时间范围和目标店铺，查询父售后单列表，再用返回的单号取得详情和需要的子售后行项，展示状态、退款汇总和返回范围。

### 上传退货面单并查看退货物流

用户：给这笔售后上传我提供的面单，然后查看退货运单。

核对目标售后与订单，按需查询面单准备信息、退货仓和承运商，依据用户资料提交，分别解释上传结果和退货物流结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
