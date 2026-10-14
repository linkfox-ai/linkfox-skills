# linkfox-dld-product-billboard

## 功能与边界

查询1688商品热销榜单，支持周榜与月榜，帮助发现热门批发商品、比较供应商和筛选采购机会。它适合“1688热销榜、爆款、趋势、商品排行”的历史周期查询，不是店铺排行榜或实时销量保证。

不处理 Amazon 或其他平台研究、1688店铺级分析、国际站数据、谈价、下单、支付、质量评价/认证、物流成本或货代。周榜只支持近90天，月榜只支持近12个月；关键词必须为中文。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`dld/productBillboard`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP/`isError`，代理成功后读取 text 或 structured content；text 为 JSON 时只解析一次，再按响应字段处理下游状态。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想时不得自动重试或改参数探测。
### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `keyWord` | string | 否 | — | 中文商品关键词，最多50字符 |
| `date` | string | 否 | — | 周榜传周日日期；月榜传当月1日，格式 `YYYY-MM-DD` |
| `pageType` | integer | 否 | 3 | `2` 周榜，`3` 月榜 |
| `pageIndex` | integer | 否 | 1 | 页码，从1开始 |
| `pageSize` | integer | 否 | 20 | 每页10–100条 |
| `sortField` | string | 否 | `orderCount` | `orderCount`、`saleCount`、`saleVolume`、`offerCreateTime`、`price`、`consignPrice` |
| `sortType` | string | 否 | `desc` | `desc` 或 `asc` |
| `searchType` | integer | 否 | 1 | `1` 模糊，`3` 精准 |
| `offerType` | integer | 否 | 0 | `0`不限、`2`新品、`3`1688严选、`4`跨境、`5`定制、`6`镇店之宝 |
| `companyType` | integer | 否 | 0 | `0`不限、`1`店铺、`2`工厂 |
| `shiLiType` | string | 否 | — | 逗号分隔：`superFactory`、`Power`、`TrustPass` |
| `beginTpYear` / `endTpYear` | integer | 否 | — | 诚信通年限范围 |
| `beginPrice` / `endPrice` | number | 否 | — | 批发价范围 |
| `beginConsignPrice` / `endConsignPrice` | number | 否 | — | 代发价范围 |
| `beginOrderCount` / `endOrderCount` | integer | 否 | — | 销售笔数范围 |
| `beginSaleCount` / `endSaleCount` | integer | 否 | — | 销售件数范围 |
| `beginSaleVolume` / `endSaleVolume` | number | 否 | — | 预估销售额范围 |
| `beginStartQuantity` / `endStartQuantity` | integer | 否 | — | 起批量范围 |
| `beginOfferCreateTime` / `endOfferCreateTime` | string | 否 | — | 上架时间范围，`YYYY-MM-DD` |
| `sendTime` | string | 否 | — | 逗号分隔 `24`、`48`、`72` 小时 |
| `proxyRights` | string | 否 | — | `4360897` 一件代发包邮，`449154` 先采后付 |
| `shopService` | string | 否 | — | `4057409` 安心购，`888777` 深度认证报告 |
| `buyerProtections` | string | 否 | — | `商品包邮`、`7天包退货`、`支持运费险`，逗号分隔 |
| `faceToFaceSupport` | string | 否 | — | `441218`淘宝、`386434`抖音、`422914`拼多多、`422978`小红书、`386370`快手 |
| `productIds` | string | 否 | — | 商品 ID 用顿号分隔，最多20个 |
| `goodsUrl` | string | 否 | — | 商品链接地址 |

### 响应字段

#### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 记录数 |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| products | array | 商品列表（见下方商品对象） |

#### `products[]`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].offerId | string | 商品id |
| products[].asin | string | 商品编号 |
| products[].title | string | 商品标题 |
| products[].price | number | 批发价 |
| products[].consignPrice | number | 代发价 |
| products[].currency | string | 币种 |
| products[].unit | string | 单位 |
| products[].quantityBegin | integer | 起批量 |
| products[].quantityPrices | string | 价格区间 |
| products[].salesOrderCount | integer | 销售笔数（按统计周期返回对应的值） |
| products[].salesQuantity | integer | 销售件数（按统计周期返回对应的值） |
| products[].estimatedSalesAmount | integer | 预估销售额（按统计周期返回对应的值） |
| products[].dataType | string | 数据类型：`weeklyData` = 周数据，`monthlyData` = 月数据 |
| products[].availableDate | string | 商品上架时间，格式为 `yyyy-MM-dd HH:mm:ss` |
| products[].deliveryTime | string | 发货时间 |
| products[].levelName | string | 类目层级名称 |
| products[].company | string | 店铺名称 |
| products[].shopId | string | 店铺id |
| products[].shopUrl | string | 店铺链接地址 |
| products[].asinUrl | string | 商品链接地址 |
| products[].imageUrl | string | 图片地址 |
| products[].sourceType | string | 来源平台（1688） |
| products[].sourceTool | string | 来源工具 |
### 错误处理

通常 HTTP 200，业务成功通过 `errorCode`/`errcode=200` 判断；`401` 为认证失败，`402` 为积分不足，其他非200值读取 `errmsg`。HTTP 401/402 按顶层 `references/onboarding.md` 处理。日期不符合周日/当月1日、超出数据窗口或筛选过窄时，解释错误并建议调整，不自动连续重试。

## 调用与展示规则

1. 非中文关键词先翻译为中文并告知用户；先确定周榜/月榜、对应日期、排序字段和筛选条件。
2. 同一任务内相同参数不得重复调用；继续查询分页或刷新榜单前说明调用消耗并等用户决定。
4. 用表格展示标题、批发价、代发价、订单数、销售件数、预估销售额、供应商、上架日期、商品链接、店铺链接和图片；价格注明 CNY/RMB 与价格语义。
5. 显示总记录数与当前页；有更多页只提示用户可继续请求。按 `dataType` 标注周/月数据，不能把榜单指标写成保证销量或收入。

## 示例

完整 `proxy_call` 参数示例：

```json
{
  "toolName": "dld/productBillboard",
  "arguments": {
    "keyWord": "手机壳",
    "pageType": 3,
    "date": "2026-08-01",
    "sortField": "orderCount",
    "sortType": "desc",
    "pageIndex": 1,
    "pageSize": 20
  }
}
```

月榜：

```json
{"keyWord":"手机壳","pageType":3,"date":"2026-08-01","sortField":"orderCount","sortType":"desc","pageIndex":1,"pageSize":20}
```

周榜按预估销售额排序：

```json
{"keyWord":"瑜伽垫","pageType":2,"date":"2026-08-23","sortField":"saleVolume","sortType":"desc","pageIndex":1,"pageSize":20}
```

工厂、跨境和发货筛选：

```json
{"keyWord":"LED灯","companyType":2,"offerType":4,"sendTime":"24","beginPrice":5,"endPrice":100,"sortField":"saleCount","sortType":"desc"}
```

如果用户需要实时近7/30天指标，改用 `linkfox-dld-product-search`；如果要判断某个商品的 SKU 采购价，改用商品详情。

## 反馈 API

用户表达赞扬、不满、建议或结果错误时，可按本子能力契约 POST `https://skill-api.linkfox.com/api/v1/public/feedback`，字段为 `skillName`（`linkfox-dld-product-billboard`）、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和 `content`；不要与商品网关混用 base URL。
