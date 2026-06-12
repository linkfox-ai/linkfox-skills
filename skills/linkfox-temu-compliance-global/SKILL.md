---
name: linkfox-temu-compliance-global
description: Temu 全球站电商合规（Compliance）API，经 LinkFox 网关转发 Partner Global 合规相关 OpenAPI（bg.compliance.*、bg.arbok.open.*、bg.flash.open.* 等，共 9 个接口）。当用户提到 Temu Global 合规、商品资质、GPSR、治理属性、实拍图、资质上传、bg.compliance.edit、arbok cert、site=global 合规 时触发。
---

# Temu 全球站 — 电商合规（Compliance）

本 skill（`linkfox-temu-compliance-global`）覆盖 Partner Platform for **Global** 的 **电商合规 / Product Compliance** 相关 OpenAPI。

已接入 **9** 个接口，清单见 [partner-global-catalog.md](./references/partner-global-catalog.md)。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 合规 OpenAPI（`global_compliance_*`、`temu_global_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| **电商合规**（本 skill） | **`linkfox-temu-compliance-global`** |
| 商品列表/详情/编辑/库存 | `linkfox-temu-manage-product-global` |
| 价格 | `linkfox-temu-price-global` |
| 促销 | `linkfox-temu-promotion-global` |
| 网关与 Temu token | 本 skill `scripts/` |

## API Usage

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码 |
| [partner-global-catalog.md](./references/partner-global-catalog.md) | 接口目录 |
| [apis/README.md](./references/apis/README.md) | 分接口文档 |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `global` | Partner Global |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `product-inventory` | 商品/合规场景 |

## Scripts（按 type）

| 脚本 | type | 状态 |
|------|------|------|
| `global_compliance_edit.py` | `bg.compliance.edit` | 已接入 |
| `global_compliance_metadata_get.py` | `bg.compliance.metadata.get` | 已接入 |
| `global_compliance_goods_compliancelabel_get.py` | `bg.goods.compliancelabel.get` | 已接入 |
| `global_compliance_arbok_cert_query_need_upload_items.py` | `bg.arbok.open.cert.queryNeedUploadItems` | 已接入 |
| `global_compliance_arbok_cert_upload_product_cert.py` | `bg.arbok.open.cert.uploadProductCert` | 已接入 |
| `global_compliance_flash_upload_recognize.py` | `bg.flash.open.upload.recognize` | 已接入 |
| `global_compliance_flash_upload_real_image.py` | `bg.flash.open.upload.real.image` | 已接入 |
| `global_compliance_arbok_upload_upload_file.py` | `bg.arbok.open.upload.uploadFile` | 已接入 |
| `global_compliance_arbok_product_cert_query.py` | `bg.arbok.open.product.cert.query` | 已接入 |
| `temu_global_proxy.py` | 任意 `type` | 通用 |
| `temu_global_file_download.py` | 加签文件下载 | 通用 |

## 示例

```bash
python scripts/global_compliance_edit.py '<JSON>'  # bg.compliance.edit
```

```bash
python scripts/global_compliance_metadata_get.py '<JSON>'  # bg.compliance.metadata.get
```

**Feedback：** `skillName`：`linkfox-temu-compliance-global`

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

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `get_temu_access_token.py`, `global_compliance_arbok_cert_query_need_upload_items.py`, `global_compliance_arbok_cert_upload_product_cert.py`, `global_compliance_arbok_product_cert_query.py`, `global_compliance_arbok_upload_upload_file.py`, `global_compliance_edit.py`, `global_compliance_flash_upload_real_image.py`, `global_compliance_flash_upload_recognize.py`, `global_compliance_goods_compliancelabel_get.py`, `global_compliance_metadata_get.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_file_download.py`, `temu_global_file_download.py`, `temu_global_proxy.py`, `temu_proxy.py`, `temu_token_guide.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
