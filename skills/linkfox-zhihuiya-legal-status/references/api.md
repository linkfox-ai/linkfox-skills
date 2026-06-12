# 智慧芽专利法律状态查询 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/zhihuiya/legalStatus`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

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
| data | array | 专利法律状态列表 |
| data[].patentId | string | 专利ID |
| data[].pn | string | 公开(公告)号 |
| data[].simpleLegalStatus | array | 简单法律状态。可选值：失效-Inactive、有效-Active、审中-Pending、未确认-Undetermined、PCT指定期内-PCT designated period、PCT指定期满-PCT designated expiration |
| data[].legalStatus | array | 法律状态。可选值：公开-Published、实质审查-Examining、授权-Granted、避重授权-Double、放弃-未指定类型-Abandoned-Undetermined、放弃-主动放弃-Abandoned-Voluntarily、放弃-视为放弃-Abandoned-Deemed、撤回-未指定类型-Withdrawn-Undetermined、撤回-主动撤回-Withdrawn-Voluntarily、撤回-视为撤回-Withdrawn-Deemed、驳回-Rejected、全部撤销-Revoked、期限届满-Expired、未缴年费-Non-Payment、权利恢复-Restoration、权利终止-Ceased、部分无效-P-Revoked、申请终止-Discontinuation、PCT国际公布-PCT published、PCT进入指定国（指定期内）-PCT entering(designated period)、PCT进入指定国（指定期满）-PCT entering(designated expiration)、PCT未进指定国-PCT unentered |
| data[].eventStatus | array | 法律事件。可选值：权利转移-Transfer、许可-License、质押/担保-Pledge、信托-Trust、异议-Opposition、复审-Re-examination、海关备案-Customs、诉讼-Litigation、保全-Preservation、无效程序-Invalid-procedure、口头审理-Oral-procedure、国防解密-Declassification、一案双申-Double application |
| data[].legalDate | integer | 法律状态更新日期（时间戳） |
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
# 通过公开号查询
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/legalStatus \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "CN115000000A"}'
```

```bash
# 通过专利ID查询（多个）
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/legalStatus \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "abc123,def456"}'
```

```bash
# 查询多个公开号
curl -X POST https://tool-gateway.linkfox.com/zhihuiya/legalStatus \
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
