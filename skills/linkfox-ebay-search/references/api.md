# eBay 商品搜索 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/ebay/search`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词，最大1024字符 |
| ebayDomain | string | 否 | eBay站点域名，默认 `ebay.com`。可选值：ebay.com（美国）、ebay.co.uk（英国）、ebay.de（德国）、ebay.fr（法国）、ebay.it（意大利）、ebay.es（西班牙）、ebay.ca（加拿大）、ebay.com.au（澳大利亚）、ebay.nl（荷兰）、ebay.at（奥地利）、ebay.ch（瑞士）、ebay.pl（波兰）、ebay.ie（爱尔兰）、ebay.com.hk（中国香港）、ebay.com.my（马来西亚）、ebay.com.sg（新加坡） |
| page | integer | 否 | 页码，用于分页，默认 `1` |
| pageSize | integer | 否 | 每页返回的最大结果数，默认 `50`。可选值：25、50、100、200 |
| orderBy | string | 否 | 排序方式，默认 `12`（Best Match）。可选值：1（即将结束）、2（价格最低）、3（价格最高）、7（距离最近）、10（最新上架）、12（最佳匹配）、15（价格+运费最低）、16（价格+运费最高）、18（新品优先）、19（二手优先） |
| priceMin | number | 否 | 最低价格筛选 |
| priceMax | number | 否 | 最高价格筛选 |
| itemCondition | string | 否 | 商品状态代码，多个用 `\|` 分隔。可选值：1000（全新）、1500（全新其他）、1750（全新有瑕疵）、2000（官方翻新）、2010（优秀翻新）、2020（良好翻新）、2030（一般翻新）、2500（卖家翻新）、2750（几乎全新）、3000（二手/已使用）、7000（配件或不工作） |
| buyingFormat | string | 否 | 购买格式。可选值：Auction（拍卖）、BIN（一口价）、BO（最佳报价） |
| showOnly | string | 否 | 过滤条件，多个值用逗号分隔。可选值：Complete（已结束）、Sold（已售出）、FR（免费退货）、RPA（接受退货）、AS（授权卖家）、Savings（折扣）、SaleItems（促销商品）、Lots（批量）、Charity（慈善）、AV、FS（免运费）、LPickup（自提） |
| location | integer | 否 | 商品所在国家/地区代码（例如：1=美国、2=加拿大、3=英国、45=中国、77=德国） |
| prefLoc | string | 否 | 首选位置范围。可选值：1（本国）、2（区域）、3（全球） |
| zipCode | string | 否 | ZIP或邮政编码，用于按区域筛选配送产品 |
| categoryId | integer | 否 | eBay类目ID，用于指定类目搜索 |
| noCache | boolean | 否 | 是否不使用缓存，默认 `false` |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 匹配结果总数 |
| products | array | 商品列表数组（详见下方商品字段） |
| columns | array | 渲染的列定义 |
| type | string | 渲染样式标识 |
| costToken | integer | 消耗token |

### 商品字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | eBay商品ID |
| title | string | 商品标题 |
| subtitle | string | 商品副标题 |
| price | number | 当前价格/成交价格 |
| minPrice | number | 价格区间起始值（适用于多规格商品） |
| maxPrice | number | 价格区间结束值（适用于多规格商品） |
| oldPrice | number | 折扣前原价 |
| currency | string | 货币单位（如 USD、GBP、EUR） |
| condition | string | 商品状态描述 |
| link | string | eBay商品详情页链接 |
| imageUrl | string | 商品缩略图URL |
| shipping | string | 配送信息 |
| location | string | 商品所在地 |
| sellerName | string | 卖家名称 |
| sellerReviews | integer | 卖家评价数量 |
| positiveFeedbackInPercentage | number | 卖家好评率 |
| salesQuantity | integer | 已售数量 |
| bidsCount | integer | 竞拍数量（拍卖商品） |
| returns | string | 退货信息 |
| promotion | string | 促销信息 |
| sponsored | boolean | 是否为赞助/推广商品 |
| sourceType | string | 来源平台标识（`ebay`） |
| sourceTool | string | 来源工具标识 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/ebay/search \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless earbuds", "ebayDomain": "ebay.com", "pageSize": 50, "orderBy": "12"}'
```

### 搜索已售出商品

```bash
curl -X POST https://tool-gateway.linkfox.com/ebay/search \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "iPhone 15 Pro", "showOnly": "Sold,Complete", "orderBy": "10"}'
```

### 按价格区间和商品状态筛选

```bash
curl -X POST https://tool-gateway.linkfox.com/ebay/search \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "laptop", "ebayDomain": "ebay.co.uk", "priceMin": 500, "priceMax": 1000, "itemCondition": "1000"}'
```

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
