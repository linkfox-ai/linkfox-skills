---
name: linkfox-temu-tax-eu
description: 管理 Temu 欧洲站店铺的电商税务资料，支持月度税务报表导出与下载、文件上传签名、发票摘要和明细查询、发票 PDF 下载以及发票和贷项通知单上传。适用于 EU 店铺发票核对、VAT 明细查看和税务报表整理；不适用于商品维护、订单履约、供货价管理或税务申报代理。
---

# Temu 欧洲站电商税务

## 适用范围

### 适用

处理已授权 Temu 欧洲站店铺的发票、贷项通知单和税务报表。

**场景速查**

| 用户表达 | 查询场景 |
|----------|----------|
| 导出某个月的税务报表 | 申请报表任务，再按任务获取报表文件。 |
| 查这些订单的发票 | 查看发票摘要及订单对应关系。 |
| 看这笔订单的 VAT 和运费 | 查看发票商品、运费和优惠等明细。 |
| 下载发票 PDF | 获取发票加签下载链接及所需文件。 |
| 上传发票或贷项通知单 | 获取文件上传签名，准备文件地址并提交票据。 |

### 边界

商品维护交给 `linkfox-temu-manage-product-eu`，订单金额与订单处理交给 `linkfox-temu-order-eu`，价格与供货价交给 `linkfox-temu-price-eu`，取消订单交给 `linkfox-temu-cancel-order-eu`，发品交给 `linkfox-temu-add-product-us` 的欧洲站能力。

## 接口清单

共 8 个操作：7 个税务业务操作与 1 个加签下载接口。通用代理脚本复用这些操作，不另计接口。

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|------|------|----------|----------|------|
| 申请导出税务报表（`temu.pay.tax.apply.export.report`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body type：`temu.pay.tax.apply.export.report` | `references/apis/temu-pay-tax-apply-export-report.md` | `scripts/eu_tax_apply_export_report.py` | 申请导出税务报表。 |
| 获取 Galerie 签名（`temu.pay.tax.get.galerie.signature`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body type：`temu.pay.tax.get.galerie.signature` | `references/apis/temu-pay-tax-get-galerie-signature.md` | `scripts/eu_tax_get_galerie_signature.py` | 获取 Galerie 签名。 |
| 发票明细查询（`temu.pay.tax.invoice.detail.query`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body type：`temu.pay.tax.invoice.detail.query` | `references/apis/temu-pay-tax-invoice-detail-query.md` | `scripts/eu_tax_invoice_detail_query.py` | 发票明细查询。 |
| 发票信息查询（`temu.pay.tax.invoice.info.query`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body type：`temu.pay.tax.invoice.info.query` | `references/apis/temu-pay-tax-invoice-info-query.md` | `scripts/eu_tax_invoice_info_query.py` | 发票信息查询。 |
| 发票 PDF 下载（`temu.pay.tax.invoice.pdf.download`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body type：`temu.pay.tax.invoice.pdf.download` | `references/apis/temu-pay-tax-invoice-pdf-download.md` | `scripts/eu_tax_invoice_pdf_download.py` | 发票 PDF 下载。 |
| 商家税务报表下载（`temu.pay.tax.merchant.report.download`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body type：`temu.pay.tax.merchant.report.download` | `references/apis/temu-pay-tax-merchant-report-download.md` | `scripts/eu_tax_merchant_report_download.py` | 商家税务报表下载。 |
| 商家上传发票（`temu.pay.tax.merchant.upload.invoice`） | POST `/temu/proxy` → 转发 path：`/temu-proxy/{site}/{managementType}`；Body type：`temu.pay.tax.merchant.upload.invoice` | `references/apis/temu-pay-tax-merchant-upload-invoice.md` | `scripts/eu_tax_merchant_upload_invoice.py` | 商家上传发票。 |
| 加签文件下载 | POST `/temu/fileDownload` | `references/api.md` | `scripts/temu_eu_file_download.py` / `scripts/temu_file_download.py` | 下载加签资源。 |

通用 EU 税务代理：`scripts/temu_eu_proxy.py`；通用入口：`scripts/temu_proxy.py`。详细目录和 Partner 文档标识见 [references/partner-eu-catalog.md](references/partner-eu-catalog.md) 与 [references/apis/README.md](references/apis/README.md)。

## 前置条件

准备 LinkFox 用户密钥和目标 Temu 店铺授权，确认店铺及税务资料。两套令牌用途不同；授权步骤及本地保存方式见 [references/access-token.md](references/access-token.md) 和 [references/authorization-flow.md](references/authorization-flow.md)。
各操作需要的业务资料和限制见对应接口文档；不向用户索取与本次任务无关的信息。

## 税务处理流程

按用户任务选择所需分支，不把以下步骤作为每次都必须执行的请求链。

1. 上传分支：获取 Galerie 文件上传签名，按上传服务要求准备文件 URL，向目标订单提交发票或贷项通知单。
2. 核对分支：查询订单发票摘要，再按需读取发票明细，核对商品、VAT、运费、优惠和附加订单信息。
3. 下载分支：根据发票信息获取 PDF 加签 URL；需要文件下载时使用加签文件下载能力。
4. 报表分支：申请指定月份税务报表，保存请求与任务标识，再按用户任务范围获取商家报表文件。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；需要再次调用时说明原因。业务封装不启用响应缓存，可复用已保存的响应文件。失败或空结果时，不得自动修改参数连续试探；按接口文档核对原因后再决定后续请求。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-tax-eu-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数与状态字段（如 `total`、`costToken`、`success`）、最大列表字段的长度和前 3 条样本。
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

- **区分两套授权**：LinkFox 用户密钥用于网关身份，Temu 店铺令牌用于业务授权；Temu 令牌须由用户在卖家后台手动复制，没有 LinkFox 自动 OAuth。
- **保持目标一致**：展示店铺与区域，按当前店铺和用途选择令牌，不因错误自动切换店铺或区域。
- **清晰展示数据**：摘要用表格列出父订单、发票号码和时间；明细按商品、运费、VAT、优惠与附加订单分组，保留币种及原始金额精度。
- **分别解释结果**：区分网关响应、Temu 调用结果与文件上传结果；下载链接不等于文件已经下载，报表任务创建不等于报表已完成。
- **保留已取得的数据**：错误或空结果时按接口文档解释，不自动重复创建报表、上传或循环轮询。
- **接口扩展约定**：仅在用户提供新 Partner 文档并明确要求扩展时，依据 type、Request/Response 表和可选 sub_menu_code 补充接口文档、调用 `_eu_tax_script.run_cli` 的业务脚本，并同步目录及本清单。

## 使用示例

### 查询订单发票

用户：帮我核对这些订单的发票和 VAT。

确认店铺和订单，先查摘要，再按需读取明细；展示发票对应关系、税额相关原始字段和币种，限制见对应接口参考。

### 导出月度税务报表

用户：导出指定月份的税务报表。

核对月份和店铺，申请任务并保存返回标识，再按实际状态说明文件是否已可下载。

### 上传发票或贷项通知单

用户：把这份发票上传到指定订单。

核对订单、票据方向、接收方和文件，取得上传签名并准备文件地址，提交后分别说明调用和上传结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
