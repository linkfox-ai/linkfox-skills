# linkfox-keepa-product-series

## 功能说明

通过 Keepa 查询单个 Amazon ASIN 的历史时序数据，用于分析 Buy Box/新品/Deal/Prime/FBA/FBM/优惠券价格、主类目和子类目 BSR、卖家数、评分、评分数以及月销量随时间的变化。所有序列点通常为 `{time, value}`；BSR 序列按类目返回 `{categoryName, points}`。

适用请求包括价格历史、降价/促销变化、BSR 趋势、FBA/FBM 价格对比、卖家竞争变化、评分变化和月销量历史。该端点一次只支持一个 ASIN；多 ASIN 详情用 `productRequest`，无 ASIN 的条件找品用 `productSearch`。

## 能力边界与特殊规则

- `asin`、`domain` 必填；`asin` 只能是单个 ASIN，最大长度 1000。
- `days` 默认 90，允许 1—365；超过 365 不能请求。采样点按 Keepa 捕获变化产生，不保证每日固定一个点。
- Buy Box 价格、评分、评分数、月销量和子类目 BSR 为核心序列；按需将 `show*` 标记设为 `1` 获取额外价格、主类目 BSR 或卖家数序列。
- BSR 数值越小表示销售排名越好；“排名改善”应解释为数值下降，“排名变差”应解释为数值上升。
- 时间序列数据量较大，启用更多 `show*` 或拉长 `days` 会增加响应大小和 Keepa token 消耗；失败或空结果不得自动换日期、ASIN 或参数连续试探。
- 本端点提供商品级历史指标，不提供关键词趋势、市场级聚合、实时库存、评论正文或广告数据。

## MCP 调用

- **MCP server**：`LinkFox`（`https://mcp-tool-gateway.linkfox.com/mcp/any-tool`）。
- **唯一工具**：`proxy_call`。
- **toolName**：`keepa/productSeries`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
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
| `asin` | string | 是 | 单个 ASIN，最大长度 1000 |
| `domain` | string | 是 | Amazon 站点 ID，见站点表 |
| `days` | integer | 否 | 历史天数，默认 90，范围 1—365 |
| `showPrice` | integer | 否 | `1` 返回市场最低新品价 |
| `showPriceList` | integer | 否 | `1` 返回划线价/标价 |
| `showPriceDeal` | integer | 否 | `1` 返回闪促价格 |
| `showPricePrime` | integer | 否 | `1` 返回 Prime 专属新品价 |
| `showPriceFba` | integer | 否 | `1` 返回第三方 FBA 新品价 |
| `showPriceFbm` | integer | 否 | `1` 返回第三方 FBM 新品价 |
| `showPriceCoupon` | integer | 否 | `1` 返回优惠券后 Buy Box 价 |
| `showBsrMain` | integer | 否 | `1` 返回大类 BSR |
| `showSellerCount` | integer | 否 | `1` 返回卖家数 |

