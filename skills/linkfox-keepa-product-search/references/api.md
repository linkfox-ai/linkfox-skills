# Keepa-亚马逊-商品搜索 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/keepa/productSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| domain | string | 是 | Amazon域名ID：1=美国, 2=英国, 3=德国, 4=法国, 5=日本, 6=加拿大, 8=意大利, 9=西班牙, 10=印度, 11=墨西哥 |
| keyword | string | 否 | 标题关键词（大小写不敏感；空格表示分词AND；关键词本身包含空格时用双引号包裹；支持前缀-排除；如果含有 & 符号会被替换为空格；最多50个关键词，最大1000字符） |
| rootCategory | array[int] | 否 | 根类目ID（最多50），仅包含列在这些根类别中的产品 |
| rootCategoryNames | array[string] | 否 | 根类目名称（最多50），当rootCategory为空时使用，系统会自动查找对应的类目ID |
| categoriesInclude | array[int] | 否 | 仅包含的子类目ID（最多50），仅包含直接列在这些子类别中的产品 |
| categoriesIncludeNames | array[string] | 否 | 包含的子类目名称（最多50），当categoriesInclude为空时使用，系统会自动查找对应的类目ID。支持传入完整类目路径（用 `:` 或 `›` 分隔），结果更准确 |
| categoriesExclude | array[int] | 否 | 排除的子类目ID（最多50） |
| categoriesExcludeNames | array[string] | 否 | 排除的子类目名称（最多50），当categoriesExclude为空时使用，系统会自动查找对应的类目ID。支持传入完整类目路径，结果更准确 |
| currentSalesGte / currentSalesLte | integer | 否 | 当前销售排名范围（数值越小排名越好） |
| avg90SalesGte / avg90SalesLte | integer | 否 | 90天平均销售排名范围 |
| deltaPercent90SalesGte / deltaPercent90SalesLte | integer | 否 | 90天销售排名变化百分比范围 |
| monthlySoldGte / monthlySoldLte | integer | 否 | 销量/月销量范围 |
| srAvgGte / srAvgLte | integer | 否 | 历史销售排名范围（正整数，数值越小排名越好，用于srAvgMonth指定月份） |
| srAvgMonth | string | 否 | 历史销售排名-选择月份（格式：YYYYMM，如202511表示2025年11月，最近36个月内） |
| currentNewGte / currentNewLte | integer | 否 | 当前新品价格范围（最小货币单位） |
| currentBuyBoxShippingGte / currentBuyBoxShippingLte | integer | 否 | 当前购买按钮含运费价格范围（最小货币单位） |
| currentCountReviewsGte / currentCountReviewsLte | integer | 否 | 当前评论数量范围 |
| currentRatingGte / currentRatingLte | number | 否 | 当前评分范围（0.0-5.0） |
| packageLengthGte / packageLengthLte | integer | 否 | 包装长度范围（毫米） |
| packageWidthGte / packageWidthLte | integer | 否 | 包装宽度范围（毫米） |
| packageHeightGte / packageHeightLte | integer | 否 | 包装高度范围（毫米） |
| packageWeightGte / packageWeightLte | integer | 否 | 包装重量范围（克） |
| brand | array[string] | 否 | 品牌（OR匹配） |
| color | array[string] | 否 | 颜色（OR匹配），筛选指定颜色的产品 |
| size | array[string] | 否 | 尺码（OR匹配），筛选指定尺码的产品 |
| availableDateGte / availableDateLte | string | 否 | 产品上架时间范围（日期格式：yyyy-MM-dd） |
| buyBoxIsAmazon | boolean | 否 | 购买按钮卖家是否为亚马逊 |
| buyBoxIsFBA | boolean | 否 | 购买按钮是否为FBA |
| isHazMat | boolean | 否 | 是否为危险品 |
| variationCountGte / variationCountLte | integer | 否 | 变体数量范围 |
| currentCountNewGte / currentCountNewLte | integer | 否 | 当前新品报价数量范围 |
| outOfStockPercentage90Gte / outOfStockPercentage90Lte | integer | 否 | 90天缺货百分比范围 |
| singleVariation | boolean | 否 | 仅返回一个变体，当设为true时，多变体产品只返回一个变体 |
| productType | array[int] | 否 | 产品类型筛选（默认[0,1,2]）：0=标准产品, 1=可下载产品, 2=电子书, 5=变体父ASIN |
| history | integer | 否 | 返回值是否包含历史数据/历史销量（1=获取, 0=不获取，默认0） |
| rating | integer | 否 | 是否获取评分信息（1=获取, 0=不获取，默认1） |
| page | integer | 否 | 页码（从1开始，默认1） |
| perPage | integer | 否 | 每页返回的最大结果数（最小50，最大100，默认50） |
| sort | array[object] | 否 | 排序（最多3）：对象数组，每项包含 `{"fieldName": "...", "sortDirection": "asc\|desc"}`。可排序字段：availableDate(上架时间)、currentSales(当前销售排名)、monthlySold(销量/月销量)、currentRating(当前评分)、currentCountReviews(当前评论数)、currentBuyBoxShipping(当前购买按钮含运费价格)、currentNew(当前新品价格) |

