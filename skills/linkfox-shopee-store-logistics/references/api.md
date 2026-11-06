# Shopee 店铺物流管理 接口说明

46 个物流操作按文件独立定义，另提供 `storeTokens` 授权状态兼容查询。每个文件包含本接口的网关字段、脚本参数及运行约定；Shopee 内部业务字段按各页官方文档与实际查询结果核对，不推测补齐。

| 操作 | 上游方法与转发 path | 接口文档 |
|---|---|---|
| `get_shipping_parameter` | GET `api/v2/logistics/get_shipping_parameter` | [apis/get-shipping-parameter.md](apis/get-shipping-parameter.md) |
| `get_mass_shipping_parameter` | POST `api/v2/logistics/get_mass_shipping_parameter` | [apis/get-mass-shipping-parameter.md](apis/get-mass-shipping-parameter.md) |
| `ship_order` | POST `api/v2/logistics/ship_order` | [apis/ship-order.md](apis/ship-order.md) |
| `mass_ship_order` | POST `api/v2/logistics/mass_ship_order` | [apis/mass-ship-order.md](apis/mass-ship-order.md) |
| `update_shipping_order` | POST `api/v2/logistics/update_shipping_order` | [apis/update-shipping-order.md](apis/update-shipping-order.md) |
| `get_tracking_number` | GET `api/v2/logistics/get_tracking_number` | [apis/get-tracking-number.md](apis/get-tracking-number.md) |
| `get_mass_tracking_number` | POST `api/v2/logistics/get_mass_tracking_number` | [apis/get-mass-tracking-number.md](apis/get-mass-tracking-number.md) |
| `get_shipping_document_parameter` | GET `api/v2/logistics/get_shipping_document_parameter` | [apis/get-shipping-document-parameter.md](apis/get-shipping-document-parameter.md) |
| `create_shipping_document` | POST `api/v2/logistics/create_shipping_document` | [apis/create-shipping-document.md](apis/create-shipping-document.md) |
| `get_shipping_document_result` | GET `api/v2/logistics/get_shipping_document_result` | [apis/get-shipping-document-result.md](apis/get-shipping-document-result.md) |
| `download_shipping_document` | GET `api/v2/logistics/download_shipping_document` | [apis/download-shipping-document.md](apis/download-shipping-document.md) |
| `get_shipping_document_data_info` | GET `api/v2/logistics/get_shipping_document_data_info` | [apis/get-shipping-document-data-info.md](apis/get-shipping-document-data-info.md) |
| `get_tracking_info` | GET `api/v2/logistics/get_tracking_info` | [apis/get-tracking-info.md](apis/get-tracking-info.md) |
| `get_address_list` | GET `api/v2/logistics/get_address_list` | [apis/get-address-list.md](apis/get-address-list.md) |
| `set_address_config` | POST `api/v2/logistics/set_address_config` | [apis/set-address-config.md](apis/set-address-config.md) |
| `update_address` | POST `api/v2/logistics/update_address` | [apis/update-address.md](apis/update-address.md) |
| `delete_address` | POST `api/v2/logistics/delete_address` | [apis/delete-address.md](apis/delete-address.md) |
| `get_channel_list` | GET `api/v2/logistics/get_channel_list` | [apis/get-channel-list.md](apis/get-channel-list.md) |
| `update_channel` | POST `api/v2/logistics/update_channel` | [apis/update-channel.md](apis/update-channel.md) |
| `get_operating_hours` | GET `api/v2/logistics/get_operating_hours` | [apis/get-operating-hours.md](apis/get-operating-hours.md) |
| `get_operating_hour_restrictions` | GET `api/v2/logistics/get_operating_hour_restrictions` | [apis/get-operating-hour-restrictions.md](apis/get-operating-hour-restrictions.md) |
| `update_operating_hours` | POST `api/v2/logistics/update_operating_hours` | [apis/update-operating-hours.md](apis/update-operating-hours.md) |
| `delete_special_operating_hour` | POST `api/v2/logistics/delete_special_operating_hour` | [apis/delete-special-operating-hour.md](apis/delete-special-operating-hour.md) |
| `batch_update_tpf_warehouse_tracking_status` | POST `api/v2/logistics/batch_update_tpf_warehouse_tracking_status` | [apis/batch-update-tpf-warehouse-tracking-status.md](apis/batch-update-tpf-warehouse-tracking-status.md) |
| `batch_ship_order` | POST `api/v2/logistics/batch_ship_order` | [apis/batch-ship-order.md](apis/batch-ship-order.md) |
| `update_tracking_status` | POST `api/v2/logistics/update_tracking_status` | [apis/update-tracking-status.md](apis/update-tracking-status.md) |
| `get_booking_shipping_parameter` | GET `api/v2/logistics/get_booking_shipping_parameter` | [apis/get-booking-shipping-parameter.md](apis/get-booking-shipping-parameter.md) |
| `ship_booking` | POST `api/v2/logistics/ship_booking` | [apis/ship-booking.md](apis/ship-booking.md) |
| `get_booking_tracking_number` | GET `api/v2/logistics/get_booking_tracking_number` | [apis/get-booking-tracking-number.md](apis/get-booking-tracking-number.md) |
| `get_booking_shipping_document_parameter` | GET `api/v2/logistics/get_booking_shipping_document_parameter` | [apis/get-booking-shipping-document-parameter.md](apis/get-booking-shipping-document-parameter.md) |
| `create_booking_shipping_document` | POST `api/v2/logistics/create_booking_shipping_document` | [apis/create-booking-shipping-document.md](apis/create-booking-shipping-document.md) |
| `get_booking_shipping_document_result` | GET `api/v2/logistics/get_booking_shipping_document_result` | [apis/get-booking-shipping-document-result.md](apis/get-booking-shipping-document-result.md) |
| `download_booking_shipping_document` | GET `api/v2/logistics/download_booking_shipping_document` | [apis/download-booking-shipping-document.md](apis/download-booking-shipping-document.md) |
| `get_booking_shipping_document_data_info` | GET `api/v2/logistics/get_booking_shipping_document_data_info` | [apis/get-booking-shipping-document-data-info.md](apis/get-booking-shipping-document-data-info.md) |
| `get_booking_tracking_info` | GET `api/v2/logistics/get_booking_tracking_info` | [apis/get-booking-tracking-info.md](apis/get-booking-tracking-info.md) |
| `download_to_label` | GET `api/v2/logistics/download_to_label` | [apis/download-to-label.md](apis/download-to-label.md) |
| `create_shipping_document_job` | POST `api/v2/logistics/create_shipping_document_job` | [apis/create-shipping-document-job.md](apis/create-shipping-document-job.md) |
| `get_shipping_document_job_status` | GET `api/v2/logistics/get_shipping_document_job_status` | [apis/get-shipping-document-job-status.md](apis/get-shipping-document-job-status.md) |
| `download_shipping_document_job` | GET `api/v2/logistics/download_shipping_document_job` | [apis/download-shipping-document-job.md](apis/download-shipping-document-job.md) |
| `update_self_collection_order_logistics` | POST `api/v2/logistics/update_self_collection_order_logistics` | [apis/update-self-collection-order-logistics.md](apis/update-self-collection-order-logistics.md) |
| `get_mart_packaging_info` | GET `api/v2/logistics/get_mart_packaging_info` | [apis/get-mart-packaging-info.md](apis/get-mart-packaging-info.md) |
| `set_mart_packaging_info` | POST `api/v2/logistics/set_mart_packaging_info` | [apis/set-mart-packaging-info.md](apis/set-mart-packaging-info.md) |
| `upload_serviceable_polygon` | POST `api/v2/logistics/upload_serviceable_polygon` | [apis/upload-serviceable-polygon.md](apis/upload-serviceable-polygon.md) |
| `check_polygon_update_status` | GET `api/v2/logistics/check_polygon_update_status` | [apis/check-polygon-update-status.md](apis/check-polygon-update-status.md) |
| `get_pause_status` | GET `api/v2/logistics/get_pause_status` | [apis/get-pause-status.md](apis/get-pause-status.md) |
| `set_pause_status` | POST `api/v2/logistics/set_pause_status` | [apis/set-pause-status.md](apis/set-pause-status.md) |
| `storeTokens` | POST `/shopee/storeTokens`（非代理转发） | [apis/store-tokens.md](apis/store-tokens.md) |

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

