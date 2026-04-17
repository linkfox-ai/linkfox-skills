# 亚马逊商业洞察报告 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/amazon/opportunity/reportByKeyword`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）
- **User-Agent**：`LinkFox-Skill/1.0`

## 请求参数

POST Body（JSON）：

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
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式 |
| 其他非200值 | 业务异常 | 参考 `msg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/opportunity/reportByKeyword \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{"site": "US", "keyword": "ice bricks"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-amazon-opportunity-report",
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
