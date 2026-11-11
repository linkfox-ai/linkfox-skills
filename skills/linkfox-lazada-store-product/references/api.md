# Lazada 店铺商品查询接口参考

## 公共规则

### 调用规范

- 基础地址读取 `LINKFOX_TOOL_GATEWAY`，默认 `https://tool-gateway.linkfox.com`。直接调用使用 `POST /lazada/developerProxy`，超时 150 秒。
- 请求头为 `Content-Type: application/json`、`Accept: application/json`、`User-Agent: LinkFox-Skill/2.0`、`Authorization: <LinkFox Key>`。Key 优先取 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID` 和 `APP_NAME`，缺省为空。
- 命名脚本接收一个 JSON 对象，自动填入 `operation`。每次调用均实时请求，`--no-cache` 保留为兼容选项。`--inline` 打印完整脱敏 JSON 并继续保存。

| 网关请求字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `connectionId` | 字符串 | 是 | 原样传入当前用户已授权的店铺连接 ID。后端据此选择店铺和站点。 |
| `operation` | 字符串 | 是 | `listProducts` 或 `getProduct`。 |
| `queryParams` | 对象 | 按操作 | 按各操作的表格传入 Lazada 查询参数。 |

### 响应结构

网关成功响应为 `{"data": <业务数据>, "requestId": <Lazada 请求标识>}`，或由外层 `data` 包裹此对象。CLI 去除外层包裹并移除敏感字段，保存 `{"data": <业务数据>, "requestId": <Lazada 请求标识或 null>, "success": true}`。

## 商品列表

`listProducts` 对应 `GET /products/get`。脚本为 `scripts/list_products.py`，可省略 `queryParams`。需要按 `item_id` 定位单件商品时使用商品详情。 [Lazada 商品 API 总览](https://open.lazada.com/apps/doc/doc?docId=108146&nodeId=10557)

| `queryParams` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `filter` | 字符串 | 否 | 商品状态，默认 `all` |
| `offset` | 0–10000 的整数或数字字符串 | 否 | 结果偏移量，默认 0 |
| `limit` | 1–50 的整数或数字字符串 | 否 | 每页条数，默认 20 |
| `create_after` | 字符串 | 否 | 商品创建时间下界 |
| `create_before` | 字符串 | 否 | 商品创建时间上界 |
| `update_after` | 字符串 | 否 | 商品更新时间下界 |
| `update_before` | 字符串 | 否 | 商品更新时间上界 |
| `options` | 字符串 | 否 | Lazada 商品列表附加选项 |
| `sku_seller_list` | 字符串 | 否 | 非空卖家 SKU 数组的 JSON 文本，例如 `"sku_seller_list":"[\"SKU-01\"]"` |

时间使用带偏移的 ISO 8601 文本，优先采用 `2026-11-01T00:00:00+08:00` 形式。LinkFox 也接受 `+0800` 并原样转发。

### 响应字段

| 保存文件路径 | 类型 | 说明 |
| --- | --- | --- |
| `data.products` | 对象数组 | 本页商品。空数组表示本次查询无匹配商品。 |
| `data.products[].item_id` | 字符串 | 商品 ID，用于在同一店铺查询详情。 |
| `data.total_products` | 数值或数字字符串 | 上游返回的总量，可能缺失。 |

有总量时据此判断是否有下一页。达到偏移量上限时，按用户要求收窄时间范围。

## 商品详情

`getProduct` 对应 `GET /product/item/get`。脚本为 `scripts/get_product.py`。只有卖家 SKU 时，先以 `sku_seller_list` 查询商品列表，再从匹配记录取得商品 ID。 [Lazada GetProductItem](https://open.lazada.com/apps/doc/api?path=%2Fproduct%2Fitem%2Fget)

| `queryParams` 字段 | 类型 | 必填 | 含义 |
| --- | --- | --- | --- |
| `item_id` | 1 至 20 位的正整数文本 | 是 | 该店铺的商品 ID |

### 响应字段

| 保存文件路径 | 类型 | 说明 |
| --- | --- | --- |
| `data` | 对象 | 商品详情。属性和 SKU 字段按实际响应展示，缺失字段保留为未知。 |
| `data.item_id` | 字符串 | 查询商品的 ID。 |

## 商品管理与辅助资料

刊登、更新、价格库存、质检与素材操作使用 [商品管理接口](product-operations.md)。商品列表和详情继续使用本页的原查询入口。

## 错误处理

- HTTP 2xx 且 JSON `errcode` 缺失、为 null、为空字符串或纯空白，或者是 200–299 的整数或数字字符串，才继续检查业务数据。`0`、`false` 与 XML `ToolErrorResponse` 属于失败。失败时保存可用诊断并以非零状态退出。
- 输出可用的错误码、`requestId`、`traceId` 以及服务端提供的 `upstreamCode`、`upstreamRequestId`。原始错误正文和凭据不进入输出。
- `error=REAUTHORIZATION_REQUIRED` 时通过授权 Skill 核对该店铺连接。单凭 401 无法区分店铺授权和 LinkFox Key，应结合诊断定位。已确认 LinkFox Key 故障时按 [认证和算力指引](onboarding.md) 处理。
- `error=LAZADA_PROXY_FORBIDDEN` 时将代理出口白名单问题交给接入维护方核查。其他 403 时核对店铺或应用权限。出现 402 时先按实际调用的接口核对网关账户或计费诊断。
- `upstreamCode=SellerNotVerified` 表示 Lazada 尚未验证该卖家。请用户在对应站点的卖家中心确认验证状态，完成后再查询。
- 超时或 5xx 保留请求标识。脚本不会自动重发。

## Feedback

用户明确同意发送后，仅提交已脱敏的反馈摘要。反馈服务使用独立地址。

- `POST https://skill-api.linkfox.com/api/v1/public/feedback`
- 请求内容类型为 `application/json`。

```json
{
  "skillName": "linkfox-lazada-store-product",
  "sentiment": "<POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<经用户同意发送的脱敏摘要>"
}
```

摘要中仅保留反馈所需信息。排除密钥、令牌、店铺身份、商品原始数据及完整响应。
