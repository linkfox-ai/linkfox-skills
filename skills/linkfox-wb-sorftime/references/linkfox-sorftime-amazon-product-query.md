# `linkfox-sorftime-amazon-product-query`

## 功能与适用场景

按多个维度搜索和筛选 Amazon 产品，支持单条件、多个条件 AND 组合、分页和历史月份快照。适用于类目探索、品牌产品组合、卖家产品研究、ASIN 相似产品发现、ABA 关键词找产品、季节性产品、价格/销量/评分/排名/履约/变体筛选及历史市场对照。

此子能力面向跨产品发现和筛选；如果用户已有一个或多个 ASIN 并要看时间序列、FBA 费用明细或单品变体，改用 `linkfox-sorftime-amazon-product-detail`。

## 能力范围与限制

- 支持 US、GB、DE、FR、IN、CA、JP、ES、IT、MX、AE、AU、BR、SA，代码全部小写；英国代码为 `gb`，默认站点为 `us`。
- `marketplace` 必填；`queryMode=1` 为单条件（默认），`queryMode=2` 为多个条件的 AND 查询。
- 单条件时 `queryType` 为 1–16，`queryValue` 的格式必须匹配类型；多条件时 `queryType` 无效，`queryValue` 必须是 JSON 数组字符串。
- 每页最多 100 个产品，最多 200 页；`page` 默认 1。只有用户明确要求时才翻页。
- 价格筛选 `queryType=8` 使用货币最小单位，例如美元 19.99 写 `1999`；开区间可写 `,1000` 或 `100,`。
- `queryMonth` 为 `yyyy-MM` 历史快照。支持范围从 2024-01 起；US、GB、DE 支持完整回看，其他站点支持可能限 Top 100，AU、BR、IN 不支持回看。
- 销量/销售额估算字段为 `-1` 时表示无法估算，不能当作负销量或负销售额。
- ABA 关键词类型（`queryType=6`）只支持 ABA 关键词，不等同于通用关键词搜索量。
- 同一任务内相同 MCP `toolName + arguments` 不得重复调用；失败、空结果或参数错误不得自动换关键词、改页码或重复试探。
- 不负责单 ASIN 趋势曲线、评论正文分析、广告投放、ABA 关键词排名/搜索量、专利/商标检查或店铺履约管理。

## MCP 调用规范

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 原 endpoint：`/sorftime/amazon/productQuery`
- 精确 `toolName`：`sorftime/amazon/productQuery`，区分大小写且不带前导 `/`。
- `arguments`：直接使用本 reference 的请求参数对象，不额外包裹 `body`、`params`、`data` 或另一层 `arguments`。
- WorkBuddy 自动注入授权上下文；禁止传 `headers`、Authorization、API Key、token、JWT、手机号或其他凭证。
- 先检查 MCP 连接、工具、schema 和 `isError`，再读取 text/structured content；text JSON 只解析一次。之后检查下游 `errcode`/`errmsg`、`code`/`msg`，最后读取结果与成本字段。
- 同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或不理想结果不得自动改参、翻页或重试收费请求；追加调用前说明潜在消耗并取得用户同意。MCP 不可用时禁止 HTTP fallback。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `marketplace` | string | 是 | `us`、`gb`、`de`、`fr`、`in`、`ca`、`jp`、`es`、`it`、`mx`、`ae`、`au`、`br`、`sa`。 |
| `queryMode` | integer | 否 | `1` 单条件（默认）；`2` 多条件 AND。 |
| `queryType` | integer | 否 | 单条件查询类型 1–16；`queryMode=2` 时无效。 |
| `queryValue` | string | 否 | 单条件的值，或多条件 JSON 数组字符串。 |
| `page` | integer | 否 | 页码，默认 1，每页最多 100 条。 |
| `queryMonth` | string | 否 | 历史月份，格式 `yyyy-MM`；省略时查实时数据。 |

多条件示例的 `queryValue`：

```json
"[{\"QueryType\":1,\"Content\":\"B0CVM8TXHP\"},{\"QueryType\":8,\"Content\":\"100,500\"}]"
```

## 单条件 queryType

| queryType | 能力 | queryValue 格式 | 示例 |
|---:|---|---|---|
| 1 | ASIN 相似产品 | ASIN | `B0CVM8TXHP` |
| 2 | 类目 | NodeId | `3743561` |
| 3 | 品牌 | 品牌名 | `Anker` |
| 4 | 卖家名称 | 店铺名 | `AnkerDirect` |
| 5 | 卖家 ID | SellerId | `A294P4X9EWVXLJ` |
| 6 | ABA 关键词 | 关键词 | `Power Bank` |
| 7 | 标题/属性匹配 | 关键词 | `10,000mAh 30W` |
| 8 | 价格范围 | `min,max`，最小货币单位 | `1,1000`（约 $0.01–$10） |
| 9 | 月销量范围 | `min,max` | `100,1000` |
| 10 | 季节性产品 | 月份列表 | `1,2,3`（1–3 月旺季） |
| 11 | 上架日期范围 | `start,end`，`yyyy-MM-dd` | `2024-06-01,2024-12-01` |
| 12 | 评分范围 | `min,max` | `3,5` |
| 13 | 评论数范围 | `min,max` | `10,500` |
| 14 | 排名范围 | `bsr_min,bsr_max;sub_min,sub_max` | `500,5000;1,100` |
| 15 | 履约方式 | `FBA` / `FBM` | `FBA,FBM` |
| 16 | 变体数 | `min,max` | `1,50` |

