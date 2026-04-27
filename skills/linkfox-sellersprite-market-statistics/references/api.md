# 卖家精灵-选市场统计 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/sellersprite/market/statistics`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: <api_key>`，从环境变量 `LINKFOXAGENT_API_KEY` 读取

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 站点编码，默认 `US` |
| nodeIdPath | string | 是 | 节点ID路径，如 `1064954:1069242:...` |
| month | string | 否 | `nearly` 或 `yyyyMM` |
| topN | integer | 否 | 头部 Listing 数量，默认 10 |
| newProduct | integer | 否 | 新品定义（月），默认 6 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| data | array | 统计结果列表 |
| columns | array | 列定义 |
| costToken | integer | 消耗 token |
| type | string | 渲染类型 |

## data 常见指标（示例）

| 字段 | 说明 |
|------|------|
| hlAvgRating | 头部Listing平均星级 |
| hlAvgPrice | 头部Listing平均价格 |
| hlAvgBsr | 头部Listing平均BSR |
| avgUnits | 平均销量 |
| avgRevenue | 平均销售额 |
| avgSellers | 平均卖家数 |
| newCount | 新品数量 |
| newProportion | 新品占比 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/market/statistics   -H "Authorization: $LINKFOXAGENT_API_KEY"   -H "Content-Type: application/json"   -d '{
    "marketplace": "US",
    "nodeIdPath": "172282:281407",
    "month": "nearly",
    "topN": 10,
    "newProduct": 6
  }'
```

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-sellersprite-market-statistics",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```
