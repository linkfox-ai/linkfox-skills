# linkfox-shopee-store-orders — 参数与字段参考

Shopee **Order 模块**全部 22 个 API，经 **`POST /shopee/developerProxy`** 转发。

授权见 **`linkfox-shopee-store-auth`**。官方文档：[Order module](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1)

## 通用约定

- **Base URL**：`${LINKFOX_TOOL_GATEWAY}`
- **Method**：POST（网关），上游 Method 见各接口
- **Auth**：Header `Authorization: <api_key>`（从 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取）
- **流程**：`POST /shopee/storeTokens` → `POST /shopee/developerProxy`
- **path**：须 `api/v2/order/...`（不含域名）
- **紫鸟代理**：自动追加 `partner_id`、`timestamp`、`sign`；`access_token`/`shop_id` 由 `developerProxy` 写入

**developerProxy Request**：
| 参数 | 必填 | 说明 |
|------|------|------|
| `path` | 是 | 如 `api/v2/order/get_order_list` |
| `method` | 是 | `GET` / `POST` |
| `accessToken` | 是 | 店铺 token |
| `shopId` / `merchantId` | 二选一 | 转发为 `shop_id` / `merchant_id` |
| `queryString` | GET 时 | 业务 query，不含 `?` |
| `body` | POST 时 | JSON 字符串 |
| `contentType` | 否 | 默认 `application/json` |

**developerProxy Response**：
```json
{"httpStatus": 200, "contentType": "application/json", "body": "{\"error\":\"\",\"response\":{...}}"}
```

脚本在 `httpStatus==200` 时解析 `body` 为 `{responseKey}` / `{responseKey}Response`。

---

## Order 模块总览

