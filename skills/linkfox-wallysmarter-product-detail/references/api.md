# WallySmarter-商品详情 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/wallysmarter/productDetail`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | integer | 是 | 商品ID（ItemId），商品详情链接中包含的数字ID。例如：`https://www.walmart.com/ip/5169493923` 中的 `5169493923` |
| includeStats | boolean | 否 | 是否包含历史价/历史销量，默认 `true` |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（`"200"` 表示成功） |
| msg | string | 消息（成功时为 `"ok"`，失败时为错误描述） |
| total | integer | 返回的商品数量（本接口通常为 1） |
| products | array | 商品列表（见下方商品对象） |
| columns | array | 列定义（描述 products 中各字段的元信息，含 field、title、cellType 等） |
| type | string | 响应渲染类型（固定值 `"productWorkbenches"`） |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

### 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| usItemId | integer | 商品内部 ID（即请求中的 productId） |
| productId | string | Walmart 商品唯一标识（字母数字混合，如 `"6YBM50F6ZXAE"`） |
| title | string | 商品名称 |
| description | string | 商品描述 |
| price | number | 当前售价（美元） |
| wasPrice | number | 划线价（美元），无折扣时可能为 null |
| minPrice | number | 最低价格（美元） |
| brand | string | 品牌名称 |
| rating | number | 商品评分（0.0–5.0） |
| reviews | integer | 评论数量（条） |
| salesEstimate | integer | 销量估算（件，近期周期内） |
| revenue | number | 收入估算（美元） |
| sellerName | string | 卖家名称 |
| fulfillmentType | string | 配送类型：`"MARKETPLACE"`（第三方卖家自配送）或 `"WFS"`（Walmart Fulfillment Services） |
| productPageUrl | string | 商品页面 URL |
| imageUrl | string | 商品图片 URL（缩略图） |
| departmentName | string | 所属部门名称（如 `"Cell Phones"`） |
| departmentId | integer | 所属部门 ID |
| listingScore | integer | Listing 质量评分 |
| contentScore | integer | 内容质量分 |
| outOfStock | integer | 是否缺货（`0`=有货，`1`=缺货） |
| sponsored | integer | 是否广告商品（`0`=否，`1`=是） |
| isBranded | integer | 是否品牌商品（`0`=否，`1`=是） |
| multipleOptionsAvailable | integer | 是否有变体（`0`=否，`1`=是） |
| createdAt | string | WallySmarter 首次收录时间（格式：`yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'`） |
| updatedAt | string | 最近一次数据更新时间（格式同上） |
| stats | object/null | 历史统计数据（仅当 `includeStats=true` 时返回，否则为 null。结构见下方） |
| sourceTool | string | 来源工具标识 |
| sourceType | string | 商品来源平台（固定值 `"walmart"`） |

### stats 对象结构

当 `includeStats=true`（默认）时返回，按天聚合、按时间升序，时区为 UTC，包含两个时间序列数组：

| 字段 | 类型 | 说明 |
|------|------|------|
| stats.price | array | 历史售价时间序列（按日期升序）。每项为单条日期-售价映射 |
| stats.sales | array | 历史销量时间序列（按日期升序）。每项为单条日期-销量映射 |

**数组元素结构：**

每个元素是一个只包含一个键值对的对象，key 为日期字符串（格式 `yyyy-MM-dd`，UTC），value 为当日数值（price：售价，美元；sales：销量，件）。

**示例片段：**

```json
{
  "stats": {
    "price": [
      {"2025-08-18": 279.94},
      {"2025-09-29": 279.94}
    ],
    "sales": [
      {"2025-08-18": 62},
      {"2025-09-29": 79}
    ]
  }
}
```

> 数据按日聚合（UTC 时区），按时间升序排列，覆盖商品被 WallySmarter 收录以来的完整历史。消费端遍历数组后，取每个对象的唯一键作为日期、唯一值作为数值。

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 code 字段区分（code = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
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
curl -X POST https://tool-gateway.linkfox.com/wallysmarter/productDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"productId": 5177343351, "includeStats": true}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-wallysmarter-product-detail",
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
