# linkfox-keepa-product-search

## 功能说明

通过 Keepa 商品数据库按多维条件搜索 Amazon 商品。适用于候选挖掘、类目筛选、按销量/BSR/价格过滤、低评论新品发现、品牌或配送方式筛选、包装尺寸重量约束和带历史月销/排名数据的结构化选品。

该端点是数据库条件筛选，不是实时 Amazon 搜索结果页模拟。它返回 `products[]` 及分页、排序和 `costToken` 信息；若用户已经有 ASIN，应改用 `productRequest` 或 `productSeries`。

## 能力边界与特殊规则

- `domain` 必填，未指定时使用 `1`（Amazon.com）；本端点支持的站点为 1、2、3、4、5、6、8、9、10、11，具体映射见下表。
- 关键词是标题过滤：大小写不敏感，空格表示 AND，短语可用双引号，前缀 `-` 排除，`&` 会被替换为空格；最多 50 个关键词，最大 1000 字符。
- 类目名称支持多层路径；`categoriesIncludeNames`/`categoriesExcludeNames` 建议用 `:` 或 `>` 分隔完整路径。每类根/子类目最多 50 个；传 ID 时优先使用 ID，名称只在对应 ID 数组为空时解析。
- BSR 数值越小表示排名越好。`currentSales*`、`avg90Sales*`、`srAvg*` 和 `deltaPercent90Sales*` 是排名条件，不要把它们当销量单位；`monthlySold*` 才是月销量单位。
- `currentNew*` 和 `currentBuyBoxShipping*` 的请求值使用最小货币单位（例如美元分）；展示结果时根据 `currency` 换算为站点常用价格。
- `perPage` 最小 50、最大 100；`sort` 最多 3 条，只能使用支持的字段；`history=1` 会增加响应大小和 token 消耗；失败或空结果不得自动换词、翻页或放宽条件。
- `productType`：`0` 标准产品、`1` 可下载产品、`2` 电子书、`5` 变体父 ASIN；`singleVariation=true` 时每个父商品只返回一个变体。
- 本端点不提供关键词搜索量/ABA、实时 SERP 排位、广告数据、评论正文、店铺库存或供应链数据。

## MCP 调用

- **MCP server**：`LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`）。
- **唯一工具**：`proxy_call`。
- **toolName**：`keepa/productSearch`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API Key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理错误；代理成功后读取 text/structured content，text 是 JSON 字符串时只解析一次，再检查下游 `errorCode`、`errcode`、`code`、`errmsg` 或 `msg`。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想不得自动重试、翻页、换 ASIN 或改参数探测。

## 站点参数

