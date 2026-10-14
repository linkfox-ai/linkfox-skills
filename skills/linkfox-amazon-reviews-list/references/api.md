# 亚马逊商品评论 API 参考

## 调用规范

- **异步提交**：`${LINKFOX_TOOL_GATEWAY}/amazon/reviews/async/submit`
- **异步查询**：`${LINKFOX_TOOL_GATEWAY}/amazon/reviews/async/result`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和算力问题** 处理）

本 Skill 只使用异步提交和查询接口。

## 异步提交

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明                                                                                                                             |
|------|------|------|--------------------------------------------------------------------------------------------------------------------------------|
| asin | string | 是 | 亚马逊商品ASIN                                                                                                                      |
| domainCode | string | 否 | 亚马逊域名代码，默认 `com`。可选值：`com`、`ca`、`co.uk`、`in`、`de`、`fr`、`it`、`es`、`co.jp`、`com.au`、`com.br`、`nl`、`se`、`com.mx`、`ae`。美国站使用 `com` |
| star1Num | integer | 否 | 1星评论数量，默认获取10条，最多100条                                                                                                          |
| star2Num | integer | 否 | 2星评论数量，默认获取10条，最多100条                                                                                                          |
| star3Num | integer | 否 | 3星评论数量，默认获取10条，最多100条                                                                                                          |
| star4Num | integer | 否 | 4星评论数量，默认获取10条，最多100条                                                                                                          |
| star5Num | integer | 否 | 5星评论数量，默认获取10条，最多100条                                                                                                          |
| filterByKeyword | string | 否 | 按关键词筛选评论，最大长度1000字符                                                                                                            |
| sortBy | string | 否 | 评论排序方式：`recent`（最新评论）或 `helpful`（最有用评论），默认 `recent`                                                                            |
| reviewerType | string | 否 | 评论者类型：`all_reviews`（所有评论）或 `avp_only_reviews`（仅认证购买），默认 `all_reviews`                                                          |
| mediaType | string | 否 | 媒体类型：`all_contents`（所有内容）或 `media_reviews_only`（仅包含媒体的评论），默认 `all_contents`                                                    |
| formatType | string | 否 | 格式类型：`all_formats`（所有格式）或 `current_format`（当前格式），默认 `all_formats`                                                           |

说明：若 `star1Num` ~ `star5Num` 均未传，则 1~5 星默认各抓取 `10` 条；若已传任意一个星级数量，则其它未传星级默认 `0`。

无需传 `provider`。后端根据 `domainCode` 自动选择 Pango 或 Apify，实际供应商在提交和查询响应的 `provider` 字段中返回。

提交成功响应：

| 字段 | 类型 | 说明 |
|------|------|------|
| taskId | string | 后续查询使用的任务ID |
| provider | string | 实际选择的供应商 |
| status | string | 初始状态，通常为 `PENDING` |
| pollAfterMillis | integer | 建议下次查询前等待的毫秒数 |

提交接口只调用一次并立即返回 `taskId`。任务未完成或单次查询失败均不得重新提交。

脚本会在本地任务标记中附加经验时间提示：Pango 通常约 `10~30` 秒、Apify 通常约 `15~60` 秒完成，并通过 `suggestedNextCheckAfterSeconds` 提示首次查询时间。该时间仅为当前实测经验，不是 SLA；Agent 应优先继续其他工作，到建议时间再查询。

## 异步查询

请求体：

```json
{
  "taskId": "异步提交返回的任务ID"
}
```

查询响应：

| 字段 | 类型 | 说明 |
|------|------|------|
| taskId | string | 任务ID |
| provider | string | 实际使用的供应商 |
| status | string | `PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED` 或 `CANCELLED` |
| error | string | 任务失败原因，仅失败时存在 |
| result | object | 成功后的评论结果 |
| pollAfterMillis | integer | 建议下次查询前等待的毫秒数；结束后为0 |
| createdAt | integer | 任务创建时间，Unix毫秒 |
| startedAt | integer | 任务开始时间，Unix毫秒 |
| completedAt | integer | 任务完成时间，Unix毫秒 |
| expiresAt | integer | 任务结果过期时间，Unix毫秒 |
| costToken | integer | 查询本身为 `0`，任务费用由后端独立结算，不代表整个任务免费 |

处理规则：

