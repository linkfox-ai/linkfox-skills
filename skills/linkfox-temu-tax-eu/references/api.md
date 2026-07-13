# linkfox-temu-tax-eu — API 参考

Temu **欧洲站电商税务（Tax）**（Partner EU **Tax** 菜单相关接口），经本 skill `temu_eu_proxy`（`POST /temu/proxy`） 转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。授权见 [access-token.md](./access-token.md)（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）。

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 税务 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_eu_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=eu`，`managementType=semi-managed`，`tokenPurpose=product-inventory` |
| 上游 OpenAPI（EU） | `https://openapi-b-eu.temu.com/openapi/router`（网关按 `site` 解析） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `eu`（本 skill 默认） |
| managementType | string | 是 | `semi-managed` |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌 |
| storeKey | string | 与 accessToken 二选一 | `~/.linkfox/temu-access-tokens.json` 中的键 |
| tokenPurpose | string | 否 | 默认 `product-inventory`；以 Partner 文档为准 |
| type | string | 是 | Temu 接口名（Partner Tax 文档中的 `type`） |
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
python scripts/temu_eu_proxy.py '{"accessToken":"TOKEN","type":"<PARTNER_TYPE>","request":{}}'
```

业务字段可放在顶层或嵌套 `params`；含 `request` 时通常整体作为 `params` 转发。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-eu-catalog.md](./partner-eu-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)（随你提供的 Partner 文档递增）。

当前 **7** 个业务 `type` 已接入；见 [apis/README.md](./apis/README.md)。

---

## 典型税务流程

```text
1. temu.pay.tax.get.galerie.signature        → 获取文件上传签名
2. temu.pay.tax.merchant.upload.invoice      → 商家上传发票/贷项通知单
3. temu.pay.tax.invoice.info.query           → 发票摘要（parentOrderSnList ≤20）
4. temu.pay.tax.invoice.detail.query         → 发票明细（含 VAT/商品/运费）
5. temu.pay.tax.invoice.pdf.download         → 发票 PDF 加签 URL
6. temu.pay.tax.apply.export.report          → 申请导出月度报表（返回 taskId）
7. temu.pay.tax.merchant.report.download     → 下载报表文件
```

---

## 与其它 EU skill 的关系

| 能力 | skill |
|------|--------|
| 税务（本 skill） | **`linkfox-temu-tax-eu`** |
| 商品管理（可含 `taxCodeInfo` 等） | `linkfox-temu-manage-product-eu` |
| 订单金额（含税字段） | `linkfox-temu-order-eu` |
| 价格 | `linkfox-temu-price-eu` |

---

## 网关错误码

| code | 说明 | 处理 |
|------|------|------|
| HTTP 401 | authorized error | 按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| HTTP 402 | — | 按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 1002 | 参数或 LinkFox Token 无效 | 修正参数与 `LINKFOXAGENT_API_KEY` |
| 1003 | 转发失败 | 检查 Temu token、白名单、网络 |

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: **`linkfox-temu-tax-eu`**
