# `linkfox-amazon-product-detail` reference

## 功能与边界

通过亚马逊前台商品页按 ASIN 获取当前结构化详情，适用于 Listing 提取、竞品对比、价格/评分核对、图片和变体查看、Prime/库存/配送检查，以及按需读取经常一起购买、相关商品和作者评论。一次最多 40 个 ASIN，以逗号分隔；详情查询按成功返回商品数计费，适合查询已经确定的 ASIN，不适合大规模探索。

不提供历史价格、销量预测、广告数据、库存管理、FBA 费用分析、ABA 关键词分析、Listing 改写或超出原始评论文本的独立情感数据。默认站点为 `amazon.com`。

## MCP 调用

- **MCP server**：`LinkFox`，连接地址 `https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- **唯一工具**：`proxy_call`
- **toolName**：`amazon/product/detail`。这是精确路由名，不加前导 `/`，不改写大小写或分隔符。
- **arguments**：直接传入下方【请求参数】定义的对象，不要再包 `body`、`params` 或 `data`。
- **返回**：`proxy_call` 的 text content 是下游 JSON 字符串时只解析一次，再按【响应字段】读取；不得把 MCP 外层对象当成业务响应。
- **调用纪律**：禁止直连工具网关；同一任务内相同 `toolName + arguments` 只调用一次。MCP 缺失、认证和计费异常按 `onboarding.md` 处理。

## 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---:|---|---|
| `asins` | string | 是 | — | 逗号分隔的 ASIN，最多 40 个，格式 `^[A-Z0-9]+(,[A-Z0-9]+){0,39}$` |
| `amazonDomain` | string | 否 | `amazon.com` | 站点域名，见下表 |
| `language` | string | 否 | — | 如 `en_US`、`de_DE`、`fr_FR`、`ja_JP`、`it_IT`、`es_ES`、`pt_BR`、`en_GB`、`zh_CN` |
| `deliveryZip` | string | 否 | — | 配送邮编，如 `10001`、`10115`、`EC1A 1BB` |
| `device` | string | 否 | `desktop` | `desktop`、`mobile` 或 `tablet` |
| `returnBoughtTogether` | boolean | 否 | `false` | 是否返回 `boughtTogether` |
| `returnRelatedProducts` | boolean | 否 | `false` | 是否返回 `relatedProducts` |
| `returnAuthorsReviews` | boolean | 否 | `false` | 是否返回 `authorsReviews` |

支持的 `amazonDomain`：`amazon.com`（美国）、`amazon.co.uk`（英国）、`amazon.de`（德国）、`amazon.fr`（法国）、`amazon.it`（意大利）、`amazon.es`（西班牙）、`amazon.co.jp`（日本）、`amazon.ca`（加拿大）、`amazon.com.au`（澳大利亚）、`amazon.com.br`（巴西）、`amazon.in`（印度）、`amazon.nl`（荷兰）、`amazon.se`（瑞典）、`amazon.pl`（波兰）、`amazon.sg`（新加坡）、`amazon.sa`（沙特）、`amazon.ae`（阿联酋）、`amazon.com.tr`（土耳其）、`amazon.com.mx`（墨西哥）、`amazon.eg`（埃及）、`amazon.cn`（中国）、`amazon.com.be`（比利时）。未指定站点时使用美国站。

## 响应字段

### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总行数 |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |
| products | array | 产品列表（详见下方） |

### `products[]` 产品对象

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].asin | string | ASIN编码 |
| products[].title | string | 商品标题 |
| products[].brand | string | 品牌 |
| products[].price | number | 价格 |
| products[].extractedPrice | number | 提取的价格 |
| products[].oldPrice | number | 原价 |
| products[].extractedOldPrice | number | 提取的原价 |
| products[].currency | string | 币种 |
| products[].discount | string | 折扣 |
| products[].saveWithCoupon | string | 优惠券节省金额 |
| products[].rating | number | 评分 |
| products[].ratings | integer | 评论数 |
| products[].prime | boolean | 是否Prime商品 |
| products[].stock | string | 库存状态 |
| products[].delivery | string | 配送信息 |
| products[].link | string | 商品链接 |
| products[].linkClean | string | 纯净链接 |
| products[].asinUrl | string | 链接 |
| products[].imageUrl | string | 缩略图 |
| products[].thumbnail | string | 缩略图 |
| products[].productImageUrls | array | 商品图片链接列表 |
| products[].aboutItem | array | 五点描述 |
| products[].productDescription | string | 商品描述列表 |
| products[].description | string | 商品描述 |
| products[].dimension | string | 商品尺寸 |
| products[].weight | string | 重量 |
| products[].tags | string | 标签列表 |
| products[].badges | string | 徽章列表 |
| products[].climatePledgeFriendly | boolean | 是否气候友好 |
| products[].snapEbtEligible | boolean | 是否支持SNAP EBT |
| products[].boughtLastMonth | string | 上月购买数（字符串） |
| products[].boughtLastMonthCount | integer | 上月购买数（数字） |
| products[].reviewsSummary | string | 评论摘要 |
| products[].reviewsImages | array | 评论图片列表 |
| products[].sourceTool | string | 来源工具 |
| products[].sourceType | string | 来源类型：amazon |
| products[].pageFileUrl | string | 完整页面文件url |
| products[].productDetails | object | 商品详细规格信息 |
| products[].customerReviews | object | 星级评分分布 |
| products[].variants | array | 商品变体列表（数组） |
| products[].itemSpecifications | object | 商品规格（动态键值） |
| products[].itemIngredients | array | 商品成分列表（数组） |
| products[].boughtTogether | array | 当 `returnBoughtTogether: true` 时返回 |
| products[].relatedProducts | array | 当 `returnRelatedProducts: true` 时返回 |
| products[].authorsReviews | array | 当 `returnAuthorsReviews: true` 时返回 |

### `products[].productDetails`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].productDetails.asin | string | ASIN编码 |
| products[].productDetails.manufacturer | string | 制造商 |
| products[].productDetails.productDimensions | string | 商品尺寸 |
| products[].productDetails.upc | string | UPC编码 |
| products[].productDetails.units | string | 单位 |
| products[].productDetails.rating | number | 评分 |
| products[].productDetails.review | integer | 评论数 |

### `products[].customerReviews`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].customerReviews.fiveStar | integer | 五星评论数 |
| products[].customerReviews.fourStar | integer | 四星评论数 |
| products[].customerReviews.threeStar | integer | 三星评论数 |
| products[].customerReviews.twoStar | integer | 二星评论数 |
| products[].customerReviews.oneStar | integer | 一星评论数 |

### `products[].variants[]`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].variants[].title | string | 变体标题（如颜色、尺寸） |
| products[].variants[].items | array | 变体项列表，每项包含 `name`（名称）、`asin`（ASIN编码）、`position`（位置）、`selected`（是否已选择） |
| products[].variants[].items[].name | 来源未说明 | 名称 |
| products[].variants[].items[].asin | 来源未说明 | ASIN编码 |
| products[].variants[].items[].position | 来源未说明 | 位置 |
| products[].variants[].items[].selected | 来源未说明 | 是否已选择 |

### `products[].boughtTogether[]`（按需返回）

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].boughtTogether[].asin | string | ASIN编码 |
| products[].boughtTogether[].title | string | 标题 |
| products[].boughtTogether[].price | string | 价格 |
| products[].boughtTogether[].extractedPrice | number | 提取的价格 |
| products[].boughtTogether[].priceUnit | string | 单价 |
| products[].boughtTogether[].extractedPriceUnit | number | 提取的单价 |
| products[].boughtTogether[].thumbnail | string | 缩略图 |
| products[].boughtTogether[].link | string | 链接 |
| products[].boughtTogether[].linkClean | string | 纯净链接 |
| products[].boughtTogether[].stock | string | 库存状态 |
| products[].boughtTogether[].delivery | array | 配送信息 |
| products[].boughtTogether[].position | integer | 位置 |

### `products[].relatedProducts[]`（按需返回）

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].relatedProducts[].asin | string | ASIN编码 |
| products[].relatedProducts[].title | string | 标题 |
| products[].relatedProducts[].price | string | 价格 |
| products[].relatedProducts[].extractedPrice | number | 提取的价格 |
| products[].relatedProducts[].oldPrice | string | 原价 |
| products[].relatedProducts[].extractedOldPrice | number | 提取的原价 |
| products[].relatedProducts[].priceUnit | string | 单价 |
| products[].relatedProducts[].extractedPriceUnit | number | 提取的单价 |
| products[].relatedProducts[].rating | number | 评分 |
| products[].relatedProducts[].reviews | integer | 评论数 |
| products[].relatedProducts[].thumbnail | string | 缩略图 |
| products[].relatedProducts[].link | string | 链接 |
| products[].relatedProducts[].linkClean | string | 纯净链接 |
| products[].relatedProducts[].prime | boolean | 是否Prime商品 |
| products[].relatedProducts[].sponsored | boolean | 是否赞助商品 |
| products[].relatedProducts[].climatePledgeFriendly | boolean | 是否气候友好 |
| products[].relatedProducts[].discount | string | 折扣 |
| products[].relatedProducts[].badges | array | 徽章列表 |
| products[].relatedProducts[].position | integer | 位置 |

### `products[].authorsReviews[]`（按需返回）

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].authorsReviews[].title | string | 标题 |
| products[].authorsReviews[].text | string | 评论内容 |
| products[].authorsReviews[].author | string | 作者 |
| products[].authorsReviews[].authorImage | string | 作者头像 |
| products[].authorsReviews[].authorLink | string | 作者链接 |
| products[].authorsReviews[].rating | integer | 评分 |
| products[].authorsReviews[].date | string | 日期 |
| products[].authorsReviews[].verifiedPurchase | boolean | 是否已验证购买 |
| products[].authorsReviews[].helpfulVotes | string | 有用投票数 |
| products[].authorsReviews[].productSize | string | 商品尺寸 |
| products[].authorsReviews[].productFlavorName | string | 商品口味名称 |
| products[].authorsReviews[].position | integer | 位置 |
## 错误、展示和成本

- `proxy_call` 返回 `isError=true` 时属于 MCP/代理错误，展示错误并停止，不得改走 HTTP；拿到下游 JSON 后，业务成功通常是 `errorCode=200`，401 表示未授权，402 表示积分不足，其他非 200 值查看 `errmsg`。401/402 走统一 onboarding。
- 多 ASIN 按 ASIN 分块；规格和价格适合表格，`aboutItem` 用列表；有评价分布时展示 5—1 星；价格带币种；图片 URL 作为图片或链接；缺失、`0`、`-1` 标 N/A。
- 失败时检查 ASIN 格式、站点域名和可选参数；不要因失败连续更换站点或参数。
- 计费规则：成功返回商品数 × 15；同一会话相同参数默认只调用一次。调用前提示按 ASIN 计费。

## 示例

```json
{"asins":"B072MQ5BRX,B08N5WRWNW","amazonDomain":"amazon.com","returnBoughtTogether":true,"returnAuthorsReviews":true}
```

```json
{
  "toolName": "amazon/product/detail",
  "arguments": {
    "asins": "B072MQ5BRX",
    "amazonDomain": "amazon.de",
    "language": "de_DE",
    "deliveryZip": "10115"
  }
}
```

## Feedback API

当结果不符合描述、数据错误、用户表扬/不满或提出改进建议时，不打断当前流程，向独立端点 `POST https://skill-api.linkfox.com/api/v1/public/feedback` 发送 JSON：

```json
{"skillName":"linkfox-wb-amazon-front-data","sentiment":"POSITIVE","category":"OTHER","content":"说明用户意图、实际结果以及问题或表扬。"}
```

`sentiment` 取 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 取 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。反馈端点与工具网关分离。

