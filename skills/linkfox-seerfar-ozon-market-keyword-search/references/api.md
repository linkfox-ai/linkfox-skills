# Seerfar Ozon 市场热词搜索 接口说明

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

## 接口：市场热词搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/marketKeywordSearch`

### 请求参数

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

#### 分页排序子字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page.orders[].field | string | 未明确 | 排序指标字段；热词用 `searchVolume` 降序，上升词用 `count30GrowthRate` 降序，低竞争用 `sellers` 升序，避免在无序大结果集中翻页。 |
| page.orders[].direction | string | 未明确 | `DESC` 倒序、`ASC` 正序。 |

#### 范围对象子字段

以下字段均继承所属范围对象的指标含义。上下界的标量类型未明确，不额外限定整数或小数；未传边界不参与过滤。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchVolume.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| searchVolume.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| searchChange30.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| searchChange30.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| monthlySales.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| monthlySales.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| monthlyRevenue.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| monthlyRevenue.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| price.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| price.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| productViews.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| productViews.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| products.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| products.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| volume.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| volume.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| marketSpace.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| marketSpace.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| conversionSharing.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| conversionSharing.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| reviews.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| reviews.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| ratings.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| ratings.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| sellers.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| sellers.max | 未明确 | 否 | 该指标上界，可单独传入。 |
| weight.min | 未明确 | 否 | 该指标下界，可单独传入。 |
| weight.max | 未明确 | 否 | 该指标上界，可单独传入。 |

#### 使用限制与脚本约定

| 项目 | 约定 |
|------|------|
| 平台筛选 | 请求无平台选择器；服务端决定 Ozon / Wildberries 数据混合情况，需要时按响应 `platform` 在客户端筛选。 |
| 类目编号 | `categories` 使用 Seerfar 类目 ID，不接受可读类目名称替代。 |
| 分页上限 | 通过 `page.page` 和 `page.pageSize` 分页；很大的 pageSize 可能被服务端截断，固定上限未明确。 |
| --inline | CLI 开关；强制完整打印，仍落盘。 |
| --no-cache | CLI 开关；跳过缓存读取和写入。默认启用 24 小时缓存，键为排序后的 JSON 参数 SHA-256 前 16 位；缓存位置为 `<cwd>/linkfox/.cache/linkfox-seerfar-ozon-market-keyword-search/`。仅公共调用器维护这一层缓存，也会缓存业务错误和空结果。 |
| 认证与网关 | 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`；`LINKFOX_TOOL_GATEWAY` 可覆盖默认网关，自动移除末尾 `/`。 |
| 会话请求头 | 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境变量。 |
| 落盘保护 | 业务入口在请求前检查当前目录、会话目录、`data` 目录及会话元数据可写，禁止 `/tmp`；完整响应使用 UTF-8 写入当前目录下的会话数据路径，不回退到家目录或临时目录。 |


### 响应结构

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

#### data[*] 关键词市场对象字段

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
| relevancy | 未明确 | 相关度；outputSchema 有定义，通常缺失或为 `null`，使用前判空。 |
| titleDensity | 未明确 | 标题密度；outputSchema 有定义，通常缺失或为 `null`，使用前判空。 |
| wordCount | 未明确 | 字数；outputSchema 有定义，通常缺失或为 `null`，使用前判空。 |
| dimension | 未明确 | 维度信息；outputSchema 有定义，通常缺失、为 `null` 或仅部分填充，使用前判空。 |

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

#### columns[*] 列定义

列定义可能不透明或仅部分填充；以下子字段的类型及更细结构未明确，应按实际响应读取，不据此补造业务数据。

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 未明确 | 列对应的字段。 |
| title | 未明确 | 列标题。 |
| cellType | 未明确 | 单元格展示类型。 |
| sortable | 未明确 | 排序标记。 |
| filterable | 未明确 | 筛选标记。 |


### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 典型成功载荷同时含 `code:"200"`、`errcode:200`，`msg` / `errmsg` 为 `ok`；这只是本接口返回形态示例，正常响应判定仍遵守公共规则。
- 业务异常可能只有 `errcode` 与 `errmsg`，没有 `code`；结合原因解释，不以 `code` 缺失单独判错。
- 脚本的本地附加字段 `_http_status` 记录本次网络请求的实际 HTTP 状态，供公共响应规则和认证/算力引导使用；它不是网关业务字段。命中缓存时，该值是缓存生成时的历史状态，`_cache.hit` 为 `true`，不代表本次发起了请求。
- 已有缓存可能没有 `_http_status`，不能据此推断 HTTP 成功，也不为补状态自动绕过缓存重发。结合 `errcode`、`errmsg` 及本地 `error` / `details` 解释结果；`error` 表示请求失败，不能仅因缺少 `errcode` 判为正常响应。如确需重新请求，先遵守成本约束。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数错误 | 查看 `errmsg`，核对是否缺少 `page`、日期格式是否正确、类目 ID 是否合法。 |
| 其他业务异常值 | 业务异常 | 查看 `errmsg` 获取原因；调整筛选或后续检索遵守 SKILL.md 成本约束。 |

### 响应示例（错误载荷）

参数错误载荷：

```json
{"errcode": 400, "errmsg": "page 为必填参数"}
```

认证失败载荷（HTTP 401）：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/marketKeywordSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

### 响应示例（简略）

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

### 筛选参数示例

以下为同一接口的不同查询意图，仅按本次任务选择一组，不默认逐一请求。

#### 高搜索、少卖家的关键词

```json
{"page":{"page":1,"pageSize":20,"orders":[{"field":"searchVolume","direction":"DESC"}]},"searchVolume":{"min":10000},"sellers":{"max":50}}
```

#### 俄语关键词模糊匹配

```json
{"page":{"page":1,"pageSize":20},"keywords":["телефон"],"matchType":1}
```

#### 指定月份及月销量下限

```json
{"page":{"page":1,"pageSize":20},"searchDate":"2026-04-01","monthlySales":{"min":1000}}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-market-keyword-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
