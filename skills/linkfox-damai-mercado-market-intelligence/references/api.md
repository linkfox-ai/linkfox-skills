# 大麦数据美客多市场洞察与选品 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：搜索候选类目（search_categories）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/damai/call`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | 固定 `search_categories`，大小写完全一致；6 个公开操作之一。 |
| `arguments` | object | 否 | 下表操作参数；无参数操作传 `{}`。 |

#### arguments 字段

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `query` | string | 否 | - | 当地语言类目关键词 |
| `limit` | integer | 否 | 默认及最大 100 | 返回数量 |

市场编码支持 `MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚；省略 `market_code` 时上游按 `MLM` 处理。类目与商品关键词使用目标市场的当地语言。

保持 snake_case 字段，不传 `uId`、`uid`、`memberId`、未文档化的 camelCase 别名或未知字段。脚本透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；上游 `X-API-Key` 由后端托管，不得向用户索要。

脚本 CLI 与缓存行为见 [脚本调用约定](#脚本调用约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 成功时为 `"200"`。 |
| `msg` | string | 成功时为 `"ok"`。 |
| `errcode` | integer/string/null | 网关状态，生产成功响应通常为 `200`，按基础规则判断。 |
| `errmsg` | string | 网关消息，生产成功响应通常为 `ok`。 |
| `type` | string | 当前为 `rawMcpToolResult`。 |
| `toolName` | string | 实际调用的操作名。 |
| `providerCharged` | boolean | 上游是否按成功调用扣次数。 |
| `charged` | boolean | LinkFox 是否计费；类目搜索免费，对应值为 false。五个收费操作成功时为 true。 |
| `data` | object | 解包后的业务数据；数组、标量或空值会被后端按响应异常处理。 |
| `rawResponse` | object | MCP `tools/call` 原始 result，仅诊断时读取。 |
| `contentText` | string | MCP text content 原文，可为空。 |
| `textParsedAsJson` | boolean | text content 是否解析为 JSON。 |
| `total` | integer | 可推断时返回的记录数。 |
| `costToken` | integer | 计费 token；响应体可能省略，实际以响应头 `X-Cost-Token` 为准。 |
| `costTime` | integer | 后端耗时，毫秒。 |

#### data 业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `request_overview` | object | 请求概况。 |
| `record_count` | integer | 返回记录数。 |
| `records[]` | array<object> | 类目记录；可能含类目 ID、名称、本地化名称、层级、路径、叶子标记、近 30 天活跃商品数、销量、GMV、均价、店铺数；记录内的字段名及类型以实际响应为准，不补造。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `1002`：参数缺失、类型或范围错误、未知字段或不支持的操作；修正请求，不自动改条件连续试探。
- `1003`：上游限流、超时、协议或服务异常；收费操作不自动重放，保留脱敏请求并联系管理员。
- `1005`：后端托管的上游认证失败；联系管理员，不让最终用户提供上游 Key。网关无权访问时检查是否误用上游 Key。
- HTTP 200 可能携带 `ToolErrorResponse` XML；业务封装将其归一化为 `errcode` / `errmsg`，失败不缓存。不只依据退出码，结合 `code` / `msg`、`error` / `errmsg` 与业务 `data` 解释结果。
- 本操作免费，不扣 LinkFox 算力。
- 空记录、`data_available=false` 或覆盖不足提示通常是正常业务结果；不自动换词、翻页或换市场。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/damai/call" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"search_categories","arguments":{"market_code":"MLM","query":"celulares","limit":10}}'
```

## 接口：查询行业概览（industry_overview）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/damai/call`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | 固定 `industry_overview`，大小写完全一致；6 个公开操作之一。 |
| `arguments` | object | 否 | 下表操作参数；无参数操作传 `{}`。 |

#### arguments 字段

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `category_id` | string | 是 | - | 类目 ID |
| `market_code` | string | 否 | `MLM` | 市场编码 |