## 响应字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| asin | string | ASIN |
| buyboxPrice | array | Buybox价格（time=时间，value=Buybox价格） |
| buyboxPrice[].time | 来源未说明 | 时间 |
| buyboxPrice[].value | 来源未说明 | Buybox价格 |
| price | array | 价格（time=时间，value=价格） |
| price[].time | 来源未说明 | 时间 |
| price[].value | 来源未说明 | 价格 |
| priceList | array | 划线价（time=时间，value=划线价格） |
| priceList[].time | 来源未说明 | 时间 |
| priceList[].value | 来源未说明 | 划线价格 |
| priceDeal | array | Deal价格（time=时间，value=Deal价格） |
| priceDeal[].time | 来源未说明 | 时间 |
| priceDeal[].value | 来源未说明 | Deal价格 |
| pricePrime | array | Prime价格（time=时间，value=Prime价格） |
| pricePrime[].time | 来源未说明 | 时间 |
| pricePrime[].value | 来源未说明 | Prime价格 |
| priceFba | array | FBA价格（time=时间，value=FBA价格） |
| priceFba[].time | 来源未说明 | 时间 |
| priceFba[].value | 来源未说明 | FBA价格 |
| priceFbm | array | FBM价格（time=时间，value=FBM价格） |
| priceFbm[].time | 来源未说明 | 时间 |
| priceFbm[].value | 来源未说明 | FBM价格 |
| priceCoupon | array | coupon价格（time=时间，value=coupon价格） |
| priceCoupon[].time | 来源未说明 | 时间 |
| priceCoupon[].value | 来源未说明 | coupon价格 |
| bsrMain | array | 大类BSR，每个元素包含 `categoryName`（类目名称）和 `points`（time=时间，value=排名） |
| bsrMain[].categoryName | 来源未说明 | 类目名称 |
| bsrMain[].points | 来源未说明 | 该类目的时序点 |
| bsrMain[].points[].time | 来源未说明 | 时间 |
| bsrMain[].points[].value | 来源未说明 | 排名 |
| bsrSub | array | 小类BSR，每个元素包含 `categoryName`（类目名称）和 `points`（time=时间，value=排名） |
| bsrSub[].categoryName | 来源未说明 | 类目名称 |
| bsrSub[].points | 来源未说明 | 该类目的时序点 |
| bsrSub[].points[].time | 来源未说明 | 时间 |
| bsrSub[].points[].value | 来源未说明 | 排名 |
| sellerCount | array | 卖家数（time=时间，value=卖家数） |
| sellerCount[].time | 来源未说明 | 时间 |
| sellerCount[].value | 来源未说明 | 卖家数 |
| rating | array | 评分（time=时间，value=评分） |
| rating[].time | 来源未说明 | 时间 |
| rating[].value | 来源未说明 | 评分 |
| ratingCount | array | 评分数（time=时间，value=评分数） |
| ratingCount[].time | 来源未说明 | 时间 |
| ratingCount[].value | 来源未说明 | 评分数 |
| monthlySold | array | 子体销量（time=时间，value=销量） |
| monthlySold[].time | 来源未说明 | 时间 |
| monthlySold[].value | 来源未说明 | 销量 |
| costToken | integer | 消耗token |

## 调用选择

价格分析按需开启 `showPrice`、`showPriceList`、`showPriceDeal`、`showPriceCoupon`；比较 FBA 与 FBM 时同时开启 `showPriceFba` 和 `showPriceFbm`；需要根类目排名时开启 `showBsrMain`；需要竞争强度时开启 `showSellerCount`。完整健康检查才使用全部 `show*` 标记，以控制响应大小和成本。

## 错误处理

正常情况下 HTTP 状态为 200，业务结果通过响应体中的 `errorCode`/`errcode` 区分；未授权通常返回 HTTP 401。

| 状态/字段 | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 按序列字段解析并报告 `costToken` |
| `401` | 认证失败 | 读取 `references/onboarding.md`，区分 MCP/代理层与下游业务层处理 |
| `402` | 积分不足 | 读取 `references/onboarding.md`，引导用户访问 LinkFox 账号页检查积分或套餐；不自动购买 |
| 其他非 200 值 | 业务异常 | 透传 `errmsg`，检查 ASIN、站点、天数和 show 参数 |

## MCP 示例

```json
{
    "toolName":  "keepa/productSeries",
    "arguments":  {
                      "asin":  "B0DFRJ7WSX",
                      "domain":  "1",
                      "days":  90,
                      "showPrice":  1,
                      "showBsrMain":  1,
                      "showSellerCount":  1
                  }
}
```

## 反馈接口

反馈接口与 Keepa 网关分离：`POST https://skill-api.linkfox.com/api/v1/public/feedback`。JSON 使用 `skillName`、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和 `content`。当结果与意图不符、出现错误、用户表扬/不满或提出改进意见时按此规则上报，不中断当前流程。


