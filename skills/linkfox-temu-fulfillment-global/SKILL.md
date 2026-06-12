---
name: linkfox-temu-fulfillment-global
description: Temu 全球站（非 US/EU）电商履行/发货 API（合一）：Buy-Shipping购标面单、合作仓履约、卖家自发货、物流跟踪等23个接口（不含 Scan Form）。当用户提到 Temu Global 发货、购标、Buy-Shipping、合作仓、自发货、tracking、shipment.create、site=global order-shipping 时触发。订单用 linkfox-temu-order-global。Scan Form 请用 linkfox-temu-fulfillment-us。
---

# Temu 全球站 — 电商履行 / 发货（Fulfillment）

本 skill（`linkfox-temu-fulfillment-global`）覆盖 Partner **Global** **Fulfillment** 域 **23** 个已接入 `type`（与 US 版对齐但 **不含** 4 个 Scan Form 接口）。

| 域 | 脚本前缀 | 接口数 |
|----|----------|--------|
| Buy-Shipping | `global_buy_shipping_*` | 13 |
| Co-Warehouse | `global_co_warehouse_*` | 4 |
| Self-Fulfilled | `global_self_fulfilled_*` | 5 |
| Tracking | `global_tracking_*` | 1 |

**未接入（相对 US）**：`temu.logistics.scanform.create`、`temu.logistics.scanform.get`、`temu.logistics.scanform.document.get`、`temu.logistics.candidate.scanform.list.get` — 请用 **`linkfox-temu-fulfillment-us`**（`site=us`）。

详见 [partner-global-catalog.md](./references/partner-global-catalog.md)。美国站请用 **`linkfox-temu-fulfillment-us`**；欧洲站请用 **`linkfox-temu-fulfillment-eu`**。

**网关**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 履约 OpenAPI | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 订单列表/详情/地址 | `linkfox-temu-order-global` |
| 取消订单 | `linkfox-temu-cancel-order-global` |
| 商品管理 | `linkfox-temu-manage-product-global` |
| 美国站履约（含 Scan Form） | `linkfox-temu-fulfillment-us` |
| 欧洲站履约 | `linkfox-temu-fulfillment-eu` |
| 退货退款 | `linkfox-temu-returns-refunds-global` |

## 默认参数

| 字段 | 默认 |
|------|------|
| site | `global` |
| managementType | `semi-managed` |
| tokenPurpose | `order-shipping` |

## Scripts（按域）

### Buy-Shipping（`global_buy_shipping_*`）

购标、面单、上门揽收等（**不含 Scan Form**）— 见 [apis/README.md](./references/apis/README.md)。

### Co-Warehouse（`global_co_warehouse_*`）

`bg.cooperativewarehouse.*` — 合作仓授权、提交/取消履约。

### Self-Fulfilled（`global_self_fulfilled_*`）

`bg.logistics.shipment.v2.*`、`shippingtype.update` 等 — 卖家自带运单号。

### Tracking（`global_tracking_*`）

`temu.track.trackinginfo.get`

### 通用

| 脚本 | 说明 |
|------|------|
| `temu_global_proxy.py` | 任意 `type` |
| `temu_global_file_download.py` | 加签文件下载 |

薄封装统一调用 **`_global_fulfillment_script.run_cli`**。

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# Buy-Shipping 购标
python scripts/global_buy_shipping_logistics_shipment_create.py '{
  "accessToken": "TOKEN",
  "site": "global",
  "tokenPurpose": "order-shipping",
  "request": { }
}'

# 卖家自发货更新跟踪号
python scripts/global_self_fulfilled_logistics_shipment_shippingtype_update.py '{
  "accessToken": "TOKEN",
  "site": "global",
  "tokenPurpose": "order-shipping",
  "request": { "editPackageRequestList": [{ "packageSn": "PKG-1", "trackingNumber": "1Z..." }] }
}'
```

**Feedback：** `skillName`：`linkfox-temu-fulfillment-global`

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/check_linkfox_token.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `get_temu_access_token.py`, `global_buy_shipping_logistics_label_list_get.py`, `global_buy_shipping_logistics_shiplogisticstype_get.py`, `global_buy_shipping_logistics_shipment_create.py`, `global_buy_shipping_logistics_shipment_document_get.py`, `global_buy_shipping_logistics_shipment_pickup_reservation_cancel.py`, `global_buy_shipping_logistics_shipment_pickup_reservation_create.py`, `global_buy_shipping_logistics_shipment_pickup_reservation_result_get.py`, `global_buy_shipping_logistics_shipment_result_get.py`, `global_buy_shipping_logistics_shipment_update.py`, `global_buy_shipping_logistics_shipped_package_confirm.py`, `global_buy_shipping_logistics_shippingservices_get.py`, `global_buy_shipping_logistics_warehouse_list_get.py`, `global_buy_shipping_order_unshipped_package_get.py`, `global_co_warehouse_cooperativewarehouse_fulfill_cancel.py`, `global_co_warehouse_cooperativewarehouse_fulfill_submit.py`, `global_co_warehouse_cooperativewarehouse_provider_list.py`, `global_co_warehouse_cooperativewarehouse_token_authorization.py`, `global_self_fulfilled_logistics_companies_get.py`, `global_self_fulfilled_logistics_shipment_shippingtype_update.py`, `global_self_fulfilled_logistics_shipment_sub_confirm.py`, `global_self_fulfilled_logistics_shipment_v2_confirm.py`, `global_self_fulfilled_logistics_shipment_v2_get.py`, `global_tracking_track_trackinginfo_get.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_file_download.py`, `temu_global_file_download.py`, `temu_global_proxy.py`, `temu_proxy.py`, `temu_token_guide.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