市场编码支持 `MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚；省略 `market_code` 时上游按 `MLM` 处理。类目与商品关键词使用目标市场的当地语言。

保持 snake_case 字段，不传 `uId`、`uid`、`memberId`、未文档化的 camelCase 别名或未知字段。脚本透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；上游 `X-API-Key` 由后端托管，不得向用户索要。

脚本 CLI 与缓存行为见 [脚本调用约定](#脚本调用约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 成功时为 `"200"`。 |
| `msg` | string | 成功时为 `"ok"`。 |
| `errcode` | integer/string/null | 网关状态，生产成功响应通常为 `200`，按基础规则判断。 |
| `errmsg` | string | 网关消息，生产成功响应通常为 `ok`。 |
| `type` | string | 当前为 `rawMcpToolResult`。 |
| `toolName` | string | 实际调用的操作名。 |
| `providerCharged` | boolean | 上游是否按成功调用扣次数。 |
| `charged` | boolean | LinkFox 是否计费；类目搜索免费，对应值为 false。五个收费操作成功时为 true。 |
| `data` | object | 解包后的业务数据；数组、标量或空值会被后端按响应异常处理。 |
| `rawResponse` | object | MCP `tools/call` 原始 result，仅诊断时读取。 |
| `contentText` | string | MCP text content 原文，可为空。 |
| `textParsedAsJson` | boolean | text content 是否解析为 JSON。 |
| `total` | integer | 可推断时返回的记录数。 |
| `costToken` | integer | 计费 token；响应体可能省略，实际以响应头 `X-Cost-Token` 为准。 |
| `costTime` | integer | 后端耗时，毫秒。 |

#### data 业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data_available` | boolean | 是否有数据。 |
| `market_code` | string | 市场编码。 |
| `taxonomy_code` | string | 类目编码。 |
| `industry_summary` | object | 行业汇总；含月销量、月均价、月 GMV、商品数、活跃商品数、平均日销量、均价和近 30 天交易额，指标的字段名及类型以实际响应为准。 |
| `monthly_order_growth_rate` | number/array/null | 返回值可能为 number、array 或 null，所在层级以实际响应为准。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `1002`：参数缺失、类型或范围错误、未知字段或不支持的操作；修正请求，不自动改条件连续试探。
- `1003`：上游限流、超时、协议或服务异常；收费操作不自动重放，保留脱敏请求并联系管理员。
- `1005`：后端托管的上游认证失败；联系管理员，不让最终用户提供上游 Key。网关无权访问时检查是否误用上游 Key。
- HTTP 200 可能携带 `ToolErrorResponse` XML；业务封装将其归一化为 `errcode` / `errmsg`，失败不缓存。不只依据退出码，结合 `code` / `msg`、`error` / `errmsg` 与业务 `data` 解释结果。
- 每次成功调用收取 12 LinkFox 算力（￥0.12）。成功但没有匹配记录时也可能扣费。
- 空记录、`data_available=false` 或覆盖不足提示通常是正常业务结果；不自动换词、翻页或换市场。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/damai/call" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"industry_overview","arguments":{"market_code":"MLM","category_id":"MLM1055"}}'
```

## 接口：搜索商品快照（search_product_snapshots）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/damai/call`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | 固定 `search_product_snapshots`，大小写完全一致；6 个公开操作之一。 |
| `arguments` | object | 否 | 下表操作参数；无参数操作传 `{}`。 |

#### arguments 字段

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

