# Temu 商品查询 接口说明

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

## 接口：Temu 商品查询

MCP 展示名为「Temu 商品查询」，确切工具名以当前环境下发的元数据为准。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/temu/productQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string, maxLen=500 | 否 | 关键词或商品 ID / 店铺 ID |
| categoryHome | string | 否 | 前台类目 ID |
| categoryBackend | string | 否 | 后台类目 ID |
| priceBegin | number，≥0 | 否 | 价格区间起始（USD），组成上游 `price` |
| priceEnd | number，≥0 | 否 | 价格区间结束（USD） |
| ratingBegin | number (0~5) | 否 | 评分区间起始，组成上游 `rating` |
| ratingEnd | number (0~5) | 否 | 评分区间结束 |
| reviewsBegin | integer，≥0 | 否 | 评论数区间起始，组成 `reviews` |
| reviewsEnd | integer，≥0 | 否 | 评论数区间结束 |
| salesTotalBegin | integer，≥0 | 否 | 总销量区间起始，组成 `sales_total` |
| salesTotalEnd | integer，≥0 | 否 | 总销量区间结束 |
| salesWeeklyBegin | integer，≥0 | 否 | 周销量区间起始，组成 `sales_weekly` |
| salesWeeklyEnd | integer，≥0 | 否 | 周销量区间结束 |
| salesDailyBegin | integer，≥0 | 否 | 日销量区间起始，组成 `sales_daily` |
| salesDailyEnd | integer，≥0 | 否 | 日销量区间结束 |
| publishTimeBegin | string (YYYY-MM-DD) | 否 | 上架日期区间起始，组成 `publish_time` |
| publishTimeEnd | string (YYYY-MM-DD) | 否 | 上架日期区间结束 |
| soldOut | integer | 否 | 是否下架：0=上架，1=下架 |
| isLocal | integer | 否 | 是否半托管：0=全托管，1=半托管 |
| region | string | 否 | 半托管地区，多个逗号分隔 |
| tags | string | 否 | 商品标签，多个逗号分隔 |
| customTags | string | 否 | 自定义标签，多个逗号分隔 |
| sortBy | string | 否 | 排序字段+方向：`order_week-0`（周销量降序，默认）、`price-0`、`order_total-0`、`rating-0` 等 |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100，建议不超过 50 |

#### 参数约束与使用限制

- 所有区间的 `*Begin` / `*End` 成对出现：价格、评分、评论数、总/周/日销量和上架时间，分别组成表中列出的上游区间。
- 类目 ID 可先从 Temu 品类检索数据源获取，不能将类目名称当成 ID。
- 排序、托管模式、上下架、地区、标签及分页的取值约定见参数表；不自行扩展未确认的排序枚举。
- 每次翻页均为单独请求，费用按 `SKILL.md` 的「算力消耗预估」计算；不得自动连续试探。

#### 脚本选项与运行约定

脚本仅依赖 Python 3 标准库，接受与接口相同的 JSON。公共调用器提供单层响应缓存，缓存键、路径和 24 小时有效期见下文。

| 参数 / 环境变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | CLI 位置参数 | 是 | 原样传递请求体，不自动转换区间、补默认值或翻页。 |
| --inline | CLI flag | 否 | 强制完整打印，同时仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过缓存读取和写入；默认使用缓存。 |
| --help / -h | CLI flag | 否 | 显示本地帮助，不发起请求。 |
| LINKFOX_AGENT_API_KEY | string | 是，二选一 | 首选认证变量；未设置时使用 LINKFOXAGENT_API_KEY。 |
| LINKFOXAGENT_API_KEY | string | 是，二选一 | 兼容认证变量。 |
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关根地址，最高优先级，默认 https://tool-gateway.linkfox.com。 |
| LINKFOX_TOOL_GATEWAY_BASE | string | 否 | 备用网关根地址配置；仅在 LINKFOX_TOOL_GATEWAY 为空时采用。 |
| LINKFOX_EHUNT_TEMU_PRODUCT_QUERY_PATH | string | 否 | 请求路径覆盖，默认 ehunt/temu/productQuery；不含域名，允许前导斜杠。 |
| SESSION_ID | string | 否 | 聚合会话数据；缺省生成进程内稳定的会话编号；设置的环境变量值同时透传为同名请求头。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 透传为同名请求头。 |

缓存位置为 `<cwd>/linkfox/.cache/linkfox-temu-product-query/linkfox-temu-product-query-<hash>.json`；缓存键为排序后的 JSON 参数的 SHA-256 前 16 位，24 小时内命中时不再请求。缓存命中会增加 `_cache.hit=true` 标记，不代表本次重新采集了数据。`--no-cache` 仍可能由公共调用器建立空缓存目录，但不读写响应缓存。