| # | API | Method | path | 脚本 | 官方文档 |
|---|-----|--------|------|------|----------|
| 1 | get_order_list | GET | `api/v2/order/get_order_list` | `get_order_list.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1) |
| 2 | get_order_detail | GET | `api/v2/order/get_order_detail` | `get_order_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1) |
| 3 | get_shipment_list | GET | `api/v2/order/get_shipment_list` | `get_shipment_list.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_shipment_list?module=94&type=1) |
| 4 | search_package_list | POST | `api/v2/order/search_package_list` | `search_package_list.py` | [doc](https://open.shopee.com/documents/v2/v2.order.search_package_list?module=94&type=1) |
| 5 | get_package_detail | GET | `api/v2/order/get_package_detail` | `get_package_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_package_detail?module=94&type=1) |
| 6 | split_order | POST | `api/v2/order/split_order` | `split_order.py` | [doc](https://open.shopee.com/documents/v2/v2.order.split_order?module=94&type=1) |
| 7 | unsplit_order | POST | `api/v2/order/unsplit_order` | `unsplit_order.py` | [doc](https://open.shopee.com/documents/v2/v2.order.unsplit_order?module=94&type=1) |
| 8 | cancel_order | POST | `api/v2/order/cancel_order` | `cancel_order.py` | [doc](https://open.shopee.com/documents/v2/v2.order.cancel_order?module=94&type=1) |
| 9 | handle_buyer_cancellation | POST | `api/v2/order/handle_buyer_cancellation` | `handle_buyer_cancellation.py` | [doc](https://open.shopee.com/documents/v2/v2.order.handle_buyer_cancellation?module=94&type=1) |
| 10 | set_note | POST | `api/v2/order/set_note` | `set_note.py` | [doc](https://open.shopee.com/documents/v2/v2.order.set_note?module=94&type=1) |
| 11 | get_pending_buyer_invoice_order_list | GET | `api/v2/order/get_pending_buyer_invoice_order_list` | `get_pending_buyer_invoice_order_list.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_pending_buyer_invoice_order_list?module=94&type=1) |
| 12 | get_buyer_invoice_info | POST | `api/v2/order/get_buyer_invoice_info` | `get_buyer_invoice_info.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_buyer_invoice_info?module=94&type=1) |
| 13 | upload_invoice_doc | POST | `api/v2/order/upload_invoice_doc` | `upload_invoice_doc.py` | [doc](https://open.shopee.com/documents/v2/v2.order.upload_invoice_doc?module=94&type=1) |
| 14 | download_invoice_doc | GET | `api/v2/order/download_invoice_doc` | `download_invoice_doc.py` | [doc](https://open.shopee.com/documents/v2/v2.order.download_invoice_doc?module=94&type=1) |
| 15 | handle_prescription_check | POST | `api/v2/order/handle_prescription_check` | `handle_prescription_check.py` | [doc](https://open.shopee.com/documents/v2/v2.order.handle_prescription_check?module=94&type=1) |
| 16 | get_warehouse_filter_config | GET | `api/v2/order/get_warehouse_filter_config` | `get_warehouse_filter_config.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_warehouse_filter_config?module=94&type=1) |
| 17 | get_booking_list | GET | `api/v2/order/get_booking_list` | `get_booking_list.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_booking_list?module=94&type=1) |
| 18 | get_booking_detail | GET | `api/v2/order/get_booking_detail` | `get_booking_detail.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_booking_detail?module=94&type=1) |
| 19 | generate_fbs_invoices | POST | `api/v2/order/generate_fbs_invoices` | `generate_fbs_invoices.py` | [doc](https://open.shopee.com/documents/v2/v2.order.generate_fbs_invoices?module=94&type=1) |
| 20 | get_fbs_invoices_result | POST | `api/v2/order/get_fbs_invoices_result` | `get_fbs_invoices_result.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_fbs_invoices_result?module=94&type=1) |
| 21 | download_fbs_invoices | POST | `api/v2/order/download_fbs_invoices` | `download_fbs_invoices.py` | [doc](https://open.shopee.com/documents/v2/v2.order.download_fbs_invoices?module=94&type=1) |
| 22 | get_estimiate_cancel_value | POST | `api/v2/order/get_estimiate_cancel_value` | `get_estimiate_cancel_value.py` | [doc](https://open.shopee.com/documents/v2/v2.order.get_estimiate_cancel_value?module=94&type=1) |

通用入口：`order_api.py`（JSON 含 `"api": "<上表 API 名>"`）。

---

## 1. get_order_list

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1)

**Query（必填）**：`time_range_field`（`create_time`|`update_time`）、`time_from`、`time_to`（Unix 秒，跨度 ≤15 天）、`page_size`（1–100）

**Query（可选）**：`cursor`、`order_status`（`UNPAID`/`READY_TO_SHIP`/`PROCESSED`/`SHIPPED`/`COMPLETED`/`IN_CANCEL`/`CANCELLED`/`INVOICE_PENDING`）、`response_optional_fields`、`request_order_status_pending`、`logistics_channel_id`（仅 BR）

**Response**：`more`、`next_cursor`、`order_list[]`（含 `order_sn`）

---

## 2. get_order_detail

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1)

**Query（必填）**：`order_sn_list`（逗号分隔或数组，1–50 个）

**Query（可选）**：`response_optional_fields`、`request_order_status_pending`

**Response**：`order_list[]`（`order_sn`、`order_status`、`total_amount`、`item_list`、`recipient_address` 等）

---

## 3. get_shipment_list

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_shipment_list?module=94&type=1)

**Query（必填）**：`page_size`（1–100）

**Query（可选）**：`cursor`

**说明**：返回可开始发货流程的 `READY_TO_SHIP` 订单/包裹。

---

## 4. search_package_list

[官方文档](https://open.shopee.com/documents/v2/v2.order.search_package_list?module=94&type=1)

**Body（必填）**：`pagination.page_size`（1–100）

**Body（可选）**：
- `filter`：`package_status`、`product_location_ids`、`logistics_channel_ids`、`fulfillment_type`、`invoice_pending`、`sorting_group`（TW）、`order_type`、`is_pre_order`、`shipping_priority`
- `pagination.cursor`
- `sort`：`sort_type`（1=ShipByDate/2=CreateDate/3=ConfirmedDate）、`ascending`

**示例**：
```json
{
  "shopId": "67890",
  "filter": {"package_status": 2, "fulfillment_type": 2},
  "pagination": {"page_size": 20, "cursor": ""},
  "sort": {"sort_type": 1, "ascending": false}
}
```

---

## 5. get_package_detail

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_package_detail?module=94&type=1)

**Query（必填）**：`package_number_list`（逗号分隔，1–50 个）

---

## 6. split_order

[官方文档](https://open.shopee.com/documents/v2/v2.order.split_order?module=94&type=1)

**Body（必填）**：`order_sn`、`package_list[]`（含 `item_list[]`：`item_id`、`model_id`；可选 `order_item_id`、`promotion_group_id`、`model_quantity`）

---

## 7. unsplit_order

[官方文档](https://open.shopee.com/documents/v2/v2.order.unsplit_order?module=94&type=1)

**Body（必填）**：`order_sn`（仅 `READY_TO_SHIP` 且未发货的已拆分订单）

---

## 8. cancel_order

[官方文档](https://open.shopee.com/documents/v2/v2.order.cancel_order?module=94&type=1)

**Body（必填）**：`order_sn`、`cancel_reason`

**Body（可选）**：`item_list`、`partial_cancel_item_list`（`item_id`、`model_id`、`model_quantity` 等）

**cancel_reason**：`OUT_OF_STOCK`、`CUSTOMER_REQUEST`、`UNDELIVERABLE_AREA`（TW/MY）、`COD_NOT_SUPPORTED`

---

## 9. handle_buyer_cancellation

[官方文档](https://open.shopee.com/documents/v2/v2.order.handle_buyer_cancellation?module=94&type=1)

**Body（必填）**：`order_sn`、`operation`（`ACCEPT`|`REJECT`）

---

## 10. set_note

[官方文档](https://open.shopee.com/documents/v2/v2.order.set_note?module=94&type=1)

**Body（必填）**：`order_sn`、`note`

---

## 11. get_pending_buyer_invoice_order_list

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_pending_buyer_invoice_order_list?module=94&type=1)

**Query（必填）**：`page_size`（1–100）

**Query（可选）**：`cursor`

**区域**：PH、BR 本地卖家

---

## 12. get_buyer_invoice_info

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_buyer_invoice_info?module=94&type=1)

**Body（必填）**：`queries[]`（含 `order_sn`）

**区域**：VN、TH、PH 本地卖家

---

## 13. upload_invoice_doc

[官方文档](https://open.shopee.com/documents/v2/v2.order.upload_invoice_doc?module=94&type=1)

**说明**：官方为 **multipart/form-data**（`order_sn`、`file_type`、`file`）。若 LinkFox 网关 `body` 仅支持 JSON 字符串，可能无法直接上传二进制；需确认网关能力或使用专用上传链路。

**区域**：PH、BR

---

## 14. download_invoice_doc

[官方文档](https://open.shopee.com/documents/v2/v2.order.download_invoice_doc?module=94&type=1)

**Query（必填）**：`order_sn`

**区域**：PH、BR

---

## 15. handle_prescription_check

[官方文档](https://open.shopee.com/documents/v2/v2.order.handle_prescription_check?module=94&type=1)

**Body（必填）**：`package_number`、`operation`（`APPROVE`|`REJECT`）

**Body（可选）**：`order_sn`、`reject_reason`、`is_approved`、`reject_reason_code`、`items`、`pharmacist_name`、`free_text`

**区域**：ID、PH 白名单卖家

---

## 16. get_warehouse_filter_config

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_warehouse_filter_config?module=94&type=1)

无额外业务参数（仅店铺公共 query）。多仓店铺返回仓库过滤配置。

---

## 17. get_booking_list

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_booking_list?module=94&type=1)

**Query（必填）**：`time_range_field`、`time_from`、`time_to`、`page_size`

**Query（可选）**：`cursor`、`booking_status`（`READY_TO_SHIP`/`PROCESSED`/`SHIPPED`/`CANCELLED`/`MATCHED`）

---

## 18. get_booking_detail

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_booking_detail?module=94&type=1)

**Query（必填）**：`booking_sn_list`（逗号分隔，1–50 个）

**Query（可选）**：`response_optional_fields`

---

## 19. generate_fbs_invoices

[官方文档](https://open.shopee.com/documents/v2/v2.order.generate_fbs_invoices?module=94&type=1)

**Body（必填）**：`batch_download`（`start`/`end` YYYYMMDD、`document_type`、`file_type`；可选 `document_status`）

**区域**：BR FBS

---

## 20. get_fbs_invoices_result

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_fbs_invoices_result?module=94&type=1)

**Body（必填）**：`request_id_list.request_id`（int 数组）

---

## 21. download_fbs_invoices

[官方文档](https://open.shopee.com/documents/v2/v2.order.download_fbs_invoices?module=94&type=1)

**Body（必填）**：`request_id_list.request_id`（int 数组）

**说明**：需先 `generate_fbs_invoices` → 本接口轮询结果 → 下载；链接 30 分钟过期。

---

## 22. get_estimiate_cancel_value

[官方文档](https://open.shopee.com/documents/v2/v2.order.get_estimiate_cancel_value?module=94&type=1)

> 官方 API 名拼写为 **estimiate**（非 estimate）。

**Body（必填）**：`order_sn`、`partial_cancel_item_list[]`（`item_id`、`model_id`、`model_quantity`；可选 `order_item_id`、`promotion_group_id`）

---

## 网关错误码

| errcode | 含义 | 建议 |
|---------|------|------|
| 1002 | 参数/未登录 | 检查 shopId 与 API Key |
| 1003 | 代理/网络异常 | 重试 |
| 1004 | 无授权记录 | auth skill |
| 1005 | path 未白名单 | 确认 `api/v2/order/...` |

紫鸟代理 HTTP：`400` 路径错误、`403` IP 白名单、`408` 超时、`5xx` 上游透传。

---

## curl 示例

```bash
export KEY=$LINKFOXAGENT_API_KEY
BASE=https://tool-gateway.linkfox.com

# 订单列表
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/order/get_order_list",
    "method": "GET",
    "accessToken": "xxx",
    "shopId": "67890",
    "queryString": "time_range_field=create_time&time_from=1607235072&time_to=1608271872&page_size=20"
  }'

# 取消订单
curl -X POST $BASE/shopee/developerProxy -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "api/v2/order/cancel_order",
    "method": "POST",
    "accessToken": "xxx",
    "shopId": "67890",
    "body": "{\"order_sn\":\"201020SQQ5K2EP\",\"cancel_reason\":\"CUSTOMER_REQUEST\"}"
  }'
```

---

## Feedback API

```bash
curl -X POST https://skill-api.linkfox.com/api/v1/public/feedback \
  -H "Content-Type: application/json" \
  -d '{"skillName":"linkfox-shopee-store-orders","sentiment":"POSITIVE",
       "category":"OTHER","content":"订单接口正常"}'
```