市场编码支持 `MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚；省略 `market_code` 时上游按 `MLM` 处理。类目与商品关键词使用目标市场的当地语言。

保持 snake_case 字段，不传 `uId`、`uid`、`memberId`、未文档化的 camelCase 别名或未知字段。脚本透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；上游 `X-API-Key` 由后端托管，不得向用户索要。

`keyword`、`category_id`、`sku_id`、`product_url`、`shop_id`、`shop_query` 至少提供一个。`product_status`、`stock_type` 及部分履约值由上游定义，不补造枚举。

脚本 CLI 与缓存行为见 [脚本调用约定](#脚本调用约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 成功时为 `"200"`。 |
| `msg` | string | 成功时为 `"ok"`。 |
| `errcode` | integer/string/null | 网关状态，生产成功响应通常为 `200`，按基础规则判断。 |
| `errmsg` | string | 网关消息，生产成功响应通常为 `ok`。 |
| `type` | string | 当前为 `rawMcpToolResult`。 |
| `toolName` | string | 实际调用的操作名。 |
| `providerCharged` | boolean | 上游是否按成功调用扣次数。 |
| `charged` | boolean | LinkFox 是否计费；类目搜索免费，对应值为 false。五个收费操作成功时为 true。 |
| `data` | object | 解包后的业务数据；数组、标量或空值会被后端按响应异常处理。 |
| `rawResponse` | object | MCP `tools/call` 原始 result，仅诊断时读取。 |
| `contentText` | string | MCP text content 原文，可为空。 |
| `textParsedAsJson` | boolean | text content 是否解析为 JSON。 |
| `total` | integer | 可推断时返回的记录数。 |
| `costToken` | integer | 计费 token；响应体可能省略，实际以响应头 `X-Cost-Token` 为准。 |
| `costTime` | integer | 后端耗时，毫秒。 |

#### data 业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `request_overview` | object | 请求概况。 |
| `record_count` | integer | 返回记录数。 |
| `matched_count` | integer | 匹配记录数。 |
| `records[]` | array<object> | 商品记录，可选字段见下表。 |
| `features` | 以实际响应为准 | 商品属性聚合，类型以实际响应为准。 |
| `notices` | 以实际响应为准 | 上游提示。 |

#### records[] 可选字段

所有字段都可能缺失或为 null，类型以实际响应为准，以下不额外限定类型。

| 字段 | 类型 | 说明 |
|---|---|---|
| `product_code` | 以实际响应为准 / null | 商品编号。 |
| `product_name` | 以实际响应为准 / null | 商品名称。 |
| `detail_link` | 以实际响应为准 / null | 详情链接。 |
| `picture_link` | 以实际响应为准 / null | 图片链接。 |
| `selling_price` | 以实际响应为准 / null | 售价。 |
| `currency_code` | 以实际响应为准 / null | 币种。 |
| `orders_last_30_days` | 以实际响应为准 / null | 近 30 天订单。 |
| `orders_last_60_days` | 以实际响应为准 / null | 近 60 天订单。 |
| `orders_last_90_days` | 以实际响应为准 / null | 近 90 天订单。 |
| `order_growth_last_30_days` | 以实际响应为准 / null | 近 30 天订单增长。 |
| `lifetime_orders` | 以实际响应为准 / null | 累计订单。 |
| `revenue_last_30_days` | 以实际响应为准 / null | 近 30 天交易额。 |
| `average_conversion_rate` | 以实际响应为准 / null | 平均转化率。 |
| `feedback_count` | 以实际响应为准 / null | 评论数。 |
| `feedback_score` | 以实际响应为准 / null | 评分。 |
| `brand_label` | 以实际响应为准 / null | 品牌。 |
| `merchant_code` | 以实际响应为准 / null | 卖家编号。 |
| `merchant_name` | 以实际响应为准 / null | 卖家名称。 |
| `merchant_type` | 以实际响应为准 / null | 卖家类型。 |
| `listing_status` | 以实际响应为准 / null | 商品状态。 |
| `taxonomy_name` | 以实际响应为准 / null | 类目名称。 |
| `taxonomy_name_localized` | 以实际响应为准 / null | 本地化类目名。 |
| `taxonomy_trail` | 以实际响应为准 / null | 类目路径。 |
| `first_listed_on` | 以实际响应为准 / null | 首次上架日期。 |
| `market_rank` | 以实际响应为准 / null | 市场排名。 |
| `segment_rank` | 以实际响应为准 / null | 细分排名。 |
| `option_count` | 以实际响应为准 / null | 变体数。 |
| `competing_offer_count` | 以实际响应为准 / null | 竞争报价数。 |
| `fulfillment_type` | 以实际响应为准 / null | 履约类型。 |
| `available_inventory` | 以实际响应为准 / null | 可用库存。 |
| `parcel_length_cm` | 以实际响应为准 / null | 包裹长度（cm）。 |
| `parcel_width_cm` | 以实际响应为准 / null | 包裹宽度（cm）。 |
| `parcel_height_cm` | 以实际响应为准 / null | 包裹高度（cm）。 |
| `dimensional_weight_kg` | 以实际响应为准 / null | 体积重量（kg）。 |
| `parcel_weight_kg` | 以实际响应为准 / null | 包裹重量（kg）。 |
| `parcel_volume_cm3` | 以实际响应为准 / null | 包裹体积（cm³）。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `1002`：参数缺失、类型或范围错误、未知字段或不支持的操作；修正请求，不自动改条件连续试探。
- `1003`：上游限流、超时、协议或服务异常；收费操作不自动重放，保留脱敏请求并联系管理员。
- `1005`：后端托管的上游认证失败；联系管理员，不让最终用户提供上游 Key。网关无权访问时检查是否误用上游 Key。
- HTTP 200 可能携带 `ToolErrorResponse` XML；业务封装将其归一化为 `errcode` / `errmsg`，失败不缓存。不只依据退出码，结合 `code` / `msg`、`error` / `errmsg` 与业务 `data` 解释结果。
- 每次成功调用收取 12 LinkFox 算力（￥0.12）。成功但没有匹配记录时也可能扣费。
- 空记录、`data_available=false` 或覆盖不足提示通常是正常业务结果；不自动换词、翻页或换市场。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/damai/call" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"search_product_snapshots","arguments":{"market_code":"MLM","category_id":"MLM1055","limit":20}}'
```

