# linkfox-temu-compliance-global — API 参考

Temu **全球站电商合规**（Partner Global **Product Compliance / 商品合规**），经本 skill `temu_global_proxy`（`POST /temu/proxy`）转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。授权见 `references/access-token.md`。

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 合规 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_global_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=global`，`managementType=semi-managed`，`tokenPurpose=product-inventory` |
| 上游 OpenAPI（Global） | `https://openapi-b-global.temu.com/openapi/router`（网关按 `site` 解析） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `global`（本 skill 默认） |
| managementType | string | 是 | `semi-managed` |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌 |
| storeKey | string | 与 accessToken 二选一 | `~/.linkfox/temu-access-tokens.json` 中的键 |
| tokenPurpose | string | 否 | 建议 `product-inventory` |
| type | string | 是 | Temu 接口名（以 Partner Compliance 文档为准） |
| params | object | 否 | 业务参数，见各接口文档 |

### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| body | string | Temu 原始 JSON 字符串；脚本解析为 `temuBody` |
| code | integer | 网关错误码：`1002` 参数/Token，`1003` 转发失败 |

解析顺序：**网关 `code`** → `JSON.parse(body)` → `success` / `errorCode` / `errorMsg` / `result`。

### 脚本调用

```bash
export LINKFOXAGENT_API_KEY="<key>"
python scripts/temu_global_proxy.py '{"accessToken":"TOKEN","site":"global","type":"<TEMU_API_TYPE>","params":{}}'
```

业务字段放在 `params`（或各 `global_compliance_*.py` 脚本约定的 `request` 结构，接入后以接口文档为准）。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-global-catalog.md](./partner-global-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)。

---

## 典型合规流程

（待按 Partner Global Compliance 菜单接入后补充。）

商品详情、类目属性等辅助查询可用 **`linkfox-temu-manage-product-global`** 对应接口。

---

## 网关错误码

| code | 说明 | 处理 |
|------|------|------|
| 1002 | 参数或 LinkFox Token 无效 | 修正参数与 `LINKFOXAGENT_API_KEY` |
| 1003 | 转发失败 | 检查 Temu token、白名单、网络 |
| 402 | HTTP 402 | 按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: **`linkfox-temu-compliance-global`**
