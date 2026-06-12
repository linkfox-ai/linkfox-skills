---
name: linkfox-temu-cancel-order-us
description: Temu 美国站取消订单 API（买家+卖家合一），经 LinkFox 网关转发 Partner US：买家售后取消列表/同意(bg.aftersales.cancel.*)、卖家申诉/缺货取消(temu.order.cancel.appeal/outofstock.*)等。当用户提到 Temu US 取消订单、买家取消、卖家取消、缺货取消、afterSalesStatusGroup、applySn、order-shipping 时触发。订单用 linkfox-temu-order-us；欧洲站用 linkfox-temu-cancel-order-eu；全球站用 linkfox-temu-cancel-order-global。
---

# Temu 美国站 — 取消订单（买家 + 卖家）

本 skill（`linkfox-temu-cancel-order-us`）覆盖 Partner Platform for US **取消订单**相关接口：

- **买家/消费者**：`bg.aftersales.cancel.list.get`、`bg.aftersales.cancel.agree`
- **店家/卖家**：`temu.order.cancel.appeal.apply`、`temu.order.cancel.appeal.result.get`、`temu.order.cancel.outofstock.apply`、`temu.order.cancel.outofstock.result.get`

详见 [partner-us-catalog.md](./references/partner-us-catalog.md)（**6** 个接口）。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 取消单 OpenAPI（`us_cancel_*`、`us_seller_cancel_*`、`temu_us_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 订单列表/详情/发货/地址/金额 | `linkfox-temu-order-us` |
| 欧洲站取消订单 | `linkfox-temu-cancel-order-eu` |
| 全球站（非 US/EU）取消订单 | `linkfox-temu-cancel-order-global` |
| 履约/发货 | `linkfox-temu-fulfillment-us` |
| 商品管理 | `linkfox-temu-manage-product-us` |
| 退货与退款 | `linkfox-temu-returns-refunds-us` |
| 网关与 Temu token | 本 skill `scripts/` |

## API Usage

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、典型流程 |
| [partner-us-catalog.md](./references/partner-us-catalog.md) | 接口目录 + Partner URL + 脚本 |
| [apis/README.md](./references/apis/README.md) | **按接口分文件** |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `us` | Partner US |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `order-shipping` | 订单/取消场景 token |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（建议 `tokenPurpose=order-shipping`）

## Scripts（按 type）

### 买家取消

| 脚本 | type |
|------|------|
| `us_cancel_aftersales_cancel_list_get.py` | `bg.aftersales.cancel.list.get` |
| `us_cancel_aftersales_cancel_agree.py` | `bg.aftersales.cancel.agree` |

### 卖家取消

| 脚本 | type |
|------|------|
| `us_seller_cancel_order_cancel_appeal_apply.py` | `temu.order.cancel.appeal.apply` |
| `us_seller_cancel_order_cancel_appeal_result_get.py` | `temu.order.cancel.appeal.result.get` |
| `us_seller_cancel_order_cancel_outofstock_apply.py` | `temu.order.cancel.outofstock.apply` |
| `us_seller_cancel_order_cancel_outofstock_result_get.py` | `temu.order.cancel.outofstock.result.get` |

### 通用

| 脚本 | 说明 |
|------|------|
| `temu_us_proxy.py` | 任意 `type` |
| `temu_us_file_download.py` | 加签文件下载 |

## 接入新接口（约定）

1. 新增 `references/apis/<type-slug>.md`
2. 新增 `scripts/us_cancel_*` 或 `us_seller_cancel_*`（调用 `_us_cancel_order_script.run_cli`）
3. 更新 [partner-us-catalog.md](./references/partner-us-catalog.md)、[apis/README.md](./references/apis/README.md)

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 买家取消 — 待处理列表
python scripts/us_cancel_aftersales_cancel_list_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": { "pageNo": 1, "pageSize": 20, "afterSalesStatusGroup": 8 }
}'

# 卖家 — 缺货取消申请
python scripts/us_seller_cancel_order_cancel_outofstock_apply.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789",
    "orderSnList": ["O-111111111"]
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-cancel-order-us`

## 网关与授权脚本

| 脚本 | 说明 |
|------|------|
| `check_linkfox_token.py` | 校验 LinkFox Token |
| `save_temu_access_token.py` / `list_temu_access_tokens.py` / `get_temu_access_token.py` | 本地 token |
| `temu_token_guide.py` | Temu 授权指引 |

授权说明：[references/access-token.md](./references/access-token.md)

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/check_linkfox_token.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `get_temu_access_token.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_file_download.py`, `temu_proxy.py`, `temu_token_guide.py`, `temu_us_file_download.py`, `temu_us_proxy.py`, `us_cancel_aftersales_cancel_agree.py`, `us_cancel_aftersales_cancel_list_get.py`, `us_seller_cancel_order_cancel_appeal_apply.py`, `us_seller_cancel_order_cancel_appeal_result_get.py`, `us_seller_cancel_order_cancel_outofstock_apply.py`, `us_seller_cancel_order_cancel_outofstock_result_get.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
