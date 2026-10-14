# 子能力归档：linkfox-amazon-opportunity-report-by-keyword

## 功能说明

按一个 Amazon 关键词生成 AI 商业洞察报告，覆盖市场潜力、产品特征、用户评论、客户画像、搜索趋势和定价分析六个维度。输出是用于决策参考的结构化 Markdown 报告，属于生成时点的快照。

## 能力边界与特殊规则

- 当前仅支持美国站，必须使用 `site=US`；不能将其他站点请求改写为美国站而不告知用户。
- `keyword` 与 `site` 均为必填；报告是 Markdown 长文本，不是可供二次聚合的结构化数据。
- 适合已知关键词的整体市场机会评估；不适合实时排名、具体 ASIN 详情/销量、历史价格跟踪、单个 ASIN 评论拆解或广告/PPC 策略。
- 报告生成涉及 AI 分析，耗时可能长；失败时按 `msg` 说明原因，建议检查关键词或稍后重试，不自动变更关键词连续试探。

## 执行、展示与反馈规则

- 通过 `LinkFox` 的 `proxy_call` 调用；新链路不提供旧脚本的 24 小时缓存、响应落盘或 stdout 摘要。
- 同一任务内相同 `toolName + arguments` 只调用一次；失败、空结果或返回不理想时不得自动重试。
- 成功时原样呈现 `stdout` Markdown，并标注站点与生成时间；同时说明它是时点快照，仅作决策参考，不额外添加主观商业建议。
- 若用户试图把报告送入数据查询工具做二次聚合，应说明该输出为非结构化 Markdown，并改用指标筛选或 ABA 能力。
- 若用户反馈结果不准确、与意图不符、表达满意/不满或提出改进建议，可按 API 末尾 Feedback API 上报，`skillName` 使用 `linkfox-wb-amazon-business-insight`。

# 亚马逊商业洞察报告 API 参考

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`amazon/opportunity/reportByKeyword`
- **arguments**：直接使用本 reference 的请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；禁止在配置或 `arguments` 中加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text 为 JSON 字符串时只解析一次，最后检查下游 `code`、`msg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；同一任务内相同 `toolName + arguments` 不得重复调用。

## 请求参数

`proxy_call.arguments`（JSON 对象）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 亚马逊站点代码，当前仅支持 `US` |
| keyword | string | 是 | 要查询洞察报告的搜索关键词 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 响应码 |
| msg | string | 提示信息或错误信息 |
| stdout | string | 综合商业洞察报告内容（Markdown 格式），包含市场潜力、产品特征、用户评论、客户画像、搜索趋势、定价分析六大维度 |
| costTime | integer | 总处理耗时（毫秒） |
| costToken | integer | token 消耗量 |
| type | string | 响应类型 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 code 字段区分。当遇到未授权等情况时，HTTP 状态码为 401。

| 错误码 | 含义 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常解析 `stdout` 字段，将 Markdown 报告展示给用户 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 其他非200值 | 业务异常 | 参考 `msg` 字段获取具体错误原因 |

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
  "toolName": "amazon/opportunity/reportByKeyword",
  "arguments": {
    "site": "US",
    "keyword": "ice bricks"
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
