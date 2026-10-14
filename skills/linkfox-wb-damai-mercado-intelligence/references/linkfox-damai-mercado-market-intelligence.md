# 大麦数据美客多市场洞察与选品 API 参考

## 子能力概览

子能力标识：`linkfox-damai-mercado-market-intelligence`。

该能力通过 LinkFox 网关查询 Mercado Libre 市场数据，覆盖类目搜索、行业概览、商品快照筛选、商品销量趋势、图片相似商品、评论和配额状态 7 个 operation。它只调用统一网关，不直接调用上游数据提供方。

### 适用范围

- `search_categories`：按市场本地语言找候选类目，返回 ID、当地化路径、层级、终端标记与市场指标。
- `industry_overview`：按类目 ID读取行业订单、价格、GMV和月度趋势摘要。
- `search_product_snapshots`：按关键词、类目、商品、商品链接或店铺条件筛选商品并返回快照、销量、卖家、履约、库存和属性聚合。
- `product_sales_trend`：按商品 ID读取月度和 ISO 周订单序列及覆盖信息。
- `image_search_products`：按公开图片 URL或 Base64 找相似美客多商品。
- `review_search`：按商品 ID分页读取评论。
- `get_my_quota_status`：免费读取套餐、额度和积分计费状态，用于连接/成本诊断。

不支持店铺授权、Listing 发布、库存更新、订单履约、退款、广告或其他 Mercado Libre 官方卖家 API；不基于缺失数据推断利润、需求、市场份额或竞争结论。

## MCP 调用

- **MCP server**：`LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`）。
- **唯一工具**：`proxy_call`。
- **toolName**：`damai/call`，即共享 endpoint `/damai/call` 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接放原 `/damai/call` 请求体，即下方包含 operation `toolName` 和 operation `arguments` 的对象；不得丢掉这一层业务路由，也不得额外添加 `body`、`data`、`params` 或 `headers`。
- **授权**：WorkBuddy 自动注入授权。禁止添加 Authorization、API Key、上游 `X-API-Key`、JWT、手机号或认证 token，也不要向用户索取。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理错误；代理成功后读取 text/structured content，text 是 JSON 字符串时只解析一次，再检查下游 `code`、`errcode`、`error`、`errmsg` 或 `msg`。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退。同一任务内相同 `toolName + arguments` 只调用一次；收费 operation 失败、空结果、限流或超时不得自动重试、翻页或改参数。

完整 MCP 参数结构如下。外层 `toolName` 是 endpoint，内层 `arguments.toolName` 才是七个 operation 之一：

```json
{
  "toolName": "damai/call",
  "arguments": {
    "toolName": "search_categories",
    "arguments": {
      "market_code": "MLM",
      "query": "celulares",
      "limit": 10
    }
  }
}
```

## MCP 与下游请求结构

```json
{
  "toolName": "damai/call",
  "arguments": {
    "toolName": "search_categories",
    "arguments": {
      "market_code": "MLM",
      "query": "celulares",
      "limit": 10
    }
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `toolName` | string | 是 | MCP 外层固定为 `damai/call` |
| `arguments.toolName` | string | 是 | 下表 7 个 operation 之一，大小写必须完全一致 |
| `arguments.arguments` | object | 是 | operation 参数对象；无参数 operation 也传 `{}` |

支持市场：`MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚。`market_code` 缺省时由上游按 `MLM` 处理。类目和商品关键词使用所选市场本地语言。

计费规则：`search_categories`、`get_my_quota_status` 免费；其余 5 个 operation 每次成功调用收取 12 LinkFox 积分（￥0.12），同时在有有效上游套餐时扣减 1 次套餐额度，账号处于积分计费模式时扣减 1 个上游积分。套餐到期或额度耗尽后不会自动切换为积分计费，实际模式以 `get_my_quota_status` 的 `credit_policy` / `points_mode` 等字段为准。同一账号的多个托管上游凭证共用套餐额度。

## Operation 参数

### `search_categories`

免费搜索候选类目。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `query` | string | 否 | - | 当地语言类目关键词 |
| `limit` | integer | 否 | 默认及最大 100 | 返回数量 |

### `industry_overview`

收费 operation。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `category_id` | string | 是 | - | 类目 ID；建议先用 `search_categories` 解析 |
| `market_code` | string | 否 | `MLM` | 市场编码 |

### `search_product_snapshots`

