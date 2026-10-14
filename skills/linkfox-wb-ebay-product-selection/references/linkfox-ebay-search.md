# eBay 商品搜索与选品数据参考

## 功能与适用边界

读取 eBay 多个国际站点的当前前台 listing，支持关键词、价格区间、商品成色、购买形式、排序、卖家位置、配送范围、类目和展示条件筛选。适用于商品发现、竞品浏览、价格对照、已售/已结束 listing 参考、拍卖浏览和区域市场观察。

不提供历史价格趋势、长期销量序列、未来预测、卖家账户管理、刊登编辑、订单、广告或跨平台比价。单页结果上限为 200。价格以搜索站点的本地货币返回，`noCache: true` 应谨慎使用。

## MCP 调用

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- `toolName`：`ebay/search`
- `arguments`：直接使用下述请求参数对象，不增加包装层。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 禁止 HTTP fallback。失败、空结果或结果不理想时不得自动换关键词、放宽筛选、翻页或重复收费调用；同一任务内相同 `toolName + arguments` 只调用一次。
- 先检查 MCP 层，再检查代理层；代理结果中的 text 是 JSON 字符串时只解析一次，最后检查下游业务状态。

## 请求参数

所有字段均为可选；未提供 `keyword` 时由接口按其他筛选条件处理。

| 参数 | 类型 | 必填 | 说明 | 默认/可选值 |
|---|---|---:|---|---|
| `keyword` | string | 否 | 搜索关键词，最长 1024 个字符 | — |
| `ebayDomain` | string | 否 | eBay 站点域名 | 默认 `ebay.com`；支持列表见下 |
| `page` | integer | 否 | 分页页码 | `1` |
| `pageSize` | integer | 否 | 每页最大结果数 | `50`；仅 `25`、`50`、`100`、`200` |
| `orderBy` | string | 否 | 排序方式 | `12`（最佳匹配）；代码见下 |
| `priceMin` | number | 否 | 最低价格筛选 | — |
| `priceMax` | number | 否 | 最高价格筛选 | — |
| `itemCondition` | string | 否 | 成色代码；多个值用 `\|` 分隔 | 代码见下 |
| `buyingFormat` | string | 否 | 购买形式 | `Auction`、`BIN`、`BO` |
| `showOnly` | string | 否 | 展示过滤条件；多个值用逗号分隔 | 代码见下 |
| `location` | integer | 否 | 商品所在国家/地区代码 | 例如 `1` 美国、`2` 加拿大、`3` 英国、`45` 中国、`77` 德国 |
| `prefLoc` | string | 否 | 首选位置范围 | `1` 本国、`2` 区域、`3` 全球 |
| `zipCode` | string | 否 | ZIP/邮政编码，用于区域配送筛选 | — |
| `categoryId` | integer | 否 | eBay 类目 ID | — |
| `noCache` | boolean | 否 | 是否绕过下游缓存获取新结果 | `false` |

### 排序代码

| 代码 | 含义 |
|---:|---|
| `12` | Best Match，最佳匹配 |
| `1` | Time，最先结束 |
| `10` | Time，新近上架 |
| `15` | Price + Shipping，价格加运费最低 |
| `16` | Price + Shipping，价格加运费最高 |
| `2` | Price，价格最低 |
| `3` | Price，价格最高 |
| `7` | Distance，距离最近 |
| `18` | Condition，全新优先 |
| `19` | Condition，二手优先 |

### 商品成色代码

| 代码 | 含义 |
|---:|---|
| `1000` | New，全新 |
| `1500` | New other，全新其他 |
| `1750` | New with defects，全新有瑕疵 |
| `2000` | Certified Refurbished，官方认证翻新 |
| `2010` | Excellent - Refurbished，优秀翻新 |
| `2020` | Very Good - Refurbished，良好翻新 |
| `2030` | Good - Refurbished，一般翻新 |
| `2500` | Seller refurbished / Remanufactured，卖家翻新/再制造 |
| `2750` | Like New，几乎全新 |
| `3000` | Used / Pre-owned，二手/已使用 |
| `7000` | For parts or not working，配件或不工作 |

### `showOnly` 过滤值

| 值 | 含义 |
|---|---|
| `Complete` | 已结束 listing |
| `Sold` | 仅已售 listing |
| `FR` | 免费退货 |
| `RPA` | 接受退货 |
| `AS` | 授权卖家 |
| `Savings` | 折扣/节省 |
| `SaleItems` | 促销商品 |
| `Lots` | 批量商品 |
| `Charity` | 慈善商品 |
| `AV` | 接口支持的 AV 过滤值 |
| `FS` | 免运费 |
| `LPickup` | 本地自提 |

### 支持的 eBay 站点