## 脚本运行约定

- 通用入口：`python scripts/logistics_api.py '<JSON 参数>' [--inline] [--no-cache]`，JSON 另含 `api`，取上表 46 个物流操作名。独立脚本不需要此字段。
- 本地依赖检测成功退出 0；缺失或检测失败退出 42，stderr 含 `DEPENDENCY_MISSING:`。支持 `LINKFOX_SKILLS_DIR`、`SKILLS_DIR`、`CURSOR_SKILLS_DIR`、`HERMES_SKILLS_EXTERNAL_DIRS`、OpenClaw 工作区与常见用户技能目录。`skipDepCheck` 默认 false；仅在外部已确认依赖时跳过安装检查，不绕过店铺授权。
- 网关环境变量优先级：`LINKFOX_TOOL_GATEWAY` → `SHOPEE_API_BASE_URL` → `https://tool-gateway.linkfox.com`。API Key 同时兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`。
- 业务封装调用公共 `call_api.run` 始终传 `--no-cache`，不读写响应缓存。公共脚本可能创建空缓存目录；需要复用结果时，从已保存的完整响应中读取。
- 完整响应保存到当前工作目录的会话 data 目录，使用微秒时间戳避免同秒覆盖。请求前检查完整会话输出目录的可写性；工作目录或 data 目录不可写时直接报错，不回退至其他目录。`--inline` 保留全量打印行为；默认按 8000 字节阈值输出完整响应或摘要。
- POST 的字符串 `body` / `requestBody` 必须是有效 JSON；空字符串、纯空白或其他非法 JSON 在发起请求前报错。有效字符串保持原样转发，对象仍紧凑序列化。
- 禁止在 `/tmp` 及其子目录执行会落盘的物流请求；业务封装在请求前拒绝该工作目录，不回退至临时目录。
- 仅从授权技能取得选店与授权信息；storeTokens 兼容函数可查询已有授权状态，不返回原始令牌。日常物流请求直接按 shopId / merchantId 选店，由代理服务端解析令牌，不额外调用 storeTokens。

## 网关业务错误

| errcode | 含义 | 处理建议 |
|---|---|---|
| 1002 | 参数错误或未登录 | 核对店铺与 API Key。 |
| 1003 | 代理或网络异常 | 保留错误；物流写入结果不明时先核对，后续调用遵守调用约束。 |
| 1004 | 无授权记录 | 交由授权技能处理。 |
| 1005 | path 未列入白名单 | 核对物流相对路径，必要时由服务端确认白名单。 |

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-logistics",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
