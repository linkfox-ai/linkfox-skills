# Temu 店铺查询 接口说明

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

## 接口：Temu 店铺查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/temu/storeQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string, maxLen=500 | 否 | 店铺名称或 ID 关键词 |
| siteId | string | 否 | 国家站点 ID，多个逗号分隔（如 211=美国，76=英国） |
| category | string | 否 | 后台类目 ID，多个逗号分隔 |
| isLocal | string | 否 | 是否半托管：0=全托管，1=半托管 |
| orderTotalMin | integer，≥0 | 否 | 总销量区间（起始） |
| orderTotalMax | integer，≥0 | 否 | 总销量区间（结束） |
| orderWeekMin | integer，≥0 | 否 | 周销量区间（起始） |
| orderWeekMax | integer，≥0 | 否 | 周销量区间（结束） |
| orderMonthMin | integer，≥0 | 否 | 月销量区间（起始） |
| orderMonthMax | integer，≥0 | 否 | 月销量区间（结束） |
| totalRevenueMin | number，≥0 | 否 | 总销售额区间（USD，起始） |
| totalRevenueMax | number，≥0 | 否 | 总销售额区间（USD，结束） |
| weekRevenueMin | number，≥0 | 否 | 周销售额区间（USD，起始） |
| weekRevenueMax | number，≥0 | 否 | 周销售额区间（USD，结束） |
| monthRevenueMin | number，≥0 | 否 | 月销售额区间（USD，起始） |
| monthRevenueMax | number，≥0 | 否 | 月销售额区间（USD，结束） |
| ratingMin | number (0~5) | 否 | 评分区间（起始） |
| ratingMax | number (0~5) | 否 | 评分区间（结束） |
| reviewNumMin | integer，≥0 | 否 | 评论数区间（起始） |
| reviewNumMax | integer，≥0 | 否 | 评论数区间（结束） |
| followerNumMin | integer，≥0 | 否 | 粉丝数区间（起始） |
| followerNumMax | integer，≥0 | 否 | 粉丝数区间（结束） |
| productNumMin | integer，≥0 | 否 | 商品数区间（起始） |
| productNumMax | integer，≥0 | 否 | 商品数区间（结束） |
| listedTimeBegin | string (YYYY-MM-DD) | 否 | 开店日期区间（起始） |
| listedTimeEnd | string (YYYY-MM-DD) | 否 | 开店日期区间（结束） |
| sortBy | string | 否 | 排序字段+方向：`order_week_count-0`（周销量降序，默认）、`order_count-0`、`total_revenue-0`、`rating-0` |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100 |

#### 参数约束与使用限制

- 请求体为 JSON，与 MCP 入参一致；MCP 展示名为“Temu 店铺查询”，确切工具名以当前环境工具元数据为准，鉴权和上游路由由网关处理。
- 各组 `*Min` / `*Max` 成对传入，组成上游区间：总/周/月销量、总/周/月销售额、评分、评论数、粉丝数、商品数。
- 站点与后台类目编号均使用字符串，多个编号用逗号分隔；`isLocal` 也使用字符串，保留 `"0"` / `"1"` 的约定。
- `sortBy` 使用“字段-方向”字符串，支持表中列出的示例；完整排序取值范围需核实，不自行扩展约定。
- 每页最多 100 条；分页是独立查询，按本页返回店铺数计费，不按 `storeNum` 计费。

#### 脚本选项与运行约定

| 参数 / 配置 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 命令行第一个位置参数，字段见上表，按原值传给网关。 |
| --inline | CLI flag | 否 | 强制完整打印，同时仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过缓存读取和写入；默认使用 24 小时缓存。 |
| --help / -h | CLI flag | 否 | 显示本地帮助，不发请求。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 首选网关根地址，默认 `https://tool-gateway.linkfox.com`。 |
| LINKFOX_TOOL_GATEWAY_BASE | 环境变量 | 否 | 网关根地址兼容别名；主变量为空时使用，自动去除末尾 `/`。 |
| LINKFOX_EHUNT_TEMU_STORE_QUERY_PATH | 环境变量 | 否 | 请求路径覆盖，默认 `ehunt/temu/storeQuery`；仅路径，不含域名，自动补齐开头 `/`。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是 | 支持两种名称，前者优先；作为原值写入 Authorization，不添加 Bearer 前缀。 |
| SESSION_ID | 环境变量 | 否 | 聚合同一任务的会话数据；未提供时自动生成会话标识。会话目录必须位于当前工作目录的当日输出目录内，不得通过绝对路径或父目录跳转越界。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 与 SESSION_ID 一起透传同名请求头，未配置时为空字符串。 |

