# linkfox-temu-fulfillment-eu — API 参考

Temu **欧洲站电商履行/发货**（Buy-Shipping + Co-Warehouse + Self-Fulfilled + Tracking），经 `temu_eu_proxy`（`POST /temu/proxy`）转发。

> 网关与鉴权见 `scripts/`；`tokenPurpose=order-shipping`。

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 履约 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_eu_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=eu`，`managementType=semi-managed`，`tokenPurpose=order-shipping` |
| 上游 OpenAPI（US） | `https://openapi-b-eu.temu.com/openapi/router`（网关按 `site` 解析） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `eu`（本 skill 默认） |
| managementType | string | 是 | `semi-managed` |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌 |
| storeKey | string | 与 accessToken 二选一 | `~/.linkfox/temu-access-tokens.json` 中的键 |
| tokenPurpose | string | 否 | 建议 **`order-shipping`** |
| type | string | 是 | Temu 接口名，如 Partner 文档中的 `bg.*` / `temu.*` |
| params | object | 否 | 业务参数；多数接口业务块在 **`params.request`** |

### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| body | string | Temu 原始 JSON 字符串；脚本解析为 `temuBody` |
| code | integer | 网关错误码：`1002` 参数/Token，`1003` 转发失败 |

解析顺序：**网关 `code`** → `JSON.parse(body)` → `success` / `errorCode` / `errorMsg` / `result`。

### 脚本调用

```bash
export LINKFOXAGENT_API_KEY="<key>"
python scripts/temu_eu_proxy.py '{"accessToken":"TOKEN","tokenPurpose":"order-shipping","type":"<API_TYPE>","params":{"request":{}}}'
```

业务字段可放在顶层或嵌套 `params`；含 `request` 时通常整体作为 `params` 转发。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-eu-catalog.md](./partner-eu-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)（随接入递增）。

| type | 说明 | 文档 |
|------|------|------|
| `bg.logistics.warehouse.list.get` | 获取店铺仓库列表（可筛支持购标仓库） | [apis/bg-logistics-warehouse-list-get.md](./apis/bg-logistics-warehouse-list-get.md) |
| `temu.logistics.shiplogisticstype.get` | 获取在线发货物流类型（购标前选类型） | [apis/temu-logistics-shiplogisticstype-get.md](./apis/temu-logistics-shiplogisticstype-get.md) |
| `bg.logistics.shippingservices.get` | 按包裹尺寸/重量查询可用物流渠道（Buy-Shipping 查价） | [apis/bg-logistics-shippingservices-get.md](./apis/bg-logistics-shippingservices-get.md) |
| `bg.logistics.shipment.create` | 在线下单购标（创建包裹，返回 packageSnList） | [apis/bg-logistics-shipment-create.md](./apis/bg-logistics-shipment-create.md) |
| `bg.logistics.shipment.result.get` | 查询购标/在线下单结果（shippingLabelStatus） | [apis/bg-logistics-shipment-result-get.md](./apis/bg-logistics-shipment-result-get.md) |
| `bg.logistics.shipment.update` | 延后发货时限更新 / 购标失败包裹重试 | [apis/bg-logistics-shipment-update.md](./apis/bg-logistics-shipment-update.md) |
| `bg.logistics.shipment.document.get` | 获取面单/运单文档 URL（PDF/PNG） | [apis/bg-logistics-shipment-document-get.md](./apis/bg-logistics-shipment-document-get.md) |
| `bg.order.unshipped.package.get` | 查询 Temu 集成物流已履约、未发货确认的包裹 | [apis/bg-order-unshipped-package-get.md](./apis/bg-order-unshipped-package-get.md) |
| `temu.logistics.label.list.get` | 查询 Temu 平台购标面单列表（筛选/分页） | [apis/temu-logistics-label-list-get.md](./apis/temu-logistics-label-list-get.md) |
| `bg.logistics.shipped.package.confirm` | 批量确认包裹已发货（购标后出库） | [apis/bg-logistics-shipped-package-confirm.md](./apis/bg-logistics-shipped-package-confirm.md) |
| `temu.logistics.candidate.scanform.list.get` | 查询可生成 Scan Form 的候选包裹分组 | [apis/temu-logistics-candidate-scanform-list-get.md](./apis/temu-logistics-candidate-scanform-list-get.md) |
| `temu.logistics.scanform.create` | 创建 Scan Form（USPS manifestation 等） | [apis/temu-logistics-scanform-create.md](./apis/temu-logistics-scanform-create.md) |
| `temu.logistics.scanform.get` | 查询 Scan Form 详情（状态、分页筛选） | [apis/temu-logistics-scanform-get.md](./apis/temu-logistics-scanform-get.md) |
| `temu.logistics.scanform.document.get` | 获取 Scan Form 文档 URL | [apis/temu-logistics-scanform-document-get.md](./apis/temu-logistics-scanform-document-get.md) |
| `temu.logistics.shipment.pickup.reservation.create` | 预约上门揽收（同渠道同仓，最多 50 包裹/次） | [apis/temu-logistics-shipment-pickup-reservation-create.md](./apis/temu-logistics-shipment-pickup-reservation-create.md) |
| `temu.logistics.shipment.pickup.reservation.result.get` | 查询上门揽收预约结果（reservationSn / reservationStatus） | [apis/temu-logistics-shipment-pickup-reservation-result-get.md](./apis/temu-logistics-shipment-pickup-reservation-result-get.md) |
| `temu.logistics.shipment.pickup.reservation.cancel` | 取消上门揽收预约（reservationSn） | [apis/temu-logistics-shipment-pickup-reservation-cancel.md](./apis/temu-logistics-shipment-pickup-reservation-cancel.md) |
| `temu.logistics.self.delivery.pod.upload.signature.query` | 自配送 POD 上传签名查询 | [apis/temu-logistics-self-delivery-pod-upload-signature-query.md](./apis/temu-logistics-self-delivery-pod-upload-signature-query.md) |
| `temu.logistics.self.delivery.pod.upload` | 自配送 POD 凭证上传（按包裹提交 proofUrlList） | [apis/temu-logistics-self-delivery-pod-upload.md](./apis/temu-logistics-self-delivery-pod-upload.md) |
| `temu.logistics.self.delivery.pod.audit.result.get` | 自配送 POD 审核结果查询（按 applySnList，最多 100） | [apis/temu-logistics-self-delivery-pod-audit-result-get.md](./apis/temu-logistics-self-delivery-pod-audit-result-get.md) |

