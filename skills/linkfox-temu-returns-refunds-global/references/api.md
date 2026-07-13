# linkfox-temu-returns-refunds-global — API 参考

Temu **全球站退货与退款（Returns & Refunds）**，经本 skill `temu_global_proxy`（`POST /temu/proxy`） 转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。建议 token 见 `references/access-token.md`（`tokenPurpose=order-shipping`）。（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 退货退款 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_global_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=global`，`managementType=semi-managed`，`tokenPurpose=order-shipping` |
| 上游 OpenAPI（Global） | `https://openapi-b-global.temu.com/openapi/router`（网关按 `site` 解析） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `global`（本 skill 默认） |
| managementType | string | 是 | `semi-managed` |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌 |
| storeKey | string | 与 accessToken 二选一 | `~/.linkfox/temu-access-tokens.json` 中的键 |
| tokenPurpose | string | 否 | 建议 **`order-shipping`** |
| type | string | 是 | Temu 接口名，如 Partner Returns & Refunds 菜单下的 `bg.*` / `temu.*` |
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
python scripts/temu_global_proxy.py '{"accessToken":"TOKEN","tokenPurpose":"order-shipping","type":"<API_TYPE>","params":{"request":{}}}'
```

业务字段可放在顶层或嵌套 `params`；含 `request` 时通常整体作为 `params` 转发。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-global-catalog.md](./partner-global-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)（随接入递增）。

| type | 说明 | 文档 |
|------|------|------|
| `bg.aftersales.aftersales.list.get` | 子售后单列表查询 | [bg-aftersales-aftersales-list-get.md](./apis/bg-aftersales-aftersales-list-get.md) |
| `bg.aftersales.parentaftersales.list.get` | 父售后单列表查询 | [bg-aftersales-parentaftersales-list-get.md](./apis/bg-aftersales-parentaftersales-list-get.md) |
| `bg.aftersales.parentreturnorder.get` | 父退货物流信息 | [bg-aftersales-parentreturnorder-get.md](./apis/bg-aftersales-parentreturnorder-get.md) |
| `temu.aftersales.carrier.get` | 承运商列表 | [temu-aftersales-carrier-get.md](./apis/temu-aftersales-carrier-get.md) |
| `temu.aftersales.parentaftersales.detail.get` | 父售后单详情 | [temu-aftersales-parentaftersales-detail-get.md](./apis/temu-aftersales-parentaftersales-detail-get.md) |
| `temu.aftersales.returnaddress.get` | 退货地址查询 | [temu-aftersales-returnaddress-get.md](./apis/temu-aftersales-returnaddress-get.md) |
| `temu.aftersales.returnlabel.prepare.get` | 退货面单准备信息 | [temu-aftersales-returnlabel-prepare-get.md](./apis/temu-aftersales-returnlabel-prepare-get.md) |
| `temu.aftersales.signature.get` | 售后签名获取 | [temu-aftersales-signature-get.md](./apis/temu-aftersales-signature-get.md) |
| `temu.aftersales.upload.returnlabel` | 上传退货面单 | [temu-aftersales-upload-returnlabel.md](./apis/temu-aftersales-upload-returnlabel.md) |

---

## 与「取消订单」skill 的区分

| 能力 | skill | 典型场景 |
|------|--------|----------|
| 买家/卖家**取消订单**（未发货或取消申请） | `linkfox-temu-cancel-order-global` | `bg.aftersales.cancel.*`、`temu.order.cancel.*` |
| **退货、退款、售后退货退款** | **`linkfox-temu-returns-refunds-global`**（本 skill） | Partner **Returns & Refunds** 菜单下 9 条接口（见 [apis/README.md](./apis/README.md)） |

订单上下文（`parentOrderSn`、`orderSn`、售后单号等）通常先通过 **`linkfox-temu-order-global`** 获取。

---

## 典型退货退款流程

```text
1. linkfox-temu-order-global                              → 订单/售后上下文
2. bg.aftersales.parentaftersales.list.get            → 父售后单列表（筛选状态与时间）
3. temu.aftersales.parentaftersales.detail.get        → 父售后详情（退款汇总、子单）
4. bg.aftersales.aftersales.list.get                  → 子售后行项
5. temu.aftersales.returnlabel.prepare.get            → 面单准备（仓、揽收时段）
6. temu.aftersales.carrier.get                        → 承运商
7. temu.aftersales.signature.get（若需要）            → 签名
8. temu.aftersales.upload.returnlabel                 → 上传面单
9. bg.aftersales.parentreturnorder.get                → 查询退货运单
10. temu.aftersales.returnaddress.get                 → 买家寄回地址（自寄场景）
```

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
- `skillName`: **`linkfox-temu-returns-refunds-global`**