业务入口为 `scripts/temu_store_query.py`（Python 3，仅标准库），经公共 `scripts/call_api.py` 的 `run` 调用，不另建 HTTP 或缓存层。缓存目录为 `<cwd>/linkfox/.cache/linkfox-temu-store-query/`，文件键为参数按键排序后的 SHA-256 前 16 位，有效期为 24 小时，命中时添加命中标记；键不包含密钥或地址，相同参数在有效期内可命中缓存。`--no-cache` 不复用也不更新响应缓存。

完整响应以 UTF-8 保存到当前工作目录的会话数据目录，更新 `_meta.json` 和 `index.jsonl`，并保留完整输出、摘要和 `--inline` 行为。业务封装在请求前检查输出根目录、实际会话数据目录及元数据初始化；目录冲突、不可写或路径越界时直接报错，不发起业务请求。不回退到家目录、临时目录或 `ACPX_WORKSPACES`；禁止以 `/tmp` 为输出位置。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| storeNum | integer | 符合条件的店铺总数（上游 `store_num`） |
| stores | array | Temu 店铺列表 |
| columns | array | 渲染的列 |
| title | string | 标题（`Temu 店铺查询`） |
| sourceType | string | 来源类型：temu |
| sourceTool | string | 工具类型：ehunt |
| type | string | 渲染的样式：tableListWorkbenches |
| code | 以实际返回为准 | 上游根级返回码，不保证固定存在；如返回则保留实际值，判断方式见响应码规则。 |

`columns` 的元素结构以实际返回为准，不预设子字段。参数和返回结构以当前网关实际返回为准，判断是否正常仍遵循下方基础规则。

#### stores[*] 店铺对象

下表列出店铺字段及上游别名；字段类型以实际返回为准，不强制转换。

| 字段 | 类型 | 上游别名 | 说明 |
|------|------|----------|------|
| storeId | 以实际返回为准 | `store_id` | 店铺 ID |
| siteId | 以实际返回为准 | `site_id` | 国家站点 ID |
| storeName | 以实际返回为准 | `store_name` | 店铺名称 |
| logoUrl | 以实际返回为准 | `logo_url` | 店铺 Logo URL |
| orderTotal | 以实际返回为准 | `order_total` | 总销量 |
| orderWeek | 以实际返回为准 | `order_week` | 周销量 |
| orderMonth | 以实际返回为准 | `order_month` | 月销量 |
| totalRevenue | 以实际返回为准 | `total_revenue` | 总销售额 |
| weekRevenue | 以实际返回为准 | `week_revenue` | 周销售额 |
| monthRevenue | 以实际返回为准 | `month_revenue` | 月销售额 |
| rating | 以实际返回为准 | - | 评分 |
| listedTime | 以实际返回为准 | `listed_time` | 开店时间 |
| reviewNum | 以实际返回为准 | `review_num` | 评论数 |
| followerNum | 以实际返回为准 | `follower_num` | 粉丝数 |
| productNum | 以实际返回为准 | `product_num` | 商品数 |
| categoriesCn | 以实际返回为准 | `categories_cn` | 中文类目列表 |
| categories | 以实际返回为准 | - | 英文类目列表 |
| isLocal | 以实际返回为准 | `is_local` | 是否半托管：0=全托管，1=半托管 |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer | 业务脚本为对象响应保留的实际 HTTP 状态，包含 JSON 错误响应；不是网关响应字段。未收到 HTTP 响应时不生成。 |
| _cache.hit | boolean | 为 `true` 时表示本地缓存命中，此时 `_http_status` 是生成缓存时的历史状态，本次未发请求；旧缓存可能没有状态字段，不推断其值。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。
- 脚本返回时，通过本地 `_http_status` 核对 HTTP 状态，并结合 `errcode` 与错误内容判断；不能因 JSON 错误响应缺少 `errcode` 就当作正常响应。缓存命中只说明历史响应，不能据此断言当前认证或余额状态；如用户需要在处理认证或余额后重新查询，说明额外消耗并使用 `--no-cache`，避免复用错误缓存。

#### 业务规则

- 上游根级 `code` 可能以 `200` 表示成功，但其类型和实际值须核对网关返回；它不替代基础规则，也不能单凭该值判定成功。
- 无数据时网关可能抛错，保留错误内容，不将错误直接改写为空列表；仅在正常响应下结合本页计数和店铺列表说明空结果。
- 返回 404 时，核对当前部署的工具 HTTP 路径；可通过 `listEnabledTool` 或运维确认实际 path，再按已确认路径设置 `LINKFOX_EHUNT_TEMU_STORE_QUERY_PATH`。不得自动试探多个路径产生额外请求。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/ehunt/temu/storeQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"searchKey":"home","siteId":"211","page":1,"pageSize":20}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-store-query",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```