收费 operation。`keyword`、`category_id`、`sku_id`、`product_url`、`shop_id`、`shop_query` 至少提供一个。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `keyword` | string | 条件必填 | - | 当地语言商品关键词 |
| `category_id` | string | 条件必填 | - | 类目 ID |
| `sku_id` | string | 条件必填 | - | 商品 ID，精确查询 |
| `product_url` | string | 条件必填 | - | HTTP(S) 商品链接 |
| `shop_id` | string | 条件必填 | - | 店铺或卖家 ID |
| `shop_query` | string | 条件必填 | - | 店铺或卖家名称关键词 |
| `price_min`, `price_max` | number | 否 | - | 价格区间 |
| `sales_30d_min`, `sales_30d_max` | integer | 否 | - | 近 30 天销量区间 |
| `historical_total_sales_min`, `historical_total_sales_max` | integer | 否 | - | 历史累计销量区间 |
| `rating_min`, `rating_max` | number | 否 | - | 评分区间 |
| `review_count_min`, `review_count_max` | integer | 否 | - | 评论数区间 |
| `listing_date_min`, `listing_date_max` | string | 否 | `YYYYMMDD` 或 `YYYY-MM-DD` | 上架日期区间 |
| `stock_type` | string | 否 | - | 库存或履约类型；不传表示不限 |
| `shop_type` | string | 否 | `cross_border`/`local` | 卖家类型 |
| `product_status` | string/integer | 否 | - | 商品状态，如 `active`、`paused` 或上游原始整数状态值 |
| `sort_by` | string | 否 | `sales_30d` | `sales_30d`、`historical_total_sales`、`price`、`listing_date`、`rating`、`review_count`、`title` |
| `sort_order` | string | 否 | `desc` | `asc` 或 `desc` |
| `page` | integer | 否 | 1 起 | 页码 |
| `limit` | integer | 否 | 默认及最大 100 | 每页数量 |

### `product_sales_trend`

收费 operation。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `sku_id` | string | 是 | - | 商品 ID |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `days` | integer | 否 | 默认 730，1–731 | 查询天数 |

### `image_search_products`

收费 operation。`image_url`、`image_base64` 至少提供一个。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `image_url` | string | 条件必填 | - | 可公开访问的 HTTP(S) 图片 URL |
| `image_base64` | string | 条件必填 | - | 图片 Base64 字符串 |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `page` | integer | 否 | 1 | 页码 |
| `limit` | integer | 否 | 50 | 返回数量；最大值由上游服务配置决定 |
| `token` | string | 否 | 服务端配置 | 图片搜索令牌，通常无需传入；传入时仅覆盖本次请求 |

WorkBuddy 调用不得传 `token`；使用后端托管配置。该行仅保留原下游参数契约，不代表需要用户提供凭证。

本地图片采用两阶段流程：先调用 `proxy_call`，外层 `toolName` 精确使用 `oss/file/presignedPut`，`arguments` 传 `contentType` 与 `fileExtension`；再运行 `python scripts/upload_image.py <本地图片路径>`，通过标准输入传入返回的预签名 URL。辅助脚本只向该预签名 OSS URL 执行 PUT，上传成功后输出去掉查询参数的公开 URL，再将该 URL 传入 `image_url`。不得把预签名查询参数、完整 Base64 或任何凭证写入面向用户的结果。

#### 本地图片预签名 MCP 调用

- **MCP server**：`LinkFox`。
- **唯一工具**：`proxy_call`。
- **toolName**：`oss/file/presignedPut`，即原 endpoint `/oss/file/presignedPut` 去掉前导 `/` 后的精确值。
- **arguments**：`contentType` 和 `fileExtension` 直接组成对象，不添加包装或认证字段。
- **返回与错误**：按 MCP/代理层、下游 `errcode`/`errmsg` 分层处理，从成功响应读取 `url`；失败时不回退 HTTP，也不自动重新申请。

预签名调用示例：

```json
{
  "toolName": "oss/file/presignedPut",
  "arguments": {
    "contentType": "image/png",
    "fileExtension": "png"
  }
}
```

### `review_search`

收费 operation。

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `sku_id` | string | 是 | - | 商品 ID |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `page` | integer | 否 | 1 | 页码 |
| `limit` | integer | 否 | 默认 20，最大 100 | 每页数量 |

### `get_my_quota_status`

无需参数，上游免费。该 operation 只用于连接验证和运维诊断，响应中的账号编码不应向最终用户展示。

## 响应结构

### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| code | string | 成功时为 `"200"` / `"ok"` |
| msg | string | 成功时为 `"200"` / `"ok"` |
| errcode | integer/string | 网关状态与错误信息；生产成功响应通常为 `200` / `ok` |
| errmsg | integer/string | 网关状态与错误信息；生产成功响应通常为 `200` / `ok` |
| type | string | 当前为 `rawMcpToolResult` |
| toolName | string | 实际调用的操作名 |
| providerCharged | boolean | 上游是否按成功调用扣次数 |
| charged | boolean | LinkFox 是否对本次调用计费；两个免费操作为 `false`，五个收费操作成功时为 `true` |
| data | object | 解包后的业务数据；若上游返回数组、标量或空值，后端按响应异常处理 |
| rawResponse | object | MCP `tools/call` 原始 result；仅诊断时读取 |
| contentText | string | MCP text content 原文，可为空 |
| textParsedAsJson | boolean | text content 是否解析为 JSON |
| total | integer | 可推断时返回的记录数 |
| costToken | integer | 计费 token；响应体可能省略，实际计费以响应头 `X-Cost-Token` 为准 |
| costTime | integer | 后端耗时，毫秒 |

### `search_categories` 的 `data`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data.request_overview | 来源未说明 | 类目搜索关键字段 |
| data.record_count | 来源未说明 | 类目搜索关键字段 |
| data.records | array | 类目搜索记录数组；来源未提供记录字段的精确名称 |

### `industry_overview` 的 `data`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data.data_available | 来源未说明 | 行业概览关键字段 |
| data.market_code | 来源未说明 | 行业概览关键字段 |
| data.taxonomy_code | 来源未说明 | 行业概览关键字段 |
| data.industry_summary | 来源未说明 | 行业概览关键字段 |
| data.monthly_order_growth_rate | number / array / null | 不同文档版本可能为 number、array 或 null，按真实响应读取 |

### `search_product_snapshots` 的 `data`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data.request_overview | 来源未说明 | 商品搜索关键字段 |
| data.record_count | 来源未说明 | 商品搜索关键字段 |
| data.matched_count | 来源未说明 | 商品搜索关键字段 |
| data.records | array | 商品记录数组 |
| data.features | 来源未说明 | 商品搜索关键字段 |
| data.notices | 来源未说明 | 商品搜索关键字段 |
| data.quota_hint | 来源未说明 | 上游返回时可见 |

#### `data.records[]` 可选字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data.records[].product_code | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].product_name | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].detail_link | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].picture_link | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].selling_price | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].currency_code | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].orders_last_30_days | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].orders_last_60_days | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].orders_last_90_days | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].order_growth_last_30_days | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].lifetime_orders | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].revenue_last_30_days | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].average_conversion_rate | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].feedback_count | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].feedback_score | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].brand_label | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].merchant_code | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].merchant_name | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].merchant_type | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].listing_status | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].taxonomy_name | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].taxonomy_name_localized | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].taxonomy_trail | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].first_listed_on | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].market_rank | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].segment_rank | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].option_count | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].competing_offer_count | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].fulfillment_type | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].available_inventory | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].parcel_length_cm | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].parcel_width_cm | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].parcel_height_cm | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].dimensional_weight_kg | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].parcel_weight_kg | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |
| data.records[].parcel_volume_cm3 | 来源未说明 | 来源仅列为商品记录的可选字段；可能缺失或为 null |

### `product_sales_trend` 的 `data`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data.market_code | 来源未说明 | 销量趋势关键字段 |
| data.product_code | 来源未说明 | 销量趋势关键字段 |
| data.input_method | 来源未说明 | 销量趋势关键字段 |
| data.range_start_date | 来源未说明 | 销量趋势关键字段 |
| data.range_end_date | 来源未说明 | 销量趋势关键字段 |
| data.requested_day_count | 来源未说明 | 销量趋势关键字段 |
| data.data_available | 来源未说明 | 销量趋势关键字段 |
| data.data_coverage | 来源未说明 | 销量趋势关键字段 |
| data.aggregation_period | 来源未说明 | 销量趋势关键字段 |
| data.monthly_order_series | 来源未说明 | 销量趋势关键字段 |
| data.weekly_order_series | 来源未说明 | 销量趋势关键字段 |
| data.notices | 来源未说明 | 销量趋势关键字段 |

### `image_search_products` 的 `data`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data.request_overview | 来源未说明 | 图片搜索关键字段 |
| data.provider_status | boolean / string | 提供方状态 |
| data.display_message | 来源未说明 | 图片搜索关键字段 |
| data.record_count | 来源未说明 | 图片搜索关键字段 |
| data.product_code | 来源未说明 | 图片搜索关键字段 |
| data.provider_payload | 来源未说明 | 图片搜索关键字段 |

### `review_search` 的 `data`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data.market_code | 来源未说明 | 评论查询关键字段 |
| data.product_code | 来源未说明 | 评论查询关键字段 |
| data.page_number | 来源未说明 | 评论查询关键字段 |
| data.page_size | 来源未说明 | 评论查询关键字段 |
| data.matched_count | 来源未说明 | 评论查询关键字段 |
| data.reviews | array | 评论记录数组；来源未提供评论字段的精确名称 |

