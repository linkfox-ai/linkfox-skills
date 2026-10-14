# linkfox-keepa-product-request

## 功能说明

通过 Keepa 获取一个或多个 Amazon ASIN 的结构化商品数据。适用于查询当前价格、标题、品牌、材质、图片、上架日期、类目、销售排名、月销量、评分、评论数、尺寸重量、配送方式、卖家数、FBA 费用和利润，以及可选的近 12 个月月销量和 30/90/180 天平均销售排名。

适用请求包括单个 ASIN 查询、最多 5 个 ASIN 的当前指标对比、商品规格核查和带 `history=1` 的月销量趋势。该端点不返回商品描述正文或评论正文；没有明确 ASIN 的候选发现应使用 `productSearch`，连续时间点曲线应使用 `productSeries`。

## 能力边界与特殊规则

- `asin` 必填，可用英文逗号分隔 1—5 个 ASIN，最大长度 300 字符。
- `domain` 必填，是数字型 Amazon 站点 ID，不是国家代码；未指定时使用 `1`（Amazon.com）。
- `history` 可选，`1` 返回历史销量/价格历史相关字段，`0` 只返回基础商品信息，默认 `0`；开启后响应体和 Keepa token 消耗会增加。
- 价格需结合 `currency` 展示；尺寸字段以毫米为主，重量以克为主。
- `0` 或 `-1` 的尺寸、数量等字段表示不可用，按 N/A 处理；`lastUpdate` 用于说明数据刷新时间。
- 单次查询可能消耗积分；失败或空结果不得自动更换 ASIN、站点或参数连续试探。同一任务内相同 `toolName + arguments` 不得重复调用。

## MCP 调用

- **MCP server**：`LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`）。
- **唯一工具**：`proxy_call`。
- **toolName**：`keepa/productRequest`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
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
| 12 | Amazon.com.br（巴西） |

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `asin` | string | 是 | 1—5 个 ASIN，英文逗号分隔，最多 300 字符 |
| `domain` | string | 是 | Amazon 站点 ID，见站点表 |
| `history` | integer | 否 | `1` 返回历史数据，`0` 仅基础信息，默认 `0` |

## 响应字段

### 顶层字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总行数 |
| perPage | integer | 每页数量 |
| sourceType | string | 来源类型：keepa |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| totalCount | integer | 总数量 |
| currentPage | integer | 当前页码 |
| type | string | 渲染的样式 |
| products | array | 商品列表（详见下方） |

