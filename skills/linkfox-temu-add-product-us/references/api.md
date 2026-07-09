# linkfox-temu-add-product-us — API 参考

Temu **美国站商品发布**（Partner US **Product > Add Products > Recommended V2 Interfaces**），经本 skill `temu_us_proxy`（`POST /temu/proxy`） 转发。Temu 的 `type` 写在 Body，**不是** URL 路径。

> 网关与鉴权：本 skill `scripts/`（`LINKFOXAGENT_API_KEY`、`accessToken` / `storeKey`）。授权步骤见同仓库 `references/access-token.md`。

---

## 调用规范

| 项 | 说明 |
|----|------|
| 网关根地址 | `${LINKFOX_TOOL_GATEWAY}`（可用 `LINKFOX_TOOL_GATEWAY` / `TEMU_API_BASE_URL` / `STORE_API_BASE_URL` 覆盖） |
| 商品 OpenAPI | `POST /temu/proxy` |
| 加签文件下载 | `POST /temu/fileDownload`（`temu_us_file_download.py`） |
| LinkFox 鉴权 | Header **`Authorization`** 与 **`Token`**（同值）；或环境变量 `LINKFOX_AGENT_API_KEY` / `LINKFOXAGENT_API_KEY`；或 JSON `token` / `linkfoxToken` |
| Temu 鉴权 | Body `accessToken`，或 `storeKey` + `site` + `managementType` + `tokenPurpose` |
| 默认 | `site=us`，`managementType=semi-managed`，`tokenPurpose=product-inventory` |
| 上游 OpenAPI（US） | `https://openapi-b-us.temu.com/openapi/router`（由网关按 `site` 解析，调用方勿直连） |

### 网关请求 Body（`/temu/proxy`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | `us`（本 skill 默认）；半托跨境发品偶用 `cn` / `partner` |
| managementType | string | 是 | `semi-managed` |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192 |
| storeKey | string | 与 accessToken 二选一 | 本地 `~/.linkfox/temu-access-tokens.json` 中的店铺键 |
| tokenPurpose | string | 否 | 建议 `product-inventory`（酷鸟卖家助手） |
| type | string | 是 | Temu 接口名，如 `temu.local.goods.v2.add` |
| params | object | 否 | 业务参数，结构见下文各接口文档 |

### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| body | string | Temu 原始 JSON **字符串**；脚本会尽量解析为 `temuBody` |
| code | integer | 网关错误码（非 Temu 业务码），如 `1002` 参数/用户 Token 无效，`1003` 转发失败 |

解析顺序：**先看网关 `code`/`message`** → 再 `JSON.parse(body)` → 读 Temu 层 `success`、`errorCode`、`errorMsg`、`result`。

### Temu 业务响应信封（`body` 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| errorCode | integer | 业务错误码；`1000000` 或 `0` 常表示成功（以实网为准） |
| errorMsg | string | 错误说明，成功时多为空 |
| requestId | string | 请求追踪 ID |
| result | object | 业务数据，结构因 `type` 而异 |

### curl 示例（经网关）

```bash
curl -X POST https://tool-gateway.linkfox.com/temu/proxy \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Token: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "site": "us",
    "managementType": "semi-managed",
    "accessToken": "TEMU_PRODUCT_TOKEN",
    "type": "temu.local.product.attributes.get",
    "params": { "catId": 12345 }
  }'
```

### 脚本调用

```bash
export LINKFOXAGENT_API_KEY="<key>"
python scripts/us_goods_attrs.py '{"accessToken":"TOKEN","params":{"catId":12345}}'
```

业务字段可放在顶层或嵌套 `params`；脚本会通过 `extract_business_params` 提取后写入网关 Body 的 `params`。

---

## 接口一览

共 **19** 个商品接口（4 V2 + 15 标准），完整 `sub_menu_code` 对照见 [partner-us-catalog.md](./partner-us-catalog.md)。

| 分组 | 文档 |
|------|------|
| 查询（list / detail） | [product-query-apis.md](./product-query-apis.md) |
| 编辑（update / property / sensitive / migrate） | [product-edit-apis.md](./product-edit-apis.md) |
| 发品 V2 + 图片 + legacy add | [product-publish-apis.md](./product-publish-apis.md) |
| 类目 / 属性 / 规格 / 品牌 / 映射 | [category-spec-apis.md](./category-spec-apis.md) |
| 库存 / 供货价 | [stock-price-apis.md](./stock-price-apis.md) |

---

## 推荐 V2 发品流程

```text
1. temu.local.product.attributes.get   → catId 拉属性模板
2. temu.local.product.variation.get    → catId 拉规格
3. temu.local.goods.image.v2.upload    → 上传图片
4. temu.local.goods.v2.add             → 提交商品
```

---

## 网关错误码

| code | 说明 | 处理 |
|------|------|------|
| 1002 | 参数校验失败或 LinkFox 用户 Token 无效 | 修正参数；检查 `LINKFOXAGENT_API_KEY`；勿盲目重试 |
| 1003 | 转发/上游失败 | 检查 Temu `accessToken`、白名单、网络；可退避重试 |

Temu 业务层 `errorCode` / `errorMsg` 在 `body` 内，需结合 `success` 判断。

---

## Feedback API

与工具网关分离，勿混用 Base URL。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-temu-add-product-us",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

- `skillName`: **`linkfox-temu-add-product-us`**
- `sentiment`: `POSITIVE` | `NEUTRAL` | `NEGATIVE`
- `category`: `BUG` | `COMPLAINT` | `SUGGESTION` | `OTHER`
