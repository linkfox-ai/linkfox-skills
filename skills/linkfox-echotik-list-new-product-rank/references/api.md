# EchoTik-TikTok新品榜 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/listNewProductRank`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 是 | 日期，格式为 `YYYY-MM-DD` |
| region | string | 否 | 区域，默认 `US`。可选值：US（美国）、ID（印度尼西亚）、TH（泰国）、PH（菲律宾）、MY（马来西亚）、VN（越南）、GB（英国）、MX（墨西哥）、SG（新加坡）、SA（沙特阿拉伯）、BR（巴西）、ES（西班牙）、JP（日本）、DE（德国）、IT（意大利）、FR（法国） |
| pageNum | integer | 否 | 分页页码，默认 `1` |
| pageSize | integer | 否 | 分页页码，默认 `50` |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| products | array | 最新商品列表（见下方商品对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | 商品名称 |
| asin | string | 商品ID |
| region | string | 区域代码 |
| price | number | SPU平均价格 |
| minPrice | number | 最低价格 |
| maxPrice | number | 最高价格 |
| currency | string | 货币 |
| totalSaleCnt | integer | 总销量 |
| totalSale30dCnt | integer | 近30天销量 |
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv30dAmt | number | 近30天销售额 |
| salesTrendFlagText | string | 销售趋势标识，0=平稳 1=上升 2=下降 |
| totalVideoCnt | integer | 视频总数 |
| totalLiveCnt | integer | 直播总数 |
| totalIflCnt | integer | 总达人数 |
| productCommissionRate | number | 商品佣金比例 |
| productRating | number | 商品评分 |
| reviewCount | integer | 评论数量 |
| availableDate | string (date) | 首次爬取日期 |
| categoryId | string | 商品分类ID |
| imageUrl | string | 商品图片 |
| productImageUrls | array | 商品图片URL列表 |
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
curl -X POST https://tool-gateway.linkfox.com/echotik/listNewProductRank \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-06-15", "region": "US", "pageNum": 1, "pageSize": 50}'
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
