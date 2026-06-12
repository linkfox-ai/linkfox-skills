# MPSTATS Ozon 品牌商品 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/mpstats/ozon/brandProducts`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「MPSTATS-Ozon-品牌商品」入参 schema 一致（同步日期 2026-04-30）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| brandName | string | 是 | Ozon 品牌展示名（俄语或拉丁） |
| startDate | string | 否 | 统计起始日，`YYYY-MM-DD`；最晚昨日 |
| endDate | string | 否 | 统计结束日，`YYYY-MM-DD`；最晚昨日 |
| page | integer | 否 | 页码，从 1 开始 |
| pageSize | integer | 否 | 每页行数，1-100，默认 100 |
| sortField | string | 否 | 排序列名（snake_case），如 `sales`、`revenue`、`final_price`、`balance`、`rating` |
| sortDirection | string | 否 | `asc` 升序 / `desc` 降序 |
| currency | string | 否 | 结果金额货币代码，默认 `RUB`，如 `USD` / `EUR` / `CNY` |
| currencyRate | integer | 否 | 自定义汇率（配合非默认货币） |
| includeFbs | boolean | 否 | 是否纳入 FBS 数据 |
| filters | array | 否 | 数值筛选条件列表，每项 `{field, op, value, value2?}`，多条件 AND |

### filters 字段说明

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| field | string | 是 | 列名（snake_case），常用见下 |
| op | string | 是 | `GTE` / `LTE` / `GT` / `LT` / `EQ` / `NOT_EQ` / `BETWEEN` |
| value | number | 是 | 主值（`BETWEEN` 时为下界） |
| value2 | number | `BETWEEN` 必填 | 上界（闭区间） |

**常用 field**：`sales`（月销）、`final_price`（售价 RUB）、`rating`（评分 0-5）、`comments`（评论数）、`balance`（库存）、`revenue`（销售额 RUB）、`days_in_stock`（有货天数）、`turnover_days`（周转天数）、`lost_profit`（损失销售额 RUB）、`category_position`（类目排名）。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 成功 |
| msg | string | 消息；成功为 `ok` |
| total | integer | 品牌下命中商品总数 |
| products | array | 商品列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

### products[*] 商品对象字段（39 个）

按官方 outputSchema 定义（`_mpstats_ozon_brandProducts`，同步日期 2026-05-06）。该 schema 与 `productSearch` / `categoryProducts` / `sellerProducts` **完全共用**；4 个端点只是查询维度不同，返回的商品卡字段集完全一致。

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
| position | integer | 当前查询维度（本端点为品牌）内排名 |
| categoryPosition | integer | 品类内排名 |
| revenueSharePercent | number | 该 SKU 在当前查询维度的销售额占比，0-100 |

## 错误码

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 解析 `products` |
| 401 | 认证失败 | 检查 `Authorization` |
| 其他 | 业务异常 | 查看 `errmsg`；常见为 `brandName` 拼写错误、日期越过昨日等 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/mpstats/ozon/brandProducts \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "brandName": "adidas",
    "sortField": "sales",
    "sortDirection": "desc",
    "pageSize": 50,
    "filters": [
      {"field": "rating", "op": "GTE", "value": 4.5}
    ]
  }'
```

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-brand-products",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "Would like fuzzy brand-name matching."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content`：用户表达、实际现象、为什么算问题或好评