- 默认脚本首次执行只提交并立即返回；后续每次执行只查询一次结果，不循环、不休眠，使 Agent 可以继续其他工作。
- 可以用原提交参数再次执行脚本并从缓存恢复任务，也可以直接传入 `{"taskId":"..."}` 查询。
- `PENDING`、`RUNNING`：从任务创建时间起最多观察 `200` 秒；窗口内保留同一个 `taskId`，继续其他工作，约 `10~20` 秒后再查询，不按 `pollAfterMillis` 忙轮询。
- 临时查询失败（网络异常、服务暂时不可用等）保留原任务，在观察窗口内稍后查询同一 `taskId`；不缓存为最终结果、不重新提交。认证/参数错误或明确的任务不存在则停止。
- `SUCCEEDED`：读取 `result` 并结束。
- `FAILED`：读取 `error` 并结束，不自动重新提交。
- `CANCELLED`：任务等待异步执行资源超时，尚未调用供应商。向用户友好说明当前评论服务可能请求较多、任务已自动取消且未产生费用，建议稍后重新提交；本次执行不自动重新提交。
- 未读取任务从提交时间起保留 4 小时；首次读取到任一终态后，后端立即删除该任务。脚本将成功结果保存到文件，缓存仅记录“已领取”和文件路径，不再缓存一份评论正文。
- 原参数与 `taskId` 在同一工作目录内共用任务记录；24h 本地缓存有效期内重复执行返回 `ALREADY_RECEIVED`、`resultFile`、`fileExists` 和本次 `costToken: 0`，不再发起后端查询。`ALREADY_RECEIVED` 是脚本本地状态，不是后端状态。应读取 `resultFile`；文件已丢失则提示用户，不自动重新抓取。
- 超过 `200` 秒仍未完成时返回 `POLL_TIMEOUT` 并停止自动查询。用户可以选择继续查询同一个 `taskId`，或停止查询；不得自动提交新任务。
- 当前没有手动取消端点。后端只自动取消尚未调用供应商的 `PENDING` 任务；停止查询不会取消已进入 `RUNNING` 的上游调用。
- 任务不存在或已过期：结束并提示用户；只有用户明确要求重试时才重新提交。
- 调用前的积分公式只用于预估。后端在上游处理结束后独立结算，与是否领取结果无关；提交和查询响应的 `X-Cost-Token`/`costToken` 为 `0` 只表示本次接口不再扣费。实际消耗以消费记录为准，不得因未领取、查询失败或本地观察超时报告任务免费，也不得由客户端推算或补记费用。

## 评论结果结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总评论数 |
| data | array | 评论列表（详见下方评论对象） |
| columns | array | 渲染的列 |
| costToken | integer | 领取结果时为 `0`；此字段不表示任务实际费用，任务费用由后台独立结算 |
| type | string | 渲染的样式 |

### 评论对象

| 字段 | 类型 | 说明 |
|------|------|------|
| reviewId | string | 评论ID |
| asin | string | 产品ASIN |
| title | string | 评论标题 |
| text | string | 评论内容 |
| rating | string | 评分 |
| date | string | 评论日期 |
| userName | string | 评论者名称 |
| verified | boolean | 是否已验证购买 |
| vine | boolean | 是否Vine Voice评论 |
| numberOfHelpful | integer | 有用数量 |
| imageUrlList | array | 评论图片列表 |
| videoUrlList | array | 评论视频列表 |
| domainCode | string | 本次查询的站点代码，不代表每条评论的来源 |
| reviewCountry | string | 单条评论所在国家/地区，Pango 和 Apify 共用；名称可能本地化，如 `Canada`、`Canadá` 均指加拿大。缺失时不要从 `domainCode` 或 `locale.country` 推断 |
| productTitle | string | 产品标题 |
| productRating | string | 产品评分 |
| countRatings | integer | 产品评分数量 |
| countReviews | integer | 产品评论数量 |
| variationId | string | 变体ID |
| variationList | array | 变体列表 |
| profilePath | string | 评论者个人资料路径 |
| currentPage | integer | 当前页码 |
| sortStrategy | string | 排序策略 |
| statusCode | integer | 状态码 |
| statusMessage | string | 状态消息 |
| locale | object | 区域信息 |
| reviewSummary | object | 评论摘要数据 |
| filters | object | 已应用的筛选条件 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和算力问题** 处理。|
| 402 | 算力不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和算力问题** 处理。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例（美国站）

### 1. 提交

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/reviews/async/submit \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B08N5WRWNW",
    "domainCode": "com",
    "star1Num": 10,
    "star2Num": 10,
    "star3Num": 0,
    "star4Num": 0,
    "star5Num": 0,
    "sortBy": "recent",
    "reviewerType": "all_reviews"
  }'
```

### 2. 查询

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/reviews/async/result \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "taskId": "提交接口返回的任务ID"
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-amazon-reviews",
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
