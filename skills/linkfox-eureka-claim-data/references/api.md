# Eureka 专利权利要求查询 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/eureka/claimData`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| patentId | string | 条件必填 | 专利ID。`patentId` 和 `patentNumber` 两个参数必须至少提供一个，如果两个都存在，会优先使用 `patentId`。多个用英文逗号隔开。 |
| patentNumber | string | 条件必填 | 公开(公告)号。`patentId` 和 `patentNumber` 两个参数必须至少提供一个，如果两个都存在，会优先使用 `patentId`。多个用英文逗号隔开。 |
| replaceByRelated | string | 否 | 是否用关联专利作为兜底。"1" = 启用兜底（当查询专利无权利要求时，尝试用关联专利替代），"0" = 不启用（默认）。 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 专利权利要求列表 |
| data[].patentId | string | 专利ID |
| data[].pn | string | 公开(公告)号 |
| data[].pnRelated | string | 关联专利公开号（仅在启用replaceByRelated且发生兜底时出现） |
| data[].claims | array | 权利要求数组，包含各项权利要求的全文 |
| data[].claimCount | integer | 权利要求总数 |
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
# 通过公开号查询权利要求
curl -X POST https://tool-gateway.linkfox.com/eureka/claimData \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN115000000A"}'
```

```bash
# 通过专利ID查询，启用关联专利兜底
curl -X POST https://tool-gateway.linkfox.com/eureka/claimData \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "abc123", "replaceByRelated": "1"}'
```

```bash
# 查询多个公开号的权利要求
curl -X POST https://tool-gateway.linkfox.com/eureka/claimData \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US11000000B2,EP3000000A1"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-eureka-claim-data",
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
