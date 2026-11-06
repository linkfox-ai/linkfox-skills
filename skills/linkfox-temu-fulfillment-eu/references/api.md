# Temu 欧洲站履约与发货 接口说明

## 接口导航

| 操作 | 接口文档 | 对应脚本（相对技能根目录） |
|------|----------|----------|
| `bg.cooperativewarehouse.fulfill.cancel` | [取消合作仓履约单](apis/bg-cooperativewarehouse-fulfill-cancel.md) | `scripts/eu_co_warehouse_cooperativewarehouse_fulfill_cancel.py` |
| `bg.cooperativewarehouse.fulfill.submit` | [提交合作仓履约](apis/bg-cooperativewarehouse-fulfill-submit.md) | `scripts/eu_co_warehouse_cooperativewarehouse_fulfill_submit.py` |
| `bg.cooperativewarehouse.provider.list` | [合作仓服务商列表](apis/bg-cooperativewarehouse-provider-list.md) | `scripts/eu_co_warehouse_cooperativewarehouse_provider_list.py` |
| `bg.cooperativewarehouse.token.authorization` | [合作仓 Token 授权](apis/bg-cooperativewarehouse-token-authorization.md) | `scripts/eu_co_warehouse_cooperativewarehouse_token_authorization.py` |
| `bg.logistics.companies.get` | [获取区域可用物流商](apis/bg-logistics-companies-get.md) | `scripts/eu_self_fulfilled_logistics_companies_get.py` |
| `bg.logistics.shipment.create` | [在线下单购标](apis/bg-logistics-shipment-create.md) | `scripts/eu_buy_shipping_logistics_shipment_create.py` |
| `bg.logistics.shipment.document.get` | [获取面单/运单文档](apis/bg-logistics-shipment-document-get.md) | `scripts/eu_buy_shipping_logistics_shipment_document_get.py` |
| `bg.logistics.shipment.result.get` | [查询购标/在线下单结果](apis/bg-logistics-shipment-result-get.md) | `scripts/eu_buy_shipping_logistics_shipment_result_get.py` |
| `bg.logistics.shipment.shippingtype.update` | [更新物流跟踪号 / 发货方式](apis/bg-logistics-shipment-shippingtype-update.md) | `scripts/eu_self_fulfilled_logistics_shipment_shippingtype_update.py` |
| `bg.logistics.shipment.sub.confirm` | [确认子包裹发货](apis/bg-logistics-shipment-sub-confirm.md) | `scripts/eu_self_fulfilled_logistics_shipment_sub_confirm.py` |
| `bg.logistics.shipment.update` | [更新发货/重试购标](apis/bg-logistics-shipment-update.md) | `scripts/eu_buy_shipping_logistics_shipment_update.py` |
| `bg.logistics.shipment.v2.confirm` | [确认发货 V2](apis/bg-logistics-shipment-v2-confirm.md) | `scripts/eu_self_fulfilled_logistics_shipment_v2_confirm.py` |
| `bg.logistics.shipment.v2.get` | [查询发货信息 V2](apis/bg-logistics-shipment-v2-get.md) | `scripts/eu_self_fulfilled_logistics_shipment_v2_get.py` |
| `bg.logistics.shipped.package.confirm` | [确认包裹已发货](apis/bg-logistics-shipped-package-confirm.md) | `scripts/eu_buy_shipping_logistics_shipped_package_confirm.py` |
| `bg.logistics.shippingservices.get` | [查询可用物流渠道](apis/bg-logistics-shippingservices-get.md) | `scripts/eu_buy_shipping_logistics_shippingservices_get.py` |
| `bg.logistics.warehouse.list.get` | [店铺仓库列表](apis/bg-logistics-warehouse-list-get.md) | `scripts/eu_buy_shipping_logistics_warehouse_list_get.py` |
| `bg.order.unshipped.package.get` | [查询未发货包裹](apis/bg-order-unshipped-package-get.md) | `scripts/eu_buy_shipping_order_unshipped_package_get.py` |
| `temu.logistics.candidate.scanform.list.get` | [候选 Scan Form 包裹列表](apis/temu-logistics-candidate-scanform-list-get.md) | `scripts/eu_buy_shipping_logistics_candidate_scanform_list_get.py` |
| `temu.logistics.label.list.get` | [面单列表查询](apis/temu-logistics-label-list-get.md) | `scripts/eu_buy_shipping_logistics_label_list_get.py` |
| `temu.logistics.scanform.create` | [创建 Scan Form](apis/temu-logistics-scanform-create.md) | `scripts/eu_buy_shipping_logistics_scanform_create.py` |
| `temu.logistics.scanform.document.get` | [获取 Scan Form 文档](apis/temu-logistics-scanform-document-get.md) | `scripts/eu_buy_shipping_logistics_scanform_document_get.py` |
| `temu.logistics.scanform.get` | [查询 Scan Form 详情](apis/temu-logistics-scanform-get.md) | `scripts/eu_buy_shipping_logistics_scanform_get.py` |
| `temu.logistics.self.delivery.pod.audit.result.get` | [自配送 POD 审核结果查询](apis/temu-logistics-self-delivery-pod-audit-result-get.md) | `scripts/eu_self_fulfilled_logistics_self_delivery_pod_audit_result_get.py` |
| `temu.logistics.self.delivery.pod.upload.signature.query` | [自配送 POD 上传签名查询](apis/temu-logistics-self-delivery-pod-upload-signature-query.md) | `scripts/eu_self_fulfilled_logistics_self_delivery_pod_upload_signature_query.py` |
| `temu.logistics.self.delivery.pod.upload` | [自配送 POD 上传](apis/temu-logistics-self-delivery-pod-upload.md) | `scripts/eu_self_fulfilled_logistics_self_delivery_pod_upload.py` |
| `temu.logistics.shiplogisticstype.get` | [在线发货物流类型](apis/temu-logistics-shiplogisticstype-get.md) | `scripts/eu_buy_shipping_logistics_shiplogisticstype_get.py` |
| `temu.logistics.shipment.pickup.reservation.cancel` | [取消上门揽收预约](apis/temu-logistics-shipment-pickup-reservation-cancel.md) | `scripts/eu_buy_shipping_logistics_shipment_pickup_reservation_cancel.py` |
| `temu.logistics.shipment.pickup.reservation.create` | [预约上门揽收](apis/temu-logistics-shipment-pickup-reservation-create.md) | `scripts/eu_buy_shipping_logistics_shipment_pickup_reservation_create.py` |
| `temu.logistics.shipment.pickup.reservation.result.get` | [查询上门揽收预约结果](apis/temu-logistics-shipment-pickup-reservation-result-get.md) | `scripts/eu_buy_shipping_logistics_shipment_pickup_reservation_result_get.py` |
| `temu.track.trackinginfo.get` | [物流轨迹详情查询](apis/temu-track-trackinginfo-get.md) | `scripts/eu_tracking_track_trackinginfo_get.py` |
| `/temu/fileDownload` | [加签文件下载](apis/file-download.md) | `scripts/temu_eu_file_download.py` |

