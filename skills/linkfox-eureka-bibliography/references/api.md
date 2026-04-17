# Eureka 专利著录项目查询 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/eureka/bibliography`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID。`patentId` 和 `patentNumber` 两个参数必须至少提供一个，如果两个都存在，会优先使用 `patentId`。多个用英文逗号隔开，上限100条。最大长度：60000字符。 |
| patentNumber | string | 条件必填 | 公开(公告)号。`patentId` 和 `patentNumber` 两个参数必须至少提供一个，如果两个都存在，会优先使用 `patentId`。多个用英文逗号隔开，上限100条。最大长度：60000字符。 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 专利著录项目列表 |
| data[].patentId | string | 专利ID |
| data[].pn | string | 公开(公告)号 |
| data[].inventionTitle | array | 专利标题，含语言信息 |
| data[].abstracts | array | 专利摘要，含语言信息 |
| data[].patentType | string | 专利类型：APPLICATION（申请）、PATENT（发明授权）、UTILITY（实用新型）、DESIGN（外观设计） |
| data[].applicants | array | 原始申请人 |
| data[].assignees | array | 当前权利人 |
| data[].inventors | array | 发明人 |
| data[].agents | array | 专利代理人 |
| data[].agency | array | 代理机构 |
| data[].examiners | array | 审查员 |
| data[].priorityClaims | array | 优先权声明 |
| data[].applicationReference | object | 申请信息（申请号、申请日等） |
| data[].publicationReference | object | 公开/公告信息（公开号、公开日等） |
| data[].datesOfPublicAvailability | object | 公开可用日期 |
| data[].classificationIpcr | object | IPC-R分类 |
| data[].classificationCpc | object | CPC分类 |
| data[].classificationUpc | object | UPC分类 |
| data[].classificationGbc | object | GBC分类 |
| data[].classificationLoc | array | 洛迦诺分类 |
| data[].classificationFi | array | FI分类 |
| data[].classificationFterm | array | F-term分类 |
| data[].referenceCitedPatents | array | 引用的专利文献 |
| data[].referenceCitedOthers | array | 引用的非专利文献 |
| data[].relatedDocuments | array | 关联文件（分案、延续等） |
| data[].pctOrRegionalFilingData | object | PCT或区域申请数据 |
| data[].pctOrRegionalPublishingData | object | PCT或区域公开数据 |
| data[].exdt | integer | 预估到期日（时间戳） |
| costToken | integer | 消耗token |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `data` 等业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
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
# 通过公开号查询
curl -X POST https://tool-gateway.linkfox.com/eureka/bibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN115000000A"}'
```

```bash
# 通过专利ID查询（多个）
curl -X POST https://tool-gateway.linkfox.com/eureka/bibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "abc123,def456"}'
```

```bash
# 查询多个公开号
curl -X POST https://tool-gateway.linkfox.com/eureka/bibliography \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US11000000B2,EP3000000A1,CN115000001A"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-eureka-bibliography",
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
