# linkfox-temu-order-eu — API 参考

Temu **欧洲站订单管理**（Partner EU **Order / 订单发货** 相关接口），经本 skill `temu_eu_proxy`（`POST /temu/proxy`） 转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。订单场景 token 见 `references/access-token.md`（`tokenPurpose=order-shipping`）。

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 订单 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_eu_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token` |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=eu`，`managementType=semi-managed`，`tokenPurpose=order-shipping` |
| 上游 OpenAPI（EU） | `https://openapi-b-eu.temu.com/openapi/router`（网关按 `site` 解析） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `eu`（本 skill 默认） |
| managementType | string | 是 | `semi-managed` |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌 |
| storeKey | string | 与 accessToken 二选一 | `~/.linkfox/temu-access-tokens.json` 中的键 |
| tokenPurpose | string | 否 | 建议 **`order-shipping`**（订单/发货） |
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
python scripts/eu_order_list_v2_get.py '{"accessToken":"TOKEN","tokenPurpose":"order-shipping","request":{"pageNumber":1,"pageSize":20,"parentOrderStatus":2}}'
```

业务字段可放在顶层或嵌套 `params`；含 `request` 时通常整体作为 `params` 转发。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-eu-catalog.md](./partner-eu-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)（随接入递增）。

已接入接口见 [apis/README.md](./apis/README.md)。

---

## 典型订单管理流程

```text
1. bg.order.list.v2.get（本 skill）                    → 按状态/时间/父单号分页查订单列表
2. bg.order.detail.v2.get（本 skill）                  → 按 parentOrderSn 拉父单+子单完整详情
3. bg.order.shippinginfo.v2.get（本 skill）            → 按 parentOrderSn 拉收货地址（含 warning）
4. bg.order.decryptshippinginfo.get（本 skill）        → 按 parentOrderSn 拉**敏感/解密**收货地址
5. bg.order.amount.query（本 skill）                   → 按 parentOrderSn 拉供货价/金额（ERP 对账，V1）
5b. temu.order.amount.v2.query / v3.query（本 skill） → 按 parentOrderSn 拉销售/客户支付金额（V2 细税费 / V3 含税价）
6. bg.order.combinedshipment.list.get（本 skill）      → 拉可合并发货的父订单组
7. bg.order.customization.get（本 skill）              → 按 orderSnList（≤10）拉定制商品内容
8. temu.local.order.verification.upload（本 skill）  → 上传 SN/IMEI 或二手鉴真编码
9. （待补充）合并发货确认/面单等                        → 填运单、确认发货
10. 取消订单（买家/卖家）                               → **`linkfox-temu-cancel-order-eu`**
11. 履约/发货（购标、自发货、合作仓、跟踪）         → **`linkfox-temu-fulfillment-eu`**
```

商品信息请用 **`linkfox-temu-manage-product-eu`**；发品请用 **`linkfox-temu-add-product-us`**；取消订单请用 **`linkfox-temu-cancel-order-eu`**；履约/发货请用 **`linkfox-temu-fulfillment-eu`**。

---

## 网关错误码

| code | 说明 | 处理 |
|------|------|------|
| 1002 | 参数或 LinkFox Token 无效 | 修正参数与 `LINKFOXAGENT_API_KEY` |
| 1003 | 转发失败 | 检查 Temu token、`tokenPurpose`、白名单、网络 |

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: **`linkfox-temu-order-eu`**
