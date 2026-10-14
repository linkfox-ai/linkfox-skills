# linkfox-dld-product-search

## 功能与边界

按中文关键词、商品 URL 或商品 ID 在1688商品库中发现和筛选货源，返回商品标题、ID、图片、批发/代发价格、价格区间、MOQ、7日/30日销售指标、发货时效、供应商身份和店铺链接。适合找工厂、批发价对比、代发、跨境标签、新品、销量或履约条件筛选。

不提供店铺级流量/排名分析、广告、评价、物流成本、订单处理、谈价或交易。关键词必须为中文；这是商品级搜索，不是热销榜历史查询（榜单用 `linkfox-dld-product-billboard`）。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`dld/productSearch`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP/`isError`，代理成功后读取 text 或 structured content；text 为 JSON 时只解析一次，再按响应字段处理下游状态。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想时不得自动重试或改参数探测。
### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `keyWord` | string | 否 | — | 中文关键词，最多50字符 |
| `goodsUrl` | string | 否 | — | 商品链接，与 `keyWord` 二选一 |
| `productIds` | string | 否 | — | 多个商品 ID 用逗号分隔，最多20个 |
| `cycle` | string | 否 | — | `7` 近7天或 `30` 近30天 |
| `searchType` | integer | 否 | 1 | `1` 模糊匹配，`3` 精准匹配 |
| `sortField` | string | 否 | `orderCount30d` | `orderCount7d`、`saleCount7d`、`saleVolume7d`、`orderCount30d`、`saleCount30d`、`saleVolume30d`、`offerCreateTime`、`price`、`consignPrice` |
| `sortType` | string | 否 | `desc` | `desc` 或 `asc` |
| `pageIndex` | integer | 否 | 1 | 页码，从1开始 |
| `pageSize` | integer | 否 | 20 | 每页10–100条 |
| `beginPrice` / `endPrice` | number | 否 | — | 批发价范围 |
| `beginConsignPrice` / `endConsignPrice` | number | 否 | — | 代发价范围 |
| `beginOrderCount` / `endOrderCount` | integer | 否 | — | 销售笔数范围 |
| `beginSaleCount` / `endSaleCount` | integer | 否 | — | 销售件数范围 |
| `beginSaleVolume` / `endSaleVolume` | number | 否 | — | 预估销售额范围 |
| `beginStartQuantity` / `endStartQuantity` | integer | 否 | — | 起购数量范围 |
| `beginTpYear` / `endTpYear` | integer | 否 | — | 诚信通年限范围 |
| `beginOfferCreateTime` / `endOfferCreateTime` | string | 否 | — | 上架时间范围，`YYYY-MM-DD` |
| `companyType` | integer | 否 | 0 | `0`不限、`1`店铺、`2`工厂 |
| `offerType` | integer | 否 | 0 | `0`不限、`2`新品、`3`1688严选、`4`跨境、`5`定制、`6`镇店之宝 |
| `shiLiType` | string | 否 | — | 逗号分隔 `superFactory`、`Power`、`TrustPass` |
| `sendTime` | string | 否 | — | 逗号分隔 `24`、`48`、`72` 小时 |
| `faceToFaceSupport` | string | 否 | — | `441218`淘宝、`386434`抖音、`422914`拼多多、`422978`小红书、`386370`快手 |
| `proxyRights` | string | 否 | — | `4360897`一件代发包邮、`449154`先采后付 |
| `shopService` | string | 否 | — | `4057409`安心购、`888777`深度认证报告 |
| `buyerProtections` | string | 否 | — | `商品包邮`、`7天包退货`、`支持运费险` |

多个枚举条件用逗号连接；`keyWord`、`goodsUrl`、`productIds` 的使用方式以用户输入为准，不能凭空补造商品 ID。

### 响应字段

#### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| total | integer | 总记录数 |
| type | string | 渲染样式 |
| columns | array | 渲染列定义 |
| products | array | 商品列表（详见下方字段） |