### `products[]` 字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].asin | string | ASIN |
| products[].title | string | 商品标题 |
| products[].brand | string | 品牌 |
| products[].manufacturer | string | 制造商 |
| products[].model | string | 型号 |
| products[].color | string | 颜色 |
| products[].material | string | 产品的材质，指其构造中使用的主要材料 |
| products[].price | number | 当前价格（单位：元，如美元/欧元等） |
| products[].primePrice | number | prime价格 |
| products[].currency | string | 币种 |
| products[].rating | number | 当前评分（0.0-5.0，如4.5星） |
| products[].ratings | integer | 评分数量 |
| products[].reviewCount | integer | 评论数量 |
| products[].salesRank | integer | 销售排名 |
| products[].salesRank30 | integer | 近30天平均销售排名 |
| products[].salesRank90 | integer | 近90天平均销售排名 |
| products[].salesRank180 | integer | 近180天平均销售排名 |
| products[].monthlySalesUnits | integer | 月销量 |
| products[].monthlySalesRevenue | number | 月销售额 |
| products[].monthlySalesUnits1MonthAgo | integer | 1月前月销量 |
| products[].monthlySalesUnits2MonthsAgo | integer | 2月前月销量 |
| products[].monthlySalesUnits3MonthsAgo | integer | 3月前月销量 |
| products[].monthlySalesUnits4MonthsAgo | integer | 4月前月销量 |
| products[].monthlySalesUnits5MonthsAgo | integer | 5月前月销量 |
| products[].monthlySalesUnits6MonthsAgo | integer | 6月前月销量 |
| products[].monthlySalesUnits7MonthsAgo | integer | 7月前月销量 |
| products[].monthlySalesUnits8MonthsAgo | integer | 8月前月销量 |
| products[].monthlySalesUnits9MonthsAgo | integer | 9月前月销量 |
| products[].monthlySalesUnits10MonthsAgo | integer | 10月前月销量 |
| products[].monthlySalesUnits11MonthsAgo | integer | 11月前月销量 |
| products[].monthlySalesUnits12MonthsAgo | integer | 12月前月销量 |
| products[].availableDate | string | 上架时间（yyyy-MM-dd HH:mm:ss） |
| products[].lastUpdate | string | 最后更新时间（yyyy-MM-dd HH:mm:ss） |
| products[].imageUrl | string | 图片URL（请求地址） |
| products[].productImageUrls | array | 商品图片列表 |
| products[].asinUrl | string | 亚马逊asin的详情网址 |
| products[].urlSlug | string | URL Slug |
| products[].itemLength | integer | 商品长度，单位为毫米，不可用时为0或-1 |
| products[].itemWidth | integer | 商品宽度，单位为毫米，不可用时为0或-1 |
| products[].itemHeight | integer | 商品高度，单位为毫米，不可用时为0或-1 |
| products[].dimension | string | 尺寸 |
| products[].dimensionsType | string | 尺寸类型 |
| products[].weight | string | 重量（克） |
| products[].packageLength | integer | 包装长度（毫米） |
| products[].packageWidth | integer | 包装宽度（毫米） |
| products[].packageHeight | integer | 包装高度（毫米） |
| products[].packageWeight | string | 包装重量（克） |
| products[].packageDimensions | string | 包装尺寸 |
| products[].packageQuantity | integer | 包装中商品的数量，不可用时为0或-1 |
| products[].fulfillment | string | 配送方式(AMZ,FBA,FBM) |
| products[].fbaFees | number | FBA配送费（单位：元） |
| products[].referralFeePercentage | number | 推荐费百分比 |
| products[].profit | number | 利润率（百分比，如25.5表示25.5%） |
| products[].buyBoxSellerId | string | 购买按钮卖家ID |
| products[].sellerNum | integer | 卖家数 |
| products[].variationNum | integer | 变体数量 |
| products[].parentAsin | string | 父ASIN |
| products[].rootCategory | integer | 根类目ID |
| products[].categoryTree | string | 类目树 |
| products[].categoryTreeId | string | 类目树Id |
| products[].subcategories | array | 子类目列表，每个元素包含 `code`（类目ID）、`rank`（排名）、`label`（类目名称） |
| products[].subcategories[].code | 来源未说明 | 子类目 ID |
| products[].subcategories[].rank | 来源未说明 | 子类目排名 |
| products[].subcategories[].label | 来源未说明 | 子类目名称 |
| products[].isAdultProduct | boolean | 是否为成人产品 |
| products[].isHazmat | boolean | 是否为危险品 |
| products[].sourceType | string | 来源类型：keepa |
| products[].sourceTool | string | 来源工具 |

## 错误处理

正常情况下 HTTP 状态为 200，业务结果通过响应体中的 `errorCode`/`errcode` 区分；未授权通常返回 HTTP 401。

| 状态/字段 | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 读取 `products`、指标和 `costToken` |
| `401` | 认证失败 | 读取 `references/onboarding.md`，区分 MCP/代理层与下游业务层处理 |
| `402` | 积分不足 | 读取 `references/onboarding.md`，引导用户访问 LinkFox 账号页检查积分或套餐；不自动购买 |
| 其他非 200 值 | 业务异常 | 透传 `errmsg`，检查 ASIN、站点和参数 |

## MCP 示例

```json
{
    "toolName":  "keepa/productRequest",
    "arguments":  {
                      "asin":  "B0088PUEPK,B00U26V4VQ",
                      "domain":  "1",
                      "history":  1
                  }
}
```

## 反馈接口

反馈接口与 Keepa 网关分离：`POST https://skill-api.linkfox.com/api/v1/public/feedback`。JSON 使用 `skillName`、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和 `content`。当结果与意图不符、出现错误、用户表扬/不满或提出改进意见时按此规则上报，不中断当前流程。


