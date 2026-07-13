# Seerfar Ozon 市场热词搜索 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/marketKeywordSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **User-Agent**：`LinkFox-Skill/1.0`；HTTP 超时 60s

## 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。除 `page` 必填外，其余均可选；所有范围筛选项均为 `{min, max}` 对象，可单边或双边传值。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20 |
| page.orders | array | 否 | 排序规则，元素 `{field, direction}`；`direction` 取 `DESC`（倒序）/ `ASC`（正序） |
| keywords | array<string> | 否 | 关键词数组（最多 1000），配合 `matchType` 使用 |
| matchType | integer | 否 | 关键词匹配模式：`0` 精准、`1` 模糊 |
| searchDate | string | 否 | 查询日期 `yyyy-MM-dd`（如 `2026-04-01`）；不传默认近 30 天，传 `2026-04-01` 查 2026 年 3 月数据 |
| categories | array<string> | 否 | 类目 ID 数组（最多 1000） |
| searchVolume | {min,max} | 否 | 搜索热度范围 |
| searchChange30 | {min,max} | 否 | 30 天搜索变化范围 |
| monthlySales | {min,max} | 否 | 月销量范围 |
| monthlyRevenue | {min,max} | 否 | 月销售额范围 |
| price | {min,max} | 否 | 价格范围 |
| productViews | {min,max} | 否 | 商品浏览量范围 |
| products | {min,max} | 否 | 商品数范围 |
| volume | {min,max} | 否 | 体量范围 |
| marketSpace | {min,max} | 否 | 市场空间范围 |
| conversionSharing | {min,max} | 否 | 转化集中度范围 |
| reviews | {min,max} | 否 | 评论数范围 |
| ratings | {min,max} | 否 | 评分范围 |
| sellers | {min,max} | 否 | 卖家数范围 |
| weight | {min,max} | 否 | 权重范围 |
| uId | string | 否 | 用户 ID |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，数据归属于 memberId） |

> **必填约束**：`page` 为唯一必填项；不传 `page` 请求会被拒绝。
> **范围筛选**：所有 `{min,max}` 对象的两个子字段都可选，传单边即做下/上界过滤。
> **排序**：建议通过 `page.orders` 按核心指标排序（如 `searchVolume` DESC、`sellers` ASC），避免在无序大结果集中翻页。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 总记录数 |
| data | array | 市场热词数据（详见下方） |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应展示类型，如 `tableListWorkbenches` |

### data[*] 关键词市场对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| query | string | 关键词（俄语原文） |
| queryCn | string | 关键词中文翻译 |
| platform | integer | 平台：`0` Ozon，`1` Wildberries |
| searchVolume | integer | 月搜热度 |
| count30GrowthRate | number | 月搜增长（%，可为负） |
| productCount | integer | 商品数（部分行可能缺失） |
| competingProducts | integer | 竞品数 |
| sellers | integer | 卖家数 |
| avgPrice | number | 平均价格 |
| itemsViews | number | 商品可见度 |
| viewSharing | number | 浏览集中度（%） |
| conversionSharing | number | 转化集中度（%） |
| marketSpace | integer | 市场空间 |
| returnCancellationRate | number | 退货取消率（%） |
| uniqQueriesWCa | integer | 加购数 |
| ca | number | 加购转化率（%） |
| categories | array | 类目 ID 数组 |
| categoryInfos | array | 类目信息（详见下方） |
| products | array | Top 商品数据（详见下方） |
| id | string | 记录 ID |

> `relevancy`（相关度）、`titleDensity`（标题密度）、`wordCount`（字数）、`dimension`（维度信息）在 outputSchema 中有定义，但实际响应中通常不返回或为 `null`，使用前需判空。

#### products[*] Top 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| ozonId | integer | Ozon 商品 ID |
| sku | integer | SKU ID |
| title | string | 商品标题（俄语） |
| imageUrl | string | 主图 URL |
| advert | integer | 广告标识（0/1） |

#### categoryInfos[*] 类目信息对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| titleCn | string | 类目中文名 |
| titleEn | string | 类目英文名 |
| titleRu | string | 类目俄语名 |
| cnTitlePath | string | 中文类目路径 |
| enTitlePath | string | 英文类目路径 |
| titlePath | string | 俄语类目路径 |
| id | string | 类目 ID |
| crossBorderSellable | boolean | 是否可跨境销售 |

## 错误码

正常情况下 HTTP 状态码为 200，业务结果通过响应体区分：
- **成功**：返回 `code:"200"` + `errcode:200`（`msg` / `errmsg` 均为 `ok`）。
- **业务错误**：HTTP 仍为 200，但仅返回 `errcode`（非 200）+ `errmsg`（原因），无 `code` 字段。
- **认证失败**：HTTP 状态码 401，响应体 `{"errcode":401,"errmsg":"authorized error"}`。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `data` 字段 |
| 400 | 参数错误 | 查看 `errmsg`；常见为缺 `page`、`searchDate` 格式错误、类目 ID 不合法等 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 计费失败 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` 获取具体原因 |

错误响应示例：

```json
{
    "errcode": 400,
    "errmsg": "page 为必填参数"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/marketKeywordSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

## 响应示例（简略）

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 506910,
  "costTime": 4706,
  "costToken": 16000,
  "type": "tableListWorkbenches",
  "data": [
    {
      "id": "6a4559b8d1fd12d9b57aacea",
      "query": "платье женское летнее",
      "queryCn": "夏季女装",
      "platform": 0,
      "searchVolume": 1167418,
      "count30GrowthRate": -4.7,
      "productCount": 519605,
      "competingProducts": 6221,
      "sellers": 974,
      "avgPrice": 2635.0,
      "itemsViews": 131.3,
      "viewSharing": 16.9,
      "conversionSharing": 17.9,
      "marketSpace": 188,
      "returnCancellationRate": 51.7,
      "ca": 13.1,
      "uniqQueriesWCa": 153707,
      "categories": ["15621031_200000933_93182"],
      "categoryInfos": [
        {
          "titleCn": "连衣裙",
          "titleEn": "Dress",
          "titleRu": "Платье",
          "cnTitlePath": "服装 > 服装 > 连衣裙",
          "enTitlePath": "Clothing > Clothing > Dress",
          "titlePath": "Одежда > Одежда > Платье",
          "id": "15621031_200000933_93182",
          "crossBorderSellable": true
        }
      ],
      "products": [
        {
          "ozonId": 4380710124,
          "sku": 4380710124,
          "title": "Платье T-SOD",
          "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg",
          "advert": 0
        }
      ],
      "dimension": null
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
  "skillName": "linkfox-seerfar-ozon-market-keyword-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "User successfully discovered high-volume low-competition Ozon keywords."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE` 三选一
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER` 四选一
- `content`：用户表达、实际现象、为什么算问题或好评
