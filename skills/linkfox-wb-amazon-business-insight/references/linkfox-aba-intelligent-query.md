# 子能力归档：linkfox-aba-intelligent-query

## 功能说明

查询并分析 Amazon Brand Analytics（ABA）搜索词报告，覆盖 15 个 Amazon 站点约 3 年的周粒度数据。结果可用于搜索热度趋势、上升词/新兴词、季节性、点击份额与转化份额、蓝海词以及高点击低转化 ASIN 等搜索词级分析。

## 能力边界与特殊规则

- 数据粒度是周，不是日；`searchFrequencyRank` 数值越小表示搜索热度越高。
- 默认站点为 `US`；支持 `US、DE、BR、CA、AU、JP、AE、ES、FR、IT、SA、TR、MX、SE、NL`。
- `analysisDescription` 必须精确写明站点、数值范围、时间范围、比较基准和去重逻辑；相同搜索词与 ASIN 的保留规则需要在描述中明确。
- `createDownloadUrl=true` 仅在用户明确要求下载、导出或生成文件时使用；下载链接最多包含 10,000 条记录。
- 本能力提供搜索词与点击/转化份额分析，不提供广告竞价、Listing 文案、评论、ASIN 销量估算或本地 ABA 文件处理。

## 执行、展示与反馈规则

- 通过 `LinkFox` 的 `proxy_call` 调用；新链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。
- 同一任务内相同 `toolName + arguments` 只调用一次；失败、空结果或返回不理想时不得自动重试。
- 展示时标明站点、报告周次和数据来源；明确提示排名数值越小越好。结果较多时优先呈现核心列，并提供 `downloadUrl`（如有）或建议生成下载链接。
- 查询失败时依据 `msg`/错误字段解释原因并建议收紧或调整查询描述；不得因失败或空结果自动更换关键词、翻页或连续改参数。
- 若用户反馈结果不准确、与意图不符、表达满意/不满或提出改进建议，可按 API 末尾 Feedback API 上报，`skillName` 使用 `linkfox-wb-amazon-business-insight`。

# ABA 智能查询 API 参考

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`aba/intelligentQuery`
- **arguments**：直接使用本 reference 的请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；禁止在配置或 `arguments` 中加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text 为 JSON 字符串时只解析一次，最后检查下游 `errorCode`、`code`、`msg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；同一任务内相同 `toolName + arguments` 不得重复调用。

## 请求参数

`proxy_call.arguments`（JSON 对象）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| analysisDescription | string | 是 | 精确描述查询意图的自然语言 |
| region | string | 否 | 站点代码，默认 `US`。可选值：US、DE、BR、CA、AU、JP、AE、ES、FR、IT、SA、TR、MX、SE、NL |
| createDownloadUrl | boolean | 否 | 是否生成CSV下载链接，默认 `false` |

- 当用户明确要求"下载"、"导出"、"生成文件"时，将 `createDownloadUrl` 设为 `true`

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否查询成功 |
| tables | array | 结果数据数组，每个元素包含 `data`（数据行）、`columns`（列定义）、`name`（Sheet名称） |
| total | integer | 结果总数 |
| downloadUrl | string | 当 `createDownloadUrl` 为 true 时返回CSV文件地址 |
| msg | string | 附加消息 |
| downloadNote | string | 下载相关提示 |
| code | string | 返回码 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |

### `tables[]` 元素

来源仅明确列出以下成员，未进一步说明成员类型或内部字段。

| 字段路径 | 类型 | 说明 |
|----------|------|------|
| tables[].data | 来源未说明 | 数据行 |
| tables[].columns | 来源未说明 | 列定义 |
| tables[].name | 来源未说明 | Sheet名称 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `tables` / `data` 等业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## MCP 调用示例

```json
{
  "toolName": "aba/intelligentQuery",
  "arguments": {
    "analysisDescription": "筛选美国站，关键词gift在过去12周的搜索热度排名",
    "region": "US"
  }
}
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-wb-amazon-business-insight",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
