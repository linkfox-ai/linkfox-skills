---
name: linkfox-shopee-store-orders
description: Shopee（虾皮）店铺订单（与 linkfox-shopee-store-auth 同系列），经 /shopee/developerProxy 转发 Shopee Open API Order 模块全部 22 个接口：get_order_list、get_order_detail、get_shipment_list、search_package_list、cancel_order、ship 相关 booking/invoice/FBS 等。当用户提到 Shopee 订单、虾皮订单列表、订单详情、包裹、拆单、取消订单、买家取消、订单备注、booking、FBS 发票、order_sn、READY_TO_SHIP、Shopee order processing 时触发。即使未明确提及"订单"，只要涉及已授权 Shopee 店铺的订单查询或订单处理，也应触发。
---

# Shopee 店铺 Orders

Shopee Open Platform **Order 模块**（22 个 API）。**依赖 `linkfox-shopee-store-auth`**：先取 `accessToken`，再经 **`POST /shopee/developerProxy`** 转发（`path` 须 `api/v2/order/...`）。

## 调用方式

- **API 端点**：`POST /shopee/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

Order 模块索引：[Shopee Open Platform — Order](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1)

---

## Prerequisites（必须先读）

1. 运行 `python scripts/check_auth_dependency.py`；exit code **42** → 先安装 **`linkfox-shopee-store-auth`** 并授权店铺。
2. **不要**在本 skill 内实现授权/令牌逻辑。

---

## Core Concepts

- **转发链路**：`storeTokens` → `developerProxy` → 紫鸟 `shopee-proxy` → Shopee API（`partner_id`/`sign` 由代理自动处理）
- **列表 → 详情**：`get_order_list` 得 `order_sn` → `get_order_detail` 拉全量字段（≤50 个/次）
- **包裹流**：`search_package_list` / `get_package_detail` / `get_shipment_list` 用于发货前包裹视图
- **写操作**：`split_order`、`cancel_order`、`set_note` 等为 **POST JSON body**
- **时间窗**：`get_order_list` / `get_booking_list` 的 `time_from`/`time_to` 最大 **15 天**

## 可用脚本（Order 模块 22 个 API）

| 脚本 | API | Method |
|------|-----|--------|
| `get_order_list.py` | get_order_list | GET |
| `get_order_detail.py` | get_order_detail | GET |
| `get_shipment_list.py` | get_shipment_list | GET |
| `search_package_list.py` | search_package_list | POST |
| `get_package_detail.py` | get_package_detail | GET |
| `split_order.py` | split_order | POST |
| `unsplit_order.py` | unsplit_order | POST |
| `cancel_order.py` | cancel_order | POST |
| `handle_buyer_cancellation.py` | handle_buyer_cancellation | POST |
| `set_note.py` | set_note | POST |
| `get_pending_buyer_invoice_order_list.py` | get_pending_buyer_invoice_order_list | GET |
| `get_buyer_invoice_info.py` | get_buyer_invoice_info | POST |
| `upload_invoice_doc.py` | upload_invoice_doc | POST |
| `download_invoice_doc.py` | download_invoice_doc | GET |
| `handle_prescription_check.py` | handle_prescription_check | POST |
| `get_warehouse_filter_config.py` | get_warehouse_filter_config | GET |
| `get_booking_list.py` | get_booking_list | GET |
| `get_booking_detail.py` | get_booking_detail | GET |
| `generate_fbs_invoices.py` | generate_fbs_invoices | POST |
| `get_fbs_invoices_result.py` | get_fbs_invoices_result | POST |
| `download_fbs_invoices.py` | download_fbs_invoices | POST |
| `get_estimiate_cancel_value.py` | get_estimiate_cancel_value | POST |
| `order_api.py` | 通用入口（JSON 含 `api` 字段） | — |

共享：`_shopee_orders_common.py`、`_order_endpoints.py`、`_order_api_runner.py`。入参详见 `references/api.md`。

## Usage Scenarios

### 1. 查待发货订单
1. auth skill 定位 `shopId`
2. `get_order_list.py`：`order_status=READY_TO_SHIP`，`time_range_field=update_time`，15 天内时间戳
3. `get_order_detail.py`：传入 `order_sn_list`

### 2. 包裹维度处理
1. `search_package_list.py`：传 `pagination.page_size` 及可选 `filter`/`sort`（或整体 `body`）
2. `get_package_detail.py`：`package_number_list`
3. 发货物流见 Logistics 模块（非本 skill）

### 3. 取消 / 备注 / 拆单
- 取消：`cancel_order.py`（`order_sn` + `cancel_reason`）
- 买家取消申请：`handle_buyer_cancellation.py`（`ACCEPT`/`REJECT`）
- 备注：`set_note.py`
- 拆单/合单：`split_order.py` / `unsplit_order.py`

### 4. 选店（高频）

| 用户上下文 | Agent 动作 |
|---|---|
| 只授权 1 家 | 直接用 `shopId` |
| 多家 + 店名 | auth skill `authorized_stores.py` 澄清 |
| 已给 order_sn | 直接详情/写操作脚本 |

## 调用原则

- 先看 **`developerProxy.httpStatus`**，再读 `*Response` 解析字段
- GET：业务参数作为脚本 JSON 顶层字段（runner 拼 `queryString`）
- POST：传 `body` 对象，或按 api.md 传顶层 body 字段
- `upload_invoice_doc` 官方为 **multipart**；若网关不支持，需在文档中说明限制
- 分页：`get_order_list` 用 `cursor`/`next_cursor`；`search_package_list` 用 `pagination.cursor`

## 常见问题

### 1005 path 白名单

确认 path 为 `api/v2/order/...`。

### 区域限制

发票类 API 限 PH/BR；`get_buyer_invoice_info` 限 VN/TH/PH；FBS 发票限 BR。见 `references/api.md`。

### token 过期

回到 **`linkfox-shopee-store-auth`** 重新授权。

## Not Applicable

- 店铺授权 → `linkfox-shopee-store-auth`
- 商户信息 → `linkfox-shopee-store-merchant`
- 店铺信息与设置 → `linkfox-shopee-store-shop`
- 商品 listing → `linkfox-shopee-store-product`
- 账户健康 Account Health → `linkfox-shopee-store-account-health`
- 跨境全球商品 → `linkfox-shopee-store-global-product`
- 物流发货 → `linkfox-shopee-store-logistics`
- 头程 FirstMile → `linkfox-shopee-store-first-mile`
- 退货退款 → `linkfox-shopee-store-returns`
- 支付结算 → `linkfox-shopee-store-payment`
- 选品 → `linkfox-youying-shopee-product-search`

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
