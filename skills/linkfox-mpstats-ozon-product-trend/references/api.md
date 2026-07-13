# MPSTATS Ozon 商品趋势（分日）API 参考

## 调用规范

- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/mpstats/ozon/productTrend`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）

## 请求参数

POST Body（JSON）。以下字段与工具网关当前登记的「MPSTATS-Ozon-商品趋势」入参 schema 一致（同步日期 2026-04-30）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | integer | 是 | Ozon 商品 SKU |
| startDate | string | 否 | 统计起始日，`YYYY-MM-DD`；数据延迟 T-1，最晚可选昨日 |
| endDate | string | 否 | 统计结束日，`YYYY-MM-DD`；数据延迟 T-1，最晚可选昨日 |
| includeFbs | boolean | 否 | 是否包含 FBS 数据 |
| includeSearchStats | boolean | 否 | 是否附带搜索位次 / 可见性；部分赛道不支持 |

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

## 错误码

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 解析 `data` |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分或余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非 200 值 | 业务异常 | 查看 `errmsg` / `msg`；常见为 `productId` 无效、日期越过昨日等 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/mpstats/ozon/productTrend \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "productId": 1786874757,
    "startDate": "2025-03-01",
    "endDate": "2025-03-31",
    "includeSearchStats": true
  }'
```

---

## Feedback API

> 该接口与上方工具接口不同，**请勿混用两个基础 URL**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-mpstats-ozon-product-trend",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Spotted a clean seasonal peak for the SKU."
}
```

**字段说明：**
- `skillName`：使用本 skill 的 YAML `name`
- `sentiment`：`POSITIVE` / `NEUTRAL` / `NEGATIVE`
- `category`：`BUG` / `COMPLAINT` / `SUGGESTION` / `OTHER`
- `content`：用户表达、实际现象、为什么算问题或好评
