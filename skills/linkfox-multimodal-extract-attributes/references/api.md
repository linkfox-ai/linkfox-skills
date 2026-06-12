# 分析商品主图 API 参考

## 调用规范

- **请求地址**：`https://tool-gateway.linkfox.com/multimodal/extractPromptsFromMainImage`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: <api_key>`，api_key 从环境变量 `LINKFOXAGENT_API_KEY` 读取（如未配置，提示用户前往 https://skill.linkfox.com/linkfoxskills/guide.htm 申请）

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productImageAnalysisPrompt | string | 是 | 用户需要提取图片中信息的具体要求，最大 1,000 字符 |
| analyzeAdditionalImages | boolean | 否 | 是否分析商品附图/图片列表，默认 `false` |
| refResultData | string | 否 | 引用上游步骤的结果数据（JSON 字符串），须包含 `products` 数组及图片 URL，最大 2,024,000 字符 |
| userInput | string | 否 | 用户输入信息，提供补充上下文，最大 10,000,000 字符 |

- `productImageAnalysisPrompt` 是核心参数，应清晰描述需要提取的视觉维度（如颜色、形状、材质、款式等）

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| sourceType | string | 来源类型 |
| columns | array | 渲染的列定义 |
| costToken | integer | 调用LLM消耗的总token数（输入token + 输出token） |
| type | string | 渲染的样式 |
| products | array | 商品属性列表，每个ASIN的每个属性都是独立的一条记录，详见下方「商品字段」 |
| attributeGroups | array | 按属性名称和属性值对商品进行分组，便于比较和归类，详见下方「属性分组」 |

### 商品字段

`products` 数组中每个对象可包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 商品ASIN编号 |
| productId | string | 商品ID |
| title | string | 商品标题 |
| imageUrl | string | 商品主图地址 |
| productImageUrls | array | 商品图片列表 |
| asinUrl | string | 商品详情页地址 |
| brand | string | 品牌名称 |
| price | number | 价格 |
| rating | number | 评分 |
| ratings | integer | 评分数 |
| color | string | 颜色 |
| material | string | 材质 |
| monthlySalesUnits | integer | 月销量 |
| monthlySalesRevenue | number | 月销售额 |
| monthlySalesUnitsGrowthRate | number | 月销量增长率 |
| availableDate | string | 上架日期 |
| sourceType | string | 来源类型（如 "amazon"） |
| sourceTool | string | 来源工具 |
| attributeName | string | 属性名称（如：颜色、材质、形状等） |
| attributeValue | string | 属性值（如：红色、塑料、圆形等） |

### 属性分组

`attributeGroups` 数组中每个对象包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| attributeName | string | 属性名称（如：颜色、材质、形状等） |
| groups | array | 该属性下的所有分组，每组包含相同属性值的商品 |
| groups[].attributeValue | string | 属性值（如：红色、蓝色、圆形、方形等） |
| groups[].count | integer | 该组中的商品数量 |
| groups[].asins | array | 具有相同属性值的商品ASIN列表 |

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
curl -X POST https://tool-gateway.linkfox.com/multimodal/extractPromptsFromMainImage \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"productImageAnalysisPrompt": "分析商品主图，提取商品的主要颜色", "analyzeAdditionalImages": false, "refResultData": "{\"products\":[{\"asin\":\"B0XXXXXXXX\",\"imageUrl\":\"https://images-na.ssl-images-amazon.com/images/I/example.jpg\",\"title\":\"示例商品\"}]}"}'
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