| 域名 | 市场 |
|---|---|
| `ebay.com` | 美国（默认） |
| `ebay.co.uk` | 英国 |
| `ebay.de` | 德国 |
| `ebay.fr` | 法国 |
| `ebay.it` | 意大利 |
| `ebay.es` | 西班牙 |
| `ebay.ca` | 加拿大 |
| `ebay.com.au` | 澳大利亚 |
| `ebay.nl` | 荷兰 |
| `ebay.at` | 奥地利 |
| `ebay.ch` | 瑞士 |
| `ebay.pl` | 波兰 |
| `ebay.ie` | 爱尔兰 |
| `ebay.com.hk` | 中国香港 |
| `ebay.com.my` | 马来西亚 |
| `ebay.com.sg` | 新加坡 |

## 完整 MCP 示例

```json
{
  "toolName": "ebay/search",
  "arguments": {
    "keyword": "iPhone 15 Pro",
    "ebayDomain": "ebay.com",
    "showOnly": "Sold,Complete",
    "orderBy": "10",
    "page": 1,
    "pageSize": 50
  }
}
```

## 响应字段

字段定义仅来自 `skills/linkfox-ebay-search/references/api.md` 的响应部分。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 匹配结果总数 |
| `products` | array | 商品列表数组（详见下方商品字段） |
| `columns` | array | 渲染的列定义 |
| `columns[]` | 来源未说明 | 渲染列定义的元素；来源未说明元素结构 |
| `type` | string | 渲染样式标识 |
| `costToken` | integer | 消耗token |
| `products[].productId` | string | eBay商品ID |
| `products[].title` | string | 商品标题 |
| `products[].subtitle` | string | 商品副标题 |
| `products[].price` | number | 当前价格/成交价格 |
| `products[].minPrice` | number | 价格区间起始值（适用于多规格商品） |
| `products[].maxPrice` | number | 价格区间结束值（适用于多规格商品） |
| `products[].oldPrice` | number | 折扣前原价 |
| `products[].currency` | string | 货币单位（如 USD、GBP、EUR） |
| `products[].condition` | string | 商品状态描述 |
| `products[].link` | string | eBay商品详情页链接 |
| `products[].imageUrl` | string | 商品缩略图URL |
| `products[].shipping` | string | 配送信息 |
| `products[].location` | string | 商品所在地 |
| `products[].sellerName` | string | 卖家名称 |
| `products[].sellerReviews` | integer | 卖家评价数量 |
| `products[].positiveFeedbackInPercentage` | number | 卖家好评率 |
| `products[].salesQuantity` | integer | 已售数量 |
| `products[].bidsCount` | integer | 竞拍数量（拍卖商品） |
| `products[].returns` | string | 退货信息 |
| `products[].promotion` | string | 促销信息 |
| `products[].sponsored` | boolean | 是否为赞助/推广商品 |
| `products[].sourceType` | string | 来源平台标识（`ebay`） |
| `products[].sourceTool` | string | 来源工具标识 |

## 错误与成本

业务成功值为 `200`，错误时读取实际的 `errcode`、`errorCode`、`errmsg` 或消息字段。401、402、403 分别按 `onboarding.md` 的授权、计费和权限规则处理；其他非 200 状态检查关键词、站点、价格、筛选码、类目和分页。不得因错误自动重复调用。

每次调用可能消耗积分，实际消耗以 `costToken` 为准。翻页、修改筛选或设置 `noCache: true` 前说明可能增加消耗，由用户决定。

## 展示与特殊规则

1. 展示关键词、站点、筛选、排序、页码、`pageSize`、当前页条数和 `total`。
2. 价格和区间始终带 `currency`；不要直接合并不同站点货币。
3. `Sold,Complete` 结果是当前接口返回的参考，不代表完整历史数据。
4. `sponsored=true` 时标注赞助/推广；卖家好评率不等同平台担保。
5. 拍卖当前价不等同最终成交价；字段缺失时标记 N/A，不补猜。
6. 接口失败或空结果时不自动改关键词、筛选、邮编或页码。

## Feedback API

当用户明确表达赞扬、不满、结果与需求不符，或发现功能/数据问题时，调用独立的 Feedback API；不要把该请求与 eBay 搜索 MCP 混用，也不要打断当前业务流程。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "linkfox-wb-ebay-product-selection",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

`sentiment` 只能是 `POSITIVE`、`NEUTRAL` 或 `NEGATIVE`；`category` 只能是 `BUG`、`COMPLAINT`、`SUGGESTION` 或 `OTHER`。`content` 应说明用户意图、实际结果以及问题或赞扬原因，不得包含敏感信息。反馈失败不得改变搜索结果，也不得自动重复上报。