#### `products[]`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| products[].offerId | string | 商品ID |
| products[].asin | string | 商品编号 |
| products[].title | string | 商品标题 |
| products[].asinUrl | string | 商品链接地址 |
| products[].imageUrl | string | 商品图片地址 |
| products[].price | number | 批发价 |
| products[].consignPrice | number | 代发价 |
| products[].quantityPrices | string | 价格区间 |
| products[].quantityBegin | integer | 起批量 |
| products[].unit | string | 单位 |
| products[].currency | string | 币种 |
| products[].salesOrderCount | integer | 销售笔数（按统计周期） |
| products[].salesQuantity | integer | 销售件数（按统计周期） |
| products[].estimatedSalesAmount | integer | 预估销售额（按统计周期） |
| products[].deliveryTime | string | 发货时间 |
| products[].availableDate | string | 商品上架时间 |
| products[].levelName | string | 类目层级名称 |
| products[].company | string | 店铺名称 |
| products[].shopId | string | 店铺ID |
| products[].shopUrl | string | 店铺链接地址 |
| products[].dataType | string | 数据类型：weeklyData（周数据）、monthlyData（月数据） |
| products[].sourceType | string | 来源平台（1688） |
| products[].sourceTool | string | 来源工具 |
### 错误处理

通常 HTTP 200，业务成功由 `errorCode`/`errcode=200` 判断；`401` 为认证失败，`402` 为积分不足，其他非200值读取 `errmsg`。HTTP 401/402 读取顶层 `references/onboarding.md`。关键词拼写、类型/格式、筛选过窄或分页无结果时给出修正建议，不自动改词或连续试探。

## 调用与展示规则

1. 英文或其他语言关键词先翻译成中文，并在结果中标明原词和译词；按 `cycle` 标注近7日或近30日。
2. 同一任务内相同参数不得重复调用；翻页、刷新或改变筛选前先说明可能的额外消耗并由用户决定。
4. 用结构化表格展示标题、商品链接、图片、批发价、代发价、销售笔数/件数、预估销售额、MOQ、发货时效和供应商信息；价格注明 CNY/RMB 与批发/代发含义。
5. `total` 大于当前页时告知总数和可继续请求的页码；图片存在时内联显示。缺失字段显示未知，不把销量当作保证，不把供应商指标改写为质量承诺。

## 示例

完整 `proxy_call` 参数示例：

```json
{
  "toolName": "dld/productSearch",
  "arguments": {
    "keyWord": "瑜伽垫",
    "cycle": "30",
    "sortField": "saleCount30d",
    "sortType": "desc",
    "pageIndex": 1,
    "pageSize": 20
  }
}
```

关键词按30日销量排序：

```json
{"keyWord":"瑜伽垫","cycle":"30","sortField":"saleCount30d","sortType":"desc","pageIndex":1,"pageSize":20}
```

工厂与价格筛选：

```json
{"keyWord":"蓝牙耳机","companyType":2,"beginPrice":10,"endPrice":50,"cycle":"30","sortField":"orderCount30d","sortType":"desc"}
```

跨境代发筛选：

```json
{"keyWord":"手机壳","offerType":4,"proxyRights":"4360897","cycle":"7","sortField":"saleVolume7d","sortType":"desc"}
```

指定商品链接或 ID：

```json
{"goodsUrl":"https://detail.1688.com/offer/805578065498.html","cycle":"30"}
```

```json
{"productIds":"123456,789012","cycle":"30","pageSize":20}
```

若用户表达的是“历史周/月榜”，改用榜单；若已有单个商品并要 SKU 价格、证书或件重尺，改用商品详情。

## 反馈 API

用户表达赞扬、不满、建议或结果错误时，可按本子能力契约 POST `https://skill-api.linkfox.com/api/v1/public/feedback`，字段为 `skillName`（`linkfox-dld-product-search`）、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和 `content`；不要与商品网关混用 base URL。
