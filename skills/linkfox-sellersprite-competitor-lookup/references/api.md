# 卖家精灵-查竞品 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/competitor-lookup`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 否 | 亚马逊站点代码，默认 `US`。可选值：US、UK、DE、FR、JP、CA、IT、ES、MX、AU、TR、IN |
| keyword | string | 否 | 搜索关键词。请尽量翻译为对应国家的语言，比如美国用英语关键词，德国用德语关键词等 |
| asinList | string | 否 | ASIN，多个ASIN使用英文逗号分隔，最多40个。格式：`^[A-Z0-9]+(,[A-Z0-9]+){0,39}$` |
| sellerName | string | 否 | 卖家名称筛选 |
| brand | string | 否 | 品牌名称筛选 |
| nodeLabel | string | 否 | 亚马逊类目名称，支持多层级类目名称，层级之间用英文冒号 `:` 分割，例如 `Electronics:Headphones` |
| nodeIdPath | string | 否 | 亚马逊类目ID路径 |
| matchType | integer | 否 | 匹配方式。1 = 词组匹配（默认），2 = 模糊匹配，3 = 精准匹配 |
| showVariation | string | 否 | 是否查询变体。`Y` = 是，`N` = 否（默认） |
| dataSnapshotMonth | string | 否 | 亚马逊商品数据快照年月。默认 `nearly`（查询最近30天实时数据）。使用 `yyyyMM` 格式查询历史快照（如 `202412` 表示2024年12月）。仅支持已存在的历史快照，不支持未来日期。建议季节性分析时查询去年同期快照进行对比 |
| page | integer | 否 | 页码，从1开始（默认1） |
| size | integer | 否 | 每页条数，返回10-100条数据（默认50） |
| order | object | 否 | 排序配置（见下方说明） |

### 排序对象（order）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| field | string | 是 | 排序字段。可选值：`total_units`（月销量）、`total_amount`（月销售额）、`bsr_rank`（BSR排名）、`price`（价格）、`rating`（评分）、`reviews`（评分数）、`profit`（毛利率）、`reviews_rate`（留评率）、`available_date`（上架时间）、`questions`（Q&A数）、`total_units_growth`（月销量增长率）、`total_amount_growth`（月销售额增长率）、`reviews_increasement`（月新增评分数）、`bsr_rank_cv`（近7天BSR增长数）、`bsr_rank_cr`（近7天BSR增长率）、`amz_unit`（子体销量）。默认：`total_units` |
| desc | string | 是 | 排序方向。`true` = 降序，`false` = 升序。默认：`true` |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 匹配结果总数 |
| sourceType | string | 来源类型（如 `amazon`） |
| message | string | 执行消息或错误描述 |
| type | string | 渲染样式 |
| nodeLabel | string | 类目名称回显 |
| columns | array | 渲染的列定义 |
| products | array | 竞品列表（见下方说明） |
| costToken | integer | 消耗token |

### 竞品对象字段（products）

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 商品ASIN |
| title | string | 商品标题 |
| price | number | 当前价格 |
| primePrice | number | Prime价格 |
| averagePrice | number | 平均价格 |
| currency | string | 币种 |
| monthlySalesUnits | integer | 月销量（件数） |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| bsr | integer | BSR排名 |
| bsrGrowthRate | number | BSR增长率 |
| bsrGrowthCount | integer | BSR增长数 |
| rating | number | 评分 |
| ratings | integer | 评分数 |
| ratingsGrowth | integer | 月新增评分数 |
| ratingsRate | number | 留评率 |
| brand | string | 品牌 |
| brandUrl | string | 品牌URL |
| sellerName | string | BuyBox卖家名称 |
| sellerId | string | BuyBox卖家ID |
| sellerNation | string | BuyBox卖家国籍 |
| sellerNum | integer | 卖家数 |
| fulfillment | string | 配送方式：AMZ、FBA、FBM |
| availableDate | string | 上架时间（日期格式） |
| availableDateString | string | 上架日期（字符串格式） |
| profit | number | 毛利率 |
| fba | number | FBA运费 |
| deliveryPrice | number | 卖家运费 |
| imageUrl | string | 商品图片URL |
| parent | string | 父体ASIN |
| variationNum | integer | 变体数 |
| variant30DayUnits | integer | 子体月销量（件数） |
| variant30DayRevenue | number | 子体月销售额 |
| variant30DayUpdatedAt | string | 子体数据更新时间（时间戳） |
| amzUnitDateString | string | 子体销量更新日期 |
| listingQualityScore | number | Listing质量得分 |
| nodeLabelPath | string | 类目路径 |
| nodeIdPath | string | 节点ID路径 |
| nodeId | integer | 节点ID |
| dimension | string | 商品尺寸 |
| dimensionsType | string | 尺寸类型 |
| weight | string | 商品重量 |
| packageDimensions | string | 包装尺寸 |
| packageDimensionType | string | 包装尺寸类型 |
| packageWeight | string | 包装重量 |
| sku | string | SKU |
| keyword | string | 匹配的关键词（如通过关键词搜索，则显示对应关键词） |
| dataSnapshotMonth | string | 数据查询月份 |
| sourceTool | string | 来源工具 |
| sourceType | string | 来源类型 |
| badgeBestSeller | string | Best Seller标识（Y/N） |
| badgeAmazonChoice | string | Amazon's Choice标识（Y/N） |
| badgeNewRelease | string | New Release标识（Y/N） |
| badgeEbc | string | A+页面（Y/N） |
| badgeVideo | string | 视频介绍（Y/N） |
| badge | object | 标识详情对象，包含：`bestSeller`、`amazonChoice`、`newRelease`、`ebc`、`video`（均为 Y/N 字符串） |
| subcategories | array | 子类目排名，每项包含 `code`（类目code）、`rank`（排名）、`label`（名称） |

## curl 示例

### 关键词搜索

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/competitor-lookup \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "US", "keyword": "wireless earbuds", "matchType": 1, "size": 20}'
```

### ASIN查询

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/competitor-lookup \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "US", "asinList": "B072MQ5BRX,B08N5WRWNW"}'
```

### 按月销售额排序并分页

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/competitor-lookup \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "US", "keyword": "phone case", "order": {"field": "total_amount", "desc": "true"}, "page": 1, "size": 50}'
```

### 历史快照查询

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/competitor-lookup \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "US", "keyword": "space heater", "dataSnapshotMonth": "202412", "order": {"field": "total_units", "desc": "true"}, "size": 20}'
```

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` 等业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
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