| domain | 站点 |
|---:|---|
| 1 | Amazon.com（美国） |
| 2 | Amazon.co.uk（英国） |
| 3 | Amazon.de（德国） |
| 4 | Amazon.fr（法国） |
| 5 | Amazon.co.jp（日本） |
| 6 | Amazon.ca（加拿大） |
| 8 | Amazon.it（意大利） |
| 9 | Amazon.es（西班牙） |
| 10 | Amazon.in（印度） |
| 11 | Amazon.com.mx（墨西哥） |

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `domain` | string | 是 | Amazon 站点 ID |
| `keyword` | string | 否 | 标题关键词；最多 50 个、最多 1000 字符，支持短语和 `-` 排除 |
| `rootCategory` / `rootCategoryNames` | array[int/string] | 否 | 根类目 ID/名称，最多 50；ID 为空时使用名称 |
| `categoriesInclude` / `categoriesIncludeNames` | array[int/string] | 否 | 包含子类目 ID/名称，最多 50，名称支持完整路径 |
| `categoriesExclude` / `categoriesExcludeNames` | array[int/string] | 否 | 排除子类目 ID/名称，最多 50 |
| `currentSalesGte` / `currentSalesLte` | integer | 否 | 当前 BSR 范围，数值越小排名越好 |
| `avg90SalesGte` / `avg90SalesLte` | integer | 否 | 90 天平均 BSR 范围 |
| `deltaPercent90SalesGte` / `deltaPercent90SalesLte` | integer | 否 | 90 天 BSR 变化百分比范围 |
| `monthlySoldGte` / `monthlySoldLte` | integer | 否 | 月销量范围 |
| `srAvgGte` / `srAvgLte` | integer | 否 | 指定历史月份的平均 BSR 范围 |
| `srAvgMonth` | string | 否 | 历史月份，`YYYYMM`，最近 36 个月内 |
| `currentNewGte` / `currentNewLte` | integer | 否 | 当前新品价格范围，最小货币单位 |
| `currentBuyBoxShippingGte` / `currentBuyBoxShippingLte` | integer | 否 | 含运费 Buy Box 价格范围，最小货币单位 |
| `currentCountReviewsGte` / `currentCountReviewsLte` | integer | 否 | 评论数范围 |
| `currentRatingGte` / `currentRatingLte` | number | 否 | 评分范围，0.0—5.0 |
| `packageLengthGte` / `packageLengthLte` | integer | 否 | 包装长度范围，毫米 |
| `packageWidthGte` / `packageWidthLte` | integer | 否 | 包装宽度范围，毫米 |
| `packageHeightGte` / `packageHeightLte` | integer | 否 | 包装高度范围，毫米 |
| `packageWeightGte` / `packageWeightLte` | integer | 否 | 包装重量范围，克 |
| `brand` / `color` / `size` | array[string] | 否 | 品牌、颜色、尺码，数组内 OR 匹配 |
| `availableDateGte` / `availableDateLte` | string | 否 | 上架日期范围，`yyyy-MM-dd` |
| `buyBoxIsAmazon` | boolean | 否 | Buy Box 卖家是否为 Amazon |
| `buyBoxIsFBA` | boolean | 否 | Buy Box 是否 FBA 配送 |
| `isHazMat` | boolean | 否 | 是否危险品 |
| `variationCountGte` / `variationCountLte` | integer | 否 | 变体数量范围 |
| `currentCountNewGte` / `currentCountNewLte` | integer | 否 | 当前新品报价数量范围 |
| `outOfStockPercentage90Gte` / `outOfStockPercentage90Lte` | integer | 否 | 90 天缺货百分比范围 |
| `singleVariation` | boolean | 否 | 是否每个父 ASIN 只返回一个变体 |
| `productType` | array[int] | 否 | `0` 标准、`1` 可下载、`2` 电子书、`5` 变体父 ASIN |
| `history` | integer | 否 | `1` 返回历史价格/排名/月销，`0` 不返回，默认 `0` |
| `rating` | integer | 否 | `1` 获取评分，`0` 不获取，默认 `1` |
| `page` | integer | 否 | 页码，从 1 开始，默认 1 |
| `perPage` | integer | 否 | 每页 50—100 条，默认 50 |
| `sort` | array[object] | 否 | 最多 3 条，格式 `{"fieldName":"...","sortDirection":"asc\|desc"}` |

支持排序字段：`availableDate`、`currentSales`、`monthlySold`、`currentRating`、`currentCountReviews`、`currentBuyBoxShipping`、`currentNew`。

## 响应字段

### 顶层字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总行数 |
| perPage | integer | 每页数量 |
| currentPage | integer | 当前页码 |
| totalCount | integer | 总数量 |
| sourceType | string | 来源类型：keepa |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| products | array | 商品列表（详见下方） |

