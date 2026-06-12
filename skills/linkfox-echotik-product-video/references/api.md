# EchoTik-TikTok商品视频 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/echotik/listProductVideo`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | string | 是 | 商品ID。最大长度 1000 |
| userId | string | 否 | 达人ID，用于筛选特定达人的带货视频。最大长度 1000 |
| productVideoSortField | integer | 否 | 排序字段：1=播放量、2=点赞数、3=分享数、4=视频销量、5=视频销售GMV、6=发布时间。默认 `1` |
| sortType | integer | 否 | 排序方式：0=升序、1=降序。默认 `1` |
| minCreateTime | integer | 否 | 视频发布时间区间-开始（秒级时间戳） |
| maxCreateTime | integer | 否 | 视频发布时间区间-结束（秒级时间戳） |
| pageNum | integer | 否 | 分页页码。默认 `1` |
| pageSize | integer | 否 | 分页条数（须为10的倍数，最大100；官方接口单页上限10，内部按10每页多次拉取后合并）。默认 `50` |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 视频列表（见下方视频对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 视频对象

| 字段 | 类型 | 说明 |
|------|------|------|
| videoId | string | 视频ID |
| productId | string | 商品ID |
| userId | string | 达人ID |
| videoDesc | string | 视频描述 |
| officialUrl | string | TikTok官方视频地址 |
| covet | integer | 分享数 |
| totalFavoritesCnt | integer | 收藏数 |
| totalVideoSaleCnt | integer | 视频销量（估算） |
| totalVideoSaleGmvAmt | integer | 视频销售GMV（估算） |
| hashTag | string | 话题标签 |
| createDate | string (date) | 视频发布日期 |
| region | string | 区域代码 |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |

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
curl -X POST https://tool-gateway.linkfox.com/echotik/listProductVideo \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "1729382310407603945",
    "productVideoSortField": 1,
    "sortType": 1,
    "pageSize": 20
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-echotik-product-video",
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