## 接口：查询商品销量趋势（product_sales_trend）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/damai/call`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | 固定 `product_sales_trend`，大小写完全一致；6 个公开操作之一。 |
| `arguments` | object | 否 | 下表操作参数；无参数操作传 `{}`。 |

#### arguments 字段

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `sku_id` | string | 是 | - | 商品 ID |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `days` | integer | 否 | 默认 730，1-731 | 查询天数 |

市场编码支持 `MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚；省略 `market_code` 时上游按 `MLM` 处理。类目与商品关键词使用目标市场的当地语言。

保持 snake_case 字段，不传 `uId`、`uid`、`memberId`、未文档化的 camelCase 别名或未知字段。脚本透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；上游 `X-API-Key` 由后端托管，不得向用户索要。

脚本 CLI 与缓存行为见 [脚本调用约定](#脚本调用约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 成功时为 `"200"`。 |
| `msg` | string | 成功时为 `"ok"`。 |
| `errcode` | integer/string/null | 网关状态，生产成功响应通常为 `200`，按基础规则判断。 |
| `errmsg` | string | 网关消息，生产成功响应通常为 `ok`。 |
| `type` | string | 当前为 `rawMcpToolResult`。 |
| `toolName` | string | 实际调用的操作名。 |
| `providerCharged` | boolean | 上游是否按成功调用扣次数。 |
| `charged` | boolean | LinkFox 是否计费；类目搜索免费，对应值为 false。五个收费操作成功时为 true。 |
| `data` | object | 解包后的业务数据；数组、标量或空值会被后端按响应异常处理。 |
| `rawResponse` | object | MCP `tools/call` 原始 result，仅诊断时读取。 |
| `contentText` | string | MCP text content 原文，可为空。 |
| `textParsedAsJson` | boolean | text content 是否解析为 JSON。 |
| `total` | integer | 可推断时返回的记录数。 |
| `costToken` | integer | 计费 token；响应体可能省略，实际以响应头 `X-Cost-Token` 为准。 |
| `costTime` | integer | 后端耗时，毫秒。 |

#### data 业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `market_code` | string | 市场编码。 |
| `product_code` | string | 商品编号。 |
| `input_method` | 以实际响应为准 | 输入方式。 |
| `range_start_date` | string | 统计起始日期。 |
| `range_end_date` | string | 统计结束日期。 |
| `requested_day_count` | integer | 请求天数。 |
| `data_available` | boolean | 数据是否可用。 |
| `data_coverage` | 以实际响应为准 | 实际覆盖信息。 |
| `aggregation_period` | 以实际响应为准 | 聚合周期。 |
| `monthly_order_series` | 以实际响应为准 | 月度订单序列；元素结构以实际响应为准。 |
| `weekly_order_series` | 以实际响应为准 | ISO 周订单序列；元素结构以实际响应为准。 |
| `notices` | 以实际响应为准 | 覆盖不足及其他提示。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `1002`：参数缺失、类型或范围错误、未知字段或不支持的操作；修正请求，不自动改条件连续试探。
- `1003`：上游限流、超时、协议或服务异常；收费操作不自动重放，保留脱敏请求并联系管理员。
- `1005`：后端托管的上游认证失败；联系管理员，不让最终用户提供上游 Key。网关无权访问时检查是否误用上游 Key。
- HTTP 200 可能携带 `ToolErrorResponse` XML；业务封装将其归一化为 `errcode` / `errmsg`，失败不缓存。不只依据退出码，结合 `code` / `msg`、`error` / `errmsg` 与业务 `data` 解释结果。
- 每次成功调用收取 12 LinkFox 算力（￥0.12）。成功但没有匹配记录时也可能扣费。
- 空记录、`data_available=false` 或覆盖不足提示通常是正常业务结果；不自动换词、翻页或换市场。
- 区分请求天数与覆盖天数，说明覆盖不足；月度与 ISO 周序列不能当成完整逐日数据。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/damai/call" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"product_sales_trend","arguments":{"market_code":"MLM","sku_id":"MLM1602785195","days":90}}'
```

