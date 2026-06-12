---
name: linkfox-temu-returns-refunds-eu
description: Temu 欧洲站电商退货与退款 API，经 LinkFox 网关转发 Partner EU Returns & Refunds / 售后退货退款 相关 bg/temu 接口（退货申请、退款、售后单查询与处理等，接口将按 Partner 文档逐条接入）。当用户提到 Temu EU 退货、退款、售后退货、return、refund、aftersales return、parentAfterSalesSn、退货单、退款单、order-shipping 售后 时触发。取消订单用 linkfox-temu-cancel-order-eu；订单用 linkfox-temu-order-eu。
---

# Temu 欧洲站 — 退货与退款（Returns & Refunds）

本 skill（`linkfox-temu-returns-refunds-eu`）覆盖 Partner Platform for EU **Returns & Refunds / 电商退货与退款**（及关联 **After-sales** 退货退款类）相关 `bg.*` / `temu.*` 接口（`menu_code` 与各 `sub_menu_code` 以 Partner 后台为准，见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)）。

已接入 **9** 条 Partner **Return and Refund** 接口，清单见 [partner-eu-catalog.md](./references/partner-eu-catalog.md)。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 退货退款 OpenAPI（`eu_returns_refunds_*`、`temu_eu_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| **退货与退款**（本 skill） | **`linkfox-temu-returns-refunds-eu`** |
| 买家发起**取消订单**（非退货退款全流程） | `linkfox-temu-cancel-order-eu` |
| 卖家发起**取消订单** / 缺货取消 / 申诉 | `linkfox-temu-cancel-order-eu` |
| 订单列表/详情/金额/售后上下文 | `linkfox-temu-order-eu` |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 履约/发货 | `linkfox-temu-fulfillment-eu` |
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
| managementType | `semi-managed` | 半托管（具体接口以 Partner 文档为准） |
| tokenPurpose | `order-shipping` | 订单/售后场景 token（见 [access-token.md](./references/access-token.md)） |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（`storeKey` 时建议带 `tokenPurpose=order-shipping`）

## Scripts

| 脚本 | 说明 |
|------|------|
| `temu_eu_proxy.py` | 任意 `type` 通用转发 |
| `temu_eu_file_download.py` | 加签文件下载 |
| `eu_returns_refunds_aftersales_parentaftersales_list_get.py` | `bg.aftersales.parentaftersales.list.get` |
| `eu_returns_refunds_aftersales_aftersales_list_get.py` | `bg.aftersales.aftersales.list.get` |
| `eu_returns_refunds_aftersales_parentaftersales_detail_get.py` | `temu.aftersales.parentaftersales.detail.get` |
| `eu_returns_refunds_aftersales_parentreturnorder_get.py` | `bg.aftersales.parentreturnorder.get` |
| `eu_returns_refunds_aftersales_returnaddress_get.py` | `temu.aftersales.returnaddress.get` |
| `eu_returns_refunds_aftersales_returnlabel_prepare_get.py` | `temu.aftersales.returnlabel.prepare.get` |
| `eu_returns_refunds_aftersales_signature_get.py` | `temu.aftersales.signature.get` |
| `eu_returns_refunds_aftersales_upload_returnlabel.py` | `temu.aftersales.upload.returnlabel` |
| `eu_returns_refunds_aftersales_carrier_get.py` | `temu.aftersales.carrier.get` |

## 接入更多接口（约定）

你每提供一条 Partner 文档（`type` + `sub_menu_code` + URL + Request/Response 参数表），将：

1. 新增 `references/apis/<type-slug>.md`（完整入参/出参层级）
2. 新增 `scripts/eu_returns_refunds_<slug>.py`（调用 `_eu_returns_refunds_script.run_cli`）
3. 更新 [partner-eu-catalog.md](./references/partner-eu-catalog.md)、[apis/README.md](./references/apis/README.md) 与本表

## 示例（通用代理）

```bash
export LINKFOXAGENT_API_KEY="<key>"

python scripts/temu_eu_proxy.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "type": "<TEMU_API_TYPE>",
  "params": {
    "request": {}
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-returns-refunds-eu`

## 网关与授权脚本

| 脚本 | 说明 |
|------|------|
| `check_linkfox_token.py` | 校验 LinkFox 用户 Token |
| `temu_token_guide.py` | Temu accessToken 后台授权步骤 |
| `save_temu_access_token.py` | 保存 accessToken 到本地 |
| `list_temu_access_tokens.py` | 列出已保存 token |
| `get_temu_access_token.py` | 读取已保存 token |
| `temu_proxy.py` | 通用网关转发（多 site） |
| `temu_file_download.py` | 加签文件下载（多 site） |

授权说明：[references/access-token.md](./references/access-token.md)

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/check_linkfox_token.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `eu_returns_refunds_aftersales_aftersales_list_get.py`, `eu_returns_refunds_aftersales_carrier_get.py`, `eu_returns_refunds_aftersales_parentaftersales_detail_get.py`, `eu_returns_refunds_aftersales_parentaftersales_list_get.py`, `eu_returns_refunds_aftersales_parentreturnorder_get.py`, `eu_returns_refunds_aftersales_returnaddress_get.py`, `eu_returns_refunds_aftersales_returnlabel_prepare_get.py`, `eu_returns_refunds_aftersales_signature_get.py`, `eu_returns_refunds_aftersales_upload_returnlabel.py`, `get_temu_access_token.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_eu_file_download.py`, `temu_eu_proxy.py`, `temu_file_download.py`, `temu_proxy.py`, `temu_token_guide.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
