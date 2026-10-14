# Shopee 商品列表检索与筛选

## 功能与边界

按 Shopee 站点和多维条件检索当前商品列表，适合关键词选品、爆款发现、价格/销量比较、类目扫描、竞品店铺查看和跨境/本土商品筛选。它不是单个 listing 详情接口。

- `station` 必填，支持马来西亚（`malaysia`/`MY`）、中国台湾（`taiwan_china`/`Taiwan_CHN`）、印度尼西亚（`indonesia`/`ID`）、泰国（`thailand`/`TH`）、菲律宾（`philippines`/`PH`）、新加坡（`singapore`/`SG`）、越南（`vietnam`/`VN`）、巴西（`brazil`/`BR`）、墨西哥（`mexico`/`MX`）、智利（`chile`/`CL`）和哥伦比亚（`columbia`/`CO`）。
- `page` 从 1 开始，`pageSize` 为 1–1000；数值按所选站点本地货币解释。
- 数据依赖友鹰抓取周期，优先展示 `lastModiTime`。空结果或失败时不自动换词、改站、翻页或放宽条件。

## MCP 调用

- MCP Server：`LinkFox`
- Server URL：`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`
- 唯一工具：`proxy_call`
- `toolName`：`youying/shopee/getProductInfos`
- `arguments`：直接使用下述请求参数对象，不增加包装层。
- WorkBuddy 自动注入授权信息；调用参数中不得添加认证字段或凭据。
- 禁止 HTTP fallback。同一任务内相同 `toolName + arguments` 只调用一次；失败、空结果或不理想时不得自动改参数或重试。
- 先检查 MCP 层，再检查代理层；代理结果中的 text 是 JSON 字符串时只解析一次，最后检查下游业务状态。

## 请求参数

### 必填与关键词

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `station` | string | 是 | Shopee 站点名称或代码，见上方映射 |
| `keyword` | string | 否 | 商品标题关键词 |
| `keywordType` | integer | 否 | `1` 整句，`2` 多词 AND，`3` 多词 OR；默认整句 |
| `notExistKeyword` | string | 否 | 排除包含该关键词的商品 |
| `notExistKeywordType` | integer | 否 | `1` 整句，`2` 多词 AND，`3` 多词 OR；默认整句 |

### 价格、销量与评价

| 参数 | 类型 | 说明 |
|---|---|---|
| `priceMin` / `priceMax` | number | 商品总价当地货币的上下限 |
| `soldMin` / `soldMax` | integer | 前 30 天实际销售件数上下限 |
| `estimateSoldStart` / `estimateSoldEnd` | integer | 估算前 30 天销量上下限 |
| `historicalSoldStart` / `historicalSoldEnd` | integer | 累计总销量上下限 |
| `paymentStart` / `paymentEnd` | number | 前 30 天销售额上下限，按当地货币 |
| `ratingMin` / `ratingMax` | number | 商品评分上下限，范围 0–5 |
| `ratingsMin` / `ratingsMax` | integer | 评分数上下限 |
| `favoriteMin` / `favoriteMax` | integer | 收藏数上下限 |
| `skuNumberStart` / `skuNumberEnd` | integer | SKU 总数上下限 |

### 时间、类目与店铺

| 参数 | 类型 | 说明 |
|---|---|---|
| `listingDateFrom` / `listingDateTo` | string | 上架时间范围，格式 `yyyy-MM-dd` |
| `statTimeStart` / `statTimeEnd` | string | 统计时间范围，格式 `yyyy-MM-dd HH:mm:ss` |
| `lastModiTimeStart` / `lastModiTimeEnd` | string | 最新抓取时间范围，格式 `yyyy-MM-dd` |
| `approvedDateStart` / `approvedDateEnd` | string | 店铺开张时间范围，格式 `yyyy-MM-dd` |
| `pL1Id` / `pL2Id` / `pL3Id` | string | 一级/二级/三级类目 ID |
| `cidList` | string | 完整类目路径，多组用 `｜` 分隔，如 `AAA,BBB,CCC｜DDD,EEE` |
| `shopIdList` | string | 指定店铺 ID，多个用逗号分隔 |
| `notExistShopIdList` | string | 排除店铺 ID，多个用逗号分隔 |
| `merchant` | string | 店铺名称或用户名 |
| `shopLocation` | string | 店铺所在地 |

### 商品属性、排序与分页

| 参数 | 类型 | 说明 |
|---|---|---|
| `shippingIconType` | integer | 店铺所在地：`0` 本地，`1` 海外 |
| `cbOption` | integer | 发货地点：`0` 本土，`1` 跨境 |
| `isShopeeVerified` | integer | 虾皮优选：`0` 否，`1` 是 |
| `isOfficialShop` | integer | 官方店铺：`0` 否，`1` 是 |
| `isHotSales` | integer | 是否热销：`0` 否，`1` 是 |
| `pids` | string | 商品 ID 列表，最多 500 个，逗号分隔 |
| `orderBy` | string | `rating`、`price`、`historical_sold`、`sold`、`payment`、`favorite`、`ratings`、`gen_time` 或 `estimate_sold` |
| `orderByType` | string | `ASC` 或 `DESC`，默认 `DESC` |
| `page` | integer | 页码，从 1 开始，默认 1 |
| `pageSize` | integer | 每页数量，1–1000，默认 1000 |

