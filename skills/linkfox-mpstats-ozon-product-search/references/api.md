# MPSTATS Ozon 商品搜索 API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/productSearch`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）。以下字段与后端 `OzonItemSearchRequest` DTO 一致（同步日期 2026-05-27）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 二选一 | 俄语搜索关键词，例如 `кроссовки`（跑鞋） |
| productIds | array | 二选一 | Ozon 商品 SKU 列表（整数或字符串） |
| startDate | string | 否 | 统计起始日，格式 `YYYY-MM-DD`；留空时按一年前；最晚可选昨日 |
| endDate | string | 否 | 统计结束日，格式 `YYYY-MM-DD`；留空时按昨天；最晚可选昨日 |

> **二选一约束**：`keyword` / `productIds` 至少传一个，全部为空时请求会被拒绝。
>
> **无分页/排序/筛选**：上游单次最多返回约 36 条记录（官方上限）。底层固定按 startRow=0、endRow=100、空 sortModel/filterModel 调用，不再暴露 `page` / `pageSize` / `sortField` / `sortDirection` / `filters` 入参；如需更精确结果请收窄 keyword/SKU 或日期窗口。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码（字符串），`"200"` 表示成功 |
| msg | string | 消息；成功为 `ok`，失败为错误描述 |
| total | integer | 命中总数 |
| products | array | 商品列表（详见下方） |
| columns | array | 渲染列定义 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应类型 |

### products[*] 商品对象字段（10 个）

按后端 `OzonProductSearchItem` DTO 定义（同步日期 2026-05-11）。**search 端点为身份解析用途，不返回价/销/评/库存/周转/排名等业务指标**——这是硬契约，不是 sparse payload。如果需要那些指标：

- 单/批 SKU 全量卡：改用 `productDetail`（36 字段，含价格、销量、收入、周期对比等）
- 维度下钻：改用 `brandProducts` / `categoryProducts` / `sellerProducts`（39 字段全量商品卡）

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | SKU ID |
| title | string | 商品名称（俄语） |
| productPageUrl | string | 商品页 URL |
| imageUrl | string | 主图 URL |
| brand | string | 品牌名 |
| brandId | integer | 品牌 ID |
| sellerName | string | 卖家名 |
| sellerId | integer | 卖家 ID |
| sourceType | string | 数据源标识，恒为 `ozon` |
| sourceTool | string | 来源工具名，恒为 `MPSTATS-Ozon商品搜索` |

## 错误码

正常情况下，HTTP 状态码为 200，业务成功与否通过 `code` / `errcode` 区分（`200` 成功）。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `products` 字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` / `msg` 获取具体原因；常见为 keyword/productIds 均缺失、日期超过昨日、非俄语关键词等 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/mpstats/ozon/productSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "кроссовки"
  }'
```

## 响应示例（简略）

```json
{
  "code": "200",
  "msg": "ok",
  "total": 8721,
  "products": [
    {
      "productId": 1786874757,
      "title": "Кроссовки мужские ...",
      "brand": "Nike",
      "sellerName": "ООО Ромашка",
      "sellerId": 3628678,
      "imageUrl": "https://...",
      "productPageUrl": "https://www.ozon.ru/product/..."
    }
  ],
  "costToken": 1
}
```

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-product-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "User successfully located Ozon SKUs from a Russian keyword."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE` 三选一
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER` 四选一
- `content`：用户表达、实际现象、为什么算问题或好评
