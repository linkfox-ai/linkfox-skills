# 亚马逊最新政策法规与资讯 API 参考

本 skill 封装两个串联接口：**政策法规资讯列表**（`amazon/policyFeed`）与**资讯详情**（`amazon/policyFeedDetail`）。先用列表接口拿到资讯 `id`，再用详情接口获取完整正文。

## 调用规范

- **请求方式**：POST，Content-Type: application/json
- **网关基础地址**：环境变量 `${LINKFOX_TOOL_GATEWAY}`（如未配置，脚本内置默认地址）
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）
- **业务成功判定**：HTTP 状态码 200，业务成功以响应体 `errcode` 字段为准（`errcode = 200` 成功，其他值为业务错误，`errmsg` 给出原因）

---

## 一、政策法规资讯列表

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/policyFeed`
- **脚本**：`scripts/amazon_policy_feed.py`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 否 | 亚马逊站点代码（大写），默认 `US`。站点筛选仅对部分资讯类型生效，部分资讯不区分站点始终返回。可选值：US/JP/UK/AU/BE/BR/CA/EG/FR/DE/IN/IT/MX/NL/PL/SA/SG/ES/SE/TR/AE/ZA/IE |
| publishedAtGte | string | 否 | 发布/变更时间下界（含），格式 `yyyy-MM-dd HH:mm:ss`。未传默认近 7 天 |
| publishedAtLte | string | 否 | 发布/变更时间上界（含），格式 `yyyy-MM-dd HH:mm:ss`。未传默认当前时间 |
| page | integer | 否 | 页码，从 1 开始，默认 `1` |
| pageSize | integer | 否 | 每页条数，默认 `20`，取值范围 1-100 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 网关响应码（200 成功） |
| errmsg | string | 提示信息 |
| code | string | 业务响应码（"200" 成功） |
| msg | string | 业务提示信息 |
| total | integer | 本次返回的条数 |
| type | string | 渲染样式，固定 `tableListWorkbenches` |
| data | array | 资讯列表，按发布/变更时间倒序（见下表） |
| costTime | integer | 总处理耗时（毫秒） |
| costToken | integer | token 消耗量 |
| columns | array | 前端列定义 |

#### data 资讯对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 记录 ID（32 位字符串），用作 `amazon/policyFeedDetail` 入参 |
| title | string | 资讯标题 |
| summaryZh | string | 中文摘要，AI 生成的 1-3 句话概括 |
| originalUrl | string | 原文链接 |
| publishedAt | string | 发布/变更时间，格式 `yyyy-MM-dd HH:mm:ss` |

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/policyFeed \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"site": "US", "pageSize": 20}'
```

---

## 二、资讯详情

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/policyFeedDetail`
- **脚本**：`scripts/amazon_policy_feed_detail.py`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 资讯记录 ID（32 位字符串），来自列表接口响应的 `data[].id` |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 网关响应码（200 成功） |
| errmsg | string | 提示信息/错误信息 |
| type | string | 响应类型，固定 `stdoutWorkbenches`（前端按 Markdown 渲染 stdout） |
| stdout | string | 资讯完整正文（Markdown 格式） |
| title | string | 资讯标题 |
| summaryZh | string | 中文摘要（AI 生成的 1-3 句话概括） |
| costTime | integer | 总处理耗时（毫秒） |
| costToken | integer | token 消耗量 |

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/policyFeedDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"}'
```

---

## 错误码

| code | 含义 | 处理建议 |
|------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key |
| 其他非 200 值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例（详情接口传入无效 id）：

```json
{
    "errcode": 400,
    "errmsg": "未找到该资讯记录。"
}
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-amazon-policy-feed",
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