完整响应按 `SKILL.md` 输出策略保存，同时维护会话 `_meta.json` 和 `linkfox/index.jsonl`。业务封装在请求前检查当前目录、实际会话数据目录及元数据可写，并固定到 `<cwd>/linkfox`，不回退到家目录或临时目录；会话目录和元数据可能在请求前建立。

### 响应结构

参数和实际返回结构以当前网关为准，下表列出商品查询的业务字段。商品对象字段及可选根级 `code` 的具体类型、更多嵌套结构和业务字段出现的位置以实际响应为准；不得据字段名补造类型或数据。

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| productNum | integer | 符合条件的商品总数（上游 `product_num`） |
| products | array | Temu 商品列表 |
| columns | array | 渲染的列 |
| title | string | 标题（`Temu 商品查询`） |
| sourceType | string | 来源类型：temu |
| sourceTool | string | 工具类型：ehunt |
| type | string | 渲染的样式：tableListWorkbenches |

#### products[] 商品对象

| 字段 | 类型 | 上游别名 | 说明 |
|------|------|----------|------|
| productId | 以实际响应为准 | `product_id` | 商品 ID |
| productName | 以实际响应为准 | `product_name` | 商品名（英文） |
| productNameCn | 以实际响应为准 | `product_name_cn` | 商品名（中文） |
| logoUrl | 以实际响应为准 | `logo_url` | 主图 URL |
| price | 以实际响应为准 | - | 价格 |
| orderTotal | 以实际响应为准 | `order_total` | 总销量 |
| orderWeek | 以实际响应为准 | `order_week` | 周销量 |
| orderDay | 以实际响应为准 | `order_day` | 日销量 |
| orderMonth | 以实际响应为准 | `order_month` | 月销量 |
| rating | 以实际响应为准 | - | 评分 |
| reviewNum | 以实际响应为准 | `review_num` | 评论数 |
| publishTime | 以实际响应为准 | `publish_time` | 上架时间 |
| soldOut | 以实际响应为准 | `sold_out` | 是否下架 |
| isLocal | 以实际响应为准 | `is_local` | 是否半托管：0=全托管，1=半托管 |
| localRegion | 以实际响应为准 | `local_region` | 半托管地区列表 |
| storeId | 以实际响应为准 | `store_id` | 店铺 ID |
| tags | 以实际响应为准 | - | 标签列表 |
| customTags | 以实际响应为准 | `custom_tags` | 自定义标签 |
| categoryHome | 以实际响应为准 | `category_home` | 前台类目 |
| categoryBackend | 以实际响应为准 | `category_backend` | 后台类目 |

#### 可选状态与脚本标记

| 字段 | 类型 | 说明 |
|------|------|------|
| code | 以实际响应为准 | 上游可能返回根级 code，成功值 200 以实际返回为准；不能替代公共响应码规则。 |
| errcode | integer / string / null | 存在时按公共响应码基本规则判断；0 和 false 不视为空。 |
| errmsg | string | 存在时用于解释网关错误原因。 |
| _http_status | integer | 业务脚本记录的实际 HTTP 状态，不是网关业务字段；与原始响应体一同保存、缓存。连接失败或已有缓存未记录状态时可能缺失。 |
| _cache.hit | boolean | 脚本在命中本地缓存时加入的标记，不是接口承诺返回的业务字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 无数据时网关可能抛错；只有正常响应且列表为空时才说明当前条件无匹配商品，不把错误响应直接解释成无商品。
- 根级 `code=200` 仅作上游状态线索，不以单个 `code` 值覆盖 HTTP 状态和 `errcode` 的基础判断。
- 使用脚本时，以 `_http_status` 配合 `errcode` 判断；即使错误体中的 `errcode` 为 200，HTTP 401/402 仍进入认证或算力引导，404 仍按路径错误处理。`error` / `details` 存在时保留其错误原因，不能解释为空商品列表。
- 缓存也可能保存错误响应；`_cache.hit=true` 时，`_http_status` 是缓存生成时的状态，不是本次请求状态。已有缓存缺少该字段时不能推断 HTTP 成功；需重新核验时，在用户授权范围内使用 `--no-cache`，不自动重试。
- 返回 404 时，可能是部署上的工具路径与默认路径不同。通过环境已提供的 `listEnabledTool` 元数据或运维确认实际路径后，设置 `LINKFOX_EHUNT_TEMU_PRODUCT_QUERY_PATH`；不要猜测路径反复请求。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ehunt/temu/productQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"searchKey":"kitchen","page":1,"pageSize":20}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-product-query",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
