# Sorftime 亚马逊产品搜索 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/amazon/productQuery`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 亚马逊站点代码：us、gb、de、fr、in、ca、jp、es、it、mx、ae、au、br、sa |
| queryMode | integer | 否 | 查询方式。`1`：单条件查询（默认）；`2`：多条件组合查询（且关系） |
| queryType | integer | 否 | 查询类型（1-16），仅当 queryMode=1 时生效。详见 SKILL.md 中 Query Types 完整说明 |
| queryValue | string | 否 | 查询条件值，格式根据 queryMode 和 queryType 不同而变化。详见 SKILL.md 中各 queryType 的格式说明 |
| page | integer | 否 | 分页页码，默认1。每页最多100个产品 |
| queryMonth | string | 否 | 回看历史月份，格式 `yyyy-MM`。不指定时查实时数据 |

- 当 `queryMode=2`（多条件组合查询）时，`queryType` 无效；所有条件通过 `queryValue` 传入 JSON 数组：`[{"QueryType":1,"Content":"B0CVM8TXHP"},{"QueryType":8,"Content":"100,500"}]`
- 当用户明确要求翻页时，调整 `page` 参数

## 响应结构

### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 响应码（200表示成功） |
| msg | string | 响应消息 |
| total | integer | 结果总数 |
| page | integer | 当前页码 |
| pageCount | integer | 总页数（最多200页） |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗Token数量 |
| requestConsumed | integer | 消耗的请求数 |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| products | array | 产品列表（详见下方） |

### 商品对象字段（products 数组元素）

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string | 商品标题 |
| brand | string | 品牌 |
| asinUrl | string | 商品链接，亚马逊Listing详情页URL |
| imageUrl | string | 主图URL |
| productImageUrls | array | 主图列表（所有商品图片URL） |
| parentAsin | string | 父ASIN，有子体时为父级ASIN，无子体时为null |
| variationNum | integer | 变体数 |
| weight | string | 重量，单位g |
| size | array | 尺寸，外包装[最长边,第二长边,最短边]，单位cm |
| price | number | 当前价格，未扣Coupon，单位为当地货币(如美元) |
| oldPrice | number | 划线价，单位为当地货币(如美元) |
| salesPrice | number | 到手价，扣除Coupon后的实际售价，单位为当地货币(如美元) |
| coupon | integer | Coupon政策。值>=0为抵扣金额(如500=$5)，值<0为折扣百分比(如-10=10%折扣) |
| fbaFees | number | FBA费用，单位为当地货币(如美元) |
| fbaDetail | array | FBA明细。首项为配送费，后续为月份:仓储费，如[475,"1-9:5","10-12:15"] |
| platformFee | number | 平台佣金，单位为当地货币(如美元) |
| profitAmount | number | 利润，到手价-FBA费-佣金，单位为当地货币(如美元) |
| profitRate | number | 利润率，例25.83表示25.83% |
| monthlySalesUnits | integer | 月销量，近30日Listing维度不区分子体，推荐用于评估销量，值为-1表示无法预估 |
| monthlySalesRevenue | number | 月销售额，预估值，单位为当地货币(如美元)，值为-1表示无法预估 |
| listingSalesVolumeOfDaily | integer | 日销量，Listing维度不区分子体，值为-1表示无法预估 |
| listingSalesOfDaily | number | 日销售额，单位为当地货币(如美元)，值为-1表示无法预估 |
| salesRank | integer | BSR排名，大类排名 |
| category | array | 大类，[大类名称, NodeId] |
| bsrCategory | array | 小类排名列表，每项包含 nodeId（节点ID）、name（类目名称）、rank（排名）、date（日期，格式yyyyMMdd） |
| rating | number | 当前评分（0.0-5.0，如4.8） |
| ratings | integer | 评分数量 |
| availableDate | string | 上架时间，格式yyyy-MM-dd |
| onlineDays | integer | 上架天数 |
| buyboxSeller | string | Buybox卖家名称 |
| buyBoxSellerId | string | Buybox卖家ID |
| buyboxSellerAddress | string | 卖家所在地，Buybox卖家国籍(二字码如CN、US)，亚马逊自营时为null |
| isFBA | boolean | 是否FBA，Buybox卖家是否使用FBA物流 |
| sellerNum | integer | 卖家数 |
| aPlus | boolean | 有A+ |
| hasVideo | boolean | 有视频 |
| hasBrandStore | boolean | 有品牌店 |


## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 code 字段区分（code = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errcode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` 等业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 402 | 余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 其他非200值 | 业务异常 | 参考 `msg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

**单条件 - ASIN同类产品：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 1, "queryValue": "B0CVM8TXHP"}'
```

**单条件 - 类目浏览：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 2, "queryValue": "3743561"}'
```

**单条件 - 品牌热销产品：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 3, "queryValue": "Anker"}'
```

**单条件 - 历史快照回看：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 1, "queryType": 2, "queryValue": "3743561", "queryMonth": "2024-11"}'
```

**多条件组合 - 新品+高销量+FBA：**

```bash
curl -X POST https://tool-gateway.linkfox.com/sorftime/amazon/productQuery \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "queryMode": 2, "queryValue": "[{\"QueryType\":11,\"Content\":\"2024-06-01,\"},{\"QueryType\":9,\"Content\":\"300,\"},{\"QueryType\":15,\"Content\":\"FBA\"}]"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-sorftime-product-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE - `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE - `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