Partner 子菜单与官方 URL 见 [partner-eu-catalog.md](partner-eu-catalog.md)，分类索引见 [apis/README.md](apis/README.md)。

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

### 认证与网关兼容

| 参数或设置 | 类型 | 必填 | 默认或说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | CLI 支持的 LinkFox 用户令牌别名，按此顺序取首个非空值，优先于环境变量。不是 Temu `accessToken`，不放入业务 `params`。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 与上述令牌二选一 | 按此顺序读取。兼容 `Authorization` 与 `Token` 双请求头（同值），保留会话追踪头。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 原样放入同名追踪请求头；未配置时为空。`SESSION_ID` 同时用于响应文件的任务聚合。 |
| LINKFOX_TOOL_GATEWAY / TEMU_API_BASE_URL / STORE_API_BASE_URL | 环境变量 | 否 | 按此顺序取首个非空值；默认 `https://tool-gateway.linkfox.com`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 业务令牌，直接传入优先。 |
| storeKey | string | 与 accessToken 二选一 | 从本地令牌库按店铺、站点、管理方式和用途精确读取；不会传至网关。 |
| site | string | EU 入口可省略 | 默认 `eu`，EU 入口将显式值去空白并转小写，网关请求与本地选店使用同一归一化值。通用入口支持 `cn` / `partner` / `us` / `global` / `eu` 枚举并要求显式传入。 |
| managementType | string | EU 入口可省略 | 默认 `semi-managed`；EU 入口归一化后用于请求与本地选店。通用入口显式校验 `full-managed` / `semi-managed`。合作仓业务仅半托管。 |
| tokenPurpose | string | 否 | EU 本地选店默认 `order-shipping`；通用本地令牌工具默认 `default`。此字段用于本地令牌选择，不发送至网关。 |
| params | object | 否 | 显式对象优先，否则 EU 入口将顶层非保留字段作为业务参数；顶层 `request` 会原样放入 `params.request`，不会擅自再套一层。 |
| TEMU_TOKEN_STORE_PATH | 环境变量 | 否 | 覆盖 `~/.linkfox/temu-access-tokens.json`。这保存店铺授权，不是接口响应缓存。 |
| --inline | CLI flag | 否 | 强制完整输出，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务脚本不使用响应缓存；业务封装调用公共 `run` 时始终加入，读取与写入均不复用响应缓存。公共调用器仍可能创建空缓存目录。 |

