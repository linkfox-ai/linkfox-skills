# Seerfar Ozon 商品详情搜索 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 接口：商品详情搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/productDetailSearch`

### 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sku | string | 是 | 商品 SKU（Ozon SKU，如 `175924376`）。即其他 Seerfar Ozon 工具返回的 `sku` |
| dateRange | string | 否 | 销量/指标统计窗口，默认 `past_30_days`。可选：`past_7_days` / `past_30_days` / `past_60_days` / `past_90_days` / `past_180_days` / `past_365_days` |
| uId | string | 否 | 用户 ID（最长 1000） |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，一个用户可归属多个团队，数据归属于 memberId，最长 1000） |

#### 使用限制

- **单 SKU 查询**：本接口一次只查一个商品详情，无批量/列表模式。
- **窗口仅作用于销量聚合**：`dateRange` 只影响 `totalSales` / `dailySales` / `totalRevenue` / `salesTrendVOList` / `startDate` / `endDate` 等销量类字段；商品元数据（标题、价格、评分、品牌、卖家、重量、配送方式等）为当下快照，不受窗口影响。
- **估算数据**：销量和销售额为 Seerfar 在所选窗口内的模型估算，不是 Ozon 官方数据。

#### 脚本选项与运行约定

| 参数／选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | string | 是 | 首个位置参数为请求 JSON，字段见上表；缺少参数或 JSON 无效时退出码为 1。 |
| --inline | CLI flag | 否 | 强制完整打印到标准输出，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次响应缓存的读取和写入；不影响会话数据落盘。 |

默认保留 24 小时本地缓存：目录为 `<cwd>/linkfox/.cache/linkfox-seerfar-ozon-product-detail-search/`，缓存文件名为 `linkfox-seerfar-ozon-product-detail-search-<hash>.json`，`hash` 为原始参数按键排序、保留中文序列化后 SHA-256 的前 16 位。缓存命中时在响应中标记 `_cache.hit=true`。包括错误和空结果在内的 JSON 响应均会缓存；不自动绕过缓存反复请求。缓存仅由公共调用器维护，无第二层缓存。

脚本以 UTF-8 保存响应，执行方式及大小分流见 `../SKILL.md`。业务脚本在请求前检查当前目录下的 `linkfox/` 可写性，固定输出在该目录；禁止写入 `/tmp`，不可写时报错，不回退到其他目录。Windows 下运行期间使用同一工作目录的扩展路径写法（本地路径或 UNC 路径），兼容深层目录的缓存与响应保存；结束时恢复原工作目录，不改变缓存位置或增加缓存层。`LINKFOX_TOOL_GATEWAY` 优先于默认网关，两种 API Key 环境变量及 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头均保持兼容。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码；成功响应为 `200`，与 `code` 并存。业务错误通常仍为 HTTP 200，仅返回 `errcode` 和 `errmsg`，不含 `code`；响应判断遵循公共规则。 |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述；HTTP 401 示例为 `{"errcode":401,"errmsg":"authorized error"}`。 |
| total | integer | 返回记录数（命中时为 `1`，未命中为 `0`），不是商品目录总数 |
| totalSales | integer | 统计窗口内总销量 |
| dailySales | number | 平均每天销量（≈ totalSales / 窗口天数） |
| totalRevenue | number | 统计窗口内销售额（卢布） |
| stock | integer | 库存 |
| startDate | string | 统计窗口起始日期（如 `2026-06-01`） |
| endDate | string | 统计窗口结束日期（如 `2026-06-30`） |
| salesTrendVOList | array | 每日销量数据序列（见下方） |
| categoryRanks | array | 商品类目排名历史（见下方） |
| products | array | 商品详情列表（单 SKU 查询命中时 1 条，未命中为空） |
| data | array | 返回数据，内容与 `products` 完全一致；命中时各含 1 条记录，展示时避免重复计数。 |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| type | string | 响应展示类型，如 `productWorkbenches` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |

