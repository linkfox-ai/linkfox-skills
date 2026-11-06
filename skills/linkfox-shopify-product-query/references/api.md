# Shopify 商品查询 接口说明

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

## 接口：Shopify 商品查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/shopify/productQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string, maxLen=500 | 否 | 关键词或 Shopify 商品/店铺 URL |
| priceMin | number，≥0 | 否 | 价格区间（起始，USD），与 priceMax 组成上游 `price` |
| priceMax | number，≥0 | 否 | 价格区间（结束，USD） |
| salesWeeklyMin | integer，≥0 | 否 | 周销量区间（起始） |
| salesWeeklyMax | integer，≥0 | 否 | 周销量区间（结束） |
| publishedTimeBegin | string (YYYY-MM-DD) | 否 | 上架日期区间起始 |
| publishedTimeEnd | string (YYYY-MM-DD) | 否 | 上架日期区间结束 |
| facebookAd | integer | 否 | 是否有 Facebook 广告：1=有 |
| competitionMin | integer，≥0 | 否 | 竞争度（在售店铺数量）区间起始 |
| competitionMax | integer，≥0 | 否 | 竞争度（在售店铺数量）区间结束 |
| hasSupplier | integer | 否 | 是否有货源：1=有，0=无 |
| showDeleted | integer | 否 | 是否显示已下架商品：1=是，0=否 |
| country | string | 否 | 发货国家（两位国家代码，如 US） |
| sortBy | integer | 否 | 排序字段，默认 14=周销量降序；其他排序编码约定见下方。 |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100，建议不超过 50 |

#### 排序与区间约定

上游排序枚举包括价格、上架时间、广告数、竞争度、周销量、周销售额、销售额增长率等的升/降序组合；除默认值外的具体编码以当前网关工具 schema 注释为准，未知时使用表中默认值，不自行编造枚举。

`*Min` / `*Max` 构成对应上游区间；允许只填一侧，只填起始值表示「起始~」，只填结束值表示「~结束」。开关参数按上表使用整数，不替换为 JSON boolean。

#### 脚本选项与运行约定

命令行：`python scripts/shopify_product_query.py '<JSON 参数>' [--inline] [--no-cache]`，使用 Python 3，仅依赖标准库。

| 参数 / 配置 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 与上表的接口入参一致；保留原值透传。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用响应缓存读取和写入；默认使用 24 小时本地缓存。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关根 URL，最高优先级；默认 `https://tool-gateway.linkfox.com`。 |
| LINKFOX_TOOL_GATEWAY_BASE | string | 否 | 备用根 URL 配置，仅在 `LINKFOX_TOOL_GATEWAY` 未设置时使用。 |
| LINKFOX_EHUNT_SHOPIFY_PRODUCT_QUERY_PATH | string | 否 | 路径覆盖，默认 `ehunt/shopify/productQuery`，不含域名；有无开头 `/` 均可。 |
| LINKFOX_AGENT_API_KEY | string | 视配置 | 优先读取的接口密钥；与 `LINKFOXAGENT_API_KEY` 至少配置一个。 |
| LINKFOXAGENT_API_KEY | string | 视配置 | 备用接口密钥，仅在优先密钥为空时读取。 |
| SESSION_ID | string | 否 | 聚合同一任务的会话目录，并透传请求头；未设置时仅为落盘目录生成进程内稳定值，请求头值为空。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 分别透传对应请求头。 |

缓存位于 `<cwd>/linkfox/.cache/linkfox-shopify-product-query/` 下，使用按参数排序后哈希命名的 JSON，24 小时过期。公共调用器负责缓存读写，业务脚本不设置第二层缓存；命中时标记 `_cache.hit=true`，仍保存完整响应。缓存仅按参数区分，切换网关、密钥或路径后如需重新获取数据，应由用户决定是否使用 `--no-cache`。

