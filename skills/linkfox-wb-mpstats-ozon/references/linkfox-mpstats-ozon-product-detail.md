# linkfox-mpstats-ozon-product-detail

## 能力说明

按 Ozon SKU 批量读取 MPSTATS 商品卡，回答价格、折扣、评分、评论、库存、配送、统计期销量与销售额等核验问题。一次最多 100 个 `productIds`；服务端并发处理并对单 SKU 失败自动重试一次，允许部分成功。该 operation 是统计期汇总，不是每日时间序列；单 SKU 的逐日走势使用 `productTrend`。

## MCP 调用与请求参数

- 响应字段来源：`skills/linkfox-mpstats-ozon-product-detail/references/api.md`。仅从该文件核对并恢复响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`mpstats/ozon/productDetail`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游业务代码与消息。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

```json
{
  "toolName": "mpstats/ozon/productDetail",
  "arguments": {
    "productIds": [
      "123456789"
    ],
    "startDate": "2026-08-01",
    "endDate": "2026-08-31"
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `productIds` | array<integer\|string> | 是 | SKU 列表，单次最多 100 个 |
| `startDate` | string | 否 | `YYYY-MM-DD`，统计起始日，最晚昨日 |
| `endDate` | string | 否 | `YYYY-MM-DD`，统计结束日，最晚昨日 |
| `includeFbs` | boolean | 否 | 是否把 FBS 数据纳入本批次；整批共享 |

统计期的 `previousSalesUnits`/`previousRevenue` 是等长上一周期；`revenuePotential` 是假设整个窗口有货的潜在销售额；`lostProfit`/`lostProfitPercent` 用于描述缺货损失。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（字符串），`"200"` 表示成功 |
| errcode | integer | 返回码（整数），`200` 表示成功 |
| msg / errmsg | string | 消息；成功为 `ok` |
| total | integer | 返回的 SKU 数（通常为 0 或 1，= `successCount` + `failedCount`） |
| successCount | integer | 成功返回卡片的 SKU 数（通常为 0 或 1） |
| failedCount | integer | 失败的 SKU 数（通常为 0 或 1） |
| failures | array | 失败 SKU 明细列表（通常最多 1 项，每项含失败的 `productId` 与错误信息） |
| products | array | 商品卡列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

### products[*] 商品详情字段（36 个）

按官方 outputSchema 定义（`_mpstats_ozon_productDetail`，同步日期 2026-05-06）。**detail 的字段集与 brand/category/seller 不同**：detail 独有 `previous*` / `revenuePotential` / `deliveryScheme` / `productImageUrls` 等深度字段，但不返回 `brandId` / `country` / `category` / `minPrice/maxPrice/averagePrice` / `balanceFbs` / `frozenStocks` / `warehousesCount` / `daysInSite/daysInStock/turnoverDays` / `position/categoryPosition/revenueSharePercent` / `isFbs`。

**身份与基础信息**

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | SKU ID |
| title | string | 商品名称（俄语） |
| brand | string | 品牌 |
| sellerName | string | 卖家名 |
| sellerId | integer | 卖家 ID |
| sellerIsBestSeller | boolean | 卖家是否为畅销卖家 |
| nicheName | string | 赛道路径（俄语，`/` 分隔） |
| nicheId | integer | 赛道 ID |
| firstDate | string | 上架日期（`yyyy-MM-dd`） |
| updated | string | 数据更新时间（`yyyy-MM-dd HH:mm:ss`） |
| note | string | 备注 |
| sourceTool / sourceType | string | 来源工具 / 数据源标识 |

**图片**

| 字段 | 类型 | 说明 |
|------|------|------|
| imageUrl | string | 主图 URL（首张大图） |
| imageCount | integer | 图片总数 |
| productImageUrls | array<string> | 除主图外的其余大图 URL |
| productPageUrl | string | 商品页 URL |

**价格与折扣**

| 字段 | 类型 | 说明 |
|------|------|------|
| price | number | 当前售价 |
| oldPrice | number | 折扣前原价 |
| ozonCardPrice | number | Ozon Card 价（银行卡优惠价） |
| discount | integer | 折扣，百分比整数 0-100 |
| currency | string | 币种符号（`₽` / `$` / `€`） |

**评分**

| 字段 | 类型 | 说明 |
|------|------|------|
| rating | number | 评分，0-5 |
| reviewCount | integer | 评论数 |

**库存与配送**

| 字段 | 类型 | 说明 |
|------|------|------|
| balance | integer | 当前库存（件） |
| deliveryScheme | string | 配送方案；`FBO`=Ozon 仓配，`FBS`=卖家自配 |

**销售与收入（当期 + 上期对比）**

| 字段 | 类型 | 说明 |
|------|------|------|
| salesPerDay | number | 日均销量（件/日） |
| salesPerDayWithStock | number | 有货日均销量（仅计有库存日） |
| dailySalesRevenue | number | 日均销售额 |
| dailySalesRevenueWithStock | number | 有货日均销售额 |
| monthlySalesUnits | integer | 统计期销量（件） |
| monthlySalesRevenue | number | 统计期销售额 |
| previousSalesUnits | integer | 上期销量（与本统计周期等长的前一段时间） |
| previousRevenue | number | 上期销售额 |
| revenuePotential | number | 潜在销售额（按全期有库存估算） |
| lostProfit | number | 损失销售额（缺货等造成） |
| lostProfitPercent | number | 损失销售额占比（%） |

### `failures[]` 中来源明确的字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `failures[].productId` | 来源未说明 | 失败的 SKU；来源未说明具体类型 |

## 错误与展示

- `200`：解析 `products`；`401`：认证失败；`402`：积分或余额不足；其他错误读取 `msg`/`errmsg`，常见为超过 100 个 SKU 或日期越过昨日。
- `failedCount > 0` 时逐项展示 `failures` 中的 `productId` 和错误信息。不要把部分成功当成完整成功。
- 紧凑表格优先 `productId/title/price/monthlySalesUnits/monthlySalesRevenue/rating/reviewCount/balance/deliveryScheme/firstDate`；货币遵循响应 `currency`，默认 Ozon 口径为 RUB；混合 FBO/FBS 时说明配送口径。

## Feedback API

反馈接口为 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，body 的 `skillName` 必须为 `linkfox-mpstats-ozon-product-detail`，其余字段为 `sentiment`、`category`、`content`。

认证/计费处理见 `references/onboarding.md`。

