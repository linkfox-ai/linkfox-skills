# Keepa 亚马逊商品搜索 接口说明

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

## 接口：商品搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/keepa/productSearch`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| domain | string | 是 | Amazon域名ID：1=美国, 2=英国, 3=德国, 4=法国, 5=日本, 6=加拿大, 8=意大利, 9=西班牙, 10=印度, 11=墨西哥；构造请求时必须传入，用户未指定站点时使用 "1"（美国） |
| keyword | string | 否 | 标题关键词（大小写不敏感；空格表示分词AND；关键词本身包含空格时用双引号包裹；支持前缀-排除；如果含有 & 符号会被替换为空格；最多50个关键词，最大1000字符） |
| rootCategory | array[int] | 否 | 根类目ID（最多50），仅包含列在这些根类别中的产品 |
| rootCategoryNames | array[string] | 否 | 根类目名称（最多50），当rootCategory为空时使用，系统会自动查找对应的类目ID |
| categoriesInclude | array[int] | 否 | 仅包含的子类目ID（最多50），仅包含直接列在这些子类别中的产品 |
| categoriesIncludeNames | array[string] | 否 | 包含的子类目名称（最多50），当categoriesInclude为空时使用，系统会自动查找对应的类目ID。支持传入完整类目路径（用 `:` 或 `›` 分隔；用户输入 `>` 时统一转换为英文冒号 `:`），结果更准确 |
| categoriesExclude | array[int] | 否 | 排除的子类目ID（最多50） |
| categoriesExcludeNames | array[string] | 否 | 排除的子类目名称（最多50），当categoriesExclude为空时使用，系统会自动查找对应的类目ID。支持传入完整类目路径，结果更准确 |
| currentSalesGte | integer | 否 | 当前销售排名范围（数值越小排名越好）（下限） |
| currentSalesLte | integer | 否 | 当前销售排名范围（数值越小排名越好）（上限） |
| avg90SalesGte | integer | 否 | 90天平均销售排名范围（下限） |
| avg90SalesLte | integer | 否 | 90天平均销售排名范围（上限） |
| deltaPercent90SalesGte | integer | 否 | 90天销售排名变化百分比范围（下限） |
| deltaPercent90SalesLte | integer | 否 | 90天销售排名变化百分比范围（上限） |
| monthlySoldGte | integer | 否 | 销量/月销量范围（下限） |
| monthlySoldLte | integer | 否 | 销量/月销量范围（上限） |
| srAvgGte | integer | 否 | 历史销售排名范围（正整数，数值越小排名越好，用于srAvgMonth指定月份）（下限） |
| srAvgLte | integer | 否 | 历史销售排名范围（正整数，数值越小排名越好，用于srAvgMonth指定月份）（上限） |
| srAvgMonth | string | 否 | 历史销售排名-选择月份（格式：YYYYMM，如202511表示2025年11月，最近36个月内） |
| currentNewGte | integer | 否 | 当前新品价格范围（最小货币单位）（下限） |
| currentNewLte | integer | 否 | 当前新品价格范围（最小货币单位）（上限） |
| currentBuyBoxShippingGte | integer | 否 | 当前购买按钮含运费价格范围（最小货币单位）（下限） |
| currentBuyBoxShippingLte | integer | 否 | 当前购买按钮含运费价格范围（最小货币单位）（上限） |
| currentCountReviewsGte | integer | 否 | 当前评论数量范围（下限） |
| currentCountReviewsLte | integer | 否 | 当前评论数量范围（上限） |
| currentRatingGte | number | 否 | 当前评分范围（0.0-5.0）（下限） |
| currentRatingLte | number | 否 | 当前评分范围（0.0-5.0）（上限） |
| packageLengthGte | integer | 否 | 包装长度范围（毫米）（下限） |
| packageLengthLte | integer | 否 | 包装长度范围（毫米）（上限） |
| packageWidthGte | integer | 否 | 包装宽度范围（毫米）（下限） |
| packageWidthLte | integer | 否 | 包装宽度范围（毫米）（上限） |
| packageHeightGte | integer | 否 | 包装高度范围（毫米）（下限） |
| packageHeightLte | integer | 否 | 包装高度范围（毫米）（上限） |
| packageWeightGte | integer | 否 | 包装重量范围（克）（下限） |
| packageWeightLte | integer | 否 | 包装重量范围（克）（上限） |
| brand | array[string] | 否 | 品牌（OR匹配） |
| color | array[string] | 否 | 颜色（OR匹配），筛选指定颜色的产品 |
| size | array[string] | 否 | 尺码（OR匹配），筛选指定尺码的产品 |
| availableDateGte | string | 否 | 产品上架时间范围（日期格式：yyyy-MM-dd）（下限） |
| availableDateLte | string | 否 | 产品上架时间范围（日期格式：yyyy-MM-dd）（上限） |
| buyBoxIsAmazon | boolean | 否 | 购买按钮卖家是否为亚马逊 |
| buyBoxIsFBA | boolean | 否 | 购买按钮是否为FBA |
| isHazMat | boolean | 否 | 是否为危险品 |
| variationCountGte | integer | 否 | 变体数量范围（下限） |
| variationCountLte | integer | 否 | 变体数量范围（上限） |
| currentCountNewGte | integer | 否 | 当前新品报价数量范围（下限） |
| currentCountNewLte | integer | 否 | 当前新品报价数量范围（上限） |
| outOfStockPercentage90Gte | integer | 否 | 90天缺货百分比范围（下限） |
| outOfStockPercentage90Lte | integer | 否 | 90天缺货百分比范围（上限） |
| singleVariation | boolean | 否 | 仅返回一个变体，当设为true时，多变体产品只返回一个变体 |
| productType | array[int] | 否 | 产品类型筛选（默认[0,1,2]）：0=标准产品, 1=可下载产品, 2=电子书, 5=变体父ASIN |
| history | integer | 否 | 返回值是否包含历史数据/历史销量（1=获取, 0=不获取，默认0） |
| rating | integer | 否 | 是否获取评分信息（1=获取, 0=不获取，默认1） |
| page | integer | 否 | 页码（从1开始，默认1） |
| perPage | integer | 否 | 每页返回的最大结果数（最小50，最大100，默认50） |
| sort | array[object] | 否 | 排序（最多3）：对象数组，每项包含 `{"fieldName": "...", "sortDirection": "asc\|desc"}`。可排序字段：availableDate(上架时间)、currentSales(当前销售排名)、monthlySold(销量/月销量)、currentRating(当前评分)、currentCountReviews(当前评论数)、currentBuyBoxShipping(当前购买按钮含运费价格)、currentNew(当前新品价格) |

