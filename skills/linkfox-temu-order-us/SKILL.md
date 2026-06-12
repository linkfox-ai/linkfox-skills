---
name: linkfox-temu-order-us
description: Temu 美国站订单管理 API，经 LinkFox 网关转发 Partner US 订单接口：订单列表/详情/收货地址/金额/合并发货/定制/SN鉴真上传(bg.order.*、temu.local.order.verification.upload)、发货、物流等。当用户提到 Temu US 订单、上传SN、IMEI、二手鉴真、verification upload、定制商品、合并发货、订单金额、parentOrderSn、order-shipping 时触发。商品管理用 linkfox-temu-manage-product-us；发品用 linkfox-temu-add-product-us；价格用 linkfox-temu-price-us。
---

# Temu 美国站订单管理 API（Manage Order）

本 skill（`linkfox-temu-order-us`）覆盖 Partner Platform for US **订单管理**相关 `bg.order.*` / `temu.local.order.*` 接口（`menu_code` 与各 `sub_menu_code` 以 Partner 后台为准，见 [partner-us-catalog.md](./references/partner-us-catalog.md)）。欧洲站请用 **`linkfox-temu-order-eu`**；全球站（非 US/EU）请用 **`linkfox-temu-order-global`**。

> 当前已接入 **8** 个接口；其余订单接口将按 Partner 文档逐条补充到 `references/apis/` 与 `us_order_*.py`。

**网关（本 skill 内置）**：

| 能力 | 方法 | 路径 |
|------|------|------|
| 订单 OpenAPI（`us_order_*`、`temu_us_proxy`） | POST | `https://tool-gateway.linkfox.com/temu/proxy` |
| 加签文件下载 | POST | `https://tool-gateway.linkfox.com/temu/fileDownload` |

## 相关 skill

| 场景 | skill |
|------|--------|
| 商品列表/详情/编辑/库存/上下架 | `linkfox-temu-manage-product-us` |
| 发品、类目、V2 add | `linkfox-temu-add-product-us` |
| 价格/供货价、定价单 | `linkfox-temu-price-us` |
| 取消订单（买家+卖家） | `linkfox-temu-cancel-order-us` |
| 退货与退款 | `linkfox-temu-returns-refunds-us` |
| 履约/发货（含自发货） | `linkfox-temu-fulfillment-us` |
| 网关与 Temu token | 本 skill `scripts/` |

## API Usage

| 文档 | 内容 |
|------|------|
| [api.md](./references/api.md) | 网关、鉴权、错误码、扩展流程 |
| [partner-us-catalog.md](./references/partner-us-catalog.md) | 接口目录 + Partner URL + 脚本（随接入更新） |
| [apis/README.md](./references/apis/README.md) | **按接口分文件**（`apis/<type-slug>.md`） |

## 默认参数

| 字段 | 默认 | 说明 |
|------|------|------|
| site | `us` | Partner US |
| managementType | `semi-managed` | 半托管 |
| tokenPurpose | `order-shipping` | 订单/发货场景 token（见 [access-token.md](./references/access-token.md)） |

## 鉴权

1. **LinkFox**：`LINKFOXAGENT_API_KEY` → Header `Authorization` + `Token`
2. **Temu**：`accessToken` 或 `storeKey`（`storeKey` 时建议带 `tokenPurpose=order-shipping`）

## Scripts（按 type）

| 脚本 | type | 状态 |
|------|------|------|
| `us_order_list_v2_get.py` | `bg.order.list.v2.get` | 已接入 |
| `us_order_detail_v2_get.py` | `bg.order.detail.v2.get` | 已接入 |
| `us_order_shippinginfo_v2_get.py` | `bg.order.shippinginfo.v2.get` | 已接入 |
| `us_order_decryptshippinginfo_get.py` | `bg.order.decryptshippinginfo.get` | 已接入 |
| `us_order_amount_query.py` | `bg.order.amount.query` | 已接入 |
| `us_order_combinedshipment_list_get.py` | `bg.order.combinedshipment.list.get` | 已接入 |
| `us_order_customization_get.py` | `bg.order.customization.get` | 已接入 |
| `us_order_verification_upload.py` | `temu.local.order.verification.upload` | 已接入 |
| `temu_us_proxy.py` | 任意 `type` | 通用 |
| `temu_us_file_download.py` | 加签文件下载 | 通用 |

## 接入新接口（约定）

你每提供一条 Partner 文档（`type` + 参数表 + 可选 `sub_menu_code`），将：

1. 新增 `references/apis/<type-slug>.md`（完整入参/出参层级）
2. 新增 `scripts/us_order_<slug>.py`（调用 `_us_order_script.run_cli`）
3. 更新 [partner-us-catalog.md](./references/partner-us-catalog.md)、[apis/README.md](./references/apis/README.md) 与本表

## 示例

```bash
export LINKFOXAGENT_API_KEY="<key>"

# 订单列表 V2（待发货 parentOrderStatus=2）
python scripts/us_order_list_v2_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "pageNumber": 1,
    "pageSize": 20,
    "parentOrderStatus": 2
  }
}'

# 按父订单号查询（最多 20 个）
python scripts/us_order_list_v2_get.py '{
  "accessToken": "TOKEN",
  "request": {
    "parentOrderSnList": ["PO-123456789"]
  }
}'

# 订单详情 V2（须 parentOrderSn）
python scripts/us_order_detail_v2_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789"
  }
}'

# 收货地址 V2（传 parentOrderSn）
python scripts/us_order_shippinginfo_v2_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789"
  }
}'

# 敏感收货地址解密（传 parentOrderSn）
python scripts/us_order_decryptshippinginfo_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789"
  }
}'

# 订单金额/供货价（ERP 对账，传 parentOrderSn）
python scripts/us_order_amount_query.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "parentOrderSn": "PO-123456789"
  }
}'

# 可合并发货订单组（request 可为空对象）
python scripts/us_order_combinedshipment_list_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {}
}'

# 定制商品内容（子订单号 orderSn，单次最多 10 个）
python scripts/us_order_customization_get.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "orderSnList": ["SO-123456789", "SO-987654321"]
  }
}'

# 上传 SN/IMEI 或二手鉴真（orderList[].orderSn）
python scripts/us_order_verification_upload.py '{
  "accessToken": "TOKEN",
  "tokenPurpose": "order-shipping",
  "request": {
    "orderList": [
      {
        "orderSn": "SO-123456789",
        "verificationInfo": [
          {
            "serialNumber": "SN-001234567890",
            "imeiNumberList": ["352099001761481"]
          }
        ]
      }
    ]
  }
}'
```

**Feedback：** `skillName`：`linkfox-temu-order-us`

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

> This skill exposes multiple entry scripts: `check_linkfox_token.py`, `get_temu_access_token.py`, `list_temu_access_tokens.py`, `save_temu_access_token.py`, `temu_file_download.py`, `temu_proxy.py`, `temu_token_guide.py`, `temu_us_file_download.py`, `temu_us_proxy.py`, `us_order_amount_query.py`, `us_order_combinedshipment_list_get.py`, `us_order_customization_get.py`, `us_order_decryptshippinginfo_get.py`, `us_order_detail_v2_get.py`, `us_order_list_v2_get.py`, `us_order_shippinginfo_v2_get.py`, `us_order_verification_upload.py`. Pass `--script scripts/<name>.py` to choose the one you need.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->
