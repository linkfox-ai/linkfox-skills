# 卖家精灵-选市场列表 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/sellersprite/market/research`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: <api_key>`，从环境变量 `LINKFOXAGENT_API_KEY` 读取

## 请求参数（高频）

> 原始 `inputSchema` 参数较多（70+），这里列高频字段。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 站点编码，默认 `US` |
| month | string | 否 | 时间筛选：`nearly` 或 `yyyyMM` |
| nodeIdPath | string | 否 | 类目节点路径 |
| departmentKeyword | string | 否 | 类目关键字路径 |
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页条数，默认 50，最大 200 |
| orderField | string | 否 | 排序字段 |
| orderDesc | boolean | 否 | 排序方向，默认 `true` |
| minAvgRevenue / maxAvgRevenue | number | 否 | 月均销售额范围 |
| minAvgUnits / maxAvgUnits | integer | 否 | 月均销量范围 |
| minAvgPrice / maxAvgPrice | number | 否 | 平均价格范围 |
| minAvgRating / maxAvgRating | number | 否 | 平均评分范围 |
| minAvgProfit / maxAvgProfit | number | 否 | 平均毛利率（%） |
| minGoodsCount / maxGoodsCount | integer | 否 | 商品数量范围 |
| minGoodsCrn / maxGoodsCrn | number | 否 | 商品集中度（%） |
| minSellerCrn / maxSellerCrn | number | 否 | 卖家集中度（%） |
| minBrandCrn / maxBrandCrn | number | 否 | 品牌集中度（%） |
| minNewProportion / maxNewProportion | number | 否 | 新品占比（%） |
| minAmazonSelfProportion / maxAmazonSelfProportion | number | 否 | 亚马逊自营占比（%） |
| minFbaProportion / maxFbaProportion | number | 否 | FBA占比（%） |
| minFbmProportion / maxFbmProportion | number | 否 | FBM占比（%） |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| data | array | 市场列表（类目聚合结果） |
| columns | array | 列定义 |
| costToken | integer | 消耗 token |
| type | string | 渲染类型 |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/market/research   -H "Authorization: $LINKFOXAGENT_API_KEY"   -H "Content-Type: application/json"   -d '{
    "marketplace": "US",
    "month": "nearly",
    "minAvgRevenue": 10000,
    "maxGoodsCrn": 40,
    "orderField": "total_amount",
    "orderDesc": true,
    "page": 1,
    "size": 50
  }'
```

---

## Feedback API

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-sellersprite-market-research",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```