## 完整 MCP 示例

```json
{
  "toolName": "youying/shopee/getProductInfos",
  "arguments": {
    "station": "malaysia",
    "keyword": "Storage Box",
    "keywordType": 2,
    "soldMin": 100,
    "orderBy": "sold",
    "orderByType": "DESC",
    "page": 1,
    "pageSize": 50
  }
}
```

## 响应字段

字段定义仅来自 `skills/linkfox-youying-shopee-get-product-infos/references/api.md` 的响应部分。

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `total` | integer | 当前返回记录数 |
| `totalSize` | integer | 总结果数 |
| `sourceTool` | string | 来源工具标识 |
| `sourceType` | string | 来源类型：`shopee` |
| `columns` | array | 渲染列定义 |
| `columns[]` | 来源未说明 | 渲染列定义的元素；来源未说明元素结构 |
| `costToken` | integer | 消耗 token |
| `type` | string | 渲染样式 |
| `products` | array | 商品列表（见下方字段） |
| `products[].pid` | string | 商品唯一ID |
| `products[].title` | string | 商品标题 |
| `products[].description` | string | 商品描述 |
| `products[].imageUrl` | string | 商品主图URL |
| `products[].productUrl` | string | Shopee商品链接 |
| `products[].shopeeUrl` | string | Shopee域名下的商品链接 |
| `products[].price` | number | 商品默认价（当地货币） |
| `products[].minPrice` | number | SKU最低价 |
| `products[].maxPrice` | number | SKU最高价 |
| `products[].sold` | integer | 前30天销售件数 |
| `products[].estimateSold` | integer | 估算前30天销售件数 |
| `products[].historicalSold` | integer | 商品总销售件数 |
| `products[].payment` | number | 前30天销售额（当地货币） |
| `products[].rating` | number | 商品评分（0-5） |
| `products[].ratings` | integer | 评分数 |
| `products[].favorite` | integer | 收藏数 |
| `products[].viewCount` | integer | 浏览数 |
| `products[].stock` | integer | 库存数 |
| `products[].skuNumber` | integer | SKU数量 |
| `products[].genTime` | string | 上架时间 |
| `products[].statTime` | string | 统计时间 |
| `products[].lastModiTime` | string | 最新抓取时间 |
| `products[].categoryStructure` | string | 类目结构路径 |
| `products[].cid` | string | 类目ID（逗号分隔） |
| `products[].shopId` | string | 店铺ID |
| `products[].shopName` | string | 店铺名称 |
| `products[].shopUrl` | string | 店铺链接 |
| `products[].userName` | string | 店主名称 |
| `products[].shopLocation` | string | 店铺所在地 |
| `products[].shopProductsCount` | integer | 店铺商品总数 |
| `products[].approvedDate` | string | 店铺开张时间 |
| `products[].isOfficialShop` | integer | 是否官方店铺（1=是, 0=否） |
| `products[].isShopeeVerified` | integer | 虾皮优选（1=是, 0=否） |
| `products[].isHotSales` | integer | 是否热销（1=是, 0=否） |
| `products[].shippingIconType` | integer | 店铺所在地类型（0=本地, 1=海外, 3或null=未知） |
| `products[].cbOption` | integer | 发货地点（0=本土, 1=跨境） |
| `products[].estimatedDays` | integer | 预计到货天数 |
| `products[].status` | integer | 商品状态（1=正常, 0=下架, 8=列表中排除） |
| `products[].notExist` | integer | 是否存在（0=存在, 1=不存在） |

## 错误与成本

业务成功值为 `200`，错误时读取实际的 `errcode`、`errorCode`、`errmsg` 或消息字段。401、402、403 分别按 `onboarding.md` 的授权、计费和权限规则处理；其他错误检查站点、关键词、范围、类目、店铺、排序和分页。不得自动重复调用。

每次调用可能消耗积分，实际消耗以 `costToken` 为准。翻页或改条件前说明额外消耗，由用户决定。

## 展示规则

1. 标注站点、本地货币、查询条件、抓取时点、当前条数、`totalSize` 和页码。
2. 优先展示标题、链接、价格、销量、销售额、评分、库存和店铺字段。
3. 官方、优选、热销、本地/海外和跨境/本土标识按返回值展示，不推导缺失状态。
4. 大列表只展示必要摘要，不自动翻页；字段缺失时标记 N/A。

## Feedback API

该反馈端点与商品查询 MCP 分离。用户明确表扬、不满、指出结果不符或发现功能问题时，以 `skillName=linkfox-wb-shopee-product-selection` 上报，不打断业务结果。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- `sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE` 三选一
- `category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 四选一
- `content`：说明用户意图、实际结果和问题/表扬原因，不得包含敏感信息
