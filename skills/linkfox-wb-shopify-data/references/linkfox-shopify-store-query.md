# Shopify 店铺查询 reference

## 能力说明与边界

按店铺名称或域名、国家、创建年限、产品数、广告数、月访问量、月订单量和排序筛选 Shopify 店铺。

- `page` 从 1 起；`pageSize` 默认 20、最大 100。
- `*Min` / `*Max` 组成产品数、广告数、月访问量和月订单量区间；只填一侧时由上游解释为开放区间。
- `year`：`1=最近 1 年`、`2=1~2 年`、`3=2~3 年`、`4=3 年以上`。
- `sortBy`：`0=产品数`、`1=类目数`、`2=月访问量`、`3=FB 粉丝`、`4=Ins 粉丝`、`5=广告数`、`6=相关度`、`7=月订单数`；`orderBy` 默认为 `desc`。
- 返回当前市场快照，不提供后台操作、历史趋势或经营保证；失败或空结果不得自动改词、翻页或改变参数。

### 计费

动态计费为“本页返回店铺数 × 1.8 积分”。翻页会重新计费，实际以响应中的消耗和当前计费规则为准；高频或大页查询先由用户决定。

## MCP 调用

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- `toolName`：`ehunt/shopify/storeQuery`
- `arguments`：直接使用下述请求对象，不增加包装层。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 禁止 HTTP fallback。同一任务内相同 `toolName + arguments` 只调用一次；收费调用失败、空结果或不理想时不得自动重试。
- 先检查 MCP 层，再检查代理层；代理结果中的 text 是 JSON 字符串时只解析一次，最后检查下游业务状态。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `searchKey` | string, maxLen=500 | 否 | 店铺名称或域名关键词 |
| `country` | string | 否 | 国家代码，如 `US`、`CN` |
| `year` | integer | 否 | 创建年限：`1=最近 1 年`、`2=1~2 年`、`3=2~3 年`、`4=3 年以上` |
| `productNumMin` | integer，≥0 | 否 | 产品数区间起始 |
| `productNumMax` | integer，≥0 | 否 | 产品数区间结束 |
| `advertiseCountMin` | integer，≥0 | 否 | 广告数区间起始 |
| `advertiseCountMax` | integer，≥0 | 否 | 广告数区间结束 |
| `monthlyVisitMin` | integer，≥0 | 否 | 月访问量区间起始 |
| `monthlyVisitMax` | integer，≥0 | 否 | 月访问量区间结束 |
| `monthOrderMin` | integer，≥0 | 否 | 月订单量区间起始 |
| `monthOrderMax` | integer，≥0 | 否 | 月订单量区间结束 |
| `sortBy` | integer | 否 | `0=产品数`、`1=类目数`、`2=月访问量`、`3=FB 粉丝`、`4=Ins 粉丝`、`5=广告数`、`6=相关度`、`7=月订单数` |
| `orderBy` | string | 否 | `desc`（默认）或 `asc` |
| `page` | integer，≥1，默认 1 | 否 | 页码，从 1 开始 |
| `pageSize` | integer，1~100，默认 20 | 否 | 每页条数，最大 100 |

## 完整 MCP 示例

```json
{
  "toolName": "ehunt/shopify/storeQuery",
  "arguments": {
    "searchKey": "fashion",
    "country": "US",
    "year": 2,
    "sortBy": 2,
    "orderBy": "desc",
    "page": 1,
    "pageSize": 20
  }
}
```

## 响应字段

字段定义仅来自 `skills/linkfox-shopify-store-query/references/api.md` 的响应部分。来源未给 `stores[]` 字段类型列，只有明确为列表或 Map 的字段使用来源类型，其余均标记为“来源未说明”。

