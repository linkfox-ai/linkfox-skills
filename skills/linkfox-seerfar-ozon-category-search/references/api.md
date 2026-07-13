# Seerfar Ozon 类目商品搜索 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/categorySearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **User-Agent**：`LinkFox-Skill/1.0`；HTTP 超时 60s

## 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。`categoryId` 与 `page` 必填，其余可选。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| categoryId | string | 是 | Ozon 类目 ID，从 Ozon 类目文档或其他 Seerfar Ozon 工具获取。形如 `15621032_15621049_115951147`（多级类目以 `_` 连接） |
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20，**最大 20**（超出返回 `errcode 1002`） |
| page.orders | array | 否 | 排序规则，元素 `{field, direction}`（两者均必填）；`direction` 取 `DESC`（倒序）/ `ASC`（正序）。常用排序字段：`sales`、`price`、`revenue`、`reviewRating` |
| date | string | 否 | 查询历史月份，格式 `yyyy-MM`（如 `2026-02`）；不传默认近 30 天 |
| fulfillment | string | 否 | 配送方式过滤，固定可选值：`FBO`、`FBS`、`RFBS`、`FBP`、`OZON`；不传查询全部。**注意是单个字符串，不是数组** |
| uId | string | 否 | 用户 ID（最长 1000） |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，一个用户可归属多个团队，数据归属于 memberId，最长 1000） |

> **必填约束**：`categoryId` 与 `page` 均为必填；缺任意一项返回 `errcode 400`。
> **分页上限**：`page.pageSize` 最大为 20，翻页请通过 `page.page` 递增。
> **排序**：建议通过 `page.orders` 按核心指标排序（如 `sales` DESC 看爆品、`revenue` DESC 看高销售额、`price` DESC 看高价带），避免在无序结果中翻页。
> **历史月份**：`date` 传 `yyyy-MM` 可查该月快照；不传则返回近 30 天数据，响应中 `startDate`/`endDate` 标明实际统计区间。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| id | string | 回显的类目 ID |
| total | integer | **本页返回记录数**（等于当前页 `data` 条数，并非类目商品总数） |
| totalSales | integer | 类目总销量（统计区间内） |
| totalRevenue | number | 类目总销售额（卢布） |
| avgPrice | number | 类目商品平均价格（卢布） |
| rating | number | 类目商品平均评分 |
| seasonalityAmplitude | string | 季节性强度，如 `STRONG_SEASONALITY` |
| seasonalityCoef | string | 季节性阶段，如 `OFF_SEASON` |
| startDate | string | 统计起始日期 |
| endDate | string | 统计结束日期 |
| sellerType | object | **配送方式分布**（非卖家本土/跨境类型），键为配送方式、值为该方式商品数，如 `{"FBO":218,"RFBS":528,"FBP":5,"FBS":240,"OZON":1}` |
| categoryInfo | object | 类目元信息，结构见下方「categoryInfo 结构」 |
| data | array | 类目商品列表（详见下方） |
| products | array | 类目商品列表，内容与 `data` 完全一致 |
| hasNextPage | boolean | 是否有下一页 |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| type | string | 响应展示类型 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

### data[*] / products[*] 类目商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| sku | integer | 商品 SKU |
| productId | integer | 统一商品 ID，映射自 `sku` |
| title | string | 商品标题 |
| price | number | 商品价格（卢布） |
| currency | string | 币种，固定 `₽` |
| sales | integer | 商品销量 |
| monthlySalesUnits | integer | 统一月销量，映射自 `sales` |
| revenue | number | 商品销售额 |
| monthlySalesRevenue | number | 统一月销售额，映射自 `revenue` |
| reviewRating | number | 商品评分 |
| rating | number | 统一评分，映射自 `reviewRating` |
| reviewCount | integer | 评论数 |
| brandName | string | 品牌名称 |
| brand | string | 统一品牌，映射自 `brandName` |
| sellerName | string | 卖家名称 |
| fulfillment | array | 商品配送方式，如 `["FBO"]`，可能含多个值 |
| imageUrl | string | 商品图片链接 |
| productUrl | string | 商品链接 |
| productPageUrl | string | 统一商品页 URL，映射自 `productUrl` |
| categoryInfo | object | 商品类目归属信息，结构见下方「categoryInfo 结构」 |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，如 `Seerfar-Ozon-查类目` |

> **统一字段 vs 原始字段**：`productId`/`rating`/`brand`/`monthlySalesUnits`/`monthlySalesRevenue`/`productPageUrl` 为后端统一映射字段，与原始 `sku`/`reviewRating`/`brandName`/`sales`/`revenue`/`productUrl` 等价；展示时二选一即可，建议用原始字段（语义更直观）。

