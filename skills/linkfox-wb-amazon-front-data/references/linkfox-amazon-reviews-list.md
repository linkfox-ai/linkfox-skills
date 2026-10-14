# `linkfox-amazon-reviews-list` reference

## 功能与边界

按一个 Amazon ASIN 获取实时买家评论，可按 1—5 星分别设定抓取数量，并按最新评论/最有用、关键词、认证购买和媒体内容筛选。适用于差评痛点、好评特征、竞品反馈、Vine/认证购买标注和产品改进线索整理。评论以发布时的原语言返回。

一次请求只允许一个 ASIN；每个星级最多 100 条；这是实时评论读取，不提供历史评论快照、销售估算、广告/定价策略或 Listing 文案。若用户给多个 ASIN，必须为每个 ASIN 单独调用，并先说明会产生额外消耗。

## MCP 调用

- **MCP server**：`LinkFox`，连接地址 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- **唯一工具**：`proxy_call`
- **toolName**：`amazon/reviews/list`。这是精确路由名，不加前导 `/`，不改成下划线名称。
- **arguments**：直接传入下方【请求参数】定义的对象，不要再包 `body`、`params` 或 `data`。
- **返回**：`proxy_call` 的 text content 是下游 JSON 字符串时只解析一次，再按【响应字段】读取；不得把 MCP 外层对象当成业务响应。
- **调用纪律**：禁止直连工具网关；同一任务内相同 `toolName + arguments` 只调用一次。多个 ASIN 必须分开调用，并先说明额外消耗。MCP 缺失、认证和计费异常按 `onboarding.md` 处理。

## 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---:|---|---|
| `asin` | string | 是 | — | 单个 Amazon 商品 ASIN |
| `domainCode` | string | 否 | `com` | 站点代码，见下表；美国站为 `com` |
| `star1Num` … `star5Num` | integer | 否 | 见下方 | 各星级抓取数量，范围 0—100 |
| `sortBy` | string | 否 | `recent` | `recent` 或 `helpful` |
| `formatType` | string | 否 | `all_formats` | `all_formats` 或 `current_format` |
| `filterByKeyword` | string | 否 | — | 评论关键词，最多 1000 字符 |
| `reviewerType` | string | 否 | `all_reviews` | `all_reviews` 或 `avp_only_reviews` |
| `mediaType` | string | 否 | `all_contents` | `all_contents` 或 `media_reviews_only` |

支持的 `domainCode`：`com`（美国）、`ca`（加拿大）、`co.uk`（英国）、`de`（德国）、`fr`（法国）、`it`（意大利）、`es`（西班牙）、`co.jp`（日本）、`in`（印度）、`com.au`（澳大利亚）、`com.br`（巴西）、`com.mx`（墨西哥）、`nl`（荷兰）、`se`（瑞典）、`ae`（阿联酋）。每次调用前确认用户目标站点。

星级数量规则：若五个星级参数都未传，则 1—5 星各默认 10 条；只要传入任意一个星级参数，其余未传星级均按 0 条处理。显式传五个 0 时不应发起供应商调用。

## 响应字段

### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总评论数 |
| data | array | 评论列表（详见下方评论对象） |
| columns | array | 渲染的列 |
| costToken | integer | 总Token消耗 |
| type | string | 渲染的样式 |

### `data[]` 评论对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data[].reviewId | string | 评论ID |
| data[].asin | string | 产品ASIN |
| data[].title | string | 评论标题 |
| data[].text | string | 评论内容 |
| data[].rating | string | 评分 |
| data[].date | string | 评论日期 |
| data[].userName | string | 评论者名称 |
| data[].verified | boolean | 是否已验证购买 |
| data[].vine | boolean | 是否Vine Voice评论 |
| data[].numberOfHelpful | integer | 有用数量 |
| data[].imageUrlList | array | 评论图片列表 |
| data[].videoUrlList | array | 评论视频列表 |
| data[].domainCode | string | 国家代码 |
| data[].productTitle | string | 产品标题 |
| data[].productRating | string | 产品评分 |
| data[].countRatings | integer | 产品评分数量 |
| data[].countReviews | integer | 产品评论数量 |
| data[].variationId | string | 变体ID |
| data[].variationList | array | 变体列表 |
| data[].profilePath | string | 评论者个人资料路径 |
| data[].currentPage | integer | 当前页码 |
| data[].sortStrategy | string | 排序策略 |
| data[].statusCode | integer | 状态码 |
| data[].statusMessage | string | 状态消息 |
| data[].locale | object | 区域信息 |
| data[].reviewSummary | object | 评论摘要数据 |
| data[].filters | object | 已应用的筛选条件 |
## 错误、展示和成本

- `proxy_call` 返回 `isError=true` 时属于 MCP/代理错误，展示错误并停止，不得改走 HTTP；拿到下游 JSON 后，业务成功通常是 `errorCode=200`，401 表示认证失败，402 表示积分不足，其他非 200 值查看 `errmsg`。401/402 走统一 onboarding。
- 按星级分组展示 `rating`、标题、文本、日期、认证状态、有用票数和媒体；评论量大时先归纳反复出现的抱怨与受好评特征，再列代表评论。明确标注 `vine` 和 `verified`，图片/视频只在 URL 存在时展示。
- 对 rating、帮助票数等站点差异字段做显示归一化，但保留原始文本含义；缺失字段标 N/A。筛选后为空要说明是“无匹配评论”，不能推断为没有全部评论。
- 失败时依据 `errmsg/statusMessage` 建议检查 ASIN、站点代码、星级范围、排序和筛选值；不要自动改变筛选重试。
- 计费按计划抓取页数：令 `P = Σ min(ceil(各星级请求评论数 / 10), 10)`，Token 为 `21000 × P`，实际积分为 `ceil((21000 × P) / 2000) = ceil(10.5 × P)`，按请求分别向上取整。未传星级时 `P=5`；所有星级显式为 0 时 `P=0`；完全失败不计费，空结果和筛选后为空仍按计划页数计费。发起较大抓取前明确预计页数和费用。

## 示例

```json
{"asin":"B08N5WRWNW","domainCode":"com","star1Num":30,"star2Num":30,"star3Num":0,"star4Num":0,"star5Num":0,"sortBy":"recent","reviewerType":"avp_only_reviews","filterByKeyword":"battery"}
```

```json
{"asin":"B08N5WRWNW","domainCode":"co.jp","star5Num":50,"star1Num":0,"star2Num":0,"star3Num":0,"star4Num":0,"sortBy":"helpful","mediaType":"media_reviews_only"}
```

```json
{
  "toolName": "amazon/reviews/list",
  "arguments": {
    "asin": "B08N5WRWNW",
    "domainCode": "com",
    "star1Num": 10,
    "star2Num": 10,
    "star3Num": 0,
    "star4Num": 0,
    "star5Num": 0
  }
}
```

## Feedback API

出现功能不符、结果错误、用户表扬/不满或改进建议时，可在不打断流程的情况下调用独立端点 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，使用 `skillName: "linkfox-wb-amazon-front-data"`，并按 `POSITIVE/NEUTRAL/NEGATIVE` 与 `BUG/COMPLAINT/SUGGESTION/OTHER` 选择枚举值。

