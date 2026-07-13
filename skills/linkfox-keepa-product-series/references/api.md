# Keepa-亚马逊价格历史 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/keepa/productSeries`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 亚马逊标准识别号(ASIN)，只支持单个ASIN，最大长度1000 |
| domain | string | 是 | 亚马逊域名ID。可选值：`1`（美国）、`2`（英国）、`3`（德国）、`4`（法国）、`5`（日本）、`6`（加拿大）、`8`（意大利）、`9`（西班牙）、`10`（印度）、`11`（墨西哥）、`12`（巴西） |
| days | integer | 否 | 限制历史数据天数，默认 `90` 天，最大 `365` |
| showPrice | integer | 否 | 设为 `1` 返回市场最低新品价曲线 |
| showPriceList | integer | 否 | 设为 `1` 返回划线价/标价曲线 |
| showPriceDeal | integer | 否 | 设为 `1` 返回闪促价格曲线 |
| showPricePrime | integer | 否 | 设为 `1` 返回Prime专属新品价曲线 |
| showPriceFba | integer | 否 | 设为 `1` 返回第三方FBA新品价曲线 |
| showPriceFbm | integer | 否 | 设为 `1` 返回第三方FBM新品价曲线 |
| showPriceCoupon | integer | 否 | 设为 `1` 返回优惠券后买盒价曲线 |
| showBsrMain | integer | 否 | 设为 `1` 返回大类BSR曲线 |
| showSellerCount | integer | 否 | 设为 `1` 返回卖家数曲线 |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| buyboxPrice | array | Buybox价格（time=时间，value=Buybox价格） |
| price | array | 价格（time=时间，value=价格） |
| priceList | array | 划线价（time=时间，value=划线价格） |
| priceDeal | array | Deal价格（time=时间，value=Deal价格） |
| pricePrime | array | Prime价格（time=时间，value=Prime价格） |
| priceFba | array | FBA价格（time=时间，value=FBA价格） |
| priceFbm | array | FBM价格（time=时间，value=FBM价格） |
| priceCoupon | array | coupon价格（time=时间，value=coupon价格） |
| bsrMain | array | 大类BSR，每个元素包含 `categoryName`（类目名称）和 `points`（time=时间，value=排名） |
| bsrSub | array | 小类BSR，每个元素包含 `categoryName`（类目名称）和 `points`（time=时间，value=排名） |
| sellerCount | array | 卖家数（time=时间，value=卖家数） |
| rating | array | 评分（time=时间，value=评分） |
| ratingCount | array | 评分数（time=时间，value=评分数） |
| monthlySold | array | 子体销量（time=时间，value=销量） |
| costToken | integer | 消耗token |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | - | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
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
curl -X POST https://tool-gateway.linkfox.com/keepa/productSeries \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0DFRJ7WSX", "domain": "1", "days": 90, "showBsrMain": 1, "showPrice": 1, "showSellerCount": 1}'
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
