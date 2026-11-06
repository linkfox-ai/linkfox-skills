# Shopify 店铺查询 接口说明

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

## 接口：Shopify 店铺查询

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ehunt/shopify/storeQuery`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKey | string, maxLen=500 | 否 | 店铺名称或域名关键词 |
| country | string | 否 | 国家代码（如 US、CN） |
| year | integer | 否 | 店铺创建年份：1=最近 1 年，2=1~2 年，3=2~3 年，4=3 年以上 |
| productNumMin | integer，≥0 | 否 | 产品数区间（起始） |
| productNumMax | integer，≥0 | 否 | 产品数区间（结束） |
| advertiseCountMin | integer，≥0 | 否 | 广告数区间（起始） |
| advertiseCountMax | integer，≥0 | 否 | 广告数区间（结束） |
| monthlyVisitMin | integer，≥0 | 否 | 月访问量区间（起始） |
| monthlyVisitMax | integer，≥0 | 否 | 月访问量区间（结束） |
| monthOrderMin | integer，≥0 | 否 | 月订单量区间（起始） |
| monthOrderMax | integer，≥0 | 否 | 月订单量区间（结束） |
| sortBy | integer | 否 | 排序字段：0=产品数,1=类目数,2=月访问量,3=FB 粉丝,4=Ins 粉丝,5=广告数,6=相关度,7=月订单数（默认） |
| orderBy | string | 否 | 排序方向：`desc`（默认）/`asc` |
| page | integer，≥1，默认 1 | 否 | 页码（从 1 开始） |
| pageSize | integer，1~100，默认 20 | 否 | 每页条数，最大 100 |

#### 参数约定

- `productNumMin` / `productNumMax`、`advertiseCountMin` / `advertiseCountMax`、`monthlyVisitMin` / `monthlyVisitMax`、`monthOrderMin` / `monthOrderMax` 必须分别成对出现，组成上游区间。
- `year` 表示店铺创建年限档位，不是公历年份。
- 本接口未定义社媒粉丝数区间入参；可按粉丝指标排序。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 本页返回条数 |
| storeNum | integer | 符合条件的店铺总数（上游 `store_num`） |
| stores | array | Shopify 店铺列表 |
| columns | array | 渲染的列 |
| title | string | 标题（`Shopify 店铺查询`） |
| sourceType | string | 来源类型：shopify |
| sourceTool | string | 工具类型：ehunt |
| type | string | 渲染的样式：tableListWorkbenches |

#### stores[] 店铺对象

| 字段 | 类型 | 上游别名 | 说明 |
|------|------|----------|------|
| storeId | 以实际返回为准 | `store_id` | 店铺 ID |
| shopId | 以实际返回为准 | `shop_id` | Shopify shop ID |
| storeName | 以实际返回为准 | `store_name` | 店铺名称 |
| storeDomain | 以实际返回为准 | `store_domain` | 店铺域名 |
| storeLink | 以实际返回为准 | `store_link` | 店铺链接 |
| country | 以实际返回为准 | - | 国家 |
| createdTime | 以实际返回为准 | `created_time` | 创建时间 |
| productNum | 以实际返回为准 | `product_num` | 产品数 |
| categoryNum | 以实际返回为准 | `category_num` | 类目数 |
| categories | array | - | 类目列表（元素含 `id`、`name`） |
| monthlyVisit | 以实际返回为准 | `monthly_visit` | 月访问量（格式化） |
| monthOrderNum | 以实际返回为准 | `month_order_num` | 月订单量（格式化） |
| fbFollowers | 以实际返回为准 | `fb_followers` | Facebook 粉丝数 |
| insFollowers | 以实际返回为准 | `ins_followers` | Instagram 粉丝数 |
| advertiseCount | 以实际返回为准 | `advertise_count` | 广告数 |
| adLink | 以实际返回为准 | `ad_link` | 广告库链接 |
| email | 以实际返回为准 | - | 联系邮箱 |
| facebookUrl | 以实际返回为准 | `facebook_url` | Facebook 主页 |
| instagramUrl | 以实际返回为准 | `instagram_url` | Instagram 主页 |
| socialLinks | object（Map） | `social_links` | 社媒链接（Map） |
| globalRank | 以实际返回为准 | `global_rank` | 全球排名 |
| logo | 以实际返回为准 | - | 店铺 Logo URL |
| availableStatus | 以实际返回为准 | `available_status` | 是否活跃：1=活跃 |

#### categories[] 类目对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | 以实际返回为准 | 类目 ID，保留实际返回值。 |
| name | 以实际返回为准 | 类目名称，保留实际返回值。 |

#### socialLinks 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| 动态键 | 以实际返回为准 | 社媒链接 Map；键名与各值的具体类型以实际返回为准。 |

#### 可出现的状态字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 如返回，按公共规则判断；不将 0 或 false 视为空。 |
| errmsg | string | 如返回，用于解释具体原因。 |
| code | 以实际返回为准 | 上游可能在根级返回，成功值可能为 200；以实际响应为准，不代替公共规则。 |

店铺对象的标量字段、类目字段及社媒链接值的具体 JSON 类型以实际返回为准；不预设 ID、格式化数值或状态字段的类型。参数与返回结构以当前网关实际返回为准。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 脚本返回对象中的 `_http_status` 是业务封装记录的实际 HTTP 状态，不是网关字段；HTTP 非 2xx 时，即使 JSON 错误体没有 `errcode` 或其中的值为 2xx，也不能判为成功。原始响应字段及错误原因仍保留。
- 缓存命中时，`_http_status`（如有）是缓存生成时的状态，不表示本次发出了请求；旧缓存可能没有该字段，不能据此推断 HTTP 成功。连接失败未取得 HTTP 响应时也没有该字段，按 `error` 解释。
- 无数据时网关可能抛错，应结合具体消息解释；不能仅凭失败断言不存在店铺。
- 成功但列表为空时，说明本次条件下未返回店铺，不自动放宽条件或连续请求。
- `total` 为本页返回条数，`storeNum`（上游 `store_num`）为符合条件的店铺总数。

### 使用限制与计费

- 消耗算力 = 本页返回的店铺数 × 1.8。翻到下一页是新请求，按下一页返回条数重新计算，不按 `storeNum` 总数一次计费。
- 例如返回 20 家店铺时，预估 36 算力；每页最大 100 家时，单页可达 180 算力，以实际扣除为准。
- 本服务按倍数动态计算，可能一次性消耗大量算力，必须提醒用户，由用户决定是否继续；不能因为只读查询而省略提醒。
- 不为失败或空结果自动更换条件、翻页或连续试探；额外请求前说明费用并由用户决定。

### 脚本运行约定

仅需 Python 3 和标准库。业务脚本通过本目录 `scripts/call_api.py` 的 `run` 执行请求、缓存和输出，不另建 HTTP transport 或第二层缓存。

| 配置或选项 | 约定 |
|------------|------|
| JSON 参数 | `python scripts/shopify_store_query.py '<JSON 参数>' [--inline] [--no-cache]`，传入与接口相同的 JSON。 |
| LINKFOX_TOOL_GATEWAY | 网关根地址，优先级最高；默认 `https://tool-gateway.linkfox.com`。 |
| LINKFOX_TOOL_GATEWAY_BASE | 网关根地址变量，仅在 `LINKFOX_TOOL_GATEWAY` 为空时使用。 |
| LINKFOX_EHUNT_SHOPIFY_STORE_QUERY_PATH | 接口路径覆盖变量，传相对路径，默认 `/ehunt/shopify/storeQuery`，缺少开头 `/` 时自动补齐。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 前者优先，后者兼容；均为空时按 `onboarding.md` 处理。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 将对应环境变量透传为同名请求头。会话标识同时用于输出聚合。 |
| 默认缓存 | TTL 为 24 小时，路径 `<cwd>/linkfox/.cache/linkfox-shopify-store-query/linkfox-shopify-store-query-<参数摘要>.json`；参数经排序 JSON 后取 SHA-256 前 16 位，可复用该路径下尚未过期的缓存。 |
| --no-cache | 不读取、不写入响应缓存，但公共调用器仍可能创建缓存目录；照常请求并落盘完整结果。 |
| 缓存命中 | 响应增加 `_cache.hit=true`，仍保存输出；缓存不区分失败响应与成功响应，必要时由用户决定是否禁用缓存重查。 |
| --inline | 始终全量打印，仍保存完整响应；默认不超过 8000 UTF-8 字节时全量输出，超过时输出摘要与最大列表前 3 条样本。 |
| 输出目录 | 从可写的任务工作目录运行。业务封装在请求前检查 `<cwd>/linkfox/` 可写并固定输出根目录；不可写或位于 `/tmp` 下时直接报错，不发起请求。不受 `ACPX_WORKSPACES` 或公共调用器已缓存的根目录影响，不回退到用户目录或临时目录。 |
| 会话文件 | 完整结果保存到 `<cwd>/linkfox/<日期>/<SESSION_ID 或自动标识>/data/linkfox-shopify-store-query-<微秒时间戳>.json`，避免同一秒内的响应相互覆盖；同步保留 `_meta.json` 与 `index.jsonl` 登记。 |

返回 404 时，不连续试探路径；可通过环境可用的 `listEnabledTool` 或运维确认实际路径后，再由用户决定是否设置路径覆盖重查。MCP 展示名为「Shopify 店铺查询」，确切工具名以当前环境下发的工具元数据为准。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/ehunt/shopify/storeQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"searchKey":"fashion","country":"US","page":1,"pageSize":20}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopify-store-query",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```