完整响应保存至 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopify-product-query-<timestamp>.json`，同时维护会话 `_meta.json` 和 `index.jsonl`。执行前创建本次会话目录，并用等长文件名检查数据目录可写；目录不可用或路径过长时在请求前报错，不回退到家目录或临时目录，不写入 `/tmp`。输出大小阈值与摘要规则见 SKILL.md。

MCP 展示名为「Shopify 商品查询」，确切工具名以当前环境下发的工具元数据为准。若默认 HTTP 路径返回 404，使用已有的 `listEnabledTool` 信息或请运维确认实际路径，再按已确认结果设置路径覆盖；不自动枚举路径请求。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | 以实际返回为准 | 上游可能在根级返回此字段，成功值为 `200`，具体以当前网关响应为准；不替代公共响应码基本规则。 |
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关消息。 |
| total | integer | 本页返回条数 |
| productNum | integer | 符合条件的商品总数（上游 `product_num`） |
| products | array | Shopify 商品列表 |
| columns | array | 渲染的列 |
| title | string | 标题（`Shopify 商品查询`） |
| sourceType | string | 来源类型：shopify |
| sourceTool | string | 工具类型：ehunt |
| type | string | 渲染的样式：tableListWorkbenches |

#### products[] 商品字段

| 字段 | 类型 | 上游别名 | 说明 |
|------|------|----------|------|
| productId | 以实际返回为准 | `product_id` | 商品 ID |
| title | 以实际返回为准 | - | 商品标题 |
| productLink | 以实际返回为准 | `product_link` | 商品链接 |
| previewImageUrl | 以实际返回为准 | `preview_image_url` | 主图 URL |
| country | 以实际返回为准 | - | 发货国家 |
| minPrice | 以实际返回为准 | `min_price` | 最低价 |
| maxPrice | 以实际返回为准 | `max_price` | 最高价 |
| storeId | 以实际返回为准 | `store_id` | 店铺 ID |
| shopId | 以实际返回为准 | `shop_id` | Shopify shop ID |
| storeLink | 以实际返回为准 | `store_link` | 店铺链接 |
| storeRank | 以实际返回为准 | `store_rank` | 店铺等级 |
| competitorCount | 以实际返回为准 | `competitor_count` | 竞争度（在售店铺数量） |
| facebookAdCount | 以实际返回为准 | `facebook_ad_count` | Facebook 广告数 |
| weekOrderCount | string | `week_order_count` | 周销量（字符串） |
| weekRevenueCount | 以实际返回为准 | `week_revenue_count` | 周销售额 |
| weekRevenueGrowth | 以实际返回为准 | `week_revenue_growth` | 周销售额增长率（%） |
| shelfTime | 以实际返回为准 | `shelf_time` | 上架时间 |
| isDeleted | 以实际返回为准 | `is_deleted` | 是否下架：0=上架，1=下架 |
| isFavourite | 以实际返回为准 | `is_favourite` | 是否已收藏 |

其余商品字段类型及 `columns[]` 内部字段以实际返回为准，不推断额外嵌套结构。

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer | 业务脚本记录的实际 HTTP 状态，属于本地字段，不是网关响应保证；即使错误响应体是 JSON，也保留该状态。 |

按公共规则同时判断 `_http_status` 和 `errcode`，不能因响应体缺少错误码或含成功码而忽略 HTTP 错误。连接失败时没有 HTTP 状态，不补造该字段。缓存命中时，该字段表示原请求的历史状态；缓存也可能保存错误响应，不代表本次已重新请求成功。历史缓存可能没有此字段，此时 HTTP 状态未知，按已有业务码和错误消息解释，不推断为 HTTP 成功；如需重新查询，遵守成本约束并使用 `--no-cache`。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 参数与业务返回结构以当前网关实际返回为准。
- 无数据时网关可能抛错，不保证一定返回成功状态加空商品列表；根据实际消息解释无匹配数据与其他错误。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ehunt/shopify/productQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"searchKey":"phone case","country":"US","page":1,"pageSize":20}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopify-product-query",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```