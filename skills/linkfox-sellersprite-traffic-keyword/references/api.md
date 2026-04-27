# 卖家精灵-流量词反查 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/sellersprite/traffic/keyword`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: <api_key>`，从环境变量 `LINKFOXAGENT_API_KEY` 读取

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 市场站点，默认 `US` |
| asin | string | 是 | 商品 ASIN |
| month | string | 否 | 历史月份，`yyyyMM`；不传默认最近30天 |
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页条数，默认 50，最大 100 |
| keyword | string | 否 | 关键词筛选 |
| badges | string | 否 | 词标签，多值英文逗号分隔（如 `naturalSearching,amazonChoice`） |
| trafficKeywordTypes | string | 否 | 流量占比类型，多值逗号分隔 |
| conversionKeywordTypes | string | 否 | 转化类型，多值逗号分隔 |
| orderField | string | 否 | 排序字段（默认 `rankPosition`） |
| orderDesc | boolean | 否 | 排序方向，`true` 倒序，默认 `false` |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| asin | string | 查询 ASIN |
| data | array | 流量词列表 |
| summaryList | array | 汇总指标 |
| columns | array | 列定义 |
| costToken | integer | 消耗 token |

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sellersprite/traffic/keyword   -H "Authorization: $LINKFOXAGENT_API_KEY"   -H "Content-Type: application/json"   -d '{
    "marketplace": "US",
    "asin": "B0XXXXXXXXX",
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
  "skillName": "linkfox-sellersprite-traffic-keyword",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```
