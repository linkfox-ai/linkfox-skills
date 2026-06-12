---
name: linkfox-temu-cancel-order-global
description: Temu 全球站（非 US/EU）取消订单 API（买家+卖家合一），经 LinkFox 网关转发 6 个接口：买家售后取消(bg.aftersales.cancel.*)、卖家申诉/缺货取消(temu.order.cancel.*)等，默认 site=global、tokenPurpose=order-shipping。当用户提到 Temu Global 取消订单、全球站买家取消、卖家缺货取消、afterSalesStatusGroup、applySn 时触发。美国站用 linkfox-temu-cancel-order-us；欧洲站用 linkfox-temu-cancel-order-eu；订单用 linkfox-temu-order-global。
---

# Temu 全球站 — 取消订单（买家 + 卖家）

本 skill（`linkfox-temu-cancel-order-global`）覆盖 **全球区（`site=global`，非美国/欧洲）** 的 **Order / 取消订单** 相关接口：

- **买家/消费者**：`bg.aftersales.cancel.list.get`、`bg.aftersales.cancel.agree`
- **店家/卖家**：`temu.order.cancel.appeal.apply`、`temu.order.cancel.appeal.result.get`、`temu.order.cancel.outofstock.apply`、`temu.order.cancel.outofstock.result.get`

详见 [partner-global-catalog.md](./references/partner-global-catalog.md)（**6** 个接口）。美国站请用 **`linkfox-temu-cancel-order-us`**；欧洲站请用 **`linkfox-temu-cancel-order-eu`**。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 取消单 OpenAPI（`global_cancel_*`、`global_seller_cancel_*`、`temu_global_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 订单列表/详情/发货/地址/金额 | `linkfox-temu-order-global` |
| 美国站取消订单 | `linkfox-temu-cancel-order-us` |
| 欧洲站取消订单 | `linkfox-temu-cancel-order-eu` |
| 履约/发货 | `linkfox-temu-fulfillment-global` |
| 商品管理 | `linkfox-temu-manage-product-global` |
| 退货与退款 | `linkfox-temu-returns-refunds-us` / `linkfox-temu-returns-refunds-eu`（`site=global`） |
| 网关与 Temu token | 本 skill `scripts/` |

## API Usage

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、典型流程 |
| [partner-global-catalog.md](./references/partner-global-catalog.md) | 接口目录 + Partner URL + 脚本 |
| [apis/README.md](./references/apis/README.md) | **按接口分文件** |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `global` | Partner Global（非 US/EU） |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `order-shipping` | 订单/取消场景 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（建议 `tokenPurpose=order-shipping`）

## Scripts（按 type）

### 买家取消

| 脚本 | type |
|------|------|
| `global_cancel_aftersales_cancel_list_get.py` | `bg.aftersales.cancel.list.get` |
| `global_cancel_aftersales_cancel_agree.py` | `bg.aftersales.cancel.agree` |

### 卖家取消

| 脚本 | type |
|------|------|
| `global_seller_cancel_order_cancel_appeal_apply.py` | `temu.order.cancel.appeal.apply` |
| `global_seller_cancel_order_cancel_appeal_result_get.py` | `temu.order.cancel.appeal.result.get` |
| `global_seller_cancel_order_cancel_outofstock_apply.py` | `temu.order.cancel.outofstock.apply` |
| `global_seller_cancel_order_cancel_outofstock_result_get.py` | `temu.order.cancel.outofstock.result.get` |

### 通用

| 脚本 | 说明 |
|------|------|
| `temu_global_proxy.py` | 任意 `type` |
| `temu_global_file_download.py` | 加签文件下载 |

## 接入新接口（约定）

1. 新增 `references/apis/<type-slug>.md`
2. 新增 `scripts/global_cancel_*` 或 `global_seller_cancel_*`（调用 `_global_cancel_order_script.run_cli`）
3. 更新 [partner-global-catalog.md](./references/partner-global-catalog.md)、[apis/README.md](./references/apis/README.md)

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 买家取消 — 待处理列表
python scripts/global_cancel_aftersales_cancel_list_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "site": "global",
  "request": { "pageNo": 1, "pageSize": 20, "afterSalesStatusGroup": 8 }
}'

# 卖家 — 缺货取消申请
python scripts/global_seller_cancel_order_cancel_outofstock_apply.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "site": "global",
  "request": {
    "parentOrderSn": "PO-123456789",
    "orderSnList": ["O-111111111"]
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-cancel-order-global`

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

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `get_temu_access_token.py`, `global_cancel_aftersales_cancel_agree.py`, `global_cancel_aftersales_cancel_list_get.py`, `global_seller_cancel_order_cancel_appeal_apply.py`, `global_seller_cancel_order_cancel_appeal_result_get.py`, `global_seller_cancel_order_cancel_outofstock_apply.py`, `global_seller_cancel_order_cancel_outofstock_result_get.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_file_download.py`, `temu_global_file_download.py`, `temu_global_proxy.py`, `temu_proxy.py`, `temu_token_guide.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
