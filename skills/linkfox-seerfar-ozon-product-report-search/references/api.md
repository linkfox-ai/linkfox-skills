# Seerfar Ozon 商品报表搜索 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/productReportSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **User-Agent**：`LinkFox-Skill/1.0`；HTTP 超时 60s

## 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。除 `page` 必填外，其余均可选；所有范围筛选项均为 `{min, max}` 对象，可单边或双边传值。

### 分页与排序

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20 |
| page.orders | array | 否 | 排序规则，元素 `{field, direction}`；`direction` 取 `DESC`（倒序）/ `ASC`（正序）。`field` 为响应中的指标字段（如 `sales`、`revenue`、`price`、`reviewRating`、`reviewCount`、`salesRate`） |

### 筛选条件

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skus | array<integer> | 否 | SKU 数组（最多 10 个），用于精确查报指定商品 |
| keywords | array<string> | 否 | 关键词数组，按商品标题筛选 |
| categoryIds | array<string> | 否 | 类目 ID 数组（Seerfar 类目 ID，非类目名） |
| sellerName | array<string> | 否 | 卖家名称数组 |
| brand | object | 否 | 品牌筛选：`{brandName: array<string>, type: integer}`；`type` 取 `0` 包含品牌、`1` 排除品牌、`2` 无品牌 |
| fulfillment | array<string> | 否 | 配送方式数组，固定可选值：`OZON`、`FBO`、`FBS`、`RFBS`、`FBP` |
| labels | array<integer> | 否 | 标签数组，固定可选值：`0` 新品、`1` 正品、`2` 畅销品 |
| creationDate | integer | 否 | 上架时间筛选（月），固定可选值：`1` 近30天、`3` 近90天、`6` 近180天、`12` 近一年、`24` 近两年；不传不筛选 |
| variationsMerge | integer | 否 | 是否合并变体：`0` 不合并、`1` 合并 |
| searchDate | string | 否 | 查询日期 `yyyy-MM-dd`（如 `2026-04-01`）；不传默认近 30 天，传 `2026-04-01` 查 2026 年 3 月数据 |
| tag | string | 否 | 标签词 |
| uId | string | 否 | 用户 ID |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，数据归属于 memberId） |

### 范围筛选（均为 `{min, max}` 对象）

| 参数 | 筛选目标 | 单位/说明 |
|------|----------|-----------|
| monthlySales | 月销量 `sales` | 件 |
| monthlySalesRate | 销量增长率 `salesRate` | % |
| monthlyRevenue | 月销售额 `revenue` | 卢布 |
| price | 价格 `price` | 卢布 |
| convToCartPdp | 购物车转化率 `convToCartPdp` | % |
| reviewRating | 评分 `reviewRating` | 0~5 |
| reviewCount | 评论数 `reviewCount` | 条 |
| questionsAndAnswers | QA 数量 `questionsAndAnswers` | 条 |
| variants | 变体数 `variants` | 个 |
| drr | 广告费用份额 `drr` | 比例 |
| grossMargin | 毛利率 `grossMargin` | % |
| returnCancellationRate | 退货取消率 `returnCancellationRate` | % |
| weight | 重量 `weight` | g |
| volume | 体积 `volume` | L |

