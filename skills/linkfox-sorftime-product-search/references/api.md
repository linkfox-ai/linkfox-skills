# Sorftime 亚马逊产品搜索 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/sorftime/amazon/productQuery`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 亚马逊站点代码：us、gb、de、fr、in、ca、jp、es、it、mx、ae、au、br、sa |
| queryMode | integer | 否 | 查询方式。`1`：单条件查询（默认）；`2`：多条件组合查询（且关系） |
| queryType | integer | 否 | 查询类型（1-16），仅当 queryMode=1 时生效。详见 SKILL.md 中 Query Types 完整说明 |
| queryValue | string | 否 | 查询条件值，格式根据 queryMode 和 queryType 不同而变化。详见 SKILL.md 中各 queryType 的格式说明 |
| page | integer | 否 | 分页页码，默认1。每页最多100个产品 |
| queryMonth | string | 否 | 回看历史月份，格式 `yyyy-MM`。不指定时查实时数据 |

- 当 `queryMode=2`（多条件组合查询）时，`queryType` 无效；所有条件通过 `queryValue` 传入 JSON 数组：`[{"QueryType":1,"Content":"B0CVM8TXHP"},{"QueryType":8,"Content":"100,500"}]`
- 当用户明确要求翻页时，调整 `page` 参数

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 响应码（200表示成功） |
| msg | string | 响应消息 |
| total | integer | 结果总数 |
| page | integer | 当前页码 |
| pageCount | integer | 总页数（最多200页） |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗Token数量 |
| requestConsumed | integer | 消耗的请求数 |
| products | array | 产品列表（完整字段说明见 SKILL.md Data Fields） |
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

**单条件 — ASIN同类产品：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 1, "queryValue": "B0CVM8TXHP"}'
```

**单条件 — 类目浏览：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 2, "queryValue": "3743561"}'
```

**单条件 — 品牌热销产品：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 3, "queryValue": "Anker"}'
```

**单条件 — 历史快照回看：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 2, "queryValue": "3743561", "queryMonth": "2024-11"}'
```

**多条件组合 — 新品+高销量+FBA：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 2, "queryValue": "[{\"QueryType\":11,\"Content\":\"2024-06-01,\"},{\"QueryType\":9,\"Content\":\"300,\"},{\"QueryType\":15,\"Content\":\"FBA\"}]"}'
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

