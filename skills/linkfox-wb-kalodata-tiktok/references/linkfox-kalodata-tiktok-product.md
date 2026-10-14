# linkfox-kalodata-tiktok-product

商品榜单与商品详情用于 TikTok Shop 选品和单品核验。rank 负责按市场/时间窗口发现商品；detail 只接受一个已知 `productId`，不能按标题搜索。

## MCP 调用规范

- MCP Server：`LinkFox`
- MCP URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- MCP 工具：`proxy_call`
- 精确 `toolName`：榜单为 `kalodata/product/rank`，详情为 `kalodata/product/detail`
- `arguments` 直接传原业务请求体，不增加 `headers`、`Authorization`、token 或其他认证字段；WorkBuddy 自动完成授权。
- 每次调用都可能产生积分消耗。默认不自动重试、不自动翻页、不因空结果改参数重复调用。
## 请求参数

### `POST /kalodata/product/rank`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 否 | TikTok Shop 市场，如 `US`；未指定时通常按服务端缺省（通常 US） |
| dateRange | string | 否 | 相对时间，如 `last7Day`、`last30Day` |
| currency | string | 否 | 货币，如 `USD` |
| language | string | 否 | 返回语言，如 `zh-CN`、`en-US` |
| sortField | object | 否 | 排序规格，省略使用默认排行；不支持的字段按 errmsg 处理 |
| pageNumber | integer | 否 | 1–5 |
| pageSize | integer | 否 | 5–100 |

无关键词参数；默认排序和可接受的 `sortField` 以网关为准。

### `POST /kalodata/product/detail`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| productId | string | 是 | 商品 ID，来自 rank 的 `product_id`；必须保留字符串精度 |
| region | string | 否 | 市场，如 `US` |
| dateRange | string | 否 | 如 `last7Day`、`last30Day` |
| language | string | 否 | 如 `zh-CN`、`en-US` |
| currency | string | 否 | 如 `USD` |

## 响应结构

### 共有顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 榜单或详情数据 |
| costToken | integer | 本次调用扣费 token，通常为 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

> 顶层字段为 `errcode` / `data` / `costToken` / `errmsg`。**真实响应不返回 `total`**（也没有总页数等分页元数据），商品列表在 `data` 数组中。详情的 `data` 固定为 1 元素数组。

### 商品榜单字段（`data` 数组中的每个元素）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 榜单数据元素 |
| `data[].product_id` | string | 商品 ID（字符串格式，避免大整数精度丢失）；作为 `productId` 查询详情 |
| `data[].product_name` | string | 商品标题 |
| `data[].unit_price` | number | 单价（货币随 `region`，如 `US` 为 USD） |
| `data[].sales_volumn` | integer | 销量（件数）。注意接口字段名为 `sales_volumn`（原样拼写，非 `volume`），用 `jq`/`ConvertFrom-Json` 取值时须用此名 |
| `data[].revenue` | number | 总销售额（GMV），= `video_revenue` + `live_revenue` + `showcase_revenue` |
| `data[].video_revenue` | number | 视频渠道销售额 |
| `data[].live_revenue` | number | 直播渠道销售额 |
| `data[].showcase_revenue` | number | 橱窗/展示渠道销售额 |
| `data[].revenue_growth_rate` | number | 销售额增长率（百分比，如 `27.94` 表示 27.94%） |
| `data[].commission_rate` | number | 佣金率（百分比，如 `25.0` 表示 25%；**非基点**） |
| `data[].launch_date` | string | 上架日期（`YYYY-MM-DD`） |

> 真实响应不包含 `total`，也没有总页数等分页元数据。需要翻页时持续请求下一页，直到某页返回条数少于 `pageSize` 或达到第 5 页。

### 商品详情字段（`data` 固定为 1 元素数组）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 详情数据元素 |
| `data[].product_id` | string | 商品唯一 ID（字符串，避免大整数精度丢失） |
| `data[].product_name` | string | 商品名称 |
| `data[].product_region` | string | 商品所在地区/市场（如 `us`） |
| `data[].product_shop_id` | string | 所属店铺 ID |
| `data[].pri_cate_id` | string | 一级类目 ID |
| `data[].sec_cate_id` | string | 二级类目 ID |
| `data[].ter_cate_id` | string | 三级类目 ID |
| `data[].unit_price` | number | 件单价（按请求的 `currency` 货币） |
| `data[].min_price` | number | 最低价（按请求的 `currency` 货币） |
| `data[].max_price` | number | 最高价（按请求的 `currency` 货币） |
| `data[].revenue` | number | 总销售额 / GMV（按请求的 `currency` 货币） |
| `data[].sales_volumn` | integer | 销量（注意字段拼写为 `volumn`） |
| `data[].commission_rate` | number | 佣金率，**直接百分比**（25.0 表示 25%） |
| `data[].product_review_count` | integer | 商品评论数 |
| `data[].launch_date` | string | 上架日期（`YYYY-MM-DD`） |
| `data[].delivery_type` | string | 配送方式（如 `local`） |
| `data[].video_number` | integer | 关联视频数 |
| `data[].video_revenue` | number | 视频带来的销售额（按请求的 `currency` 货币） |
| `data[].live_number` | integer | 关联直播数 |
| `data[].live_revenue` | number | 直播带来的销售额（按请求的 `currency` 货币） |
| `data[].shopping_mall_revenue` | number | 商城销售额（按请求的 `currency` 货币） |
| `data[].creator_number` | integer | 关联达人数 |

> **收入渠道拆分**：详情 `revenue` = `video_revenue` + `live_revenue` + `shopping_mall_revenue`。
> **字段拼写注意**：`sales_volumn` 拼写为 `volumn`（非 `volume`），用 `jq` / `ConvertFrom-Json` 抽取时需使用准确字段名；`commission_rate` 为直接百分比（25.0 = 25%）。

## MCP 调用示例

榜单：

```json
{
  "toolName": "kalodata/product/rank",
  "arguments": {"region":"US","dateRange":"last7Day","currency":"USD","pageSize":20,"pageNumber":1}
}
```

详情：

```json
{
  "toolName": "kalodata/product/detail",
  "arguments": {"productId":"1729508370969629931","region":"US","dateRange":"last7Day","currency":"USD"}
}
```

## 特殊规则与错误

- rank 是榜单浏览，不是关键词搜索；没有 `total` 时用 `data.length` 判断当前页，最多翻到第 5 页。
- 合法但空结果可能 `errcode=200` 且缺少 `data`，仍可能扣费。`productId` 缺失/非法、页码越界按 `errmsg` 修正。
- 501 若 `errmsg` 指向 Kalodata HTTP 522/554 等上游错误，向用户说明后停止；只有用户明确同意时才可用相同参数重试，禁止自动重试或改参数试探。
- 401/402 读取 `references/onboarding.md`，并先区分 MCP 层与下游业务层；其他错误透传 `errmsg`。金额标注币种，销量使用 `sales_volumn`，百分比带 `%`，ID 作为字符串。
-

## Feedback API

用户表达表扬、建议、抱怨或结果错误时，按需调用独立接口 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，不要与数据网关混用：

```json
{"skillName":"linkfox-kalodata-tiktok-product","sentiment":"POSITIVE","category":"OTHER","content":"Results were accurate, user was satisfied."}
```

`sentiment` 只能是 `POSITIVE`/`NEUTRAL`/`NEGATIVE`；`category` 只能是 `BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`；content 说明用户意图、实际结果及问题或肯定点。

