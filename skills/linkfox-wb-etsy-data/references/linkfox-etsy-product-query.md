# `linkfox-etsy-product-query` 参考

## 能力说明

按多维条件筛选 Etsy 商品，用于关键词找品、价格/销量区间筛查、标签筛选和候选 Listing 列表研究。返回商品标题、链接、主图、价格、销量、收藏、评论、类目、标签、发货地和店铺等公开字段。

## 能力边界与特殊规则

- `page` 从 1 开始，`pageSize` 默认 20，最大 100，建议不超过 50。
- `begin*` 与 `end*` 组成区间；只填一侧时表示开放区间。价格参数为 `number`，其余数量参数为非负整数。
- `sortBy` 只能使用 `1~6`；`sortDesc` 使用 `1=降序、2=升序`，不要复用店铺查询的 `0=升序`。
- `productType`：`1` 手工、`2` 复古、`3` 数字、`4` 定制、`9` 其他；多个值用逗号分隔。
- `currencyCode` 默认 `USD`；`category` 是单个类目 ID，可先用类目检索获得。
- `searchKey` 可为关键词或 Etsy 商品 URL，但要得到一个 Listing 的完整页面信息时使用详情接口。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`ehunt/etsy/productQuery`
- **arguments**：直接使用下表请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；配置和 `arguments` 不得加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text JSON 只解析一次，最后检查下游 `errcode`、`code`、`errmsg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；相同 `toolName + arguments` 不得重复收费调用，失败、空结果或返回不理想时不得自动重试。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `beginFavorites` / `endFavorites` | integer，≥0 | 否 | 收藏数区间 |
| `beginFavoritesWeekly` / `endFavoritesWeekly` | integer，≥0 | 否 | 周新增收藏区间 |
| `beginPrice` / `endPrice` | number，≥0 | 否 | 价格区间；可单填一侧 |
| `beginReviews` / `endReviews` | integer，≥0 | 否 | 评论数区间 |
| `beginReviewsWeekly` / `endReviewsWeekly` | integer，≥0 | 否 | 周新增评论区间 |
| `beginSales` / `endSales` | integer，≥0 | 否 | 总销量区间 |
| `beginSalesWeekly` / `endSalesWeekly` | integer，≥0 | 否 | 周销量区间 |
| `category` | string，最大 1000 | 否 | 单个商品分类 ID |
| `country` | string，最大 1000 | 否 | 发货国家 |
| `currencyCode` | string，最大 1000 | 否 | 币种，默认 `USD` |
| `isBestsell` / `isPick` / `isRaving` | integer | 否 | 相应标签筛选 |
| `listedTime` | `YYYY-MM-DD` | 否 | 上架时间不早于该日期 |
| `page` | integer，≥1 | 否 | 页码，默认 1 |
| `pageSize` | integer，1~100 | 否 | 每页条数，默认 20，建议 ≤50 |
| `productType` | string | 否 | `1,2,3,4,9` 的逗号分隔组合 |
| `searchKey` | string，最大 500 | 否 | 关键词或 Etsy 商品 URL |
| `sortBy` | integer，1~6 | 否 | 上游排序字段 |
| `sortDesc` | integer | 否 | `1` 降序，`2` 升序 |
| `status` | integer | 否 | 商品状态示例：1 上架、0 下架 |

示例：

```json
{"searchKey":"poster","currencyCode":"USD","beginPrice":20,"endPrice":100,"beginSales":100,"productType":"1,4","sortBy":1,"sortDesc":1,"page":1,"pageSize":20}
```

### 响应字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 记录数（本页返回条数，便于与列表长度对齐） |
| `sourceTool` | string | 工具类型：ehunt |
| `sourceType` | string | 来源类型：etsy |
| `columns` | array | 渲染的列 |
| `costToken` | integer | 消耗 token（按本页返回条数估算） |
| `productNum` | integer | 符合条件的商品总数（上游 product_num） |
| `title` | string | 标题 |
| `type` | string | 渲染的样式 |
| `products` | array | Etsy 商品列表 |
| `columns[]` | 来源未说明 | 渲染列定义元素；来源未说明内部字段 |

`products[]`：

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `products[].category` | string | 类目名称 |
| `products[].favorites` | integer | 收藏数 |
| `products[].favoritesWeekly` | integer | 周新增收藏数 |
| `products[].imageUrl` | string | 主图 URL |
| `products[].isBestsell` | integer | 是否畅销：1=是 |
| `products[].isPick` | integer | 是否 Pick：1=是 |
| `products[].isRaving` | integer | 是否 Raving：1=是 |
| `products[].price` | number | 价格 |
| `products[].productUrl` | string | 商品链接 |
| `products[].releaseTime` | string | 上架/发布时间 |
| `products[].reviews` | integer | 评论数 |
| `products[].reviewsWeekly` | integer | 周新增评论数 |
| `products[].salesTotal` | integer | 总销量 |
| `products[].salesWeekly` | integer | 周销量 |
| `products[].shipsFrom` | string | 发货国家 |
| `products[].status` | integer | 商品状态：1=上架，0=下架 |
| `products[].storeName` | string | 店铺名称 |
| `products[].tags` | string | 标签 |
| `products[].title` | string | 商品标题 |

## MCP 调用示例

```json
{
  "toolName": "ehunt/etsy/productQuery",
  "arguments": {
    "searchKey": "poster",
    "currencyCode": "USD",
    "page": 1,
    "pageSize": 20
  }
}
```

## 错误、费用和展示

按响应的 `errcode`/`errmsg` 或根级 `code` 解释结果；参数范围、商品类型和排序编码错误时直接修正请求，不自动试探。`costToken` 以实网返回为准，动态规则为“本页返回商品数 × 1.8”；下一页是新请求并重新计费。列表中区分 `total`（本页条数）与 `productNum`（符合条件总数），保留空字段，不把标签或销量表述为保证性结论。认证/余额问题读取 `references/onboarding.md`。
