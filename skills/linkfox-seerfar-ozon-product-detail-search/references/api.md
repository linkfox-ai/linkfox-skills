# Seerfar Ozon 商品详情搜索 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/productDetailSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **User-Agent**：`LinkFox-Skill/1.0`；HTTP 超时 60s

## 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。仅 `sku` 必填，其余可选。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sku | string | 是 | 商品 SKU（Ozon SKU，如 `175924376`）。即其他 Seerfar Ozon 工具返回的 `sku` |
| dateRange | string | 否 | 销量/指标统计窗口，默认 `past_30_days`。可选：`past_7_days` / `past_30_days` / `past_60_days` / `past_90_days` / `past_180_days` / `past_365_days` |
| uId | string | 否 | 用户 ID（最长 1000） |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，一个用户可归属多个团队，数据归属于 memberId，最长 1000） |

> **必填约束**：`sku` 为必填；缺失返回 `errcode 400`（`sku 为必填参数`）。
> **单 SKU 查询**：本接口一次只查一个商品详情，无批量/列表模式。
> **窗口仅作用于销量聚合**：`dateRange` 只影响 `totalSales` / `dailySales` / `totalRevenue` / `salesTrendVOList` / `startDate` / `endDate` 等销量类字段；商品元数据（标题、价格、评分、品牌、卖家、配送方式等）为当下快照，不受窗口影响。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项 |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 返回记录数（命中时为 `1`，未命中为 `0`） |
| totalSales | integer | 统计窗口内总销量 |
| dailySales | number | 平均每天销量（≈ totalSales / 窗口天数） |
| totalRevenue | number | 统计窗口内销售额（卢布） |
| stock | integer | 库存 |
| startDate | string | 统计窗口起始日期（如 `2026-06-01`） |
| endDate | string | 统计窗口结束日期（如 `2026-06-30`） |
| salesTrendVOList | array | 每日销量数据序列（见下方） |
| categoryRanks | array | 商品类目排名历史（见下方） |
| products | array | 商品详情列表（单 SKU 查询命中时 1 条，未命中为空） |
| data | array | 返回数据，内容与 `products` 完全一致 |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| type | string | 响应展示类型，如 `productWorkbenches` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

> 未命中的 SKU：返回成功（`code:"200"`、`errcode:200`），但 `total:0`、`products:[]`，且销量聚合字段（`totalSales` / `dailySales` / `totalRevenue` / `stock` / `startDate` / `endDate`）不返回。判断"商品无数据"应基于 `total=0` 或 `products` 为空，而非 `errcode`。

### products[*] / data[*] 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| sku | integer | 商品 SKU |
| productId | integer | 统一商品 ID，映射自 `sku` |
| title | string | 商品标题 |
| price | number | 商品价格（卢布） |
| currency | string | 币种，固定 `₽` |
| reviewRating | number | 商品评分 |
| rating | number | 统一评分，映射自 `reviewRating` |
| reviewCount | integer | 评论数 |
| questionsAndAnswers | integer | QA 数量 |
| brandName | string | 品牌名称 |
| brand | string | 统一品牌，映射自 `brandName` |
| brandId | integer | 品牌 ID |
| brandUrl | string | 品牌链接 |
| sellerName | string | 卖家名称 |
| sellerId | integer | 卖家 ID（负值为 Ozon 平台自营卖家，如 `-4` Ozon Россия） |
| fulfillment | array | 商品配送方式，如 `["FBO"]`、`["OZON"]`，可能含多个值 |
| upTime | integer | 上架时间，毫秒时间戳 |
| upDays | integer | 上架天数 |
| upMonths | integer | 上架月数 |
| imageUrl | string | 统一主图 URL，映射自 `imageUrls` 首张 |
| imageUrls | array | 商品图片 URL 列表 |
| productUrl | string | 商品 URL |
| productPageUrl | string | 统一商品页 URL，映射自 `productUrl` |
| categoryInfo | object | 商品类目信息（见下方） |
| monthlySalesUnits | integer | 统一月销量，实际取值等于当前统计窗口的 `totalSales` |
| monthlySalesRevenue | number | 统一月销售额，实际取值等于当前统计窗口的 `totalRevenue` |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，标识 Seerfar Ozon 接口（如 `Seerfar-Ozon-查竞品`） |
| weight | number | 商品重量，单位 g（数字/服务类商品可能不返回，见字段差异） |
| grossMargin | number | 毛利率（schema 定义，实测部分商品不返回，见字段差异） |

> **`data` 与 `products`**：两者内容完全一致，单 SKU 查询命中时各含 1 条记录。

### salesTrendVOList[*] 每日销量对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期（如 `2026-06-01`） |
| sales | integer | 当日销量（可能为 `0`） |
| revenue | number | 当日销售额（卢布） |
| price | number | 当日价格（卢布） |
| stock | integer | 当日库存 |
| reviewCount | integer | 截至当日评论数（累计） |
| reviewRating | number | 截至当日评分 |

### categoryRanks[*] 类目排名对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 月份（如 `2026-02`；当月为具体日期 `2026-07-01`） |
| rank | integer | 类目排名 |
| count | integer | 统计计数（以网关实际口径为准） |

> `categoryRanks` 仅含 `date` / `rank` / `count`，不含类目名称；类目名称/路径请取自 `categoryInfo`。

