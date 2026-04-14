# Sorftime 产品详情(含趋势) API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/sorftime/amazon/productDetail`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 亚马逊标准识别号（ASIN），支持多个（最多10个），以英文逗号隔开。示例：`B0088PUEPK` 或 `B0088PUEPK,B00U26V4VQ` |
| marketplace | string | 是 | 亚马逊站点代码：us、gb、de、fr、in、ca、jp、es、it、mx、ae、au、br、sa |
| includeTrend | integer | 否 | 是否包含趋势数据。`1`：包含（默认）；`2`：不包含 |
| queryTrendStartDate | string | 否 | 趋势开始日期，格式 `yyyy-MM-dd`。默认仅返回近15天，查询天数>15天时扣费加倍 |
| queryTrendEndDate | string | 否 | 趋势截止日期，格式 `yyyy-MM-dd` |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 响应码（200表示成功） |
| msg | string | 响应消息 |
| total | integer | 结果总数 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗Token数量 |
| requestConsumed | integer | 消耗的请求数 |
| sourceType | string | 来源类型 |
| products | array | 产品详情列表（完整字段说明见 SKILL.md Data Fields） |
| columns | array | 渲染的列 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 code 字段区分（code = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errcode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` 等业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
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
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B00FLYWNYQ", "marketplace": "us"}'
```

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B00FLYWNYQ", "marketplace": "us", "includeTrend": 1, "queryTrendStartDate": "2025-01-01", "queryTrendEndDate": "2025-03-01"}'
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

