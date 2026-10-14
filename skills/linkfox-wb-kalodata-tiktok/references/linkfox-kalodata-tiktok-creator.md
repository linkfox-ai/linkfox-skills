# linkfox-kalodata-tiktok-creator

达人榜单与达人详情用于 TikTok Shop 达人发现、合作线索和带货表现分析。rank 负责发现达人；detail 只接受已知 `creatorId`，不按昵称或 handle 搜索。

## MCP 调用规范

- MCP Server：`LinkFox`
- MCP URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- MCP 工具：`proxy_call`
- 精确 `toolName`：榜单为 `kalodata/creator/rank`，详情为 `kalodata/creator/detail`
- `arguments` 直接传原业务请求体，不增加 `headers`、`Authorization`、token 或其他认证字段；WorkBuddy 自动完成授权。
- 每次调用都可能产生积分消耗。默认不自动重试、不自动翻页、不因空结果改参数重复调用。
## 请求参数

### `POST /kalodata/creator/rank`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 否 | 市场，如 `US` |
| dateRange | string | 否 | 如 `last7Day`、`last30Day` |
| pageNumber | integer | 否 | 1–5 |
| pageSize | integer | 否 | 5–100 |
| language | string | 否 | 如 `zh-CN`、`en-US` |
| currency | string | 否 | 如 `USD` |
| sortField | object | 否 | 排序条件；`{}` 走默认 revenue 排序 |

默认按 revenue/GMV 降序，无关键词搜索。

### `POST /kalodata/creator/detail`

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| creatorId | string | 是 | 来自 rank `creator_id` 的达人 ID，字符串传递 |
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

### 达人榜单字段（`data` 数组中的每个元素）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 榜单数据元素 |
| `data[].creator_nickname` | string | 达人昵称 |
| `data[].creator_handle` | string | TikTok 主页名，例如 `@based` |
| `data[].creator_id` | string | 达人唯一 ID，字符串格式以避免大整数精度丢失 |
| `data[].creator_followers` | string | 粉丝数，以字符串返回 |
| `data[].content_views` | string | 内容总观看数，以字符串返回 |
| `data[].sales_volumn` | integer | 销量，字段拼写为 `volumn` |
| `data[].revenue` | number | 总销售额 / GMV，按请求的 `currency` 返回 |
| `data[].video_revenue` | number | 短视频带货销售额 |
| `data[].live_revenue` | number | 直播带货销售额 |
| `data[].revenue_growth_rate` | number | 销售额增长率（%），可正可负 |

> `outputSchema` 可能声明 `total` 字段，但真实响应不包含 `total`，也没有总页数等分页元数据。需要翻页时持续请求下一页，直到某页返回条数少于 `pageSize`。

### 达人详情字段（`data` 固定为 1 元素数组）

| 字段路径 | 类型 | 说明 |
|------|------|------|
| `data[]` | object | 详情数据元素 |
| `data[].creator_id` | string | 达人唯一 ID |
| `data[].creator_nickname` | string | 达人昵称 |
| `data[].creator_handle` | string | 达人 handle |
| `data[].creator_region` | string | 达人地区 |
| `data[].creator_status` | string | 达人状态 |
| `data[].creator_bio` | string | 达人简介 |
| `data[].creator_belonged_shop_id` | string | 所属店铺 ID |
| `data[].creator_followers` | string | 粉丝总数，以字符串返回 |
| `data[].new_followers` | integer | `dateRange` 窗口内新增粉丝 |
| `data[].revenue` | number | 总销售额 / GMV |
| `data[].video_revenue` | number | 视频销售额 |
| `data[].live_revenue` | number | 直播销售额 |
| `data[].sales_volumn` | integer | 销量，字段拼写为 `volumn` |
| `data[].unit_price` | number | 件单价 |
| `data[].video_number` | integer | 窗口内视频数 |
| `data[].video_views` | integer | 视频总播放量 |
| `data[].video_gpm` | number | 视频 GPM |
| `data[].live_number` | integer | 窗口内直播数 |
| `data[].live_views` | integer | 直播总观看量 |
| `data[].live_gpm` | number | 直播 GPM |
| `data[].product_number` | integer | 关联商品数 |
| `data[].shop_number` | integer | 关联店铺数 |
| `data[].creator_contact_email` | string | 联系邮箱 |
| `data[].creator_contact_ins` | string | Instagram 联系方式 |
| `data[].creator_contact_whatsapp` | string | WhatsApp 联系方式 |
| `data[].creator_contact_facebook` | string | Facebook 联系方式 |
| `data[].creator_contact_tiktok` | string | TikTok 联系方式 |
| `data[].creator_contact_zalo` | string | Zalo 联系方式 |
| `data[].creator_contact_line` | string | Line 联系方式 |

> `data` 对于有效 `creatorId` 通常为 1 元素数组。详情响应不包含 `total` 字段。

## MCP 调用示例

榜单：

```json
{
  "toolName": "kalodata/creator/rank",
  "arguments": {"region":"US","dateRange":"last7Day","currency":"USD","pageSize":10,"pageNumber":1,"sortField":{}}
}
```

详情：

```json
{
  "toolName": "kalodata/creator/detail",
  "arguments": {"creatorId":"7153432386608251946","region":"US","dateRange":"last7Day","currency":"USD"}
}
```

## 特殊规则与错误

- 榜单按市场/时间浏览，不是昵称、handle 或关键词搜索；没有 `total` 时按 `data.length` 判断分页，最多第 5 页。
- `creator_followers`、`content_views` 是字符串，比较前解析；所有销量使用 `sales_volumn`。空联系方式表示未提供，不应编造或输出空的联系方式组。
- 501 若指向 Kalodata HTTP 554 上游错误，向用户说明后停止；只有用户明确同意时才可同参重试。页码越界或 `creatorId` 缺失/无效按 `errmsg` 修正。
- 401/402 读取 `references/onboarding.md`，并先区分 MCP 层与下游业务层；不支持的 sortField 回退默认 revenue 排序，不试探其他字段。数据可能 T+1，金额标明币种/地区/时间窗。
-

## Feedback API

用户反馈时可调用独立 `POST https://skill-api.linkfox.com/api/v1/public/feedback`：

```json
{"skillName":"linkfox-kalodata-tiktok-creator","sentiment":"POSITIVE","category":"OTHER","content":"Results were accurate, user was satisfied."}
```

`sentiment` 为 `POSITIVE`/`NEUTRAL`/`NEGATIVE` 之一，`category` 为 `BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER` 之一。
