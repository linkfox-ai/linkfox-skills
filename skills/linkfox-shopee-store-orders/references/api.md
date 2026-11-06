# Shopee 店铺订单接口说明

本技能包含 22 个 Order 操作及 1 个 storeTokens 兼容函数，除 Feedback 共 23 个操作；订单业务均由 POST `/shopee/developerProxy` 转发。

| 操作 | 独立接口文档 |
|---|---|
| `get_order_list` | [apis/get-order-list.md](apis/get-order-list.md) |
| `get_order_detail` | [apis/get-order-detail.md](apis/get-order-detail.md) |
| `get_shipment_list` | [apis/get-shipment-list.md](apis/get-shipment-list.md) |
| `search_package_list` | [apis/search-package-list.md](apis/search-package-list.md) |
| `get_package_detail` | [apis/get-package-detail.md](apis/get-package-detail.md) |
| `split_order` | [apis/split-order.md](apis/split-order.md) |
| `unsplit_order` | [apis/unsplit-order.md](apis/unsplit-order.md) |
| `cancel_order` | [apis/cancel-order.md](apis/cancel-order.md) |
| `handle_buyer_cancellation` | [apis/handle-buyer-cancellation.md](apis/handle-buyer-cancellation.md) |
| `set_note` | [apis/set-note.md](apis/set-note.md) |
| `get_pending_buyer_invoice_order_list` | [apis/get-pending-buyer-invoice-order-list.md](apis/get-pending-buyer-invoice-order-list.md) |
| `get_buyer_invoice_info` | [apis/get-buyer-invoice-info.md](apis/get-buyer-invoice-info.md) |
| `upload_invoice_doc` | [apis/upload-invoice-doc.md](apis/upload-invoice-doc.md) |
| `download_invoice_doc` | [apis/download-invoice-doc.md](apis/download-invoice-doc.md) |
| `handle_prescription_check` | [apis/handle-prescription-check.md](apis/handle-prescription-check.md) |
| `get_warehouse_filter_config` | [apis/get-warehouse-filter-config.md](apis/get-warehouse-filter-config.md) |
| `get_booking_list` | [apis/get-booking-list.md](apis/get-booking-list.md) |
| `get_booking_detail` | [apis/get-booking-detail.md](apis/get-booking-detail.md) |
| `generate_fbs_invoices` | [apis/generate-fbs-invoices.md](apis/generate-fbs-invoices.md) |
| `get_fbs_invoices_result` | [apis/get-fbs-invoices-result.md](apis/get-fbs-invoices-result.md) |
| `download_fbs_invoices` | [apis/download-fbs-invoices.md](apis/download-fbs-invoices.md) |
| `get_estimiate_cancel_value` | [apis/get-estimiate-cancel-value.md](apis/get-estimiate-cancel-value.md) |
| `storeTokens` | [apis/store-tokens.md](apis/store-tokens.md) |

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 运行约定

- **依赖与选店**：运行 `python scripts/check_auth_dependency.py [--json]`；返回 0 表示已安装认证技能，返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示需安装 `linkfox-shopee-store-auth`。检查脚本保留环境变量、多平台和常用安装目录探测。`skipDepCheck=true` 仅跳过安装检查，不能替代授权。
- **认证兼容**：API Key 读取顺序为 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`；网关优先 `LINKFOX_TOOL_GATEWAY`，其次兼容变量 `SHOPEE_API_BASE_URL`，默认正式地址。每次调用保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头；HTTP POST 超时 150 秒。
- **令牌与授权状态**：订单脚本由服务端依 shopId / merchantId 解析并注入 token；调用方提供的 accessToken 不参与认证。resolve_store_tokens 可单独查询已授权状态，不返回原始令牌；订单 CLI 不自动串联此查询。本技能不实现授权或刷新流程。
- **CLI**：`python scripts/<操作名>.py '<JSON 参数>' [--inline] [--no-cache]`；或 `python scripts/order_api.py '{"api":"<操作名>", ...}' [--inline] [--no-cache]`。`--help` 展示本地帮助，无网络请求。GET 顶层业务标量组成 queryString；值百分号编码、布尔小写、编号列表逗号连接。POST 优先 body，再 requestBody，再注册表中的顶层业务字段；显式 null 在请求前拒绝，不回退到其他来源。
- **缓存**：订单脚本无响应缓存，全部业务封装始终向公共 `call_api.run` 传 `--no-cache`；不读写响应缓存，不增加另一层缓存。公共调用器可能创建空 `.cache` 目录。
- **完整响应与目录**：每次请求通过公共 run 保存完整的加工后结果，其中含原始 developerProxy。路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-orders-<接口标识>-<timestamp>.json`。SESSION_ID 优先，否则进程内生成；不得是路径。响应不超过 8000 UTF-8 字节时完整打印，超过则打印摘要及最大列表前三项；--inline 强制完整打印。业务封装在请求前检查当前目录，并创建本次会话下的完整响应文件；任一目录或文件不可写时不发送请求。固定根目录为 cwd/linkfox，禁止回退家目录或 /tmp。
- **错误和重试**：没有自动重试、自动换参或自动翻页；写操作结果不确定时先核对订单状态，避免重复提交。网关错误及代理错误见各接口业务规则，重新授权交给认证技能。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-orders",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