## 接口：搜索图片相似商品（image_search_products）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/damai/call`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | 固定 `image_search_products`，大小写完全一致；6 个公开操作之一。 |
| `arguments` | object | 否 | 下表操作参数；无参数操作传 `{}`。 |

#### arguments 字段

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `image_url` | string | 条件必填 | - | 可公开访问的 HTTP(S) 图片 URL |
| `image_base64` | string | 条件必填 | - | 图片 Base64 字符串 |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `page` | integer | 否 | 1 | 页码 |
| `limit` | integer | 否 | 50 | 返回数量；最大值由上游服务配置决定 |
| `token` | string | 否 | 服务端配置 | 图片搜索令牌，通常无需传入；传入时仅覆盖本次请求 |

市场编码支持 `MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚；省略 `market_code` 时上游按 `MLM` 处理。类目与商品关键词使用目标市场的当地语言。

保持 snake_case 字段，不传 `uId`、`uid`、`memberId`、未文档化的 camelCase 别名或未知字段。脚本透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；上游 `X-API-Key` 由后端托管，不得向用户索要。

`image_url`、`image_base64` 至少提供一个。本地图片先运行 `python scripts/upload_image.py <path>`，取得公开 URL 再图搜；上传预签名接口详见本文件对应接口节。`token` 与部分履约值由上游定义，不推测枚举；不得在用户结果中显示完整 Base64 或预签名查询参数。

脚本 CLI 与缓存行为见 [脚本调用约定](#脚本调用约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 成功时为 `"200"`。 |
| `msg` | string | 成功时为 `"ok"`。 |
| `errcode` | integer/string/null | 网关状态，生产成功响应通常为 `200`，按基础规则判断。 |
| `errmsg` | string | 网关消息，生产成功响应通常为 `ok`。 |
| `type` | string | 当前为 `rawMcpToolResult`。 |
| `toolName` | string | 实际调用的操作名。 |
| `providerCharged` | boolean | 上游是否按成功调用扣次数。 |
| `charged` | boolean | LinkFox 是否计费；类目搜索免费，对应值为 false。五个收费操作成功时为 true。 |
| `data` | object | 解包后的业务数据；数组、标量或空值会被后端按响应异常处理。 |
| `rawResponse` | object | MCP `tools/call` 原始 result，仅诊断时读取。 |
| `contentText` | string | MCP text content 原文，可为空。 |
| `textParsedAsJson` | boolean | text content 是否解析为 JSON。 |
| `total` | integer | 可推断时返回的记录数。 |
| `costToken` | integer | 计费 token；响应体可能省略，实际以响应头 `X-Cost-Token` 为准。 |
| `costTime` | integer | 后端耗时，毫秒。 |

#### data 业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `request_overview` | object | 请求概况。 |
| `provider_status` | boolean/string | 上游状态；不臆造枚举。 |
| `display_message` | string | 展示消息。 |
| `record_count` | integer | 记录数。 |
| `product_code` | 以实际响应为准 | 相似商品编号，单值或集合形式以实际响应为准。 |
| `provider_payload` | 以实际响应为准 | 上游原始业务数据。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `1002`：参数缺失、类型或范围错误、未知字段或不支持的操作；修正请求，不自动改条件连续试探。
- `1003`：上游限流、超时、协议或服务异常；收费操作不自动重放，保留脱敏请求并联系管理员。
- `1005`：后端托管的上游认证失败；联系管理员，不让最终用户提供上游 Key。网关无权访问时检查是否误用上游 Key。
- HTTP 200 可能携带 `ToolErrorResponse` XML；业务封装将其归一化为 `errcode` / `errmsg`，失败不缓存。不只依据退出码，结合 `code` / `msg`、`error` / `errmsg` 与业务 `data` 解释结果。
- 每次成功调用收取 12 LinkFox 算力（￥0.12）。成功但没有匹配记录时也可能扣费。
- 空记录、`data_available=false` 或覆盖不足提示通常是正常业务结果；不自动换词、翻页或换市场。
- 图搜返回商品编号，补充完整商品快照需要另一次可能收费的查询。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/damai/call" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"image_search_products","arguments":{"market_code":"MLM","image_url":"https://example.com/product.png"}}'
```

