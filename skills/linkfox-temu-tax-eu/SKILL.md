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

## API Usage

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码、接入约定 |
| [partner-eu-catalog.md](./references/partner-eu-catalog.md) | 接口目录 + Partner URL + 脚本（随接入更新） |
| [apis/README.md](./references/apis/README.md) | **按接口分文件**（`apis/<type-slug>.md`） |

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

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/check_linkfox_token.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `eu_tax_apply_export_report.py`, `eu_tax_get_galerie_signature.py`, `eu_tax_invoice_detail_query.py`, `eu_tax_invoice_info_query.py`, `eu_tax_invoice_pdf_download.py`, `eu_tax_merchant_report_download.py`, `eu_tax_merchant_upload_invoice.py`, `get_temu_access_token.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_eu_file_download.py`, `temu_eu_proxy.py`, `temu_file_download.py`, `temu_proxy.py`, `temu_token_guide.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