### categoryInfo 类目信息对象

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitlePath | string | 中文类目路径 |
| enTitlePath | string | 英文类目路径 |
| titlePath | string | 类目路径（原文） |
| category | object | 末级类目对象（字段见下方） |
| fullCategoryId | array | 完整类目 ID 路径（字符串数组，根→末级，如 `["99999999", "99999999_200001489", "99999999_200001489_970727001"]`） |

#### category 对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitle | string | 类目中文名 |
| enTitle | string | 类目英文名 |
| title | string | 类目原文标题 |
| level | integer | 类目层级 |
| id | string | 类目 ID |
| pid | string | 父类目 ID |
| crossBorderSellable | boolean | 是否支持跨境销售 |
| disabled | boolean | 是否停用 |

## 错误码

正常情况下 HTTP 状态码为 200，业务结果通过响应体区分：
- **成功**：返回 `code:"200"` + `errcode:200`（`msg` / `errmsg` 均为 `ok`）。
- **业务错误**：HTTP 仍为 200，但仅返回 `errcode`（非 200）+ `errmsg`（原因），无 `code` 字段。
- **认证失败**：HTTP 状态码 401，响应体 `{"errcode":401,"errmsg":"authorized error"}`。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` / `data` 及销量聚合字段 |
| 400 | 参数错误 | 查看 `errmsg`；常见为缺 `sku`（`sku 为必填参数`） |
| 1003 | 请求过于频繁 | 限流，稍后重试 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 计费失败 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` 获取具体原因 |

错误响应示例：

```json
{
    "errcode": 400,
    "errmsg": "sku 为必填参数"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/productDetailSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{"sku": "175924376", "dateRange": "past_30_days"}'
```

## 响应示例（真实响应脱敏简略）

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 1,
  "totalSales": 58357,
  "dailySales": 1945,
  "totalRevenue": 232823930.0,
  "stock": 9999,
  "startDate": "2026-06-01",
  "endDate": "2026-06-30",
  "type": "productWorkbenches",
  "costTime": 1492,
  "costToken": 16000,
  "salesTrendVOList": [
    {"date": "2026-06-01", "sales": 3233, "revenue": 11283170.0, "price": 3490.0, "stock": 9999, "reviewCount": 73482, "reviewRating": 5.0},
    {"date": "2026-06-30", "sales": 0, "revenue": 0.0, "price": 4490.0, "stock": 9999, "reviewCount": 89148, "reviewRating": 4.9}
  ],
  "categoryRanks": [
    {"date": "2026-05", "count": 46, "rank": 1},
    {"date": "2026-06", "count": 49, "rank": 1}
  ],
  "products": [
    {
      "sku": 175924376,
      "productId": 175924376,
      "title": "Яндекс Плюс на 12 месяцев",
      "price": 4490.0,
      "currency": "₽",
      "reviewRating": 4.9,
      "rating": 4.9,
      "reviewCount": 89148,
      "questionsAndAnswers": 4141,
      "brandName": "Яндекс",
      "brand": "Яндекс",
      "brandId": 13013270,
      "brandUrl": "https://www.ozon.ru/brand/13013270/",
      "sellerName": "Ozon Россия",
      "sellerId": -4,
      "fulfillment": ["OZON"],
      "upTime": 1591647267000,
      "upDays": 2214,
      "upMonths": 73,
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-g/wc500/11171014792.jpg",
      "imageUrls": ["https://ir.ozone.ru/s3/multimedia-1-g/wc500/11171014792.jpg"],
      "productUrl": "https://www.ozon.ru/product/175924376",
      "productPageUrl": "https://www.ozon.ru/product/175924376",
      "categoryInfo": {"cnTitlePath": "电影、音乐、视频游戏、软件 > 数码商品 > 订阅音乐", "enTitlePath": "Movies, Music, Video Games, Software > Digital Products > Music Subscription", "titlePath": "Кино, музыка, видеоигры, софт > Цифровые товары > Подписка на музыку", "category": {"cnTitle": "订阅音乐", "enTitle": "Music Subscription", "title": "Подписка на музыку", "level": 3, "id": "99999999_200001489_970727001", "pid": "99999999_200001489", "crossBorderSellable": false, "disabled": true}, "fullCategoryId": ["99999999", "99999999_200001489", "99999999_200001489_970727001"]},
      "monthlySalesUnits": 58357,
      "monthlySalesRevenue": 232823930.0,
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查竞品"
    }
  ],
  "data": [ "..." ]
}
```

> `data` 内容与 `products` 完全一致；`salesTrendVOList` / `categoryRanks` / `imageUrls` / `categoryInfo` 在示例中已截断，真实返回更完整。

## 字段差异（实测）

- **`monthlySalesUnits` / `monthlySalesRevenue`**：outputSchema 标注"上游无对应字段，保持 null"，但**实测会返回**，取值分别等于当前统计窗口的 `totalSales` / `totalRevenue`，可直接使用。
- **`weight`**：实物商品返回（单位 g）；数字/服务类商品（如订阅会员）实测**不返回**，使用前判空。
- **`grossMargin`**：schema 定义为毛利率，实测部分商品（如 Ozon 平台自营卖家）**不返回**，使用前判空。
- **`fulfillment` 取值**：除 `FBO` / `FBS` 外，平台自营商品可为 `["OZON"]`。

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-product-detail-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "User successfully retrieved a single Ozon product's full detail, sales trend and category rank."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE` 三选一
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER` 四选一
- `content`：用户表达、实际现象、为什么算问题或好评