| 字段路径 | 类型 | 上游别名 | 说明 |
|---|---|---|---|
| `total` | integer | — | 本页返回条数 |
| `storeNum` | integer | `store_num` | 符合条件的店铺总数（上游 `store_num`） |
| `stores` | array | — | Shopify 店铺列表 |
| `stores[]` | object | — | Shopify 店铺列表元素；来源以元素字段表定义为对象 |
| `columns` | array | — | 渲染的列 |
| `columns[]` | 来源未说明 | — | 渲染列元素；来源未说明元素结构 |
| `title` | string | — | 标题（`Shopify 店铺查询`） |
| `sourceType` | string | — | 来源类型：shopify |
| `sourceTool` | string | — | 工具类型：ehunt |
| `type` | string | — | 渲染的样式：tableListWorkbenches |
| `stores[].storeId` | 来源未说明 | `store_id` | 店铺 ID |
| `stores[].shopId` | 来源未说明 | `shop_id` | Shopify shop ID |
| `stores[].storeName` | 来源未说明 | `store_name` | 店铺名称 |
| `stores[].storeDomain` | 来源未说明 | `store_domain` | 店铺域名 |
| `stores[].storeLink` | 来源未说明 | `store_link` | 店铺链接 |
| `stores[].country` | 来源未说明 | - | 国家 |
| `stores[].createdTime` | 来源未说明 | `created_time` | 创建时间 |
| `stores[].productNum` | 来源未说明 | `product_num` | 产品数 |
| `stores[].categoryNum` | 来源未说明 | `category_num` | 类目数 |
| `stores[].categories` | array | - | 类目列表（元素含 `id`、`name`） |
| `stores[].categories[]` | object | - | 类目列表元素；来源明确元素含字段，但未说明类型 |
| `stores[].categories[].id` | 来源未说明 | - | 类目元素的 `id`；来源未说明类型和具体含义 |
| `stores[].categories[].name` | 来源未说明 | - | 类目元素的 `name`；来源未说明类型和具体含义 |
| `stores[].monthlyVisit` | 来源未说明 | `monthly_visit` | 月访问量（格式化） |
| `stores[].monthOrderNum` | 来源未说明 | `month_order_num` | 月订单量（格式化） |
| `stores[].fbFollowers` | 来源未说明 | `fb_followers` | Facebook 粉丝数 |
| `stores[].insFollowers` | 来源未说明 | `ins_followers` | Instagram 粉丝数 |
| `stores[].advertiseCount` | 来源未说明 | `advertise_count` | 广告数 |
| `stores[].adLink` | 来源未说明 | `ad_link` | 广告库链接 |
| `stores[].email` | 来源未说明 | - | 联系邮箱 |
| `stores[].facebookUrl` | 来源未说明 | `facebook_url` | Facebook 主页 |
| `stores[].instagramUrl` | 来源未说明 | `instagram_url` | Instagram 主页 |
| `stores[].socialLinks` | object | `social_links` | 社媒链接（Map） |
| `stores[].globalRank` | 来源未说明 | `global_rank` | 全球排名 |
| `stores[].logo` | 来源未说明 | - | 店铺 Logo URL |
| `stores[].availableStatus` | 来源未说明 | `available_status` | 是否活跃：1=活跃 |

## 错误与展示

下游根级 `code=200` 可表示成功，具体以实际响应为准；错误时读取业务状态和消息。401、402、403 分别按 `onboarding.md` 的授权、计费和权限规则处理。无数据或其他异常时停止，不自动重试。

展示查询范围、本页条数、`storeNum`、分页和消耗；优先展示名称、域名、国家、创建时间、产品/类目数、月访问量、月订单量、社媒指标、广告数和活跃状态。格式化值按原样保留，缺失字段标记 N/A。

## Feedback API

反馈接口与店铺查询 MCP 独立：`POST https://skill-api.linkfox.com/api/v1/public/feedback`。使用统一 `skillName=linkfox-wb-shopify-data`；`sentiment` 为 `POSITIVE`/`NEUTRAL`/`NEGATIVE`，`category` 为 `BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`，`content` 简述意图、结果和原因。反馈不得中断当前流程或包含敏感信息。
