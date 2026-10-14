# linkfox-kalodata-tiktok-video

带货视频榜单与视频详情用于 TikTok Shop 内容选品和表现研究。rank 支持 GMV 范围过滤；detail 只接受已知 `videoId`，不按标题搜索。

## MCP 调用规范

- MCP Server：`LinkFox`
- MCP URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- MCP 工具：`proxy_call`
- 精确 `toolName`：榜单为 `kalodata/video/rank`，详情为 `kalodata/video/detail`
- `arguments` 直接传原业务请求体，不增加 `headers`、`Authorization`、token 或其他认证字段；WorkBuddy 自动完成授权。
- 每次调用都可能产生积分消耗。默认不自动重试、不自动翻页、不因空结果改参数重复调用。
## 请求参数

### `POST /kalodata/video/rank`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 否 | 市场，如 `US` |
| dateRange | string | 否 | 如 `last7Day`、`last30Day` |
| pageNumber | integer | 否 | 1–5 |
| pageSize | integer | 否 | 5–100 |
| language | string | 否 | 如 `zh-CN`、`en-US` |
| currency | string | 否 | 如 `USD` |
| revenue_range | string | 否 | GMV 范围，如 `1-100`、`>1000`、`<100` |
| sortField | object | 否 | GMV 排序，如 `{"field":"revenue","type":"DESC"}` |

rank 是榜单浏览，不支持关键词视频搜索；`revenue` 是总 GMV，不是利润或广告花费。

### `POST /kalodata/video/detail`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| videoId | string | 是 | 视频 ID，来自 rank `video_id`，也可为 TikTok 视频 URL |
| region | string | 否 | 如 `US` |
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

### 视频榜单字段（`data` 数组中的每个元素）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 榜单数据元素 |
| `data[].video_id` | string | 视频 ID，字符串格式以避免大整数精度丢失 |
| `data[].video_title` | string | 视频标题 / 文案 |
| `data[].views` | integer | 播放量 |
| `data[].digg_count` | integer | 点赞数 |
| `data[].comment_count` | integer | 评论数 |
| `data[].share_count` | integer | 分享数 |
| `data[].revenue` | number | 总销售额 / GMV，按请求的 `currency` 返回 |
| `data[].revenue_growth_rate` | number | 销售额增长率（%），可正可负 |
| `data[].ad` | integer | 是否广告/带货视频标识（1=是） |
| `data[].ad_view_ratio` | number | 广告播放占比（%） |
| `data[].ad_revenue_ratio` | number | 广告带来的销售额占比（%） |
| `data[].ads_roas` | number | 广告 ROAS |
| `data[].belonged_creator_id` | string | 所属达人 ID |
| `data[].belonged_creator_handle` | string | 所属达人用户名 |
| `data[].creator_debut` | string | 达人入驻日期（`YYYY-MM-DD`） |

> 真实响应不包含 `total`，也没有总页数等分页元数据。需要翻页时持续请求下一页，直到某页返回条数少于 `pageSize` 或达到第 5 页。

### 视频详情字段（`data` 固定为 1 元素数组）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 详情数据元素 |
| `data[].video_id` | string | 视频 ID，字符串格式以避免大整数精度丢失 |
| `data[].video_title` | string | 视频标题 / 文案 |
| `data[].video_region` | string | 视频地区，可能为空字符串 |
| `data[].belonged_creator_id` | string | 归属达人 ID |
| `data[].belonged_creator_handle` | string | 归属达人用户名 |
| `data[].views` | integer | 播放量 |
| `data[].digg_count` | integer | 点赞数 |
| `data[].comment_count` | integer | 评论数 |
| `data[].share_count` | integer | 分享数 |
| `data[].revenue` | number | 总销售额 / GMV |
| `data[].sales_volumn` | integer | 销量，字段拼写为 `volumn` |
| `data[].video_gpm` | number | 视频 GPM（每千次播放 GMV） |
| `data[].ad` | integer | 是否投放广告（1=有广告，0=无广告） |
| `data[].ads_views` | integer | 广告播放数 |
| `data[].ads_roas` | number | 广告 ROAS |
| `data[].ad_cpa` | number | 广告 CPA |
| `data[].ad_view_ratio` | number | 广告播放占比（%） |
| `data[].ads_period` | integer | 广告投放周期（天） |
| `data[].duration` | number | 视频时长（秒） |
| `data[].product_number` | integer | 视频关联商品数 |

> `data` 对于有效 `videoId` 通常为 1 元素数组。详情响应不包含 `total` 字段。

## MCP 调用示例

榜单：

```json
{
  "toolName": "kalodata/video/rank",
  "arguments": {"region":"US","dateRange":"last7Day","revenue_range":"1-1000","sortField":{"field":"revenue","type":"DESC"},"pageSize":10,"pageNumber":1,"currency":"USD"}
}
```

详情：

```json
{
  "toolName": "kalodata/video/detail",
  "arguments": {"videoId":"7659161409279806734","region":"US","dateRange":"last7Day","currency":"USD"}
}
```

## 特殊规则与错误

- rank 不支持关键词/标题搜索；没有总页数时按 `data.length` 分页，`pageNumber` 1–5、`pageSize` 5–100。
- detail 必须有 `videoId`；不能只用标题定位。`revenue_range` 过滤的是总 GMV；`revenue_growth_rate` 与广告比例均按百分比展示。
- 501 若 `errmsg` 含 Kalodata HTTP 554，向用户说明后停止，只有用户明确同意时才可同参重试；videoId 缺失/无效时核对 rank 的 `video_id`。401/402 读取 `references/onboarding.md`，并先区分 MCP 层与下游业务层，其他错误透传 errmsg。
- `video_gpm` 是每千次播放 GMV，不是百分比；`sales_volumn` 必须按原字段抽取。

## Feedback API

用户反馈时可调用独立 `POST https://skill-api.linkfox.com/api/v1/public/feedback`：

```json
{"skillName":"linkfox-kalodata-tiktok-video","sentiment":"POSITIVE","category":"OTHER","content":"Results were accurate, user was satisfied."}
```

`sentiment` 为 `POSITIVE`/`NEUTRAL`/`NEGATIVE` 之一，`category` 为 `BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER` 之一。

