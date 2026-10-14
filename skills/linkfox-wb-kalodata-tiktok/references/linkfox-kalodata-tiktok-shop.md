# linkfox-kalodata-tiktok-shop

店铺榜单与店铺详情用于 TikTok Shop 店铺发现、竞品比较和渠道结构核验。rank 负责发现店铺；detail 只接受已知 `shopId`，不按店铺名搜索。

## MCP 调用规范

- MCP Server：`LinkFox`
- MCP URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- MCP 工具：`proxy_call`
- 精确 `toolName`：榜单为 `kalodata/shop/rank`，详情为 `kalodata/shop/detail`
- `arguments` 直接传原业务请求体，不增加 `headers`、`Authorization`、token 或其他认证字段；WorkBuddy 自动完成授权。
- 每次调用都可能产生积分消耗。默认不自动重试、不自动翻页、不因空结果改参数重复调用。
## 请求参数

### `POST /kalodata/shop/rank`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 否 | 地区/市场，如 `US`，最大长度 1000 |
| dateRange | string | 否 | 如 `last7Day`、`last30Day`，最大长度 1000 |
| pageNumber | integer | 否 | 1–5 |
| pageSize | integer | 否 | 5–100 |
| language | string | 否 | 如 `zh-CN`、`en-US`，最大长度 1000 |
| currency | string | 否 | 如 `USD`，最大长度 1000 |
| sortField | object | 否 | 排序条件；`{}` 走默认排序 |

默认按 `revenue` GMV 降序，每条 rank 记录有 `rank`；无关键词搜索。

### `POST /kalodata/shop/detail`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 是 | 来自 rank `shop_id` 的店铺 ID，保留字符串精度 |
| region | string | 否 | 如 `US` |
| dateRange | string | 否 | 如 `last7Day`、`last30Day` |
| language | string | 否 | 如 `zh-CN`、`en-US` |
| currency | string | 否 | 如 `USD` |

详情无分页，成功时 `data` 通常为 1 个元素。

## 响应结构

### 共有顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 店铺榜单列表（rank）或 1 元素详情数组（detail） |
| costToken | integer | 本次调用扣费 token，固定 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

> ⚠️ `outputSchema` 可能声明 `total` 字段，但**真实响应不包含 `total`**，也没有总页数等分页元数据。需翻页时持续请求下一页，直到某页返回条数少于 `pageSize`。详情响应 `data` 恒为 1 个元素的数组。

> ⚠️ **详情字段名与店铺 RANK 接口不同**：详情用 `self_account_revenue`（RANK 用 `self_promotion_revenue`）、`shoppingmall_revenue`（`shopping` 与 `mall` 之间**无下划线**，RANK 用 `shopping_mall_revenue`）、`seller_type`（RANK 用 `shop_type`）。详情还返回 `creator_number`/`video_number`/`live_number`/`product_number`（RANK 不返回），且不返回 `rank`/`revenue_growth_rate`/`on_sell_product_count`。抽取数据时务必使用对应接口的确切字段名。

### 店铺榜单字段（`data` 数组中的每个元素）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 榜单数据元素 |
| `data[].rank` | integer | 排名位次（1 为最高） |
| `data[].shop_name` | string | 店铺名称 |
| `data[].shop_id` | string | 店铺唯一 ID（字符串，避免大整数精度丢失） |
| `data[].shop_type` | string | 店铺类型（如 `BRAND`） |
| `data[].revenue` | number | 总销售额 / GMV（按请求的 `currency` 货币） |
| `data[].sales_volumn` | integer | 销量（注意字段拼写为 `volumn`） |
| `data[].on_sell_product_count` | integer | 在售商品数 |
| `data[].unit_price` | number | 件单价（按请求的 `currency` 货币） |
| `data[].revenue_growth_rate` | number | 销售额增长率（%，可正可负） |
| `data[].self_promotion_revenue` | number | 自营/自推广销售额 |
| `data[].affiliate_revenue` | number | 达人分销销售额 |
| `data[].shopping_mall_revenue` | number | 商城销售额 |

> **收入渠道拆分（榜单）**：`revenue` = `self_promotion_revenue` + `affiliate_revenue` + `shopping_mall_revenue`。

### 店铺详情字段（`data` 固定为 1 元素数组）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 详情数据元素 |
| `data[].shop_id` | string | 店铺唯一 ID（字符串，避免大整数精度丢失） |
| `data[].shop_name` | string | 店铺名称 |
| `data[].seller_type` | string | 店铺/卖家类型（如 `BRAND`）——详情用 `seller_type`，非 `shop_type` |
| `data[].region` | string | 地区/市场（如 `US`） |
| `data[].revenue` | number | 总销售额 / GMV（按请求的 `currency` 货币） |
| `data[].sales_volumn` | integer | 销量（注意字段拼写为 `volumn`） |
| `data[].product_number` | integer | 在售商品数 |
| `data[].unit_price` | number | 件单价（按请求的 `currency` 货币） |
| `data[].self_account_revenue` | number | 自营/自播自推销售额——详情用 `self_account_revenue`，非 `self_promotion_revenue` |
| `data[].affiliate_revenue` | number | 达人分销销售额 |
| `data[].shoppingmall_revenue` | number | 商城销售额（注意：`shopping` 与 `mall` 之间**无下划线**） |
| `data[].creator_number` | integer | 达人合作数 |
| `data[].video_number` | integer | 关联视频数 |
| `data[].live_number` | integer | 关联直播数 |

> **收入渠道拆分（详情）**：`revenue` ≈ `self_account_revenue` + `affiliate_revenue` + `shoppingmall_revenue`。各分项可能独立四舍五入（如 `shoppingmall_revenue` 在详情接口返回 `10431.0`，而榜单接口为 `10431.39`），故三者之和可能与 `revenue` 存在微小差异，不要当作精确恒等式。

## MCP 调用示例

榜单：

```json
{
  "toolName": "kalodata/shop/rank",
  "arguments": {"region":"US","dateRange":"last7Day","currency":"USD","pageSize":10,"pageNumber":1,"sortField":{}}
}
```

详情：

```json
{
  "toolName": "kalodata/shop/detail",
  "arguments": {"shopId":"7495514739648989419","region":"US","dateRange":"last7Day","currency":"USD"}
}
```

## 特殊规则与错误

- rank 是市场/时间榜单，不是关键词搜索；无 `total`，按 `data.length` 翻页至不足 `pageSize` 或第 5 页。
- `errcode=400` 常表示 detail 缺 `shopId`，按 errmsg 补齐；501 可能是页码越界或 Kalodata HTTP 554 上游错误；先按 `errmsg` 说明原因，只有用户明确同意时才可同参重试，禁止自动重试。
- 401/402 读取 `references/onboarding.md`，并先区分 MCP 层与下游业务层；其他非 200 按 `errmsg` 处理。不支持的 sortField 回退默认排序，不绕过。
- 展示时严格区分 rank 的 `shop_type`/`self_promotion_revenue`/`shopping_mall_revenue` 与 detail 的 `seller_type`/`self_account_revenue`/`shoppingmall_revenue`；金额标注币种，`sales_volumn` 不改成 volume。
-

## Feedback API

用户反馈时可调用独立 `POST https://skill-api.linkfox.com/api/v1/public/feedback`：

```json
{"skillName":"linkfox-kalodata-tiktok-shop","sentiment":"POSITIVE","category":"OTHER","content":"Results were accurate, user was satisfied."}
```

`sentiment` 为 `POSITIVE`/`NEUTRAL`/`NEGATIVE` 之一，`category` 为 `BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER` 之一。