所有脚本通过 JSON CLI 接收参数。EU 专用入口、`temu_eu_proxy.py` 与 `temu_eu_file_download.py` 均共享默认站点与选店逻辑；通用 `temu_proxy.py`、`temu_file_download.py` 要求显式传入站点和管理方式。LinkFox 业务请求统一经 `call_api.run`，兼容逻辑仅在业务模块中实现。业务响应解析为 `temuBody`，并完整保存一次；不可写的当前目录在请求前报错，不回退家目录或临时目录。`SESSION_ID` 用于聚合同一任务；未提供时在进程内生成稳定编号。

网关对外路径为 `/temu/proxy` 与 `/temu/fileDownload`；`type` 区分 Temu 操作，没有 `developerProxy.path`。紫鸟内部转发路径为 `/temu-proxy/{site}/{managementType}`，EU 半托管对应 `/temu-proxy/eu/semi-managed`；EU 上游为 `https://openapi-b-eu.temu.com/openapi/router`。调用方不直接向上述上游发送业务请求。

### 本地授权工具

| 脚本 | JSON 字段 | 行为 |
|------|------|------|
| `scripts/temu_token_guide.py` | `shopType`（可用 `managementType` 代替）、`tokenPurpose`、`site` | 输出手动授权步骤；完整店铺类型、用途、应用和注意事项见 [access-token.md](access-token.md)。 |
| `scripts/save_temu_access_token.py` | `storeKey`、`site`、`managementType`、`accessToken` 必填；`tokenPurpose` 默认 `default`；`label` 可选 | 按四元组保存或替换令牌，保留其他店铺记录。 |
| `scripts/get_temu_access_token.py` | `storeKey`、`site`、`managementType` 必填；`tokenPurpose` 默认 `default` | 精确读取；未找到返回 `found=false` 并退出 1。 |
| `scripts/list_temu_access_tokens.py` | `mask` 默认 `true` | 默认脱敏；显式 `false` 才展示完整令牌。 |
| `scripts/check_linkfox_token.py` | 可选 LinkFox 用户令牌别名 | 提供最小认证探测 CLI；会实际请求网关，不应为本地校验执行真实探测。其 `ok=true` 仅表示收到正常网关响应且未命中已知认证错误，不代表 Temu 店铺已授权；HTTP 或 `errcode` 异常时返回 `ok=false`，保留响应与实际 HTTP 状态。 |

授权细节见 [authorization-flow.md](authorization-flow.md)。子账号可能无法访问服务市场；多站点分别取令牌，过期后重取，调用前确认紫鸟 IP 白名单。

### 网关业务错误

| code | 说明 | 处理 |
|------|------|------|
| 1002 | 参数或 LinkFox Token 无效 | 核对参数与用户令牌，不能据此认定店铺业务成功。 |
| 1003 | 转发失败 | 核对 Temu 令牌、令牌用途、白名单与网络。 |

外层 HTTP 与 `errcode` 按固定公共规则判断；HTTP 401 / 402 或认证、计费消息按 [onboarding.md](onboarding.md) 处理。正常网关响应不保证 Temu 业务成功，操作状态见各接口。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-fulfillment-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
