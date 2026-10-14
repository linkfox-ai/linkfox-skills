# linkfox-kalodata-tiktok-livestream

带货直播榜单与直播详情用于 TikTok Shop 直播表现研究。rank 浏览地区/时间窗口榜单；detail 只接受已知 `livestreamId`，不能按标题搜索。

## MCP 调用规范

- MCP Server：`LinkFox`
- MCP URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- MCP 工具：`proxy_call`
- 精确 `toolName`：榜单为 `kalodata/livestream/rank`，详情为 `kalodata/livestream/detail`
- `arguments` 直接传原业务请求体，不增加 `headers`、`Authorization`、token 或其他认证字段；WorkBuddy 自动完成授权。
- 每次调用都可能产生积分消耗。默认不自动重试、不自动翻页、不因空结果改参数重复调用。
## 请求参数

### `POST /kalodata/livestream/rank`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 否 | 市场，如 `US`，最大长度 1000 |
| dateRange | string | 否 | 如 `last7Day`、`last30Day`，最大长度 1000 |
| pageNumber | integer | 否 | 1–5 |
| pageSize | integer | 否 | 5–100 |
| language | string | 否 | 如 `zh-CN`、`en-US` |
| currency | string | 否 | 如 `USD` |
| sortField | object | 否 | 网关定义的排序对象；`{}` 走默认顺序 |

默认按 `revenue`/GMV 降序；不支持关键词搜索，真实响应没有 `total`。

### `POST /kalodata/livestream/detail`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| livestreamId | string | 是 | 来自 rank `livestream_id` 的 ID，camelCase，保留字符串 |
| region | string | 否 | 如 `US` |
| dateRange | string | 否 | 如 `last7Day`、`last30Day` |
| language | string | 否 | 如 `zh-CN`、`en-US` |
| currency | string | 否 | 如 `USD` |

detail 无 `pageNumber`、`pageSize`、`sortField`，成功时 `data` 通常为 1 个元素。

## 响应结构

### 共有顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 直播榜单列表或直播详情数据 |
| costToken | integer | 本次调用扣费 token，固定 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

> ⚠️ 两个接口的响应都**不包含 `total`**，也没有总页数等分页元数据。直播榜单需翻页时持续请求下一页，直到某页返回条数少于 `pageSize` 或达到第 5 页；直播详情的 `data` 成功时恒为 1 元素数组。

### 直播榜单字段（`data` 数组中的每个元素）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 榜单数据元素 |
| `data[].livestream_start_time` | integer | 直播开始时间（epoch 毫秒） |
| `data[].livestream_end_time` | integer | 直播结束时间（epoch 毫秒） |
| `data[].livestream_duration` | integer | 直播时长（秒） |
| `data[].livestream_title` | string | 直播标题 |
| `data[].livestream_id` | string | 直播唯一 ID（字符串，避免大整数精度丢失）；可用作详情接口的 `livestreamId` |
| `data[].creator_id` | string | 达人唯一 ID（字符串，避免大整数精度丢失） |
| `data[].creator_handle` | string | 达人账号 handle |
| `data[].revenue` | string | 总销售额 / GMV（按请求的 `currency` 货币；**返回为字符串**，如 `"185590.52"`） |
| `data[].unit_price` | string | 件单价（按请求的 `currency` 货币；**返回为字符串**，如 `"265.89"`） |
| `data[].views` | integer | 观看数 |
| `data[].record_type` | string | 记录类型（如 `SHORT`） |

> **货币字段为字符串**：榜单接口的 `revenue` 与 `unit_price` 返回的是字符串（如 `"185590.52"`），不是数字，使用前需转换为数值类型（`float()` / `Number()` / `ConvertFrom-Json`）。默认按 `revenue`（GMV）降序排列。

### 直播详情字段（`data` 固定为 1 元素数组）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 详情数据元素 |
| `data[].livestream_id` | string | 直播唯一 ID（与请求的 `livestreamId` 一致） |
| `data[].livestream_title` | string | 直播标题（如 `24 HOUR STREAM`） |
| `data[].creator_id` | string | 达人唯一 ID（字符串，避免大整数精度丢失） |
| `data[].creator_handle` | string | 达人用户名/handle（如 `pokepiglt`） |
| `data[].livestream_start_time` | integer | 直播开始时间，epoch 毫秒（如 `1783810950000`） |
| `data[].livestream_end_time` | integer | 直播结束时间，epoch 毫秒（如 `1783898407000`） |
| `data[].livestream_duration` | integer | 直播时长，单位**秒**（如 `87457`） |
| `data[].record_type` | string | 记录类型（如 `SHORT`） |
| `data[].viewers` | integer | 观看人数（注意：DETAIL 用 `viewers`，RANK 用 `views`） |
| `data[].revenue` | number | 直播销售额 / GMV，**数字**类型，按请求的 `currency` 货币（如 `185590.52`）——注意：在直播 RANK 接口中 `revenue` 是字符串，此处为数字 |
| `data[].gpm` | number | GMV per mille（每千次展示 GMV），数字类型——DETAIL 独有，RANK 接口无此字段 |
| `data[].product_number` | integer | 直播带货商品数 |

> **与 RANK 接口的字段名/类型差异**：直播 DETAIL 接口使用 `viewers`（RANK 接口使用 `views`）；DETAIL 的 `revenue` 是**数字**（RANK 的 `revenue` 是**字符串**）；DETAIL 有 `gpm`（RANK 无），DETAIL 无 `unit_price`（RANK 有）。用 `jq`/`ConvertFrom-Json` 抽取时务必使用上方对应接口的字段名。

## MCP 调用示例

榜单：

```json
{
  "toolName": "kalodata/livestream/rank",
  "arguments": {"region":"US","dateRange":"last7Day","currency":"USD","language":"en-US","pageSize":10,"pageNumber":1,"sortField":{}}
}
```

详情：

```json
{
  "toolName": "kalodata/livestream/detail",
  "arguments": {"livestreamId":"7661409374878878494","region":"US","dateRange":"last7Day","currency":"USD"}
}
```

## 特殊规则与错误

- rank 不是直播关键词搜索；默认按 revenue 降序、无 rank 字段，顺序位置即隐含排名。满页时可继续下一页，最多第 5 页；若用户要完整榜单，以返回条数少于 `pageSize` 为停止信号。
- rank 的 `revenue`/`unit_price` 是字符串，比较或格式化前解析；detail 的 `revenue` 是数字。rank 使用 `views`，detail 使用 `viewers`；detail 有 `gpm`、无 `unit_price`。
- `errcode=501` 若为 Kalodata HTTP 554 上游错误，向用户说明后停止，只有用户明确同意时才可同参重试；页码越界按 1–5 修正，缺少 detail ID 时从 rank 的 `livestream_id` 取得。401/402 读取 `references/onboarding.md`，并先区分 MCP 层与下游业务层；不支持的 sortField 回退默认排序。
- 时间按 epoch 毫秒转换本地可读时间，时长按秒；标明 `dateRange`、`region`、`currency` 和可能的 T+1 延迟。

## Feedback API

用户反馈时可调用独立 `POST https://skill-api.linkfox.com/api/v1/public/feedback`：

```json
{"skillName":"linkfox-kalodata-tiktok-livestream","sentiment":"POSITIVE","category":"OTHER","content":"Results were accurate, user was satisfied."}
```

`sentiment` 为 `POSITIVE`/`NEUTRAL`/`NEGATIVE` 之一，`category` 为 `BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER` 之一。