## 接口：查询商品评论（review_search）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/damai/call`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `toolName` | string | 是 | 固定 `review_search`，大小写完全一致；6 个公开操作之一。 |
| `arguments` | object | 否 | 下表操作参数；无参数操作传 `{}`。 |

#### arguments 字段

| 参数 | 类型 | 必填 | 默认/范围 | 说明 |
|---|---|---:|---|---|
| `sku_id` | string | 是 | - | 商品 ID |
| `market_code` | string | 否 | `MLM` | 市场编码 |
| `page` | integer | 否 | 1 | 页码 |
| `limit` | integer | 否 | 默认 20，最大 100 | 每页数量 |

市场编码支持 `MLM` 墨西哥、`MLB` 巴西、`MLA` 阿根廷、`MLC` 智利、`MCO` 哥伦比亚；省略 `market_code` 时上游按 `MLM` 处理。类目与商品关键词使用目标市场的当地语言。

保持 snake_case 字段，不传 `uId`、`uid`、`memberId`、未文档化的 camelCase 别名或未知字段。脚本透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`；上游 `X-API-Key` 由后端托管，不得向用户索要。

脚本 CLI 与缓存行为见 [脚本调用约定](#脚本调用约定)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 成功时为 `"200"`。 |
| `msg` | string | 成功时为 `"ok"`。 |
| `errcode` | integer/string/null | 网关状态，生产成功响应通常为 `200`，按基础规则判断。 |
| `errmsg` | string | 网关消息，生产成功响应通常为 `ok`。 |
| `type` | string | 当前为 `rawMcpToolResult`。 |
| `toolName` | string | 实际调用的操作名。 |
| `providerCharged` | boolean | 上游是否按成功调用扣次数。 |
| `charged` | boolean | LinkFox 是否计费；类目搜索免费，对应值为 false。五个收费操作成功时为 true。 |
| `data` | object | 解包后的业务数据；数组、标量或空值会被后端按响应异常处理。 |
| `rawResponse` | object | MCP `tools/call` 原始 result，仅诊断时读取。 |
| `contentText` | string | MCP text content 原文，可为空。 |
| `textParsedAsJson` | boolean | text content 是否解析为 JSON。 |
| `total` | integer | 可推断时返回的记录数。 |
| `costToken` | integer | 计费 token；响应体可能省略，实际以响应头 `X-Cost-Token` 为准。 |
| `costTime` | integer | 后端耗时，毫秒。 |

#### data 业务字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `market_code` | string | 市场编码。 |
| `product_code` | string | 商品编号。 |
| `page_number` | integer | 页码。 |
| `page_size` | integer | 每页数量。 |
| `matched_count` | integer | 匹配记录数。 |
| `reviews[]` | array<object> | 评论可能含 ID、评分、标题或商品名、原文、英文或本地化文本、时间、买家名；内部字段名及类型以实际响应为准，不补造。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `1002`：参数缺失、类型或范围错误、未知字段或不支持的操作；修正请求，不自动改条件连续试探。
- `1003`：上游限流、超时、协议或服务异常；收费操作不自动重放，保留脱敏请求并联系管理员。
- `1005`：后端托管的上游认证失败；联系管理员，不让最终用户提供上游 Key。网关无权访问时检查是否误用上游 Key。
- HTTP 200 可能携带 `ToolErrorResponse` XML；业务封装将其归一化为 `errcode` / `errmsg`，失败不缓存。不只依据退出码，结合 `code` / `msg`、`error` / `errmsg` 与业务 `data` 解释结果。
- 每次成功调用收取 12 LinkFox 算力（￥0.12）。成功但没有匹配记录时也可能扣费。
- 空记录、`data_available=false` 或覆盖不足提示通常是正常业务结果；不自动换词、翻页或换市场。
- 保留评论原语言；仅在上游返回译文时标注翻译。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/damai/call" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"toolName":"review_search","arguments":{"market_code":"MLM","sku_id":"MLM1602785195","limit":20}}'
```

