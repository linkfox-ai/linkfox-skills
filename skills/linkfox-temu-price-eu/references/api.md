# linkfox-temu-price-eu — API 参考

Temu **欧洲站商品价格管理**（Partner EU **Price** 菜单下价格/供货价相关接口），经本 skill `temu_eu_proxy`（`POST /temu/proxy`） 转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。授权见 `references/access-token.md`。

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 价格 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_eu_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token` |
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
| tokenPurpose | string | 否 | 建议 `product-inventory` |
| type | string | 是 | Temu 接口名，如 `bg.local.goods.priceorder.query` |
| params | object | 否 | 业务参数；多数 Manage 接口业务块在 **`params.request`** |

### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| body | string | Temu 原始 JSON 字符串；脚本解析为 `temuBody` |
| code | integer | 网关错误码：`1002` 参数/Token，`1003` 转发失败 |

解析顺序：**网关 `code`** → `JSON.parse(body)` → `success` / `errorCode` / `errorMsg` / `result`。

### 脚本调用

```bash
export LINKFOXAGENT_API_KEY="<key>"
python scripts/eu_price_priceorder_query.py '{"accessToken":"TOKEN","request":{"page":1,"size":20,"priceOrderType":1}}'
```

业务字段可放在顶层或嵌套 `params`；含 `request` 时通常整体作为 `params` 转发。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-eu-catalog.md](./partner-eu-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)。

---

## 典型价格管理流程

```text
1. linkfox-temu-manage-product-eu → list/detail / spec.info.get           → 拿 goodsId、catId、specIdList
2. bg.local.goods.priceorder.query（本 skill，白名单）                     → 分页查定价单/报价列表
3. temu.local.goods.recommendedprice.query（本 skill）                     → 按 goodsIdList 查平台推荐供货价
4. temu.local.goods.baseprice.recommend（本 skill）                        → 发品/改价前推荐基础价估算
5. bg.local.goods.priceorder.change.sku.price（本 skill，白名单）          → 批量改 SKU 基础价
6. bg.local.goods.priceorder.query                                         → 改价后核对 priceAuditList / supplierPrice
```

发品侧半托管供货价列表（`temu.goods.price.list.get`，入参 `productSkuIds`）见 **`linkfox-temu-add-product-us`**，与本 skill 的 `bg.local.*` 本地仓价格接口**不要混用**。

---

## 网关错误码

| code | 说明 | 处理 |
|------|------|------|
| 1002 | 参数或 LinkFox Token 无效 | 修正参数与 `LINKFOXAGENT_API_KEY` |
| 1003 | 转发失败 | 检查 Temu token、白名单、网络 |

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: **`linkfox-temu-price-eu`**
