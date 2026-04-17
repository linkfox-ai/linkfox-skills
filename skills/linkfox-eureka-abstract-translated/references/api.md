# Eureka 获取摘要翻译 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/eureka/abstractDataTranslated`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | patentId 和 patentNumber 至少填一个 | 专利ID，多个用英文逗号隔开，上限100条。最大长度 60,000 字符 |
| patentNumber | string | patentId 和 patentNumber 至少填一个 | 公开(公告)号，多个用英文逗号隔开，上限100条。最大长度 60,000 字符 |
| replaceByRelated | integer | 否 | 摘要无法获取时是否用同族专利摘要替代：`1` 是，`0` 否。默认 `0` |
| lang | string | 否 | 翻译目标语言。可选值：`en`（英文，默认）、`cn`（中文）、`jp`（日语）。最大长度 1,000 字符 |

- `patentId` 和 `patentNumber` 至少需要提供一个。如果两个都存在，会优先使用 `patentId`

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 返回的专利记录数 |
| data | array | 专利列表 |
| data[].patentId | string | 专利ID |
| data[].pn | string | 公开(公告)号 |
| data[].title | string | 标题翻译 |
| data[].abstractText | string | 摘要翻译 |
| data[].pnRelated | string | 替代专利的公开号（仅当使用同族专利替代时提供） |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |

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
curl -X POST https://tool-gateway.linkfox.com/eureka/abstractDataTranslated \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US20200012345A1", "lang": "en", "replaceByRelated": 0}'
```

### 批量查询示例

```bash
curl -X POST https://tool-gateway.linkfox.com/eureka/abstractDataTranslated \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN112345678A,US20200067890A1", "lang": "cn", "replaceByRelated": 1}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-eureka-abstract-translated",
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