- 请求参数 `categoriesIncludeNames` 类目名称，支持多层级的类目名称，层级之间用英文冒号 `:` 进行分割，需要根据用户输入自动进行转换

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总行数 |
| perPage | integer | 每页数量 |
| currentPage | integer | 当前页码 |
| totalCount | integer | 总数量 |
| sourceType | string | 来源类型：keepa |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| products | array | 商品列表（详见下方） |

### 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string | 商品标题 |
| brand | string | 品牌 |
| manufacturer | string | 制造商 |
| model | string | 型号 |
| price | number | 当前价格（单位：元，如美元/欧元等） |
| primePrice | number | Prime价格 |
| currency | string | 币种 |
| salesRank | integer | 销售排名 |
| salesRank30 | integer | 近30天平均销售排名 |
| salesRank90 | integer | 近90天平均销售排名 |
| salesRank180 | integer | 近180天平均销售排名 |
| monthlySalesUnits | integer | 月销量 |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnits1MonthAgo .. monthlySalesUnits12MonthsAgo | integer | 最近12个月每月的月销量 |
| rating | number | 当前评分（0.0-5.0） |
| ratings | integer | 评分数量 |
| reviewCount | integer | 评论数量 |
| availableDate | string | 上架时间（yyyy-MM-dd HH:mm:ss） |
| lastUpdate | string | 最后更新时间（yyyy-MM-dd HH:mm:ss） |
| imageUrl | string | 图片URL（请求地址） |
| productImageUrls | array | 商品图片列表 |
| asinUrl | string | 亚马逊ASIN的详情网址 |
| categoryTree | string | 类目树 |
| categoryTreeId | string | 类目树ID |
| rootCategory | integer | 根类目ID |
| subcategories | array | 子类目列表，包含 code(类目ID)、rank(排名)、label(类目名称) |
| fulfillment | string | 配送方式（AMZ, FBA, FBM） |
| buyBoxSellerId | string | 购买按钮卖家ID |
| sellerNum | integer | 卖家数 |
| parentAsin | string | 父ASIN |
| variationNum | integer | 变体数量 |
| color | string | 颜色 |
| dimension | string | 尺寸 |
| dimensionsType | string | 尺寸类型 |
| material | string | 产品的材质，指其构造中使用的主要材料 |
| weight | string | 重量（克） |
| packageWeight | string | 包装重量（克） |
| packageLength | integer | 包装长度（毫米） |
| packageWidth | integer | 包装宽度（毫米） |
| packageHeight | integer | 包装高度（毫米） |
| packageDimensions | string | 包装尺寸 |
| packageQuantity | integer | 包装中商品的数量，不可用时为0或-1 |
| itemLength | integer | 商品长度（毫米），不可用时为0或-1 |
| itemWidth | integer | 商品宽度（毫米），不可用时为0或-1 |
| itemHeight | integer | 商品高度（毫米），不可用时为0或-1 |
| isAdultProduct | boolean | 是否为成人产品 |
| isHazmat | boolean | 是否为危险品 |
| referralFeePercentage | number | 推荐费百分比 |
| fbaFees | number | FBA配送费（单位：元） |
| profit | number | 利润率（百分比，如25.5表示25.5%） |
| urlSlug | string | URL Slug |
| sourceType | string | 来源类型：keepa |
| sourceTool | string | 来源工具 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/keepa/productSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"domain": "1", "keyword": "wireless charger", "monthlySoldGte": 500, "currentRatingGte": 4.0}'
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
