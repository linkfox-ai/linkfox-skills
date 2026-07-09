# Seerfar Ozon 关键词反查 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/keywordBackSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）
- **User-Agent**：`LinkFox-Skill/1.0`；HTTP 超时 60s

## 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。`skuIds`、`hasVariant`、`page` 为必填项，其余均可选；所有范围筛选项均为 `{min, max}` 对象，可单边或双边传值。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skuIds | array<integer> | 是 | 反查 SKU 列表，最多 20 个 |
| hasVariant | integer | 是 | 是否剔除变体：`0` 不剔除变体、`1` 剔除变体 |
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20 |
| page.orders | array | 否 | 排序规则，元素 `{field, direction}`；`direction` 取 `DESC`（倒序）/ `ASC`（正序） |
| matchType | integer | 否 | 关键词匹配模式：`0` 精准、`1` 模糊 |
| type | array<string> | 否 | 搜索词类型筛选，固定可选值：`0` 自然搜索词、`1` 广告搜索词；不传不筛选 |
| historyDate | string | 否 | 历史月份 `yyyy-MM`（如 `2026-02`）；按文档可留空查当期 |
| includeKeywords | array<string> | 否 | 包含关键词数组（最多 1000），仅返回包含指定词的搜索词 |
| excludeKeywords | array<string> | 否 | 排除关键词数组（最多 1000），剔除不相关词 |
| searchVolume | {min,max} | 否 | 月搜热度范围 |
| searchChange30 | {min,max} | 否 | 30 天搜索变化范围 |
| wordCount | {min,max} | 否 | 关键词字数范围 |
| productViews | {min,max} | 否 | 商品浏览量范围 |
| products | {min,max} | 否 | 商品数范围 |
| sellers | {min,max} | 否 | 卖家数范围 |
| marketSpace | {min,max} | 否 | 市场空间范围 |
| conversionSharing | {min,max} | 否 | 转化集中度范围 |
| uniqQueriesWCa | {min,max} | 否 | 加购数范围 |
| ca | {min,max} | 否 | 加购转化率范围 |
| conversion | {min,max} | 否 | 转化率范围 |
| titleDensity | {min,max} | 否 | 标题密度范围 |
| adRivalCount | {min,max} | 否 | 广告竞品数范围 |
| adRank | {min,max} | 否 | 广告排名范围 |
| naturalRank | {min,max} | 否 | 自然排名范围 |
| exposure | {min,max} | 否 | 曝光范围 |
| uId | string | 否 | 用户 ID |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，数据归属于 memberId） |

> **必填约束**：`skuIds`、`hasVariant`、`page` 均为必填；缺任意一项请求会被拒绝。`skuIds` 最多 20 个，超出会被拒绝或截断。
> **范围筛选**：所有 `{min,max}` 对象的两个子字段都可选，传单边即做下/上界过滤。
> **自然词 / 广告词**：`type` 用于只看自然搜索词（`["0"]`）或广告搜索词（`["1"]`）；不传则两类都返回。
> **与市场热词搜索 / 关键词挖掘的区别**：本接口为「按 SKU 反查关键词」——必须传 `skuIds`，结果是这些商品出现在哪些搜索词下及其市场画像；不支持按 `searchDate` 选月（仅 `historyDate` 历史月份）、不支持 `categories` 类目筛选、也不接收 `keyword` 种子词或 `price` 等 mining/market 独有筛选项。
> **排序**：建议通过 `page.orders` 按核心指标排序（如 `searchVolume` DESC、`sellers` ASC），避免在无序大结果集中翻页。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 总记录数 |
| data | array | 关键词反查数据（详见下方） |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应展示类型，如 `tableListWorkbenches` |

### data[*] 关键词反查对象字段

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
| marketSpace | number | 市场空间 |
| returnCancellationRate | number | 退货取消率（%） |
| uniqQueriesWCa | integer | 加购数 |
| ca | number | 加购转化率（%） |
| titleDensity | number | 标题密度 |
| wordCount | integer | 字数 |
| categories | array | 类目 ID 数组 |
| dimension | object | 维度对象，承载反查专属指标（详见下方） |
| products | array | Top 商品数据（详见下方） |
| id | string | 记录 ID |

> **字段填充（以真实响应为准）**：`dimension`（维度对象）**每行均返回**，承载反查专属指标（`type` / `naturalRank` / `exposure` / `conversion` / `x`，详见下方）。`titleDensity`（标题密度）、`wordCount`（字数）每行均返回。`productCount`（商品数）大部分行返回，个别行可能为 `null`。`relevancy`（相关度）虽在 outputSchema / `columns` 中定义，但实测 `data[*]` **不返回**；`categoryInfos`（类目信息）同样**不返回**（同族 `keywordMining` 亦不返回，`marketKeywordSearch` 返回——勿假设一致）。

