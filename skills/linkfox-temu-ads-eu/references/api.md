# linkfox-temu-ads-eu — API 参考

Temu **欧洲站电商广告（Ads）**，经本 skill `temu_eu_proxy`（`POST /temu/proxy`） 转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。授权见 `references/access-token.md`。

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `LINKFOX_TOOL_GATEWAY` / `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 广告 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_eu_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理） |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=eu`，`managementType=semi-managed`，`tokenPurpose=product-inventory` |
| 上游 OpenAPI（US） | `https://openapi-b-eu.temu.com/openapi/router`（网关按 `site` 解析） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `eu`（本 skill 默认） |
| managementType | string | 是 | `semi-managed` |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌 |
| storeKey | string | 与 accessToken 二选一 | `~/.linkfox/temu-access-tokens.json` 中的键 |
| tokenPurpose | string | 否 | 建议 **`product-inventory`**（以各 Ads 接口 Partner 文档为准） |
| type | string | 是 | Temu 接口名，如 Partner **Ads** 菜单下的 `bg.*` / `temu.*` |
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
python scripts/temu_eu_proxy.py '{"accessToken":"TOKEN","tokenPurpose":"product-inventory","type":"<API_TYPE>","params":{"request":{}}}'
```

业务字段可放在顶层或嵌套 `params`；含 `request` 时通常整体作为 `params` 转发。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-eu-catalog.md](./partner-eu-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)（随接入递增）。

| type | 说明 | 文档 |
|------|------|------|
| `temu.searchrec.ad.roas.pred` | 广告 ROAS 预测 | [apis/temu-searchrec-ad-roas-pred.md](./apis/temu-searchrec-ad-roas-pred.md) |
| `temu.searchrec.ad.reports.mall.query` | 店铺广告报表查询 | [apis/temu-searchrec-ad-reports-mall-query.md](./apis/temu-searchrec-ad-reports-mall-query.md) |
| `temu.searchrec.ad.create` | 创建广告 | [apis/temu-searchrec-ad-create.md](./apis/temu-searchrec-ad-create.md) |
| `temu.searchrec.ad.detail.query` | 广告详情查询 | [apis/temu-searchrec-ad-detail-query.md](./apis/temu-searchrec-ad-detail-query.md) |
| `temu.searchrec.ad.log.query` | 广告操作日志查询 | [apis/temu-searchrec-ad-log-query.md](./apis/temu-searchrec-ad-log-query.md) |
| `temu.searchrec.ad.goods.create.query` | 广告可创建商品查询 | [apis/temu-searchrec-ad-goods-create-query.md](./apis/temu-searchrec-ad-goods-create-query.md) |
| `temu.searchrec.ad.modify` | 修改广告 | [apis/temu-searchrec-ad-modify.md](./apis/temu-searchrec-ad-modify.md) |

---

## 典型广告流程

```text
1. temu.searchrec.ad.goods.create.query     → 商品是否可创建广告
2. temu.searchrec.ad.roas.pred              → ROAS 预测
3. temu.searchrec.ad.create                 → 创建广告
4. temu.searchrec.ad.detail.query           → 广告详情
5. temu.searchrec.ad.modify                 → 暂停/改预算/改 ROAS/删除
6. temu.searchrec.ad.reports.mall.query     → 店铺报表
7. temu.searchrec.ad.log.query              → 操作日志
```

---

## 与其他 Temu EU skill 的区分

| 能力 | skill |
|------|--------|
| **广告 Ads**（本 skill） | **`linkfox-temu-ads-eu`** |
| 促销/营销活动 | `linkfox-temu-promotion-eu` |
| 商品管理 | `linkfox-temu-manage-product-eu` |
| 价格/供货价 | `linkfox-temu-price-eu` |
| 订单 | `linkfox-temu-order-eu` |

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
- `skillName`: **`linkfox-temu-ads-eu`**
