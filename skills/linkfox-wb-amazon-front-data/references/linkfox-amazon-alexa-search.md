# `linkfox-amazon-alexa-search` reference

## 功能与边界

通过 Amazon 前台 Alexa 购物助手提出自然语言购物问题，返回导购回答、分组商品推荐、ASIN/链接和 Alexa 提供的后续问题。适用于对话式选品、按用途/预算/特征找商品、基于具体分类页或搜索页提问，以及在上一轮结果基础上的追问。

每次调用是独立会话，只支持一个 prompt；Alexa 不保留跨调用上下文。它不是完整 SERP、确定性排序、历史搜索分析、详细 ASIN Listing、评论级情感分析或图片视觉搜索。非美国站点的可用性取决于 Alexa 前台覆盖。

## MCP 调用

- **MCP server**：`LinkFox`，连接地址 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- **唯一工具**：`proxy_call`
- **toolName**：`amazon/alexaSearch`。这是精确路由名，不加前导 `/`，并保留 `alexaSearch` 的大小写。
- **arguments**：直接传入下方【请求参数】定义的对象，不要再包 `body`、`params` 或 `data`。
- **返回**：`proxy_call` 的 text content 是下游 JSON 字符串时只解析一次，再按【响应字段】读取；不得把 MCP 外层对象当成业务响应。
- **调用纪律**：禁止直连工具网关；同一任务内相同 `toolName + arguments` 只调用一次。每轮追问是一次新的收费调用，调用前按下方规则确认。MCP 缺失、认证和计费异常按 `onboarding.md` 处理。

## 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---:|---|---|
| `prompts` | string[] | 是 | — | 只能有 1 个元素；提示词长度不超过 255 字符 |
| `format` | string | 否 | `markdown` | `markdown` 或 `json` |
| `url` | string | 否 | — | 具体分类页、搜索结果页或商品详情页 URL；不要传普通首页 |

关键规则：把站点、用途、预算和硬性特征尽量前置到 `prompts[0]`；不能把多个问题放入数组。追问时总结上一轮回答中的关键推荐、ASIN 和结论，再拼接新问题形成新的 `prompts[0]`。没有具体页面时省略 `url`。

## 响应字段

### 顶层响应（字段适用格式见说明）

| 字段路径 | 类型 | 说明 |
|---|---|---|
| stdout | string | Markdown 格式问答报告，包含每一轮的用户问题、Alexa 回答、推荐商品、可继续追问的问题；仅 `format=markdown` 时返回 |
| data | array | 结构化对话结果数组；仅 `format=json` 时返回 |
| resultsNum | integer | Alexa 实际答复的对话轮次数量；为 0 表示未产生有效回答 |
| code | string | 业务状态码，成功为 `"200"`（同 `errcode` 数值版） |
| errcode | integer | 业务状态码（HTTP 层一般为 200，业务成功与否以此字段为准） |
| msg | string | 响应消息，成功为 `ok` |
| errmsg | string | 响应消息，成功为 `ok` |
| costTime | integer | 接口耗时，单位毫秒 |
| costToken | integer | 本次调用消耗 Token 数；上游成功才计费 |
| taskId | string | 上游返回的本次任务标识 |
| type | string | 渲染样式：`stdoutWorkbenches`（markdown）或 `json` |

### `data[]` 结构（`format=json`）

| 字段路径 | 类型 | 说明 |
|---|---|---|
| data[].prompt | string | 当前轮次发送给 Alexa 的提示词 |
| data[].content | string | Alexa 本轮回答的文本内容 |
| data[].screenshot | string | 本轮对话截图链接 |
| data[].followUpQuestions | string[] | Alexa 推荐继续追问的问题列表 |
| data[].products | array | 推荐商品分组列表，每个分组包含 `title` 和 `items` |
| data[].products[].items | array | 来源未说明 |
| data[].products[].title | string | 推荐分组标题 |
| data[].products[].items[].asin | string | 商品 ASIN |
| data[].products[].items[].title | string | 商品标题 |
| data[].products[].items[].url | string | 商品详情页 URL |
| data[].products[].items[].cover | string | 商品封面图 URL |
| data[].products[].items[].price | string | 现价（带币种） |
| data[].products[].items[].originalPrice | string | 原价或划线价 |
| data[].products[].items[].score | string | 评分 |
| data[].products[].items[].ratingsCount | string | 评价数量 |
| data[].products[].items[].describe | string | 商品简介 |
## 错误、展示和成本

- `proxy_call` 返回 `isError=true` 时属于 MCP/代理错误，展示错误并停止，不得改走 HTTP；拿到下游 JSON 后，成功为 `code="200"` 或 `errcode=200`，401 为认证失败，402 为计费/积分不足，其他非 200 值查看 `msg`/`errmsg`。401/402 走统一 onboarding。
- `format=markdown` 时直接保留 `stdout` 的问答、推荐分组和追问结构；`format=json` 时展示回答、每组 ASIN、标题、价格、评分、评论数、商品 URL 和追问。价格必须保留币种，截图作为补充链接。
- 显示 `resultsNum`；为 0 时建议改写问题或用具体页面 URL。非 200 时展示错误消息，建议使用更简单的单一 prompt，不要自动变换问题反复调用。
- Alexa 由上游生成，内容会因时间、流量和上下文变化；同一 prompt 不保证相同结果。计费规则为 13 积分/轮；调用前说明多轮追问会产生额外消耗。

## 示例

### 普通推荐

```json
{"prompts":["best wireless earbuds for running on Amazon US under $100"]}
```

### 页面上下文与结构化输出

```json
{"prompts":["What are the most popular picks on this page?"],"url":"https://www.amazon.com/s?k=electric+kettle","format":"json"}
```

### 追问

```json
{"prompts":["Previously Alexa recommended: 1) Cosori Electric Kettle (B07T1KY5TZ, $35.99, 4.7 stars), 2) Mueller Ultra Kettle (B09KC7D3HR, $29.97, 4.5 stars). Now compare these two on noise level and boil time."],"format":"json"}
```

```json
{
  "toolName": "amazon/alexaSearch",
  "arguments": {
    "prompts": ["best electric kettle on Amazon US"],
    "format": "json"
  }
}
```

## Feedback API

当能力目的与实际行为不符、结果不符合用户意图、用户表扬/不满或提出改进意见时，在不打断流程的情况下调用独立端点 `POST https://skill-api.linkfox.com/api/v1/public/feedback`。`skillName` 使用 `linkfox-wb-amazon-front-data`；情绪枚举为 `POSITIVE`、`NEUTRAL`、`NEGATIVE`，类别枚举为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。