#### dimension 维度对象字段

每行 `data[*]` 均返回 `dimension`，承载该搜索词相对反查 SKU 的专属指标；输入侧的 `type` / `naturalRank` / `adRank` / `exposure` / `conversion` 筛选项即作用于这些值。

| 字段 | 类型 | 说明 |
|------|------|------|
| type | integer | 搜索词渠道：`0` 自然搜索词、`1` 广告搜索词 |
| naturalRank | integer | 自然排名（反查 SKU 在该词下的自然位次） |
| exposure | number | 曝光（0–1） |
| conversion | number | 转化率（0–1） |
| x | array | 位置/分页指示，语义不透明 |

> 广告词（`type:1`）行可能额外携带 `adRank`；本次测试 SKU 仅有自然词（`type:0`，按 `type:["1"]` 查询 `total:0`），未观测到 `adRank`，使用前需判空。

#### products[*] Top 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| ozonId | integer | Ozon 商品 ID |
| sku | integer | SKU ID |
| title | string | 商品标题（俄语） |
| imageUrl | string | 主图 URL |
| advert | integer | 广告标识（0/1） |

#### categoryInfos[*] 类目信息对象字段

> ⚠️ 实测 `data[*]` 行中**不返回** `categoryInfos`（仅在 `columns` 列定义中出现）；下方字段为 outputSchema 定义，仅供出现时参考。

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
| 400 | 参数错误 | 查看 `errmsg`；常见为缺 `skuIds` / `hasVariant` / `page` 等 |
| 1002 | 参数校验失败 | 查看 `errmsg`；常见为 `skuIds` 传空数组等 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式 |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` 获取具体原因 |

错误响应示例（缺 `skuIds`）：

```json
{
    "errcode": 400,
    "errmsg": "skuIds 为必填参数"
}
```

`skuIds` 传空数组时：

```json
{
    "errcode": 1002,
    "errmsg": "参数校验失败，请检查输入。参数 skuIds 不能为空，请至少传入一个值。"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/keywordBackSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "skuIds": [4380710124],
    "hasVariant": 0,
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

## 响应示例（简略）

以 `skuIds:[4380710124]`、`hasVariant:0`、按 `searchVolume` DESC 反查的真实响应（截取 2 行，`products` 各保留 2 条）：

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 388,
  "costTime": 1376,
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
      "uniqQueriesWCa": 153707,
      "ca": 13.1,
      "titleDensity": 0.0,
      "wordCount": 3,
      "categories": ["15621031_200000933_93182"],
      "dimension": {"exposure": 0.3495, "x": [1], "naturalRank": 1, "type": 0, "conversion": 0.353},
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0},
        {"ozonId": 3042328733, "sku": 3042328733, "title": "Платье BELLA ROSA", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-3/wc300/9689632131.jpg", "advert": 0}
      ]
    },
    {
      "id": "6a4559d2d1fd12d9b57e7d19",
      "query": "платье",
      "queryCn": "裙子",
      "platform": 0,
      "searchVolume": 392783,
      "count30GrowthRate": -4.2,
      "productCount": null,
      "competingProducts": 5763,
      "sellers": 974,
      "avgPrice": 5791.0,
      "itemsViews": 99.8,
      "viewSharing": 16.2,
      "conversionSharing": 18.3,
      "marketSpace": 68,
      "returnCancellationRate": 55.4,
      "uniqQueriesWCa": 43543,
      "ca": 11.1,
      "titleDensity": 1.0,
      "wordCount": 1,
      "categories": ["15621031_200000933_93182"],
      "dimension": {"exposure": 0.1176, "x": [1], "naturalRank": 1, "type": 0, "conversion": 0.1004},
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0},
        {"ozonId": 3563361777, "sku": 3563361777, "title": "Платье SIMBAL Коллекция лето 2026", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-0/wc300/9173740572.jpg", "advert": 0}
      ]
    }
  ]
}
```

> 两行均为自然词（`dimension.type:0`）；第 2 行 `productCount` 为 `null`（部分行缺失）。`relevancy` / `categoryInfos` 在真实 `data[*]` 中不返回。

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-keyword-back-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "User successfully reverse-looked-up Ozon search keywords for a product SKU list."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE` 三选一
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER` 四选一
- `content`：用户表达、实际现象、为什么算问题或好评
