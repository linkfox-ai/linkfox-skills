# MPSTATS Ozon 商品详情（批量）API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/productDetail`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「MPSTATS-Ozon-商品详情」入参 schema 一致（同步日期 2026-04-30）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productIds | array | 是 | Ozon 商品 ID 列表（整数或字符串），**单次最多 100 个**，超过请分批调用 |
| startDate | string | 否 | 统计起始日，格式 `YYYY-MM-DD`；整批共享；最晚可选昨日 |
| endDate | string | 否 | 统计结束日，格式 `YYYY-MM-DD`；整批共享；最晚可选昨日 |
| includeFbs | boolean | 否 | 是否包含 FBS 数据；整批共享 |

> 服务端并发请求每个 SKU，单条失败自动重试一次；支持部分成功。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（字符串），`"200"` 表示成功 |
| errcode | integer | 返回码（整数），`200` 表示成功 |
| msg / errmsg | string | 消息；成功为 `ok` |
| total | integer | 返回的 SKU 数（= `successCount` + `failedCount`） |
| successCount | integer | 成功返回卡片的 SKU 数 |
| failedCount | integer | 失败的 SKU 数 |
| failures | array | 失败 SKU 明细列表（每项含失败的 `productId` 与错误信息） |
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

## 错误码

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` |
| 401 | 认证失败 | 检查 `Authorization` 请求头是否正确携带 API Key |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` / `msg`；常见为批量超过 100、日期越过昨日等 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/mpstats/ozon/productDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "productIds": [1786874757, 151623766, 142257239],
    "startDate": "2025-03-01",
    "endDate": "2025-03-31",
    "includeFbs": true
  }'
```

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-product-detail",
  "sentiment": "NEGATIVE",
  "category": "BUG",
  "content": "Batch with 80 SKUs returned only 40 entries."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content`：用户表达、实际现象、为什么算问题或好评
