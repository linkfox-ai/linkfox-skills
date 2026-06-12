# 亚马逊商品评论（美国站）API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/amazon/usReviewsList`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 亚马逊商品ASIN（如 "B076CLQDR4"） |
| marketplace | string | 否 | 固定值 `US`，默认 `US` |
| star1Num | integer | 否 | 1星评论数量(0-100)，默认0 |
| star2Num | integer | 否 | 2星评论数量(0-100)，默认0 |
| star3Num | integer | 否 | 3星评论数量(0-100)，默认0 |
| star4Num | integer | 否 | 4星评论数量(0-100)，默认0 |
| star5Num | integer | 否 | 5星评论数量(0-100)，默认0 |
| allStarsNum | integer | 否 | 全星级评论数量(0-100)，默认10。当 star1-5Num 均为0时生效 |
| positiveNum | integer | 否 | 4-5星正面评论数量(0-100)，默认0 |
| criticalNum | integer | 否 | 1-3星负面评论数量(0-100)，默认0 |
| sortBy | string | 否 | 排序：`recent`（最新）或 `helpful`（最有用），默认 `recent` |
| formatType | string | 否 | 格式类型：`current_format`（当前ASIN）或 `all_formats`（所有变体），默认 `current_format` |

> **注意**：美国站 API 不支持 `filterByKeyword`、`reviewerType`、`mediaType` 参数。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 返回码（200=成功） |
| msg | string | 消息 |
| sourceUrl | string | 来源URL |
| total | integer | 总评论数 |
| title | string | 查询标题 |
| data | array | 评论列表（详见下方评论对象） |
| costTime | integer | 查询耗时（毫秒） |
| costToken | integer | 总Token消耗 |
| taskId | string | 任务ID |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |

### 评论对象

| 字段 | 类型 | 说明 |
|------|------|------|
| reviewId | string | 评论ID |
| asin | string | 产品ASIN |
| title | string | 评论标题 |
| text | string | 评论内容 |
| rating | string | 评分（完整描述，如 "5.0 out of 5 stars"） |
| date | string | 评论日期（英文格式，如 "April 3, 2026"） |
| userName | string | 评论者名称 |
| authorId | string | 评论者ID |
| verified | boolean | 是否已验证购买 |
| vine | boolean | 是否Vine Voice评论 |
| numberOfHelpful | string | 有用数量（字符串类型，如 "5 people found this helpful"） |
| imageUrlList | array | 评论图片列表 |
| videoUrlList | array | 评论视频列表 |
| attributes | array | 产品选购属性（如颜色、尺码等） |
| profilePath | string | 评论者个人资料路径 |
| domainCode | string | 国家代码（"us"） |
| sortStrategy | string | 排序策略 |
| statusCode | integer | 状态码 |

## 与非美国站 API 的关键字段差异

| 字段 | 非美国站（api.md） | 美国站（本文档） |
|------|-------------------|-----------------|
| rating | 数字字符串 `"4.5"` | 完整描述 `"5.0 out of 5 stars"`，需提取数字 |
| numberOfHelpful | integer | string，需转为数字 |
| attributes | 无 | array（产品属性如颜色、尺码） |
| authorId | 无 | string |
| productTitle / productRating | 评论对象内 | 无（productTitle 在响应顶层 `title` 中） |
| variationId / variationList | 有 | 无 |
| countRatings / countReviews | 有 | 无 |

## 错误码

正常情况下，HTTP 状态码为 200，业务成功与否通过响应体中的 `code` 字段区分（code = 200 表示成功）。业务异常时检查 `msg` 字段。未授权时 HTTP 状态码为 401。

| code | 含义 | 处理建议 |
|------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key |
| 其他非200值 | 业务异常 | 参考 `msg` 字段获取具体错误原因 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/amazon/usReviewsList \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B08N5WRWNW",
    "marketplace": "US",
    "allStarsNum": 10,
    "sortBy": "recent"
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
