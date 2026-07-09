# Walmart前端-商品列表 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/walmart/search`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否* | 搜索关键词，最大长度1024字符。*与 categoryId 至少提供一个 |
| categoryId | string | 否* | 类目ID，*与 keyword 至少提供一个。`0` 表示所有部门。例如：`976759_976787` 表示"Cookies" |
| sort | string | 否 | 排序方式。可选值：`price_low`（价格从低到高）、`price_high`（价格从高到低）、`best_seller`（最畅销）、`best_match`（最佳匹配） |
| page | integer | 否 | 页码，用于分页，默认为1，最大值为100 |
| minPrice | number | 否 | 最低价格 |
| maxPrice | number | 否 | 最高价格 |
| spelling | boolean | 否 | 激活拼写修正，默认 `true`。`true` 包含拼写修正，`false` 不包含 |
| softSort | boolean | 否 | 按相关性排序，默认为 `true`。设置为 `false` 可禁用按相关性排序 |
| storeId | string | 否 | 商店ID，用于按特定商店筛选产品 |
| device | string | 否 | 设备类型，默认 `desktop`。可选值：`desktop`（桌面浏览器）、`tablet`（平板浏览器）、`mobile`（移动浏览器） |
| facet | string | 否 | 过滤条件，格式为 key:value 对，用 `\|\|` 分隔 |
| nextDayEnabled | boolean | 否 | 仅显示NextDay配送结果，默认 `false`。`true` 启用，`false` 禁用 |
| jsonRestrictor | string | 否 | JSON字段限制器 |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| products | array | 产品列表（见下方产品对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 产品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 产品ID |
| usItemId | string | US商品ID |
| title | string | 标题 |
| description | string | 描述 |
| price | number | 价格 |
| wasPrice | number | 原价（was_price） |
| currency | string | 货币单位 |
| minPrice | number | 最低价格 |
| pricePerUnitAmount | string | 单价金额 |
| pricePerUnit | string | 单价单位 |
| rating | number | 评分 |
| reviews | integer | 评价数 |
| sellerName | string | 卖家名称 |
| sellerId | string | 卖家ID |
| imageUrl | string | 缩略图 |
| productPageUrl | string | 产品页面URL |
| sponsored | boolean | 是否是赞助商品 |
| outOfStock | boolean | 是否缺货 |
| freeShipping | boolean | 是否免运费 |
| twoDayShipping | boolean | 是否支持两日配送 |
| freeShippingWithWalmartPlus | boolean | Walmart Plus会员免运费 |
| shippingPrice | number | 运费 |
| multipleOptionsAvailable | boolean | 是否有多个选项 |
| variantSwatches | array | 变体样本列表（每项包含 `name` 变体名称、`imageUrl` 变体图片URL、`productPageUrl` 变体产品页面URL、`variantFieldId` 变体字段ID） |
| sourceTool | string | 来源工具 |
| sourceType | string | 来源类型：walmart |

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
curl -X POST https://tool-gateway.linkfox.com/walmart/search \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless earbuds", "sort": "best_seller", "page": 1}'
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
