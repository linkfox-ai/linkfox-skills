# ABA 智能查询 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aba/intelligentQuery`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

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

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/aba/intelligentQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"analysisDescription": "筛选美国站，关键词gift在过去12周的搜索热度排名", "region": "US"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
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
