# 商品标题分词分析 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/product/titleAnalyze`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tokenizationAndCountingRequest | string | 是 | 自然语言描述，指定要从标题中提取的属性维度（如场景词、人群词、材质等）。每次只分析一个维度 |
| outputMode | string | 否 | 属性值输出模式。`MULTIPLE_RECORDS`（默认）：拆分属性值，每个属性值单独一条记录；`COMMA_SEPARATED`：保持LLM返回格式，多个属性值用逗号分隔在一条记录中 |
| refResultData | string | 否 | 引用的商品数据（JSON字符串）。仅在需要读取之前轮次对话的数据时使用，当前轮次的商品数据会自动汇总 |

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| sourceType | string | 来源类型 |
| type | string | 渲染样式 |
| columns | array | 渲染的列定义 |
| costToken | integer | 调用LLM消耗的总token数（输入token + 输出token） |
| products | array | 商品属性列表，每个ASIN的每个属性都是独立的一条记录 |
| products[].asin | string | 商品ASIN编号 |
| products[].title | string | 商品标题 |
| products[].attributeName | string | 属性名称（如：颜色、材质、形状等） |
| products[].attributeValue | string | 属性值（如：红色、塑料、圆形等） |
| products[].price | number | 价格 |
| products[].monthlySalesUnits | integer | 月销量 |
| products[].monthlySalesRevenue | number | 月销售额 |
| products[].monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| products[].rating | number | 评分 |
| products[].ratings | integer | 评分数 |
| products[].brand | string | 品牌名称 |
| products[].imageUrl | string | 商品主图地址 |
| products[].asinUrl | string | 商品详情页地址 |
| products[].availableDate | string | 上架日期 |
| products[].color | string | 颜色 |
| products[].material | string | 材质 |
| products[].productId | string | 商品ID |
| products[].productImageUrls | array | 商品图片列表 |
| products[].sourceTool | string | 来源工具 |
| products[].sourceType | string | 来源类型 |
| attributeGroups | array | 按属性名称和属性值对商品进行分组 |
| attributeGroups[].attributeName | string | 属性名称 |
| attributeGroups[].groups | array | 该属性下的所有分组 |
| attributeGroups[].groups[].attributeValue | string | 属性值 |
| attributeGroups[].groups[].count | integer | 该组中的商品数量 |
| attributeGroups[].groups[].asins | array | 具有相同属性值的商品ASIN列表 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | 检查请求头 `Authorization` 是否正确携带 API Key；API Key 申请方式请参考上述[调用规范](#调用规范)下的认证方式。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/product/titleAnalyze \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tokenizationAndCountingRequest": "统计 商品标题 中出现的 场景词", "outputMode": "MULTIPLE_RECORDS"}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