#### 排序对象字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sort[].fieldName | string | 是（传排序对象时） | 排序字段，枚举见上方 `sort` 行。 |
| sort[].sortDirection | string | 是（传排序对象时） | `asc` 升序或 `desc` 降序。 |

#### 参数单位与使用限制

- `Gte` 为下限，`Lte` 为上限；BSR 数值越小排名越好，历史月份排名上下界须为正整数。
- 请求中的价格均为最小货币单位，例如美元 25.99 对应 2599；包装尺寸用毫米、重量用克。响应金额的口径见响应字段表。
- `categoriesIncludeNames` 支持多层级类目；按用户输入自动转换为英文冒号 `:` 分隔的路径，避免将层级拆成互不相关的类目。
- `history=1` 会明显增加响应体积和 token 消耗，仅在需要历史价格、排名或月销量时开启。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 原样传递上述请求参数；脚本不擅自注入站点、筛选或分页条件。 |
| --inline | CLI flag | 否 | 强制全量打印，完整响应仍保存文件。 |
| --no-cache | CLI flag | 否 | 关闭本次响应缓存读取与写入；默认使用 24 小时缓存。 |

脚本通过 `call_api.run` 调用接口，只使用公共调用器的一层缓存。缓存路径为 `<cwd>/linkfox/.cache/linkfox-keepa-product-search/`，缓存键取参数 JSON 按键排序后计算的 SHA-256 前 16 位，有效期为 24 小时；相同参数调整键顺序仍可复用缓存。缓存命中添加 `_cache.hit=true`，同样保存完整响应与会话索引。脚本会缓存失败或空结果，不自动重试；显式刷新应遵守 SKILL.md 的成本约束。

