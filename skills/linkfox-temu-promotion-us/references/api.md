# linkfox-temu-promotion-us — API 参考

Temu **美国站电商促销**（Partner US **Promotion** / 促销活动等），经本 skill `temu_us_proxy`（`POST /temu/proxy`） 转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。授权见 `references/access-token.md`。

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 促销 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_us_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token` |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=us`，`managementType=semi-managed`，`tokenPurpose=product-inventory` |
| 上游 OpenAPI（US） | `https://openapi-b-us.temu.com/openapi/router`（网关按 `site` 解析） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `us`（本 skill 默认） |
| managementType | string | 是 | `semi-managed` |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌 |
| storeKey | string | 与 accessToken 二选一 | `~/.linkfox/temu-access-tokens.json` 中的键 |
| tokenPurpose | string | 否 | 建议 **`product-inventory`** |
| type | string | 是 | Temu 接口名，如 Partner Promotion 菜单下的 `bg.*` / `temu.*` |
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
python scripts/temu_us_proxy.py '{"accessToken":"TOKEN","tokenPurpose":"product-inventory","type":"<API_TYPE>","params":{"request":{}}}'
```

业务字段可放在顶层或嵌套 `params`；含 `request` 时通常整体作为 `params` 转发。

---

## 接口一览

完整 `sub_menu_code` 与 Partner 文档 URL 见 [partner-us-catalog.md](./partner-us-catalog.md)。

**每个接口单独一份文档**：[apis/README.md](./apis/README.md)（随接入递增）。

| type | 说明 | 文档 |
|------|------|------|
| `bg.promotion.activity.query` | 促销活动查询 | [apis/bg-promotion-activity-query.md](./apis/bg-promotion-activity-query.md) |
| `bg.promotion.activity.candidate.goods.query` | 活动候选商品查询 | [apis/bg-promotion-activity-candidate-goods-query.md](./apis/bg-promotion-activity-candidate-goods-query.md) |
| `bg.promotion.activity.goods.query` | 活动已报名商品查询 | [apis/bg-promotion-activity-goods-query.md](./apis/bg-promotion-activity-goods-query.md) |
| `bg.promotion.activity.goods.enroll` | 活动商品报名 | [apis/bg-promotion-activity-goods-enroll.md](./apis/bg-promotion-activity-goods-enroll.md) |
| `bg.promotion.activity.goods.operation.query` | 活动商品操作结果查询 | [apis/bg-promotion-activity-goods-operation-query.md](./apis/bg-promotion-activity-goods-operation-query.md) |
| `bg.promotion.activity.goods.update` | 活动商品更新 | [apis/bg-promotion-activity-goods-update.md](./apis/bg-promotion-activity-goods-update.md) |

---

## 典型促销流程

```text
1. bg.promotion.activity.query                      → 查可参加/已参加的活动
2. bg.promotion.activity.candidate.goods.query      → 查候选商品与推荐活动价
3. bg.promotion.activity.goods.enroll               → 报名（得 draftId）
4. bg.promotion.activity.goods.operation.query      → 轮询报名/更新结果
5. bg.promotion.activity.goods.query                → 查已报名商品与活动价
6. bg.promotion.activity.goods.update               → 改价/改量/下架/加 SKU
```

---

## 与其他 Temu US skill 的区分

| 能力 | skill |
|------|--------|
| **促销**（本 skill） | **`linkfox-temu-promotion-us`** |
| 商品管理（列表/编辑/库存/上下架） | `linkfox-temu-manage-product-us` |
| 价格/供货价 | `linkfox-temu-price-us` |
| 发品 | `linkfox-temu-add-product-us` |
| 订单 | `linkfox-temu-order-us` |

---

## 网关错误码

| code | 说明 | 处理 |
|------|------|------|
| 1002 | 参数或 LinkFox Token 无效 | 修正参数与 `LINKFOXAGENT_API_KEY` |
| 1003 | 转发失败 | 检查 Temu token、`tokenPurpose`、白名单、网络 |

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `skillName`: **`linkfox-temu-promotion-us`**
