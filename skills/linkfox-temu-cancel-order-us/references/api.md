# linkfox-temu-cancel-order-us — API 参考

Temu **美国站取消订单**（买家取消 + 卖家取消）（Partner US **Cancel Order** — 买家 `bg.aftersales.cancel.*` + 卖家 `temu.order.cancel.*`），经本 skill `temu_us_proxy`（`POST /temu/proxy`） 转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。建议 token 见 `references/access-token.md`（`tokenPurpose=order-shipping`）。

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `LINKFOX_TOOL_GATEWAY` / `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 卖家取消单 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_us_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token` |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=us`，`managementType=semi-managed`，`tokenPurpose=order-shipping` |
| 上游 OpenAPI（US） | `https://openapi-b-us.temu.com/openapi/router`（网关按 `site` 解析） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `us`（本 skill 默认） |
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
python scripts/temu_us_proxy.py '{"accessToken":"TOKEN","tokenPurpose":"order-shipping","type":"<API_TYPE>","params":{"request":{}}}'
```

业务字段可放在顶层或嵌套 `params`；含 `request` 时通常整体作为 `params` 转发。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-us-catalog.md](./partner-us-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)（随接入递增）。

> 已接入接口见 [apis/README.md](./apis/README.md)。

---

## 典型买家取消流程

```text
1. bg.aftersales.cancel.list.get（本 skill）  → 查待处理买家取消售后（afterSalesStatusGroup=8 等）
2. bg.aftersales.cancel.agree（本 skill）     → 同意取消（parentAfterSalesSn + parentOrderSn）
3. linkfox-temu-order-us                     → 刷新订单状态
```

## 典型卖家取消流程

```text
1. linkfox-temu-order-us                           → 查订单 parentOrderSn / orderSn、发货状态
2a. temu.order.cancel.appeal.apply（本 skill）       → 申诉类取消申请，返回 applySn
2b. temu.order.cancel.outofstock.apply（本 skill）   → 缺货取消申请（提交风控），返回 applyResult
3. temu.order.cancel.appeal.result.get（本 skill）   → 按 applySnList 查询申诉 status
4. linkfox-temu-order-us                           → 取消后刷新订单状态（list/detail）
```

---

## 网关错误码

| code | 说明 | 处理 |
|------|------|------|
| 1002 | 参数或 LinkFox Token 无效 | 修正参数与 `LINKFOXAGENT_API_KEY` |
| 1003 | 转发失败 | 检查 Temu token、`tokenPurpose`、白名单、网络 |

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: **`linkfox-temu-cancel-order-us`**
