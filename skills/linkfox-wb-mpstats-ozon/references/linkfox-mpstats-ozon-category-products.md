# linkfox-mpstats-ozon-category-products

## 能力说明

按 Ozon 使用的俄语完整类目路径查询该类目下的商品 SKU，并按销量、销售额、价格、评分、库存、周转和损失销售额筛选排序。适用于类目爆款挖掘、细分类目机会扫描和类目内品牌/卖家格局观察。`categoryPath` 必须是完整路径，层级用 `/` 分隔，例如 `Одежда/Женская одежда/Футболки и топы женские`；本 operation 不负责浏览类目树。

## MCP 调用与请求参数

- 响应字段来源：`skills/linkfox-mpstats-ozon-category-products/references/api.md`。仅从该文件核对并恢复响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`mpstats/ozon/categoryProducts`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游业务代码与消息。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

```json
{
  "toolName": "mpstats/ozon/categoryProducts",
  "arguments": {
    "categoryPath": "Одежда / Обувь",
    "startDate": "2026-08-01",
    "endDate": "2026-08-31",
    "page": 1,
    "pageSize": 20
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `categoryPath` | string | 是 | 俄语完整类目路径，层级用 `/` 分隔 |
| `startDate` / `endDate` | string | 否 | `YYYY-MM-DD`，统计窗口，最晚昨日 |
| `page` | integer | 否 | 页码，从 1 开始 |
| `pageSize` | integer | 否 | 每页 1–100，默认 100 |
| `sortField` | string | 否 | snake_case 列名，如 `sales`、`revenue`、`final_price`、`balance`、`rating` |
| `sortDirection` | string | 否 | `asc` 或 `desc` |
| `currency` | string | 否 | 金额货币，默认 `RUB`，可用 `USD` 等 |
| `currencyRate` | integer | 否 | 非默认货币时自定义汇率 |
| `includeFbs` | boolean | 否 | 是否纳入 FBS 数据 |
| `filters` | array | 否 | 数值条件列表，多个条件 AND 连接 |

`filters[]` 形如 `{"field":"<snake_case>","op":"<OP>","value":<num>,"value2":<num>}`。`op` 可为 `GTE`、`LTE`、`GT`、`LT`、`EQ`、`NOT_EQ`、`BETWEEN`；`BETWEEN` 需要 `value2` 作为闭区间上界。常用 field：`sales`、`final_price`、`rating`、`comments`、`balance`、`revenue`、`days_in_stock`、`turnover_days`、`lost_profit`、`category_position`。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 成功 |
| msg | string | 消息；成功为 `ok` |
| total | integer | 类目下命中商品总数 |
| products | array | 商品列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

### products[*] 商品对象字段（39 个）

按官方 outputSchema 定义（`_mpstats_ozon_categoryProducts`，同步日期 2026-05-06）。该 schema 与 `productSearch` / `brandProducts` / `sellerProducts` **完全共用**；4 个端点只是查询维度不同，返回的商品卡字段集完全一致。

**身份与基础信息**

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | SKU ID |
| title | string | 商品名称（俄语） |
| brand | string | 品牌 |
| brandId | integer | 品牌 ID |
| sellerName | string | 卖家名 |
| sellerId | integer | 卖家 ID |
| category | string | 品类路径（俄语，`/` 分隔） |
| nicheName | string | 赛道路径（俄语） |
| nicheId | integer | 赛道 ID |
| country | string | 销售国，Ozon 恒为 `RU` |
| firstDate | string | 上架日期（`yyyy-MM-dd`） |
| imageUrl | string | 主图 URL |
| productPageUrl | string | 商品页 URL |
| sourceTool / sourceType | string | 来源工具 / 数据源标识 |

**价格与货币**

| 字段 | 类型 | 说明 |
|------|------|------|
| price | number | 当前售价 |
| oldPrice | number | 折扣前原价 |
| ozonCardPrice | number | Ozon Card 价 |
| minPrice / maxPrice / averagePrice | number | 统计期内最低价 / 最高价 / 均价 |
| currency | string | 币种符号（`₽` / `$` / `€`） |

**评分与评论**

| 字段 | 类型 | 说明 |
|------|------|------|
| rating | number | 评分，0-5 |
| reviewCount | integer | 评论数 |

**库存与 FBS**

| 字段 | 类型 | 说明 |
|------|------|------|
| balance | integer | 当前库存（件） |
| balanceFbs | integer | FBS 库存（卖家自发货件数） |
| frozenStocks | integer | 滞销库存 |
| warehousesCount | integer | FBO 分仓数 |
| isFbs | boolean | 是否 FBS 发货 |

**销售与周转**

| 字段 | 类型 | 说明 |
|------|------|------|
| salesPerDay | number | 日均销量（件/日） |
| monthlySalesUnits | integer | 统计期销量（件） |
| monthlySalesRevenue | number | 统计期销售额 |
| lostProfit | number | 损失销售额（缺货等造成） |
| daysInSite | integer | 在售天数（统计期，含缺货日） |
| daysInStock | integer | 有货天数 |
| turnoverDays | number | 周转天数（越小越快） |

**排名与占比**

| 字段 | 类型 | 说明 |
|------|------|------|
| position | integer | 当前查询维度（本端点为类目）内排名 |
| categoryPosition | integer | 品类内排名 |
| revenueSharePercent | number | 该 SKU 在当前查询维度的销售额占比，0-100 |

## 错误与展示

- `200`：解析 `products`；`401`：认证失败；`402`：积分或余额不足；其他错误读取 `msg`/`errmsg`，常见为路径不完整/非俄语或日期越过昨日。
- 展示 `total`、页码和每页行数；类目很大时优先收紧筛选。说明 `position` 越低越靠前，`revenueSharePercent` 只属于本次类目结果集；转换货币时明确标注。

## Feedback API

反馈接口为 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，body 的 `skillName` 必须为 `linkfox-mpstats-ozon-category-products`，其余字段为 `sentiment`、`category`、`content`。

认证/计费处理见 `references/onboarding.md`。

