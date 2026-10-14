# linkfox-mpstats-ozon-product-trend

## 能力说明

返回一个 Ozon SKU 在日期窗口内的分日价格、销量、库存、评分和商品标记，用于观察增长、季节性、价格变化和缺货波动。每次只能传一个 `productId`；若要批量商品卡汇总，使用 `productDetail`。MPSTATS 数据延迟一天，结束日期不能晚于昨日。

## MCP 调用与请求参数

- 响应字段来源：`skills/linkfox-mpstats-ozon-product-trend/references/api.md`。仅从该文件核对并恢复响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`mpstats/ozon/productTrend`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游业务代码与消息。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

```json
{
  "toolName": "mpstats/ozon/productTrend",
  "arguments": {
    "productId": "123456789",
    "startDate": "2026-08-01",
    "endDate": "2026-08-31"
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `productId` | integer | 是 | 单个数字型 Ozon SKU |
| `startDate` | string | 否 | `YYYY-MM-DD`，统计起始日，最晚昨日 |
| `endDate` | string | 否 | `YYYY-MM-DD`，统计结束日，最晚昨日 |
| `includeFbs` | boolean | 否 | 是否包含 FBS 数据 |
| `includeSearchStats` | boolean | 否 | 请求搜索位次/可见性扩展；部分赛道不支持 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（字符串），`"200"` 表示成功 |
| errcode | integer | 返回码（整数），`200` 表示成功 |
| msg / errmsg | string | 消息；成功为 `ok` |
| total | integer | 分日数据点数量（窗口天数） |
| data | array | 分日数据点列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

> 注意：**分日序列字段名为 `data`**，不是 `trend`；响应体不包含独立的 `productId` 回显。

### data 数据点字段

按官方 outputSchema 定义（`_mpstats_ozon_productTrend`，同步日期 2026-05-06）。共 13 个字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期，`YYYY-MM-DD` |
| hasData | boolean | 当日是否有数据（`false` 表示缺失日，区别于 `sales=0`） |
| price | number | 当日售价 |
| oldPrice | number | 当日折扣前原价 |
| ozonCardPrice | number | Ozon Card 价（Ozon 官方银行卡优惠价） |
| discount | integer | 折扣，百分比整数 0-100 |
| currency | string | 币种符号（如 `₽` / `$` / `€`） |
| sales | integer | 当日销量（件） |
| balance | integer | 当日 FBO 仓库库存（件） |
| rating | number | 评分，取值 0-5 |
| comments | integer | 评论数 |
| isBestseller | boolean | 当日是否带"畅销"标识 |
| isNew | boolean | 当日是否带"新品"标识 |

> **Schema 未声明的字段不会返回**：端点不独立返回 `revenue`、`reviewCount`、`balanceFbs`、`isInStock` 等；如需销售额，用 `sales × price` 估算。

### includeSearchStats 说明

入参层 `includeSearchStats=true` 仅作为服务端可选能力开关；官方 outputSchema 未声明任何额外顶层数组或 per-point 字段。若未来 schema 扩展，请以工具网关 `listEnabledTool` 返回的最新 outputSchema 为准。

## 错误与展示

- `200`：解析 `data`；`401`：认证失败；`402`：积分或余额不足；其他错误读取 `msg`/`errmsg`，常见为 `productId` 无效或日期越过昨日。
- 展示可用逐日表格或 sparkline 友好格式，列出 `date/price/sales/balance/rating/comments`。事实性标注单日尖峰和 `balance=0` 连续缺货，不把走势直接变成采购建议。

## Feedback API

反馈接口为 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，body 的 `skillName` 必须为 `linkfox-mpstats-ozon-product-trend`，其余字段为 `sentiment`、`category`、`content`。

认证/计费处理见 `references/onboarding.md`。

