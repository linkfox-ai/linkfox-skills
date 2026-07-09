---
name: linkfox-temu-tax-eu
description: Temu 欧洲站电商税务（Tax）API，经 LinkFox 网关转发 Partner EU 7 个 temu.pay.tax.* 接口：导出报表、Galerie签名、发票查询/下载、商家报表下载/上传发票等。当用户提到 Temu EU Tax、temu.pay.tax.invoice、VAT、发票上传、export report、Galerie signature、site=eu 税务 时触发。商品管理用 linkfox-temu-manage-product-eu。
---

# Temu 欧洲站 — 电商税务（Tax）

本 skill（`linkfox-temu-tax-eu`）覆盖 Partner Platform for EU **Tax / 电商税务** 相关 OpenAPI（`menu_code` 与各 `sub_menu_code` 以 Partner 后台为准，见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)）。

> 当前已接入 **7** 个接口；其余 Tax 接口将按 Partner 文档逐条补充。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 税务 OpenAPI（`eu_tax_*`、`temu_eu_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 商品列表/编辑/合规（含 `taxCodeInfo` 等字段） | `linkfox-temu-manage-product-eu` |
| 订单金额（含税/不含税明细） | `linkfox-temu-order-eu` |
| 价格/供货价 | `linkfox-temu-price-eu` |
| 买家/卖家取消订单 | `linkfox-temu-cancel-order-eu` |
| 发品 | `linkfox-temu-add-product-us`（`site=eu`） |
| 网关与 Temu token | 本 skill `scripts/` |

## 调用方式

- **API 端点**：`POST /temu/proxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-tax-eu-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `eu` | Partner EU |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `product-inventory` | 酷鸟卖家助手 token（若 Partner 要求其它 purpose，以文档为准） |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（`storeKey` 时建议带 `tokenPurpose=product-inventory`）

## Scripts（按 type）

| 脚本 | type | 状态 |
|------|------|------|
| `eu_tax_apply_export_report.py` | `temu.pay.tax.apply.export.report` | 已接入 |
| `eu_tax_get_galerie_signature.py` | `temu.pay.tax.get.galerie.signature` | 已接入 |
| `eu_tax_invoice_detail_query.py` | `temu.pay.tax.invoice.detail.query` | 已接入 |
| `eu_tax_invoice_info_query.py` | `temu.pay.tax.invoice.info.query` | 已接入 |
| `eu_tax_invoice_pdf_download.py` | `temu.pay.tax.invoice.pdf.download` | 已接入 |
| `eu_tax_merchant_report_download.py` | `temu.pay.tax.merchant.report.download` | 已接入 |
| `eu_tax_merchant_upload_invoice.py` | `temu.pay.tax.merchant.upload.invoice` | 已接入 |
| `temu_eu_proxy.py` | 任意 `type` | 通用 |
| `temu_eu_file_download.py` | 加签文件下载 | 通用 |

## 接入新接口（约定）

你每提供一条 Partner 文档（HTML/URL + `type` + Request/Response 表 + 可选 `sub_menu_code`），将：

1. 新增 `references/apis/<type-slug>.md`（入参/出参层级全部展开）
2. 新增 `scripts/eu_tax_<slug>.py`（调用 `_eu_tax_script.run_cli`）
3. 更新 [partner-eu-catalog.md](./references/partner-eu-catalog.md)、[apis/README.md](./references/apis/README.md) 与本表

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 发票信息查询（最多 20 个父单号）
python scripts/eu_tax_invoice_info_query.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "product-inventory",
  "site": "eu",
  "request": {
    "parentOrderSnList": ["PO-123456789"]
  }
}'

# 申请导出税务报表（月份 YYYY-MM）
python scripts/eu_tax_apply_export_report.py '{
  "accessToken": "TOKEN",
  "request": {
    "reportMonth": "2025-04",
    "requestId": "req-uuid-001"
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-tax-eu`

## 网关与授权脚本

授权说明：[references/access-token.md](./references/access-token.md)