### categoryInfo 结构（顶层与每个商品均返回）

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitlePath | string | 中文类目路径，如 `鞋类 > 运动鞋和工作鞋 > 举重鞋` |
| enTitlePath | string | 英文类目路径，如 `Footwear > Sports and Work Footwear > Weightlifting Shoes` |
| titlePath | string | 俄文（前台）类目路径，如 `Обувь > Спортивная и рабочая обувь > Штангетки` |
| fullCategoryId | array | 各级类目 ID 数组，如 `["15621032","15621032_15621049","15621032_15621049_115951147"]` |
| category | object | 末级类目对象，含 `cnTitle`/`enTitle`/`title`(俄文)/`level`/`crossBorderSellable`(是否可跨境销售)/`pid`/`disabled`/`id` |

> `categoryInfo` 在顶层与每个 `data[*]` 中均返回且内容一致，可用于核对类目名称（中/英/俄）与可否跨境销售（`category.crossBorderSellable`）。

## 错误码

正常情况下 HTTP 状态码为 200，业务结果通过响应体区分：
- **成功**：返回 `code:"200"` + `errcode:200`（`msg` / `errmsg` 均为 `ok`）。
- **业务错误**：HTTP 仍为 200，但仅返回 `errcode`（非 200）+ `errmsg`（原因），无 `code` 字段。
- **认证失败**：HTTP 状态码 401，响应体 `{"errcode":401,"errmsg":"authorized error"}`。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `data` / `products` 字段 |
| 400 | 参数错误 | 查看 `errmsg`；常见为缺 `categoryId`、缺 `page` |
| 1002 | 分页参数超出限制 | `page.pageSize` 最大为 20，调小后重试 |
| 1003 | 请求过于频繁 | 限流，稍后重试 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 计费失败 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` 获取具体原因 |

> **不存在的类目 ID**：传入不存在的 `categoryId` 通常返回 `errcode:200`、`total:0`、`data:[]`（空结果）。判断"类目无数据"应基于 `total=0`，而非 `errcode`。

错误响应示例：

```json
{
    "errcode": 1002,
    "errmsg": "分页参数超出限制，请检查输入。参数 page.pageSize 最大为 20，请调小后重试。"
}
```

```json
{
    "errcode": 400,
    "errmsg": "categoryId 为必填参数"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/categorySearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "categoryId": "15621032_15621049_115951147",
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "sales", "direction": "DESC"}]}
  }'
```

## 响应示例（简略）

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "id": "15621032_15621049_115951147",
  "total": 5,
  "totalSales": 2066,
  "totalRevenue": 12973043,
  "avgPrice": 7228.0,
  "rating": 4.9,
  "seasonalityAmplitude": "STRONG_SEASONALITY",
  "seasonalityCoef": "OFF_SEASON",
  "startDate": "2026-06-01",
  "endDate": "2026-07-01",
  "hasNextPage": true,
  "type": "productWorkbenches",
  "costTime": 1415,
  "costToken": 16000,
  "sellerType": {"FBO": 218, "RFBS": 528, "FBP": 5, "FBS": 240, "OZON": 1},
  "categoryInfo": {
    "cnTitlePath": "鞋类 > 运动鞋和工作鞋 > 举重鞋",
    "enTitlePath": "Footwear > Sports and Work Footwear > Weightlifting Shoes",
    "titlePath": "Обувь > Спортивная и рабочая обувь > Штангетки",
    "fullCategoryId": ["15621032", "15621032_15621049", "15621032_15621049_115951147"],
    "category": {
      "cnTitle": "举重鞋", "enTitle": "Weightlifting Shoes", "title": "Штангетки",
      "level": 3, "crossBorderSellable": true, "pid": "15621032_15621049",
      "disabled": false, "id": "15621032_15621049_115951147"
    }
  },
  "data": [
    {
      "sku": 1546459445,
      "productId": 1546459445,
      "title": "Штангетки YOUNGS",
      "price": 6481.0,
      "currency": "₽",
      "sales": 21,
      "monthlySalesUnits": 21,
      "revenue": 122635.0,
      "monthlySalesRevenue": 122635.0,
      "reviewRating": 4.8,
      "rating": 4.8,
      "reviewCount": 524,
      "brandName": "YOUNGS",
      "brand": "YOUNGS",
      "sellerName": "YoungS shoes",
      "fulfillment": ["FBO"],
      "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-j/wc300/7000839379.jpg",
      "productUrl": "https://www.ozon.ru/product/1546459445",
      "productPageUrl": "https://www.ozon.ru/product/1546459445",
      "categoryInfo": { "...": "同顶层 categoryInfo" },
      "sourceType": "ozon",
      "sourceTool": "Seerfar-Ozon-查类目"
    }
  ],
  "products": [ "..." ],
  "columns": [ { "field": "sku", "title": "商品SKU", "cellType": "number", "sortable": true, "filterable": true } ]
}
```

> `products` 内容与 `data` 完全一致，示例中用 `"..."` 表示省略。`total` 为本页返回记录数（本例 5），并非类目商品总数；`hasNextPage=true` 表示还有更多页。`sellerType` 为配送方式分布（非卖家本土/跨境类型）。

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-category-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "User successfully retrieved a category's best-sellers, total sales/revenue and average price for category selection analysis."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE` 三选一
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER` 四选一
- `content`：用户表达、实际现象、为什么算问题或好评