> **必填约束**：`page` 为唯一必填项；不传 `page` 请求会被拒绝。
> **范围筛选**：所有 `{min, max}` 对象的两个子字段都可选，传单边即做下/上界过滤。
> **排序**：数据量可达数千万，务必通过 `page.orders` 按核心指标排序后再分页，避免在无序大结果集中翻页。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 总匹配记录数（无筛选时可达数千万；按 `skus` 精确查时为命中数） |
| data | array | 商品报表数据（详见下方），与 `products` 内容完全一致 |
| products | array | 商品报表数据（与 `data` 完全一致，同一份数据的两个键） |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}`，标识可排序/可筛选字段 |
| type | string | 响应展示类型，如 `productWorkbenches` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

> **`data` 与 `products`**：两者为同一份数组，读取任一即可。
> **`total` 语义**：为整库匹配总数（而非当前页条数），无筛选时量级可达数千万，务必配合排序与分页。

### data[*] / products[*] 商品报表对象字段

**标识与基础**

| 字段 | 类型 | 说明 |
|------|------|------|
| sku | integer | 商品 SKU |
| productId | integer | 统一商品 ID（= `sku`） |
| title | string | 商品标题（俄语原文） |
| imageUrl | string | 商品主图 URL |
| productUrl | string | 商品链接 |
| productPageUrl | string | 统一商品页 URL（= `productUrl`） |
| currency | string | 币种，固定 `₽` |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具标识（如 `Seerfar-Ozon-查热销榜单`） |

**销量与销售**

| 字段 | 类型 | 说明 |
|------|------|------|
| sales | integer | 月销量 |
| monthlySalesUnits | integer | 统一月销量（= `sales`） |
| revenue | number | 月销售额（卢布） |
| monthlySalesRevenue | number | 统一月销售额（= `revenue`） |
| missedRevenue | number | 损失销售额（卢布） |
| price | number | 价格（卢布） |

**转化与增长**

| 字段 | 类型 | 说明 |
|------|------|------|
| convToCartPdp | number | 购物车转化率（%） |
| orderConversionRate | number | 下单转化率（%） |
| salesRate | number | 销量增长率（%） |
| revenueRate | number | 销售额增长率（%） |
| drr | number | 广告费用份额（比例） |
| grossMargin | number | 毛利率（%） |
| returnCancellationRate | number | 退货取消率（%） |
| views | integer | 浏览量 |

**评价与互动**

| 字段 | 类型 | 说明 |
|------|------|------|
| reviewRating | number | 评分（0~5） |
| rating | number | 统一评分（= `reviewRating`） |
| reviewCount | integer | 评论数 |
| questionsAndAnswers | integer | QA 数量 |
| variants | integer | 变体数 |

**履约与物流**

| 字段 | 类型 | 说明 |
|------|------|------|
| fulfillment | array<string> | 配送方式（取值 `OZON`/`FBO`/`FBS`/`RFBS`/`FBP`） |
| weight | number | 重量（g） |
| volume | number | 体积（L） |

**上架时间**

| 字段 | 类型 | 说明 |
|------|------|------|
| upTime | integer | 上架时间戳（毫秒） |
| upDays | integer | 上架天数 |
| upMonths | integer | 上架月数 |

**品牌与卖家**

| 字段 | 类型 | 说明 |
|------|------|------|
| brandName | string | 品牌名称 |
| brand | string | 统一品牌（= `brandName`） |
| brandId | integer | 品牌 ID |
| brandUrl | string | 品牌链接 |
| sellerName | string | 卖家名称 |
| sellerId | integer | 卖家 ID（Ozon 自营可能为负值） |
| categoryInfo | object | 类目信息（详见下方） |

### categoryInfo 类目信息对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitlePath | string | 中文类目路径 |
| enTitlePath | string | 英文类目路径 |
| titlePath | string | 俄语类目路径 |
| fullCategoryId | array<string> | 完整类目 ID 层级数组 |
| category | object | 类目节点：`{cnTitle, enTitle, title, level, id, pid, crossBorderSellable, disabled}` |

### 统一字段与原始字段对照（值完全相同）

| 统一字段 | 原始字段 |
|----------|----------|
| productId | sku |
| monthlySalesUnits | sales |
| monthlySalesRevenue | revenue |
| rating | reviewRating |
| brand | brandName |
| productPageUrl | productUrl |

> 这六对字段为同一值的两个键，读取任一即可，无需重复展示。

## 错误码

正常情况下 HTTP 状态码为 200，业务结果通过响应体区分：
- **成功**：返回 `code:"200"` + `errcode:200`（`msg` / `errmsg` 均为 `ok`）。
- **业务错误**：HTTP 仍为 200，但仅返回 `errcode`（非 200）+ `errmsg`（原因），无 `code` 字段。
- **认证失败**：HTTP 状态码 401，响应体 `{"errcode":401,"errmsg":"authorized error"}`。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `data` / `products` 字段 |
| 400 | 参数错误 | 查看 `errmsg`；常见为缺 `page`、`searchDate` 格式错误、类目 ID 不合法等 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 计费失败 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 1003 | 请求过于频繁 | 限流，等待后重试，不要通过减小 `pageSize` 绕过 |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` 获取具体原因 |

错误响应示例：

```json
{
    "errcode": 1003,
    "errmsg": "请求过于频繁，请稍后再试。"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/productReportSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "page": {"page": 1, "pageSize": 3, "orders": [{"field": "sales", "direction": "DESC"}]}
  }'
```

## 响应示例（简略）

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 27879682,
  "type": "productWorkbenches",
  "costTime": 1492,
  "costToken": 16000,
  "data": [
    {
      "sku": 2107989735,
      "productId": 2107989735,
      "title": "Туалетная Бумага ROSE 12 рулонов 3 слоя с ароматом Розы",
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-a/wc300/7814428966.jpg",
      "productUrl": "https://www.ozon.ru/product/2107989735",
      "productPageUrl": "https://www.ozon.ru/product/2107989735",
      "price": 297.0,
      "currency": "₽",
      "sales": 307524,
      "monthlySalesUnits": 307524,
      "revenue": 83095800.0,
      "monthlySalesRevenue": 83095800.0,
      "missedRevenue": 0.0,
      "salesRate": 56.0,
      "revenueRate": 58.0,
      "convToCartPdp": 25.1,
      "orderConversionRate": 87.9,
      "reviewRating": 4.9,
      "rating": 4.9,
      "reviewCount": 492242,
      "questionsAndAnswers": 277,
      "variants": 2,
      "views": 48680877,
      "drr": 0.23,
      "grossMargin": 12.7,
      "returnCancellationRate": 4.9,
      "weight": 718.0,
      "volume": 11.088,
      "upTime": 1746565200000,
      "upDays": 421,
      "upMonths": 14,
      "brandName": "Лилия",
      "brand": "Лилия",
      "brandId": 100218750,
      "brandUrl": "https://www.ozon.ru/brand/100218750",
      "sellerName": "ЛИЛИЯ",
      "sellerId": 1275208,
      "fulfillment": ["FBO"],
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查热销榜单",
      "categoryInfo": {
        "cnTitlePath": "美容和卫生 > 个人卫生用品 > 卫生纸",
        "enTitlePath": "Beauty & Hygiene > Personal Hygiene Products > Toilet Paper",
        "titlePath": "Красота и гигиена > Товары личной гигиены > Туалетная бумага",
        "fullCategoryId": ["17027489", "17027489_200001243", "17027489_200001243_93507"],
        "category": {
          "cnTitle": "卫生纸",
          "enTitle": "Toilet Paper",
          "title": "Туалетная бумага",
          "level": 3,
          "id": "17027489_200001243_93507",
          "pid": "17027489_200001243",
          "crossBorderSellable": true,
          "disabled": false
        }
      }
    }
  ]
}
```

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-product-report-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "User successfully screened high-sales low-price Ozon products."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE` 三选一
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER` 四选一
- `content`：用户表达、实际现象、为什么算问题或好评