### `products[]` 字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].asin | string | ASIN |
| products[].title | string | 商品标题 |
| products[].brand | string | 品牌 |
| products[].manufacturer | string | 制造商 |
| products[].model | string | 型号 |
| products[].price | number | 当前价格（单位：元，如美元/欧元等） |
| products[].primePrice | number | Prime价格 |
| products[].currency | string | 币种 |
| products[].salesRank | integer | 销售排名 |
| products[].salesRank30 | integer | 近30天平均销售排名 |
| products[].salesRank90 | integer | 近90天平均销售排名 |
| products[].salesRank180 | integer | 近180天平均销售排名 |
| products[].monthlySalesUnits | integer | 月销量 |
| products[].monthlySalesRevenue | number | 月销售额 |
| products[].monthlySalesUnits1MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits2MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits3MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits4MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits5MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits6MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits7MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits8MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits9MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits10MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits11MonthAgo | integer | 最近12个月每月的月销量 |
| products[].monthlySalesUnits12MonthAgo | integer | 最近12个月每月的月销量 |
| products[].rating | number | 当前评分（0.0-5.0） |
| products[].ratings | integer | 评分数量 |
| products[].reviewCount | integer | 评论数量 |
| products[].availableDate | string | 上架时间（yyyy-MM-dd HH:mm:ss） |
| products[].lastUpdate | string | 最后更新时间（yyyy-MM-dd HH:mm:ss） |
| products[].imageUrl | string | 图片URL（请求地址） |
| products[].productImageUrls | array | 商品图片列表 |
| products[].asinUrl | string | 亚马逊ASIN的详情网址 |
| products[].categoryTree | string | 类目树 |
| products[].categoryTreeId | string | 类目树ID |
| products[].rootCategory | integer | 根类目ID |
| products[].subcategories | array | 子类目列表，包含 code(类目ID)、rank(排名)、label(类目名称) |
| products[].subcategories[].code | 来源未说明 | 子类目 ID |
| products[].subcategories[].rank | 来源未说明 | 子类目排名 |
| products[].subcategories[].label | 来源未说明 | 子类目名称 |
| products[].fulfillment | string | 配送方式（AMZ, FBA, FBM） |
| products[].buyBoxSellerId | string | 购买按钮卖家ID |
| products[].sellerNum | integer | 卖家数 |
| products[].parentAsin | string | 父ASIN |
| products[].variationNum | integer | 变体数量 |
| products[].color | string | 颜色 |
| products[].dimension | string | 尺寸 |
| products[].dimensionsType | string | 尺寸类型 |
| products[].material | string | 产品的材质，指其构造中使用的主要材料 |
| products[].weight | string | 重量（克） |
| products[].packageWeight | string | 包装重量（克） |
| products[].packageLength | integer | 包装长度（毫米） |
| products[].packageWidth | integer | 包装宽度（毫米） |
| products[].packageHeight | integer | 包装高度（毫米） |
| products[].packageDimensions | string | 包装尺寸 |
| products[].packageQuantity | integer | 包装中商品的数量，不可用时为0或-1 |
| products[].itemLength | integer | 商品长度（毫米），不可用时为0或-1 |
| products[].itemWidth | integer | 商品宽度（毫米），不可用时为0或-1 |
| products[].itemHeight | integer | 商品高度（毫米），不可用时为0或-1 |
| products[].isAdultProduct | boolean | 是否为成人产品 |
| products[].isHazmat | boolean | 是否为危险品 |
| products[].referralFeePercentage | number | 推荐费百分比 |
| products[].fbaFees | number | FBA配送费（单位：元） |
| products[].profit | number | 利润率（百分比，如25.5表示25.5%） |
| products[].urlSlug | string | URL Slug |
| products[].sourceType | string | 来源类型：keepa |
| products[].sourceTool | string | 来源工具 |

## 查询构造规则

1. 先将用户国家/站点映射为 `domain`，未指定使用 `1`。
2. 将标题中的正向词放入 `keyword`，排除词以前缀 `-` 加入；多层类目优先用完整路径。
3. 将销量、BSR、价格、评分、评论数、尺寸重量和配送要求分别映射到对应的 Gte/Lte 或布尔字段。
4. 用户要求排序时使用 `sort`，不超过 3 条；需要月销历史或价格/排名历史时才设置 `history=1`。
5. 结果过少时先报告空结果和当前条件，说明放宽哪一项会产生额外调用，由用户决定，不自动试探。

## 错误处理

正常情况下 HTTP 状态为 200，业务结果通过响应体中的 `errorCode`/`errcode` 区分；未授权通常返回 HTTP 401。

| 状态/字段 | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 读取 `products`、分页字段和 `costToken` |
| `401` | 认证失败 | 读取 `references/onboarding.md`，区分 MCP/代理层与下游业务层处理 |
| `402` | 积分不足 | 读取 `references/onboarding.md`，引导用户访问 LinkFox 账号页检查积分或套餐；不自动购买 |
| 其他非 200 值 | 业务异常 | 透传 `errmsg`，检查站点、筛选范围、排序和分页 |

## MCP 示例

```json
{
    "toolName":  "keepa/productSearch",
    "arguments":  {
                      "domain":  "1",
                      "keyword":  "wireless charger",
                      "monthlySoldGte":  500,
                      "currentRatingGte":  4.0,
                      "perPage":  50
                  }
}
```

## 反馈接口

反馈接口与 Keepa 网关分离：`POST https://skill-api.linkfox.com/api/v1/public/feedback`。JSON 使用 `skillName`、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和 `content`。当结果与意图不符、出现错误、用户表扬/不满或提出改进意见时按此规则上报，不中断当前流程。