#### products[*] / data[*] 商品对象字段

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
| fulfillment | array | 商品配送方式，可含 `FBO` / `FBS`；平台自营商品还可为 `["OZON"]`，可能含多个值。 |
| upTime | integer | 上架时间，毫秒时间戳 |
| upDays | integer | 上架天数 |
| upMonths | integer | 上架月数 |
| imageUrl | string | 统一主图 URL，映射自 `imageUrls` 首张 |
| imageUrls | array | 商品图片 URL 列表 |
| productUrl | string | 商品 URL |
| productPageUrl | string | 统一商品页 URL，映射自 `productUrl` |
| categoryInfo | object | 商品类目信息（见下方） |
| monthlySalesUnits | integer | 统一月销量；实际响应取值等于当前统计窗口的 `totalSales`，可直接使用，不固定为自然月；outputSchema 中“上游无对应字段，保持 null”的标注不适用于该返回值。 |
| monthlySalesRevenue | number | 统一月销售额；实际响应取值等于当前统计窗口的 `totalRevenue`，可直接使用，不固定为自然月；outputSchema 中“上游无对应字段，保持 null”的标注不适用于该返回值。 |
| sourceType | string | 数据源，固定 `ozon` |
| sourceTool | string | 来源工具，标识 Seerfar Ozon 接口（如 `Seerfar-Ozon-查竞品`） |
| weight | number | 商品重量，单位 g；实物商品返回，数字/服务类商品（如订阅会员）不返回，使用前判空。 |
| grossMargin | number | schema 定义的毛利率；部分商品（如 Ozon 平台自营卖家）不返回，使用前判空。 |

#### salesTrendVOList[*] 每日销量对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期（如 `2026-06-01`） |
| sales | integer | 当日销量（可能为 `0`） |
| revenue | number | 当日销售额（卢布） |
| price | number | 当日价格（卢布） |
| stock | integer | 当日库存 |
| reviewCount | integer | 截至当日评论数（累计） |
| reviewRating | number | 截至当日评分 |

#### categoryRanks[*] 类目排名对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 月份（如 `2026-02`；当月为具体日期 `2026-07-01`） |
| rank | integer | 类目排名 |
| count | integer | 统计计数（以网关实际口径为准） |

> `categoryRanks` 仅含 `date` / `rank` / `count`，不含类目名称；类目名称/路径请取自 `categoryInfo`。

#### categoryInfo 类目信息对象

| 字段 | 类型 | 说明 |
|------|------|------|
| cnTitlePath | string | 中文类目路径 |
| enTitlePath | string | 英文类目路径 |
| titlePath | string | 类目路径（原文） |
| category | object | 末级类目对象（字段见下方） |
| fullCategoryId | array | 完整类目 ID 路径（字符串数组，根→末级，如 `["99999999", "99999999_200001489", "99999999_200001489_970727001"]`） |

##### category 对象字段

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

#### columns[*] 列定义对象

列定义包含以下字段；字段类型以实际响应为准，不预设类型。

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 未注明 | 列对应的字段名。 |
| title | 未注明 | 列标题。 |
| cellType | 未注明 | 单元格类型。 |
| sortable | 未注明 | 是否可排序。 |
| filterable | 未注明 | 是否可筛选。 |

#### 脚本缓存标记

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅缓存命中时由脚本加入的本地元信息，不是接口业务字段。 |
| _cache.hit | boolean | 缓存命中时为 true。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

> 未命中的 SKU：返回成功（`code:"200"`、`errcode:200`），但 `total:0`、`products:[]`，且销量聚合字段（`totalSales` / `dailySales` / `totalRevenue` / `stock` / `startDate` / `endDate`）不返回。判断"商品无数据"应基于 `total=0` 或 `products` 为空，而非 `errcode`。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数错误 | 查看 `errmsg`；缺少 `sku` 时为 `sku 为必填参数`。 |
| 1003 | 请求过于频繁 | 稍候重试，遵守成本约束，不自动反复请求。 |

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/productDetailSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"sku": "175924376", "dateRange": "past_30_days"}'
```

### 响应示例（脱敏简略）

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

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-product-detail-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```