## 接口：获取图片上传预签名

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `contentType` | string | 是 | 图片 MIME 类型。脚本映射 jpg/jpeg→image/jpeg、png→image/png、gif→image/gif、webp→image/webp、heic→image/heic。 |
| `fileExtension` | string | 是 | 小写、不含点的扩展名：jpg、jpeg、png、gif、webp、heic。 |

#### 上传脚本约定

| 参数 / 步骤 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `<local_image_path>` | 命令行字符串 | 是 | `python scripts/upload_image.py <local_image_path>`；先检查本地文件存在与扩展名，失败不请求网关。 |
| `--inline` / `--no-cache` | 命令行开关 | 否 | 上传 CLI 不接受此类查询选项；内部预签名调用固定 `--no-cache`，不复用预签名。 |
| 预签名后续 PUT | HTTP PUT | 是 | 向返回的 OSS URL 原样 PUT 文件；超时 150s，Content-Type 与申请一致，`x-oss-object-acl: public-read`。不得带 LinkFox Authorization 或会话头。 |

预签名 LinkFox 请求透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。随后 OSS PUT 是素材上传，非大麦业务接口。上传成功后移除查询串得到公开 URL，有效期 24 小时。不在用户结果显示预签名查询串或完整 Base64。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer/string/null | 网关业务状态，按基础规则判断；成功示例为 200。 |
| `errmsg` | string | 网关消息或错误原因。 |
| `url` | string | 预签名 PUT 地址；仅用于上传，不向用户输出查询串。 |

#### 上传 CLI 输出

| 字段 | 类型 | 说明 |
|---|---|---|
| `url` | string | PUT 成功后去掉查询串的公开图片 URL，可用于图搜。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应缺少可用 `url` 时停止，不执行 PUT 或收费图搜。预签名不缓存，也不自动重试。
- OSS PUT 仅 HTTP 200、201 视为上传完成；上传失败先修正图片或上传问题，不调用收费图搜。不输出含签名的 URL 或原始错误响应。
- 图片上传预签名的算力价格不确定，不推定免费或套用大麦收费标准。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/file/presignedPut" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"contentType":"image/png","fileExtension":"png"}'
```

## 脚本调用约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 原样传递上述网关请求，不改写字段或筛选条件。 |
| `--inline` | 命令行开关 | 否 | 强制完整打印，同时保存完整响应。 |
| `--no-cache` | 命令行开关 | 否 | 跳过 24 小时缓存的读取与写入。 |

业务脚本使用 `<cwd>/linkfox/.cache/linkfox-damai-mercado-market-intelligence/` 下按规范化完整请求计算的缓存键；仅复用有效成功响应，缓存命中含 `_cache.hit=true`。公共调用器始终传 `--no-cache`，不引入第二层响应缓存。失败与 XML 业务错误不写缓存；未过期正常空结果可复用。响应写入当前工作目录会话数据文件，禁止 `/tmp`，在请求前检查实际会话目录及目标文件可写；保存失败时返回非零退出码，提示请求可能已完成，禁止自动重试。不回退家目录或临时目录。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-damai-mercado-market-intelligence",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
