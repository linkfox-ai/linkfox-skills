# `linkfox-ai-mode-google-search`

## 功能说明

对一个自然语言问题执行 Google AI Mode 搜索，返回带引用链接的 AI Overview Markdown，用于最新网页信息归纳、海外消费者偏好、技术问答和长尾方向研究。

## 能力边界与特殊规则

- 每次调用只接受一个必填 `keyword`，只支持单轮；没有 `prompts` 追问参数。
- 用户追问时，先总结上一轮 `stdout` 的关键事实、引用和上下文，再把总结与新问题拼成新的 `keyword` 发起新调用；新调用可能再次计费。
- 结果受 Google 实时页面、语言和措辞影响；接口没有显式地区参数，应使用目标市场语言并在问题中加入地区线索。
- `resultsNum=0` 表示本次未渲染 AI Overview，不代表网上没有相关内容；不要编造答案或引用。
- 输出是非结构化 Markdown，不应送入 SQL 或结构化数据分析沙箱；若用户只要原始网页或平台商品数据，应转到适当能力。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`aiMode/googleSearch`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理错误；代理成功后读取 text/structured content，text 为 JSON 时只解析一次，再按响应字段检查下游状态。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想不得自动重试、翻页或改参数探测。
### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keyword` | string | 是 | 作为 Google AI Mode `q=` 的单个问题或查询；追问时放入总结后的新问题 |

### 响应字段

#### 完整响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| stdout | string | AI 概览正文，Markdown 格式；按问题顺序逐段输出每个问题的 AI 概览要点与参考来源链接 |
| sourceUrl | string | 抓取目标 URL，最终发往 Google 的搜索页地址 |
| resultsNum | integer | AI 概览块数量；>0 表示页面渲染了 AI Overview，0 表示该关键词未触发 AI Overview |
| code | string | 业务状态码，成功为 `"200"`（同 `errcode` 数值版） |
| errcode | integer | 业务状态码（HTTP 层一般为 200，业务成功与否以此字段为准） |
| msg | string | 响应消息，成功为 `ok` |
| errmsg | string | 响应消息，成功为 `ok` |
| costTime | integer | 接口耗时，单位毫秒 |
| costToken | integer | 本次调用消耗 Token 数；上游返回成功才计费 |
| taskId | string | 上游返回的本次抓取任务标识 |
| type | string | 渲染样式，固定 `stdoutWorkbenches`，配合 `stdout` 字段以 Markdown 格式渲染 |

### 错误与成本

- 先按 MCP/代理层与下游业务层分层处理错误；MCP 授权和下游 401/402/403 见 `onboarding.md`。
- `resultsNum=0` 表示该关键词未触发 AI Overview，不等于没有相关网页，也不是自动重试理由。
- 来源响应定义说明 `costToken` 在上游返回成功时计费。追问是新的收费调用；同一任务内相同 `toolName + arguments` 不得重复调用。

### MCP 示例

```json
{
  "toolName": "aiMode/googleSearch",
  "arguments": {
    "keyword": "best wireless earbuds for US consumers in 2026"
  }
}
```


## 使用与展示

```json
{"keyword":"Based on current web sources, what are the unsolved pain points of robot vacuums for US pet owners in 2026?"}
```

直接保留 `stdout` 的标题、段落、列表和引用链接，同时说明 `sourceUrl`、`resultsNum` 和调用时效。若 `resultsNum=0`，明确建议改写问题或换目标市场语言；若业务失败，展示 `msg`/`errmsg`，不伪造网页结论。追问示例：先把上一轮概览总结为“已提到的产品、观点和来源”，再与“哪些痛点尚未解决？”拼成新的 `keyword`。

## 反馈 API

用户表达结果错误、与意图不符、满意、抱怨或建议时，可异步 POST 到独立地址 `https://skill-api.linkfox.com/api/v1/public/feedback`：

```json
{"skillName":"linkfox-wb-google-tools","sentiment":"POSITIVE","category":"OTHER","content":"说明用户意图、实际结果及问题或满意点"}
```

`sentiment` 取 `POSITIVE`、`NEUTRAL`、`NEGATIVE`；`category` 取 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。