认证优先读取 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`；网关支持 `LINKFOX_TOOL_GATEWAY` 覆盖并去掉末尾 `/`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。业务脚本在请求前检查当前目录及实际会话数据目录可写，提前创建会话元数据，并将响应固定保存到当前目录的 `linkfox/`，不回退到家目录或临时目录。会话目录或 `data` 目录被文件占用、不可写时，在请求前报错退出。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码，按公共响应码基本规则判断。 |
| errmsg | string | 业务消息或错误原因。 |
| errorCode | integer / string | 诊断状态字段，仅在实际返回时用于诊断，不替代公共规则中的 `errcode` 判断。 |
| total | integer | 总行数 |
| perPage | integer | 每页数量 |
| currentPage | integer | 当前页码 |
| totalCount | integer | 总数量 |
| sourceType | string | 来源类型：keepa |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| products | array | 商品列表（详见下方） |

#### products[] 商品对象字段

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
| monthlySalesUnits1MonthAgo | integer | 1 个月前的月销量（最近 12 个月） |
| monthlySalesUnits2MonthsAgo | integer | 2 个月前的月销量（最近 12 个月） |
| monthlySalesUnits3MonthsAgo | integer | 3 个月前的月销量（最近 12 个月） |
| monthlySalesUnits4MonthsAgo | integer | 4 个月前的月销量（最近 12 个月） |
| monthlySalesUnits5MonthsAgo | integer | 5 个月前的月销量（最近 12 个月） |
| monthlySalesUnits6MonthsAgo | integer | 6 个月前的月销量（最近 12 个月） |
| monthlySalesUnits7MonthsAgo | integer | 7 个月前的月销量（最近 12 个月） |
| monthlySalesUnits8MonthsAgo | integer | 8 个月前的月销量（最近 12 个月） |
| monthlySalesUnits9MonthsAgo | integer | 9 个月前的月销量（最近 12 个月） |
| monthlySalesUnits10MonthsAgo | integer | 10 个月前的月销量（最近 12 个月） |
| monthlySalesUnits11MonthsAgo | integer | 11 个月前的月销量（最近 12 个月） |
| monthlySalesUnits12MonthsAgo | integer | 12 个月前的月销量（最近 12 个月） |
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

#### products[].subcategories[] 子类目对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | 以实际返回类型为准 | 类目 ID，保留实际返回类型。 |
| rank | 以实际返回类型为准 | 类目内排名，保留实际返回类型。 |
| label | 以实际返回类型为准 | 类目名称，保留实际返回类型。 |

响应 `price` 已定义为标准货币单位（如美元、欧元），`fbaFees` 同样为标准货币单位；`primePrice` 按实际响应口径核对。不要因请求价格使用最小货币单位而将结果价格再次除以 100。`packageQuantity`、`itemLength`、`itemWidth`、`itemHeight` 的 0 或 -1 表示不可用，不作为真实数量或尺寸展示。`columns` 和 `productImageUrls` 为数组，元素结构以实际返回内容为准。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应状态统一依照公共规则判断，不额外规定成功必须恰为 200；实际返回 `errorCode` 时将其保留用于诊断，不替代 `errcode` 判断。
- `authorized error` 表示认证失败，按 `onboarding.md` 引导；权限错误不误归为余额问题。
- 找商品阶段为空时不再计拉取详情阶段 token；不因此自动更换条件或翻页继续调用。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/keepa/productSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"domain": "1", "keyword": "wireless charger", "monthlySoldGte": 500, "currentRatingGte": 4.0}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-keepa-product-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```