### `get_my_quota_status` 的 `data`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data.customer_account_code | 来源未说明 | 配额查询可能返回的字段 |
| data.credit_balance | 来源未说明 | 配额查询可能返回的字段 |
| data.credit_policy | 来源未说明 | 配额查询可能返回的字段 |
| data.plan_code | 来源未说明 | 配额查询可能返回的字段 |
| data.plan_name | 来源未说明 | 配额查询可能返回的字段 |
| data.quota_limit | 来源未说明 | 配额查询可能返回的字段 |
| data.used_quota | 来源未说明 | 配额查询可能返回的字段 |
| data.quota_starts_at | 来源未说明 | 配额查询可能返回的字段 |
| data.quota_ends_at | 来源未说明 | 配额查询可能返回的字段 |
| data.available_points | 来源未说明 | 配额查询可能返回的字段 |
| data.points_mode | 来源未说明 | 配额查询可能返回的字段 |
| data.customer_code | 来源未说明 | 配额查询可能返回的字段 |
| data.service_plan | 来源未说明 | 配额查询可能返回的字段 |
| data.request_allowance | 来源未说明 | 配额查询可能返回的字段 |
| data.allowance_period_seconds | 来源未说明 | 配额查询可能返回的字段 |
| data.requests_consumed | 来源未说明 | 配额查询可能返回的字段 |
| data.requests_available | 来源未说明 | 配额查询可能返回的字段 |
| data.allowance_refresh_at | 来源未说明 | 配额查询可能返回的字段 |

### 本地图片预签名响应

来源 `skills/linkfox-damai-mercado-market-intelligence/scripts/upload_image.py` 仅明确使用以下响应字段：

| 字段路径 | 类型 | 说明 |
|---|---|---|
| errcode | 来源未说明 | 成功时脚本按 `200` 判断 |
| errmsg | 来源未说明 | 预签名请求失败时的错误信息 |
| url | 来源未说明 | 预签名 PUT URL；查询参数不得对用户展示 |

读取原则：先读 `data`；仅当 `data` 是文本或含义不明确时读取 `contentText`；除非用户请求诊断，不展示 `rawResponse`。

## 错误处理

| 状态/errcode | 含义 | 处理 |
|---|---|---|
| `1002` | 参数缺失、类型/范围错误、未知字段或不支持的 `toolName` | 按本文件修正请求，不自动改条件连续重试 |
| HTTP 401 | LinkFox 网关认证失败 | 读取 `references/onboarding.md`，区分 MCP/代理层与下游业务层处理 |
| HTTP 402 | LinkFox 积分或套餐不足 | 读取 `references/onboarding.md`，停止收费调用 |
| HTTP 403 | LinkFox 网关无权访问 | 按权限或路由异常处理，不按充值处理，也不要求用户提供上游 Key |
| `1003` | 上游限流、超时、协议或服务异常 | 收费 operation 不自动重放；保留脱敏请求并联系管理员 |
| `1005` | 后端托管的上游认证失败 | 联系管理员，不能让最终用户提供上游 Key |

下游可能以 HTTP 200 + `ToolErrorResponse` XML 表示业务错误。按代理返回内容识别并展示 `errcode` / `errmsg`，不得循环解析或因外层成功忽略业务错误。

空结果、`data_available=false` 或覆盖不足提示通常是正常业务结果，不等同于系统故障。HTTP 429/5xx或超时也不自动重试收费 operation。

## 本地图片上传辅助

- `scripts/upload_image.py` 仅负责校验本地 jpg/jpeg/png/gif/webp/heic 文件，并向标准输入提供的预签名 OSS URL 执行 `public-read` PUT；它不调用 LinkFox 网关、不读取 API Key，也不获取预签名 URL。
- 预签名 URL 必须先通过 `proxy_call` 调用 `oss/file/presignedPut` 获取。辅助脚本上传成功后只输出去掉 query string 的公开 URL，不打印完整预签名 URL。
- 预签名 URL 属于敏感短期资源，只用于一次上传；上传失败不得自动重新申请预签名或重复上传。

## MCP 示例

```json
{
  "toolName": "damai/call",
  "arguments": {
    "toolName": "search_categories",
    "arguments": {
      "market_code": "MLM",
      "query": "celulares",
      "limit": 10
    }
  }
}
```

## Feedback API

此接口独立于工具网关：

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "linkfox-damai-mercado-market-intelligence",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "Product trend coverage should be explained more clearly."
}
```

- `sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE`
- `category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`
- `content`：只写必要的用户意图、实际行为和改进点，不包含 Key、隐私、Base64 图片或完整大响应。

