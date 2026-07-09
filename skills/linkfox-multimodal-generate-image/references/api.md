# AI绘图 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/multimodal/generateImage`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 提示词（支持各种文生图、图生图、图片修改、模特更换），最大长度 1000 |
| referenceImageUrl | string | 否 | 参考图地址，多个图片用逗号隔开，最多支持3个图片，最大长度 1000 |
| aspectRatio | string | 否 | 宽高比，支持 `1:1`（正方形，默认）、`3:4`（竖版）、`4:3`（横版）、`9:16`（竖版全屏）、`16:9`（横版全屏），默认 `1:1` |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | id |
| finished | boolean | 是否完成 |
| status | string | 状态 |
| text | string | 图片内容 |
| type | string | markdown类型 |
| title | string | 图片 |
| costToken | integer | 使用token |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
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
curl -X POST https://tool-gateway.linkfox.com/multimodal/generateImage \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "生成一张红色手提包的专业商品照，白色背景，影棚灯光",
    "aspectRatio": "1:1"
  }'
```

### 带参考图示例

```bash
curl -X POST https://tool-gateway.linkfox.com/multimodal/generateImage \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "更换图片1的背景颜色为热带海滩场景",
    "referenceImageUrl": "https://example.com/product.jpg",
    "aspectRatio": "4:3"
  }'
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
