# Google AI 搜索 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/aiMode/googleSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | Google 搜索关键词，作为 `q=` 参数发起 Google AI Mode 搜索。仅支持单轮对话，不支持 prompts 追问参数。如需追问，agent 须自行总结上一轮 AI 概览的关键信息，拼接新问题后作为新的 keyword 发起新请求 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| stdout | string | AI 概览正文，Markdown 格式；按问题顺序逐段输出每个问题的 AI 概览要点与参考来源链接 |
| sourceUrl | string | 抓取目标 URL，最终发往 Google 的搜索页地址 |
| resultsNum | integer | AI 概览块数量；>0 表示页面渲染了 AI Overview，0 表示该关键词未触发 AI Overview |
| code | string | 业务状态码，成功为 `"200"`（同 `errcode` 数值版） |
| errcode | integer | 业务状态码（HTTP 层一般为 200，业务成功与否以此字段为准） |
| msg / errmsg | string | 响应消息，成功为 `ok` |
| costTime | integer | 接口耗时，单位毫秒 |
| costToken | integer | 本次调用消耗 Token 数；上游返回成功才计费 |
| taskId | string | 上游返回的本次抓取任务标识 |
| type | string | 渲染样式，固定 `stdoutWorkbenches`，配合 `stdout` 字段以 Markdown 格式渲染 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 `errcode` / `code` 字段区分（`200` 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 `errcode` 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `stdout` 等业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。 |
| 其他非 200 值 | 业务异常 | 参考 `errmsg` / `msg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/aiMode/googleSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "keyword": "best wireless earbuds 2026"
      }'
```

成功响应（节选）：

```json
{
  "msg": "ok",
  "sourceUrl": "https://www.google.com/search?num=10&udm=50&q=best+wireless+earbuds+2026",
  "errcode": 200,
  "code": "200",
  "stdout": "# Google AI Mode 概览 - best wireless earbuds 2026\n\n## AI 概览要点\n- ...\n",
  "costTime": 10799,
  "costToken": 11200,
  "resultsNum": 1,
  "type": "stdoutWorkbenches",
  "taskId": "1779367311421-d728ce53704fc86e"
}
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-google-aimode-search",
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