---

## 典型 Buy-Shipping 流程

```text
1. linkfox-temu-order-eu                    → 查待发货订单（注意 earliestTimeBuyShippingLabel 等字段）
2. bg.logistics.warehouse.list.get          → 仓库列表 / warehouseId（购标可用仓库）
3. temu.logistics.shiplogisticstype.get     → 在线发货物流类型 shipLogisticsType
4. bg.logistics.shippingservices.get        → 可用渠道 / channelId、估价
5. bg.logistics.shipment.create              → 购标，获得 packageSnList
6. temu.logistics.shipment.pickup.reservation.create（可选） → 需上门揽收渠道时预约时段
7. temu.logistics.shipment.pickup.reservation.result.get → 查询揽收预约结果
8. temu.logistics.shipment.pickup.reservation.cancel（可选） → 取消揽收预约
9. bg.logistics.shipment.result.get         → 轮询购标结果 / 面单状态
10. bg.logistics.shipment.update             → 调整 shipLaterLimitTime 或失败包裹重试
11. temu.logistics.candidate.scanform.list.get（可选） → 可合并 Scan Form 的候选包裹分组
12. temu.logistics.scanform.create（可选）   → USPS 等创建 Scan Form / manifestation
13. temu.logistics.scanform.get（可选）      → 查询 Scan Form 状态与详情
14. temu.logistics.scanform.document.get    → Scan Form 文档 url
15. bg.logistics.shipment.document.get      → 面单 URL；temu_eu_file_download 下载 PDF/PNG
16. temu.logistics.label.list.get            → 面单列表查询（状态/打印/时间窗筛选）
17. bg.order.unshipped.package.get          → 已购标、待发货确认包裹列表
18. bg.logistics.shipped.package.confirm    → 确认已发货（48h 内未确认可能自动转已发货）
19. linkfox-temu-order-eu                   → 刷新订单发货状态
```

订单列表/详情/地址解密等请用 **`linkfox-temu-order-eu`**。卖家自带运单号发货请用 **`linkfox-temu-fulfillment-eu`**。

---

## 网关错误码

| code | 说明 | 处理 |
|------|------|------|
| 1002 | 参数或 LinkFox Token 无效 | 修正参数与 `LINKFOXAGENT_API_KEY` |
| 1003 | 转发失败 | 检查 Temu token、`tokenPurpose`、白名单、网络 |
| 402 | HTTP 402 | 按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: **`linkfox-temu-fulfillment-eu`**

## 典型 Co-Warehouse 流程

```text
1. linkfox-temu-order-eu                         → 查待履约订单（合作仓相关字段）
2. bg.cooperativewarehouse.provider.list         → 可选合作仓服务商、permitsStatus
3. bg.cooperativewarehouse.token.authorization   → 服务商 Token 授权
4. bg.cooperativewarehouse.fulfill.submit        → 提交合作仓履约
5. bg.cooperativewarehouse.fulfill.cancel        → 取消合作仓履约单
6. bg.cooperativewarehouse.fulfill.query         → 查询履约状态（待接入）
7. linkfox-temu-fulfillment-eu          → 物流轨迹（如需要）
8. linkfox-temu-order-eu                         → 刷新订单履约状态
```

---

## 典型自发货流程

```text
1. linkfox-temu-order-eu                    → 查待发货订单（fulfillmentType=fulfillBySeller）
2. bg.logistics.companies.get               → carrierId（= logisticsServiceProviderId）
3. linkfox-temu-fulfillment-eu   → bg.logistics.warehouse.list.get（warehouseId）
4. bg.logistics.shipment.v2.confirm         → 确认发货（主流程）
5. bg.logistics.shipment.v2.get             → 核对运单/包裹/轨迹预警
6. bg.logistics.shipment.sub.confirm        → 拆包追加子包裹（可选）
7. bg.logistics.shipment.shippingtype.update → 更正跟踪号 / 集成改非集成（可选）
8. linkfox-temu-order-eu                    → 刷新订单发货状态
```

订单列表/详情/地址解密等请用 **`linkfox-temu-order-eu`**；商品与库存请用 **`linkfox-temu-manage-product-eu`**。

---

## 物流跟踪

```text
temu.track.trackinginfo.get（本 skill，eu_tracking_track_trackinginfo_get.py）
```

---

## 典型 Self-Delivery POD 流程（EU）

```text
1. linkfox-temu-order-eu                                      → 确认需上传 POD 的包裹 packageSn
2. temu.logistics.self.delivery.pod.upload.signature.query    → 获取上传签名 signature
3. （将 POD 图片上传至 Temu 存储，得到 proofUrl）
4. temu.logistics.self.delivery.pod.upload                    → 提交 podPackageInfoList（packageSn + proofUrlList），获得 applySn
5. temu.logistics.self.delivery.pod.audit.result.get          → 按 applySnList 查询 reviewStatus / rejectedReasonList
6. linkfox-temu-order-eu                                      → 刷新订单履约状态
```
