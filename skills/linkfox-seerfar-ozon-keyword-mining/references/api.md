# Seerfar Ozon 关键词挖掘 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/keywordMining`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **User-Agent**：`LinkFox-Skill/1.0`；HTTP 超时 60s

## 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。`keyword` 与 `page` 为必填项，其余均可选；所有范围筛选项均为 `{min, max}` 对象，可单边或双边传值。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 种子关键词，挖掘围绕该词展开（maxLength 1000） |
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20 |
| page.orders | array | 否 | 排序规则，元素 `{field, direction}`；`direction` 取 `DESC`（倒序）/ `ASC`（正序） |
| matchType | integer | 否 | 关键词匹配模式：`0` 精准、`1` 模糊 |
| includeKeywords | array<string> | 否 | 包含关键词数组（最多 1000），用于在种子词基础上进一步收窄/指定必须出现的词 |
| excludeKeywords | array<string> | 否 | 排除关键词数组（最多 1000），用于剔除不相关词 |
| wordCount | {min,max} | 否 | 关键词字数范围 |
| searchVolume | {min,max} | 否 | 搜索热度范围 |
| searchChange30 | {min,max} | 否 | 30 天搜索变化范围 |
| productViews | {min,max} | 否 | 商品浏览量范围 |
| products | {min,max} | 否 | 商品数范围 |
| sellers | {min,max} | 否 | 卖家数范围 |
| price | {min,max} | 否 | 价格范围 |
| marketSpace | {min,max} | 否 | 市场空间范围 |
| conversionSharing | {min,max} | 否 | 转化集中度范围 |
| relevancy | {min,max} | 否 | 相关度范围（与种子词的相关程度） |
| uniqQueriesWCa | {min,max} | 否 | 加购数范围 |
| ca | {min,max} | 否 | 加购转化率范围 |
| titleDensity | {min,max} | 否 | 标题密度范围 |
| adRivalCount | {min,max} | 否 | 广告竞品数范围 |
| uId | string | 否 | 用户 ID |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，数据归属于 memberId） |

> **必填约束**：`keyword` 与 `page` 均为必填；缺任意一项请求会被拒绝。
> **范围筛选**：所有 `{min,max}` 对象的两个子字段都可选，传单边即做下/上界过滤。
> **与市场热词搜索的区别**：本接口为「围绕种子词挖掘」——必须传 `keyword`，结果是与种子词相关的关键词及其市场画像；不支持按 `searchDate` 选月、不支持按 `categories` 类目筛选，也没有 `monthlySales` / `monthlyRevenue` / `volume` / `reviews` / `ratings` / `weight` 等筛选项。若需浏览全市场热词请改用 `marketKeywordSearch`。
> **排序**：建议通过 `page.orders` 按核心指标排序（如 `searchVolume` DESC、`sellers` ASC、`relevancy` DESC），避免在无序大结果集中翻页。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 总记录数 |
| data | array | 关键词挖掘数据（详见下方） |
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
| marketSpace | number | 市场空间 |
| returnCancellationRate | number | 退货取消率（%） |
| uniqQueriesWCa | integer | 加购数 |
| ca | number | 加购转化率（%） |
| relevancy | number | 相关度（与种子词的相关程度） |
| titleDensity | number | 标题密度 |
| wordCount | integer | 字数 |
| categories | array | 类目 ID 数组 |
| categoryInfos | array | 类目信息（详见下方） |
| products | array | Top 商品数据（详见下方） |
| id | string | 记录 ID |

> **字段填充（以真实响应为准）**：`relevancy`（相关度）、`titleDensity`（标题密度）、`wordCount`（字数）在实际响应中**均有返回** —— 相关度是种子词挖掘的核心输出，种子词本身相关度为 `100`，相关词按相关度递减。`productCount`（商品数）在大部分行返回，但与种子词完全一致的行可能缺失。`dimension`（维度信息）与 `categoryInfos`（类目信息）虽在 outputSchema / `columns` 中有定义，但 `data[*]` 行中**不返回**，使用前需判空。

#### products[*] Top 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| ozonId | integer | Ozon 商品 ID |
| sku | integer | SKU ID |
| title | string | 商品标题（俄语） |
| imageUrl | string | 主图 URL |
| advert | integer | 广告标识（0/1） |

#### categoryInfos[*] 类目信息对象字段

> ⚠️ 实测 `data[*]` 行中**未返回** `categoryInfos`（仅在 `columns` 列定义中出现）；下方字段为 outputSchema 定义，仅供出现时参考。

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
| 400 | 参数错误 | 查看 `errmsg`；常见为缺 `keyword` / `page`、关键词为空等 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 计费失败 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` 获取具体原因 |

错误响应示例（缺 `keyword`）：

```json
{
    "errcode": 400,
    "errmsg": "keyword 为必填参数",
    "keyword": ""
}
```

缺 `page` 时：

```json
{
    "errcode": 400,
    "errmsg": "page 为必填参数"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/keywordMining \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/1.0" \
  -d '{
    "keyword": "платье",
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

## 响应示例（简略）

以 `keyword:"платье"`、按 `searchVolume` DESC 挖掘的真实响应（截取 2 行，`products` 各保留 1 条）：

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 1000,
  "costTime": 4255,
  "costToken": 16000,
  "type": "tableListWorkbenches",
  "data": [
    {
      "id": "6a4559d2d1fd12d9b57e7d19",
      "query": "платье",
      "queryCn": "裙子",
      "platform": 0,
      "searchVolume": 392783,
      "count30GrowthRate": -4.2,
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
      "relevancy": 100,
      "titleDensity": 1.0,
      "wordCount": 1,
      "categories": ["15621031_200000933_93182"],
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0}
      ]
    },
    {
      "id": "6a4559bcd1fd12d9b57b6866",
      "query": "платье женское",
      "queryCn": "女装",
      "platform": 0,
      "searchVolume": 349725,
      "count30GrowthRate": -29.4,
      "productCount": 711194,
      "competingProducts": 5974,
      "sellers": 1063,
      "avgPrice": 5261.0,
      "itemsViews": 137.3,
      "viewSharing": 15.0,
      "conversionSharing": 18.8,
      "marketSpace": 59,
      "returnCancellationRate": 49.4,
      "uniqQueriesWCa": 41624,
      "ca": 11.9,
      "relevancy": 12,
      "titleDensity": 0.1,
      "wordCount": 2,
      "categories": ["15621031_200000933_93182", "15621031_200000933_93184"],
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0}
      ]
    }
  ]
}
```

> 第 1 行为种子词本身（`relevancy: 100`，无 `productCount`）；第 2 行为相关词（`relevancy: 12`，含 `productCount`）。`dimension` / `categoryInfos` 在真实 `data[*]` 中不返回。

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-keyword-mining",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "User successfully mined high-relevancy Ozon keywords around a seed term."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE` 三选一
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER` 四选一
- `content`：用户表达、实际现象、为什么算问题或好评