`queryType=1` 的语义是查与给定 ASIN 相似的产品，不保证把该 ASIN 本身作为结果；指定 ASIN 详情应使用另一端点。

## 多条件组合规则

`queryMode=2` 时用 `queryValue` 传入 JSON 数组，每项键名为 `QueryType` 和 `Content`，各条件按 AND 生效，`queryType` 字段不参与查询。例如：

```json
{
  "toolName": "sorftime/amazon/productQuery",
  "arguments": {
    "marketplace": "us",
    "queryMode": 2,
    "queryValue": "[{\"QueryType\":11,\"Content\":\"2024-06-01,\"},{\"QueryType\":9,\"Content\":\"300,\"},{\"QueryType\":15,\"Content\":\"FBA\"}]"
  }
}
```

上述条件表示上架日期不早于 2024-06-01、月销量至少 300、FBA。组合前逐项核对 `Content` 格式，不要把数组作为未转义的普通文本传给外层 JSON。

## 历史快照规则

设置 `queryMonth` 可获取对应月份的产品快照，用于和不带 `queryMonth` 的实时请求比较价格、销量、排名等变化。格式必须是 `yyyy-MM`；服务支持的起始月份为 2024-01。US、GB、DE 支持完整回看；其他站点可能仅支持 Top 100；AU、BR、IN 不支持回看。收到接口关于月份或站点的限制时，以响应 `msg` 为准。

## 响应结构

响应字段来源：`skills/linkfox-sorftime-amazon-product-query/references/api.md`。

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
### products 内嵌数组/对象字段

以下层级均由来源字段说明明确给出；来源未说明具体类型时不作推断。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `products[].productImageUrls[]` | 来源未说明 | 单张商品图片 URL。 |
| `products[].size[0]` | 来源未说明 | 外包装最长边，单位 cm。 |
| `products[].size[1]` | 来源未说明 | 外包装第二长边，单位 cm。 |
| `products[].size[2]` | 来源未说明 | 外包装最短边，单位 cm。 |
| `products[].fbaDetail[0]` | 来源未说明 | FBA 配送费。 |
| `products[].fbaDetail[1...]` | 来源未说明 | 月份与仓储费，来源示例为 `"1-9:5"`、`"10-12:15"`。 |
| `products[].category[0]` | 来源未说明 | 大类名称。 |
| `products[].category[1]` | 来源未说明 | 大类 NodeId。 |
| `products[].bsrCategory[]` | object | 单个小类排名项。 |
| `products[].bsrCategory[].nodeId` | 来源未说明 | 节点 ID。 |
| `products[].bsrCategory[].name` | 来源未说明 | 类目名称。 |
| `products[].bsrCategory[].rank` | 来源未说明 | 排名。 |
| `products[].bsrCategory[].date` | 来源未说明 | 日期，格式 `yyyyMMdd`。 |

来源只称 `columns` 为渲染列数组，没有说明 `columns[]` 的元素结构，不能补猜。

## 错误码与处理

| errcode | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 解析 `products`、分页和成本字段。 |
| `401` | 认证失败 | 读取 `references/onboarding.md`，按 WorkBuddy 自动授权异常处理，不传凭证。 |
| `402` | 余额不足 | 读取 `references/onboarding.md`，引导用户自助处理，不自动查询套餐或支付。 |
| 其他非 200 | 业务或参数异常 | 根据 `msg` 修正站点、queryMode、queryType、queryValue、页码或月份；不自动改参重试。 |

错误示例：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

## MCP 请求示例

**单条件：ASIN 相似产品**

```json
{"toolName":"sorftime/amazon/productQuery","arguments":{"marketplace":"us","queryMode":1,"queryType":1,"queryValue":"B0CVM8TXHP"}}
```

**单条件：类目浏览**

```json
{"toolName":"sorftime/amazon/productQuery","arguments":{"marketplace":"us","queryMode":1,"queryType":2,"queryValue":"3743561"}}
```

**历史快照**

```json
{"toolName":"sorftime/amazon/productQuery","arguments":{"marketplace":"us","queryMode":1,"queryType":2,"queryValue":"3743561","queryMonth":"2024-11"}}
```

**多条件：新品、高销量、FBA**

```json
{"toolName":"sorftime/amazon/productQuery","arguments":{"marketplace":"us","queryMode":2,"queryValue":"[{\"QueryType\":11,\"Content\":\"2024-06-01,\"},{\"QueryType\":9,\"Content\":\"300,\"},{\"QueryType\":15,\"Content\":\"FBA\"}]"}}
```

每个示例只表示一次调用。不同月份、页码或筛选条件都是新的收费请求，不得自动追加。

## 反馈 API

当实际行为与本能力描述不符、结果不符合意图、用户表达满意/不满或提出改进建议时，按需调用独立反馈端点，不影响当前结果交付：

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- `Content-Type: application/json`
- `skillName` 使用当前 WorkBuddy 能力名 `linkfox-wb-sorftime`。
- `sentiment` 取 `POSITIVE`、`NEUTRAL` 或 `NEGATIVE`。
- `category` 取 `BUG`、`COMPLAINT`、`SUGGESTION` 或 `OTHER`。
- `content` 说明用户意图/反馈、实际表现以及问题或表扬原因。
