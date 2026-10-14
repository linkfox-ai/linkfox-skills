# `linkfox-etsy-store-query` 参考

## 能力说明

按销量、周销量、收藏、评论、开店时间、国家、主营类目、Raving、星标和状态筛选 Etsy 店铺，用于店铺发现、卖家表现研究和候选店铺排序。

## 能力边界与特殊规则

- `page` 从 1 开始，`pageSize` 默认 20，最大 100。
- `begin*` 与 `end*` 组成逗号区间；只填一侧时表示开放区间。
- `sortBy` 只能使用 `8~11`：8 总销量、9 周销量、10 评论数、11 收藏数。
- `sortDesc` 使用 `1=降序、0=升序`，与商品查询的 `sortDesc: 2` 升序不同。
- `beginStoreOpenedAt`、`endStoreOpenedAt` 使用 `YYYY-MM-DD`；`category` 表示店铺主营分类，`country` 表示店铺所在国家。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`ehunt/etsy/storeQuery`
- **arguments**：直接使用下表请求参数对象，不增加 `body`、`data`、`params` 或凭证字段。
- WorkBuddy 自动注入 Authorization；配置和 `arguments` 不得加入 headers、API Key、token、JWT 或手机号。
- 先检查 MCP/schema/`isError`，再读取代理内容；text JSON 只解析一次，最后检查下游 `errcode`、`code`、`errmsg`。
- MCP 缺失或失败时停止，不得 HTTP fallback；相同 `toolName + arguments` 不得重复收费调用，失败、空结果或返回不理想时不得自动重试。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `beginFavorites` / `endFavorites` | integer，≥0 | 否 | 店铺收藏数区间 |
| `beginFavoritesWeekly` / `endFavoritesWeekly` | integer，≥0 | 否 | 周新增收藏区间 |
| `beginReviews` / `endReviews` | integer，≥0 | 否 | 店铺评论数区间 |
| `beginReviewsWeekly` / `endReviewsWeekly` | integer，≥0 | 否 | 周新增评论区间 |
| `beginSales` / `endSales` | integer，≥0 | 否 | 店铺总销量区间 |
| `beginSalesWeekly` / `endSalesWeekly` | integer，≥0 | 否 | 店铺周销量区间 |
| `beginStoreOpenedAt` / `endStoreOpenedAt` | `YYYY-MM-DD` | 否 | 开店日期区间 |
| `category` / `country` | string，最大 1000 | 否 | 主营分类 / 所在国家 |
| `isRaving` / `isStar` | integer | 否 | 1 表示对应标签店铺 |
| `page` | integer，≥1 | 否 | 页码，默认 1 |
| `pageSize` | integer，1~100 | 否 | 每页条数，默认 20 |
| `searchKey` | string，最大 500 | 否 | 关键词、店铺名称或店铺 URL |
| `sortBy` | integer，8~11 | 否 | 8 总销量、9 周销量、10 评论数、11 收藏数 |
| `sortDesc` | integer | 否 | `1` 降序，`0` 升序 |
| `status` | integer | 否 | 店铺状态：1 活跃、0 非活跃 |

示例：

```json
{"searchKey":"ceramic","country":"US","beginSalesWeekly":10,"endSalesWeekly":1000,"isRaving":1,"sortBy":9,"sortDesc":1,"page":1,"pageSize":20}
```

### 响应字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 记录数（本页返回条数） |
| `sourceTool` | string | 工具类型：ehunt |
| `sourceType` | string | 来源类型：etsy |
| `stores` | array | 店铺列表 |
| `columns` | array | 渲染的列 |
| `costToken` | integer | 消耗 token（按本页返回条数估算） |
| `storeNum` | integer | 符合条件的店铺总数（上游 store_num） |
| `title` | string | 标题 |
| `type` | string | 渲染的样式 |
| `columns[]` | 来源未说明 | 渲染列定义元素；来源未说明内部字段 |

`stores[]`：

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `stores[].category` | array | 主营类目列表 |
| `stores[].category[]` | 来源未说明 | 主营类目列表元素 |
| `stores[].country` | array | 国家/地区列表 |
| `stores[].country[]` | 来源未说明 | 国家/地区列表元素 |
| `stores[].favorites` | integer | 收藏数 |
| `stores[].favoritesWeekly` | integer | 周新增收藏数 |
| `stores[].isRaving` | integer | 是否 Raving：1=是 |
| `stores[].isStar` | integer | 是否星标：1=是 |
| `stores[].logoUrl` | string | 店铺头像 URL |
| `stores[].productCount` | integer | 店铺商品数量 |
| `stores[].rating` | number | 评分 |
| `stores[].reviews` | integer | 评论数 |
| `stores[].reviewsWeekly` | integer | 周新增评论数 |
| `stores[].salesTotal` | integer | 总销量 |
| `stores[].salesWeekly` | integer | 周销量 |
| `stores[].shopWebsite` | string | 店铺官网/外链 |
| `stores[].startAt` | string | 开店日期 |
| `stores[].status` | integer | 店铺状态：1=活跃，0=非活跃 |
| `stores[].storeId` | string | 店铺 ID |
| `stores[].storeName` | string | 店铺名称 |
| `stores[].storeUrl` | string | 店铺链接 |

## MCP 调用示例

```json
{
  "toolName": "ehunt/etsy/storeQuery",
  "arguments": {
    "searchKey": "ceramic",
    "country": "US",
    "page": 1,
    "pageSize": 20
  }
}
```

## 错误、费用和展示

按 `errcode`/`errmsg` 或根级 `code` 解释结果；国家、日期、区间和排序编码错误时给出修正建议。`costToken` 以实网返回为准，动态规则为“本页返回店铺数 × 1.8”；翻页重新计费。展示时区分 `total`（本页条数）与 `storeNum`（符合条件总数），分开展示总销量/周销量、评论/周评论和收藏/周收藏，不把公开评分或销量直接等同于收入或未来表现。认证/余额问题读取 `references/onboarding.md`。
