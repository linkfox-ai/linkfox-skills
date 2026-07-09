# EchoTik-TikTok商品批量详情 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/batchProductDetail`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productIds | array&lt;string&gt; | 否* | 商品ID列表（最多 1000 个）。示例：`["1729382310407603945", "1729382310407603946"]` |
| productUrls | array&lt;string&gt; | 否* | 商品URL列表（最多 1000 个），形如 `https://shop.tiktok.com/us/pdp/<slug>/<productId>?...`；后端会从每个URL中提取末尾的 `productId` 并合并到 `productIds`，与 `productIds` 不互斥 |

\* `productIds` 与 `productUrls` 至少传其一，可同时传入；二者合并后最多 1000 个商品。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| products | array | 商品详情列表（详见下方商品对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 商品对象字段

> 销量、GMV、直播、视频、达人、观看等指标均按 `1d / 7d / 15d / 30d / 60d / 90d` 多周期及累计（total）返回。价格字段单位均为 USD。

**基础信息**

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 商品ID |
| productName | string | 商品名称 |
| imageUrl | string | 商品图片 |
| productImageUrls | array | 商品图片列表 |
| region | string | 区域代码 |
| sellerId | string | 卖家ID |
| categoryId | string | 一级分类ID |
| categoryL2Id | string | 二级分类ID |
| categoryL3Id | string | 三级分类ID |

**价格 / 评分 / 佣金**

| 字段 | 类型 | 说明 |
|------|------|------|
| minPrice | number | 最低SKU价格(USD) |
| maxPrice | number | 最高SKU价格(USD) |
| spuAvgPrice | number | SPU平均价格(USD) |
| productRating | number | 商品评分 |
| reviewCount | integer | 评论数量 |
| productCommissionRate | number | 商品佣金比例 |

**销量（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalSaleCnt | integer | 总销量 |
| totalSale1dCnt | integer | 近1天销量 |
| totalSale7dCnt | integer | 近7天销量 |
| totalSale15dCnt | integer | 近15天销量 |
| totalSale30dCnt | integer | 近30天销量 |
| totalSale60dCnt | integer | 近60天销量 |
| totalSale90dCnt | integer | 近90天销量 |

**销售额 GMV（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalSaleGmvAmt | number | 总销售额 |
| totalSaleGmv1dAmt | number | 近1天销售额 |
| totalSaleGmv7dAmt | number | 近7天销售额 |
| totalSaleGmv15dAmt | number | 近15天销售额 |
| totalSaleGmv30dAmt | number | 近30天销售额 |
| totalSaleGmv60dAmt | number | 近60天销售额 |
| totalSaleGmv90dAmt | number | 近90天销售额 |

**直播（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalLiveCnt | integer | 总直播数量 |
| totalLive1dCnt | integer | 近1天直播数量 |
| totalLive7dCnt | integer | 近7天直播数量 |
| totalLive15dCnt | integer | 近15天直播数量 |
| totalLive30dCnt | integer | 近30天直播数量 |
| totalLive60dCnt | integer | 近60天直播数量 |
| totalLive90dCnt | integer | 近90天直播数量 |

**直播销量 / 直播销售额（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalLiveSale1dCnt | integer | 近1天直播销量 |
| totalLiveSale7dCnt | integer | 近7天直播销量 |
| totalLiveSale15dCnt | integer | 近15天直播销量 |
| totalLiveSale30dCnt | integer | 近30天直播销量 |
| totalLiveSale60dCnt | integer | 近60天直播销量 |
| totalLiveSale90dCnt | integer | 近90天直播销量 |
| totalLiveSaleGmv1dAmt | integer | 近1天直播销售额 |
| totalLiveSaleGmv7dAmt | integer | 近7天直播销售额 |
| totalLiveSaleGmv15dAmt | integer | 近15天直播销售额 |
| totalLiveSaleGmv30dAmt | integer | 近30天直播销售额 |
| totalLiveSaleGmv60dAmt | integer | 近60天直播销售额 |
| totalLiveSaleGmv90dAmt | integer | 近90天直播销售额 |

**视频（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalVideoCnt | integer | 总视频数量 |
| totalVideo1dCnt | integer | 近1天视频数量 |
| totalVideo7dCnt | integer | 近7天视频数量 |
| totalVideo15dCnt | integer | 近15天视频数量 |
| totalVideo30dCnt | integer | 近30天视频数量 |
| totalVideo60dCnt | integer | 近60天视频数量 |
| totalVideo90dCnt | integer | 近90天视频数量 |

**达人（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalIflCnt | integer | 总达人数量 |
| totalIflVideo1dCnt | integer | 近1天达人视频数量 |
| totalIflVideo7dCnt | integer | 近7天达人视频数量 |
| totalIflVideo15dCnt | integer | 近15天达人视频数量 |
| totalIflVideo30dCnt | integer | 近30天达人视频数量 |
| totalIflVideo60dCnt | integer | 近60天达人视频数量 |
| totalIflVideo90dCnt | integer | 近90天达人视频数量 |
| totalIflLive1dCnt | integer | 近1天达人直播数量 |
| totalIflLive7dCnt | integer | 近7天达人直播数量 |
| totalIflLive15dCnt | integer | 近15天达人直播数量 |
| totalIflLive30dCnt | integer | 近30天达人直播数量 |
| totalIflLive60dCnt | integer | 近60天达人直播数量 |
| totalIflLive90dCnt | integer | 近90天达人直播数量 |

**观看次数（多周期）**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalViewsCnt | integer | 总观看次数 |
| totalViews1dCnt | integer | 近1天观看次数 |
| totalViews7dCnt | integer | 近7天观看次数 |
| totalViews15dCnt | integer | 近15天观看次数 |
| totalViews30dCnt | integer | 近30天观看次数 |
| totalViews60dCnt | integer | 近60天观看次数 |
| totalViews90dCnt | integer | 近90天观看次数 |

**状态标识与其它**

| 字段 | 类型 | 说明 |
|------|------|------|
| discount | string | 折扣信息 |
| freeShipping | integer | 是否免运费 |
| salesFlag | integer | 主要配送方式 |
| salesTrendFlag | integer | 销售趋势标识：0=稳定、1=上升、2=下降 |
| isSShop | integer | 是否全托管店铺 |
| offMark | integer | 商品下架标识 |
| firstCrawlDt | string | 首次爬取日期 |
| descDetail | string | 商品详情描述 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因（如商品ID不正确、商品不存在等） |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/echotik/batchProductDetail \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "productIds": ["1729382310407603945", "1729382310407603946"]
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-echotik-batch-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Batch product detail results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
